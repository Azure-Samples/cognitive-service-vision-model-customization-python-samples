# **Guide to Optimal AI Quality with Model Customization Service**

This guide outlines essential tips, insights, and best practices for ensuring top-tier AI performance using the Model Customization Service.

## **1. Data Preparation**

- **Descriptive Category Names:** The Vision Model Customization of Cognitive Service employs both image and text for training. Opt for clear and descriptive category names to boost the model's effectiveness.

## **2. Training Dataset**

- **Alignment with Production Needs:** Your training data should mirror the actual use-case scenario. For example, a model trained with a few internet images of wild tomcats might not effectively recognize a domesticated house cat.
- **Dataset Balance:** Aim for a dataset where every category is equally represented. Such balance can amplify the model's precision.
- **Dataset Size and Diversity:** Generally, comprehensive and varied datasets lead to superior outcomes.
- **Image Quality:** Low-quality images can obstruct efficient training. Ideally, images should be at least 800x600 pixels.

## **3. Evaluation Dataset**

- **Relevance and Size:** Ensure your evaluation set is significant and mirrors your operational setting. This helps in gauging your model's real-world efficiency.
- **Adaptability:** Regularly update the evaluation set, especially if there are shifts in the operational environment.

## **4. Object Detection**

- **Bounding Box Proportions:** If bounding boxes are too small compared to the entire image, it could hamper training. For a 1080P image (1920x1080), it's advisable for bounding boxes to be a minimum of (40x20) pixels. Depending on the context, (80x40) pixels might be even more suitable.

## **5. Training Budget**

- **Adequate Funding:** Ensure sufficient budget allocation. A constrained budget can limit the service's capability to determine the best-suited model for your requirements.
