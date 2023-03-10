from enum import Enum
from typing import List, Union


class AnnotationKind(Enum):
    MULTICLASS_CLASSIFICATION = 'imageClassification'
    OBJECT_DETECTION = 'imageObjectDetection'

    def __str__(self) -> str:
        return self.value


class AuthenticationKind(Enum):
    MI = 'managedIdentity',
    SAS = 'sas'

    def __str__(self) -> str:
        return self.value


class Authentication:
    def __init__(self, kind: AuthenticationKind = AuthenticationKind.MI, sas_token=None):
        kind = AuthenticationKind(kind) if isinstance(kind, str) else kind
        self.kind = kind
        self.sas_token = sas_token

    @property
    def params(self):
        return {
            'kind': self.kind.value,
            'sasToken': self.sas_token
        }

    @staticmethod
    def from_response(json):
        if not json:
            return None

        return Authentication(json['kind'], json.get('sas'))


class Dataset:
    def __init__(self, name: str, annotation_kind: Union[AnnotationKind, str], annotation_file_uris: List[str], authentication: Authentication = None, custom_properties: dict = None) -> None:
        annotation_kind = AnnotationKind(annotation_kind) if isinstance(annotation_kind, str) else annotation_kind
        assert name
        assert annotation_file_uris

        self.name = name
        self.annotation_kind = annotation_kind
        self.annotation_file_uris = annotation_file_uris
        self.authentication = authentication
        self.custom_properties = custom_properties

    @property
    def params(self):
        params = {
            "AnnotationKind": self.annotation_kind.value,
            "AnnotationFileUris": self.annotation_file_uris,
        }

        if self.authentication:
            params["authentication"] = self.authentication.params

        if self.custom_properties:
            params["customProperties"] = self.custom_properties

        return params

    def __str__(self):
        return f'Dataset(name={self.name}, annotation_kind={self.annotation_kind}, annotation_file_uris={self.annotation_file_uris}, ' \
               f'authentication={self.authentication}, custom_properties={self.custom_properties})'


class DatasetResponse(Dataset):
    def __init__(self, name: str, annotation_kind: str, annotation_file_uris: List[str], created_date_time, updated_date_time, authentication: Authentication = None) -> None:
        super().__init__(name, annotation_kind, annotation_file_uris, authentication)
        self.created_date_time = created_date_time
        self.updated_date_time = updated_date_time

    @classmethod
    def from_response(cls, response):
        return cls(response['name'],
                   AnnotationKind(response['annotationKind']),
                   response['annotationFileUris'],
                   response['createdDateTime'],
                   response['updatedDateTime'],
                   Authentication.from_response(response.get('authentication')))
