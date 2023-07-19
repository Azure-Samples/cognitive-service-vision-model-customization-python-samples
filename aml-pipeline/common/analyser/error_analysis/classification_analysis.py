import os
import time
from typing import Any, Dict, List, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import mlflow
import pandas as pd
import torch
from loguru import logger as logging
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from torch.utils.data import DataLoader
from tqdm import tqdm

from common.analyser.error_analysis.error_analyser import ErrorAnalyser
from common.analyser.helper_classes.similarity import FeaturesExtractor, SimilarityDataset
from common.analyser.parsers.classification_parser import ClassificationParser


class ClassificationAnalysis(ErrorAnalyser):
    def __init__(
        self,
        ground_truth: Dict[str, Any],
        predictions: Dict[str, Any],
        params: Dict[str, Any],
        verbose: bool = False,
    ):
        super().__init__(ground_truth=ground_truth, predictions=predictions, verbose=verbose)

        self.dataset_base_path = params["dataset_base_path"]
        self._results = {}

    def validate_input(self):

        super().validate_input()

        # check that predictions file has classification predictions
        if "classification" not in self.predictions["predictions"]:
            msg = "no classification predictions were found in predictions file"
            logging.error(msg)
            raise KeyError

        return True

    def parse_input(self):
        classification_parser = ClassificationParser(
            ground_truth=self.ground_truth, predictions=self.predictions
        )
        return classification_parser.parse()

    def apply(self):

        input_valid = self.validate_input()
        results = {}

        if input_valid:
            y_true, y_pred, y_scores, labels, img_list = self.parse_input()

            y_score = [max(x) for x in y_scores]

            confusion_matrix_fig = self.create_report(
                img_list=img_list,
                y_pred=y_pred,
                y_true=y_true,
                confidence=y_score,
                labels=labels,
            )

            mispredictions_df = self.get_mispredictions(
                img_list=img_list, y_pred=y_pred, y_true=y_true, confidence=y_score
            )

            similarities_df = self.find_similar(base_path=self.dataset_base_path, img_list=img_list)

            results["confusion_matrix_fig"] = confusion_matrix_fig
            results["mispredictions_df"] = mispredictions_df
            results["similarities_df"] = similarities_df

            self._results = results

        return self._results

    def mlflow_log(self, log_path: str, log_name: str = "classification_analysis"):

        max_retries = 5
        retry_delay = 3

        retries = 0
        while retries < max_retries:
            try:
                mlflow.log_figure(
                    self._results["confusion_matrix_fig"],
                    os.path.join(log_path, log_name, "confusion_matrix_fig.png"),
                )
                misprediction_df = self._results["mispredictions_df"].merge(
                    self._results["similarities_df"], on="img_path", how="left"
                )

                csv_file_path = os.path.join(log_path, log_name)
                if not os.path.exists(csv_file_path):
                    os.makedirs(csv_file_path)
                full_path = os.path.join(csv_file_path, "mispredictions.csv")
                misprediction_df.to_csv(full_path, index=False)
                mlflow.log_artifact(full_path, csv_file_path)

                break
            except Exception as e:
                logging.warning(
                    f"Failed to log to MLflow. Retrying in {retry_delay} seconds. Error: {e}"
                )
                time.sleep(retry_delay)
                retries += 1

    def find_similar(self, base_path: str, img_list: List[str], top_n: int = 10) -> pd.DataFrame:
        # init features extractor
        model = FeaturesExtractor()
        # init dataset and pass it to pytorch dataloader
        ds = SimilarityDataset(base_path, img_list, transform=model.transform)
        dataloader = DataLoader(ds, batch_size=64, shuffle=False)
        # run inferencing and collect all extracted feature vectors as a single tensor
        outputs = None
        with torch.no_grad():
            for batch in tqdm(iter(dataloader)):
                batch_outputs = model(batch)
                if outputs is None:
                    outputs = batch_outputs
                else:
                    outputs = torch.cat((outputs, batch_outputs), 0)
        # calculate pairwise cosine distance for feature vectors
        distance_tensor = torch.cdist(outputs, outputs, p=2.0)
        # fill diagonal with really high value for it to be listed at the end when sorting
        distance_tensor.fill_diagonal_(999)
        # for each input sort most similar (smallest distance) instances and return indexes
        closest_idxs = torch.argsort(distance_tensor, dim=-1, descending=False)
        closest_images = [[img_list[idx] for idx in row[:top_n]] for row in closest_idxs]
        # combine results into pandas
        df = pd.DataFrame(data={"img_path": img_list, "most_similar_imgs": closest_images})
        return df

    def get_mispredictions(
        self,
        img_list: List[str],
        y_true: List[Union[int, str]],
        y_pred: List[Union[int, str]],
        confidence: List[Union[int, float]],
    ) -> pd.DataFrame:
        # put data into pandas
        df = pd.DataFrame(
            data={
                "img_path": img_list,
                "y_true": y_true,
                "y_pred": y_pred,
                "confidence": confidence,
            }
        )
        # sort dataframe by confidence
        df.sort_values(by=["confidence"], ascending=False, inplace=True)
        # return only rows with mispredictions (y_true!=y_pred)
        return df[df.y_pred != df.y_true]

    def create_report(
        self,
        img_list: List[str],
        y_true: List[Union[int, str]],
        y_pred: List[Union[int, str]],
        confidence: List[Union[int, float]],
        labels: List[Union[int, str]],
    ) -> Tuple[plt.Figure]:
        # create confusion matrix and matplot figure
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
        cm_fig, ax = plt.subplots(figsize=(30, 30), facecolor="white")
        ax.tick_params(axis="both", which="major", labelsize=18)
        ax.tick_params(axis="both", which="minor", labelsize=18)
        ax.set_xlabel("Predicted label", fontsize=20)
        ax.set_ylabel("True label", fontsize=20)
        cm_display.plot(ax=ax, xticks_rotation="vertical")

        return cm_fig
