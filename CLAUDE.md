# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **clash-verge-cli**, a command-line interface for controlling Clash Verge Rev (a Mihomo/Clash.Meta proxy client). The CLI is built with Python using the Click framework and packaged as a standalone binary using PyInstaller.

The CLI source code is located in `clash-verge-rev/agent-harness/` and is structured as a namespace package under `cli_anything.clash_verge_rev`.

## Project Structure

```
/home/dev/repos/clash-verge-cli/
├── clash-verge-rev/agent-harness/          # Main source directory
│   ├── cli_anything/clash_verge_rev/       # Python package
│   │   ├── clash_verge_rev_cli.py          # CLI entry point (~1000 lines)
│   │   ├── core/                           # Core business logic
│   │   │   ├── config.py                   # ConfigManager, VergeConfig, ProfilesConfig
│   │   │   ├── runtime.py                  # RuntimeManager, ClashInfo
│   │   │   ├── service.py                  # ServiceManager (macOS/Linux privileged helper)
│   │   │   └── backup.py                   # BackupManager
│   │   ├── utils/                          # Utilities
│   │   │   ├── output.py                   # OutputFormatter (JSON/human output)
│   │   │   └── validators.py               # Input validation functions
│   │   └── tests/                          # Unit tests
│   ├── setup.py                            # Package setup with console_scripts entry points
│   ├── clash-verge-cli.spec                # PyInstaller spec for binary build
│   └── build.sh                            # Build script for standalone binary
└── clash-verge-cli                         # Built binary (output to project root)
```

## Common Commands

### Development Setup

```bash
cd clash-verge-rev/agent-harness
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running the CLI

```bash
# From source (development)
python -m cli_anything.clash_verge_rev.clash_verge_rev_cli

# Or after pip install
clash-verge-rev --help
```

### Testing

```bash
# Run all tests (use venv python - 'pytest' is not on PATH)
venv/bin/python -m pytest cli_anything/clash_verge_rev/tests/ -v

# Run with coverage
venv/bin/python -m pytest --cov=cli_anything.clash_verge_rev

# Run specific test file
venv/bin/python -m pytest cli_anything/clash_verge_rev/tests/test_core.py

# Run specific test
venv/bin/python -m pytest cli_anything/clash_verge_rev/tests/test_core.py::TestConfigManager::test_read_write_verge_config

# Install pytest if missing from venv
venv/bin/pip install pytest pytest-cov
```

### Code Quality

```bash
# Format code
black cli_anything/clash_verge_rev/

# Type check
mypy cli_anything/clash_verge_rev/
```

### Building the Binary

```bash
cd clash-verge-rev/agent-harness
./build.sh
```

This creates the standalone binary at `/home/dev/repos/clash-verge-cli/clash-verge-cli`.

## Architecture

### CLI Command Structure

The CLI uses Click for command organization. Main command groups:

- `profile` - Profile management (list, use, import, create, delete)
- `core` - Core control (start, stop, status, validate, generate)
- `config` - Configuration management (get, set, unset)
- `proxy` - Proxy settings (enable/disable system proxy and TUN mode)
- `backup` - Backup operations (create, restore, list)
- `service` - Service management (macOS/Linux only)
- `dns` - DNS configuration

### Core Modules

**ConfigManager** (`core/config.py`)
- Manages all YAML configuration files
- Provides mtime-based caching for performance
- Platform-specific config directory detection
- Key files: `verge.yaml`, `profiles.yaml`, `config.yaml`, `dns_config.yaml`

**RuntimeManager** (`core/runtime.py`)
- Generates runtime configuration by merging profile + verge settings
- Merges port overrides from verge.yaml into the active profile
- Validates configuration before applying

**ServiceManager** (`core/service.py`)
- Manages the `clash-verge-service` privileged helper
- Only available on macOS/Linux (uses launchd/systemd)
- Required for system proxy and TUN mode operations

**BackupManager** (`core/backup.py`)
- Creates timestamped ZIP backups of all config files
- Backup location: `{config_dir}/clash-verge-rev-backup/`

### Output Formatting

All commands support `--json` flag for machine-readable output. The `OutputFormatter` class handles both JSON and human-readable formats with optional terminal colors.

### Configuration Directories

The CLI reads/writes to the same directories as the GUI:

- **Windows**: `%LOCALAPPDATA%/io.github.clash-verge-rev.clash-verge-rev/`
- **macOS**: `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/`
- **Linux**: `~/.local/share/io.github.clash-verge-rev.clash-verge-rev/`

Override with `--config-dir` flag.

## Entry Points

The package defines two console scripts in `setup.py`:
- `clash-verge-rev` (primary)
- `cli-anything-clash-verge-rev` (alternate)

Both invoke `cli_anything.clash_verge_rev.clash_verge_rev_cli:main`.

## Testing Notes

- Tests use `tempfile.TemporaryDirectory` for isolation
- No external dependencies required for unit tests
- E2E tests may require actual Clash Verge Rev installation
