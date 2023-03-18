import argparse
import json
import logging
import pathlib

from cognitive_service_vision_model_customization_python_samples import AnnotationKind
from dataclasses import dataclass
from enum import Enum
from tqdm import tqdm
from typing import List


@dataclass
class QuotaLimit:
    min_image_cnt_per_tag: int
    max_image_cnt: int
    max_image_dim: int
    min_image_dim: int
    max_categories: int
    min_categories: int


class Purpose(Enum):
    TRAINING = 'training'
    EVALUATION = 'evaluation'

    def __str__(self) -> str:
        return self.value


def _get_quota_limit(annotation_kind: AnnotationKind, purpose: Purpose) -> QuotaLimit:
    if annotation_kind == AnnotationKind.MULTICLASS_CLASSIFICATION:
        if purpose == Purpose.TRAINING:
            return QuotaLimit(2, 1000000, 10240, 10, 2000, 2)
        else:
            return QuotaLimit(1, 100000, 16000, 50, 2000, 2)
    else:
        if purpose == Purpose.TRAINING:
            return QuotaLimit(1, 200000, 10240, 10, 2000, 1)
        else:
            return QuotaLimit(1, 100000, 16000, 50, 2000, 1)


def _check(condition, err_msg):
    if not condition:
        raise ValueError(err_msg)


def _field_present_and_has_value_check(coco_dict: dict, custom_message: str, field_name: str):
    _check(coco_dict.get(field_name) is not None, f'"{field_name}" field missing or None. {custom_message}.')


def _fields_present_and_has_value_check(coco_dict: dict, custom_message: str, *field_names):
    for name in field_names:
        _field_present_and_has_value_check(coco_dict, custom_message, name)


def _id_value_range_check(id: int, max_id: int, id_name: str, custom_message: str):
    _check(isinstance(id, int) and 0 < id <= max_id, f'{id_name} must be integer in [1, {max_id}], {id} found. {custom_message}.')


def bbox_check(bbox: List, custom_message):
    _check(len(bbox) == 4, f'bbox must be of 4 floats. {len(bbox)} found. {custom_message}')
    left, top, width, height = bbox
    _check(0 <= left < 1.0, f'left must be in [0, 1). {left} found. {custom_message}')
    _check(0 <= top < 1.0, f'top must be in [0, 1). {top} found. {custom_message}')
    _check(0.0 < width <= 1.0, f'width must be in (0, 1]. {width} found. {custom_message}')
    _check(0.0 < height <= 1.0, f'height must be in (0, 1]. {width} found. {custom_message}')
    _check(left + width <= 1.0, f'left + width must be in (0, 1]. {left + width} found. {custom_message}')
    _check(top + height <= 1.0, f'top + height must be in (0, 1]. {top + height} found. {custom_message}')


def image_check(image: dict, max_id: int, quota_limit: QuotaLimit):
    img_msg = f'image with id = {image.get("id")}'
    _fields_present_and_has_value_check(image, img_msg, 'id', 'width', 'height', 'file_name')
    _check(('coco_url' in image) or ('absolute_url' in image), f'Neither "coco_url" nor "absolute_url" present. {img_msg}.')
    for key in ['width', 'height']:
        dim = image[key]
        _check(dim >= quota_limit.min_image_dim and dim <= quota_limit.max_image_dim, f'width {dim} must be present and in [{quota_limit.min_image_dim}, {quota_limit.max_image_dim}]. {img_msg}.')
    _id_value_range_check(image['id'], max_id, 'id', img_msg)


def category_check(catetory: dict, max_id: int):
    category_msg = f'image with id = {catetory.get("id")}'
    _fields_present_and_has_value_check(catetory, category_check, 'id', 'name')
    _id_value_range_check(catetory['id'], max_id, 'id', category_msg)


