import unittest

from environ_composition import EnvConfig


class TestEnvConfig(unittest.TestCase):

    def test_env_config_simple_vars(self):
        env_vars = {"VAR1": "value1", "VAR2": "value2"}
        config = EnvConfig(env_vars)
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2, "value2")

    def test_env_config_nested_vars(self):
        env_vars = {
            "VAR1": "value1",
            "VAR2": {
                "NESTED_VAR1": "nested_value1",
                "NESTED_VAR2": "nested_value2"
            },
        }
        config = EnvConfig(env_vars)
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2.nested_var1, "nested_value1")
        self.assertEqual(config.var2.nested_var2, "nested_value2")


if __name__ == '__main__':
    unittest.main()
