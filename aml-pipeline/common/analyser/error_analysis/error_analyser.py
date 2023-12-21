from abc import abstractmethod
from typing import Any, Dict

from loguru import logger as logging
from common.analyser.base.analyser_base import Analyser


class ErrorAnalyser(Analyser):
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

    @abstractmethod
    def apply(self):

        """apply method needs to be implemented by child class of ErrorAnalyser."""
        msg = "apply method needs to be implemented by child class of ErrorAnalyser."
        logging.error(msg)
        raise NotImplementedError(msg)

    def mlflow_log(self):

        """mlflow_log method needs to be implemented by child class of ErrorAnalyser."""
        msg = "mlflow_log method needs to be implemented by child class of ErrorAnalyser."
        logging.error(msg)
        raise NotImplementedError(msg)

    def validate_input(self):
        # validate coco gt file keys
        if not all(
                key in self.ground_truth.keys()
                for key in ("categories", "images", "annotations")
        ):
            msg = "One or more of the following keys are missing in ground truth file: categories, images, annotations"
            logging.error(msg)
            raise KeyError

        # validate predictions keys
        if not all(
                key in self.predictions.keys()
                for key in ("categories", "images", "predictions")
        ):
            msg = "One or more of the following keys are missing in predictions file: categories, images, predictions"
            logging.error(msg)
            raise KeyError

        # check that all categories in predictions exist in ground_truth
        gt_categories = [x["name"] for x in self.ground_truth["categories"]]
        for category in self.predictions["categories"]:
            if category["name"] not in gt_categories:
                msg = f"Category {category['name']} is not present in ground truth file"
                logging.error(msg)
                raise ValueError
