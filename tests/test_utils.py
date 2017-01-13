#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pdb
from mock import patch

try:
    from StringIO import StringIO
    # monkey patching on StringIO
    def debug(*args):
        return args[0]

    StringIO.__exit__ = debug
    StringIO.__enter__ = debug

except ImportError:
    from io import StringIO

from packyou.utils import get_filename, get_source


@patch('os.path.isdir')
def test_get_filename_init_case(os_path_isdir_mock):
    full_name = 'packyou.github'
    os_path_isdir_mock.return_value = True
    expected = '/home/leonardo/visible/packyou/packyou/github/__init__.py'
    assert expected == get_filename(full_name)


@patch('os.path.isdir')
def test_get_filename_py_file_case(os_path_isdir_mock):
    full_name = 'packyou.github.pepe'
    os_path_isdir_mock.return_value = False
    expected = '/home/leonardo/visible/packyou/packyou/github/pepe.py'
    assert expected == get_filename(full_name)


@patch('os.path.isdir')
def test_get_source(os_path_isdir_mock):
    full_name = 'packyou.github.pepe'
    os_path_isdir_mock.return_value = False
    fake_file = StringIO()
    fake_file.write('ok!')
    fake_file.seek(0)
    with patch('packyou.utils.open', return_value=fake_file, create=True) as open_mock:
        assert 'ok!' == get_source(full_name)
        pdb.set_trace()


@patch('os.path.isdir')
def test_get_source_package(os_path_isdir_mock):
    full_name = 'packyou.github.pepe'
    os_path_isdir_mock.return_value = True
    fake_file = StringIO()
    fake_file.write('ok!')
    fake_file.seek(0)
    with patch('packyou.utils.open', return_value=fake_file, create=True) as open_mock:
        assert 'ok!' == get_source(full_name)
        pdb.set_trace()
