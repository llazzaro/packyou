import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from packyou.py3 import GithubFinder, GithubFinderAbc


class TestCheckUsernameAvailable:

    @patch('packyou.py3.requests')
    def test_username_exists(self, mock_requests):
        """Should return None when username is found (200 on first try)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        finder = GithubFinderAbc()
        result = finder.check_username_available('testuser')
        assert result is None
        mock_requests.get.assert_called_once_with('https://github.com/testuser')

    @patch('packyou.py3.requests')
    def test_username_with_dash_fallback(self, mock_requests):
        """Should try underscore-to-dash replacement when 404."""
        responses = [
            MagicMock(status_code=404),
            MagicMock(status_code=200),
        ]
        mock_requests.get.side_effect = responses

        finder = GithubFinderAbc()
        result = finder.check_username_available('test_user')
        assert result == 'https://github.com/test-user'
        assert mock_requests.get.call_count == 2

    @patch('packyou.py3.requests')
    def test_username_404_no_underscore(self, mock_requests):
        """Should return None when 404 and no underscore replacement succeeds."""
        responses = [
            MagicMock(status_code=404),
            MagicMock(status_code=404),
        ]
        mock_requests.get.side_effect = responses

        finder = GithubFinderAbc()
        result = finder.check_username_available('test_user')
        assert result is None


class TestCheckRepositoryAvailable:

    @patch('packyou.py3.requests')
    def test_repo_found_directly(self, mock_requests):
        """Should return repo URL when found on first try."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        finder = GithubFinderAbc()
        result = finder.check_repository_available('user', 'repo')
        assert result == 'https://github.com/user/repo.git'

    @patch('packyou.py3.requests')
    def test_repo_found_with_username_dash(self, mock_requests):
        """Should find repo when username needs underscore-to-dash."""
        responses = [
            MagicMock(status_code=404),
            MagicMock(status_code=200),
        ]
        mock_requests.get.side_effect = responses

        finder = GithubFinderAbc()
        result = finder.check_repository_available('user_name', 'repo')
        assert result == 'https://github.com/user-name/repo.git'

    @patch('packyou.py3.requests')
    def test_repo_found_with_reponame_dash(self, mock_requests):
        """Should find repo when repo name needs underscore-to-dash."""
        responses = [
            MagicMock(status_code=404),
            MagicMock(status_code=200),
        ]
        mock_requests.get.side_effect = responses

        finder = GithubFinderAbc()
        result = finder.check_repository_available('user', 'repo_name')
        assert result == 'https://github.com/user/repo-name.git'

    @patch('packyou.py3.requests')
    def test_repo_found_with_both_dash(self, mock_requests):
        """Should find repo when both user and repo need underscore-to-dash."""
        responses = [
            MagicMock(status_code=404),
            MagicMock(status_code=404),
            MagicMock(status_code=404),
            MagicMock(status_code=200),
        ]
        mock_requests.get.side_effect = responses

        finder = GithubFinderAbc()
        result = finder.check_repository_available('user_name', 'repo_name')
        assert result == 'https://github.com/user-name/repo-name.git'

    @patch('packyou.py3.requests')
    def test_repo_not_found_raises_import_error(self, mock_requests):
        """Should raise ImportError when all combinations return 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        finder = GithubFinderAbc()
        with pytest.raises(ImportError, match='Github repository not found'):
            finder.check_repository_available('user_name', 'repo_name')


class TestGithubFinderFindSpec:

    @patch('packyou.py3.requests')
    def test_non_packyou_import_delegates(self, mock_requests):
        """Non-packyou imports should delegate to find_module_in_cloned_repos."""
        finder = GithubFinder()
        with patch.object(finder, 'find_module_in_cloned_repos', return_value=([], 'some.other.module')) as mock_find:
            result = finder.find_spec('some.other.module', ['/some/path'])
            mock_find.assert_called_once_with('some.other.module')
            assert result is None

    @patch('packyou.py3.requests')
    def test_packyou_github_with_username_only(self, mock_requests):
        """packyou.github.username should check username availability."""
        mock_requests.get.return_value = MagicMock(status_code=200)

        finder = GithubFinder()
        result = finder.find_spec('packyou.github.someuser', ['/some/path'])
        assert result is None

    @patch('packyou.py3.requests')
    def test_packyou_github_returns_none_for_unavailable_user(self, mock_requests):
        """Should return None when username is not available."""
        mock_requests.get.return_value = MagicMock(status_code=404)

        finder = GithubFinder()
        result = finder.find_spec('packyou.github.baduser', ['/some/path'])
        assert result is None


class TestGithubFinderInMetaPath:

    def test_finder_registered(self):
        """GithubFinder should be registered in sys.meta_path."""
        finder_types = [type(f) for f in sys.meta_path]
        assert GithubFinder in finder_types
