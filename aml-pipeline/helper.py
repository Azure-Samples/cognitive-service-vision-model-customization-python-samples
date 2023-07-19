import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import os
import json
from typing import Tuple
from azureml.core import Run, Datastore
from azureml.core import Dataset as aml_dataset
from cognitive_service_vision_model_customization_python_samples import DatasetClient, Dataset, AnnotationKind


def read_img_as_bytes(img_path):
    with open(img_path, "rb") as f:
        img = f.read()
    return img

def mlflow_safe_log(function, *args):
    import time, logging
    max_retries = 5
    retry_delay = 3

    retries = 0
    while retries < max_retries:
        try:
            function(*args)
            break
        except Exception as e:
            logging.warning(
                f"Failed to log to MLflow. Retrying in {retry_delay} seconds. Error: {e}"
            )
            time.sleep(retry_delay)
            retries += 1

def get_secret(name: str) -> str:
    """
    Function to extract secrets from Azure KeyVault.

    Args:
        name (str): secret key for which the value is needed

    Returns:
       secret: value stored in KeyVault
    """

    run = Run.get_context()
    secret_value = run.get_secret(name=name)
    return secret_value

def str2bool(v: str) -> bool:
    """
    Function to transform string input parameters into boolean input format for ArgumentParser.

    Args:
        v (str): string to indicate 'True' or 'False'

    Returns:
        boolean: boolean True or False
    """
    return v.lower() in ("yes", "true", "t", "1")

def extract_florence_spec(aml_ds: str) -> Tuple[str, str]:
    """
    Function to extract underlying blob storage information (annotation_file, storage_base) from AML Dataset v1.
    We are assuming the Dataset already exists in AML.

    Args:
        aml_ds (str): Name of registered AML Dataset

    Returns:
        annotation_file (str): Annotation URI to individual coco file stored in the underlying blob storage
        storage_base (str): Storage URI to the images stored in the underlying blob storage
    """

    run = Run.get_context()
    workspace = run.experiment.workspace

    # Extract underlying datastore name from dataset
    dataset_aml = aml_dataset.get_by_name(workspace, name=aml_ds)
    js = json.loads(dataset_aml._definition)
    for k, v in js.items():
        if k == "blocks":
            for a in v:
                datastore_name = a["arguments"]["datastores"][0]["datastoreName"]
                blob_folder = os.path.dirname(a["arguments"]["datastores"][0]["path"])

    datastore = Datastore(workspace, datastore_name)

    annotation_file = (
        "https://"
        + str(datastore.account_name)
        + ".blob.core.windows.net/"
        + str(datastore.container_name)
        + "/"
        + str(blob_folder)
        + "/coco_info.json"
    )
    # storage_base = (
    #     "https://"
    #     + str(datastore.account_name)
    #     + ".blob.core.windows.net/"
    #     + str(datastore.container_name)
    # )

    # return annotation_file, storage_base
    return annotation_file

def aml_to_uvs_dataset(
    aml_ds: str,
    resource_type: str,
    resource_name: str,
    multi_service_endpoint: str,
    resource_key: str,
) -> None:
    """
    Function to transform AML to UVS compatible dataset.
    UVS Dataset is automatically registered in UVS.
    UVS Dataset will receive exactly the same name as AML Dataset.
    Creates new UVS dataset if given dataset name already exists.

    Args:
        aml_ds (str): AML Dataset name (will also be used for UVS Dataset name)
        resource_type (str): Specify if single service or multi service resource is required
        resource_name (str): Name of resource (Currently empty string)
        multi_service_endpoint (str): Cognitive Service Resource Endpoint URI
        resource_key (str): Resource key for Cognitive Service Resource
    """

    # annotation_file, storage_base = extract_florence_spec(aml_ds)
    annotation_file = extract_florence_spec(aml_ds)


    dataset_client = DatasetClient(
        resource_type, resource_name, multi_service_endpoint, resource_key
    )

    ds = Dataset(
        name=aml_ds,
        annotation_kind=AnnotationKind.MULTICLASS_CLASSIFICATION,
        annotation_file_uris=[annotation_file]
    )

    # Check if dataset exists
    try:
        # Dataset does not yet exist
        dataset_client.register_dataset(ds)
        print("Registered new UVS dataset with name: ", aml_ds)
    except:
        print("Dataset is already registered in UVS.")

        # TO DO: Decide if it's necessary to re-register dataset with different name.
        aml_ds = aml_ds + "_" + str(datetime.now().strftime("%m%d%Y%H%M%S"))
        print(
            "Dataset name already exists in UVS... created new dataset with name: ",
            aml_ds,
        )
        ds = Dataset(
            name=aml_ds,
            annotation_kind=AnnotationKind.MULTICLASS_CLASSIFICATION,
            annotation_file_uris=[annotation_file]
        )
        dataset_client.register_dataset(ds)
    return aml_ds

def create_barplot(ean: list, ean_acc: list) -> matplotlib.figure.Figure:
    """
    Function to create custom barplot for AML Metrics Dashboard.
    The plot contains the average accuracy per individual product (EAN Level).

    Args:
        ean (list): List of EAN
        ean_acc (list): List of average accuracies

    Returns:
        matplotlib figure: Custom figure
    """

    unsorted_list = [(each_ean_acc, each_ean) for each_ean, each_ean_acc in zip(ean, ean_acc)]
    sorted_list = sorted(unsorted_list, reverse=True)

    ean_sorted = []
    ean_acc_sorted = []

    for i in sorted_list:
        ean_sorted += [i[1]]
        ean_acc_sorted += [i[0]]

    fig = plt.figure(figsize=(30,30), facecolor='white')
    plt.rc('font', size=20) 
    plt.bar(ean_sorted, ean_acc_sorted)
    plt.title("Individual Accuracy")
    plt.xlabel("EAN")
    plt.ylabel("Accuracy per EAN")
    plt.xticks(rotation=90)
    plt.tight_layout()

    return fig
