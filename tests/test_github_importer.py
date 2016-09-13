#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import Mock, patch

from packyou import ImportFromGithub


@patch('sys.modules')
@patch('packyou.PathFinder')
@patch('packyou.requests')
def test_first_level_of_import_name(requests_mock, path_finder_mock, sys_modules_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    importer = ImportFromGithub()

    mocked_response = Mock()
    mocked_response.status_code = 200
    requests_mock.return_value = mocked_response
    assert 'packyou.github' not in sys_modules
    importer.load_module('packyou.github')
    assert 'packyou.github' in sys_modules
    # check cached module in sys.modules
    importer.load_module('packyou.github')
    assert path_finder_mock.mock_calls[0][1] == ('packyou.github',)


@patch('packyou.open')
@patch('os.mkdir')
@patch('sys.modules')
@patch('packyou.PathFinder')
def test_second_level_of_import_name(path_finder_mock, sys_modules_mock, mkdir_mock, open_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    importer = ImportFromGithub()
    importer.load_module('packyou.github.github_username')

    assert 'packyou/github/github_username/__init__.py' in open_mock.mock_calls[0][1][0]
    assert 'packyou/github/github_username' in mkdir_mock.mock_calls[0][1][0]
    assert path_finder_mock.mock_calls[0][1] == ('packyou.github.github_username', )


@patch('packyou.open')
@patch('packyou.Repo')
@patch('sys.modules')
@patch('packyou.PathFinder')
@patch('packyou.requests')
def test_third_level_of_import_name(requests_mock, path_finder_mock, sys_modules_mock, repo_mock, open_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    importer = ImportFromGithub()

    mocked_response = Mock()
    mocked_response.status_code = 200
    requests_mock.return_value = mocked_response

    importer.load_module('packyou.github.github_username.test_repo')
    assert 'packyou/github/github_username/test_repo/__init__.py' in open_mock.mock_calls[0][1][0]
    assert repo_mock.mock_calls[0][1][0] == 'https://github.com/github_username/test_repo.git'
    assert 'packyou/github/github_username/test_repo' in repo_mock.mock_calls[0][1][1]
    assert path_finder_mock.mock_calls[0][1] == ('packyou.github.github_username.test_repo', )
    assert requests_mock.mock_calls[0][1][0] == 'https://github.com/github_username/test_repo.git'
