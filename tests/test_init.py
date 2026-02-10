import os
import sys
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from packyou import get_root_path, find_module_path_in_cloned_repos, init_logging, MODULES_PATH


class TestGetRootPath:

    def test_returns_correct_directory(self):
        """get_root_path should return the packyou package directory."""
        root = get_root_path()
        assert os.path.isdir(root)
        assert root.endswith('packyou')
        assert os.path.exists(os.path.join(root, '__init__.py'))

    def test_returns_string(self):
        """get_root_path should return a string."""
        root = get_root_path()
        assert isinstance(root, str)

    def test_is_absolute_path(self):
        """get_root_path should return an absolute path."""
        root = get_root_path()
        assert os.path.isabs(root)


class TestFindModulePathInClonedRepos:

    def test_find_existing_module(self, tmp_path):
        """Should find a .py file in the package directory."""
        with patch('packyou.MODULES_PATH', str(tmp_path)):
            pkg_dir = tmp_path / "packyou"
            pkg_dir.mkdir()
            (pkg_dir / "somefile.py").touch()

            result_path, remaining = find_module_path_in_cloned_repos("packyou.somefile")
            assert len(result_path) == 1
            assert remaining is None

    def test_not_found_returns_remaining(self, tmp_path):
        """Should return empty path and remaining parts when not found."""
        with patch('packyou.MODULES_PATH', str(tmp_path)):
            result_path, remaining = find_module_path_in_cloned_repos("nonexistent.module")
            assert result_path == []
            assert remaining == "nonexistent.module"

    def test_empty_fullname_parts(self, tmp_path):
        """Should handle module names that match directory structure completely."""
        with patch('packyou.MODULES_PATH', str(tmp_path)):
            sub = tmp_path / "mymod"
            sub.mkdir()

            result_path, remaining = find_module_path_in_cloned_repos("mymod")
            assert remaining is not None or result_path != []


class TestInitLogging:

    def test_default_level(self):
        """init_logging with no args should set INFO level."""
        logger = logging.getLogger('packyou')
        original_handlers = logger.handlers[:]
        logger.handlers = []
        try:
            init_logging()
            assert logger.level == logging.INFO
        finally:
            logger.handlers = original_handlers

    def test_warning_level(self):
        """init_logging with 'warning' should set WARN level."""
        logger = logging.getLogger('packyou')
        original_handlers = logger.handlers[:]
        logger.handlers = []
        try:
            init_logging(level='warning')
            assert logger.level == logging.WARN
        finally:
            logger.handlers = original_handlers

    def test_adds_handlers(self):
        """init_logging should add file and stream handlers."""
        logger = logging.getLogger('packyou')
        original_handlers = logger.handlers[:]
        logger.handlers = []
        try:
            init_logging()
            handler_types = [type(h) for h in logger.handlers]
            assert logging.FileHandler in handler_types
            assert logging.StreamHandler in handler_types
        finally:
            logger.handlers = original_handlers


class TestModulesPath:

    def test_modules_path_is_string(self):
        assert isinstance(MODULES_PATH, str)

    def test_modules_path_exists(self):
        assert os.path.isdir(MODULES_PATH)
