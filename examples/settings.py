from typing import NamedTuple

from pylogg.settings import YAMLSettings

# Load settings from `settings.yaml` file and environment variables.
# If a file is given as the first argument, load it as the YAML file.
# Environment variables will be searched as `SETT_TEST_ROW1` etc.
# Prefer environment variable definitions over YAML definitions.
yaml = YAMLSettings(
    'sett', first_arg_as_file=True, load_env=True, prefer_env=True)


# Define a classmethod to load the settings.
class Test(NamedTuple):
    row1: float = 23.6
    row2: str   = 'Hello'
    row3: str   = 'world'

    @classmethod
    def settings(c) -> 'Test': return yaml(c)


if __name__ == '__main__':
    # Use the class method to load the settings.
    test = Test.settings()
    print(test)

    # Settings can be globally set/updated.
    updated = test._replace(row3='Earth')
    yaml.set(Test, updated)

    # This now has updated values.
    print(yaml)

    if not yaml.is_loaded():
        # Write to the YAML file.
        yaml.save()
