# CLI Anything - Clash Verge Rev

A complete CLI harness for the [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) proxy client.

This CLI provides comprehensive control over Clash Verge Rev without requiring the GUI, making it suitable for automation, scripting, and server deployments.

## Features

- **Profile Management**: Import, create, update, delete, and switch between proxy profiles
- **Core Control**: Start, stop, restart, and configure the Clash core
- **Proxy Settings**: Enable/disable system proxy and TUN mode
- **Configuration**: View and modify all verge.yaml settings
- **Backups**: Create, restore, and manage configuration backups
- **Service Management**: Install/uninstall clash-verge-service (macOS/Linux)
- **DNS Configuration**: Manage DNS settings separately
- **Validation**: Validate configuration files for syntax errors
- **JSON Output**: Machine-readable output for automation (`--json` flag)

## Installation

### From PyPI (recommended)

```bash
pip install cli-anything-clash-verge-rev
```

### From Source

```bash
cd clash-verge-rev/agent-harness
pip install -e .
```

## Usage

### Quick Start

```bash
# List all profiles
cli-anything-clash-verge-rev profile list

# Show current profile
cli-anything-clash-verge-rev profile current

# Switch to a profile
cli-anything-clash-verge-rev profile use <profile-uid>

# Enable system proxy
cli-anything-clash-verge-rev proxy enable

# Enable TUN mode
cli-anything-clash-verge-rev proxy tun-enable
```

### Profile Commands

```bash
# List profiles
cli-anything-clash-verge-rev profile list

# Show current profile
cli-anything-clash-verge-rev profile current

# Switch to a profile
cli-anything-clash-verge-rev profile use <uid>

# Import from URL
cli-anything-clash-verge-rev profile import --url https://example.com/config.yaml --name "My Profile"

# Create new profile
cli-anything-clash-verge-rev profile create "My Profile"

# Delete profile
cli-anything-clash-verge-rev profile delete <uid>

# Show profile content
cli-anything-clash-verge-rev profile show <uid>

# Update profile from URL
cli-anything-clash-verge-rev profile update <uid>
```

### Core Commands

```bash
# Get core connection info
cli-anything-clash-verge-rev core info

# Show runtime config
cli-anything-clash-verge-rev core config

# Show raw YAML
cli-anything-clash-verge-rev core config --yaml

# Validate config
cli-anything-clash-verge-rev core validate

# Generate config file
cli-anything-clash-verge-rev core generate
```

### Configuration Commands

```bash
# Get all config
cli-anything-clash-verge-rev config get

# Get specific value
cli-anything-clash-verge-rev config get enable_system_proxy

# Set a value
cli-anything-clash-verge-rev config set enable_system_proxy true
cli-anything-clash-verge-rev config set mixed_port 7890

# Unset a value
cli-anything-clash-verge-rev config unset enable_auto_launch

# Show config paths
cli-anything-clash-verge-rev config path
```

### Proxy Commands

```bash
# Show proxy status
cli-anything-clash-verge-rev proxy status

# Enable/disable system proxy
cli-anything-clash-verge-rev proxy enable
cli-anything-clash-verge-rev proxy disable

# Enable/disable TUN mode
cli-anything-clash-verge-rev proxy tun-enable
cli-anything-clash-verge-rev proxy tun-disable
```

### Backup Commands

```bash
# List backups
cli-anything-clash-verge-rev backup list

# Create backup
cli-anything-clash-verge-rev backup create

# Restore backup
cli-anything-clash-verge-rev backup restore <filename>

# Delete backup
cli-anything-clash-verge-rev backup delete <filename>

# Export backup
cli-anything-clash-verge-rev backup export <filename> /path/to/destination.zip

# Import backup
cli-anything-clash-verge-rev backup import /path/to/source.zip

# Clean up old backups
cli-anything-clash-verge-rev backup cleanup --keep 5
```

### Service Commands (macOS/Linux)

```bash
# Check service status
cli-anything-clash-verge-rev service status

# Install service
cli-anything-clash-verge-rev service install

# Uninstall service
cli-anything-clash-verge-rev service uninstall
```

### DNS Commands

```bash
# Get DNS config
cli-anything-clash-verge-rev dns get

# Set DNS config from YAML string
cli-anything-clash-verge-rev dns set "enable: true\nnameserver:\n  - 8.8.8.8"

# Set DNS config from file
cli-anything-clash-verge-rev dns set "$(cat dns.yaml)"

# Enable/disable DNS settings
cli-anything-clash-verge-rev dns enable
cli-anything-clash-verge-rev dns disable
```

### Utility Commands

```bash
# Show version
cli-anything-clash-verge-rev version

# Run diagnostics
cli-anything-clash-verge-rev doctor
```

## JSON Output

All commands support JSON output for scripting and automation:

```bash
cli-anything-clash-verge-rev --json profile list
cli-anything-clash-verge-rev --json core info
cli-anything-clash-verge-rev --json config get
```

Output format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional status message"
}
```

## Configuration Directory

The CLI uses the same configuration directory as the GUI:

- **Windows**: `%LOCALAPPDATA%/io.github.clash-verge-rev.clash-verge-rev/`
- **macOS**: `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/`
- **Linux**: `~/.local/share/io.github.clash-verge-rev.clash-verge-rev/`

Use `--config-dir` to override:

```bash
cli-anything-clash-verge-rev --config-dir /custom/path profile list
```

## Environment Variables

- `CLI_ANYTHING_FORCE_INSTALLED=1`: Force subprocess tests to use installed CLI

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=cli_anything.clash_verge_rev

# Format code
black cli_anything/clash_verge_rev/

# Type check
mypy cli_anything/clash_verge_rev/
```

## License

MIT License - same as Clash Verge Rev.

## See Also

- [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) - The GUI application
- [Clash.Meta](https://github.com/MetaCubeX/Clash.Meta) - The Clash core
