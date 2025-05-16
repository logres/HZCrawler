import json
import os

class Settings:
    REQUIRED_FIELDS = ["base_url", "x_access_token"]

    def __init__(self, config_path="config.json"):
        self.config = {}
        self.load_config(config_path)

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file '{config_path}' not found.")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse '{config_path}': {e}")

        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in self.config]
        if missing_fields:
            raise ValueError(f"Config file '{config_path}' missing required fields: {', '.join(missing_fields)}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    @property
    def base_url(self):
        return self.config.get("base_url")

    @property
    def x_access_token(self):
        return self.config.get("x_access_token")

settings = Settings()
