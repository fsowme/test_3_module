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
    def __init__(self, path):
        self.path = path

    def save(self, name, data):
        with open(self._full_path(name), 'w') as f:
            f.write(data)

    def read(self, name):
        with open(self._full_path(name), 'r') as f:
            return f.read()

    def _full_path(self, name):
        return os.path.join(self.path, name)
