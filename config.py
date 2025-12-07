import json

FILENAME = "config.json"

class Config:
    _config: dict = {}

    def __init__(self):
        self.load_config()

    def load_config(self):
        with open(FILENAME, "r") as file:
            self._config = json.load(file)
    
    def get(self, key: str):
        return self._config.get(key)
