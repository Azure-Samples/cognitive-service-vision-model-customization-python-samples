import json
import os
import pathlib
import pytest
from cognitive_service_vision_model_customization_python_samples import check_coco_annotation_file, AnnotationKind, Purpose


BASE_PATH = pathlib.Path(os.path.dirname(__file__)) / 'resources' / "sample_jsons"
ANNOTATION_KIND_MAPPING = {
    'ic': AnnotationKind.MULTICLASS_CLASSIFICATION,
    'od': AnnotationKind.OBJECT_DETECTION
}

PURPOSE_MAPPING = {
    'train': Purpose.TRAINING,
    'eval': Purpose.EVALUATION
}


@pytest.mark.parametrize("file_name, error_message", [
    ('ic_eval_image_size_too_small.json', "width 10 must be present and in [50, 16000]. image with id = 1."),
    ('ic_eval_valid.json', None),
    ('ic_train_too_few_images.json', "Each category must have >= 2 images present, only 1 images found for category 2."),
    ('ic_train_valid.json', None),
    ('od_eval_valid.json', None),
    ('od_train_invalid_bbox.json', "left + width must be in (0, 1]. 1.1 found. annotation with id = 1"),
    ('od_train_valid.json', None),
])
def test_ic_train_invalid(file_name: str, error_message: str):
    ann_kind, purpose = file_name.split('_')[:2]
    ann_kind = ANNOTATION_KIND_MAPPING[ann_kind]
    purpose = PURPOSE_MAPPING[purpose]
    file_name: pathlib.Path = BASE_PATH / file_name

    if error_message:
        with pytest.raises(ValueError) as exinfo:
            check_coco_annotation_file(json.loads(file_name.read_text()), ann_kind, purpose)
            assert exinfo.value.message == error_message
    else:
        check_coco_annotation_file(json.loads(file_name.read_text()), ann_kind, purpose)
