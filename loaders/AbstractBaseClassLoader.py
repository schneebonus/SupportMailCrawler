from abc import ABC, abstractmethod

class AbstractBaseClassLoader(ABC):
    def __init__(self, value):
        super().__init__()

    @abstractmethod
    def init():
        pass

    @abstractmethod
    def load_and_soup(soup):
        pass

    @abstractmethod
    def cleanup():
        pass
