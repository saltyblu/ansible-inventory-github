# Ansible Inventory Plugin: GitHub Repositories

A dynamic Ansible inventory plugin that retrieves GitHub repositories and creates an inventory based on repository metadata. This plugin allows you to manage and organize your GitHub repositories as Ansible hosts, making it easy to automate operations across multiple repositories.

## Features

- 🔍 **Dynamic Repository Discovery**: Automatically discovers repositories from a GitHub organization
- 🏷️ **Flexible Grouping**: Group repositories by:
  - Team assignments (via repository topics)
  - Programming languages
  - Custom regex patterns
  - Repository metadata
- 🚀 **Caching Support**: Built-in caching to improve performance and reduce API calls
- 🔐 **Secure Authentication**: Uses GitHub Personal Access Tokens for authentication
- 📝 **Rich Metadata**: Exposes all repository metadata as Ansible variables
- 🔧 **Configurable Filtering**: Filter repositories using search patterns and regex

## Installation

### Prerequisites

- Ansible >= 2.15.4
- Python >= 3.8
- PyGithub library

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install as Ansible Collection

```bash
ansible-galaxy collection install saltyblu.github
```

## Configuration

### 1. Create Inventory Configuration File

Create a YAML file (e.g., `github_repositories.yml`) with your configuration:

```yaml
---
plugin: github_repositories_inventory
url: "https://github.com"
access_token: "your_github_pat_token"
org: "your-organization"
repository_filter: "*-deployment"  # Optional: filter repositories
regex_filter: "^project-(\w+)"     # Optional: group by regex pattern
cache: true                        # Optional: enable caching
group_by_languages: true          # Optional: group by programming languages
show_archived_repos: false        # Optional: include archived repositories
```

### 2. Configuration Options

| Option | Description | Required | Default | Environment Variable |
|--------|-------------|----------|---------|---------------------|
| `url` | GitHub URL | No | `https://github.com/` | `GITHUB_INVENTORY_URL` |
| `access_token` | GitHub Personal Access Token | Yes | - | `GITHUB_INVENTORY_ACCESS_TOKEN` |
| `org` | GitHub organization name | Yes | - | `GITHUB_INVENTORY_ORG` |
| `repository_filter` | Repository search filter | No | `""` | `GITHUB_INVENTORY_SEARCH_FILTER` |
| `regex_filter` | Regex pattern for grouping | No | `""` | `GITHUB_INVENTORY_REGEX_GROUP_FILTER` |
| `cache` | Enable inventory caching | No | `false` | - |
| `group_by_languages` | Group by programming languages | No | `false` | `GITHUB_INVENTORY_GROUP_BY_LANGUAGES` |
| `show_archived_repos` | Include archived repositories | No | `false` | `GITHUB_INVENTORY_ARCHIVED` |

### 3. GitHub Personal Access Token

Create a GitHub Personal Access Token with the following permissions:
- `repo` (if working with private repositories)
- `public_repo` (for public repositories)

## Usage

### Basic Usage

```bash
# Test the inventory
ansible-inventory -i github_repositories.yml --list

# Use with ansible-playbook
ansible-playbook -i github_repositories.yml your-playbook.yml
```

### Example Inventory Output

```json
{
  "_meta": {
    "hostvars": {
      "my-awesome-repo": {
        "ansible_host": "localhost",
        "ansible_connection": "local",
        "name": "my-awesome-repo",
        "full_name": "myorg/my-awesome-repo",
        "clone_url": "https://github.com/myorg/my-awesome-repo.git",
        "ssh_url": "git@github.com:myorg/my-awesome-repo.git",
        "topics": ["team-backend", "python", "api"],
        "team": "team-backend",
        "default_branch": "main",
        "languages": {"Python": 95.2, "Dockerfile": 4.8}
      }
    }
  },
  "all": {
    "children": ["team_backend", "python", "unassigned"]
  },
  "team_backend": {
    "hosts": ["my-awesome-repo"]
  },
  "python": {
    "hosts": ["my-awesome-repo"]
  }
}
```

## Grouping Strategies

### 1. Team-based Grouping

Repositories are automatically grouped by team if they have topics starting with `team-`:

```yaml
# Repository topics: ["team-backend", "python", "api"]
# Result: Repository assigned to group "team_backend"
```

### 2. Language-based Grouping

Enable `group_by_languages: true` to group repositories by their primary programming languages:

```yaml
group_by_languages: true
# Result: Groups like "python", "javascript", "go", etc.
```

### 3. Regex-based Grouping

Use regex patterns to create custom groups:

```yaml
regex_filter: "^(project|service)-(\w+)"
# Repository: "project-auth-service"
# Result: Groups "main-project", "project", "auth"
```

## Advanced Examples

### Filter Deployment Repositories

```yaml
---
plugin: github_repositories_inventory
access_token: "{{ github_token }}"
org: "myorg"
repository_filter: "*-deployment OR *-infra"
cache: true
```

### Group by Project and Environment

```yaml
---
plugin: github_repositories_inventory
access_token: "{{ github_token }}"
org: "myorg"
regex_filter: "^(\w+)-(dev|staging|prod)$"
group_by_languages: false
cache: true
```

### Include All Repository Types

```yaml
---
plugin: github_repositories_inventory
access_token: "{{ github_token }}"
org: "myorg"
show_archived_repos: true
group_by_languages: true
cache: true
```

## Caching

The plugin supports caching to improve performance:

```yaml
cache: true
```

Cache files are stored in the default Ansible cache directory. To force cache refresh:

```bash
ansible-inventory -i github_repositories.yml --list --flush-cache
```

## Environment Variables

You can use environment variables instead of hardcoding values:

```bash
export GITHUB_INVENTORY_ACCESS_TOKEN="your_token"
export GITHUB_INVENTORY_ORG="your-org"
export GITHUB_INVENTORY_GROUP_BY_LANGUAGES="true"

ansible-inventory -i github_repositories.yml --list
```

## Troubleshooting

### Enable Debug Logging

The plugin logs to `dynamic_inventory.log` in the current directory. To see debug information, check this file or increase Ansible verbosity:

```bash
ansible-inventory -i github_repositories.yml --list -vvv
```

### Common Issues

1. **Authentication Errors**: Verify your GitHub token has the correct permissions
2. **No Repositories Found**: Check your organization name and repository filter
3. **Rate Limiting**: Enable caching to reduce API calls
4. **Empty Groups**: Ensure your regex patterns are correct

## Sample Inventory Configuration

See the complete example in [`inventory.sample/my.github_repositories.yml`](inventory.sample/my.github_repositories.yml).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the GPL-3.0-or-later license. See the source code for full license text.

## Authors

- Volker Schmitz (saltyblu)
- Martin Soentgenrath (merin80)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
