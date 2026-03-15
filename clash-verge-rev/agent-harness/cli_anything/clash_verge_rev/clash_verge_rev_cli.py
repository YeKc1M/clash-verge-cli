#!/usr/bin/env python3
"""
CLI Anything - Clash Verge Rev

A complete CLI harness for the Clash Verge Rev proxy client.

This CLI provides comprehensive control over Clash Verge Rev without requiring
the GUI, making it suitable for automation, scripting, and server deployments.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from cli_anything.clash_verge_rev.core import (
    BackupManager,
    ConfigManager,
    RuntimeManager,
    ServiceManager,
    VergeConfig,
    ProfilesConfig,
    PrfItem,
)
from cli_anything.clash_verge_rev.utils import OutputFormatter, validate_url, validate_yaml_content


# Global state for JSON output mode
pass_config = click.make_pass_decorator(ConfigManager, ensure=True)


def get_formatter(json_mode: bool) -> OutputFormatter:
    """Get output formatter."""
    return OutputFormatter(use_json=json_mode)


@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.option("--config-dir", type=click.Path(), help="Override config directory")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool, config_dir: Optional[str]) -> None:
    """
    Clash Verge Rev CLI - Complete control without the GUI.

    Manage proxy profiles, control the Clash core, configure system proxy,
    handle backups, and more - all from the command line.

    Examples:
        clash-verge-rev --json profile list
        clash-verge-rev core start
        clash-verge-rev config set enable_system_proxy true
    """
    # Ensure context object exists
    if ctx.obj is None:
        ctx.obj = {}

    # Store JSON mode in context
    ctx.obj["json_mode"] = json_mode

    # Initialize config manager
    config_path = Path(config_dir) if config_dir else None
    ctx.obj["config"] = ConfigManager(config_path)

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# =============================================================================
# Profile Commands
# =============================================================================

@cli.group("profile")
def profile_cmd():
    """Manage proxy profiles."""
    pass


@profile_cmd.command("list")
@click.pass_context
def profile_list(ctx: click.Context) -> None:
    """List all profiles."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()
        items = []

        for item in profiles.items:
            item_dict = {
                "uid": item.uid,
                "name": item.name,
                "desc": item.desc or "",
                "file": item.file or "",
                "url": item.url or "",
                "is_current": item.uid == profiles.current,
                "updated": item.updated,
            }
            items.append(item_dict)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({"profiles": items}, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("current")
@click.pass_context
def profile_current(ctx: click.Context) -> None:
    """Show the currently active profile."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()
        current = profiles.get_current_profile()

        if current:
            data = {
                "uid": current.uid,
                "name": current.name,
                "desc": current.desc,
                "file": current.file,
                "url": current.url,
                "updated": current.updated,
            }
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(data, success=True, message=f"Current profile: {current.name}"))
        else:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=True, message="No profile currently selected"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("use")
@click.argument("profile_uid")
@click.pass_context
def profile_use(ctx: click.Context, profile_uid: str) -> None:
    """Switch to a profile by UID."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()

        # Verify profile exists
        profile = profiles.get_profile_by_uid(profile_uid)
        if not profile:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Profile not found: {profile_uid}"))
            sys.exit(1)

        # Update current profile
        profiles.current = profile_uid
        config.write_profiles(profiles)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({"uid": profile_uid, "name": profile.name}, success=True, message=f"Switched to profile: {profile.name}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("import")
@click.option("--url", required=True, help="URL to import profile from")
@click.option("--name", help="Custom name for the profile")
@click.option("--interval", type=int, help="Auto-update interval in minutes")
@click.pass_context
def profile_import(ctx: click.Context, url: str, name: Optional[str], interval: Optional[int]) -> None:
    """Import a profile from URL."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    # Validate URL
    valid, error = validate_url(url)
    if not valid:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=error))
        sys.exit(1)

    try:
        import urllib.request
        import uuid
        from datetime import datetime

        # Download profile content
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "clash-verge-rev/1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")

        # Validate YAML
        valid, error = validate_yaml_content(content)
        if not valid:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Invalid profile content: {error}"))
            sys.exit(1)

        # Parse to get name if not provided
        parsed = yaml.safe_load(content)
        profile_name = name or parsed.get("name") or f"Imported-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Generate unique ID and filename
        uid = str(uuid.uuid4())[:8]
        filename = f"{profile_name.replace(' ', '_')}_{uid}.yaml"

        # Save profile file
        config.write_profile_file(filename, content)

        # Create profile item
        profiles = config.read_profiles()
        new_item = PrfItem(
            uid=uid,
            name=profile_name,
            file=filename,
            url=url,
            updated=int(datetime.now().timestamp()),
            option={"update_interval": interval} if interval else None,
        )
        profiles.items.append(new_item)
        config.write_profiles(profiles)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(
            {"uid": uid, "name": profile_name, "file": filename},
            success=True,
            message=f"Imported profile: {profile_name}",
        ))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=f"Import failed: {e}"))
        sys.exit(1)


@profile_cmd.command("create")
@click.argument("name")
@click.option("--from-file", type=click.Path(exists=True), help="Create from YAML file")
@click.option("--from-content", help="Create from YAML content string")
@click.pass_context
def profile_create(ctx: click.Context, name: str, from_file: Optional[str], from_content: Optional[str]) -> None:
    """Create a new profile."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        import uuid
        from datetime import datetime

        # Get content
        content = ""
        if from_file:
            with open(from_file, "r") as f:
                content = f.read()
        elif from_content:
            content = from_content
        else:
            # Create minimal config
            content = f"""# {name}
name: "{name}"
proxies: []
proxy-groups: []
rules: []
"""

        # Validate YAML
        valid, error = validate_yaml_content(content)
        if not valid:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Invalid YAML: {error}"))
            sys.exit(1)

        # Generate unique ID and filename
        uid = str(uuid.uuid4())[:8]
        filename = f"{name.replace(' ', '_')}_{uid}.yaml"

        # Save profile file
        config.write_profile_file(filename, content)

        # Create profile item
        profiles = config.read_profiles()
        new_item = PrfItem(
            uid=uid,
            name=name,
            desc=f"Created profile",
            file=filename,
            updated=int(datetime.now().timestamp()),
        )
        profiles.items.append(new_item)
        config.write_profiles(profiles)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(
            {"uid": uid, "name": name, "file": filename},
            success=True,
            message=f"Created profile: {name}",
        ))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("delete")
@click.argument("profile_uid")
@click.confirmation_option(prompt="Are you sure you want to delete this profile?")
@click.pass_context
def profile_delete(ctx: click.Context, profile_uid: str) -> None:
    """Delete a profile."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()

        # Find profile
        profile = profiles.get_profile_by_uid(profile_uid)
        if not profile:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Profile not found: {profile_uid}"))
            sys.exit(1)

        # Remove from list
        profiles.items = [p for p in profiles.items if p.uid != profile_uid]

        # If this was current, clear current
        if profiles.current == profile_uid:
            profiles.current = profiles.items[0].uid if profiles.items else None

        config.write_profiles(profiles)

        # Delete file
        if profile.file:
            file_path = config.get_profile_file_path(profile.file)
            if file_path.exists():
                file_path.unlink()

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Deleted profile: {profile.name}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("show")
@click.argument("profile_uid")
@click.pass_context
def profile_show(ctx: click.Context, profile_uid: str) -> None:
    """Show profile content."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()
        profile = profiles.get_profile_by_uid(profile_uid)

        if not profile:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Profile not found: {profile_uid}"))
            sys.exit(1)

        if not profile.file:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message="Profile has no file"))
            sys.exit(1)

        content = config.read_profile_file(profile.file)

        if json_mode:
            # Parse and output as JSON
            parsed = yaml.safe_load(content)
            click.echo(json.dumps(parsed, indent=2))
        else:
            click.echo(content)

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@profile_cmd.command("update")
@click.argument("profile_uid")
@click.pass_context
def profile_update(ctx: click.Context, profile_uid: str) -> None:
    """Update a profile from its URL."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        profiles = config.read_profiles()
        profile = profiles.get_profile_by_uid(profile_uid)

        if not profile:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Profile not found: {profile_uid}"))
            sys.exit(1)

        if not profile.url:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message="Profile has no update URL"))
            sys.exit(1)

        import urllib.request
        from datetime import datetime

        req = urllib.request.Request(
            profile.url,
            headers={"User-Agent": "clash-verge-rev/1.0"},
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")

        # Validate YAML
        valid, error = validate_yaml_content(content)
        if not valid:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Invalid profile content: {error}"))
            sys.exit(1)

        # Update file
        config.write_profile_file(profile.file, content)

        # Update timestamp
        profile.updated = int(datetime.now().timestamp())
        config.write_profiles(profiles)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Updated profile: {profile.name}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Core Commands
# =============================================================================

@cli.group("core")
def core_cmd():
    """Control the Clash core."""
    pass


@core_cmd.command("info")
@click.pass_context
def core_info(ctx: click.Context) -> None:
    """Get Clash core connection info."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        runtime = RuntimeManager(config)
        info = runtime.get_clash_info()

        data = {
            "port": info.port,
            "socks_port": info.socks_port,
            "mixed_port": info.mixed_port,
            "redir_port": info.redir_port,
            "tproxy_port": info.tproxy_port,
            "external_controller": info.external_controller,
            "secret": info.secret,
        }

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(data, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@core_cmd.command("config")
@click.option("--yaml", "output_yaml", is_flag=True, help="Output raw YAML")
@click.pass_context
def core_config(ctx: click.Context, output_yaml: bool) -> None:
    """Show the runtime configuration."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        runtime = RuntimeManager(config)

        if output_yaml:
            content = runtime.get_runtime_yaml()
            click.echo(content)
        else:
            cfg = runtime.get_runtime_config()
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(cfg, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@core_cmd.command("validate")
@click.pass_context
def core_validate(ctx: click.Context) -> None:
    """Validate current runtime configuration."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        runtime = RuntimeManager(config)
        is_valid, message = runtime.validate_config()

        formatter = get_formatter(json_mode)
        data = {"valid": is_valid, "message": message}
        click.echo(formatter.output(data, success=is_valid, message=message if message else None))

        if not is_valid:
            sys.exit(1)

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@core_cmd.command("generate")
@click.pass_context
def core_generate(ctx: click.Context) -> None:
    """Generate and save runtime config to clash config.yaml."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        runtime = RuntimeManager(config)
        success = runtime.apply_generate_config()

        formatter = get_formatter(json_mode)
        if success:
            click.echo(formatter.output(None, success=True, message="Configuration generated successfully"))
        else:
            click.echo(formatter.output(None, success=False, message="Failed to generate configuration"))
            sys.exit(1)

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Config Commands
# =============================================================================

@cli.group("config")
def config_cmd():
    """Manage application configuration."""
    pass


@config_cmd.command("get")
@click.argument("key", required=False)
@click.pass_context
def config_get(ctx: click.Context, key: Optional[str]) -> None:
    """Get configuration value(s)."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()

        if key:
            value = getattr(verge, key, None)
            formatter = get_formatter(json_mode)
            click.echo(formatter.output({key: value}, success=True))
        else:
            # Show all non-None values
            data = verge.to_dict()
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(data, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()

        if not hasattr(verge, key):
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Unknown config key: {key}"))
            sys.exit(1)

        # Try to convert value to appropriate type
        current_value = getattr(verge, key)
        if isinstance(current_value, bool):
            parsed_value = value.lower() in ("true", "1", "yes", "on")
        elif isinstance(current_value, int):
            parsed_value = int(value)
        elif isinstance(current_value, float):
            parsed_value = float(value)
        else:
            parsed_value = value

        setattr(verge, key, parsed_value)
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({key: parsed_value}, success=True, message=f"Set {key} = {parsed_value}"))

    except ValueError as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=f"Invalid value: {e}"))
        sys.exit(1)
    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@config_cmd.command("unset")
