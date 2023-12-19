import argparse
import os
import logging
import json
import pandas as pd

logging.getLogger().setLevel(logging.INFO)
from azureml.core import Run
from azureml.core import Dataset as amlds
import mlflow
from cognitive_service_vision_model_customization_python_samples import (
    ResourceType,
    TrainingClient,
    Model,
    ModelKind,
    TrainingParameters,
    PredictionClient,
)
from datetime import datetime
from helper import create_barplot, aml_to_uvs_dataset, get_secret, str2bool, read_img_as_bytes, mlflow_safe_log

from common.analyser.metrics.classification_metrics import ClassificationMetrics
from common.analyser.error_analysis.classification_analysis import ClassificationAnalysis


def run(
    resource_key: str,
    model_name: str,
    train_aml_dataset_name: str,
    train: bool = False,
    time_budget_in_hours: int = 20,  # 20 hours
    inference: bool = False,
    inference_data_path: str = "",
    coco_json_url: str = ""
):
    if not os.path.exists("outputs/"):
        os.makedirs("outputs/")
        print(">>>>>>>Created 'outputs' dir..")
    # TODO: Change hardcoded values to function args
    # resource_type = ResourceType.SINGLE_SERVICE_RESOURCE  # or ResourceType.MULTI_SERVICE_RESOURCE
    resource_type = ResourceType.MULTI_SERVICE_RESOURCE
    resource_name = ""  # not used / leave empty string
    multi_service_endpoint = "https://westeurope.api.cognitive.microsoft.com/"

    # MODEL TRAINING
    model_kind = ModelKind.GENERIC_IC
    # interval of time in seconds to check on models training progress
    check_wait_in_secs = 10 * 60  # 10 minutes

    training_client = TrainingClient(
        resource_type, resource_name, multi_service_endpoint, resource_key
    )

    if train:
        train_aml_dataset_name = aml_to_uvs_dataset(
            train_aml_dataset_name,
            resource_type,
            resource_name,
            multi_service_endpoint,
            resource_key,
            coco_json_url
        )

        train_params = TrainingParameters(
            training_dataset_name=train_aml_dataset_name,
            time_budget_in_hours=time_budget_in_hours,
            model_kind=model_kind,
        )

        # Check if model already exists
        try:
            training_client.query_model(model_name)
            model_exists = True
        except:
            print(
                "Model name is not yet registered. Will train new model using model name ",
                model_name,
            )
            model_exists = False
            pass

        if model_exists:
            model_name = model_name + "_" + str(datetime.now().strftime("%m%d%Y%H%M%S"))
            print("Model name already exists... created new model name: ", model_name)

        model = Model(model_name, train_params)
        # start training process and wait for completion
        model = training_client.train_model(model)
        # this line will cause the job to wait for models training completion (or failure)
        # comment out if you don't want to wait
        model = training_client.wait_for_training_completion(model_name, check_wait_in_secs)
    else:
        model = training_client.query_model(model_name)
    # only works if model training is completed and metrics are available
    # comment out to bypass
    print(type(model), model)
    print(model.model_performance)

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    # Tags are shown as properties of the job in the Azure ML dashboard. Run once.
    tags = {
        "model_type": "uvs_florence",
        "uvs_model_name": model.name,
        "status": model.status,
        #"failure_code": model.failure_error_code,
        "error_message": model.error,
        "training_params": model.training_params,
        #"model_kind": model.training_params.model_kind,
        "time_budget_in_hours": model.training_params.time_budget_in_hours,
    }
    mlflow.set_tags(tags)
    model_metrics = {}
    ean_acc = []
    for k, v in model.model_performance.items():
        if type(v) in [int, float]:
            model_metrics[k] = v
        if k == "tagPerformance":
            ean = [key for key in v.keys()]
            acc_list = [val for val in v.values()]
            for ind_acc in acc_list:
                for ind_acc_float in ind_acc.values():
                    ean_acc.append(ind_acc_float)

    fig = create_barplot(ean, ean_acc)
    mlflow_safe_log(mlflow.log_figure, fig, "per_ean_accuracy.png")

    model_metrics["training_cost_in_minutes"] = model.training_cost_in_minutes
    mlflow.log_metrics(model_metrics)

    if inference:
        model_predictions_results = {}

        # initialize UVS prediction client
        prediction_client = PredictionClient(
            resource_type, resource_name, multi_service_endpoint, resource_key
        )
        # read annotation json file and check if there are multiple ones
        json_files_list = [file for file in os.listdir(inference_data_path) if file.endswith('.json')]
        if len(json_files_list) > 1:
            raise RuntimeError('Only one annotation json file may exist in dataset folder')
        if len(json_files_list) == 0:
            raise FileNotFoundError('No annotation json file was found in dataset folder')
        inference_coco_annotation_file = json.load(open(os.path.join(inference_data_path, json_files_list[0])))

        # images and categories in prediction format
        inference_images = inference_coco_annotation_file["images"]
        model_predictions_results["images"] = [dict((("id", x["id"]), ("name", x["file_name"]))) for x in inference_images]
        model_predictions_results["categories"] = inference_coco_annotation_file["categories"]
        predictions_categories_reverse_dict = dict(
            [(x["name"], x["id"]) for x in model_predictions_results["categories"]]
        )
        predictions_images_reverse_dict = dict(
            [(x["name"], x["id"]) for x in model_predictions_results["images"]]
        )
        ####
        inference_results = []
        categories_dict = dict([(x["id"], x["name"]) for x in model_predictions_results["categories"]])
        inference_annotations = inference_coco_annotation_file["annotations"]
        annotations_dict = dict([(x["image_id"], categories_dict[x["category_id"]]) for x in inference_annotations])
        ####
        model_predictions = []

        for i, img in enumerate(inference_images):

            img_file_name = img["file_name"]
            img_path = os.path.join(inference_data_path, img_file_name)
            img_bytes = read_img_as_bytes(img_path)
            # getting the predictions and select the one class with the highest confidence
            prediction_json = prediction_client.predict(model_name, img_bytes, content_type="image/png")
            predictions = prediction_json['customModelResult']['tagsResult']['values']

            tmp_model_prediction = {}
            tmp_model_prediction["prediction_id"] = i
            tmp_model_prediction["image_id"] = predictions_images_reverse_dict[img_file_name]
            scores = []
            for cat in predictions:
                tmp_score = {}
                tmp_score["category_id"] = predictions_categories_reverse_dict[cat["name"]]
                tmp_score["score"] = cat["confidence"]
                scores.append(tmp_score)

            tmp_model_prediction["scores"] = scores

            model_predictions.append(tmp_model_prediction)
            ######
            # sort predictions by label to make downstream tasks easier
            predictions = sorted(
                predictions,
                key=lambda d: d['name'], reverse=False)
            # sort predictions by confidence
            top_1_prediction = sorted(
                predictions,
                key=lambda d: d['confidence'], reverse=True)[0]

            img_inference_results = {
                "image_id": img["id"],
                "image_name": img["file_name"],
                "true_category": annotations_dict[img["id"]],
                "pred_category": top_1_prediction['name'],
                "confidence": top_1_prediction['confidence'],
                "predictions": predictions
            }
            inference_results.append(img_inference_results)
            ######

        model_predictions_results["predictions"] = {"classification": model_predictions}
        print("###############")        
        df_inf_results = pd.DataFrame.from_records(inference_results)
        df_inf_results.to_csv("outputs/test_results.csv", index=False)
        mlflow_safe_log(mlflow.log_artifact, "outputs/test_results.csv")
        print("###############")
        top_k_list = [3, 4, 5]
        classification_metrics = ClassificationMetrics(ground_truth=inference_coco_annotation_file,
                                                       predictions=model_predictions_results,
                                                       params={"top_k_list": top_k_list})
        metrics = classification_metrics.calculate()
        mlflow.log_metrics(metrics)
        classification_metrics.mlflow_log(log_path="mlflow_logs")

        classification_analysis = ClassificationAnalysis(ground_truth=inference_coco_annotation_file,
                                                         predictions=model_predictions_results,
                                                         params={"dataset_base_path": inference_data_path})

        analysis_results = classification_analysis.apply()
        classification_analysis.mlflow_log(log_path="mlflow_logs")

        mlflow_safe_log(mlflow.log_figure, analysis_results["confusion_matrix_fig"], "test_confusion_matrix.png")
        misprediction_df = analysis_results["mispredictions_df"].merge(analysis_results["similarities_df"], on='img_path', how='left')
        misprediction_df.to_csv("outputs/test_mispred.csv", index=False)
        mlflow_safe_log(mlflow.log_artifact, "outputs/test_mispred.csv")
        
        print("---------done-----------")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--uvs_resource_key",
        type=str,
        help="UVS resource key",
        default="12345"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="UVS model name. Needs to be unique",
        default="testaml1",
    )
    parser.add_argument(
        "--train_aml_dataset_name",
        type=str,
        help="AML dataset name for model training",
        default="Test_Jan-19-2023-09-07-22",
    )
    parser.add_argument(
        "--train",
        type=lambda x: str2bool(x),
        help="Train model or just retrieve performance",
        default="False",
    )
    parser.add_argument(
        "--time_budget_in_hours",
        type=int,
        help="UVS Model training job budget time in hours",
        default=20 * 60,
    )
    parser.add_argument(
        "--inference",
        type=lambda x: str2bool(x),
        help="Run inference on the given inference dataset or not",
        default="False",
    )
    parser.add_argument(
        "--inference_data_path",
        type= str,
        help="path of AML dataset to be mount for inference",
        default=""
    )
    parser.add_argument(
        "--coco_json_url",
        type= str,
        help="Full url to coco json file for training dataset",
        default=""
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    run(
        resource_key=args.uvs_resource_key,
        model_name=args.model_name,
        train_aml_dataset_name=args.train_aml_dataset_name,
        train=args.train,
        time_budget_in_hours=args.time_budget_in_hours,
        inference=args.inference,
        inference_data_path=args.inference_data_path,
        coco_json_url=args.coco_json_url
    )
