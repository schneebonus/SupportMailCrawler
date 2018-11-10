from abc import ABC, abstractmethod

class AbstractBaseClassParser(ABC):
    def __init__(self, value):
        super().__init__()

    @abstractmethod
    def extract_mail_addresses(soup, VERBOSE):
        pass
