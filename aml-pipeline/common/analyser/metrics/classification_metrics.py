from typing import Any, Dict, List, Tuple, Union

from common.analyser.metrics.metric_calculator import MetricCalculator
from common.analyser.parsers.classification_parser import ClassificationParser

import mlflow
import time
import os
from loguru import logger as logging
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    top_k_accuracy_score,
)


class ClassificationMetrics(MetricCalculator):
    def __init__(
        self,
        ground_truth: Dict[str, Any],
        predictions: Dict[str, Any],
        params: Dict[str, Any],
        verbose: bool = False,
    ):
        self._metrics = {}
        self.top_k_accuracy = params["top_k_list"]
        super().__init__(
            ground_truth=ground_truth, predictions=predictions, verbose=verbose
        )

    def validate_input(self):

        super().validate_input()

        # check that predictions file has classification predictions
        if "classification" not in self.predictions["predictions"]:
            msg = "no classification predictions were found in predictions file"
            logging.error(msg)
            raise KeyError

        # check if number of categories is smaller than top_k_accuracy
        number_of_categories = len(self.ground_truth["categories"])
        for k in self.top_k_accuracy:
            if k > number_of_categories:
                msg = f"top_k_accuracy {k} is larger or equal to the total number of categories found in dataset"
                logging.error(msg)
                raise ValueError

        return True

    def parse_input(self):
        classification_parser = ClassificationParser(ground_truth=self.ground_truth,
                                                     predictions=self.predictions)
        return classification_parser.parse()

    def calculate(self):

        input_valid = self.validate_input()
        metrics = {}
        if input_valid:
            y_true, y_pred, y_score, labels, img_list = self.parse_input()
            print('y_true: ', y_true)
            print('y_pred: ', y_pred)
            print('y_score: ', y_score)
            print('labels: ', labels)

            accuracy, precision, recall, f1 = self.get_base_metrics(
                y_true=y_true, y_pred=y_pred
            )
            metrics["accuracy"] = accuracy
            metrics["precision"] = precision
            metrics["recall"] = recall
            metrics["f1"] = f1

            # For k = 2: Calculating top k accuracy score using probabilities for class 1
            if self.top_k_accuracy == [2]:
                y_score = np.array([score[0] for score in y_score])

            for k in self.top_k_accuracy:
                top_acc = self.get_top_k_accuracy(
                    y_true=y_true, y_score=y_score, labels=labels, k=k
                )
                metrics[f"top_{k}_accuracy"] = top_acc

            self._metrics = metrics

        return self._metrics

    def mlflow_log(self, log_path: str, log_name: str = "classification_metrics"):

        max_retries = 5
        retry_delay = 3

        retries = 0
        while retries < max_retries:
            try:
                if log_name.endswith(".json"):
                    mlflow.log_dict(self._metrics, os.path.join(log_path, log_name))
                else:
                    mlflow.log_dict(self._metrics, os.path.join(log_path, log_name+".json"))
                break
            except Exception as e:
                logging.warning(
                    f"Failed to log to MLflow. Retrying in {retry_delay} seconds. Error: {e}"
                )
                time.sleep(retry_delay)
                retries += 1


    @staticmethod
    def get_base_metrics(
        y_true: List[Union[int, str]],
        y_pred: List[Union[int, str]],
    ) -> Tuple[float, float, float, float]:
        precision = precision_score(y_true, y_pred, average="macro")
        recall = recall_score(y_true, y_pred, average="macro")
        f1 = f1_score(y_true, y_pred, average="macro")
        accuracy = accuracy_score(y_true, y_pred)

        return accuracy, precision, recall, f1

    @staticmethod
    def get_top_k_accuracy(
        y_true: List[Union[int, str]],
        y_score: List[List[Union[int, str]]],
        labels: List[Union[int, str]],
        k: int,
    ) -> float:
        return top_k_accuracy_score(y_true=y_true, y_score=y_score, labels=labels, k=k)
