"""Run E2E tests.

Those tests require the following environment variables.
- CS_SERVICE_ENDPOINT
- CS_SERVICE_KEY
- IC_DATASET_URL
- OD_DATASET_URL
"""
import os
import unittest
import uuid
from cognitive_service_vision_model_customization_python_samples import TrainingClient, DatasetClient, Dataset, AnnotationKind, ResourceType, TrainingParameters, Model, ModelKind, Evaluation,\
    EvaluationClient, ModelStatus, EvaluationStatus


def is_configured():
    return os.getenv('CS_SERVICE_ENDPOINT') and os.getenv('CS_SERVICE_KEY') and os.getenv('IC_DATASET_URL') and os.getenv('OD_DATASET_URL')


class TestE2E(unittest.TestCase):
    def setUp(self):
        self.endpoint = os.getenv('CS_SERVICE_ENDPOINT')
        self.resource_key = os.getenv('CS_SERVICE_KEY')
        self.ic_dataset_url = os.getenv('IC_DATASET_URL')
        self.od_dataset_url = os.getenv('OD_DATASET_URL')

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_dataset_ic(self):
        dataset_name = str(uuid.uuid4())
        annotation_file_uris = [self.ic_dataset_url]
        dataset_client = DatasetClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        dataset = Dataset(name=dataset_name, annotation_kind=AnnotationKind.MULTICLASS_CLASSIFICATION, annotation_file_uris=annotation_file_uris)
        try:
            response = dataset_client.register_dataset(dataset)
            self.assertEqual(response.name, dataset_name)
            self.assertEqual(response.annotation_file_uris, annotation_file_uris)
            response = dataset_client.query_dataset(dataset_name)
            self.assertEqual(response.name, dataset_name)

            annotation_file_uris = [self.ic_dataset_url, self.ic_dataset_url]
            dataset.annotation_file_uris = annotation_file_uris
            response = dataset_client.update_dataset(dataset)
            self.assertEqual(response.annotation_file_uris, annotation_file_uris)
        finally:
            dataset_client.delete_dataset(dataset_name)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_dataset_od(self):
        dataset_name = str(uuid.uuid4())
        dataset_client = DatasetClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        dataset = Dataset(name=dataset_name, annotation_kind=AnnotationKind.OBJECT_DETECTION, annotation_file_uris=[self.od_dataset_url])
        try:
            response = dataset_client.register_dataset(dataset)
            self.assertEqual(response.name, dataset_name)
            response = dataset_client.query_dataset(dataset_name)
            self.assertEqual(response.name, dataset_name)
        finally:
            dataset_client.delete_dataset(dataset_name)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_dataset_custom_properties(self):
        dataset_name = str(uuid.uuid4())
        dataset_client = DatasetClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        dataset = Dataset(name=dataset_name, annotation_kind=AnnotationKind.OBJECT_DETECTION, annotation_file_uris=[self.od_dataset_url], custom_properties={'key': 'value'})
        try:
            response = dataset_client.register_dataset(dataset)
            self.assertEqual(response.custom_properties, {'key': 'value'})
            dataset.custom_properties['key2'] = 'value2'
            response = dataset_client.update_dataset(dataset)
            self.assertEqual(response.custom_properties, {'key': 'value', 'key2': 'value2'})
        finally:
            dataset_client.delete_dataset(dataset_name)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_training_ic(self):
        self.test_request_training_core(ModelKind.GENERIC_IC)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_training_od(self):
        self.test_request_training_core(ModelKind.GENERIC_OD)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_training_pr(self):
        self.test_request_training_core(ModelKind.PRODUCT_RECOGNITION)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_training_core(self, model_kind=ModelKind.GENERIC_IC):
        dataset_name = str(uuid.uuid4())
        dataset_client = DatasetClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        dataset = Dataset(name=dataset_name, annotation_kind=AnnotationKind.OBJECT_DETECTION, annotation_file_uris=[self.od_dataset_url], custom_properties={'key': 'value'})
        model_name = dataset_name + '_model'
        model = Model(model_name, TrainingParameters(training_dataset_name=dataset_name, time_budget_in_hours=1, model_kind=model_kind))
        training_client = TrainingClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        try:
            dataset_client.register_dataset(dataset)
            response = training_client.train_model(model)
            self.assertEqual(response.status, ModelStatus.NOT_STARTED)
            response = training_client.query_model(model_name)
            self.assertIn(response.status, [ModelStatus.NOT_STARTED, ModelStatus.TRAINING])
            training_client.cancel_model_training(model_name)
        finally:
            dataset_client.delete_dataset(dataset_name)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_evaluation_ic(self):
        self.test_request_evaluation_core(ModelKind.GENERIC_IC)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_evaluation_od(self):
        self.test_request_evaluation_core(ModelKind.GENERIC_OD)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_evaluation_pr(self):
        self.test_request_evaluation_core(ModelKind.PRODUCT_RECOGNITION)

    @unittest.skipUnless(is_configured(), "requires endpoint info")
    def test_request_evaluation_core(self, model_kind=ModelKind.GENERIC_IC):
        dataset_name = str(uuid.uuid4())
        dataset_client = DatasetClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        evaluation_client = EvaluationClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        dataset = Dataset(name=dataset_name, annotation_kind=AnnotationKind.OBJECT_DETECTION, annotation_file_uris=[self.od_dataset_url], custom_properties={'key': 'value'})
        model_name = dataset_name + '_model'
        model = Model(model_name, TrainingParameters(training_dataset_name=dataset_name, time_budget_in_hours=1, model_kind=model_kind))
        training_client = TrainingClient(ResourceType.MULTI_SERVICE_RESOURCE, None, self.endpoint, self.resource_key)
        evaluation = Evaluation('test_eval', model_name, dataset_name)
        try:
            dataset_client.register_dataset(dataset)
            training_client.train_model(model)
            response = training_client.wait_for_completion(model_name)
            self.assertEqual(response.status, ModelStatus.SUCCEEDED)
            response = evaluation_client.evaluate(evaluation)
            self.assertEqual(response.status, EvaluationStatus.NOT_STARTED)
            response = evaluation_client.wait_for_completion('test_eval', model_name)
            self.assertEqual(response.status, EvaluationStatus.SUCCEEDED)
        finally:
            dataset_client.delete_dataset(dataset_name)
            training_client.delete_model(model_name)
