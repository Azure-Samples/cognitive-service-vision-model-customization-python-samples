```az ml job create -f azure-ml-job.yaml --resource-group kz-aml-rg --workspace-name kz-aml --set inputs.uvs_resource_key="<cogs_key>"```

TODO:
- UVS/Cogs
  - Document Create CogS resource and request access for public preview
  - https://aka.ms/visionaipublicpreview
  - UVS/CogS resource key - remove hardcoded value from aml job yaml
    - Check if we can pass input arguments in the aml job command
- Dataset
  - Document format requirements (COCO)
  - Document registration/upload in AML
  - Document Managed Identity access for UVS/CogS to storage account
