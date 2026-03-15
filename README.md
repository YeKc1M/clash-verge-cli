# Clash Verge Rev CLI

A complete command-line interface for [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) proxy client, built with [CLI-Anything](https://github.com/HKUDS/CLI-Anything).

This CLI provides comprehensive control over Clash Verge Rev without requiring the GUI, making it suitable for automation, scripting, and server deployments.

## Features

- **Profile Management** - Import, create, update, delete, and switch between proxy profiles
- **Core Control** - Start, stop, restart, and configure the Clash core
- **Proxy Settings** - Enable/disable system proxy and TUN mode
- **Configuration** - View and modify all verge.yaml settings
- **Backups** - Create, restore, and manage configuration backups
- **Service Management** - Install/uninstall clash-verge-service (macOS/Linux)
- **DNS Configuration** - Manage DNS settings separately
- **Validation** - Validate configuration files for syntax errors
- **JSON Output** - Machine-readable output for automation (`--json` flag)

## Requirements

- **Mihomo (Clash.Meta)** - The Clash core must be installed separately. The CLI controls the core but does not bundle it.
  - Install from: https://github.com/MetaCubeX/mihomo/releases

## Installation

### From PyPI (recommended)

```bash
pip install cli-anything-clash-verge-rev
```

### From Source

```bash
git clone https://github.com/clash-verge-rev/clash-verge-rev.git
cd clash-verge-rev/agent-harness
pip install -e .
```

## Quick Start

```bash
# List all profiles
clash-verge-rev profile list

# Show current profile
clash-verge-rev profile current

# Switch to a profile
clash-verge-rev profile use <profile-uid>

# Generate runtime config
clash-verge-rev core generate

# Start mihomo core
clash-verge-rev core start

# Check core status
clash-verge-rev core status

# Enable system proxy
clash-verge-rev proxy enable

# Enable TUN mode
clash-verge-rev proxy tun-enable

# Stop mihomo core
clash-verge-rev core stop
```

## Commands

### Profile Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev profile list` | List all profiles |
| `clash-verge-rev profile current` | Show current profile |
| `clash-verge-rev profile use <uid>` | Switch to a profile |
| `clash-verge-rev profile import --url <url>` | Import from URL |
| `clash-verge-rev profile create "Name"` | Create new profile |
| `clash-verge-rev profile delete <uid>` | Delete profile |
| `clash-verge-rev profile show <uid>` | Show profile content |
| `clash-verge-rev profile update <uid>` | Update from URL |

### Core Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev core info` | Get core connection info |
| `clash-verge-rev core config` | Show runtime config |
| `clash-verge-rev core validate` | Validate config |
| `clash-verge-rev core generate` | Generate config.yaml |
| `clash-verge-rev core start` | Start mihomo core |
| `clash-verge-rev core stop` | Stop mihomo core |
| `clash-verge-rev core status` | Check core status |

### Configuration Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev config get` | Get all config |
| `clash-verge-rev config get <key>` | Get specific value |
| `clash-verge-rev config set <key> <value>` | Set a value |
| `clash-verge-rev config unset <key>` | Unset a value |
| `clash-verge-rev config path` | Show config paths |

### Proxy Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev proxy status` | Show proxy status |
| `clash-verge-rev proxy enable` | Enable system proxy |
| `clash-verge-rev proxy disable` | Disable system proxy |
| `clash-verge-rev proxy tun-enable` | Enable TUN mode |
| `clash-verge-rev proxy tun-disable` | Disable TUN mode |

### Backup Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev backup list` | List backups |
| `clash-verge-rev backup create` | Create backup |
| `clash-verge-rev backup restore <file>` | Restore backup |
| `clash-verge-rev backup delete <file>` | Delete backup |
| `clash-verge-rev backup export <file> <dest>` | Export backup |
| `clash-verge-rev backup import <source>` | Import backup |
| `clash-verge-rev backup cleanup --keep 5` | Clean old backups |

### Service Commands (macOS/Linux)

| Command | Description |
|---------|-------------|
| `clash-verge-rev service status` | Check service status |
| `clash-verge-rev service install` | Install service |
| `clash-verge-rev service uninstall` | Uninstall service |

### DNS Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev dns get` | Get DNS config |
| `clash-verge-rev dns set "<yaml>"` | Set DNS config |
| `clash-verge-rev dns enable` | Enable DNS settings |
| `clash-verge-rev dns disable` | Disable DNS settings |

### Utility Commands

| Command | Description |
|---------|-------------|
| `clash-verge-rev version` | Show version |
| `clash-verge-rev doctor` | Run diagnostics |

## JSON Output

All commands support JSON output for scripting:

```bash
clash-verge-rev --json profile list
clash-verge-rev --json core info
clash-verge-rev --json config get
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
clash-verge-rev --config-dir /custom/path profile list
```

## Scripting Examples

### Automated Profile Switching

```bash
#!/bin/bash
# switch-to-fastest.sh

PROFILE_UID=$(clash-verge-rev --json profile list | \
    jq -r '.data.profiles[] | select(.name | contains("fast")) | .uid' | head -1)

if [ -n "$PROFILE_UID" ]; then
    clash-verge-rev profile use "$PROFILE_UID"
else
    echo "No fast profile found"
    exit 1
fi
```

### Backup Before Update

```bash
#!/bin/bash
# update-profile.sh

PROFILE_UID=$1

# Create backup
clash-verge-rev backup create

# Update profile
clash-verge-rev profile update "$PROFILE_UID"

# Validate
if ! clash-verge-rev core validate; then
    echo "Validation failed, restoring backup..."
    LATEST=$(clash-verge-rev --json backup list | jq -r '.data.backups[0].filename')
    clash-verge-rev backup restore "$LATEST" --force
    exit 1
fi
```

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

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Clash Verge Rev                         │
│  ┌─────────────────┐    ┌───────────────────────────────┐   │
│  │   Web Frontend   │◄──►│     Tauri Rust Backend        │   │
│  │  (React/TS)      │    │  - Command handlers           │   │
│  └─────────────────┘    │  - Config management          │   │
│                         │  - Core lifecycle             │   │
│                         └───────────────┬───────────────┘   │
│                                         │                   │
│                         ┌───────────────▼───────────────┐   │
│                         │      Clash Core               │   │
│                         │   (Clash.Meta/Mihomo)         │   │
│                         └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    CLI Anything Harness                     │
│  - Profile management      - Backup/restore                 │
│  - Config control          - Service management             │
│  - Proxy settings          - DNS configuration              │
└─────────────────────────────────────────────────────────────┘
```

## See Also

- [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev) - The GUI application
- [CLI-Anything](https://github.com/HKUDS/CLI-Anything) - Framework for building CLIs
- [Clash.Meta](https://github.com/MetaCubeX/Clash.Meta) - The Clash core
