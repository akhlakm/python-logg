from pylogg.settings import NamedTuple, YAMLSettings


def test_yaml_write(assets, tmp_path):
    asset_file = assets / "settings.yaml"
    test_output = tmp_path / "settings.yaml"

    yaml = YAMLSettings('pytest', yamlfile=test_output)

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
