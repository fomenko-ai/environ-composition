import unittest

from environ_composition import EnvConfig


class TestEnvConfig(unittest.TestCase):

    def test_simple_vars(self):
        env_vars = {"VAR1": "value1", "VAR2": "value2"}
        config = EnvConfig(env_vars)
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2, "value2")

    def test_nested_vars(self):
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

    def test_null_values(self):
        env_vars = {"VAR1": "", "VAR2": "None", "VAR3": "null"}
        config = EnvConfig(env_vars)
        self.assertEqual(config.var1, None)
        self.assertEqual(config.var2, None)
        self.assertEqual(config.var3, None)


if __name__ == '__main__':
    unittest.main()
