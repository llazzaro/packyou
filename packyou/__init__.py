# -*- coding: utf-8 -*-
import os
import sys

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))


class ImportFromGithub(object):
    def __init__(self, *args):
        pass

    def find_module(self, fullname, path=None):
        if fullname.startswith('packyou.github'):
            self.path = path
            return self

    def load_module(self, name):
        print('ACA', name)
        print('ACA', self.path)

sys.meta_path = [ImportFromGithub()]
