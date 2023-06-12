import logging
import urllib.parse
import requests
from ..clients.common import ResourceType

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, resource_type, resource_name: str, multi_service_endpoint, resource_key: str, api_version: str='2023-04-01-preview') -> None:
        resource_type = ResourceType(resource_type) if isinstance(resource_type, str) else resource_type

        if resource_type == ResourceType.MULTI_SERVICE_RESOURCE:
            assert multi_service_endpoint
            self._endpoint = urllib.parse.urljoin(multi_service_endpoint, '/computervision')
        else:
            assert resource_name
            self._endpoint = f'https://{resource_name}.cognitiveservices.azure.com/computervision'

        self._headers = {'Ocp-Apim-Subscription-Key': resource_key}
        self._params = {'api-version': api_version}

    def _construct_url(self, path):
        return self._endpoint + '/' + path

    @staticmethod
    def _get_json_response(response):
        if not response.ok:
            logger.error(response.content)
        response.raise_for_status()

        json_response = response.json()
        logger.debug(f"Response: {json_response}")
        return json_response

    def request_get(self, path):
        r = requests.get(self._construct_url(path), params=self._params, headers=self._headers)
        return self._get_json_response(r)

    def request_put(self, path, json=None, data=None, content_type=None):
        headers = dict(self._headers, **{'Content-Type': content_type}) if content_type else self._headers

        r = requests.put(self._construct_url(path), json=json, params=self._params, data=data, headers=headers)
        return self._get_json_response(r)

    def request_post(self, path, params=None, data=None, content_type=None):
        assert data is None or content_type

        params = params or {}
        headers = dict(self._headers, **{'Content-Type': content_type}) if content_type else self._headers
        r = requests.post(self._construct_url(path), data=data, params=dict(self._params, **params), headers=headers)

        if r.headers.get('Content-Type', None) == 'image/jpeg':
            return r.content

        return self._get_json_response(r)

    def request_patch(self, path, json):
        r = requests.patch(self._construct_url(path), json=json, params=self._params, headers=self._headers)
        return self._get_json_response(r)

    def request_delete(self, path):
        r = requests.delete(self._construct_url(path), params=self._params, headers=self._headers)
        if not r.ok:
            logger.error(r.content)
        r.raise_for_status()
