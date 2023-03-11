from typing import List, Union
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import Image, ImageTag, ImageRegion, Project
from msrest.authentication import ApiKeyCredentials
import argparse
import time
import json
import pathlib
import logging
from azure.storage.blob import ContainerClient, BlobClient
import multiprocessing


N_PROCESS = 8


def get_file_name(sub_folder, image_id):
    return f'{sub_folder}/images/{image_id}'


def blob_copy(params):
    container_client, sub_folder, image = params
    blob_client: BlobClient = container_client.get_blob_client(get_file_name(sub_folder, image.id))
    blob_client.start_copy_from_url(image.original_image_uri)
    return blob_client


def wait_for_completion(blobs, time_out=5):
    pendings = blobs
    time_break = 0.5
    while pendings and time_out > 0:
        pendings = [b for b in pendings if b.get_blob_properties().copy.status == 'pending']
        if pendings:
            logging.info(f'{len(pendings)} pending copies. wait for {time_break} seconds.')
            time.sleep(time_break)
            time_out -= time_break


def copy_images_with_retry(pool, container_client, sub_folder, images: List, batch_id, n_retries=5):
    retry_limit = n_retries
    urls = []
    while images and n_retries > 0:
        params = [(container_client, sub_folder, image) for image in images]
        img_and_blobs = zip(images, pool.map(blob_copy, params))
        logging.info(f'Batch {batch_id}: Copied {len(images)} images.')
        urls = urls or [b.url for _, b in img_and_blobs]

        wait_for_completion([b for _, b in img_and_blobs])
        images = [image for image, b in img_and_blobs if b.get_blob_properties().copy.status in ['failed', 'aborted']]
        n_retries -= 1
        if images:
            time.sleep(0.5 * (retry_limit - n_retries))

    if images:
        raise RuntimeError(f'Copy failed for some images in batch {batch_id}')

    return urls


class CocoOperator:
    def __init__(self):
        self._images = []
        self._annotations = []
        self._categories = []
        self._category_name_to_id = {}

    @property
    def num_imges(self):
        return len(self._images)

    @property
    def num_categories(self):
        return len(self._categories)

    @property
    def num_annotations(self):
        return len(self._annotations)

    def add_image(self, width, height, coco_url, file_name):
        self._images.append(
            {
                'id': len(self._images) + 1,
                'width': width,
                'height': height,
                'coco_url': coco_url,
                'file_name': file_name,
            })

    def add_annotation(self, image_id, category_id_or_name: Union[int, str], bbox: List[float] = None):
        self._annotations.append({
            'id': len(self._annotations) + 1,
            'image_id': image_id,
            'category_id': category_id_or_name if isinstance(category_id_or_name, int) else self._category_name_to_id[category_id_or_name]})

        if bbox:
            self._annotations[-1]['bbox'] = bbox

    def add_category(self, name):
        self._categories.append({
            'id': len(self._categories) + 1,
            'name': name
        })

        self._category_name_to_id[name] = len(self._categories)

    def to_json(self) -> str:
        coco_dict = {
            'images': self._images,
            'categories': self._categories,
            'annotations': self._annotations,
        }

        return json.dumps(coco_dict, ensure_ascii=False, indent=2)


def log_project_info(training_client: CustomVisionTrainingClient, project_id):
    project: Project = training_client.get_project(project_id)
    proj_settings = project.settings
    project.settings = None
    logging.info(f'Project info dict: {project.__dict__}')
    logging.info(f'Project setting dict: {proj_settings.__dict__}')
    logging.info(f'Project info: n tags: {len(training_client.get_tags(project_id))},'
                 f' n images: {training_client.get_image_count(project_id)} (tagged: {training_client.get_tagged_image_count(project_id)},'
                 f' untagged: {training_client.get_untagged_image_count(project_id)})')


def export_data(azure_storage_account_name, azure_storage_key, azure_storage_container_name, custom_vision_endpoint, custom_vision_training_key, custom_vision_project_id, n_process):
    azure_storage_account_url = f"https://{azure_storage_account_name}.blob.core.windows.net"
    container_client = ContainerClient(azure_storage_account_url, azure_storage_container_name, credential=azure_storage_key)
    credentials = ApiKeyCredentials(in_headers={"Training-key": custom_vision_training_key})
    trainer = CustomVisionTrainingClient(custom_vision_endpoint, credentials)

    coco_operator = CocoOperator()
    for tag in trainer.get_tags(custom_vision_project_id):
        coco_operator.add_category(tag.name)

    skip = 0
    batch_id = 0
    project_name = trainer.get_project(custom_vision_project_id).name
    log_project_info(trainer, custom_vision_project_id)
    sub_folder = f'{project_name}_{custom_vision_project_id}'
    with multiprocessing.Pool(n_process) as pool:
        while True:
            images: List[Image] = trainer.get_images(project_id=custom_vision_project_id, skip=skip)
            if not images:
                break
            urls = copy_images_with_retry(pool, container_client, sub_folder, images, batch_id)
            for i, image in enumerate(images):
                coco_operator.add_image(image.width, image.height, urls[i], get_file_name(sub_folder, image.id))
                image_tags: List[ImageTag] = image.tags
                image_regions: List[ImageRegion] = image.regions
                if image_regions:
                    for img_region in image_regions:
                        coco_operator.add_annotation(coco_operator.num_imges, img_region.tag_name, [img_region.left, img_region.top, img_region.width, img_region.height])
                elif image_tags:
                    for img_tag in image_tags:
                        coco_operator.add_annotation(coco_operator.num_imges, img_tag.tag_name)

            skip += len(images)
            batch_id += 1

    coco_json_file_name = 'train.json'
    local_json = pathlib.Path(coco_json_file_name)
    local_json.write_text(coco_operator.to_json(), encoding='utf-8')
    coco_json_blob_client: BlobClient = container_client.get_blob_client(f'{sub_folder}/{coco_json_file_name}')
    if coco_json_blob_client.exists():
        logging.warning(f'coco json file exists in blob. Skipped uploading. If existing one is outdated, please manually upload your new coco json from ./train.json to {coco_json_blob_client.url}')
    else:
        coco_json_blob_client.upload_blob(local_json.read_bytes())
        logging.info(f'coco file train.json uploaded to {coco_json_blob_client.url}.')


def parse_args():
    parser = argparse.ArgumentParser('Export Custom Vision workspace data to blob storage, with annotations in coco format.')

    parser.add_argument('--custom_vision_project_id', '-p', type=str, required=True, help='Custom Vision Project Id.')
    parser.add_argument('--custom_vision_training_key', '-k', type=str, required=True, help='Custom Vision training key.')
    parser.add_argument('--custom_vision_endpoint', '-e', type=str, required=True, help='Custom Vision endpoint.')

    parser.add_argument('--azure_storage_account_name', '-a', type=str, required=True, help='Azure storage account name.')
    parser.add_argument('--azure_storage_account_key', '-t', type=str, required=True, help='Azure storage account key.')
    parser.add_argument('--azure_storage_container_name', '-c', type=str, required=True, help='Azure storage container name.')

    parser.add_argument('--n_process', '-n', type=int, required=False, default=8, help='Number of processes used in exporting data.')

    return parser.parse_args()


def main():
    args = parse_args()

    export_data(args.azure_storage_account_name, args.azure_storage_account_key, args.azure_storage_container_name,
                args.custom_vision_endpoint, args.custom_vision_training_key, args.custom_vision_project_id, args.n_process)


if __name__ == '__main__':
    main()
