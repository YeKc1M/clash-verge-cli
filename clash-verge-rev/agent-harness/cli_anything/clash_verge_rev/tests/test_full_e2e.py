"""End-to-end tests for clash-verge-rev CLI.

These tests use the Click testing runner to invoke CLI commands.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

import pytest
from click.testing import CliRunner

from cli_anything.clash_verge_rev.clash_verge_rev_cli import cli
from cli_anything.clash_verge_rev.core.config import ConfigManager, PrfItem, ProfilesConfig


class TestCLIEntryPoint:
    """Tests for CLI entry point."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Clash Verge Rev CLI" in result.output
        assert "profile" in result.output
        assert "core" in result.output
        assert "config" in result.output

    def test_cli_version(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["version"])

        assert result.exit_code == 0
        assert "cli_version" in result.output

    def test_cli_json_flag(self):
        """Test global JSON flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "version"])

        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert data["success"] is True
        assert "cli_version" in data["data"]


class TestProfileCommands:
    """E2E tests for profile commands."""

    def test_profile_list_command(self):
        """Test profile list command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(cli, ["--config-dir", str(config_dir), "profile", "list"])

            assert result.exit_code == 0
            assert "profiles" in result.output or result.output == ""

    def test_profile_current_command(self):
        """Test profile current command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(cli, ["--config-dir", str(config_dir), "profile", "current"])

            assert result.exit_code == 0

    def test_profile_create_command(self):
        """Test profile create command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "create", "TestProfile"],
            )

            assert result.exit_code == 0
            assert "Created" in result.output or "profile" in result.output.lower()

            # Verify file was created
            profiles_dir = config_dir / "profiles"
            yaml_files = list(profiles_dir.glob("*.yaml"))
            assert len(yaml_files) > 0

    def test_profile_use_command(self):
        """Test profile use command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # First create a profile
            runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "create", "TestProfile"],
            )

            # Get the UID
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "--json", "profile", "list"],
            )
            data = json.loads(result.output)
            profiles = data["data"]["profiles"]
            assert len(profiles) > 0
            uid = profiles[0]["uid"]

            # Use the profile
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "use", uid],
            )

            assert result.exit_code == 0
            assert "Switched" in result.output or "profile" in result.output.lower()

    def test_profile_show_command(self):
        """Test profile show command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a profile
            runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "create", "TestProfile"],
            )

            # Get the UID
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "--json", "profile", "list"],
            )
            data = json.loads(result.output)
            profiles = data["data"]["profiles"]
            uid = profiles[0]["uid"]

            # Show the profile
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "show", uid],
            )

            assert result.exit_code == 0
            assert "name" in result.output or "TestProfile" in result.output

    def test_profile_delete_command(self):
        """Test profile delete command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a profile
            runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "create", "TestProfile"],
            )

            # Get the UID
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "--json", "profile", "list"],
            )
            data = json.loads(result.output)
            profiles = data["data"]["profiles"]
            uid = profiles[0]["uid"]

            # Delete the profile with --yes flag
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "profile", "delete", uid, "--yes"],
            )

            assert result.exit_code == 0


class TestCoreCommands:
    """E2E tests for core commands."""

    def test_core_info_command(self):
        """Test core info command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "core", "info"],
            )

            assert result.exit_code == 0
            assert "port" in result.output.lower() or "mixed_port" in result.output

    def test_core_config_command(self):
        """Test core config command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a profile and set it as current
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            profile_content = "port: 7890\nproxies:\n  - name: Test\n    type: ss\n"
            config_manager.write_profile_file("test.yaml", profile_content)
            item = PrfItem(uid="test123", name="Test", file="test.yaml")
            profiles = ProfilesConfig(current="test123", items=[item])
            config_manager.write_profiles(profiles)

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "core", "config"],
            )

            assert result.exit_code == 0
            assert "port" in result.output or "7890" in result.output

    def test_core_validate_command(self):
        """Test core validate command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a profile with valid config
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            profile_content = "proxies:\n  - name: Test\n    type: ss\n"
            config_manager.write_profile_file("test.yaml", profile_content)
            item = PrfItem(uid="test123", name="Test", file="test.yaml")
            profiles = ProfilesConfig(current="test123", items=[item])
            config_manager.write_profiles(profiles)

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "core", "validate"],
            )

            assert result.exit_code == 0
            assert "valid" in result.output.lower() or "true" in result.output.lower()

    def test_core_generate_command(self):
        """Test core generate command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a valid config
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            config_manager.write_clash({
                "proxies": [{"name": "Test", "type": "ss"}],
            })

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "core", "generate"],
            )

            assert result.exit_code == 0
            assert "generated" in result.output.lower() or "success" in result.output.lower()


class TestConfigCommands:
    """E2E tests for config commands."""

    def test_config_get_command(self):
        """Test config get command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Set a config value first
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            verge = config_manager.read_verge()
            verge.verge_mixed_port = 7890
            config_manager.write_verge(verge)

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "config", "get", "verge_mixed_port"],
            )

            assert result.exit_code == 0
            assert "7890" in result.output

    def test_config_set_command(self):
        """Test config set command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "config", "set", "verge_mixed_port", "8080"],
            )

            assert result.exit_code == 0
            assert "8080" in result.output

            # Verify it was set
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "--json", "config", "get", "verge_mixed_port"],
            )
            data = json.loads(result.output)
            # Note: CLI converts the value to int since the field is an int type
            assert data["data"]["verge_mixed_port"] == 8080 or data["data"]["verge_mixed_port"] == "8080"

    def test_config_unset_command(self):
        """Test config unset command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Set a value first
            runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "config", "set", "verge_mixed_port", "8080"],
            )

            # Unset it
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "config", "unset", "verge_mixed_port"],
            )

            assert result.exit_code == 0

    def test_config_path_command(self):
        """Test config path command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "config", "path"],
            )

            assert result.exit_code == 0
            assert "config_dir" in result.output


class TestProxyCommands:
    """E2E tests for proxy commands."""

    def test_proxy_status_command(self):
        """Test proxy status command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "proxy", "status"],
            )

            assert result.exit_code == 0
            assert "enable_system_proxy" in result.output.lower() or "mixed_port" in result.output.lower()

    def test_proxy_enable_disable(self):
        """Test proxy enable/disable commands."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Enable
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "proxy", "enable"],
            )
            assert result.exit_code == 0

            # Disable
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "proxy", "disable"],
            )
            assert result.exit_code == 0

    def test_proxy_tun_commands(self):
        """Test TUN mode commands."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Enable TUN
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "proxy", "tun-enable"],
            )
            assert result.exit_code == 0

            # Disable TUN
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "proxy", "tun-disable"],
            )
            assert result.exit_code == 0


