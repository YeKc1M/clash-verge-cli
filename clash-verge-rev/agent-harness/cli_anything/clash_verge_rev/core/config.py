"""
Configuration management for Clash Verge Rev.

Manages verge.yaml, profiles.yaml, and the config directory structure.
"""

import os
import platform
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigNotFoundError(ConfigError):
    """Raised when a configuration file is not found."""
    pass


@dataclass
class VergeConfig:
    """
    Represents verge.yaml configuration.

    Based on IVerge struct in src/config/verge.rs
    """
    # Logging
    app_log_level: Optional[str] = None
    app_log_max_size: Optional[int] = None
    app_log_max_count: Optional[int] = None

    # UI Settings
    language: Optional[str] = None
    theme_mode: Optional[str] = None  # light, dark, system
    theme_setting: Optional[Dict[str, Any]] = None
    traffic_graph: Optional[bool] = None
    enable_memory_usage: Optional[bool] = None
    enable_group_icon: Optional[bool] = None
    common_tray_icon: Optional[bool] = None
    sysproxy_tray_icon: Optional[bool] = None
    tun_tray_icon: Optional[bool] = None
    notice_position: Optional[str] = None
    collapse_navbar: Optional[bool] = None
    menu_icon: Optional[str] = None
    menu_order: Optional[List[str]] = None

    # Proxy Settings
    enable_tun_mode: Optional[bool] = None
    enable_system_proxy: Optional[bool] = None
    enable_proxy_guard: Optional[bool] = None
    enable_bypass_check: Optional[bool] = None
    enable_dns_settings: Optional[bool] = None
    use_default_bypass: Optional[bool] = None
    system_proxy_bypass: Optional[str] = None
    proxy_auto_config: Optional[bool] = None
    proxy_host: Optional[str] = None
    pac_file_content: Optional[str] = None
    proxy_guard_duration: Optional[int] = None

    # Auto-launch
    enable_auto_launch: Optional[bool] = None
    enable_silent_start: Optional[bool] = None

    # Core Settings
    clash_core: Optional[str] = None
    default_latency_test: Optional[str] = None
    default_latency_timeout: Optional[int] = None
    enable_auto_delay_detection: Optional[bool] = None
    auto_delay_detection_interval_minutes: Optional[int] = None
    enable_builtin_enhanced: Optional[bool] = None
    auto_close_connection: Optional[bool] = None

    # Hotkeys
    hotkeys: Optional[List[str]] = None
    enable_global_hotkey: Optional[bool] = None

    # UI Layout
    proxy_layout_column: Optional[int] = None
    home_cards: Optional[Dict[str, Any]] = None
    start_page: Optional[str] = None
    tray_event: Optional[str] = None
    env_type: Optional[str] = None
    startup_script: Optional[str] = None

    # Web UI
    web_ui_list: Optional[List[str]] = None

    # Testing
    test_list: Optional[List[Dict[str, Any]]] = None

    # Logging cleanup
    auto_log_clean: Optional[int] = None  # 0: none, 1: 1d, 2: 7d, 3: 30d, 4: 90d

    # Backup
    enable_auto_backup_schedule: Optional[bool] = None
    auto_backup_interval_hours: Optional[int] = None
    auto_backup_on_change: Optional[bool] = None

    # Port overrides
    verge_mixed_port: Optional[int] = None
    verge_socks_port: Optional[int] = None
    verge_socks_enabled: Optional[bool] = None

    # Platform-specific (Linux/Mac)
    verge_redir_port: Optional[int] = None
    verge_redir_enabled: Optional[bool] = None
    verge_tproxy_port: Optional[int] = None
    verge_tproxy_enabled: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VergeConfig":
        """Create VergeConfig from dictionary."""
        # Filter only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class PrfItem:
    """Represents a profile item."""
    uid: Optional[str] = None
    name: Optional[str] = None
    desc: Optional[str] = None
    file: Optional[str] = None
    url: Optional[str] = None
    selected: Optional[List[Dict[str, str]]] = None
    extra: Optional[Dict[str, Any]] = None
    updated: Optional[int] = None  # Unix timestamp
    option: Optional[Dict[str, Any]] = None
    home: Optional[str] = None


