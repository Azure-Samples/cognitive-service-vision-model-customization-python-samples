# Model Quality FAQ

This documentation covers the knowledge, tips and good practice about training a model aiming for the best AI quality wtih Model Customization Service.

## Data Preparation

- Meaningful category names: Cognitive Service Vision Model Customization utilized both image and text information in training, thus having meaningful category names can improve model quality
- Training dataset:
  - Keeping training dataset as close as possible to your production setting is essential to make sure your model works after being deployed. A bad example would be collecting a few images of tom cats from web, train an object detector and use the model to detect your pet cat in your house
  - Most of time, keeping dataset balanced (each class is evenly represented in the dataset), if possible, can improve model quality
  - If possible, for data, the more, the better; the more diverse, the better
  - Very low resolution images could make it hard to train a good model. Try keep the image resolution at a reasonable size (e.g., 800x600).
- Evaluation dataset:
  - It is critical to have a meaningful evalution set large enough, close to your production setting to make an verdict on the quality of the your trained model
  - When production setting changes, it is also recommended to update your evalution dataset
- Object detection
  - Bounding boxes being too small compared with image size can be problematic for training. Taking a 1080P image (1920x1080) as an example, it would be helpful to keep your bounding boxes larger than (40x20). Note that this is just an example, for some problem, it could be better to have bounding boxes larger than (80x40) for 1080P images.

## Training

- Specifing sufficient budget is key to good model quality. With insufficient budget, service can be limited in finding the best model for you
