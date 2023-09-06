# Model Quality FAQ

This documentation covers the knowledge, tips and good practice about training a model aiming for the best AI quality wtih Model Customization Service.

## Data Preparation

- Meaningful category names: Cognitive Service Vision Model Customization utilized both image and text information in training, thus having meaningful category names can improve model quality
- Training dataset:
  - Keeping training dataset as close as possible to your production setting is essential to make sure your model works after being deployed. A bad example would be collecting a few images of bobcats from web, train an object detector and use the model to detect your pet cat in your house
  - keeping dataset balanced (each class is evenly represented in the dataset), if possible, can improve model quality
  - W.r.t. data, the more, the better; the more diverse, the better
  - Very low resolution images could make it hard to train a good model. Try keep the image resolution at a reasonable size (e.g., 800x600), to retain enough details.
- Evaluation dataset:
  - It is critical to have a meaningful evalution set large enough, close to your production setting to make an verdict on the quality of the your trained model
  - When production setting changes, it is also recommended to update your evalution dataset, and re-evaluate your model to see if new round of data collection and model training is required
- Object detection
  - Bounding boxes being too small compared with image size can be problematic for training. Taking a 1080P image (1920x1080) as an example, it would be helpful to keep your bounding boxes larger than (80x40). Note that this could be a minimum requirement for the model to start gaining a reasonabel model quality but not the best.

## Training

- Specifing sufficient budget is key to good model quality. With insufficient budget, service can be limited in finding the best model for you
