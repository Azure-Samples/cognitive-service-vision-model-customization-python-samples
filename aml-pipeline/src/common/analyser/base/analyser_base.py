from abc import ABC, abstractmethod

from loguru import logger as logging


class Analyser(ABC):
    def __init__(self, verbose=False, **kwargs):
        self._verbose = verbose

    @abstractmethod
    def validate_input(self, **kwargs):

        """validate_input method needs to be implemented by child class of Analyser."""
        msg = (
            "validate_input method needs to be implemented by child class of Analyser."
        )
        logging.error(msg)
        raise NotImplementedError(msg)

    @abstractmethod
    def parse_input(self, **kwargs):

        """parse_input method needs to be implemented by child class of Analyser."""
        msg = "parse_input method needs to be implemented by child class of Analyser."
        logging.error(msg)
        raise NotImplementedError(msg)
