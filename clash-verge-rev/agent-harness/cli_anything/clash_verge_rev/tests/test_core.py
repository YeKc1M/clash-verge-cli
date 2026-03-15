"""Unit tests for clash-verge-rev CLI core modules."""

import json
import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from cli_anything.clash_verge_rev.core.config import (
    ConfigManager,
    ConfigNotFoundError,
    ProfilesConfig,
    PrfItem,
    VergeConfig,
)
from cli_anything.clash_verge_rev.core.runtime import ClashInfo, RuntimeManager
from cli_anything.clash_verge_rev.core.service import ServiceManager, ServiceStatus
from cli_anything.clash_verge_rev.core.backup import BackupManager, BackupFile, BackupNotFoundError
from cli_anything.clash_verge_rev.utils.output import OutputFormatter
from cli_anything.clash_verge_rev.utils.validators import (
    validate_profile_name,
    validate_url,
    validate_port,
    validate_yaml_content,
)


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_config_manager_init_default(self):
        """Test initialization with default config directory."""
        manager = ConfigManager()
        assert manager._config_dir is None
        # Should be able to get config dir
        config_dir = manager.get_config_dir()
        assert isinstance(config_dir, Path)

    def test_config_manager_init_custom(self):
        """Test initialization with custom config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir)
            manager = ConfigManager(custom_path)
            assert manager._config_dir == custom_path
            assert manager.get_config_dir() == custom_path

    def test_ensure_dirs_creates_directories(self):
        """Test that ensure_dirs creates all necessary directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()

            assert manager.get_config_dir().exists()
            assert manager.get_profiles_dir().exists()
            assert manager.get_logs_dir().exists()
            assert manager.get_backup_dir().exists()

    def test_read_write_verge_config(self):
        """Test reading and writing verge.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Write a config
            config = VergeConfig(
                verge_mixed_port=7890,
                enable_system_proxy=True,
                theme_mode="dark",
            )
            manager.write_verge(config)

            # Read it back
            read_config = manager.read_verge(use_cache=False)
            assert read_config.verge_mixed_port == 7890
            assert read_config.enable_system_proxy is True
            assert read_config.theme_mode == "dark"

    def test_read_write_profiles_config(self):
        """Test reading and writing profiles.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Write a config
            item = PrfItem(uid="test123", name="Test Profile", file="test.yaml")
            config = ProfilesConfig(current="test123", items=[item])
            manager.write_profiles(config)

            # Read it back
            read_config = manager.read_profiles(use_cache=False)
            assert read_config.current == "test123"
            assert len(read_config.items) == 1
            assert read_config.items[0].uid == "test123"
            assert read_config.items[0].name == "Test Profile"

    def test_read_write_clash_config(self):
        """Test reading and writing clash config.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            config = {
                "port": 7890,
                "socks-port": 7891,
                "mixed-port": 7890,
                "proxies": [],
            }
            manager.write_clash(config)

            read_config = manager.read_clash()
            assert read_config["port"] == 7890
            assert read_config["socks-port"] == 7891

    def test_read_write_dns_config(self):
        """Test reading and writing dns_config.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            config = {
                "enable": True,
                "nameserver": ["8.8.8.8", "1.1.1.1"],
            }
            manager.write_dns(config)

            read_config = manager.read_dns()
            assert read_config["enable"] is True
            assert "8.8.8.8" in read_config["nameserver"]

    def test_patch_verge_config(self):
        """Test partial updates to verge config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Initial config
            config = VergeConfig(verge_mixed_port=7890, theme_mode="light")
            manager.write_verge(config)

            # Patch it
            updated = manager.patch_verge({"verge_mixed_port": 8080, "enable_tun_mode": True})

            assert updated.verge_mixed_port == 8080
            assert updated.theme_mode == "light"  # Unchanged
            assert updated.enable_tun_mode is True

    def test_patch_profiles_config(self):
        """Test partial updates to profiles config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Initial config
            item = PrfItem(uid="test", name="Test")
            config = ProfilesConfig(current="test", items=[item])
            manager.write_profiles(config)

            # Patch it
            updated = manager.patch_profiles({"current": "new_current"})

            assert updated.current == "new_current"
            assert len(updated.items) == 1  # Unchanged

    def test_profile_file_operations(self):
        """Test reading and writing profile files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()

            content = "proxies:\n  - name: Test\n    type: ss\n"
            manager.write_profile_file("test_profile.yaml", content)

            read_content = manager.read_profile_file("test_profile.yaml")
            assert read_content == content

            # Test file exists
            file_path = manager.get_profile_file_path("test_profile.yaml")
            assert file_path.exists()


class TestVergeConfig:
    """Tests for VergeConfig dataclass."""

    def test_verge_config_to_dict(self):
        """Test conversion to dictionary."""
        config = VergeConfig(verge_mixed_port=7890, enable_system_proxy=True)
        data = config.to_dict()

        assert data["verge_mixed_port"] == 7890
        assert data["enable_system_proxy"] is True

    def test_verge_config_from_dict(self):
        """Test parsing from dictionary."""
        data = {
            "verge_mixed_port": 7890,
            "enable_system_proxy": True,
            "theme_mode": "dark",
        }
        config = VergeConfig.from_dict(data)

        assert config.verge_mixed_port == 7890
        assert config.enable_system_proxy is True
        assert config.theme_mode == "dark"

    def test_verge_config_excludes_none(self):
        """Test that None values are excluded from dict."""
        config = VergeConfig(verge_mixed_port=7890)
        data = config.to_dict()

        assert "verge_mixed_port" in data
        assert "enable_system_proxy" not in data
        assert "theme_mode" not in data


class TestProfilesConfig:
    """Tests for ProfilesConfig dataclass."""

    def test_profiles_config_get_by_uid(self):
        """Test getting profile by UID."""
        item1 = PrfItem(uid="uid1", name="Profile 1")
        item2 = PrfItem(uid="uid2", name="Profile 2")
        config = ProfilesConfig(items=[item1, item2])

        found = config.get_profile_by_uid("uid1")
        assert found is not None
        assert found.name == "Profile 1"

        not_found = config.get_profile_by_uid("uid3")
        assert not_found is None

    def test_profiles_config_get_by_name(self):
        """Test getting profile by name."""
        item1 = PrfItem(uid="uid1", name="Profile 1")
        item2 = PrfItem(uid="uid2", name="Profile 2")
        config = ProfilesConfig(items=[item1, item2])

        found = config.get_profile_by_name("Profile 2")
        assert found is not None
        assert found.uid == "uid2"

    def test_profiles_config_get_current(self):
        """Test getting current profile."""
        item1 = PrfItem(uid="uid1", name="Profile 1")
        item2 = PrfItem(uid="uid2", name="Profile 2")
        config = ProfilesConfig(current="uid2", items=[item1, item2])

        current = config.get_current_profile()
        assert current is not None
        assert current.uid == "uid2"

    def test_profiles_config_to_dict(self):
        """Test conversion to dictionary."""
        item = PrfItem(uid="uid1", name="Test", file="test.yaml")
        config = ProfilesConfig(current="uid1", items=[item])
        data = config.to_dict()

        assert data["current"] == "uid1"
        assert len(data["items"]) == 1
        assert data["items"][0]["uid"] == "uid1"

    def test_profiles_config_from_dict(self):
        """Test parsing from dictionary."""
        data = {
            "current": "uid1",
            "items": [
                {"uid": "uid1", "name": "Test", "file": "test.yaml"},
            ],
        }
        config = ProfilesConfig.from_dict(data)

        assert config.current == "uid1"
        assert len(config.items) == 1
        assert config.items[0].name == "Test"


class TestRuntimeManager:
    """Tests for RuntimeManager."""

    def test_runtime_get_config(self):
        """Test getting runtime configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))

            # Setup test config
            verge = VergeConfig(verge_mixed_port=8080)
            manager.write_verge(verge)

            runtime = RuntimeManager(manager)
            config = runtime.get_runtime_config()

            assert config["mixed-port"] == 8080

    def test_runtime_get_yaml(self):
        """Test getting runtime as YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()

            # Create a profile and set it as current
            profile_content = "port: 7890\nproxies:\n  - name: Test\n"
            manager.write_profile_file("test.yaml", profile_content)
            from cli_anything.clash_verge_rev.core.config import PrfItem, ProfilesConfig
            item = PrfItem(uid="test123", name="Test", file="test.yaml")
            profiles = ProfilesConfig(current="test123", items=[item])
            manager.write_profiles(profiles)

            runtime = RuntimeManager(manager)
            yaml_str = runtime.get_runtime_yaml()

            assert "port: 7890" in yaml_str

    def test_runtime_get_exists_keys(self):
        """Test getting existing config keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()

            # Create a profile and set it as current
            profile_content = "port: 7890\nsocks-port: 7891\nproxies:\n  - name: Test\n"
            manager.write_profile_file("test.yaml", profile_content)
            from cli_anything.clash_verge_rev.core.config import PrfItem, ProfilesConfig
            item = PrfItem(uid="test123", name="Test", file="test.yaml")
            profiles = ProfilesConfig(current="test123", items=[item])
            manager.write_profiles(profiles)

            runtime = RuntimeManager(manager)
            keys = runtime.get_exists_keys()

            assert "port" in keys
            assert "socks-port" in keys

    def test_runtime_validate_config_valid(self):
        """Test validating valid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()

            # Create a profile and set it as current with valid config
            profile_content = "proxies:\n  - name: Test\n    type: ss\n"
            manager.write_profile_file("test.yaml", profile_content)
            from cli_anything.clash_verge_rev.core.config import PrfItem, ProfilesConfig
            item = PrfItem(uid="test123", name="Test", file="test.yaml")
            profiles = ProfilesConfig(current="test123", items=[item])
            manager.write_profiles(profiles)

            runtime = RuntimeManager(manager)
            is_valid, message = runtime.validate_config()

            assert is_valid is True

    def test_runtime_validate_config_invalid(self):
        """Test validating invalid config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.ensure_dirs()
            # Empty config is invalid (no proxies)
            # No profile set, so runtime config is empty

            runtime = RuntimeManager(manager)
            is_valid, message = runtime.validate_config()

            assert is_valid is False
            assert "proxies" in message.lower() or "proxy-providers" in message.lower()

    def test_runtime_get_clash_info(self):
        """Test getting clash connection info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(Path(tmpdir))
            manager.write_clash({"mixed-port": 7890})

            runtime = RuntimeManager(manager)
            info = runtime.get_clash_info()

            assert isinstance(info, ClashInfo)
            assert info.mixed_port == 7890


class TestServiceManager:
    """Tests for ServiceManager."""

    def test_service_manager_is_available(self):
        """Test checking platform availability."""
        manager = ServiceManager()
        # Should return bool based on platform
        is_available = manager.is_service_available()
        assert isinstance(is_available, bool)

    def test_service_get_status(self):
        """Test getting service status."""
        manager = ServiceManager()
        info = manager.get_status()

        assert hasattr(info, "status")
        assert hasattr(info, "is_available")
        assert isinstance(info.is_available, bool)

    def test_service_status_info(self):
        """Test ServiceInfo dataclass."""
        info = ServiceStatus.INSTALLED
        assert info.value == "installed"


class TestBackupManager:
    """Tests for BackupManager."""

    def test_backup_manager_init(self):
        """Test initialization."""
        manager = BackupManager()
        assert isinstance(manager.backup_dir, Path)

    def test_create_backup(self):
        """Test creating backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()

            # Create some config files
            config_manager.write_clash({"port": 7890})
            config_manager.write_verge(VergeConfig(verge_mixed_port=7890))

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            assert backup.path.exists()
            assert backup.filename.startswith("clash-verge-rev-backup")
            assert backup.size > 0

    def test_list_backups(self):
        """Test listing backups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            backups = backup_mgr.list_backups()
            assert len(backups) >= 1
            assert any(b.filename == backup.filename for b in backups)

    def test_get_backup(self):
        """Test getting specific backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            found = backup_mgr.get_backup(backup.filename)
            assert found.filename == backup.filename

    def test_delete_backup(self):
        """Test deleting backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            assert backup.path.exists()
            backup_mgr.delete_backup(backup.filename)
            assert not backup.path.exists()

    def test_restore_backup(self):
        """Test restoring from backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()

            # Create initial config
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            # Modify config
            config_manager.write_clash({"port": 8080})

            # Restore backup
            backup_mgr.restore_backup(backup.filename, force=True)

            # Verify restored
            restored = config_manager.read_clash()
            assert restored["port"] == 7890

    def test_import_export_backup(self):
        """Test import and export operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)
            backup = backup_mgr.create_backup()

            # Export
            export_path = Path(tmpdir) / "exported.zip"
            backup_mgr.export_backup(backup.filename, export_path)
            assert export_path.exists()

            # Import
            imported_name = backup_mgr.import_backup(export_path)
            assert "imported" in imported_name

    def test_cleanup_old_backups(self):
        """Test removing old backups."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            config_manager = ConfigManager(Path(tmpdir))
            config_manager.ensure_dirs()
            config_manager.write_clash({"port": 7890})

            backup_mgr = BackupManager(config_manager)

            # Create multiple backups with small delay to ensure different timestamps
            for _ in range(5):
                backup_mgr.create_backup()
                time.sleep(0.01)  # Small delay for different timestamps

            # Verify we have 5 backups
            backups = backup_mgr.list_backups()
            assert len(backups) == 5

            # Cleanup, keeping only 2
            removed = backup_mgr.cleanup_old_backups(2)
            assert removed == 3

            backups = backup_mgr.list_backups()
            assert len(backups) == 2


