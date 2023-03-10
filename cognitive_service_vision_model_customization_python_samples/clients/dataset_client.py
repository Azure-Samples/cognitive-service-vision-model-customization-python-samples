from .client import Client
from ..models import Dataset, DatasetResponse


class DatasetClient(Client):
    def register_dataset(self, dataset: Dataset) -> Dataset:
        response_json = self.request_put(f'datasets/{dataset.name}', json=dataset.params)
        return DatasetResponse.from_response(response_json)

    def query_dataset(self, dataset_name: str) -> Dataset:
        assert dataset_name and isinstance(dataset_name, str)
        response_json = self.request_get(f'datasets/{dataset_name}')
        return DatasetResponse.from_response(response_json)

    def update_dataset(self, dataset: Dataset) -> Dataset:
        response_json = self.request_patch(f'datasets/{dataset.name}', json=dataset.params)
        return DatasetResponse.from_response(response_json)

    def delete_dataset(self, dataset_name: str):
        self.request_delete(f'datasets/{dataset_name}')
