# -*- coding: utf-8 -*-
import os
import sys
import ipdb
import glob

from importlib.machinery import ModuleSpec
from importlib.abc import SourceLoader

from git import Repo

from packyou import GithubFinderAbc


MODULES_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = os.path.join(MODULES_PATH, 'github')


class GithubLoader(SourceLoader):

    def __init__(self, fullname, path, repo_url=None):
        self.name = fullname
        if path:
            self.path = path[0]
        self.repo_url = repo_url

    def clone_github_repo(self, username, repository_name):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(self.repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

    def get_data(self, path):
        print('get data', path)
        with open(path, 'r') as data_file:
            return data_file.read()

    def get_filename(self, fullname):
        if fullname == 'packyou.github.reverse_shell.routersploit':
            ipdb.set_trace()
        parent = '{0}.'.format(self.path.split('packyou/')[2].replace('/', '.'))
        pre_filename = os.path.join(self.path, fullname.split(parent)[1].replace('.', '/'))
        filename = os.path.join(pre_filename, '__init__.py')
        if not os.path.exists(filename):
            filename = '{0}.py'.format(pre_filename)
            if not os.path.exists(filename):
                ipdb.set_trace()
                raise ImportError('Filename {0} not found.'.format(filename))
        print('get filename ', filename)
        return filename

    def load_module(self, fullname):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        print('LOAD', fullname)
        try:
            super().load_module(fullname)
        except Exception as ex:
            print('EX ->', ex)
            ipdb.set_trace()

        if fullname in sys.modules:
            return sys.modules[fullname]

        splitted_names = fullname.split('.')
        username = None
        repository_name = None
        if 'github' in splitted_names:
            if len(splitted_names) >= 3:
                username = splitted_names[splitted_names.index('github') + 1]
            if len(splitted_names) >= 4:
                repository_name = splitted_names[splitted_names.index('github') + 2]

            if username and repository_name:
                self.clone_github_repo(username, repository_name)

            if len(splitted_names) == 2:
                return super().load_module(fullname)
            if len(splitted_names) == 3:
                username_directory = os.path.join(MODULES_PATH, 'github', username)
                if not os.path.exists(username_directory):
                    os.mkdir(username_directory)
                    init_filename = os.path.join(repository_local_destination, '__init__.py')
                    open(init_filename, 'a').close()
                return super().load_module(fullname)
            if len(splitted_names) >= 4:
                ipdb.set_trace()
                module =  super().load_module(fullname)
                return module

        else:
            module = super().load_module(fullname)
            if not module:
                raise ImportError
            return module


class GithubFinder(GithubFinderAbc):
    """
        Import hook that will allow to import from the specific loader.
    """

    def find_module_in_cloned_repos(self, fullname):
        for root, subdirs, files in os.walk(GITHUB_REPOSITORIES_DIRECTORY):
            current_dir = os.path.split(root)[-1]
            if current_dir in ['__pycache__', '.git']:
                continue
            if os.path.isdir(root):
                pass
            if fullname == current_dir:
                # check if the module is here or more deep
                loader = GithubLoader(fullname, root)
                return loader.load_module(fullname)

    def find_spec(self, fullname, path, target=None):
        print('SPEC', fullname)
        print('PATH', path)
        repo_url = None
        if fullname.startswith('packyou.github.'):

            splitted_names = fullname.split('.')

            if len(splitted_names) >= 3:
                username = splitted_names[splitted_names.index('github') + 1]
                if not self.check_username_available(username):
                    return

            if len(splitted_names) >= 4:
                repository_name = splitted_names[splitted_names.index('github') + 2]
                repo_url = self.check_repository_available(username, repository_name)
                if not repo_url:
                    return

            loader = GithubLoader(fullname, path, repo_url)
            return loader.load_module(fullname)
        else:
            # we are in the case of relative imports.
            # all the meta_path finders were already executed.
            # we need to search in the repos path for the specified module
            print('Search in cloned repos')
            found_in_cloned_repos = self.find_module_in_cloned_repos(fullname)
            print('Found result ', found_in_cloned_repos)
            return found_in_cloned_repos


sys.meta_path = [GithubFinder()] + sys.meta_path
