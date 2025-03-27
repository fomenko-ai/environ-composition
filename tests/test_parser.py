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
        for key in [
            "VAR1", "VAR2", "VAR3", "VAR2__NESTED_VAR1", "VAR2__NESTED_VAR2",
            "VAR", "TEMPLATE_VAR", "TEMPLATE_VAR__NESTED_VAR", "TEMPLATE_VAR__NESTED_INIT_VAR",
            "INIT_VAR", "INIT_TEMPLATE_VAR__NESTED_VAR", "INIT_TEMPLATE_VAR__NESTED_INIT_VAR"
        ]:
            if key in os.environ:
                del os.environ[key]

    def test_environ(self):
        os.environ["VAR1"] = "value1"
        os.environ["VAR2__NESTED_VAR1"] = "nested_value1"
        parser = EnvConfigParser()
        config = parser.parse()
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2.nested_var1, "nested_value1")

    def test_dotenv(self):
        with open(self.dotenv_file, "w") as f:
            f.write("VAR1=value1\n")
            f.write("VAR2__NESTED_VAR1=nested_value1\n")
        parser = EnvConfigParser(dotenv_path=str(self.dotenv_file))
        config = parser.parse(use_environ=False)
        self.assertEqual(config.var1, "value1")
        self.assertEqual(config.var2.nested_var1, "nested_value1")

    def test_both(self):
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

    def test_dotenv_not_found(self):
        parser = EnvConfigParser(dotenv_path="non_existent_file.env")
        with self.assertRaises(FileNotFoundError):
            parser.parse(use_environ=False)

    def test_parsing_with_annotations(self):
        test_data = [
            (str, 'string', 'init_string', 'nested_string', 'nested_init_string'),
            (int, 1, 2, 3, 4),
            (float, 1.01, 1.02, 1.03, 1.04),
            (bool, True, False, True, False),
            (list, ['string', 1, 1.01, True], ['init_string', 2, 1.02, False], ['nested_string', 3, 1.03, True], ['nested_init_string', 4, 1.04, False]),
            (tuple, ('string', 1, 1.01, True), ('init_string', 2, 1.02, False), ('nested_string', 3, 1.03, True), ('nested_init_string', 4, 1.04, False)),
            (set, {'string', 1, 1.01, True}, {'init_string', 2, 1.02, False}, {'nested_string', 3, 1.03, True}, {'nested_init_string', 4, 1.04, False}),
            (dict, {'string': 1}, {'init_string': 2}, {'nested_string': 3}, {'nested_init_string': 4})
        ]

        parser = EnvConfigParser()

        for _type, var, init_var, nested_var, nested_init_var in test_data:
            os.environ["VAR"] = str(var)
            os.environ["TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            os.environ["INIT_VAR"] = str(init_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            class NestedTemplate:
                nested_var: _type = None

                def __init__(self):
                    self.nested_init_var: _type = None

            class Template:
                var: _type = None
                template_var: NestedTemplate = NestedTemplate()

                def __init__(self):
                    self.init_var: _type = None
                    self.init_template_var: NestedTemplate = NestedTemplate()

            template = Template()
            config = parser.parse(template)

            self.assertEqual(config.var, var)
            self.assertEqual(config.template_var.nested_var, nested_var)
            self.assertEqual(config.template_var.nested_init_var, nested_init_var)

            self.assertEqual(config.init_var, init_var)
            self.assertEqual(config.init_template_var.nested_var, nested_var)
            self.assertEqual(config.init_template_var.nested_init_var, nested_init_var)

    def test_parsing_with_type_error(self):
        test_data = [
            (dict, 'string', 'init_string', 'nested_string', 'nested_init_string'),
            (str, 1, 2, 3, 4),
            (int, 1.01, 1.02, 1.03, 1.04),
            (float, True, False, True, False),
            (bool, ['string', 1, 1.01, True], ['init_string', 2, 1.02, False], ['nested_string', 3, 1.03, True], ['nested_init_string', 4, 1.04, False]),
            (list, ('string', 1, 1.01, True), ('init_string', 2, 1.02, False), ('nested_string', 3, 1.03, True), ('nested_init_string', 4, 1.04, False)),
            (tuple, {'string', 1, 1.01, True}, {'init_string', 2, 1.02, False}, {'nested_string', 3, 1.03, True}, {'nested_init_string', 4, 1.04, False}),
            (set, {'string': 1}, {'init_string': 2}, {'nested_string': 3}, {'nested_init_string': 4})
        ]

        parser = EnvConfigParser()

        for _type, var, init_var, nested_var, nested_init_var in test_data:
            os.environ["VAR"] = str(var)
            os.environ["TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            os.environ["INIT_VAR"] = str(init_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            class NestedTemplate:
                nested_var: _type = None

                def __init__(self):
                    self.nested_init_var: _type = None

            class Template:
                var: _type = None
                template_var: NestedTemplate = NestedTemplate()

                def __init__(self):
                    self.init_var: _type = None
                    self.init_template_var: NestedTemplate = NestedTemplate()

            template = Template()

            with self.assertRaises(TypeError):
                parser.parse(template)

    def test_parsing_with_init_var_annotations(self):
        test_data = [
            (dict, 'string', 'init_string', 'nested_string', 'nested_init_string'),
            (str, 1, 2, 3, 4),
            (int, 1.01, 1.02, 1.03, 1.04),
            (float, True, False, True, False),
            (bool, ['string', 1, 1.01, True], ['init_string', 2, 1.02, False], ['nested_string', 3, 1.03, True], ['nested_init_string', 4, 1.04, False]),
            (list, ('string', 1, 1.01, True), ('init_string', 2, 1.02, False), ('nested_string', 3, 1.03, True), ('nested_init_string', 4, 1.04, False)),
            (tuple, {'string', 1, 1.01, True}, {'init_string', 2, 1.02, False}, {'nested_string', 3, 1.03, True}, {'nested_init_string', 4, 1.04, False}),
            (set, {'string': 1}, {'init_string': 2}, {'nested_string': 3}, {'nested_init_string': 4})
        ]

        parser = EnvConfigParser()

        for _type, var, init_var, nested_var, nested_init_var in test_data:
            os.environ["VAR"] = str(var)
            os.environ["TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            os.environ["INIT_VAR"] = str(init_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_VAR"] = str(nested_var)
            os.environ["INIT_TEMPLATE_VAR__NESTED_INIT_VAR"] = str(nested_init_var)

            class NestedTemplate:
                nested_var = None

                def __init__(self):
                    self.nested_init_var: _type = None

            class Template:
                var = None
                template_var = NestedTemplate()

                def __init__(self):
                    self.init_var: _type = None
                    self.init_template_var: NestedTemplate = NestedTemplate()

            template = Template()
            config = parser.parse(template)

            self.assertEqual(config.var, var)
            self.assertEqual(config.template_var.nested_var, nested_var)
            self.assertEqual(config.template_var.nested_init_var, nested_init_var)

            self.assertEqual(config.init_var, init_var)
            self.assertEqual(config.init_template_var.nested_var, nested_var)
            self.assertEqual(config.init_template_var.nested_init_var, nested_init_var)

    def test_incorrect_config(self):
        os.environ["VAR"] = "var"
        os.environ["TEMPLATE_VAR__NESTED_VAR"] = "nested_var"

        class Template:
            var = None
            template_var = None

        parser = EnvConfigParser()
        template = Template()

        with self.assertRaises(TypeError):
            parser.parse(template)

    def test_incorrect_template(self):
        os.environ["VAR"] = "var"
        os.environ["TEMPLATE_VAR"] = "nested_var"

        class NestedTemplate:
            nested_var = None

        class Template:
            var = None
            template_var = NestedTemplate()

        parser = EnvConfigParser()
        template = Template()

        with self.assertRaises(TypeError):
            parser.parse(template)

    def test_null_values(self):
        os.environ["VAR1"] = ''
        os.environ["VAR2"] = 'None'
        os.environ["VAR3"] = 'null'

        parser = EnvConfigParser()
        config = parser.parse()

        self.assertEqual(config.var1, None)
        self.assertEqual(config.var2, None)
        self.assertEqual(config.var3, None)


if __name__ == '__main__':
    unittest.main()