@click.argument("key")
@click.pass_context
def config_unset(ctx: click.Context, key: str) -> None:
    """Unset a configuration value (set to null)."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()

        if not hasattr(verge, key):
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=f"Unknown config key: {key}"))
            sys.exit(1)

        setattr(verge, key, None)
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Unset {key}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@config_cmd.command("path")
@click.pass_context
def config_path(ctx: click.Context) -> None:
    """Show configuration directory path."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        data = {
            "config_dir": str(config.get_config_dir()),
            "profiles_dir": str(config.get_profiles_dir()),
            "logs_dir": str(config.get_logs_dir()),
            "backup_dir": str(config.get_backup_dir()),
            "verge_path": str(config.verge_path()),
            "profiles_path": str(config.profiles_path()),
            "clash_path": str(config.clash_path()),
        }

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(data, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Proxy Commands
# =============================================================================

@cli.group("proxy")
def proxy_cmd():
    """Manage system proxy settings."""
    pass


@proxy_cmd.command("status")
@click.pass_context
def proxy_status(ctx: click.Context) -> None:
    """Get current proxy status from config."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        runtime = RuntimeManager(config)
        info = runtime.get_clash_info()

        data = {
            "enable_system_proxy": verge.enable_system_proxy,
            "enable_tun_mode": verge.enable_tun_mode,
            "mixed_port": info.mixed_port,
            "socks_port": info.socks_port,
            "proxy_host": verge.proxy_host or "127.0.0.1",
            "proxy_auto_config": verge.proxy_auto_config,
            "enable_proxy_guard": verge.enable_proxy_guard,
            "proxy_guard_duration": verge.proxy_guard_duration,
        }

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(data, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@proxy_cmd.command("enable")
@click.pass_context
def proxy_enable(ctx: click.Context) -> None:
    """Enable system proxy."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_system_proxy = True
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="System proxy enabled (restart app to apply)"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@proxy_cmd.command("disable")
@click.pass_context
def proxy_disable(ctx: click.Context) -> None:
    """Disable system proxy."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_system_proxy = False
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="System proxy disabled (restart app to apply)"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@proxy_cmd.command("tun-enable")
@click.pass_context
def proxy_tun_enable(ctx: click.Context) -> None:
    """Enable TUN mode."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_tun_mode = True
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="TUN mode enabled (restart core to apply)"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@proxy_cmd.command("tun-disable")
@click.pass_context
def proxy_tun_disable(ctx: click.Context) -> None:
    """Disable TUN mode."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_tun_mode = False
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="TUN mode disabled (restart core to apply)"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Backup Commands
# =============================================================================

@cli.group("backup")
def backup_cmd():
    """Manage configuration backups."""
    pass


@backup_cmd.command("list")
@click.pass_context
def backup_list(ctx: click.Context) -> None:
    """List all backups."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        backups = backup_mgr.list_backups()

        data = [b.to_dict() for b in backups]

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({"backups": data}, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("create")
@click.pass_context
def backup_create(ctx: click.Context) -> None:
    """Create a new backup."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        backup = backup_mgr.create_backup()

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(backup.to_dict(), success=True, message=f"Created backup: {backup.filename}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("restore")
@click.argument("filename")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_context
def backup_restore(ctx: click.Context, filename: str, force: bool) -> None:
    """Restore from a backup."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)

        if not force:
            click.confirm(f"Restore from backup '{filename}'? Current config will be backed up first.", abort=True)

        backup_mgr.restore_backup(filename, force=True)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Restored from backup: {filename}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("delete")
@click.argument("filename")
@click.confirmation_option(prompt="Are you sure you want to delete this backup?")
@click.pass_context
def backup_delete(ctx: click.Context, filename: str) -> None:
    """Delete a backup."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        backup_mgr.delete_backup(filename)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Deleted backup: {filename}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("export")
@click.argument("filename")
@click.argument("destination", type=click.Path())
@click.pass_context
def backup_export(ctx: click.Context, filename: str, destination: str) -> None:
    """Export a backup to external location."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        backup_mgr.export_backup(filename, Path(destination))

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message=f"Exported backup to: {destination}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("import")
@click.argument("source", type=click.Path(exists=True))
@click.pass_context
def backup_import(ctx: click.Context, source: str) -> None:
    """Import a backup from external location."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        new_filename = backup_mgr.import_backup(Path(source))

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({"filename": new_filename}, success=True, message=f"Imported backup as: {new_filename}"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@backup_cmd.command("cleanup")
@click.option("--keep", default=10, help="Number of backups to keep")
@click.pass_context
def backup_cleanup(ctx: click.Context, keep: int) -> None:
    """Remove old backups, keeping only N most recent."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        backup_mgr = BackupManager(config)
        removed = backup_mgr.cleanup_old_backups(keep)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output({"removed": removed}, success=True, message=f"Removed {removed} old backups"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Service Commands
# =============================================================================

@cli.group("service")
def service_cmd():
    """Manage clash-verge-service (macOS/Linux only)."""
    pass


@service_cmd.command("status")
@click.pass_context
def service_status(ctx: click.Context) -> None:
    """Get service status."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        service_mgr = ServiceManager()
        info = service_mgr.get_status()

        data = {
            "is_available": info.is_available,
            "status": info.status.value,
            "install_path": str(info.install_path) if info.install_path else None,
        }

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(data, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@service_cmd.command("install")
@click.pass_context
def service_install(ctx: click.Context) -> None:
    """Install the service."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        service_mgr = ServiceManager()
        success, message = service_mgr.install_service()

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=success, message=message))

        if not success:
            sys.exit(1)

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@service_cmd.command("uninstall")
@click.pass_context
def service_uninstall(ctx: click.Context) -> None:
    """Uninstall the service."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        service_mgr = ServiceManager()
        success, message = service_mgr.uninstall_service()

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=success, message=message))

        if not success:
            sys.exit(1)

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# DNS Commands
# =============================================================================

@cli.group("dns")
def dns_cmd():
    """Manage DNS configuration."""
    pass


@dns_cmd.command("get")
@click.pass_context
def dns_get(ctx: click.Context) -> None:
    """Get DNS configuration."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        dns_config = config.read_dns()

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(dns_config or {}, success=True))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@dns_cmd.command("set")
@click.argument("config_yaml")
@click.pass_context
def dns_set(ctx: click.Context, config_yaml: str) -> None:
    """Set DNS configuration from YAML string or file."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        # Check if it's a file path
        if os.path.isfile(config_yaml):
            with open(config_yaml, "r") as f:
                content = f.read()
        else:
            content = config_yaml

        # Validate YAML
        valid, error = validate_yaml_content(content)
        if not valid:
            formatter = get_formatter(json_mode)
            click.echo(formatter.output(None, success=False, message=error))
            sys.exit(1)

        dns_config = yaml.safe_load(content)
        config.write_dns(dns_config)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="DNS configuration updated"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@dns_cmd.command("enable")
@click.pass_context
def dns_enable(ctx: click.Context) -> None:
    """Enable DNS settings."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_dns_settings = True
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="DNS settings enabled"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


