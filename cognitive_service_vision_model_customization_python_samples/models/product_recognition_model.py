import enum

from .common import Error


class ProductRecognitionStatus(enum.Enum):
    NOT_STARTED = 'notStarted'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class ProductRecognition:
    def __init__(self, name: str, model_name: str) -> None:
        assert name
        assert model_name

        self.name = name
        self.model_name = model_name


class ProductRecognitionResponse(ProductRecognition):
    def __init__(self, name: str, model_name: str, status: ProductRecognitionStatus,
                 created_date_time: str, updated_date_time: str, result: dict, error: Error) -> None:
        super().__init__(name, model_name)
        self.status = status
        self.created_date_time = created_date_time
        self.updated_date_time = updated_date_time
        self.result = result
        self.error = error

    @staticmethod
    def from_response(json):
        return ProductRecognitionResponse(
            json['runName'],
            json['modelName'],
            ProductRecognitionStatus(json['status']),
            json['createdDateTime'],
            json['updatedDateTime'],
            json.get('result'),
            Error(json.get('error')))
