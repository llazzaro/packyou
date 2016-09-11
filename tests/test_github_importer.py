#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pytest import raises
from mock import patch

from packyou import ImportFromGithub


@patch('sys.modules')
@patch('imp.find_module')
@patch('imp.load_module')
def test_first_level_of_import_name(imp_load_module, imp_find_module_mock, sys_modules_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    imp_load_module.return_value = 'mocked_module'
    importer = ImportFromGithub()
    module = importer.load_module('packyou.github')

    assert imp_find_module_mock.mock_calls[0][1] == ('github', None)
    assert module == 'mocked_module'
    assert sys_modules_mock['packyou.github'] == 'mocked_module'

    # check cached module in sys.modules
    module = importer.load_module('packyou.github')
    assert module == 'mocked_module'


@patch('packyou.open')
@patch('os.mkdir')
@patch('sys.modules')
@patch('imp.find_module')
@patch('imp.load_module')
def test_second_level_of_import_name(imp_load_module, imp_find_module_mock, sys_modules_mock, mkdir_mock, open_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    imp_load_module.return_value = 'mocked_module'
    importer = ImportFromGithub()
    module = importer.load_module('packyou.github.github_username')

    assert 'packyou/github/github_username/__init__.py' in open_mock.mock_calls[0][1][0]
    assert 'packyou/github/github_username' in mkdir_mock.mock_calls[0][1][0]
    assert imp_find_module_mock.mock_calls[0][1] == ('github_username', None)
    assert module == 'mocked_module'
    assert sys_modules_mock['packyou.github.github_username'] == 'mocked_module'


@patch('packyou.open')
@patch('packyou.Repo')
@patch('sys.modules')
@patch('imp.find_module')
@patch('imp.load_module')
def test_third_level_of_import_name(imp_load_module, imp_find_module_mock, sys_modules_mock, repo_mock, open_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    imp_load_module.return_value = 'mocked_module'
    importer = ImportFromGithub()
    module = importer.load_module('packyou.github.github_username.test_repo')
    assert 'packyou/github/github_username/test_repo/__init__.py' in open_mock.mock_calls[0][1][0]
    assert repo_mock.mock_calls[0][1][0] == 'https://github.com/github_username/test_repo.git'
    assert 'packyou/github/github_username/test_repo' in repo_mock.mock_calls[0][1][1]
    assert imp_find_module_mock.mock_calls[0][1] == ('test_repo', None)
    assert module == 'mocked_module'
    assert sys_modules_mock['packyou.github.github_username.test_repo'] == 'mocked_module'


def test_raise_import_error_when_load_module_is_called_without_github():
    importer = ImportFromGithub()
    with raises(ImportError):
        importer.load_module('os.path')


def test_import_something_already_cloned():
    importer = ImportFromGithub()
    # this call will clone the repo
    module = importer.load_module('packyou.github.llazzaro.test_scripts.test')
    # this call will reuse the cloned repo
    module = importer.load_module('packyou.github.llazzaro.test_scripts.test')
    assert 'function1' in dir(module)