@dns_cmd.command("disable")
@click.pass_context
def dns_disable(ctx: click.Context) -> None:
    """Disable DNS settings."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    try:
        verge = config.read_verge()
        verge.enable_dns_settings = False
        config.write_verge(verge)

        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=True, message="DNS settings disabled"))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


# =============================================================================
# Utility Commands
# =============================================================================

@cli.command("version")
@click.pass_context
def version_cmd(ctx: click.Context) -> None:
    """Show version information."""
    json_mode = ctx.obj.get("json_mode", False)

    data = {
        "cli_version": "0.1.0",
        "app_id": "io.github.clash-verge-rev.clash-verge-rev",
    }

    formatter = get_formatter(json_mode)
    click.echo(formatter.output(data, success=True))


@cli.command("doctor")
@click.pass_context
def doctor_cmd(ctx: click.Context) -> None:
    """Diagnose configuration and environment issues."""
    config = ctx.obj["config"]
    json_mode = ctx.obj["json_mode"]

    issues = []
    warnings = []

    try:
        # Check config directory exists
        config_dir = config.get_config_dir()
        if not config_dir.exists():
            issues.append(f"Config directory does not exist: {config_dir}")
        else:
            # Check required files
            if not config.verge_path().exists():
                warnings.append("verge.yaml not found - will be created on first run")

            if not config.profiles_path().exists():
                warnings.append("profiles.yaml not found - will be created on first run")

        # Check profiles directory
        profiles_dir = config.get_profiles_dir()
        if profiles_dir.exists():
            profile_count = len(list(profiles_dir.glob("*.yaml")))
            if profile_count == 0:
                warnings.append("No profile files found in profiles directory")

        # Validate current runtime config
        try:
            runtime = RuntimeManager(config)
            is_valid, message = runtime.validate_config()
            if not is_valid:
                issues.append(f"Runtime config validation: {message}")
        except Exception as e:
            warnings.append(f"Could not validate runtime config: {e}")

        # Summary
        data = {
            "config_dir": str(config_dir),
            "issues": issues,
            "warnings": warnings,
            "healthy": len(issues) == 0,
        }

        formatter = get_formatter(json_mode)
        if issues:
            click.echo(formatter.output(data, success=False, message=f"Found {len(issues)} issues"))
            sys.exit(1)
        else:
            msg = "All checks passed" if not warnings else f"All checks passed with {len(warnings)} warnings"
            click.echo(formatter.output(data, success=True, message=msg))

    except Exception as e:
        formatter = get_formatter(json_mode)
        click.echo(formatter.output(None, success=False, message=str(e)))
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
