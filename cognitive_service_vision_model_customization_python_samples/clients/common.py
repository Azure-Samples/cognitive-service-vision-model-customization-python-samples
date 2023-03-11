import enum


class ResourceType(enum.Enum):
    """
    https://learn.microsoft.com/en-us/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Canomaly-detector%2Clanguage-service%2Ccomputer-vision%2Cwindows
    """

    MULTI_SERVICE_RESOURCE = "multi_service_account"
    SINGLE_SERVICE_RESOURCE = "single_service_account"
