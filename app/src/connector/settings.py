import json

from .storages import FileStorage

SettingsType = dict[str, str]


class Settings:
    _settings_file = 'persist/settings.json'

    def __init__(self):
        self.storage = FileStorage()

    def get_settings(self) -> SettingsType:
        try:
            settings_raw = self.storage.read(self._settings_file)
        except FileNotFoundError:
            settings = {}
            self.save_settings(settings)
        else:
            settings = json.loads(settings_raw)
        return settings

    def save_settings(self, settings: SettingsType) -> None:
        self.storage.save(self._settings_file, json.dumps(settings))

    def get_topics(self) -> list[str]:
        settings = self.get_settings()
        return list(settings.values())

    def add_topic(self, name: str, topic: str) -> tuple[str, str]:
        name, topic = self._validate_value(name), self._validate_value(topic)

        settings = self.get_settings()
        settings[name] = topic
        self.save_settings(settings)
        return name, topic

    def _validate_value(self, value: str) -> str:
        return value.lower()
