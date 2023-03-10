import argparse
import pathlib
import json
import logging
from typing import List
from tqdm import tqdm


from cognitive_service_vision_model_customization_python_samples import AnnotationKind

OD_LOWER_IMAGE_LIMIT_PER_TAG = 2
IC_LOWER_IMAGE_LIMIT_PER_TAG = 2
OD_UPPER_IMAGE_LIMIT = 200000
IC_UPPER_IMAGE_LIMIT = 1000000
MAX_IMAGE_DIM = 10240
OD_MAX_CATEGORIES = 1000
IC_MAX_CATEGORIES = 2000
OD_MIN_CATEGORIES = 1
IC_MIN_CATEGORIES = 2


def check(condition, err_msg):
    if not condition:
        raise ValueError(err_msg)


def field_present_and_has_value_check(coco_dict: dict, custom_message: str, field_name: str):
    check(coco_dict.get(field_name) is not None, f'"{field_name}" field missing or None. {custom_message}.')


def fields_present_and_has_value_check(coco_dict: dict, custom_message: str, *field_names):
    for name in field_names:
        field_present_and_has_value_check(coco_dict, custom_message, name)


def id_value_range_check(id: int, max_id: int, id_name: str, custom_message: str):
    check(isinstance(id, int) and 0 < id <= max_id, f'{id_name} must be integer in [1, {max_id}], {id} found. {custom_message}.')


def bbox_check(bbox: List, custom_message):
    check(len(bbox) == 4, f'bbox must be of 4 floats. {len(bbox)} found. {custom_message}')
    left, top, width, height = bbox
    check(0 <= left < 1.0, f'left must be in [0, 1). {left} found. {custom_message}')
    check(0 <= top < 1.0, f'top must be in [0, 1). {top} found. {custom_message}')
    check(0.0 < width <= 1.0, f'width must be in (0, 1]. {width} found. {custom_message}')
    check(0.0 < height <= 1.0, f'height must be in (0, 1]. {width} found. {custom_message}')
    check(left + width <= 1.0, f'left + width must be in (0, 1]. {left + width} found. {custom_message}')
    check(top + height <= 1.0, f'top + height must be in (0, 1]. {top + height} found. {custom_message}')


def image_check(image: dict, max_id: int):
    img_msg = f'image with id = {image.get("id")}'
    fields_present_and_has_value_check(image, img_msg, 'id', 'width', 'height', 'file_name')
    check(('coco_url' in image) or ('absolute_url' in image), f'Neither "coco_url" nor "absolute_url" present. {img_msg}.')
    check(image['width'] and image['width'] > 0 and image['width'] <= MAX_IMAGE_DIM, f'width must be present and in (0, {MAX_IMAGE_DIM}]. {img_msg}.')
    check(image['height'] and image['height'] > 0 and image['width'] <= MAX_IMAGE_DIM, f'height must be present and in (0, {MAX_IMAGE_DIM}]. {img_msg}.')
    id_value_range_check(image['id'], max_id, 'id', img_msg)


def category_check(catetory: dict, max_id: int):
    category_msg = f'image with id = {catetory.get("id")}'
    fields_present_and_has_value_check(catetory, category_check, 'id', 'name')
    id_value_range_check(catetory['id'], max_id, 'id', category_msg)


def annotation_check(annotation: dict, data_type: str, max_id: int, max_img_id: int, max_category_id: int):
    ann_msg = f'annotation with id = {annotation.get("id")}'
    fields_present_and_has_value_check(annotation, ann_msg, 'id', 'image_id', 'category_id')
    if data_type == AnnotationKind.OBJECT_DETECTION:
        fields_present_and_has_value_check(annotation, ann_msg, 'bbox')
        bbox_check(annotation['bbox'], ann_msg)

    id_value_range_check(annotation['image_id'], max_img_id, 'image_id', ann_msg)
    id_value_range_check(annotation['category_id'], max_category_id, 'category_id', ann_msg)
    id_value_range_check(annotation['id'], max_id, 'id', ann_msg)


