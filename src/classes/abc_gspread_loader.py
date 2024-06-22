from abc import ABC, abstractmethod

from gspread import Client


class ABCGspreadLoader(ABC):

    @abstractmethod
    def __init__(self, gclient: Client):
        pass

    @abstractmethod
    def reload(self):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def find(self, key, value):
        pass







