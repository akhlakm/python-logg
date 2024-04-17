from typing import ClassVar

from pydantic import BaseModel

from pylogg.settings import SettingsParser


class TestSettings(BaseModel):
    name: str   = 'Mike'
    age : int   = 94

class Settings(BaseModel):
    YAML : ClassVar = None

    # Define the sections ...
    Test : TestSettings

    @classmethod
    def load(c, yaml_file = None, first_arg = False) -> 'Settings':
        c.YAML = SettingsParser('example', yaml_file, first_arg=first_arg)
        return c.YAML.populate(c)

    def save(self, yaml_file = None):
        self.YAML.save(self, yaml_file=yaml_file)


if __name__ == '__main__':
    settings = Settings.load('settings.yaml')
    test = settings.Test
    print(test)

    # Settings can be globally set/updated.
    test.age = 23

    # This now has updated values.
    print(test)

    # All settings
    print(settings)

    # Save to the yaml file.
    # settings.save()
