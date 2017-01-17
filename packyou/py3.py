# -*- coding: utf-8 -*-
import os
import sys

from importlib.machinery import ModuleSpec
from importlib.abc import FileLoader

from git import Repo

from packyou import GithubFinderAbc


MODULES_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_REPOSITORIES_DIRECTORY = os.path.join(MODULES_PATH, 'github')


class GithubLoader(FileLoader):

    def __init__(self, fullname, path, repo_url):
        self.name = fullname
        self.path = path
        self.repo_url = repo_url

#    def exec_module(self, module):
#        super().exec_module(module)

    def clone_github_repo(self, username, repository_name):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = os.path.join(MODULES_PATH, 'github', username, repository_name)
        if not os.path.exists(repository_local_destination):
            Repo.clone_from(self.repo_url, repository_local_destination, branch='master')
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

    def get_source(self):
        pass

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
                import ipdb
                ipdb.set_trace()
                return super().load_module(fullname)

        else:
            module = super().load_module(fullname)
            if not module:
                raise ImportError
            return module


class GithubFinder(GithubFinderAbc):
    """
        Import hook that will allow to import from the specific loader.
    """

    def find_spec(self, fullname, path, target=None):
        print(fullname)
        repo_url = None
        import ipdb
        ipdb.set_trace()
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


sys.meta_path.append(GithubFinder())
