import yaml


class ConfigLoader:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    @property
    def allowed_channels(self):
        return self._config.get("allowed_channels", [])

    @property
    def system_prompt(self):
        return self._config.get("system_prompt", "")

    @property
    def error_message(self):
        return self._config.get("error_message", "エラーが発生しました。")

    @property
    def reaction_emoji(self):
        return self._config.get("reaction_emoji", "✅")

    @property
    def gemini_model(self):
        return self._config.get("gemini_model", "gemini-1.5-flash")

    @property
    def grok_model(self):
        return self._config.get("grok_model", "grok-3")
