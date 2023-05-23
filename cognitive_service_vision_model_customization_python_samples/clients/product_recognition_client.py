import logging
import time

from .client import Client
from ..models import ProductRecognition, ProductRecognitionResponse, ProductRecognitionStatus

logger = logging.getLogger(__name__)


class ProductRecognitionClient(Client):
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str) -> None:
        super().__init__(resource_type, resource_name, multi_service_endpoint, resource_key)

    def create_run(self, run: ProductRecognition, img: bytes, content_type='image/jpeg') -> ProductRecognitionResponse:
        json_response = self.request_put(f'/productrecognition/{run.model_name}/runs/{run.name}', data=img, content_type=content_type)
        return ProductRecognitionResponse.from_response(json_response)

    def query_run(self, name, model_name) -> ProductRecognitionResponse:
        json_response = self.request_get(f'/productrecognition/{model_name}/runs/{name}')
        return ProductRecognitionResponse.from_response(json_response)

    def delete_run(self, name, model_name) -> None:
        self.request_delete(f'/productrecognition/{model_name}/runs/{name}')

    def wait_for_completion(self, name: str, model_name: str, check_wait_in_secs: int = 2) -> ProductRecognitionResponse:
        start_time = time.time()
        total_elapsed = 0
        while True:
            run = self.query_run(name, model_name)
            status = run.status
            if status in [ProductRecognitionStatus.FAILED, ProductRecognitionStatus.SUCCEEDED]:
                break
            time.sleep(check_wait_in_secs)
            total_elapsed = time.time() - start_time
            logging.info(f'Product recognition running {name} for {total_elapsed} seconds. Status {status}.')

        logger.info(f'Product recognition finished with state {run.status}.')

        if run.status == ProductRecognitionStatus.FAILED:
            logger.warning(f'Product recognition failed: {run.error}.')
        else:
            logger.info(f'Wall-clock time {total_elapsed / 60} minutes.')
            logger.info(f'Product recognition result: {run.result}')

        return run
