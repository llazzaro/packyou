import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from packyou.py3 import GithubLoader, MODULES_PATH


class TestGithubLoaderInit:

    def test_init_without_token(self):
        """Should set repo_url directly when no GITHUB_TOKEN."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('packyou.github.user.repo', ['/some/path'], 'https://github.com/user/repo.git')
            assert loader.repo_url == 'https://github.com/user/repo.git'
            assert loader.name == 'packyou.github.user.repo'
            assert loader.path == '/some/path'
            assert loader.username is None
            assert loader.repository_name is None

    def test_init_with_token(self):
        """Should embed token in repo_url when GITHUB_TOKEN is set."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'mytoken123'}):
            loader = GithubLoader('packyou.github.user.repo', ['/some/path'], 'https://github.com/user/repo.git')
            assert loader.repo_url == 'https://mytoken123:x-oauth-basic@github.com/user/repo.git'
            assert loader.github_token == 'mytoken123'

    def test_init_with_empty_path(self):
        """Should handle empty path list."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', [], 'https://github.com/u/r.git')
            assert loader.name == 'test'


class TestCloneGithubRepo:

    @patch('packyou.py3.Repo')
    @patch.object(Path, 'exists', return_value=False)
    def test_clone_when_not_exists(self, mock_exists, mock_repo):
        """Should clone repo when local destination doesn't exist."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', ['/path'], 'https://github.com/user/repo.git')
            loader.username = 'user'
            loader.repository_name = 'repo'

            with patch.object(Path, 'touch'):
                loader.clone_github_repo()

            mock_repo.clone_from.assert_called_once()
            call_args = mock_repo.clone_from.call_args
            assert call_args[0][0] == 'https://github.com/user/repo.git'
            assert 'user' in call_args[0][1]
            assert 'repo' in call_args[0][1]

    @patch('packyou.py3.Repo')
    @patch.object(Path, 'exists', return_value=True)
    def test_skip_clone_when_exists(self, mock_exists, mock_repo):
        """Should not clone when local destination already exists."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', ['/path'], 'https://github.com/user/repo.git')
            loader.username = 'user'
            loader.repository_name = 'repo'
            loader.clone_github_repo()

            mock_repo.clone_from.assert_not_called()


class TestGetData:

    def test_reads_file_content(self, tmp_path):
        """Should read and return file content."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', [str(tmp_path)], None)
            content = loader.get_data(str(test_file))
            assert content == "print('hello')"


class TestGetFilename:

    @patch.object(Path, 'exists', return_value=True)
    def test_package_path(self, mock_exists):
        """Should return __init__.py path when it exists."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', ['/some/path'], None)
            result = loader.get_filename('some.module')
            assert result.endswith('__init__.py')

    @patch.object(Path, 'exists', side_effect=[False, True])
    def test_py_file_path(self, mock_exists):
        """Should return .py path when __init__.py doesn't exist but .py does."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', ['/some/path'], None)
            result = loader.get_filename('some.module')
            assert result.endswith('.py')

    @patch.object(Path, 'exists', return_value=False)
    def test_import_error_on_missing(self, mock_exists):
        """Should raise ImportError when neither __init__.py nor .py exists."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('test', ['/some/path'], None)
            with pytest.raises(ImportError, match='not found'):
                loader.get_filename('some.module')


class TestLoadModule:

    def test_returns_cached_module(self):
        """Should return module from sys.modules if already cached."""
        fake_module = MagicMock()

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('packyou.github.user.repo', ['/path'], 'https://github.com/user/repo.git')

            with patch.dict(sys.modules, {'packyou.github.user.repo': fake_module}):
                result = loader.load_module('packyou.github.user.repo')
                assert result is fake_module

    @patch.object(Path, 'mkdir')
    @patch.object(Path, 'exists', return_value=False)
    def test_level_3_creates_username_dir(self, mock_exists, mock_mkdir):
        """Loading packyou.github.username should create the username directory."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('packyou.github.testuser', ['/path'], None)

            with patch.object(Path, 'touch'):
                with patch.object(type(loader).__mro__[1], 'load_module', return_value=MagicMock()) as mock_super:
                    result = loader.load_module('packyou.github.testuser')
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_level_2_github_import(self):
        """Loading packyou.github should delegate to super."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader('packyou.github', ['/path'], None)

            with patch.object(type(loader).__mro__[1], 'load_module', return_value=MagicMock()) as mock_super:
                result = loader.load_module('packyou.github')
                mock_super.assert_called_once_with('packyou.github')

    @patch('packyou.py3.Repo')
    @patch.object(Path, 'exists', return_value=False)
    def test_level_4_clones_and_loads(self, mock_exists, mock_repo):
        """Loading packyou.github.user.repo should clone and load."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader(
                'packyou.github.user.repo',
                ['/path'],
                'https://github.com/user/repo.git'
            )

            mock_module = MagicMock()
            with patch.object(Path, 'touch'):
                with patch.object(type(loader).__mro__[1], 'load_module', return_value=mock_module):
                    result = loader.load_module('packyou.github.user.repo')
                    assert result is mock_module
                    mock_repo.clone_from.assert_called_once()

    @patch('packyou.py3.Repo')
    @patch.object(Path, 'exists', return_value=False)
    def test_level_4_sets_root_module_in_sys_modules(self, mock_exists, mock_repo):
        """Loading root module should add short name to sys.modules."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader(
                'packyou.github.user.myrepo',
                ['/path'],
                'https://github.com/user/myrepo.git'
            )

            mock_module = MagicMock()
            with patch.object(Path, 'touch'):
                with patch.object(type(loader).__mro__[1], 'load_module', return_value=mock_module):
                    result = loader.load_module('packyou.github.user.myrepo')
                    assert sys.modules.get('myrepo') is mock_module

    def test_non_github_module_loads_via_super(self):
        """Loading a non-github module should delegate to super."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader(
                'somelib.utils', ['/path'], None,
            )

            mock_module = MagicMock()
            with patch.object(
                type(loader).__mro__[1], 'load_module',
                return_value=mock_module,
            ):
                result = loader.load_module('somelib.utils')
                assert result is mock_module
                assert sys.modules.get('somelib.utils') is mock_module

    def test_non_github_module_raises_on_none(self):
        """Loading a non-github module should raise ImportError if None."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GITHUB_TOKEN', None)
            loader = GithubLoader(
                'somelib.badmod', ['/path'], None,
            )

            # Ensure it's not cached from a prior call
            sys.modules.pop('somelib.badmod', None)
            with patch.object(
                type(loader).__mro__[1], 'load_module',
                return_value=None,
            ):
                with pytest.raises(ImportError):
                    loader.load_module('somelib.badmod')
