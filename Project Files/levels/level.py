from abc import ABC, abstractmethod
from resources.dimension import Dimensions


class BaseLevel(ABC):

    def __init__(self, autoplay: bool, dimensions: Dimensions) -> None:
        self.auto_play = autoplay
        self.x_length = dimensions.horizontal
        self.y_length = dimensions.veritcal

    @abstractmethod
    def is_over(self):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError
