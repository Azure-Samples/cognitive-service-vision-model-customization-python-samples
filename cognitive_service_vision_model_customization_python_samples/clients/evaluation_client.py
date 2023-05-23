import logging
import time

from .client import Client
from ..models import EvaluationResponse, Evaluation, EvaluationStatus

logger = logging.getLogger(__name__)


class EvaluationClient(Client):
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str) -> None:
        super().__init__(resource_type, resource_name, multi_service_endpoint, resource_key)
        self._endpoint_format_str = self._endpoint + '/models/{0}/evaluations/{1}'

    def evaluate(self, evaluation: Evaluation) -> EvaluationResponse:
        json_response = self.request_put(f'/models/{evaluation.model_name}/evaluations/{evaluation.name}', json=evaluation.params)
        return EvaluationResponse.from_response(json_response)

    def query_run(self, name, model_name) -> EvaluationResponse:
        json_response = self.request_get(f'/models/{model_name}/evaluations/{name}')
        return EvaluationResponse.from_response(json_response)

    def wait_for_completion(self, name: str, model_name: str, check_wait_in_secs: int = 60) -> EvaluationResponse:
        start_time = time.time()
        total_elapsed = 0
        while True:
            eval_run = self.query_run(name, model_name)
            status = eval_run.status
            if status in [EvaluationStatus.FAILED, EvaluationStatus.SUCCEEDED]:
                break
            time.sleep(check_wait_in_secs)
            total_elapsed = time.time() - start_time
            logging.info(f'Training {name} for {total_elapsed} seconds. Status {status}.')

        logger.info(f'Training finished with state {eval_run.status}.')

        if eval_run.status == EvaluationStatus.FAILED:
            logger.warning(f'Evaluation failed: {eval_run.error}.')
        else:
            logger.info(f'Wall-clock time {total_elapsed / 60} minutes.')
            logger.info(f'Model performance: {eval_run.model_performance}')

        return eval_run
