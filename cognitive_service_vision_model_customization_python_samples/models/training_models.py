import enum
from typing import Optional

from .common import Error
from .evaluation_models import EvaluationParameters


class ModelKind(enum.Enum):
    GENERIC_IC = 'Generic-Classifier'
    GENERIC_OD = 'Generic-Detector'
    PRODUCT_RECOGNIZER = 'Product-Recognizer'


class ModelStatus(enum.Enum):
    NOT_STARTED = 'notStarted'
    TRAINING = 'training'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELLING = 'cancelling'
    CANCELLED = 'cancelled'


class TrainingParameters:
    def __init__(self, training_dataset_name: str, time_budget_in_hours: int, model_kind: ModelKind) -> None:
        model_kind = ModelKind(model_kind) if isinstance(model_kind, str) else model_kind
        assert training_dataset_name
        assert time_budget_in_hours > 0

        self.training_dataset_name = training_dataset_name
        self.time_budget_in_hours = time_budget_in_hours
        self.model_kind = model_kind

    @property
    def params(self) -> dict:
        return {
            'TrainingDatasetName': self.training_dataset_name,
            'TimeBudgetInHours': self.time_budget_in_hours,
            'ModelKind': self.model_kind.value
        }

    def __str__(self):
        return f'TrainingParameters(dataset={self.training_dataset_name}, budget={self.time_budget_in_hours}, model_kind={self.model_kind})'


class Model:
    def __init__(self, name: str, trainingParams: TrainingParameters, evaluationParams: Optional[EvaluationParameters] = None) -> None:
        assert name
        self.name = name
        self.training_params = trainingParams
        self.evaluation_params = evaluationParams

    @property
    def params(self) -> dict:
        params = {'TrainingParameters': self.training_params.params}
        if self.evaluation_params:
            params['EvaluationParameters'] = self.evaluation_params.params
        return params

    def __str__(self):
        return f'Model(name={self.name}, training_params={self.training_params}, evaluation_params={self.evaluation_params})'


class ModelResponse(Model):
    def __init__(self, name: str, trainingParams: TrainingParameters, training_cost_in_minutes: int, status: ModelStatus, model_performance: dict, created_date_time: str, updated_date_time: str,
                 error: Error, evaluationParams: Optional[EvaluationParameters] = None) -> None:
        super().__init__(name, trainingParams, evaluationParams)
        self.training_cost_in_minutes = training_cost_in_minutes
        self.status = status
        self.model_performance = model_performance
        self.created_date_time = created_date_time
        self.updated_date_time = updated_date_time
        self.error = error

    def __str__(self):
        return f'Model(name={self.name}, training_params={self.training_params}, evaluation_params={self.evaluation_params}, ' \
               f'status={self.status}, training_cost_in_minutes={self.training_cost_in_minutes}, model_performance={self.model_performance}, error={self.error})'

    @staticmethod
    def from_response(json):
        train_params_dict = json['trainingParameters']
        training_params = TrainingParameters(train_params_dict['trainingDatasetName'], train_params_dict['timeBudgetInHours'], train_params_dict['modelKind'])
        eval_params = json.get('evaluationParameters')
        eval_params = EvaluationParameters(eval_params['testDatasetName']) if eval_params else None
        model_response = ModelResponse(
            json['name'],
            training_params,
            json.get('trainingCostInMinutes'),
            ModelStatus(json['status']),
            json.get('modelPerformance'),
            json['createdDateTime'],
            json['updatedDateTime'],
            Error.from_response(json.get('error')),
            eval_params
        )

        return model_response
