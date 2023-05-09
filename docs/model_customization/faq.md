
# FAQ

## What is the max number of images accepted for training? What is the max number of hours accepted for training budget?

For quota limit information, please refer to [quota_limit.md](./quota_limit.md)

## Why does my training take longer/shorter than my specified budget?

Note that the budget specified and actual charged training time are actual **compute time**, not wall-clock time. Some common reasons for the difference are listed below:

### Longer than specified budget

- When there is a high training traffic, the GPU resources might be tight and your job might stay in queue or be on hold during training
- Training in our backend runs into un/expected failures, which results in retrying logic. As the failed runs do not consume your budget, this can lead to longer training time in general
- Your data is stored in a different region than your created computer vision resource, which will lead to longer data transmission time.

### Shorter than specified budget

- The service sometimes trains with multi-GPU depending on your data, which shortens wall-clock training time
- The service sometimes trains multiple exploration trials on multiple GPUs at the same time
- The service sometimes uses premier/faster GPU skus to train
- The service decided there is no need to explore futher before budget runs out

The first three speed up training at the cost of using more budget in certain wall-clock time.

## Why does my training fail and what I should do?

Some common failures:

- **diverged**: It means the training cannot learn meaningful things from your data. Some common causes are
  - Data is not enough: provide more data should help
  - Data is of bad quality: check if your images are of very low resolution, aspect ratio being very extreme, or annotations are wrong
- **notEnoughBudget**: it means your specified budget is not enough for the size of your dataset and model kind you are training. Specify more budget please
- **datasetCorrupt**: Usually this is due to the fact that your provided annoation files or images are not accessible or annotation file is of wrong format. For annotation check, you can check [`cognitive_service_vision_model_customization.ipynb`](cognitive_service_vision_model_customization.ipynb) for annotation format documentation and run [`check_coco_annotation.ipynb`](check_coco_annotation.ipynb) for a quick check. You can check the error message returned from the API call response for dataset format violation as well
- **datasetNotFound**: dataset cannot be found
- **unknown**: It could be our system's issue, please reach out to us for investigation

## Why does the evaluation run fail?

Below are the possible reasons:

- **internalServerError**: An unknown error occurred. Please try again later.
- **modelNotFound**: The specified model was not found.
- **datasetNotFound**: The specified dataset was not found.
- **datasetCorrupt**: Usually this is due to the fact your provided annoation files or images are not accessible or annotation file is of wrong format. For annotation check, you can check [`cognitive_service_vision_model_customization.ipynb`](cognitive_service_vision_model_customization.ipynb) for annotation format documentation and run [`check_coco_annotation.ipynb`](check_coco_annotation.ipynb) for a quick check. You can check the error message returned from the API call response for dataset format violation as well.
- **incorrectModelKind**: Model kind is not compatible to be evaluated on the selected dataset, e.g. evaluate a classification model on a detection dataset.

## Why does my dataset registery fail?

The API reponse should be informative enough. Normally,

- **DatasetAlreadyExists**: A dataset with the same name exists
- **DatasetInvalidAnnotationUri**: "An invalid uri was provided among the annotation uris at dataset registration time.

## Can I controll the hyper-parameters or use my own models in training?

No, model customization service is a low-code AutoML training system that takes care of the hyper-param search and base model selection in the backend.

## Can I export my model after training?

Not for now, currently only cloud inference via prediction API is supported (see [`cognitive_service_vision_model_customization.ipynb`](cognitive_service_vision_model_customization.ipynb) for example). We have the plan of supporting container export for future.

## What are the metrics used for evaluating the models?

`https://github.com/microsoft/vision-evaluation` contains the metrics code we use for model evaluation.

## What is the reported evaluation result when an evaluation set is not provided?

During training, a random subset $S$ is held out from training data for hyper-parameter tuning, UVS chooses the optimal hyper-parameters which achieve the best evaluation metrics $M$ computed on $S$. Last, all training data (including $S$) is used for a final train with the optimal hyper-parameters. If an evaluation set is not provided, $M$ is reported as evaluation result for model performance estimation.

## How many images are required for a reasonble/good/best model quality?

Short answer is the more the better.

Although Florence models have great few-shot capability, i.e. achieving great model performance under limited data availability, in general more data makes your trained model better and more robust. Moreover, some problem is easy requiring little data (classify an apple against a banana), while some problem is hard requiring more data (detecting 200 kinds of insects in a rain forest.), which makes it hard for us to give a universal recommendation here.

If data labeling budget is under constraints, our recommended workflow is to repeat the following steps:

1. Collect $N$ images per class, where $N$ images per class are quite easy for you to collect, e.g., $N=3$
2. Train a model, and test on your evaluation set
3. If the model performance is
    - **Good enough** (performance is better than your expectation or performance close to your previous experiment with less data collected): Stop here and use this model.
    - **Not good** (performance is still below your expectation or better than your previous experiment with less data collected at a reasonable margin):
      - Collect $\delta$ more images, and go back to Step 2 (pick the $\delta$ that following the same guidance with step 1)
      - If you notice the performance is not improving any more even with a few rounds of (data collection, train), it could be because
        - this problem is not well-defined, or too hard: reach out to us for case-by-case analysis
        - the evalaution data might be problematic or too little: Collect more evalution data for reliable and robust guidance/evaluation and check if there are wrong annotations, or very low-pixel images. Make sure training and evaluation data don't have domain gap
        - the training data might be of low quality: check if there are wrong annotations, or very low-pixel images

For more model qualtiy questions, please refer to [model_quality_faq.md](model_quality_faq.md).

## How much training budget should I specify

Short answer is to specify the upper limit of budget you are willing to consume. We have an AutoML system in our backend to try out different models/training recipes to find the best model for your problem/data. The more budget given, the higher chance of finding a better model.

Our AutoML system also stops automatically, if it thinks there is no need to try more, even if there is still remaining budget, i.e., it does not always exhaust your specified budget. You are guanranteed not to be billed over your specified budget as well.

We are adding a budget suggestion API to help you pick the right budget, which will come later.
