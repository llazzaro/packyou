# -*- coding: utf-8 -*-
import ipdb
import os
import imp
import sys

from git import Repo

MODULES_PATH = os.path.dirname(os.path.abspath(__file__))


class ImportFromGithub:
    """
        Import hook that will allow to import from a  github repo.
    """
    def __init__(self):
        self.call_number = 0
        self.username = None
        self.path = None
        self.call_mapping = {
            1: 'github',
            2: 'username',
            3: 'repository_name',
        }

    def find_module(self, fullname, path=None):
        if fullname.startswith('packyou.github'):
            self.path = path
            return self

    def find_and_load_module(self, name, complete_name):
        if complete_name in sys.modules:
            return sys.modules[name]
        module_info = imp.find_module(name, self.path)
        module = imp.load_module(name, *module_info)
        sys.modules[complete_name] = module
        return module

    def clone_github_repo(self, username, repository_name):
        repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name)
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            repo = Repo.clone_from(repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()
        #cloned_repo = repo.clone(os.path.join(MODULES_PATH, 'repository_name'))

    def load_module(self, name):
        complete_name = name
        name = name.split('.')[-1]
        self.call_number += 1
        if self.call_number == 1:
            return self.find_and_load_module('github', complete_name)
        if self.call_number == 2:
            self.username = name
            username_init_filename = os.path.join(MODULES_PATH, 'github', self.username, '__init__.py')
            open(username_init_filename, 'a').close()
            return self.find_and_load_module(name, complete_name)
        if self.call_number == 3:
            self.clone_github_repo(self.username, name)
            return self.find_and_load_module(name, complete_name)
        if self.call_number >= 4:
            return self.find_and_load_module(name, complete_name)

sys.meta_path = [ImportFromGithub()]
