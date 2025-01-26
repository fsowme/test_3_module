import abc
import json


class SerializerError(Exception):
    pass


class SerializationError(SerializerError):
    pass


class DeserializationError(SerializerError):
    pass


class BaseSerializer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def serialize(self, obj):
        pass

    @abc.abstractmethod
    def deserialize(self, data):
        pass


class JsonSerializer(BaseSerializer):
    def serialize(self, obj):
        try:
            return json.dumps(obj)
        except (TypeError, ValueError) as err:
            raise SerializationError() from err

    def deserialize(self, data):
        try:
            return json.loads(data)
        except json.JSONDecodeError as err:
            raise DeserializationError() from err
