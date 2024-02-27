from pylogg.settings import NamedTuple, YAMLSettings


def test_yaml_write(assets, tmp_path):
    asset_file = assets / "settings.yaml"
    test_output = tmp_path / "settings.yaml"

    yaml = YAMLSettings('pytest', yamlfile=test_output, first_arg_as_file=False)

    class Test(NamedTuple):
        row1: float = 23.6
        row2: str   = 'Hello'
        row3: str   = 'World'

        @classmethod
        def settings(c) -> 'Test': return yaml(c)

    test = Test.settings()

    assert test.row1 == 23.6
    assert type(test.row1) == float
    assert test.row2 == 'Hello'

    yaml.save(test)
    assert test_output.read_text() == asset_file.read_text()

    yaml.save(Test)
    assert test_output.read_text() == asset_file.read_text()


def test_args_subs():
    import sys
    sys.argv += ['--name', 'world', '--debug', '--num', '22']
    yaml = YAMLSettings('pytest', first_arg_as_file=False)

    class Test(NamedTuple):
        greeting: str   = 'Hello $name'
        number : int    = '$num'
        debug : bool    = '$debug'

        @classmethod
        def settings(c) -> 'Test': return yaml(c)

    test = Test.settings()

    assert test.greeting == 'Hello world'
    assert test.number == 22
    assert test.debug == True

    print(test)


def test_postitional_args():
    import sys

    yaml = YAMLSettings('pytest', first_arg_as_file=False)
    assert yaml.file == 'settings.yaml'
    print(yaml.pos_args)

    sys.argv += ['--name', 'world', 'settings2.yaml', '--debug', '--num', '22']
    yaml = YAMLSettings('pytest', first_arg_as_file=True)
    assert yaml.file == 'settings2.yaml'
    print(yaml.pos_args)

    sys.argv += ['settings2.yaml']
    yaml = YAMLSettings('pytest', first_arg_as_file=True)
    assert yaml.pos_args == ['settings2.yaml', 'settings2.yaml']
    print(yaml.pos_args)
