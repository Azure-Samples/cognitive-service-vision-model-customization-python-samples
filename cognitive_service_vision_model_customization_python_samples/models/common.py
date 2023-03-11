import dataclasses
import typing


@dataclasses.dataclass
class Error:
    code: str = ''
    message: str = ''
    target: str = ''
    details: typing.List['Error'] = dataclasses.field(default_factory=list)

    @classmethod
    def from_response(cls, response):
        if not response:
            return None

        return cls(**response)
