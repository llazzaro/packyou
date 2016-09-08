#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
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


@patch('sys.modules')
@patch('imp.find_module')
@patch('imp.load_module')
def test_seconds_level_of_import_name(imp_load_module, imp_find_module_mock, sys_modules_mock):
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    imp_load_module.return_value = 'mocked_module'
    importer = ImportFromGithub()
    module = importer.load_module('packyou.github.llazzaro')

    assert imp_find_module_mock.mock_calls[0][1] == ('github', None)
    assert module == 'mocked_module'
    assert sys_modules_mock['packyou.github.llazzaro'] == 'mocked_module'


@patch('packyou.open')
@patch('packyou.Repo')
@patch('sys.modules')
@patch('imp.find_module')
@patch('imp.load_module')
def test_third_level_of_import_name(imp_load_module, imp_find_module_mock, sys_modules_mock, repo_mock, open_mock):
    pdb.set_trace()
    sys_modules = {}

    def getitem(name):
        return sys_modules[name]

    def setitem(name, val):
        sys_modules[name] = val

    sys_modules_mock.__getitem__.side_effect = getitem
    sys_modules_mock.__setitem__.side_effect = setitem
    imp_load_module.return_value = 'mocked_module'
    importer = ImportFromGithub()
    module = importer.load_module('packyou.github.llazzaro.test_repo')
    assert imp_find_module_mock.mock_calls[0][1] == ('test_repo', None)
    assert module == 'mocked_module'
    assert sys_modules_mock['packyou.github.llazzaro.test_repo'] == 'mocked_module'
