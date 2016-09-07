# -*- coding: utf-8 -*-
import sys


class ImportFromGithub(object):
    def __init__(self, *args):
        pass

    def find_module(self, fullname, path=None):
        pass

    def load_module(self, name):
        pass

sys.meta_path = [ImportFromGit()]
