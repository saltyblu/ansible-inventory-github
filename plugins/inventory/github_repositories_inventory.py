# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from github import Github
import re
import logging
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable
from ansible.inventory.group import to_safe_group_name

DOCUMENTATION = '''
    author:
        - Volker Schmitz (saltyblu)
        - Martin Soentgenrath (merin80)
    name: github-repository-inventory
    short_description: GitHub repositories as inventory source
    version_added: 0.0.0
    description:
        - Get repositories from the GitHub API and store them as hosts.
        - The primary IP addresses contains the Git Repository clone url.
    extends_documentation_fragment:
        - inventory_cache
    options:
        url:
            description: GitHub URL.
            default: 'https://github.com/'
            env:
                - name: GITHUB_INVENTORY_URL
        access_token:
            description: GitHub authentication PAT.
            required: true
            env:
                - name: GITHUB_INVENTORY_ACCESS_TOKEN
        org:
            description: GitHub organization.
            required: true
            env:
                - name: GITHUB_INVENTORY_ORG
        repository_filter:
            description: Repository Filter
            default: ""
            env:
                - name: GITHUB_INVENTORY_SEARCH_FILTER
        cache:
            description: The Cache option
            required: false
            default: False
        group_by_languages:
            description: Load all language Informations from github Repos and group the repositories by Language
            default: false
            env:
                - name: GITHUB_INVENTORY_GROUP_BY_LANGUAGES
        regex_filter:
            description: A regexp which allows grouping of the inventory. For that the pattern will be applied on the repository.name and if a match is found all regex groups matches will be added as group name for the repository
            default: ""
            env:
                - name: GITHUB_INVENTORY_REGEX_GROUP_FILTER
        show_archived_repos:
            description: Exclude archived repos in search, boolean.
            default: false
            env:
                - name: GITHUB_INVENTORY_ARCHIVED
'''

EXAMPLES = '''
# github-inventory.yml
access_token: secure
org: saltyblu
repository_filter: *-deployment
'''


def get_logger(name, logger=None):
    """Get or create a logger instance.

    Args:
        name: Logger name
        logger: Optional pre-configured logger instance

    Returns:
        logger instance
    """
    if logger is not None:
        return logger
    return logging.getLogger(name)


class GitHubRepositoryFetcher:
    """Fetches repositories from GitHub API."""

    def __init__(self, access_token, logger=None, per_page=100):
        """Initialize the GitHub client.

        Args:
            access_token: GitHub API token
            logger: Optional logger instance
        """
        self.access_token = access_token
        self.logger = get_logger('GitHubRepositoryFetcher', logger)
        self._github_client = None
        self.per_page = per_page

    @property
    def github_client(self):
        """Lazy-load GitHub client."""
        if self._github_client is None:
            self._github_client = Github(self.access_token, per_page=self.per_page)
        return self._github_client

    def set_github_client(self, client):
        """Set a custom GitHub client (useful for testing)."""
        self._github_client = client

    def fetch_repositories(
        self,
        repository_filter,
        org,
        archived=False,
        group_by_languages=False
    ):
        """Fetch repositories from GitHub.

        Args:
            repository_filter: Search filter string
            org: GitHub organization
            archived: Include archived repositories
            group_by_languages: Include language information

        Returns:
            List of repository data dictionaries
        """
        repos = []
        try:
            search_result = self.github_client.search_repositories(
                query=repository_filter,
                owner=org,
                sort="updated",
                archived=archived
            )
        except Exception as e:
            self.logger.error(f'Exception while searching repositories: {e}')
            raise

        try:
            for count, repository in enumerate(search_result, 1):
                repo_raw_data = dict(getattr(repository, '_rawData', {}))
                self.logger.debug(f"Group by Language is: {group_by_languages}")

                topics = repo_raw_data.get('topics')
                if topics is None:
                    try:
                        topics = repository.get_topics()
                    except Exception:
                        topics = []
                repo_raw_data['topics'] = topics

                if group_by_languages:
                    repo_raw_data['languages'] = repository.get_languages()
                else:
                    repo_raw_data['languages'] = None

                self.logger.debug(f'Counter: {count} - {repository.name}')
                repos.append(repo_raw_data)

            return repos
        except Exception as e:
            self.logger.error(f'Exception while iterating repositories: {e}')
            raise


