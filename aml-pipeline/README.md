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

- Create AML Workspace
- Clone repo

#### Steps for dataset:

- create a storage account/container
- run script to modify coco json 
- upload dataset + coco to container via Azure Portal
- register the datastore + dataset

#### For Florence/UVS:

- Create Compute Vision resource
- Enable managed identity
- Assign Blob Storage Contributor rights to CV MI