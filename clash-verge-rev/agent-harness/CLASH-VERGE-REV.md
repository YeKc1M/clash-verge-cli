# Clash Verge Rev - Software Operating Procedures

## Overview

**Clash Verge Rev** is a modern GUI proxy client built on Tauri (Rust backend + web frontend) that provides a user-friendly interface to the Clash core (Clash.Meta/Mihomo).

This document serves as the SOP for understanding and operating the CLI harness for Clash Verge Rev.

## Architecture

### Core Components

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
```

### Configuration Files

| File | Path | Purpose |
|------|------|---------|
| `verge.yaml` | `{config_dir}/verge.yaml` | App settings (theme, proxy, ports) |
| `profiles.yaml` | `{config_dir}/profiles.yaml` | Profile list and current selection |
| `config.yaml` | `{config_dir}/config.yaml` | Generated Clash core config |
| `dns_config.yaml` | `{config_dir}/dns_config.yaml` | Optional DNS settings |
| Profile files | `{config_dir}/profiles/*.yaml` | Individual proxy profiles |

### Configuration Directories

- **Windows**: `%LOCALAPPDATA%/io.github.clash-verge-rev.clash-verge-rev/`
- **macOS**: `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/`
- **Linux**: `~/.local/share/io.github.clash-verge-rev.clash-verge-rev/`

## Key Concepts

### Profiles

A **profile** is a YAML configuration file containing:
- `proxies`: List of proxy servers
- `proxy-groups`: Group definitions (select, url-test, fallback, etc.)
- `rules`: Traffic routing rules

Profile lifecycle:
1. **Import**: Download from URL or create from file
2. **Select**: Set as current active profile
3. **Enhance**: Apply scripts/chains to modify config
4. **Generate**: Merge into runtime config for Clash core

### Runtime Configuration

The runtime config is the final merged configuration applied to the Clash core:

```
Runtime Config = Base Profile + Chain Scripts + Verge Overrides + DNS Settings
```

Key overrides from verge.yaml:
- Port settings (`mixed-port`, `socks-port`, etc.)
- TUN mode enable/disable
- DNS configuration injection

### Service (macOS/Linux)

The `clash-verge-service` is a privileged helper for:
- Setting system proxy
- Managing TUN interface
- Other root-required operations

## CLI Command Mapping

| GUI Action | CLI Equivalent |
|------------|----------------|
| Import profile from URL | `profile import --url <url>` |
| Switch profile | `profile use <uid>` |
| Enable system proxy | `config set enable_system_proxy true` |
| Enable TUN mode | `config set enable_tun_mode true` |
| Start core | Core starts automatically with GUI |
| Backup configs | `backup create` |
| Restore backup | `backup restore <file>` |

## State Model

### Configuration State

```python
# verge.yaml - Application settings
verge = {
    "enable_system_proxy": bool,
    "enable_tun_mode": bool,
    "mixed_port": int,
    # ... more settings
}

# profiles.yaml - Profile management
profiles = {
    "current": "uid-of-active-profile",
    "items": [
        {"uid": "...", "name": "...", "file": "...", "url": "..."}
    ],
    "chain": ["uid1", "uid2"],  # Enhancement chain
    "valid": ["uid1"]  # Valid profiles
}

# config.yaml - Generated Clash config (read-only via CLI)
```

### Proxy Modes

| Mode | Description | Configuration |
|------|-------------|---------------|
| System Proxy | HTTP/HTTPS proxy via system settings | `enable_system_proxy: true` |
| TUN Mode | Virtual network interface for all traffic | `enable_tun_mode: true` |
| PAC | Proxy Auto-Config script | `proxy_auto_config: true` |
| Mixed Port | HTTP + SOCKS on same port | `mixed_port: 7890` |

## Common Operations

### Switching Profiles

```bash
# 1. List available profiles
cli-anything-clash-verge-rev profile list

# 2. Switch to profile
cli-anything-clash-verge-rev profile use <profile-uid>

# 3. Generate new runtime config (if needed)
cli-anything-clash-verge-rev core generate
```

### Enabling System Proxy

```bash
# Enable system proxy
cli-anything-clash-verge-rev config set enable_system_proxy true

# Configure proxy port
cli-anything-clash-verge-rev config set verge_mixed_port 7890

# Check status
cli-anything-clash-verge-rev proxy status
```

### Backup and Restore

```bash
# Create backup before major changes
cli-anything-clash-verge-rev backup create

# List available backups
cli-anything-clash-verge-rev backup list

# Restore (current config auto-backed up)
cli-anything-clash-verge-rev backup restore clash-verge-rev-backup-20240115_120000.zip
```

### Importing from Subscription URL

```bash
# Import with auto-update every 60 minutes
cli-anything-clash-verge-rev profile import \
    --url "https://example.com/subscription.yaml" \
    --name "My Subscription" \
    --interval 60
```

## Error Handling

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Profile not found | Wrong UID | Use `profile list` to get correct UID |
| Invalid YAML | Syntax error in profile | Validate with `core validate` |
| Port in use | Another service using port | Change port in config |
| Service not available | Windows or not installed | Not needed on Windows |

### Validation

Always validate after changes:

```bash
# Validate runtime config
cli-anything-clash-verge-rev core validate

# Run full diagnostics
cli-anything-clash-verge-rev doctor
```

## Scripting Examples

### Automated Profile Switching

```bash
#!/bin/bash
# switch-to-fastest.sh

# Get all profiles, find one with 'fast' in name
PROFILE_UID=$(cli-anything-clash-verge-rev --json profile list | \
    jq -r '.data.profiles[] | select(.name | contains("fast")) | .uid' | head -1)

if [ -n "$PROFILE_UID" ]; then
    cli-anything-clash-verge-rev profile use "$PROFILE_UID"
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
cli-anything-clash-verge-rev backup create

# Update profile
cli-anything-clash-verge-rev profile update "$PROFILE_UID"

# Validate
if ! cli-anything-clash-verge-rev core validate; then
    echo "Validation failed, restoring backup..."
    LATEST=$(cli-anything-clash-verge-rev --json backup list | jq -r '.data.backups[0].filename')
    cli-anything-clash-verge-rev backup restore "$LATEST" --force
    exit 1
fi
```

## Security Considerations

1. **Profile URLs**: Subscription URLs often contain authentication tokens. Treat them as secrets.
2. **Service Installation**: Installing the service requires root/admin privileges.
3. **TUN Mode**: Grants the application network-level access.
4. **Config Files**: Contain proxy credentials. Secure backup files appropriately.

## References

- [Clash Verge Rev Repository](https://github.com/clash-verge-rev/clash-verge-rev)
- [Clash.Meta Documentation](https://wiki.metacubex.one/)
- [Clash Documentation](https://dreamacro.github.io/clash/)
