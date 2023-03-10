import time
import logging

from .client import Client
from ..models import Model, ModelResponse, ModelStatus

logger = logging.getLogger(__name__)


class TrainingClient(Client):
    def train_model(self, model: Model) -> ModelResponse:
        json_response = self.request_put(f'models/{model.name}', json=model.params)
        return ModelResponse.from_response(json_response)

    def query_model(self, name) -> ModelResponse:
        json_response = self.request_get(f'models/{name}')
        return ModelResponse.from_response(json_response)

    def cancel_model_training(self, name):
        self.request_post(f'models/{name}:cancel')

    def delete_model(self, name):
        self.request_delete(f'models/{name}')

    def wait_for_completion(self, model_name, check_wait_in_secs: int = 60) -> ModelResponse:
        start_time = time.time()
        while True:
            model = self.query_model(model_name)
            status = model.status
            if status in [ModelStatus.FAILED, ModelStatus.SUCCEEDED, ModelStatus.CANCELLED]:
                break
            time.sleep(check_wait_in_secs)
            total_elapsed = time.time() - start_time
            logger.info(f'Training {model_name} for {total_elapsed} seconds. Status {status}.')

        logger.info(f'Training finished with status {model.status}.')

        if model.status == ModelStatus.FAILED:
            logger.warning(f'Training failed: {model.error}')
        else:
            logger.info(f'Wall-clock time {total_elapsed / 60} minutes, actual training compute time billed {model.training_cost_in_minutes} minutes.')
            logger.info(f'Model performance: {model.model_performance}')

        return model