@dataclass
class ProfilesConfig:
    """
    Represents profiles.yaml configuration.

    Based on IProfiles struct in src/config/profiles.rs
    """
    current: Optional[str] = None
    items: List[PrfItem] = field(default_factory=list)
    chain: Optional[List[str]] = None  # Profile chain for enhanced mode
    valid: Optional[List[str]] = None  # Valid profiles for enhanced mode

    def get_profile_by_uid(self, uid: str) -> Optional[PrfItem]:
        """Get profile by UID."""
        for item in self.items:
            if item.uid == uid:
                return item
        return None

    def get_profile_by_name(self, name: str) -> Optional[PrfItem]:
        """Get profile by name."""
        for item in self.items:
            if item.name == name:
                return item
        return None

    def get_current_profile(self) -> Optional[PrfItem]:
        """Get currently active profile."""
        if self.current:
            return self.get_profile_by_uid(self.current)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {}
        if self.current is not None:
            result["current"] = self.current
        if self.items:
            result["items"] = [
                {k: v for k, v in asdict(item).items() if v is not None}
                for item in self.items
            ]
        if self.chain is not None:
            result["chain"] = self.chain
        if self.valid is not None:
            result["valid"] = self.valid
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfilesConfig":
        """Create ProfilesConfig from dictionary."""
        items = []
        if "items" in data and data["items"]:
            for item_data in data["items"]:
                items.append(PrfItem(**item_data))

        return cls(
            current=data.get("current"),
            items=items,
            chain=data.get("chain"),
            valid=data.get("valid"),
        )


