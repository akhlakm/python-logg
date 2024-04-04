from pylogg.settings import NamedTuple, YAMLSettings


def test_load_settings(assets, tmp_path):
    asset_file = assets / "settings.yaml"
    test_output = tmp_path / "settings.yaml"

    class Test(NamedTuple):
        row1: float = 100.0
        row2: str   = 'Package'
        row3: str   = 'Settings'

    class Person(NamedTuple):
        name : str = 'John'
        age : int = 3

    class Settings(NamedTuple):
        YAML = None
        TestSettings : Test
        PersonSettings : Person

        @classmethod
        def load(c, yaml_file = None, first_arg = False) -> 'Settings':
            c.YAML = YAMLSettings('pytest')
            c.YAML.load_file(yaml_file=yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def create(self, newfile = None):
            self.YAML.save(self, yamlfile=newfile)


    sett = Settings.load(asset_file)
    sett = sett._replace(TestSettings = sett.TestSettings._replace(row1 = 90.0))
    sett.create(test_output)


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
            c.YAML = YAMLSettings('pytest')
            c.YAML.load_file(yaml_file=yaml_file, first_arg=first_arg)
            return c.YAML.populate(c)

        def save(self, newfile = None):
            self.YAML.save(self, yamlfile=newfile)

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
            c.YAML = YAMLSettings('pytest')
            c.YAML.load_file(yaml_file=yaml_file, first_arg=first_arg)
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

    yaml = YAMLSettings('pytest')
    print(yaml._pos_args)

    sys.argv += ['--name', 'world', 'settings2.yaml', '--debug', '--num', '22']
    yaml = YAMLSettings('pytest')
    print(yaml._pos_args)

    sys.argv += ['settings2.yaml']
    yaml = YAMLSettings('pytest')
    assert yaml._pos_args == ['settings2.yaml', 'settings2.yaml']
    print(yaml._pos_args)
