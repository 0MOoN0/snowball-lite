from abc import ABC, abstractmethod


class DataBoxDataAdapter(ABC):

    def get_core(self):
        pass

    @abstractmethod
    def get_rt(self, code):
        pass
