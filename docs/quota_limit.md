# Quota Limit

|                                     | Generic IC                      | Generic OD                      |
| ----------------------------------- | ------------------------------- | ------------------------------- |
| Max # training hours*               | 336 (14 compute days)           | 1344 (56 compute days)          |
| Max # training images               | 1,000,000                       | 200,000                         |
| Max # evaluation images             | 100,000                         | 100,000                         |
| Min # training images per category  | 2                               | 2                               |
| Max # tags per image                | multiclass: 1                   | NA                              |
| Max # regions per image             | NA                              | 1,000                           |
| Max # categories                    | 2,000                           | 1,000                           |
| Min # categories                    | 2                               | 1                               |
| Max image size (Training)           | 20MB                            | 20MB                            |
| Max image size (Prediction)         | Sync: 6MB, Batch: 20MB          | Sync: 6MB, Batch: 20MB          |
| Max image width/height (Training)   | 10,240                          | 10,240                          |
| Min image width/height (Training)   | 10                              | 10                              |
| Min image width/height (Prediction) | 50                              | 50                              |
| Available regions                   | West US 2, East US, West Europe | West US 2, East US, West Europe |
| Accepted image types                | jpg, png, bmp, gif, jpeg        | jpg, png, bmp, gif, jpeg        |

* Note that compute hours/days is different than wall-clock time. The wall-clock time can vary based on a a few things (seen in [faq.md](./faq.md#why-does-my-training-take-longershorter-than-my-specified-budget)), e.g., the service might run trainings with 4 GPUs which can roughly shortens the wall-clock time by 3-4 times.