def images_check(images: List, data_type: str):
    if data_type == AnnotationKind.OBJECT_DETECTION:
        check(len(images) >= OD_LOWER_IMAGE_LIMIT_PER_TAG and len(images) <= OD_UPPER_IMAGE_LIMIT, f'Number of images must be in [{OD_LOWER_IMAGE_LIMIT_PER_TAG}, {OD_UPPER_IMAGE_LIMIT}].')
    else:
        check(len(images) >= IC_LOWER_IMAGE_LIMIT_PER_TAG and len(images) <= IC_UPPER_IMAGE_LIMIT, f'Number of images must be in [{IC_LOWER_IMAGE_LIMIT_PER_TAG}, {IC_UPPER_IMAGE_LIMIT}].')

    check(len(set([img['id'] for img in images])) == len(images), 'Duplicate image ids exist.')

    for image in tqdm(images, 'Checking "images..."'):
        image_check(image, len(images))


def categories_check(categories: List, data_type: str):
    upper_limit = IC_MAX_CATEGORIES if data_type == AnnotationKind.MULTICLASS_CLASSIFICATION else OD_MAX_CATEGORIES
    lower_limit = IC_MIN_CATEGORIES if data_type == AnnotationKind.MULTICLASS_CLASSIFICATION else OD_MIN_CATEGORIES
    check(lower_limit <= len(categories) <= upper_limit, f'Number of categories must be in [{lower_limit}, {upper_limit}], for {data_type}')
    check(len(set([category['id'] for category in categories])) == len(categories), 'Duplicate category ids exist.')

    if len(set([category['name'] for category in categories])) != len(categories):
        logging.warning('Duplicate category name exists in "categories". It might harm your model performance.')

    for category in tqdm(categories, 'Checking "categories..."'):
        category_check(category, len(categories))


def annotations_check(annotations: List, data_type: str, max_img_id: int, max_category_id: int):
    check(len(set([ann['id'] for ann in annotations])) == len(annotations), 'Duplicate annotation ids exist.')

    img_lower_limit = OD_LOWER_IMAGE_LIMIT_PER_TAG if data_type == AnnotationKind.OBJECT_DETECTION else IC_LOWER_IMAGE_LIMIT_PER_TAG

    category_stats = {}
    for annotation in tqdm(annotations, 'Checking "annotations"...'):
        annotation_check(annotation, data_type, len(annotations), max_img_id, max_category_id)
        ann_cate_id = annotation['category_id']
        category_stats[ann_cate_id] = category_stats.get(ann_cate_id, 0) + 1

    print(f'category stats {category_stats}.')
    for cat_id, stat in category_stats.items():
        check(stat >= img_lower_limit, f'Each category must have >= {img_lower_limit} images present, only {stat} images found for category {cat_id}.')


def check_coco_annotation_file(coco_dict: dict, data_type: str):
    fields_present_and_has_value_check(coco_dict, None, 'images', 'annotations', 'categories')
    images_check(coco_dict['images'], data_type)
    categories_check(coco_dict['categories'], data_type)
    annotations_check(coco_dict['annotations'], data_type, len(coco_dict['images']), len(coco_dict['categories']))


def parse_args():
    parser = argparse.ArgumentParser('Check if coco annotation file is well prepared.')
    parser.add_argument('--coco_json', '-c', type=pathlib.Path, help='Single coco json file to check.', required=True)
    parser.add_argument('--data_type', '-t', help='Type of data.', type=AnnotationKind, choices=list(AnnotationKind), required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    coco_dict = json.loads(args.coco_json.read_text(encoding='utf-8'))
    data_type = args.data_type
    check_coco_annotation_file(coco_dict, data_type)
    print(f'Annotation file {args.coco_json} looks good as a {data_type} dataset! Note that image file accessibility and image size is beyond this check.')


if __name__ == '__main__':
    main()
