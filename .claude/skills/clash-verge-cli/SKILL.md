---
name: clash-verge-cli
description: How to use the clash-verge-cli binary to control Clash Verge Rev (a Mihomo/Clash.Meta proxy client) from the command line. Use this skill whenever the user asks about managing proxy profiles, starting/stopping the clash core, enabling/disabling system proxy or TUN mode, editing verge.yaml config, managing backups, or scripting/automating any clash-verge-rev operation. Trigger even if the user just says "switch profile", "start clash", "enable proxy", "backup config", or other informal variants — this skill covers all of it.
---

# clash-verge-cli Usage

The `clash-verge-cli` binary provides full control over Clash Verge Rev without needing the GUI. It reads and writes the same config files the GUI uses, so changes take effect immediately.

**Binary location:** `./clash-verge-cli` at the project root (built via `/build-binary` skill).

**Global flags** (go before the subcommand):
- `--json` — machine-readable JSON output (great for scripting)
- `--config-dir <path>` — override the default config directory

---

## Command Groups

### `profile` — Proxy Profile Management

```bash
clash-verge-cli profile list                          # list all profiles (uid, name, url, active)
clash-verge-cli profile current                       # show which profile is active
clash-verge-cli profile use <uid>                     # switch active profile
clash-verge-cli profile import --url <url>            # import subscription URL
clash-verge-cli profile import --url <url> --name "MyProxy" --interval 60
clash-verge-cli profile create "Name"                 # empty profile
clash-verge-cli profile create "Name" --from-file /path/to/config.yaml
clash-verge-cli profile show <uid>                    # print profile YAML
clash-verge-cli profile update <uid>                  # re-download from stored URL
clash-verge-cli profile delete <uid>                  # delete (prompts confirmation)
```

### `core` — Clash Core (Mihomo) Control

```bash
clash-verge-cli core info                             # ports, controller address, secret
clash-verge-cli core generate                         # merge profile + settings → config.yaml
clash-verge-cli core start                            # generate config then launch mihomo
clash-verge-cli core start --binary /usr/local/bin/mihomo  # specify binary explicitly
clash-verge-cli core stop                             # stop mihomo (SIGTERM → SIGKILL)
clash-verge-cli core status                           # is mihomo running? (PID if yes)
clash-verge-cli core config                           # show merged runtime config
clash-verge-cli core config --yaml                    # raw YAML instead of table
clash-verge-cli core validate                         # validate config.yaml (syntax + required fields)
```

`core start` auto-detects the mihomo binary from `$PATH` and common locations (`/usr/local/bin`, `~/.local/bin`, etc.).

### `proxy` — System Proxy & TUN Mode

```bash
clash-verge-cli proxy status                          # show proxy state, TUN state, ports
clash-verge-cli proxy enable                          # enable system proxy
clash-verge-cli proxy disable                         # disable system proxy
clash-verge-cli proxy tun-enable                      # enable TUN mode
clash-verge-cli proxy tun-disable                     # disable TUN mode
```

Note: proxy/TUN changes update `verge.yaml`; restart the core to apply.

### `config` — App Settings (verge.yaml)

```bash
clash-verge-cli config get                            # show all settings
clash-verge-cli config get <key>                      # get one setting
clash-verge-cli config set <key> <value>              # set a value (auto-casts type)
clash-verge-cli config unset <key>                    # set to null
clash-verge-cli config path                           # show all config file paths
```

Common config keys: `enable_system_proxy`, `enable_tun_mode`, `verge_mixed_port`, `verge_socks_port`, `enable_auto_launch`, `clash_core`, `language`, `theme_mode`.

### `backup` — Configuration Backups

```bash
clash-verge-cli backup list                           # list backups (newest first)
clash-verge-cli backup create                         # ZIP backup of all config files
clash-verge-cli backup restore <filename>             # restore (auto-creates pre-restore backup)
clash-verge-cli backup restore <filename> --force     # skip confirmation
clash-verge-cli backup delete <filename>              # delete backup (prompts)
clash-verge-cli backup export <filename> <dest>       # copy backup to external path
clash-verge-cli backup import <source>                # copy external ZIP into backup dir
clash-verge-cli backup cleanup --keep 5               # keep only N most recent
```

Backups are ZIPs stored in `{config_dir}/clash-verge-rev-backup/`.

### `service` — Privileged Service (macOS/Linux)

```bash
clash-verge-cli service status
clash-verge-cli service install
clash-verge-cli service uninstall
```

The service manages system proxy and TUN interface operations that require elevated privileges.

### `dns` — DNS Configuration

```bash
clash-verge-cli dns get                               # read dns_config.yaml
clash-verge-cli dns set "<yaml-string>"               # write DNS config
clash-verge-cli dns enable                            # set enable_dns_settings = true
clash-verge-cli dns disable                           # set enable_dns_settings = false
```

### Utility

```bash
clash-verge-cli version                               # show version + app ID
clash-verge-cli doctor                                # diagnostics (config dir, files, validity)
```

---

## Common Workflows

### Start the proxy from scratch
```bash
clash-verge-cli profile list                          # find the right profile UID
clash-verge-cli profile use <uid>
clash-verge-cli core generate                         # build config.yaml
clash-verge-cli core start
clash-verge-cli proxy enable
```

### Switch profile without restart
```bash
clash-verge-cli profile use <uid>
clash-verge-cli core generate
# restart core if needed: clash-verge-cli core stop && clash-verge-cli core start
```

### Safe profile update (backup first)
```bash
clash-verge-cli backup create
clash-verge-cli profile update <uid>
clash-verge-cli core validate || clash-verge-cli backup restore "$(clash-verge-cli --json backup list | jq -r '.data.backups[0].filename')" --force
```

### Import a subscription
```bash
clash-verge-cli profile import --url "https://example.com/sub.yaml" --name "Work VPN" --interval 1440
clash-verge-cli profile use <new-uid>
clash-verge-cli core generate && clash-verge-cli core start
```

---

## JSON Output & Scripting

All commands support `--json` for machine-readable output:

```bash
clash-verge-cli --json profile list
# { "success": true, "data": { "profiles": [...] } }

# Find and switch to a profile by name
UID=$(clash-verge-cli --json profile list | jq -r '.data.profiles[] | select(.name | test("fast")) | .uid' | head -1)
clash-verge-cli profile use "$UID"

# Check if core is running
STATUS=$(clash-verge-cli --json core status | jq -r '.data.status')
[ "$STATUS" = "running" ] || clash-verge-cli core start
```

---

## Config Directory

| Platform | Path |
|----------|------|
| Linux    | `~/.local/share/io.github.clash-verge-rev.clash-verge-rev/` |
| macOS    | `~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/` |
| Windows  | `%LOCALAPPDATA%/io.github.clash-verge-rev.clash-verge-rev/` |

Override with `--config-dir`:
```bash
clash-verge-cli --config-dir /custom/path profile list
```

Key files: `verge.yaml` (settings), `profiles.yaml` (profile list), `config.yaml` (generated core config), `dns_config.yaml`, `profiles/*.yaml` (profile files).
