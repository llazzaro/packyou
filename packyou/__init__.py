# -*- coding: utf-8 -*-
import os
import sys
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder, Loader

import requests

from git import Repo


MODULES_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = os.path.join(MODULES_PATH, 'github')


class PathFileFinder:
    pass


class GithubModuleLoader(Loader):

    def __init__(self, path):
        self.path = path

    def exec_module(self, module):
        pass

    def check_repository_available(self, username, repository_name):
        """
            Sometimes github has a - in the username or repository name.
            The - can't be used in the import statement.
        """
        repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name)
        response = requests.get(repo_url)
        if response.status_code == 404:
            if '_' in username:
                repo_url = 'https://github.com/{0}/{1}.git'.format(username.replace('_', '-'), repository_name)
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url
            if '_' in repository_name:
                repo_url = 'https://github.com/{0}/{1}.git'.format(username, repository_name.replace('_', '-'))
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url

            repo_url = 'https://github.com/{0}/{1}.git'.format(username.replace('_', '-'), repository_name.replace('_', '-'))
            response = requests.get(repo_url)
            if response.status_code == 200:
                return repo_url
            raise ImportError('Github repository not found.')

        return repo_url

    def clone_github_repo(self, username, repository_name):
        """
            Clones a github repo with a username and repository_name
        """
        repo_url = self.check_repository_available(username, repository_name)
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(repo_url, repository_local_destination, branch='master')
            init_filename = os.path.join(repository_local_destination, '__init__.py')
            open(init_filename, 'a').close()

        self.update_sys_path()

    def update_sys_path(self):
        """
            Iterates over all cloned repos and add them to the syspath.
            This was required since cloned project uses relative imports.
        """
        github_repos_path = os.path.join(MODULES_PATH, 'github')
        for file_or_directory in os.listdir(github_repos_path):
            if os.path.isdir(file_or_directory) or os.path.splitext(file_or_directory)[1] in ['.py', '.pyc']:
                if file_or_directory not in sys.path:
                    sys.path.append(file_or_directory)

    def load_module(self, fullname):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        print(fullname)
        if fullname in sys.modules:
            return sys.modules[fullname]

        splitted_names = fullname.split('.')
        username = None
        repository_name = None
        self.update_sys_path()
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
                username_init_filename = os.path.join(MODULES_PATH, 'github', username, '__init__.py')
                open(username_init_filename, 'a').close()
                return super().load_module(fullname)
            if len(splitted_names) >= 4:
                return super().load_module(fullname)

        else:
            module = super().load_module(fullname)
            if not module:
                raise ImportError
            return module


class PackYouFinder(MetaPathFinder):
    """
        Import hook that will allow to import from the specific loader.
    """

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('packyou.github.'):
            print('ACA ', fullname)
            loader = GithubModuleLoader(path)
            return ModuleSpec(fullname, loader)
        return None


sys.meta_path.append(PackYouFinder())
