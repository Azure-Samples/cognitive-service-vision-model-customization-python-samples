import time
import logging
from typing import Tuple, Any

from .client import Client
from ..models import Model, ModelResponse, ModelStatus, Evaluation, EvaluationStatus, EvaluationResponse

logger = logging.getLogger(__name__)


class TrainingClient(Client):
    def train_model(self, model: Model) -> ModelResponse:
        json_response = self.request_put(f'models/{model.name}', json=model.params)
        return ModelResponse.from_response(json_response)

    def query_model(self, name: str) -> ModelResponse:
        json_response = self.request_get(f'models/{name}')
        return ModelResponse.from_response(json_response)

    def cancel_model_training(self, name: str):
        self.request_post(f'models/{name}:cancel')

    def delete_model(self, name: str):
        self.request_delete(f'models/{name}')

    def evaluate_model(self, evaluation: Evaluation):
        self.request_put(f'models/{evaluation.model_name}/evaluations/{evaluation.name}', json=evaluation.params)

    def query_model_evaluation(self, model_name: str, evaluation_name: str) -> EvaluationResponse:
        json_response = self.request_get(f'models/{model_name}/evaluations/{evaluation_name}')
        return EvaluationResponse.from_response(json_response)

    def delete_model_evaluation(self, model_name: str, evaluation_name: str):
        self.request_delete(f'models/{model_name}/evaluations/{evaluation_name}')

    def wait_for_training_completion(self, model_name, check_wait_in_secs: int = 60) -> ModelResponse:
        def query():
            evaluation = self.query_model(model_name)
            return evaluation, evaluation.status

        model, total_elapsed = self._wait_for_completion(query, [ModelStatus.FAILED, ModelStatus.SUCCEEDED, ModelStatus.CANCELLED], check_wait_in_secs)

        logger.info(f'Training finished with status {model.status}.')

        if model.status == ModelStatus.FAILED:
            logger.warning(f'Training failed: {model.error}')
        else:
            logger.info(f'Wall-clock time {total_elapsed / 60} minutes, actual training compute time billed {model.training_cost_in_minutes} minutes.')
            logger.info(f'Model performance: {model.model_performance}')

        return model

    def wait_for_evaluation_completion(self, model_name, evaluation_name, check_wait_in_secs: int = 60) -> ModelResponse:
        def query():
            evaluation = self.query_model_evaluation(model_name, evaluation_name)
            return evaluation, evaluation.status

        evaluation, total_elapsed = self._wait_for_completion(query, [EvaluationStatus.FAILED, EvaluationStatus.SUCCEEDED], check_wait_in_secs)

        logger.info(f'Evalaution finished with status {evaluation.status}.')

        if evaluation.status == ModelStatus.FAILED:
            logger.warning(f'Evaluation failed: {evaluation.error.code}, {evaluation.error.message}')
        else:
            logger.info(f'Wall-clock time {total_elapsed} seconds.')
            logger.info(f'Model performance: {evaluation.model_performance}')

        return evaluation

    def _wait_for_completion(self, query, ending_states, check_wait_in_secs: int = 60) -> Tuple[Any, float]:
        start_time = time.time()
        total_elapsed = 0
        while True:
            entity, status = query()
            if status in ending_states:
                break
            time.sleep(check_wait_in_secs)
            total_elapsed = time.time() - start_time
            logger.info(f'waiting for {total_elapsed} seconds. Status {status}.')

        return entity, total_elapsed
