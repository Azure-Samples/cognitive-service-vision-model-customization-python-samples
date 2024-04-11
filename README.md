# Azure Cognitive Services Computer Vision - Python SDK Samples

## Model Customization

Computer Vision's Model Customization is a custom model training service that allows users like developers to easily train an image classification model (Multiclass only for now) or object detection model, with low-code experience and very little understanding of machine learning or computer vision required. The service is available in regions: West US 2, East US, West Europe.

This is a sample repository demonstrating how to train and predict a custom model with Cognitive Service for Vision, using Python. To get started, check out [this tutorial in Python notebook](./docs/cognitive_service_vision_model_customization.ipynb).

Moreover, you can use your familiar Azure Machine Learning (AML) environment and Data Science Tools (AML Data Assets or Jobs, CLIv2 or MLFlow) for training and evaluating your custom Florence model following [this documentation](./aml-pipeline/README.md).

### Product Recognition

One of the scenarios we would like to introudce as a model customization scenario is Product Recognition. Computer Vision's product recognition service has been designed to be used in retail scenarios, where users would like to detect products, such as Consumer Packaged Goods (CPG), on a shelf. It comes with a set of APIs, a pre-built AI model, and a custom AI model that can be trained following the model customization guide above. You can try these out by following tutorials in Python notebooks: 
* **[Image Composition](./docs/cognitive_service_vision_image_composition.ipynb)**: for stitching together the segmented shelf images using Image Stitching API, as well as adjusting any slanted or squished shelf images to a correct orientation using Image Rectification API
* **[Product Recognition](./docs/cognitive_service_vision_product_recognition.ipynb)**: for detecting products and gaps on a shelf image using a pre-built model, and individually classifying the detected products using customized model, both using Product Understanding API
* **[Planogram Compliance](./docs/cognitive_service_vision_planogram_compliance.ipynb)**: for assessing the matchings between a planogram schema and the detected products on a shelf using Planogram Compliance API

### Existing Custom Vision (customvision.ai) Customers

Refer to [export_cvs_data_to_blob_storage.ipynb](./docs/export_cvs_data_to_blob_storage.ipynb) for instructions or directly run [export_cvs_data_to_blob_storage.py](cognitive_service_vision_model_customization_python_samples/data/export_cvs_data_to_blob_storage.py) to export Custom Vision images and annotations to your own blob storage, which can be later used for model customization training.

Once data is exported, you can use it with Cognitive Service Vision Model Customization.

### RESTful API & SDK

If you would like to explore more functionalities offered in Cognitive Service Vision, you can refer to [this link](https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/image-analysis-client-library-40?pivots=programming-language-python&tabs=visual-studio%2Cwindows) for a quick start.

### FAQ & Docs

For frequently asked questions or quick troubleshooting, check out [FAQ](./docs/faq.md), including things like troubleshooting guides, quota information, etc.

For more documentation, check out:

- API: [Here](https://learn.microsoft.com/en-us/rest/api/computervision/2023-02-01-preview/models)
- SDK: [Here](https://github.com/Azure-Samples/azure-ai-vision-sdk/tree/main/samples/python/image-analysis) (note that model customization training and product recognition are not supported in this SDK yet, while prediction is supported.)
