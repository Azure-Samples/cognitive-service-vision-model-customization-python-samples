import io
import json
import logging

from .client import Client
from ..models import ImageStitchingRequest, ImageRectificationRequest

logger = logging.getLogger(__name__)


class ImageCompositionClient(Client):
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str) -> None:
        super().__init__(resource_type, resource_name, multi_service_endpoint, resource_key)

    def stitch_images(self, request: ImageStitchingRequest) -> bytes:
        return self.request_post('/imagecomposition:stitch', data=json.dumps(request.to_dict()), content_type='application/json')

    def rectify_image(self, request: ImageRectificationRequest) -> bytes:
        return self.request_post('/imagecomposition:rectify', data=json.dumps(request.to_dict()), content_type='application/json')