class TestOutputFormatter:
    """Tests for OutputFormatter."""

    def test_format_output_json(self):
        """Test JSON output format."""
        formatter = OutputFormatter(use_json=True)
        output = formatter.output({"key": "value"}, success=True)

        data = json.loads(output)
        assert data["success"] is True
        assert data["data"]["key"] == "value"

    def test_format_output_human(self):
        """Test human-readable output."""
        formatter = OutputFormatter(use_json=False, use_color=False)
        output = formatter.output({"key": "value"}, success=True, message="Done")

        assert "Done" in output
        assert "key:" in output or "key" in output

    def test_format_output_with_colors(self):
        """Test colored terminal output."""
        formatter = OutputFormatter(use_json=False, use_color=True)
        output = formatter.output(None, success=True, message="Success")

        # Check for ANSI escape codes
        assert "\033[" in output or "Success" in output

    def test_format_dict_human(self):
        """Test formatting dictionary."""
        formatter = OutputFormatter(use_json=False, use_color=False)
        output = formatter._format_dict({"name": "test", "port": 7890})

        assert "name" in output
        assert "test" in output

    def test_format_list_human(self):
        """Test formatting list."""
        formatter = OutputFormatter(use_json=False, use_color=False)
        output = formatter._format_list(["item1", "item2"])

        assert "item1" in output
        assert "item2" in output


