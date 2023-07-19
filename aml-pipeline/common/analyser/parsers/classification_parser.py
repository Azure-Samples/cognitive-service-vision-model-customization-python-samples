from common.analyser.parsers.parser_base import Parser
from typing import Any, Dict

from loguru import logger as logging


class ClassificationParser(Parser):
    def __init__(
        self,
        ground_truth: Dict[str, Any],
        predictions: Dict[str, Any],
        verbose: bool = False,
        **kwargs,
    ):
        super().__init__(verbose)
        self.ground_truth = ground_truth
        self.predictions = predictions

    def parse(self):

        gt_categories = self.ground_truth["categories"]
        gt_annotations = self.ground_truth["annotations"]
        gt_images = self.ground_truth["images"]

        img_list = [x["file_name"] for x in gt_images]

        # gt dict {category_id: category_name}
        gt_categories_dict = dict([(x["id"], x["name"]) for x in gt_categories])

        # gt dict {img_id: file_name}
        gt_images_dict = dict([(x["id"], x["file_name"]) for x in gt_images])

        # gt dict {image_name: category_name}
        gt_annotations_dict = dict(
            [
                (gt_images_dict[x["image_id"]], gt_categories_dict[x["category_id"]])
                for x in gt_annotations
            ]
        )

        predictions_images = self.predictions["images"]
        predictions_categories = self.predictions["categories"]

        # predictions dict {img_id: img_name}
        predictions_images_dict = dict(
            [(x["id"], x["name"]) for x in predictions_images]
        )

        # predictions dict {category_name: category_id}
        predictions_categories_reverse_dict = dict(
            [(x["name"], x["id"]) for x in predictions_categories]
        )

        labels = sorted(list(predictions_categories_reverse_dict.values()))

        y_true = []
        y_pred = []
        y_score = []
        for classification_prediction in self.predictions["predictions"][
            "classification"
        ]:
            id_sorted_scores = sorted(
                classification_prediction["scores"],
                key=lambda d: d["category_id"],
                reverse=False,
            )
            y_score.append([x["score"] for x in id_sorted_scores])

            score_sorted_scores = sorted(
                classification_prediction["scores"],
                key=lambda d: d["score"],
                reverse=True,
            )
            predicted_category = score_sorted_scores[0]["category_id"]
            y_pred.append(predicted_category)

            image_file_name = predictions_images_dict[
                classification_prediction["image_id"]
            ]
            image_true_category_name = gt_annotations_dict[image_file_name]
            true_category_id_predictions = predictions_categories_reverse_dict[
                image_true_category_name
            ]
            y_true.append(true_category_id_predictions)

        return y_true, y_pred, y_score, labels, img_list