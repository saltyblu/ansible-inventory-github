# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Volker Schmitz (saltyblu)
    name: github--repository-inventory
    short_description: GitHub repositories as inventory source
    version_added: 0.0.0
    description:
        - Get repositories from the GitHub API and store them as hosts.
        - The primary IP addresses contains the Git Repository clone url.
    options:
      url:
        description: GitHub URL.
        default: 'https://github.com/'
        env:
            - name: GITHUB_URL
      access_token:
        description: GitHub authentication PAT.
        required: true
        env:
            - name: GITHUB_ACCESS_TOKEN
            - type: str
      org:
        description: GitHub organization.
        required: true
        env:
            - name: GITHUB_ORG
            - type: str
      cache:
        description: The Cache option
        required: false
'''

EXAMPLES = '''
# github-inventory.yml
access_token: secure
org: saltyblu
repository_filter: *-deployment
'''

from github import Github
#from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, to_safe_group_name

class InventoryModule(BaseInventoryPlugin, Cacheable):
    ''' Host inventory parser for ansible using cobbler as source. '''

    NAME = 'github_repositories'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.cache_key = None
        self.connection = None

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('github_repositories.yaml', 'github_repositories.yml')):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending with "github-inventory.yaml/.yml"')
        return valid

    #def _init_cache(self):
    #    if self.cache_key not in self._cache:
    #        self._cache[self.cache_key] = {}

    #def _reload_cache(self):
    #    if self.get_option('cache_fallback'):
    #        self.display.vvv('Cannot connect to server, loading cache\n')
    #        self._options['cache_timeout'] = 0
    #        self.load_cache_plugin()
    #        self._cache.get(self.cache_key, {})

    def parse(self, inventory, loader, path, cache=True):

        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # get connection host
        self.github_url = str(self.get_option('url'))
        self.access_token = str(self.get_option('access_token'))
        self.org = str(self.get_option('org'))
        #self.repository_filter = str(self.get_option('repository_filter'))
        #self.cache_key = self.get_cache_key(path)
        #self.use_cache = cache and self.get_option('cache')

        g = Github(self.access_token)
        try:
            r = g.search_repositories(self.repository_filter, owner=self.org)
            # add main group as inventory group
            for project in r:
                self.inventory.add_host(project.ssh_url_to_repo, safe_subgroup)
                # add basic vars to host
                self.inventory.set_variable(project.ssh_url_to_repo, 'ansible_host', 'localhost')

                # add all infos of gitlab api to host as vars
                #for attr, value in project.__dict__.items():
                #    self.inventory.set_variable(project.ssh_url_to_repo, attr, value)
        except Exception as e:
            print(
                f"Error: {e}",
            )
            return
