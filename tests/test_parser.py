import os
import unittest
import tempfile

from environ_composition import EnvConfigParser


class TestEnvConfigParser(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dotenv_file = os.path.join(self.temp_dir.name, ".env")

    def tearDown(self):
        self.temp_dir.cleanup()
        for key in ["VAR1", "VAR2__NESTED_VAR1", "VAR2__NESTED_VAR2"]:
            if key in os.environ:
                del os.environ[key]

    def test_env_config_parser_environ(self):
        os.environ["VAR1"] = "value1"
        os.environ["VAR2__NESTED_VAR1"] = "nested_value1"
        parser = EnvConfigParser()
        config = parser.parse()
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2.nested_var1, "nested_value1")

    def test_env_config_parser_dotenv(self):
        with open(self.dotenv_file, "w") as f:
            f.write("VAR1=value1\n")
            f.write("VAR2__NESTED_VAR1=nested_value1\n")
        parser = EnvConfigParser(dotenv_path=str(self.dotenv_file))
        config = parser.parse(use_environ=False)
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2.nested_var1, "nested_value1")

    def test_env_config_parser_both(self):
        with open(self.dotenv_file, "w") as f:
            f.write("VAR1=value1_from_dotenv\n")
            f.write("VAR2__NESTED_VAR1=nested_value1_from_dotenv\n")
        os.environ["VAR1"] = "value1_from_environ"
        os.environ["VAR2__NESTED_VAR2"] = "nested_value2_from_environ"
        parser = EnvConfigParser(dotenv_path=str(self.dotenv_file))
        config = parser.parse()
        # .env file values should take precedence over environment variables
        self.assertEqual(config.var1, "value1_from_dotenv")
        self.assertEqual(config.var2.nested_var1, "nested_value1_from_dotenv")
        self.assertEqual(config.var2.nested_var2, "nested_value2_from_environ")

    def test_env_config_parser_dotenv_not_found(self):
        parser = EnvConfigParser(dotenv_path="non_existent_file.env")
        with self.assertRaises(FileNotFoundError):
            parser.parse(use_environ=False)


if __name__ == '__main__':
    unittest.main()
