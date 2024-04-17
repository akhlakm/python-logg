from pylogg.settings import NamedTuple, SettingsParser


def test_load_settings(assets, tmp_path):
    asset_file = assets / "settings.yaml"
    test_output = tmp_path / "settings.yaml"

    class Test(NamedTuple):
        row1: float = 100.0
        row2: str   = 'Package'
        row3: str   = 'Settings'
        row4: str   = 'Default'

    class Person(NamedTuple):
        name : str = 'John'
        age : int = 3

    class Settings(NamedTuple):
        YAML = None
        TestSettings : Test
        PersonSettings : Person

        @classmethod
        def load(c, yaml_file = None, first_arg = False) -> 'Settings':
            c.YAML = SettingsParser('pytest', yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def create(self, newfile = None):
            self.YAML.save(self, yaml_file=newfile)


    sett = Settings.load(asset_file)
    test = sett.TestSettings
    assert test.row1 == 23.6
    assert test.row2 == "Hello"
    assert test.row3 == "World"
    assert test.row4 == "Default"

    sett = sett._replace(TestSettings = sett.TestSettings._replace(row1 = 90.0))
    test = sett.TestSettings
    assert test.row1 == 90.0
    assert test.row4 == "Default"

    person = sett.PersonSettings
    assert person.name == "Mike"
    assert person.age == 29

    sett.create(test_output)
    assert 'row1: 90.0' in test_output.read_text()
    assert 'age: 29' in test_output.read_text()
    assert 'row4: Default' in test_output.read_text()


def test_yaml_write(assets, tmp_path):
    asset_file = assets / "settings.yaml"
    test_output = tmp_path / "settings.yaml"

    class Test(NamedTuple):
        row1: float = 23.6
        row2: str   = 'Hello'
        row3: str   = 'World'

    class Settings(NamedTuple):
        YAML = None
        TestSettings : Test

        @classmethod
        def load(c, yaml_file = None, first_arg = False) -> 'Settings':
            c.YAML = SettingsParser('pytest', yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def save(self, newfile = None):
            self.YAML.save(self, yaml_file=newfile)

    settings = Settings.load(asset_file)
    test = settings.TestSettings

    assert test.row1 == 23.6
    assert type(test.row1) == float
    assert test.row2 == 'Hello'

    settings.save(newfile=test_output)
    assert str(test.row1) in test_output.read_text()
    assert test.row2 in test_output.read_text()
    assert test.row3 in test_output.read_text()


def test_args_subs():
    import sys
    sys.argv += ['--name', 'world', '--debug', '--num', '22']

    class Test(NamedTuple):
        greeting: str   = 'Hello $name'
        number : int    = '$num'
        debug : bool    = '$debug'

    class Settings(NamedTuple):
        YAML = None
        TestSettings : Test

        @classmethod
        def load(c, yaml_file = None, first_arg = False) -> 'Settings':
            c.YAML = SettingsParser('pytest', yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def save(self, newfile = None):
            self.YAML.save(self, yamlfile=newfile)

    settings = Settings.load(None)
    test = settings.TestSettings

    assert test.greeting == 'Hello world'
    assert test.number == 22
    assert test.debug == True

    print(test)


def test_postitional_args():
    import sys

    yaml = SettingsParser('pytest')
    print(yaml._pos_args)

    sys.argv += ['--name', 'world', 'settings2.yaml', '--debug', '--num', '22']
    yaml = SettingsParser('pytest')
    print(yaml._pos_args)

    sys.argv += ['settings2.yaml']
    yaml = SettingsParser('pytest')
    assert yaml._pos_args == ['settings2.yaml', 'settings2.yaml']
    print(yaml._pos_args)
