"""
    A simple module to load configurations from environment varibles or
    a YAML file.

"""

import os
import string
import sys
from typing import NamedTuple

import yaml

# For access to the __annotations__ attribute.
assert sys.version_info >= (3, 10), "Minimum Python 3.10 required"


class YAMLSettings:
    """
    Load all settings from environment variables and/or a YAML file.

    name:
        Name of the settings. Used as the prefix for environment variables.

    load_env:
        Load settings from environment variables or not.

    prefer_env:
        Override YAML vars with environment variables or vice versa.


    Example: Subclass the typing.NamedTuple, and define a classmethod to load the
    settings.

    class Test(NamedTuple):
        name: str   = 'hello'

    class Settings(NamedTuple):
        YAML = None
        TestSettings : Test

        @classmethod
        def load(c, yaml_file = None, first_arg = False) -> 'Settings':
            c.YAML = YAMLSettings('pytest')
            c.YAML.load_file(yaml_file=yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def save(self, newfile = None):
            self.YAML.save(self, yamlfile=newfile)

    settings = Settings.load(asset_file)
    test = settings.TestSettings
    print(test.name)
    """

    def __init__(self, name : str, load_env : bool = True,
                prefer_env : bool = False):

        # Prefix of the env vars.
        self._name = name

        # Environment variables.
        self._env  = os.environ if load_env else {}

        # Override file vars with env vars.
        self._prefer_env = prefer_env

        # Commandline args.
        self._args = self._get_cmdline_subs()
        self._pos_args = self._get_positional_args()

        # Loaded file path
        self._file = 'settings.yaml'

        # YAML file loaded variables.
        self._yamlvars : dict[str, dict[str, any]] = {}


    def __repr__(self) -> str:
        s = self.__class__.__name__ + ": "
        for k, v in self._yamlvars.items():
            s += f"{k} {v._asdict()}"
        return s


    def _populate_section(self, section_name : str, section_cls : NamedTuple):
        """ Populate settings to the current class/section. """

        assert hasattr(section_cls, '_fields'), "Section must be a NamedTuple."

        fields = {}

        # for each namedtuple fields ...
        for field in section_cls._fields:
            fieldname = f"{section_name}.{field}"
            data_type = section_cls.__annotations__[field]

            # Default value.
            value = section_cls._field_defaults.get(field, None)

            env_var_name = \
                f"{self._name.upper()}_{section_name.upper()}_{field.upper()}"

            if not self._prefer_env:
                value = self._get_env(env_var_name, value)

            # Override with YAML file vars.
            value = self._get_yaml(section_name, field, value)

            # Override with env vars.
            if self._prefer_env:
                value = self._get_env(env_var_name, value)

            # Check if there is any arg template in env vars / yaml.
            value = self._get_arg(fieldname, value)

            # Convert to expected type.
            if value is not None:
                try:
                    value = data_type(value)
                except:
                    raise ValueError(
                        f"Invalid type for {fieldname}: {value}")

            # Add to class fields
            fields[field] = value

        # Return initialized class.
        return section_cls(**fields)


    def populate(self, settings : NamedTuple):
        """ Populate settings to all sections. """

        assert hasattr(settings, '_fields'), "Settings must be a NamedTuple."

        sections = {}

        # for each settings sections ...
        for section_name in settings._fields:
            section_definition = settings.__annotations__[section_name]

            # populate individual section
            value = self._populate_section(section_name, section_definition)

            # Add to class sections
            sections[section_name] = value

        # Return initialized class.
        return settings(**sections)


    def _get_positional_args(self) -> list[str]:
        positionals = []
        for i in range(1, len(sys.argv)):
            field = sys.argv[i]
            if not field.startswith("-"):
                if not sys.argv[i-1].startswith("-"):
                    positionals.append(field)
        return positionals


    def _get_cmdline_subs(self) -> dict:
        """ Create a dictionary of commandline --key value pairs.
        """
        d = {}
        i = 1
        while i < len(sys.argv):
            field = sys.argv[i]
            if field.startswith('--'):
                field = field[2:]   # remove -- prefix
                if i + 1 < len(sys.argv):
                    value = sys.argv[i+1]
                    if value.startswith('--'):
                        value = 1   # boolean flag
                else:
                    value = 1       # boolean flag
                d[field] = value
            i += 1
        return d


    def _get_arg(self, fieldname : str, value) -> str:
        """ Perform string substitution using commandline arguments.
            Substitution placeholders are prefixed with a $.
            Raises ValueError if arguments do not contain a placeholder.
        """
        if type(value) == str and '$' in value:
            tmpl = string.Template(value)
            try:
                value = tmpl.substitute(self._args)
            except KeyError as err:
                err = str(err)[1:-1] # remove quotes
                raise ValueError(
                    f"Argument required for {fieldname}='{value}', --{err} ?")

        return value


    def _get_env(self, var_name, default_value):
        return self._env.get(var_name, default_value)


    def _get_yaml_section(self, classname, default_value):
        return self._yamlvars.get(classname, default_value)


    def _get_yaml(self, classname, var_name, default_value):
        if classname in self._yamlvars:
            return self._yamlvars[classname].get(var_name, default_value)
        else:
            return default_value


    def set(self, cls : type, instance : NamedTuple):
        """ Set the cached instance of a class with new version.
            Useful to update the global settings or writing new sections
            to YAML file.
        """
        assert type(instance) == cls, "Class and instance do not match"

        classname = cls.__name__
        self._cache[classname] = instance


    def load_file(
        self, yaml_file : str = None, first_arg : bool = False):

        """ Load all sections and variables of a YAML file.

        yaml_file:
            YAML file to load the settings.

        first_arg:
            Treat the first argument as the settings YAML file if any.

        """

        self._file = yaml_file if yaml_file else self._file

        # Treat the first argument as the settings file if any.
        if first_arg and len(self._pos_args):
            self._file = self._pos_args[0]

        if os.path.isfile(self._file):
            contents = yaml.safe_load(open(self._file))
            for section, fields in contents.items():
                for fieldname, value in fields.items():
                    if section not in self._yamlvars:
                        self._yamlvars[section] = {}
                    self._yamlvars[section][fieldname] = value


    def is_loaded(self) -> bool:
        """ Returns True if at least one section from YAML file was loaded. """
        return len(self._yamlvars) > 0


    def save(self, settings : NamedTuple, yamlfile : str = None,
                keep_existing : bool = True):
        """ Save the settings to a YAML file.
            If no yamlfile is given, the initial file is used.

            keep_existing:
                Keep the already existing sections in the YAML file.
        """

        configs = self._yamlvars if keep_existing else {}
        outfile = yamlfile if yamlfile is not None else self._file

        assert hasattr(settings, '_fields'), "Settings must be a NamedTuple."

        # for each settings sections ...
        for section_name in settings._fields:
            section = getattr(settings, section_name)

            if hasattr(section, '_asdict'):
                configs[section_name] = section._asdict()

        yaml.safe_dump(configs, open(outfile, 'w'), indent=4)
        print("Save OK:", outfile)


    def copy_sample(self, sample_file : str):
        """ Copy a sample YAML file to the current settings file. """
        import shutil
        shutil.copyfile(sample_file, self._file)
        print("Save OK:", self._file)
