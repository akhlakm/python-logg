import os
import shutil

import pytest


@pytest.fixture
def assets(tmp_path, request):
    '''
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    '''
    # Pytest test file path.
    filename = request.module.__file__

    # Directory name is same as the test file name.
    asset_dir, _ = os.path.splitext(filename)

    # Copy the files from the asset_dir to a /assets dir of the temp path.
    d = tmp_path / "assets"

    if os.path.isdir(asset_dir):
        shutil.copytree(asset_dir, d)

    return d