class ConfigManager:
    """
    Manages Clash Verge Rev configuration files.

    Handles reading and writing to:
    - verge.yaml (app settings)
    - profiles.yaml (proxy profiles)
    - config.yaml (clash core config)
    - dns_config.yaml (DNS settings)
    """

    APP_ID = "io.github.clash-verge-rev.clash-verge-rev"
    CLASH_CONFIG = "config.yaml"
    VERGE_CONFIG = "verge.yaml"
    PROFILE_YAML = "profiles.yaml"
    DNS_CONFIG = "dns_config.yaml"

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize ConfigManager.

        Args:
            config_dir: Override the default config directory.
                       If not provided, uses platform-specific location.
        """
        self._config_dir = config_dir
        self._verge_cache: Optional[VergeConfig] = None
        self._profiles_cache: Optional[ProfilesConfig] = None
        self._verge_mtime: float = 0
        self._profiles_mtime: float = 0

    def get_config_dir(self) -> Path:
        """Get the configuration directory path."""
        if self._config_dir:
            return self._config_dir

        # Check for portable mode
        portable_marker = Path(__file__).parent / ".config" / "PORTABLE"
        if portable_marker.exists():
            return Path(__file__).parent / ".config" / self.APP_ID

        # Platform-specific paths
        system = platform.system()
        if system == "Windows":
            app_data = os.environ.get("LOCALAPPDATA", "")
            return Path(app_data) / self.APP_ID
        elif system == "Darwin":
            home = Path.home()
            return home / "Library" / "Application Support" / self.APP_ID
        else:  # Linux and other Unix
            xdg_data = os.environ.get("XDG_DATA_HOME", "")
            if xdg_data:
                return Path(xdg_data) / self.APP_ID
            return Path.home() / ".local" / "share" / self.APP_ID

    def get_profiles_dir(self) -> Path:
        """Get the profiles directory path."""
        return self.get_config_dir() / "profiles"

    def get_logs_dir(self) -> Path:
        """Get the logs directory path."""
        return self.get_config_dir() / "logs"

    def get_backup_dir(self) -> Path:
        """Get the backup directory path."""
        return self.get_config_dir() / "clash-verge-rev-backup"

    def verge_path(self) -> Path:
        """Get verge.yaml path."""
        return self.get_config_dir() / self.VERGE_CONFIG

    def profiles_path(self) -> Path:
        """Get profiles.yaml path."""
        return self.get_config_dir() / self.PROFILE_YAML

    def clash_path(self) -> Path:
        """Get config.yaml path."""
        return self.get_config_dir() / self.CLASH_CONFIG

    def dns_path(self) -> Path:
        """Get dns_config.yaml path."""
        return self.get_config_dir() / self.DNS_CONFIG

    def ensure_dirs(self) -> None:
        """Ensure all config directories exist."""
        self.get_config_dir().mkdir(parents=True, exist_ok=True)
        self.get_profiles_dir().mkdir(parents=True, exist_ok=True)
        self.get_logs_dir().mkdir(parents=True, exist_ok=True)
        self.get_backup_dir().mkdir(parents=True, exist_ok=True)

    def _read_yaml(self, path: Path) -> Dict[str, Any]:
        """Read YAML file."""
        if not path.exists():
            raise ConfigNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return {}
            return yaml.safe_load(content) or {}

    def _write_yaml(self, path: Path, data: Dict[str, Any], header: Optional[str] = None) -> None:
        """Write YAML file."""
        self.ensure_dirs()

        with open(path, "w", encoding="utf-8") as f:
            if header:
                f.write(f"# {header}\n")
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def read_verge(self, use_cache: bool = True) -> VergeConfig:
        """
        Read verge.yaml configuration.

        Args:
            use_cache: If True, returns cached data if file hasn't changed.

        Returns:
            VergeConfig object
        """
        path = self.verge_path()

        if use_cache and self._verge_cache:
            try:
                mtime = path.stat().st_mtime
                if mtime == self._verge_mtime:
                    return self._verge_cache
            except FileNotFoundError:
                pass

        try:
            data = self._read_yaml(path)
        except ConfigNotFoundError:
            return VergeConfig()

        self._verge_cache = VergeConfig.from_dict(data)
        try:
            self._verge_mtime = path.stat().st_mtime
        except FileNotFoundError:
            self._verge_mtime = 0

        return self._verge_cache

    def write_verge(self, config: VergeConfig) -> None:
        """
        Write verge.yaml configuration.

        Args:
            config: VergeConfig object to write
        """
        path = self.verge_path()
        self._write_yaml(path, config.to_dict(), "Verge Config")
        self._verge_cache = config
        try:
            self._verge_mtime = path.stat().st_mtime
        except FileNotFoundError:
            self._verge_mtime = 0

    def read_profiles(self, use_cache: bool = True) -> ProfilesConfig:
        """
        Read profiles.yaml configuration.

        Args:
            use_cache: If True, returns cached data if file hasn't changed.

        Returns:
            ProfilesConfig object
        """
        path = self.profiles_path()

        if use_cache and self._profiles_cache:
            try:
                mtime = path.stat().st_mtime
                if mtime == self._profiles_mtime:
                    return self._profiles_cache
            except FileNotFoundError:
                pass

        try:
            data = self._read_yaml(path)
        except ConfigNotFoundError:
            return ProfilesConfig()

        self._profiles_cache = ProfilesConfig.from_dict(data)
        try:
            self._profiles_mtime = path.stat().st_mtime
        except FileNotFoundError:
            self._profiles_mtime = 0

        return self._profiles_cache

    def write_profiles(self, config: ProfilesConfig) -> None:
        """
        Write profiles.yaml configuration.

        Args:
            config: ProfilesConfig object to write
        """
        path = self.profiles_path()
        self._write_yaml(path, config.to_dict(), "Profiles Config for Clash Verge")
        self._profiles_cache = config
        try:
            self._profiles_mtime = path.stat().st_mtime
        except FileNotFoundError:
            self._profiles_mtime = 0

    def read_clash(self) -> Dict[str, Any]:
        """Read clash config.yaml."""
        try:
            return self._read_yaml(self.clash_path())
        except ConfigNotFoundError:
            return {}

    def write_clash(self, config: Dict[str, Any]) -> None:
        """Write clash config.yaml."""
        self._write_yaml(self.clash_path(), config, "Clash Config")

    def read_dns(self) -> Dict[str, Any]:
        """Read dns_config.yaml."""
        try:
            return self._read_yaml(self.dns_path())
        except ConfigNotFoundError:
            return {}

    def write_dns(self, config: Dict[str, Any]) -> None:
        """Write dns_config.yaml."""
        self._write_yaml(self.dns_path(), config, "DNS Config")

    def patch_verge(self, updates: Dict[str, Any]) -> VergeConfig:
        """
        Patch verge configuration with partial updates.

        Args:
            updates: Dictionary of fields to update

        Returns:
            Updated VergeConfig
        """
        config = self.read_verge()

        # Update fields
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.write_verge(config)
        return config

    def patch_profiles(self, updates: Dict[str, Any]) -> ProfilesConfig:
        """
        Patch profiles configuration with partial updates.

        Args:
            updates: Dictionary of fields to update

        Returns:
            Updated ProfilesConfig
        """
        config = self.read_profiles()

        if "current" in updates:
            config.current = updates["current"]

        self.write_profiles(config)
        return config

    def get_profile_file_path(self, filename: str) -> Path:
        """Get full path to a profile file."""
        return self.get_profiles_dir() / filename

    def read_profile_file(self, filename: str) -> str:
        """Read a profile file's content."""
        path = self.get_profile_file_path(filename)
        if not path.exists():
            raise ConfigNotFoundError(f"Profile file not found: {filename}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_profile_file(self, filename: str, content: str) -> None:
        """Write a profile file's content."""
        path = self.get_profile_file_path(filename)
        self.ensure_dirs()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
