# Changelog

## Unreleased]

### Changed

- Function get_inventory is now get_repositories and return an array containing _rawData for each found repository

### Added

- Logging
- Caching Parameters to ansible.cfg

### Fixed

- search_repositories returned duplicates, this was fixed by adding `sort="updated"`

### Removed

- outdated, commented code
