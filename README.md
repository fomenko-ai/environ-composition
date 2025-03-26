# environ composition

The library for parsing environ configuration and creating nested configuration classes through composition.

* `EnvConfigParser` is designed to parse environment variables and a `.env` file to create a structured configuration.
* `EnvConfig` takes the parsed environment variables (a dictionary) and creates an object with attributes matching the keys.

### Import

```python 
from environ_composition import EnvConfigParser
```

### Usage

```python 
config = EnvConfigParser(dotenv_path='path_to/.env', separator='__').parse()
```

In `EnvConfigParser` each environment variable name goes into a lowercase attribute of `EnvConfig` instance. 

Adding some separator (i.e. double underscores "__") to the variable name adds a level of nesting to the config.

```
VAR1=value1
VAR2__NESTED_VAR1=nested_value1
```

```python 
config.var1 = "value1" 
config.var2.nested_var1 = "nested_value1"
```

When specifying a template, the parser updates the values in the template.

Without a template, the parser returns the config in `EnvConfig` instance.

```python 
class NestedTemplate:
    def __init__(self):
        self.nested_var1 = None

class Template:
    def __init__(self):
        self.var1 = None
        self.var2 = NestedTemplate()

template = Template()

parser = EnvConfigParser('path_to/.env')

config = parser.parse(template)
```

The structure and nesting levels of the template must match the names in the environment variable.

Mismatched names of attributes and private attributes in the template are not updated.