from typing import NamedTuple

from pylogg.settings import SettingsParser


class TestSettings(NamedTuple):
    name: str   = 'Mike'
    age : int   = 94

class Settings(NamedTuple):
    YAML = None

    # Define the sections ...
    Test : TestSettings

    @classmethod
    def load(c, yaml_file = None, first_arg = False) -> 'Settings':
        c.YAML = SettingsParser('example', yaml_file, first_arg=first_arg)
        return c.YAML.populate(c)

    def save(self, yaml_file = None):
        self.YAML.save(self, yaml_file=yaml_file)


if __name__ == '__main__':
    # Load settings from YAML
    settings = Settings.load('settings.yaml')
    test = settings.Test
    print("Loaded from yaml:", test)

    # Change single value of settings
    test = test._replace(age = 50)
    print("Changed age from yaml:", test)

    # Create new settings.
    test = TestSettings(name='John', age=23)

    # This now has updated values.
    print("New settings:", test)

    # Update global settings
    settings = settings._replace(Test = test)
    print("All updated settings:", settings)

    # Save to the yaml file.
    # settings.save()
