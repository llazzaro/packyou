import requests
from importlib.abc import MetaPathFinder


class GithubFinderAbc(MetaPathFinder):

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
