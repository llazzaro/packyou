import os
import sys
import logging
from pathlib import Path

from importlib.abc import SourceLoader, MetaPathFinder
from importlib.machinery import ModuleSpec

import requests
from git import Repo

from packyou import find_module_path_in_cloned_repos


MODULES_PATH = str(Path(__file__).parent)
GITHUB_REPOSITORIES_DIRECTORY = str(Path(MODULES_PATH) / 'github')
LOGGER = logging.getLogger(__name__)


class GithubFinderAbc(MetaPathFinder):

    def check_username_available(self, username):
        """
            Sometimes github has a - in the username or repository name.
            The - can't be used in the import statement.
        """
        user_profile_url = f'https://github.com/{username}'
        response = requests.get(user_profile_url)
        if response.status_code == 200:
            return user_profile_url
        if response.status_code == 404:
            dash_name = username.replace("_", "-")
            user_profile_url = f'https://github.com/{dash_name}'
            response = requests.get(user_profile_url)
            if response.status_code == 200:
                return user_profile_url
        return None

    def check_repository_available(self, username, repository_name):
        repo_url = f'https://github.com/{username}/{repository_name}.git'
        response = requests.get(repo_url)
        if response.status_code == 404:
            if '_' in username:
                dash_user = username.replace("_", "-")
                repo_url = (
                    f'https://github.com/{dash_user}'
                    f'/{repository_name}.git'
                )
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url
            if '_' in repository_name:
                dash_repo = repository_name.replace("_", "-")
                repo_url = (
                    f'https://github.com/{username}'
                    f'/{dash_repo}.git'
                )
                response = requests.get(repo_url)
                if response.status_code == 200:
                    return repo_url

            dash_user = username.replace("_", "-")
            dash_repo = repository_name.replace("_", "-")
            repo_url = (
                f'https://github.com/{dash_user}'
                f'/{dash_repo}.git'
            )
            response = requests.get(repo_url)
            if response.status_code == 200:
                return repo_url
            raise ImportError('Github repository not found.')

        return repo_url


class GithubLoader(SourceLoader):

    def __init__(self, fullname, path, repo_url=None):
        self.github_token = token = os.environ.get("GITHUB_TOKEN")

        if not token:
            self.repo_url = repo_url
        else:
            base = repo_url[len("https://"):]
            self.repo_url = f"https://{token}:x-oauth-basic@{base}"

        self.name = fullname
        if path:
            self.path = path[0]
        self.username = None
        self.repository_name = None
        self.root_module = None

    def clone_github_repo(self):
        """
            Clones a github repo with a username and repository_name
        """
        repository_local_destination = (
            Path(MODULES_PATH) / 'github'
            / self.username / self.repository_name
        )
        if not repository_local_destination.exists():
            Repo.clone_from(
                self.repo_url,
                str(repository_local_destination),
                branch='master',
            )
            (repository_local_destination / '__init__.py').touch()

    def get_data(self, path):
        LOGGER.info(f'get data from {path}')
        return Path(path).read_text(encoding='utf-8')

    def get_filename(self, fullname):
        LOGGER.info(
            f'Get filename for {fullname}.'
            f' Current Path is {self.path}'
        )
        filename = Path(self.path) / '__init__.py'
        if not filename.exists():
            filename = Path(f'{self.path}.py')
            if not filename.exists():
                raise ImportError(f'Filename {filename} not found.')
        return str(filename)

    def load_module(self, fullname):
        """
            Given a name it will load the module from github.
            When the project is not locally stored it will clone the
            repo from github.
        """
        LOGGER.info(f'Loading module {fullname}')
        if fullname in sys.modules:
            return sys.modules[fullname]

        splitted_names = fullname.split('.')
        if 'github' in splitted_names:
            if len(splitted_names) >= 3:
                gh_idx = splitted_names.index('github')
                self.username = splitted_names[gh_idx + 1]
            if len(splitted_names) >= 4:
                gh_idx = splitted_names.index('github')
                self.repository_name = splitted_names[gh_idx + 2]

            if self.username and self.repository_name:
                self.clone_github_repo()

            if len(splitted_names) == 2:
                return super().load_module(fullname)
            if len(splitted_names) == 3:
                username_directory = (
                    Path(MODULES_PATH) / 'github' / self.username
                )
                if not username_directory.exists():
                    username_directory.mkdir(parents=True, exist_ok=True)
                    (username_directory / '__init__.py').touch()
                return super().load_module(fullname)
            if len(splitted_names) >= 4:
                module = super().load_module(fullname)
                parent, _, current_module = fullname.rpartition('.')
                uname = self.username
                rname = self.repository_name
                root_modules = [
                    f'packyou.github.{uname}.{rname}',
                    f'packyou.github.{uname}.{rname}.{rname}',
                ]
                LOGGER.info(f'Current module is {current_module}')
                if fullname in root_modules:
                    self.root_module = fullname
                    sys.modules[current_module] = module
                return module

        else:
            module = super().load_module(fullname)
            sys.modules[fullname] = module
            if not module:
                raise ImportError
            return module


class GithubFinder(GithubFinderAbc):
    """
        Import hook that will allow to import from the specific loader.
    """
    def find_module_in_cloned_repos(self, fullname):
        return find_module_path_in_cloned_repos(fullname)

    def find_spec(self, fullname, paths, target=None):
        LOGGER.info(f'Loading Spec -> {fullname}')
        repo_url = None
        if fullname.startswith('packyou.github.'):

            splitted_names = fullname.split('.')

            if len(splitted_names) >= 3:
                gh_idx = splitted_names.index('github')
                username = splitted_names[gh_idx + 1]
                if not self.check_username_available(username):
                    return

            if len(splitted_names) >= 4:
                gh_idx = splitted_names.index('github')
                repository_name = splitted_names[gh_idx + 2]
                repo_url = self.check_repository_available(
                    username, repository_name,
                )
                if not repo_url:
                    return
            fixed_paths = []
            for path in paths:
                p = Path(path)
                if (p / p.name).exists():
                    p = p / p.name
                current_module = fullname.rpartition('.')[2]
                if p.name != current_module:
                    p = p / fullname.rpartition('.')[2]
                fixed_paths.append(str(p))
            loader = GithubLoader(fullname, fixed_paths, repo_url)
            module = loader.load_module(fullname)
            if module is not None:
                spec = ModuleSpec(fullname, loader, is_package=True)
                spec.submodule_search_locations = fixed_paths
                return spec
            return None
        else:
            # Only search cloned repos for non-packyou imports
            if fullname.startswith('packyou.') or fullname == 'packyou':
                return None
            LOGGER.info('Searching in cloned repos')
            found_paths, remaining = self.find_module_in_cloned_repos(fullname)
            LOGGER.info(f'Result found was {found_paths}')
            if found_paths and not remaining:
                loader = GithubLoader(fullname, found_paths)
                module = loader.load_module(fullname)
                if module is not None:
                    spec = ModuleSpec(fullname, loader, is_package=True)
                    spec.submodule_search_locations = found_paths
                    return spec
            return None


sys.meta_path = [GithubFinder()] + sys.meta_path
