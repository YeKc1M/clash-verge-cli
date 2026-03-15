"""
Runtime configuration management for Clash Verge Rev.

Manages runtime config which is the merged/enhanced configuration
that gets applied to the Clash core.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from .config import ConfigManager, ConfigNotFoundError


@dataclass
class ClashInfo:
    """Clash core connection information."""
    port: int = 7890
    socks_port: int = 7891
    mixed_port: int = 7890
    redir_port: int = 0
    tproxy_port: int = 0
    external_controller: str = "127.0.0.1:9090"
    secret: Optional[str] = None


class RuntimeManager:
    """
    Manages runtime configuration for Clash Verge Rev.

    The runtime config is the merged configuration that includes:
    - Base profile configuration
    - Profile chain (enhancement scripts)
    - Verge overrides (ports, TUN, etc.)
    - DNS settings
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize RuntimeManager.

        Args:
            config_manager: ConfigManager instance. Creates new if not provided.
        """
        self.config = config_manager or ConfigManager()

    def get_runtime_config(self) -> Dict[str, Any]:
        """
        Get the current runtime configuration.

        This is derived from:
        1. Current profile's config file
        2. Applied chain/valid enhancements
        3. Verge settings overrides

        Returns:
            Merged configuration dictionary
        """
        # Start with current profile
        profiles = self.config.read_profiles()
        runtime_config: Dict[str, Any] = {}

        current_profile = profiles.get_current_profile()
        if current_profile and current_profile.file:
            try:
                profile_content = self.config.read_profile_file(current_profile.file)
                runtime_config = yaml.safe_load(profile_content) or {}
            except (ConfigNotFoundError, yaml.YAMLError):
                runtime_config = {}

        # Apply verge settings overrides
        verge = self.config.read_verge()

        # Port overrides
        ports: Dict[str, Any] = {}
        if verge.verge_mixed_port is not None:
            ports["mixed-port"] = verge.verge_mixed_port
        if verge.verge_socks_port is not None and verge.verge_socks_enabled:
            ports["socks-port"] = verge.verge_socks_port
        if verge.verge_redir_port is not None and verge.verge_redir_enabled:
            ports["redir-port"] = verge.verge_redir_port
        if verge.verge_tproxy_port is not None and verge.verge_tproxy_enabled:
            ports["tproxy-port"] = verge.verge_tproxy_port

        if ports:
            runtime_config.update(ports)

        # TUN mode
        if verge.enable_tun_mode is not None:
            if "tun" not in runtime_config:
                runtime_config["tun"] = {}
            runtime_config["tun"]["enable"] = verge.enable_tun_mode

        # DNS settings
        if verge.enable_dns_settings:
            dns_config = self.config.read_dns()
            if dns_config:
                runtime_config["dns"] = dns_config

        return runtime_config

    def get_runtime_yaml(self) -> str:
        """
        Get runtime configuration as YAML string.

        Returns:
            YAML formatted configuration
        """
        config = self.get_runtime_config()
        return yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def get_exists_keys(self) -> Set[str]:
        """
        Get set of keys that exist in runtime config.

        Returns:
            Set of configuration keys
        """
        config = self.get_runtime_config()

        def collect_keys(obj: Any, prefix: str = "") -> Set[str]:
            keys = set()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    keys.add(full_key)
                    keys.update(collect_keys(value, full_key))
            return keys

        return collect_keys(config)

    def get_chain_logs(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Get chain processing logs.

        Returns:
            Dictionary mapping chain item UID to list of (timestamp, message)
        """
        # This would track enhancement script processing
        # For now, return empty structure
        return {}

    def get_proxy_chain_config(self, exit_node: str) -> Optional[str]:
        """
        Get proxy chain configuration for a specific exit node.

        Args:
            exit_node: Name of the exit proxy node

        Returns:
            YAML string with proxy chain or None
        """
        config = self.get_runtime_config()
        proxies = config.get("proxies", [])

        if not isinstance(proxies, list):
            return None

        # Build chain by following dialer-proxy links
        chain = []
        current_name = exit_node

        while current_name:
            proxy = next(
                (p for p in proxies if isinstance(p, dict) and p.get("name") == current_name),
                None
            )
            if not proxy:
                break

            chain.append(proxy)
            current_name = proxy.get("dialer-proxy")

        if not chain:
            return None

        # Reverse to get entry -> exit order
        chain.reverse()

        result = {"proxies": chain}
        return yaml.dump(result, default_flow_style=False, allow_unicode=True)

    def validate_config(self) -> Tuple[bool, str]:
        """
        Validate current runtime configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            config = self.get_runtime_config()

            # Basic structure validation
            if not isinstance(config, dict):
                return False, "Configuration must be a YAML mapping"

            # Check for required fields
            if "proxies" not in config and "proxy-providers" not in config:
                return False, "Configuration must have 'proxies' or 'proxy-providers'"

            # Validate YAML can be serialized
            yaml.dump(config)

            return True, ""

        except yaml.YAMLError as e:
            return False, f"YAML error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"

    def get_clash_info(self) -> ClashInfo:
        """
        Get Clash connection information.

        Returns:
            ClashInfo with connection details
        """
        config = self.get_runtime_config()
        verge = self.config.read_verge()

        # Determine ports - verge overrides take precedence
        mixed_port = verge.verge_mixed_port or config.get("mixed-port", 7890)
        socks_port = verge.verge_socks_port or config.get("socks-port", 7891)
        redir_port = verge.verge_redir_port or config.get("redir-port", 0)
        tproxy_port = verge.verge_tproxy_port or config.get("tproxy-port", 0)

        # External controller
        ec = config.get("external-controller", "127.0.0.1:9090")
        if isinstance(ec, int):
            ec = f"127.0.0.1:{ec}"

        return ClashInfo(
            port=config.get("port", 7890),
            socks_port=socks_port,
            mixed_port=mixed_port,
            redir_port=redir_port,
            tproxy_port=tproxy_port,
            external_controller=ec,
            secret=config.get("secret"),
        )

    def apply_generate_config(self) -> bool:
        """
        Apply and generate configuration to clash config.yaml.

        Returns:
            True if successful
        """
        try:
            config = self.get_runtime_config()
            self.config.write_clash(config)
            return True
        except Exception:
            return False
