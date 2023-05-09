from typing import List
from urllib.parse import urlparse


class PlanogramMatchingRequest:
    def __init__(self, detected_products: dict, planogram: dict) -> None:
        assert detected_products
        assert planogram

        self.detected_products = detected_products
        self.planogram = planogram


class PostionMatchingResult:
    def __init__(self, position_id: str, detected_object: dict) -> None:
        assert position_id
        assert detected_object

        self.position_id = position_id
        self.detected_object = detected_object

    @staticmethod
    def from_response(json):
        return PostionMatchingResult(
            json['positionId'],
            json.get('detectedObject'))


class PlanogramMatchingResponse:
    def __init__(self, matching_result: List[PostionMatchingResult]) -> None:
        assert matching_result

        self.matching_result = matching_result

    @staticmethod
    def from_response(json):
        return PlanogramMatchingResponse(
            [PostionMatchingResult.from_response(item) for item in json['MatchingResultPerPosition']])