class TestBackupCommands:
    """E2E tests for backup commands."""

    def test_backup_list_command(self):
        """Test backup list command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "backup", "list"],
            )

            assert result.exit_code == 0
            assert "backups" in result.output

    def test_backup_create_command(self):
        """Test backup create command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create some config
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "backup", "create"],
            )

            assert result.exit_code == 0
            assert "backup" in result.output.lower()

    def test_backup_restore_command(self):
        """Test backup restore command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create config and backup
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "backup", "create"],
            )

            # Get backup filename
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "--json", "backup", "list"],
            )
            data = json.loads(result.output)

            if data["data"]["backups"]:
                filename = data["data"]["backups"][0]["filename"]

                # Restore with force flag
                result = runner.invoke(
                    cli,
                    ["--config-dir", str(config_dir), "backup", "restore", filename, "--force"],
                )

                assert result.exit_code == 0


class TestDNSCommands:
    """E2E tests for DNS commands."""

    def test_dns_get_command(self):
        """Test DNS get command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "dns", "get"],
            )

            assert result.exit_code == 0

    def test_dns_set_command(self):
        """Test DNS set command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            yaml_content = "enable: true\nnameserver:\n  - 8.8.8.8"

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "dns", "set", yaml_content],
            )

            assert result.exit_code == 0

    def test_dns_enable_disable(self):
        """Test DNS enable/disable commands."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Enable
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "dns", "enable"],
            )
            assert result.exit_code == 0

            # Disable
            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "dns", "disable"],
            )
            assert result.exit_code == 0


class TestUtilityCommands:
    """E2E tests for utility commands."""

    def test_doctor_command(self):
        """Test doctor command."""
        runner = CliRunner()

        with runner.isolated_filesystem() as fs:
            config_dir = Path(fs)

            # Create a valid config
            config_manager = ConfigManager(config_dir)
            config_manager.ensure_dirs()
            config_manager.write_clash({
                "proxies": [{"name": "Test", "type": "ss"}],
            })

            result = runner.invoke(
                cli,
                ["--config-dir", str(config_dir), "doctor"],
            )

            # Should pass with valid config
            assert result.exit_code in [0, 1]  # 0 if healthy, 1 if issues found


class TestCLISubprocess:
    """Tests for CLI via subprocess (requires installed CLI)."""

    def _resolve_cli(self, command: str) -> List[str]:
        """Resolve CLI command, checking for installed version first."""
        # Check if CLI is installed in PATH
        if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
            return [command]

        # Try to find the CLI in PATH
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return [command]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        # Not installed, skip tests
        return None

    @pytest.mark.skipif(
        not os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"),
        reason="CLI not installed in PATH"
    )
    def test_cli_subprocess_version(self):
        """Test CLI version via subprocess."""
        cmd = self._resolve_cli("cli-anything-clash-verge-rev")
        if cmd is None:
            pytest.skip("CLI not installed")

        result = subprocess.run(
            cmd + ["--json", "version"],
            capture_output=True,
            text=True,
        )

        assert result.return_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "cli_version" in data["data"]

    @pytest.mark.skipif(
        not os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"),
        reason="CLI not installed in PATH"
    )
    def test_cli_subprocess_profile_list(self):
        """Test profile list via subprocess."""
        cmd = self._resolve_cli("cli-anything-clash-verge-rev")
        if cmd is None:
            pytest.skip("CLI not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                cmd + ["--config-dir", tmpdir, "--json", "profile", "list"],
                capture_output=True,
                text=True,
            )

            assert result.return_code == 0
            data = json.loads(result.stdout)
            assert data["success"] is True
            assert "profiles" in data["data"]

    @pytest.mark.skipif(
        not os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"),
        reason="CLI not installed in PATH"
    )
    def test_cli_subprocess_config_path(self):
        """Test config path via subprocess."""
        cmd = self._resolve_cli("cli-anything-clash-verge-rev")
        if cmd is None:
            pytest.skip("CLI not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                cmd + ["--config-dir", tmpdir, "--json", "config", "path"],
                capture_output=True,
                text=True,
            )

            assert result.return_code == 0
            data = json.loads(result.stdout)
            assert data["success"] is True
            assert "config_dir" in data["data"]
