import os
from typing import Any, Union

from .config import EnvConfig


__all__ = ['EnvConfigParser']


class EnvConfigParser:
    """
    Parses environment variables and .env file, organizes keys with
    similar values into a dictionary and returns an `EnvConfig` object.

    Parameters:
    - dotenv_path (str, optional): Path to .env file (default=None).
    - separator (str, optional): Separator between variable level names
    (default='__')

    Methods:
    - parse(): Parses environment variables and the `.env` file (if specified)
    and returns an `EnvConfig` object.
    """

    def __init__(self, dotenv_path: str = None, separator: str = '__'):
        self.dotenv_path = dotenv_path
        self.separator = separator
        self._config = None

    def _check_config(self):
        if self._config is None:
            self._config = {}

    def _parse_env_vars(self):
        """
        Parses environment variables and populates the config dictionary.
        """
        self._check_config()
        for key, value in os.environ.items():
            self._add_to_config(self._config, key.split(self.separator), value)

    def _parse_dotenv(self):
        """
        Parses .env file and populates the config dictionary.
        """
        self._check_config()
        if os.path.exists(self.dotenv_path):
            with open(self.dotenv_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=")
                        key = key.strip()
                        value = value.strip()
                        self._add_to_config(
                            self._config,
                            key.split(self.separator),
                            value
                        )
        else:
            raise FileNotFoundError(f"File {self.dotenv_path} not found")

    def _add_to_config(self, config, key_parts, value):
        """
        Recursively adds key-value pair to the config dictionary.
        """
        if len(key_parts) == 1:
            config[key_parts[0]] = value
        else:
            if key_parts[0] not in config:
                config[key_parts[0]] = {}
            self._add_to_config(config[key_parts[0]], key_parts[1:], value)

    def update_config(self, template: Any, env_config: EnvConfig) -> Any:
        for key, t_value in template.__dict__.items():
            if key.startswith('_'):
                continue
            if hasattr(env_config, key):
                e_value = getattr(env_config, key)
                if not (
                    hasattr(t_value, '__dict__')
                    or hasattr(e_value, '__dict__')
                ):
                    setattr(template, key, e_value)
                elif (
                    hasattr(t_value, '__dict__')
                    and hasattr(e_value, '__dict__')
                ):
                    self.update_config(t_value, e_value)
                else:
                    raise TypeError(
                        f"Value type of key '{key}' does not match "
                        "environmental variables."
                    )

    def parse(self, template=None, use_environ=True) -> Union[EnvConfig, Any]:
        """
        :param template: Instance of config class for using as
        template (default=None)
        :param use_environ: Boolean flag to indicate whether to use
        environment variables for parsing (default=True)
        :return: An instance of EnvConfig or template
        """
        if use_environ:
            self._parse_env_vars()
        if self.dotenv_path:
            self._parse_dotenv()
        env_config = EnvConfig(self._config)
        if template is None:
            return env_config
        elif template and hasattr(template, '__dict__'):
            return self.update_config(template, env_config)
        else:
            raise TypeError(
                f"Template {template} doesn't have '__dict__' method"
            )
