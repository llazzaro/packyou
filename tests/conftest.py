import os
import sys
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_response_200():
    """Return a mock response with status_code 200."""
    response = MagicMock()
    response.status_code = 200
    return response


@pytest.fixture
def mock_response_404():
    """Return a mock response with status_code 404."""
    response = MagicMock()
    response.status_code = 404
    return response


@pytest.fixture(autouse=True)
def clean_packyou_modules():
    """Remove any packyou.github.* entries from sys.modules after each test."""
    yield
    keys_to_remove = [k for k in sys.modules if k.startswith('packyou.github.') and len(k.split('.')) > 2]
    for key in keys_to_remove:
        del sys.modules[key]


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path
