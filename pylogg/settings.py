"""
    A simple module to load configurations from environment varibles or
    a YAML file.

    Subclass the typing.NamedTuple, and define a classmethod to load the
    settings.

    yaml = YAMLSettings()

    class Test(NamedTuple):
        name: str   = 'hello'

        @classmethod
        def settings(cls) -> 'Test': return yaml(cls)

    test = Test.settings()
    print(test.name)

"""

import os
import sys
from typing import NamedTuple

import yaml

# For access to the __annotations__ attribute.
assert sys.version_info >= (3, 10), "Minimum Python 3.10 required"


class YAMLSettings:
    """
    Load settings from environment variables and/or a YAML file.

    name:
        Name of the settings. Used as the prefix for environment variables.

    yamlfile:
        YAML file to load the settings.

    first_arg_as_file:
        Treat the first argument as the settings YAML file if any.

    load_env:
        Load settings from environment variables or not.

    prefer_env:
        Override YAML vars with environment variables or vice versa.
    """

    def __init__(self, name : str,
        yamlfile : str = 'settings.yaml', first_arg_as_file : bool = True,
        load_env : bool = True, prefer_env : bool = True):

        # Prefix of the env vars.
        self.name = name

        # Environment variables.
        self.env  = os.environ if load_env else {}

        # Override file vars with env vars.
        self.prefer_env = prefer_env

        # Take the first argument as the settings file if any.
        self.file = (sys.argv[1] if len(sys.argv) > 1 else yamlfile) \
            if first_arg_as_file else yamlfile

        # YAML file loaded variables.
        self.yamlvars : dict[str, dict[str, any]] = {}

        # Cache for the processed sections.
        self.cache = {}

        self.load_file()


    def __repr__(self) -> str:
        s = self.__class__.__name__ + ": "
        for k, v in self.cache.items():
            s += f"{k} {v._asdict()}"
        return s

    def __call__(self, cls : NamedTuple):
        """ Populate settings to the current class/section. """

        assert hasattr(cls, '_fields'), "Settings must be a NamedTuple."

        fields = {}
        classname : str = cls.__name__

        if classname in self.cache:
            return self.cache[classname]

        # for each namedtuple fields ...
        for field in cls._fields:
            data_type = cls.__annotations__[field]
            value = cls._field_defaults.get(field, None)

            if value is not None:
                try:
                    value = data_type(value)
                except:
                    raise ValueError(
                        f"Invalid default for {classname}.{field}: {value}")

            env_var_name = \
                f"{self.name.upper()}_{classname.upper()}_{field.upper()}"

            if not self.prefer_env:
                value = self._get_env(env_var_name, value)

            # Override with YAML file vars.
            value = self._get_yaml(classname, field, value)

            # Override with env vars.
            if self.prefer_env:
                value = self._get_env(env_var_name, value)

            # Convert to expected type.
            if value is not None:
                try:
                    value = data_type(value)
                except:
                    raise ValueError(
                        f"Invalid type for {classname}.{field}: {value}")

            # Add to class fields
            fields[field] = value

        # Cache for future.
        self.cache[classname] = cls(**fields)

        # Return initialized class.
        return self.cache[classname]


    def _get_env(self, var_name, default_value):
        return self.env.get(var_name, default_value)


    def _get_yaml(self, classname, var_name, default_value):
        if classname in self.yamlvars:
            return self.yamlvars[classname].get(var_name, default_value)
        else:
            return default_value


    def set(self, cls : type, instance : NamedTuple):
        """ Set the cached instance of a class with new version.
            Useful to update the global settings or writing new sections
            to YAML file.
        """
        assert type(instance) == cls, "Class and instance do not match"

        classname = cls.__name__
        self.cache[classname] = instance


    def load_file(self):
        """ Load the variables of the YAML file. """
        if os.path.isfile(self.file):
            yamlfile = yaml.safe_load(open(self.file))
            for section, fields in yamlfile.items():
                for fieldname, value in fields.items():
                    if section not in self.yamlvars:
                        self.yamlvars[section] = {}
                    self.yamlvars[section][fieldname] = value


    def is_loaded(self) -> bool:
        """ Returns True if at least one section from YAML file was loaded. """
        return len(self.yamlvars) > 0


    def save(self, *sections : NamedTuple, yamlfile : str = None):
        """ Save the given sections to YAML file.
            If no section is specified, all sections are written.
            If no yamlfile is given, the initial file is used.
        """
        configs = {}
        outfile = yamlfile if yamlfile is not None else self.file

        # Use all sections
        if len(sections) == 0:
            sections = self.cache.values()

        # For each NamedTuple section
        for cls in sections:
            assert hasattr(cls, '_fields'), "Section must be a NamedTuple"

            try:
                # class
                section = cls.__name__
                configs[section] = cls.get()._asdict()

            except AttributeError:
                # instance
                section = cls.__class__.__name__
                configs[section] = cls._asdict()

        yaml.safe_dump(configs, open(outfile, 'w'), indent=4)
        print("Save OK:", outfile)


    def copy_sample(self, sample_file : str):
        """ Copy a sample YAML file to the current settings file. """
        import shutil
        shutil.copyfile(sample_file, self.file)
        print("Save OK:", self.file)
