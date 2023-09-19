# FAQ

## What is the max number of images accepted for training? What is the max number of hours accepted for training budget?

For quota limit information, please refer to [quota_limit.md](./quota_limit.md)

## Why does my training take longer/shorter than my specified budget?

There are three concetps:

- Specified training budget time
- Billing training time
- Real-world elapsed training time, aka wall clock time.

It's important to clarify that both the budget specified and the actual training time charged refer to compute time, not the real-world elapsed time. The training time billed will be never over your specified budget. Sometimes it might be way shorter than your specifid training budget, due to the training engine determining that further exploration isn't beneficial and completes the training before the budget is exhausted.

The **billing training time** can be different than **real-world elapsed training time** for the following reasons.

### Real-world elapsed training time might take longer

**Example**: With 2 hours budget specified, training starts at 3PM PST and finishes at 11PM PST (8 hours real-world elapsed time), and got billed for 2 hours training.

- **High Training Traffic**: If many users are training simultaneously, GPU resources can become limited. This might cause your job to be queued or paused, extending the duration.
Backend Failures: Sometimes training can encounter expected or unexpected issues. Our system often retries after failures, and while the failed runs don’t count against your budget, they can extend the overall training time.
- **Data Storage Location**: If your data is stored in a region different from where your computer vision resource is located, it can take longer to transmit, thus adding to the training time.

### Real-world elapsed training time might be shorter

**Example**: With 10 hours budget specified, training starts at 2PM PST and finishes at 6PM PST (4 hours real-world elapsed time), and got billed for 9 hours training.

- **Use of Multi-GPU**: Depending on your data size and complexity, the service might use multiple GPUs, which can reduce the actual training time.
- **Concurrent Exploration Trials**: The service can run multiple exploration trials using different GPUs simultaneously.
- **Upgraded GPU Models**: Occasionally, the service might use more advanced or faster GPU models, which can expedite training.

## Why does my training fail and what I should do?

Some common failures:

- **diverged**: It means the training cannot learn meaningful things from your data. Some common causes are
  - Data is not enough: provide more data should help
  - Data is of bad quality: check if your images are of very low resolution, aspect ratio being very extreme, or annotations are wrong
- **notEnoughBudget**: it means your specified budget is not enough for the size of your dataset and model kind you are training
  - When you see this error, you can find a minimum budget required and a suggested budget in the training error message
  - We provide you with a rough upfront minimum budget to train your model effectively and a recommended budget for optimal model quality. It's important to note that the minimum budget ensures basic model functionality. Investing sufficient budget into the training allows us to allocate more computational power and fine-tune the model extensively, leading to better outcomes.
    - **Generic-Classifier**: the miminum budget is: **0.0003334 * num_images** hours. For optimal quality, try at least 5-10x higher than the min budget.
    - **Generic-Detector**: the minimum budget hours is: **0.0066667 * num_images** hours. For optimal quality, try at least 3-5x higher than the min budget.
    - **Product-Recognizer**: the minimum budget hours is: **0.0003334 * num_images * average_boxes_per_images** hours. For optimal quality, try at least 2-4x higher than the min budget.
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
