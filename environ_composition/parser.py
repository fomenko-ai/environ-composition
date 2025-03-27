import ast
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

    @staticmethod
    def _get_literal_value(value: str) -> Any:
        try:
            value = ast.literal_eval(value)
        except Exception as e:
            pass
        finally:
            return value

    @staticmethod
    def _validate_type(annotations, key, value):
        if key in annotations and not isinstance(value, annotations.get(key)):
            raise TypeError(
                f"Value type of key '{key}' does not match "
                "variable annotation."
            )

    def update_config(
        self,
        template: Any,
        env_config: EnvConfig,
        use_literal_eval: bool,
        use_type_validation: bool
    ) -> Any:
        annotations = template.__class__.__annotations__

        attrs_dict = {
            key: getattr(template, key) for key in dir(template)
            if not key.startswith('_')
        }

        attrs_dict.update(
            {
                key: t_value for key, t_value in template.__dict__.items()
                if not key.startswith('_')
            }
        )

        for key, t_value in attrs_dict.items():
            if hasattr(env_config, key):
                e_value = getattr(env_config, key)

                if not hasattr(e_value, '__dict__') and use_literal_eval:
                    e_value = self._get_literal_value(e_value)

                if not (
                    hasattr(t_value, '__dict__')
                    or hasattr(e_value, '__dict__')
                ):
                    if use_literal_eval and use_type_validation:
                        self._validate_type(annotations, key, e_value)
                    setattr(template, key, e_value)
                elif (
                    hasattr(t_value, '__dict__')
                    and hasattr(e_value, '__dict__')
                ):
                    self.update_config(
                        t_value,
                        e_value,
                        use_literal_eval,
                        use_type_validation
                    )
                else:
                    raise TypeError(
                        f"Value type of key '{key}' does not match "
                        "environmental variables."
                    )
        return template

    def parse(
        self,
        template=None,
        use_environ: bool = True,
        use_literal_eval: bool = True,
        use_type_validation: bool = True
    ) -> Union[EnvConfig, Any]:
        """
        :param template: Instance of config class for using as
        template (default=None)
        :param use_environ: Use environment variables for parsing
        (default=True)
        :param use_literal_eval: Use 'ast.literal_eval' function
        for value parsing (default=True)
        :param use_type_validation: Use type validation based on
        variable annotations (default=True). Validation works only
        if use_literal_eval=True.
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
            return self.update_config(
                template,
                env_config,
                use_literal_eval,
                use_type_validation
            )
        else:
            raise TypeError(
                f"Template {template} doesn't have '__dict__' method"
            )
