from abc import ABC, abstractmethod

from loguru import logger as logging


class Parser(ABC):
    def __init__(self, verbose=False, **kwargs):
        self._verbose = verbose

    @abstractmethod
    def parse(self, **kwargs):

        """parse method needs to be implemented by child class of Parser."""
        msg = (
            "parse method needs to be implemented by child class of Parser."
        )
        logging.error(msg)
        raise NotImplementedError(msg)
