import enum
from .common import Error


class EvaluationStatus(enum.Enum):
    NOT_STARTED = 'notStarted'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class EvaluationParameters:
    def __init__(self, test_dataset_name: str) -> None:
        assert test_dataset_name

        self.test_dataset_name = test_dataset_name

    @property
    def params(self) -> dict:
        return {'TestDatasetName': self.test_dataset_name}


class Evaluation:
    def __init__(self, name, model_name, dataset_name) -> None:
        assert name
        assert model_name
        assert dataset_name

        self.name = name
        self.model_name = model_name
        self.eval_params = EvaluationParameters(dataset_name)

    @property
    def params(self) -> dict:
        return {'EvaluationParameters': self.eval_params.params}


class EvaluationResponse(Evaluation):
    def __init__(self, name: str, model_name: str, evaluationParams: EvaluationParameters, status: EvaluationStatus, created_date_time: str,
                 updated_date_time: str, model_performance: dict, error: Error) -> None:
        super().__init__(name, model_name, evaluationParams['testDatasetName'])
        self.status = status
        self.created_date_time = created_date_time
        self.updated_date_time = updated_date_time
        self.model_performance = model_performance
        self.error = error

    @staticmethod
    def from_response(json):
        return EvaluationResponse(
            json['name'],
            json['modelName'],
            json['evaluationParameters'],
            EvaluationStatus(json['status']),
            json['createdDateTime'],
            json['updatedDateTime'],
            json.get('modelPerformance'),
            Error(json.get('error')))
