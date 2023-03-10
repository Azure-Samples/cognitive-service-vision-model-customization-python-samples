import unittest
from cognitive_service_vision_model_customization_python_samples import TrainingClient, ResourceType


class TestClients(unittest.TestCase):
    def test_create_multi_service_client_fails_when_endpoint_missing(self):
        with self.assertRaises(AssertionError):
            TrainingClient(ResourceType.MULTI_SERVICE_RESOURCE, None, None, 'test_key')

    def test_create_multi_service_client_works(self):
        TrainingClient(ResourceType.MULTI_SERVICE_RESOURCE, None, 'https://example.com', 'test_key')

    def test_create_single_service_client_fails_when_resource_name_missing(self):
        with self.assertRaises(AssertionError):
            TrainingClient(ResourceType.MULTI_SERVICE_RESOURCE, None, None, 'test_key')
