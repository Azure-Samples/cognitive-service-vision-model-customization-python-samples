# Quota Limit

## Training

|                                    | Generic IC                      | Generic OD                      | Product Recognition             |
| ---------------------------------- | ------------------------------- | ------------------------------- | ------------------------------- |
| Max # training hours*              | 336 (14 compute days)           | 1344 (56 compute days)          | 336 (14 compute days)           |
| Max # training images              | 1,000,000                       | 200,000                         | 50,000                          |
| Min # training images per category | 2                               | 2                               | 1                               |
| Max # tags per image               | multiclass: 1                   | NA                              | NA                              |
| Max # regions per image            | NA                              | 1,000                           | 1,000                           |
| Max # categories                   | 3,000                           | 1,500                           | 1,000                           |
| Min # categories                   | 2                               | 1                               | 1                               |
| Max image size                     | 20MB                            | 20MB                            | 20MB                            |
| Max image width/height             | 10,240                          | 10,240                          | 10,240                          |
| Min image width/height             | 10                              | 10                              | 10                              |
| Available regions                  | West US 2, East US, West Europe | West US 2, East US, West Europe | West US 2, East US, West Europe |
| Accepted image types               | jpg, png, bmp, gif, jpeg        | jpg, png, bmp, gif, jpeg        | jpg, png, bmp, gif, jpeg        |

`*` Note that compute hours/days is different than wall-clock time. The wall-clock time can vary based on a a few things (seen in [faq.md](./faq.md#why-does-my-training-take-longershorter-than-my-specified-budget)), e.g., the service might run trainings with 4 GPUs which can roughly shortens the wall-clock time by 3-4 times.

## Prediction/Evaluation

|                                      | Generic IC                      | Generic OD                      | Product Recognition             |
| ------------------------------------ | ------------------------------- | ------------------------------- | ------------------------------- |
| Max # evaluation images              | 100,000                         | 100,000                         | 10,000                          |
| Min # evaluation images per category | 1                               | 1                               | 1                               |
| Max # tags per image                 | multiclass: 1                   | NA                              | NA                              |
| Max # regions per image              | NA                              | 1,000                           | 1,000                           |
| Max # categories                     | 3,000                           | 1,500                           | 1,000                           |
| Min # categories                     | 2                               | 1                               | 1                               |
| Max image size                       | Sync: 6MB, Batch: 20MB          | Sync: 6MB, Batch: 20MB          | Sync: 6MB, Batch: 20MB          |
| Max image width/height               | 16,000                          | 16,000                          | 16,000                          |
| Min image width/height               | 50                              | 50                              | 50                              |
| Available regions                    | West US 2, East US, West Europe | West US 2, East US, West Europe | West US 2, East US, West Europe |
| Accepted image types                 | jpg, png, bmp, gif, jpeg        | jpg, png, bmp, gif, jpeg        | jpg, png, bmp, gif, jpeg        |