def annotation_check(annotation: dict, data_type: str, max_id: int, max_img_id: int, max_category_id: int):
    ann_msg = f'annotation with id = {annotation.get("id")}'
    _fields_present_and_has_value_check(annotation, ann_msg, 'id', 'image_id', 'category_id')
    if data_type == AnnotationKind.OBJECT_DETECTION:
        _fields_present_and_has_value_check(annotation, ann_msg, 'bbox')
        bbox_check(annotation['bbox'], ann_msg)

    _id_value_range_check(annotation['image_id'], max_img_id, 'image_id', ann_msg)
    _id_value_range_check(annotation['category_id'], max_category_id, 'category_id', ann_msg)
    _id_value_range_check(annotation['id'], max_id, 'id', ann_msg)


def images_check(images: List, quota_limit: QuotaLimit):
    _check(len(images) >= quota_limit.min_image_cnt_per_tag and len(images) <= quota_limit.max_image_cnt,
           f'Number of images must be in [{quota_limit.min_image_cnt_per_tag}, {quota_limit.max_image_cnt}].')

    _check(len(set([img['id'] for img in images])) == len(images), 'Duplicate image ids exist.')

    for image in tqdm(images, 'Checking "images..."'):
        image_check(image, len(images), quota_limit)


def categories_check(categories: List, quota_limit: QuotaLimit):
    _check(quota_limit.min_categories <= len(categories) <= quota_limit.max_categories, f'Number of categories must be in [{quota_limit.min_categories}, {quota_limit.max_categories}]')
    _check(len(set([category['id'] for category in categories])) == len(categories), 'Duplicate category ids exist.')

    if len(set([category['name'] for category in categories])) != len(categories):
        logging.warning('Duplicate category name exists in "categories". It might harm your model performance.')

    for category in tqdm(categories, 'Checking "categories..."'):
        category_check(category, len(categories))


def annotations_check(annotations: List, data_type: str, max_img_id: int, max_category_id: int, quota_limit: QuotaLimit):
    _check(len(set([ann['id'] for ann in annotations])) == len(annotations), 'Duplicate annotation ids exist.')

    category_stats = {}
    for annotation in tqdm(annotations, 'Checking "annotations"...'):
        annotation_check(annotation, data_type, len(annotations), max_img_id, max_category_id)
        ann_cate_id = annotation['category_id']
        category_stats[ann_cate_id] = category_stats.get(ann_cate_id, 0) + 1

    print(f'category stats {category_stats}.')
    for cat_id, stat in category_stats.items():
        _check(stat >= quota_limit.min_image_cnt_per_tag, f'Each category must have >= {quota_limit.min_image_cnt_per_tag} images present, only {stat} images found for category {cat_id}.')


def check_coco_annotation_file(coco_dict: dict, data_type: str, purpose: Purpose):
    quota_limit = _get_quota_limit(data_type, purpose)
    _fields_present_and_has_value_check(coco_dict, None, 'images', 'annotations', 'categories')
    images_check(coco_dict['images'], quota_limit)
    categories_check(coco_dict['categories'], quota_limit)
    annotations_check(coco_dict['annotations'], data_type, len(coco_dict['images']), len(coco_dict['categories']), quota_limit)


def _parse_args():
    parser = argparse.ArgumentParser('Check if coco annotation file is well prepared.')
    parser.add_argument('--coco_json', '-c', type=pathlib.Path, help='Single coco json file to check.', required=True)
    parser.add_argument('--data_type', '-t', help='Type of data.', type=AnnotationKind, choices=list(AnnotationKind), required=True)
    parser.add_argument('--purpose', '-t', help='Purpose for the data..', type=Purpose, choices=list(Purpose), required=True)
    return parser.parse_args()


def main():
    args = _parse_args()
    coco_dict = json.loads(args.coco_json.read_text(encoding='utf-8'))
    data_type = args.data_type
    purpose = args.purpose
    check_coco_annotation_file(coco_dict, data_type, purpose)
    print(f'Annotation file {args.coco_json} looks good as a {data_type} dataset for {args.purpose}! Note that image file accessibility and image size is beyond this check.')


if __name__ == '__main__':
    main()
