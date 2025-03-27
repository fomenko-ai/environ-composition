__all__ = ['EnvConfig']


class EnvConfig:
    """
    The EnvConfig class is used to create config object with attributes
    based on the key-value pairs provided in the environment variables
    dictionary when initialized.

    Parameters:
    - env_vars (dict): A dictionary containing the environment variable
    key-value pairs.
    """
    def __init__(self, env_vars: dict):
        self.env_vars = env_vars

        self._create_attrs()

    def _create_attrs(self):
        for key, value in self.env_vars.items():
            key = key.lower()
            value = value if value not in ['', 'None', 'null'] else None
            if isinstance(value, dict):
                setattr(self, key, EnvConfig(value))
            else:
                setattr(self, key, value)
