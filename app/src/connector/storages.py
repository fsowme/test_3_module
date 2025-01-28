import os
from abc import ABCMeta, abstractmethod


class BaseStorage(metaclass=ABCMeta):
    @abstractmethod
    def save(self, name, data):
        pass

    @abstractmethod
    def read(self, name):
        pass


class FileStorage(BaseStorage):
    def save(self, name, data):
        with open(name, 'w') as f:
            f.write(data)

    def read(self, name):
        with open(name, 'r') as f:
            return f.read()
