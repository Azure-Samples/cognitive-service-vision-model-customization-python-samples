# Cognitive Service Vision Model Customization using Python

## Intro

Cognitive Service Vision Model Customization is a model training service that allows users like developers to easily train an image classification model (Multiclass only for now) or object detection model, with low-code experience and very little understanding in machine learning or computer vision required.

This is a sample repository demonstrating how to train and predict a custom model with Cognitive Service for Vision, using Python. To get started, checkout [this tutorial in Python notebook](./tutorial.ipynb).

## Existing Custom Vision (customvision.ai) Customers

Refer to [export_cvs_data_to_blob_storage.ipynb](export_cvs_data_to_blob_storage.ipynb) for instructions or directly run [export_cvs_data_to_blob_storage.py](cognitive_service_vision_model_customization_python_samples/data/export_cvs_data_to_blob_storage.py) to export Custom Vision images and annotations to your own blob storage, which can be later used for model customization training.

Once data is exported, you can use it with Cognitive Service Vision Model Customization.

## FAQ

For frequently asked questions or quick trouble shoot, checkout [FAQ](FAQ.md), including things like trouble shooting guide, quota information, etc.
