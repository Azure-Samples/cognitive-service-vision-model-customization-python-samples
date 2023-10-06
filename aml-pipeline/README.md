```az ml job create -f azure-ml-job.yaml --resource-group kz-aml-rg --workspace-name kz-aml --set inputs.uvs_resource_key="<cogs_key>"```

TODO:
- UVS/Cogs
  - Document Create CogS resource and request access for public preview
  - https://aka.ms/visionaipublicpreview
- Dataset
  - Document format requirements (COCO)
  - Document registration/upload in AML
  - Document Managed Identity access for UVS/CogS to storage account

## Dataset Adjustment and Upload to AML
- cd cognitive-service-vision-model-customization-python-samples/aml-pipeline
- run python adjust_coco.py -s 'new_blob_name'
- Register Dataset in AML

### Documentation:

#### Prerequisites:
Required Azure Resources:
- **[Azure Machine Learning](https://ml.azure.com/)**
- **[Azure AI Vision Studio](https://portal.vision.cognitive.azure.com/)**
- **[Azure Storage Account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal)**

### Preparations for Model Training:
- #### Clone repository
- #### Data Set:
  - Create a new folder in Storage Account: "cats-dogs"
  - Modify coco_url in [coco json file](aml-pipeline/data/cats_dogs/coco_info.json) by running ```python adjust_coco.py -s 'your_storage_account_name'```
  - Upload adjusted coco json file and associated images to Blob Container "cats-dogs"
  - Register Datastore and DataAsset in AML
- #### Florence Model/UVS:
  - Enable Managed Identity for Azure AI Vision: ![](docs/image-1.png)
  - Assign Storage Blob Data Contributor Role for Managed Identity:
    - Select Role ![](docs/image-2.png)
    - Select Storage Blob Data Contributor ![](docs/image-3.png)
    - Assign access to Managed Identity ![](docs/image-4.png)
    - Review and Assign ![](docs/image-5.png)

#### Steps for dataset:

- create a storage account/container
- run script to modify coco json 
- upload dataset + coco to container via Azure Portal
- register the datastore + dataset

#### For Florence/UVS:

- Create Compute Vision resource
- Enable managed identity
- Assign Blob Storage Contributor rights to CV MI