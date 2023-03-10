from .client import Client


class PredictionClient(Client):
    def predict(self, model_name: str, img: bytes, content_type='image/jpeg'):
        return self.request_post('imageanalysis:analyze', params={'model-name': model_name}, data=img, content_type=content_type)
