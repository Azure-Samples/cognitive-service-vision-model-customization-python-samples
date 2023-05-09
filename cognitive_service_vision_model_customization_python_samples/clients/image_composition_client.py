import logging

from cognitive_service_vision_model_customization_python_samples.clients import Client
from ..models import ImageStitchingRequest, ImageRectificationRequest

logger = logging.getLogger(__name__)


class ImageCompositionClient(Client):
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str) -> None:
        super().__init__(resource_type, resource_name, multi_service_endpoint, resource_key)

    def stitch_images(self, request: ImageStitchingRequest) -> bytes:
        json_response = self.request_post('/imagecomposition:stitch', data=request.to_json(), content_type='application/json')
        return json_response.content
    
    def rectify_image(self, request: ImageRectificationRequest) -> bytes:
        json_response = self.request_post('/imagecomposition:rectify', data=request.to_json(), content_type='application/json')
        return json_response.content