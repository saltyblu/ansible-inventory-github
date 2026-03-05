# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Pytest configuration for ansible-inventory-github tests.
"""

import sys
import os
import types
from unittest.mock import MagicMock

# Add the project root to the path so we can import the inventory plugin
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Mock Ansible modules if not available
try:
    from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable  # noqa: F401
    from ansible.inventory.group import to_safe_group_name  # noqa: F401
except ModuleNotFoundError:
    ansible_module = types.ModuleType('ansible')
    ansible_plugins_module = types.ModuleType('ansible.plugins')
    ansible_plugins_inventory_module = types.ModuleType('ansible.plugins.inventory')
    ansible_inventory_module = types.ModuleType('ansible.inventory')
    ansible_inventory_group_module = types.ModuleType('ansible.inventory.group')

    class BaseInventoryPlugin:
        pass

    class Cacheable:
        pass

    def to_safe_group_name(name, force=False, silent=False):
        return name

    ansible_plugins_inventory_module.BaseInventoryPlugin = BaseInventoryPlugin
    ansible_plugins_inventory_module.Cacheable = Cacheable
    ansible_inventory_group_module.to_safe_group_name = to_safe_group_name

    sys.modules['ansible'] = ansible_module
    sys.modules['ansible.plugins'] = ansible_plugins_module
    sys.modules['ansible.plugins.inventory'] = ansible_plugins_inventory_module
    sys.modules['ansible.inventory'] = ansible_inventory_module
    sys.modules['ansible.inventory.group'] = ansible_inventory_group_module

# Mock github module only if PyGithub is not installed
try:
    from github import Github  # noqa: F401
except ModuleNotFoundError:
    github_module = MagicMock()
    github_module.Github = MagicMock()
    sys.modules['github'] = github_module
