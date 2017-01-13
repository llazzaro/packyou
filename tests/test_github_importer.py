#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
from pytest import raises, main
from mock import Mock, patch

from packyou import GithubLoader, GithubFinder

try:
    from StringIO import StringIO

    def debug(*args):
        return args[0]

    StringIO.__exit__ = debug
    StringIO.__enter__ = debug
except ImportError:
    from io import StringIO


@patch('packyou.modules')
@patch('packyou.requests')
def test_first_level_of_import_name(requests_mock, sys_modules_mock):
    sys_modules = {}

    def getitem(name):
        print(sys_modules)
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    importer = GithubLoader()

    mocked_response = Mock()
    mocked_response.status_code = 200
    requests_mock.return_value = mocked_response
    assert 'packyou.github' not in sys_modules
    importer.load_module('packyou.github')
    assert 'packyou.github' in sys_modules
    # check cached module in sys.modules
    importer.load_module('packyou.github')


@patch('packyou.utils.isdir')
@patch('packyou.exists')
@patch('packyou.mkdir')
@patch('sys.modules')
#@patch('packyou.PathFinder')
def test_second_level_of_import_name(sys_modules_mock, mkdir_mock, exists_mock, isdir_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem

    exists_mock.return_value = False
    isdir_mock.return_value = True

    importer = GithubLoader()

    fake_file = StringIO()
    fake_file.write('print("ok!")')
    fake_file.seek(0)

    fake_file_2 = StringIO()
    fake_file_2.write('print("ok!")')
    fake_file_2.seek(0)

    with patch('packyou.utils.open', return_value=fake_file, create=True) as open_utils_mock:
        with patch('packyou.open', return_value=fake_file_2, create=True) as open_mock:
            importer.load_module('packyou.github.github_username')
            assert 'packyou/github/github_username/__init__.py' in open_mock.mock_calls[0][1][0]
    assert 'packyou/github/github_username' in mkdir_mock.mock_calls[0][1][0]
#    assert path_finder_mock.mock_calls[0][1] == ('packyou.github.github_username', )


@patch('packyou.utils.isdir')
@patch('packyou.isdir')
@patch('packyou.exists')
@patch('packyou.Repo')
@patch('sys.modules')
# @patch('packyou.PathFinder')
@patch('packyou.requests')
def test_third_level_of_import_name(requests_mock, sys_modules_mock, repo_mock, exists_mock, isdir_mock, isdir_utils_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem

    exists_mock.return_value = False
    isdir_mock.return_value = True
    isdir_utils_mock.return_value = True

    importer = GithubLoader()

    mocked_response = Mock()
    mocked_response.status_code = 200
    requests_mock.return_value = mocked_response

    fake_file = StringIO()
    fake_file.write('print("Ok!")')
    fake_file.seek(0)

    fake_file_2 = StringIO()
    fake_file_2.write('print("Ok!")')
    fake_file_2.seek(0)

    with patch('packyou.open', return_value=fake_file, create=True) as open_mock:
        with patch('packyou.utils.open', return_value=fake_file_2, create=True) as open_utils_mock:
            importer.load_module('packyou.github.github_username.test_repo')
    assert 'packyou/github/github_username/test_repo/__init__.py' in open_mock.mock_calls[0][1][0]
    assert repo_mock.mock_calls[0][1][0] == 'https://github.com/github_username/test_repo.git'
    assert 'packyou/github/github_username/test_repo' in repo_mock.mock_calls[0][1][1]
    # assert path_finder_mock.mock_calls[0][1] == ('packyou.github.github_username.test_repo', )
    assert requests_mock.mock_calls[0][1][0] == 'https://github.com/github_username/test_repo.git'


@patch('packyou.open')
# @patch('packyou.PathFinder')
@patch('packyou.requests')
@patch('packyou.Repo')
def test_check_repo_exists_username_with_dash(repo_mock, requests_mock, open_mock):
    urls = []

    def get_side_effect(url):
        urls.append(url)
        mocked_response = Mock()
        mocked_response.status_code = 404
        if 'github-username' in url:
            mocked_response.status_code = 200
        return mocked_response

    requests_mock.get = get_side_effect

    importer = GithubLoader()

    fake_file = StringIO()
    fake_file.write('print("Ok!")')
    fake_file.seek(0)
    with patch('packyou.utils.open', return_value=fake_file, create=True) as open_mock:
        importer.load_module('packyou.github.github_username.test_repo')
    assert set(urls) == set(['https://github.com/github_username/test_repo.git', 'https://github.com/github-username/test_repo.git'])


@patch('packyou.open')
# @patch('packyou.PathFinder')
@patch('packyou.requests')
@patch('packyou.Repo')
def test_check_repo_exists_repository_name_with_dash(repo_mock, requests_mock, open_mock):
    urls = []

    def get_side_effect(url):
        urls.append(url)
        mocked_response = Mock()
        mocked_response.status_code = 404
        if 'test-repo' in url:
            mocked_response.status_code = 200
        return mocked_response

    requests_mock.get = get_side_effect

    importer = GithubLoader()
    importer.load_module('packyou.github.github_username.test_repo')
    assert set(urls) == set(['https://github.com/github_username/test_repo.git', 'https://github.com/github-username/test_repo.git', 'https://github.com/github_username/test-repo.git'])


@patch('packyou.open')
# @patch('packyou.PathFinder')
@patch('packyou.requests')
@patch('packyou.Repo')
def test_repo_does_not_exists(repo_mock, requests_mock, open_mock):
    urls = []

    def get_side_effect(url):
        urls.append(url)
        mocked_response = Mock()
        mocked_response.status_code = 404
        return mocked_response

    requests_mock.get = get_side_effect

    importer = GithubLoader()
    with raises(ImportError):
        importer.load_module('packyou.github.github_username.test_repo')


@patch('packyou.open')
# @patch('packyou.PathFinder')
@patch('packyou.requests')
@patch('packyou.Repo')
def test_check_repo_exists_username_and_repository_name_with_dash(repo_mock, requests_mock, open_mock):
    urls = []

    def get_side_effect(url):
        urls.append(url)
        mocked_response = Mock()
        mocked_response.status_code = 404
        if 'test-repo' in url and 'github-username' in url:
            mocked_response.status_code = 200
        return mocked_response

    requests_mock.get = get_side_effect

    importer = GithubLoader()
    importer.load_module('packyou.github.github_username.test_repo')
    assert set(urls) == set(['https://github.com/github_username/test_repo.git', 'https://github.com/github-username/test_repo.git', 'https://github.com/github_username/test-repo.git', 'https://github.com/github-username/test-repo.git'])


def test_invalid_import():
    importer = GithubLoader()

    with raises(ImportError):
        importer.load_module('os.mkdir')


def test_valid_imports_can_be_imported():
    importer = GithubLoader()
    module = importer.load_module('os.path')
    'split' in dir(module)


def test_find_module():
    importer = GithubFinder()
    with raises(ImportError):
        importer.find_module('pepe.pepe', 'path')

if __name__ == '__main__':
    main()