class TestValidators:
    """Tests for validators."""

    def test_validate_profile_name(self):
        """Test profile name validation."""
        # Valid names
        assert validate_profile_name("My Profile")[0] is True
        assert validate_profile_name("test-123")[0] is True
        assert validate_profile_name("test_123")[0] is True

        # Invalid names
        assert validate_profile_name("")[0] is False
        assert validate_profile_name("a" * 101)[0] is False

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com/config.yaml")[0] is True
        assert validate_url("http://localhost:8080/config")[0] is True

        # Invalid URLs
        assert validate_url("")[0] is False
        assert validate_url("not-a-url")[0] is False
        assert validate_url("ftp://example.com/file")[0] is False

    def test_validate_port(self):
        """Test port validation."""
        # Valid ports
        assert validate_port(7890)[0] is True
        assert validate_port(1)[0] is True
        assert validate_port(65535)[0] is True

        # Invalid ports
        assert validate_port(0)[0] is False
        assert validate_port(65536)[0] is False
        assert validate_port(-1)[0] is False
        assert validate_port("abc")[0] is False

    def test_validate_yaml_content(self):
        """Test YAML validation."""
        # Valid YAML
        assert validate_yaml_content("key: value")[0] is True
        assert validate_yaml_content("proxies:\n  - name: test")[0] is True

        # Invalid YAML
        assert validate_yaml_content("")[0] is False
        assert validate_yaml_content("invalid: yaml: syntax:")[0] is False
