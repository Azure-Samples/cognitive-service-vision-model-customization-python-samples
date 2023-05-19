import logging
import json

from .client import Client
from ..models import PlanogramMatchingRequest, PlanogramMatchingResponse

logger = logging.getLogger(__name__)


class PlanogramComplianceClient(Client):
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str) -> None:
        super().__init__(resource_type, resource_name, multi_service_endpoint, resource_key)

    def match_planogram(self, request: PlanogramMatchingRequest) -> PlanogramMatchingResponse:
        json_response = self.request_post('/planogramcompliance:match', data=json.dumps(request.to_dict()), content_type='application/json')
        return PlanogramMatchingResponse.from_response(json_response)
