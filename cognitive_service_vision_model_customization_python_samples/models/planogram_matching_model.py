from typing import List
from urllib.parse import urlparse


class PlanogramMatchingRequest:
    def __init__(self, detected_products: dict, planogram: dict) -> None:
        assert detected_products
        assert planogram

        self.detected_products = detected_products
        self.planogram = planogram

    def to_dict(self) -> dict:
        return {
            'detectedProducts': self.detected_products,
            'planogram': self.planogram
        }


class PlanogramMatchingResponse:
    def __init__(self, matching_result: dict) -> None:
        assert matching_result

        self.matching_result = matching_result

    @staticmethod
    def from_response(json):
        return PlanogramMatchingResponse(json['matchingResultPerPosition'])

    def to_dict(self) -> dict:
        return {
            'matchingResultPerPosition': self.matching_result
        }