class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using GitHub as source. '''

    NAME = 'github_repositories_inventory'

    def __init__(self, logger=None, fetcher=None):
        """Initialize the inventory plugin.

        Args:
            logger: Optional logger instance for testing
            fetcher: Optional GitHubRepositoryFetcher instance for testing
        """
        super(InventoryModule, self).__init__()
        self.cache_key = None
        self.connection = None
        self.logger = get_logger('DynamicInventory', logger)
        self.fetcher = fetcher

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('github_repositories.yaml', 'github_repositories.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending with "github_repositories.yaml/.yml"')
        return valid

    def parse_groupnames(self, repository, regex_filter):
        try:
            matches = re.findall(regex_filter, repository['name'])
            if matches:
                result = []
                main_group = f'main-{matches[0][0]}'
                if main_group:
                    result.append(main_group)
                for match in matches:
                    result.extend(match)
                return result
            else:
                return False
        except Exception as e:
            self.logger.debug(f'Exception while parsing groups: {e}')
            return False

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self.load_cache_plugin()
        cache_key = self.get_cache_key(path)
        self.logger.debug(f'The Cache Key is: {cache_key}')

        # read config from file, this sets 'options'
        self._read_config_data(path)

        user_cache_setting = self.get_option('cache')
        self.logger.debug(f'User Cache Setting is: {user_cache_setting}')
        # read if the user has caching enabled and the cache isn't being refreshed
        attempt_to_read_cache = user_cache_setting and cache
        self.logger.debug(f'Attempt to read cache is: {attempt_to_read_cache}')
        # update if the user has caching enabled and the cache is being refreshed; update this value to True if the cache has expired below
        cache_needs_update = user_cache_setting and not cache
        self.logger.debug(f'Cache needs update is: {cache_needs_update}')

        # get connection host
        self.github_url = str(self.get_option('url'))
        self.access_token = str(self.get_option('access_token'))
        self.org = str(self.get_option('org'))
        self.repository_filter = str(self.get_option('repository_filter'))
        self.regex_filter = str(self.get_option('regex_filter'))
        self.archived = bool(self.get_option('show_archived_repos'))
        self.group_by_languages = bool(self.get_option('group_by_languages'))

        results = None

        if attempt_to_read_cache:
            self.logger.debug("Attempting to read cache")
            try:
                results = self._cache[cache_key]
                self.logger.debug(f'Results: {results}')
            except KeyError as e:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True
                self.logger.error(f'Exception while Updating cache: {e}')
        if not attempt_to_read_cache or cache_needs_update or not results:
            self.logger.debug("Not attempting to read cache")
            # parse the provided inventory source
            results = self.get_repositories()
            self.logger.debug(f'Results: {results}')
        if cache_needs_update:
            try:
                self._cache[cache_key] = results
                self.logger.debug(f'Cached Result as: {self._cache}')
            except Exception as e:
                self.logger.error(f'Exception on Cache Update: {e}')

        self.populate(results or [])

    def get_repositories(self):
        """Fetch repositories using GitHubRepositoryFetcher.

        Returns:
            List of repository data dictionaries
        """
        if self.fetcher is None:
            self.fetcher = GitHubRepositoryFetcher(self.access_token, self.logger)

        try:
            return self.fetcher.fetch_repositories(
                self.repository_filter,
                self.org,
                archived=self.archived,
                group_by_languages=self.group_by_languages
            )
        except Exception as e:
            self.logger.error(f'Error fetching repositories: {e}')
            print(f"Error: {e}")
            return None

    def populate(self, r):
        try:
            # add main group as inventory group
            group = "all"
            for project in r:

                groupnames = []
                topics = project.get('topics', [])
                team = next((topic for topic in topics if topic.startswith("team-")), None)
                if team is not None:
                    groupnames.append(team)
                else:
                    groupnames.append("unassigned")

                self.logger.debug(f'regex_filter: {self.regex_filter}')
                if self.regex_filter != "":
                    regex_groups = self.parse_groupnames(project, self.regex_filter)
                    if regex_groups:
                        for group in regex_groups:
                            groupnames.append(group)
                else:
                    if "unassigned" not in groupnames:
                        groupnames.append("unassigned")
                self.logger.debug(f'Name: {project["name"]}')
                if self.group_by_languages:
                    for key, value in (project.get('languages') or {}).items():
                        group = self.inventory.add_group(to_safe_group_name(f'{key.lower().replace(" ", "")}', force=True, silent=True))
                        hostname = self.inventory.add_host(str(project['name']), group)
                for groupentry in groupnames:
                    group = self.inventory.add_group(str(groupentry).replace("-", "_"))

                    hostname = self.inventory.add_host(str(project['name']), group)

                self.inventory.set_variable(hostname, 'ansible_host', 'localhost')
                self.inventory.set_variable(hostname, 'ansible_connection', 'local')
                for key, value in project.items():
                    self.inventory.set_variable(hostname, key, value)
                if team is not None:
                    self.inventory.set_variable(hostname, 'team', team)

        except Exception as e:
            self.logger.error(f'Exception: {e}')
            print(
                f"Error: {e}",
            )
            return
