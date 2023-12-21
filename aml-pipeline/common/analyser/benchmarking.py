import importlib
import json
import os
import sys

from azure.identity import ClientSecretCredential
from azure.storage.blob import ContainerClient
from loguru import logger as logging


class BenchmarkingCalculator:
    def __init__(self, config_file_path: str):
        configs = json.load(open(config_file_path))

        self._replace_env_variables(configs, "$")

        self._predictions_storage = configs["predictions_storage"]
        self._metrics_types = configs["metrics_types"]
        self._predictions_results = configs["predictions_results"]

        if "mlflow_logging_path" in configs.keys():
            self._mlflow_logging_path = configs["mlflow_logging_path"]
        else:
            self._mlflow_logging_path = "./logs"

        try:
            credential = ClientSecretCredential(
                tenant_id=self._predictions_storage["tenant_id"],
                client_id=self._predictions_storage["sp_client_id"],
                client_secret=self._predictions_storage["sp_client_secret"],
            )
        except ValueError as e:
            logging.error(e)
            raise ValueError(e)

        self._container = ContainerClient(
            account_url=self._predictions_storage["blob_account_url"],
            container_name=self._predictions_storage["container_name"],
            credential=credential,
        )

        if self._container is not None:
            logging.debug(
                f"established connection to container "
                f"properties: "
                f"{self._container.get_container_properties()}"
            )
        elif self._container is None:
            logging.warning(f"could not establish connection to container ")

        self._results = {}

        logging.info("benchmarking initialized")

    def _read_file(self, file_path: str) -> bytes:

        logging.debug(f"Reading file from blob storage from location: {file_path}")

        # --- read bytes from file ---
        file_content = None
        blob_client = self._container.get_blob_client(file_path)

        if blob_client.exists():
            download_stream = blob_client.download_blob()
            file_content = download_stream.readall()
        else:
            logging.warning(f"blob {file_path} does not exists")

        return file_content

    @staticmethod
    def _json_blobs_in_path(blob_container: ContainerClient, path: str):
        path_content = blob_container.list_blobs(name_starts_with=path)
        path_content = [
            x for x in path_content if x.content_settings["content_type"] == "application/json"
        ]
        return path_content

    @staticmethod
    def _class_from_name(class_name, module_name=None):
        if module_name is not None:
            module = importlib.import_module(module_name)
        else:
            module = sys.modules[__name__]
        class_obj = getattr(module, class_name)
        return class_obj

    def _replace_env_variables(self, json_input, lookup_char):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if type(v) == str and v[0] == lookup_char:
                    json_input[k] = os.environ[v[2:-1]]
                else:
                    self._replace_env_variables(v, lookup_char)
        elif isinstance(json_input, list):
            for item in json_input:
                self._replace_env_variables(item, lookup_char)

    def calculate(self, mlflow_logging: bool = True):

        # load ground truth coco file
        gt_base_dir = self._predictions_storage["gt_base_dir"]
        dataset_name = self._predictions_results["dataset_name"]
        gt_path = os.path.join(gt_base_dir, dataset_name)
        gt_path_content = self._json_blobs_in_path(self._container, gt_path)
        if len(gt_path_content) > 1:
            msg = f"Only one annotation json file may exist in dataset path {gt_path}"
            logging.error(msg)
            raise RuntimeError(msg)
        if len(gt_path_content) == 0:
            msg = f"No annotation json file was found in dataset path {gt_path}"
            logging.error(msg)
            raise FileNotFoundError(msg)
        gt_json = json.loads(self._read_file(gt_path_content[0].name))

        # load predictions and calculate metrics
        model_results_base_dir = self._predictions_storage["model_results_base_dir"]

        for model in self._predictions_results["models_predictions"]:
            for version in model["model_versions"]:
                tmp_model_version = os.path.join(
                    model_results_base_dir, model["model_name"], version
                )
                model_prediction_path_content = self._json_blobs_in_path(
                    self._container, tmp_model_version
                )

                for predictions_file_blob in model_prediction_path_content:
                    predictions_json = json.loads(self._read_file(predictions_file_blob.name))

                    if predictions_json["dataset_name"] == dataset_name:

                        if "metrics_type" in self._metrics_types.keys():
                            if not self._metrics_types["metrics_type"][0] in self._results.keys():
                                self._results[self._metrics_types["metrics_type"][0]] = []
                            metrics_calculator = self._class_from_name(
                                self._metrics_types["metrics_type"][0],
                                self._metrics_types["metrics_type"][1],
                            )(
                                ground_truth=gt_json,
                                predictions=predictions_json,
                                params=self._metrics_types["params"],
                            )
                            metrics = metrics_calculator.calculate()
                            if mlflow_logging:
                                metrics_calculator.mlflow_log(log_path=
                                                              os.path.join(self._mlflow_logging_path,
                                                                           model["model_name"],
                                                                           version))
                            self._results[self._metrics_types["metrics_type"][0]].append({
                                predictions_file_blob.name: metrics
                            })

                        if "error_analysis_type" in self._metrics_types.keys():
                            if not self._metrics_types["error_analysis_type"][0] in self._results.keys():
                                self._results[self._metrics_types["error_analysis_type"][0]] = []
                            error_analysis_calculator = self._class_from_name(
                                self._metrics_types["error_analysis_type"][0],
                                self._metrics_types["error_analysis_type"][1],
                            )(
                                ground_truth=gt_json,
                                predictions=predictions_json,
                                params=self._metrics_types["params"],
                            )
                            error_analysis = error_analysis_calculator.apply()
                            if mlflow_logging:
                                error_analysis_calculator.mlflow_log(log_path=
                                                                     os.path.join(self._mlflow_logging_path,
                                                                                  model["model_name"],
                                                                                  version))
                            self._results[self._metrics_types["error_analysis_type"][0]].append({
                                predictions_file_blob.name: error_analysis
                            })

                    else:
                        msg = f"{predictions_file_blob.name} doesn't match dataset"\
                              f"{dataset_name}. It will be ignored"
                        logging.warning(msg)

        print("results: ", self._results)

        return self._results
