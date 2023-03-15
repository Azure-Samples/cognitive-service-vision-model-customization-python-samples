# Cognitive Service Vision Model Customization using Python

## Intro

Cognitive Service Vision Model Customization is a model training service that allows users like developers to easily train an image classification model (Multiclass only for now) or object detection model, with low-code experience and very little understanding in machine learning or computer vision required.

This is a sample repository demonstrating how to train and predict a custom model with Cognitive Service for Vision, using Python. To get started, checkout [this tutorial in Python notebook](./docs/cognitive_service_vision_model_customization.ipynb).

## Existing Custom Vision (customvision.ai) Customers

Refer to [export_cvs_data_to_blob_storage.ipynb](./docs/export_cvs_data_to_blob_storage.ipynb) for instructions or directly run [export_cvs_data_to_blob_storage.py](cognitive_service_vision_model_customization_python_samples/data/export_cvs_data_to_blob_storage.py) to export Custom Vision images and annotations to your own blob storage, which can be later used for model customization training.

Once data is exported, you can use it with Cognitive Service Vision Model Customization.

## FAQ

For frequently asked questions or quick trouble shoot, checkout [FAQ](./docs/faq.md), including things like trouble shooting guide, quota information, etc.

## RESTful API & SDK

If you would like to exlpore more functionalities offered in Cognitive Service Vision, you can refer to [this link](https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/image-analysis-client-library-40?pivots=programming-language-python&tabs=visual-studio%2Cwindows) for a quick start.

For more documentation,

- API: [Here](https://learn.microsoft.com/en-us/rest/api/computervision/2023-02-01-preview/models)
- SDK: [Here](https://github.com/Azure-Samples/azure-ai-vision-sdk/tree/main/samples/python/image-analysis) (note that model customization training is not supported in this SDK yet, while prediction is supported.)
