FROM python:3.8.13-bullseye


RUN apt-get update && apt-get install -y git
RUN pip install 'azureml-core==1.49.0' \
                'azureml-mlflow' \
                'mlflow-skinny' \
                'pytest' \
                'wheel' \
                'matplotlib' \
                'pandas' \
                'scikit-learn' \
                'torch' \
                'torchvision' \
                'pillow' \
                'loguru' \
                # 'cognitive-service-vision-model-customization-python-samples==0.0.5' \
                'git+https://github.com/karolzak/cognitive-service-vision-model-customization-python-samples'
