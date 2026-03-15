"""
Runtime configuration management for Clash Verge Rev.

Manages runtime config which is the merged/enhanced configuration
that gets applied to the Clash core.
"""

import os
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

import yaml

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

    def _get_pid_file(self) -> Path:
        """Get path to the PID file for tracking mihomo process."""
        return self.config.get_config_dir() / "mihomo.pid"

    def _find_mihomo_binary(self) -> Optional[str]:
        """
        Find mihomo binary in common locations.

        Returns:
            Path to mihomo binary or None if not found
        """
        # Check common binary names and paths
        binary_names = ["mihomo", "clash", "clash-meta"]
        search_paths = os.environ.get("PATH", "").split(os.pathsep)

        # Add common install locations
        common_locations = [
            "/usr/local/bin",
            "/usr/bin",
            "/opt/homebrew/bin",
            "/opt/local/bin",
            str(Path.home() / ".local/bin"),
            str(Path.home() / "bin"),
        ]
        search_paths.extend(common_locations)

        for name in binary_names:
            for path in search_paths:
                binary_path = Path(path) / name
                if binary_path.exists() and os.access(binary_path, os.X_OK):
                    return str(binary_path)

        # Try which command as fallback
        for name in binary_names:
            try:
                result = subprocess.run(
                    ["which", name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception:
                pass

        return None

    def start_mihomo(self, binary_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Start the mihomo core process.

        Args:
            binary_path: Optional path to mihomo binary. If not provided, will search PATH.

        Returns:
            Tuple of (success, message)
        """
        # Check if already running
        pid_file = self._get_pid_file()
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                if os.path.exists(f"/proc/{pid}") or self._is_process_running(pid):
                    return False, f"Mihomo already running (PID: {pid})"
            except (ValueError, OSError):
                pass
            # Stale PID file, remove it
            pid_file.unlink(missing_ok=True)

        # Find binary
        mihomo_path = binary_path or self._find_mihomo_binary()
        if not mihomo_path:
            return False, "Mihomo binary not found. Install mihomo or provide path with --binary"

        # Generate config first
        if not self.apply_generate_config():
            return False, "Failed to generate configuration"

        clash_config_path = self.config.clash_path()
        if not clash_config_path.exists():
            return False, f"Config file not found: {clash_config_path}"

        try:
            # Start mihomo process
            log_dir = self.config.get_logs_dir()
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "mihomo.log"

            with open(log_file, "a") as log:
                # Write start marker
                log.write(f"\n--- Started at {datetime.now().isoformat()} ---\n")
                log.flush()

                process = subprocess.Popen(
                    [mihomo_path, "-f", str(clash_config_path)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )

            # Save PID
            pid_file.write_text(str(process.pid))

            # Quick check if process started
            import time
            time.sleep(0.5)
            if process.poll() is not None:
                # Process exited quickly
                pid_file.unlink(missing_ok=True)
                return False, "Mihomo process exited immediately. Check logs for errors."

            return True, f"Mihomo started (PID: {process.pid})"

        except Exception as e:
            return False, f"Failed to start mihomo: {e}"

    def stop_mihomo(self) -> Tuple[bool, str]:
        """
        Stop the mihomo core process.

        Returns:
            Tuple of (success, message)
        """
        pid_file = self._get_pid_file()

        if not pid_file.exists():
            # Try to find and kill by process name as fallback
            killed = self._kill_by_name()
            if killed:
                return True, "Mihomo stopped (found by process name)"
            return False, "Mihomo not running (no PID file)"

        try:
            pid = int(pid_file.read_text().strip())
        except (ValueError, OSError) as e:
            pid_file.unlink(missing_ok=True)
            return False, f"Invalid PID file: {e}"

        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)

            # Wait for process to terminate
            import time
            for _ in range(10):
                if not self._is_process_running(pid):
                    break
                time.sleep(0.5)
            else:
                # Force kill if still running
                os.kill(pid, signal.SIGKILL)

            pid_file.unlink(missing_ok=True)
            return True, f"Mihomo stopped (PID: {pid})"

        except ProcessLookupError:
            # Process already gone
            pid_file.unlink(missing_ok=True)
            return True, "Mihomo already stopped"
        except PermissionError:
            return False, f"Permission denied to stop process {pid}"
        except Exception as e:
            return False, f"Failed to stop mihomo: {e}"

    def get_mihomo_status(self) -> Tuple[bool, Optional[int], str]:
        """
        Get mihomo process status.

        Returns:
            Tuple of (is_running, pid, status_message)
        """
        pid_file = self._get_pid_file()

        if not pid_file.exists():
            return False, None, "Not running"

        try:
            pid = int(pid_file.read_text().strip())
            if self._is_process_running(pid):
                return True, pid, f"Running (PID: {pid})"
            else:
                # Stale PID file
                pid_file.unlink(missing_ok=True)
                return False, None, "Not running (stale PID file removed)"
        except (ValueError, OSError):
            pid_file.unlink(missing_ok=True)
            return False, None, "Not running (invalid PID file)"

    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    def _kill_by_name(self) -> bool:
        """Try to kill mihomo process by name (fallback)."""
        try:
            for name in ["mihomo", "clash", "clash-meta"]:
                result = subprocess.run(
                    ["pkill", "-f", name],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return True
        except Exception:
            pass
        return False
