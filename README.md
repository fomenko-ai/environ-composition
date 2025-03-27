# environ composition

The library for parsing environ configuration and creating nested configuration classes through composition.

* `EnvConfigParser` is designed to parse environment variables and a `.env` file to create a structured configuration.
* `EnvConfig` takes the parsed environment variables (a dictionary) and creates an object with attributes matching the keys.

### Installation

```python 
pip install environ-composition
```

### Import

```python 
from environ_composition import EnvConfigParser
```

### Usage

```python 
config = EnvConfigParser(dotenv_path='path_to/.env', separator='__').parse()
```

In `EnvConfigParser` each environment variable name goes into a lowercase attribute of `EnvConfig` instance. 

Adding some separator (i.g. double underscores "__") to the variable name adds a level of nesting to the config.

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

### Parsing values

The `ast` library and the `literal_eval` function are used for parsing string values. 

Standard data types are available: str, int, float, bool, list, tuple, set, dict, etc.

```
VAR1=['string', 1, 1.01, True]
VAR2__NESTED_VAR1={"string": 1}
```

For variables with null string values ('', 'None', 'null'), `None` is assigned.

```
VAR1=
VAR2=None
VAR3=null
```

The `use_literal_eval` flag in the `parse` method determines to use or not parsing.

### Type validation

If there is a type annotation for __class__ attributes, the parser validates the assigned values.

If there is a type annotation for __instance__ attributes, the parser does not validate.

Validation is not applied to nested config instances.

```python 
class NestedTemplate:
    nested_var1: str = None

class Template:
    var1: str = None
    var2: int = None
    var3: NestedTemplate = NestedTemplate() # it will not be validated

    def __init__(self):
        self.var4: int = None  # it will not be validated
        self.var5: NestedTemplate = NestedTemplate() # it will not be validated
```

The `use_type_validation` flag in the `parse` method determines to use or not type validation. Validation only works if `use_literal_eval = True`.