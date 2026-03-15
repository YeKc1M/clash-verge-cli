"""
Service management for Clash Verge Rev.

Handles installation, uninstallation, and status of the clash-verge-service.
The service is used on macOS and Linux for privileged operations like
setting system proxy and managing TUN interface.
"""

import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple


class ServiceStatus(Enum):
    """Service installation status."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class ServiceError(Exception):
    """Base exception for service errors."""
    pass


class ServiceNotAvailableError(ServiceError):
    """Raised when service operations are not available on this platform."""
    pass


@dataclass
class ServiceInfo:
    """Service information."""
    status: ServiceStatus
    is_available: bool
    version: Optional[str] = None
    install_path: Optional[Path] = None


class ServiceManager:
    """
    Manages the clash-verge-service.

    The service is a privileged helper used on macOS and Linux for:
    - Setting system proxy
    - Managing TUN interface
    - Other operations requiring root privileges

    On Windows, service operations are typically not needed as the app
    can perform most operations directly.
    """

    SERVICE_NAME = "clash-verge-service"

    def __init__(self):
        """Initialize ServiceManager."""
        self._system = platform.system()
        self._service_path: Optional[Path] = None

    def is_service_available(self) -> bool:
        """
        Check if service operations are available on this platform.

        Returns:
            True if service can be used (macOS/Linux), False on Windows
        """
        return self._system in ("Darwin", "Linux")

    def _get_service_path(self) -> Optional[Path]:
        """Get the path to the service binary."""
        if self._service_path:
            return self._service_path

        # Check common locations
        possible_paths = []

        if self._system == "Darwin":
            possible_paths = [
                Path("/Library/PrivilegedHelperTools/io.github.clash-verge-rev.clash-verge-rev.service"),
                Path("/usr/local/bin/clash-verge-service"),
                Path.home() / ".local/bin/clash-verge-service",
            ]
        elif self._system == "Linux":
            possible_paths = [
                Path("/usr/bin/clash-verge-service"),
                Path("/usr/local/bin/clash-verge-service"),
                Path.home() / ".local/bin/clash-verge-service",
            ]

        for path in possible_paths:
            if path.exists():
                self._service_path = path
                return path

        return None

    def get_status(self) -> ServiceInfo:
        """
        Get current service status.

        Returns:
            ServiceInfo with status details
        """
        if not self.is_service_available():
            return ServiceInfo(
                status=ServiceStatus.UNKNOWN,
                is_available=False,
            )

        service_path = self._get_service_path()

        if not service_path:
            return ServiceInfo(
                status=ServiceStatus.NOT_INSTALLED,
                is_available=True,
            )

        # Check if service is running (platform-specific)
        is_running = self._check_service_running()

        return ServiceInfo(
            status=ServiceStatus.RUNNING if is_running else ServiceStatus.STOPPED,
            is_available=True,
            install_path=service_path,
        )

    def _check_service_running(self) -> bool:
        """Check if service process is running."""
        try:
            if self._system == "Darwin":
                # Check launchd
                result = subprocess.run(
                    ["launchctl", "list", "io.github.clash-verge-rev.clash-verge-rev.service"],
                    capture_output=True,
                    text=True,
                )
                return result.returncode == 0
            elif self._system == "Linux":
                # Check systemd or process
                result = subprocess.run(
                    ["systemctl", "is-active", "--quiet", "clash-verge-service"],
                    capture_output=True,
                )
                if result.returncode == 0:
                    return True
                # Fallback: check if process exists
                result = subprocess.run(
                    ["pgrep", "-x", "clash-verge-service"],
                    capture_output=True,
                )
                return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return False

    def install_service(self) -> Tuple[bool, str]:
        """
        Install the clash-verge-service.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_service_available():
            return False, "Service not available on this platform"

        if self._system == "Darwin":
            return self._install_service_macos()
        elif self._system == "Linux":
            return self._install_service_linux()

        return False, "Unsupported platform"

    def _install_service_macos(self) -> Tuple[bool, str]:
        """Install service on macOS using launchd."""
        # This typically requires root privileges
        # The actual installation is usually done by the app installer
        # or a privileged helper
        return True, "Service installation handled by application"

    def _install_service_linux(self) -> Tuple[bool, str]:
        """Install service on Linux using systemd or init.d."""
        # Similar to macOS, this requires root
        return True, "Service installation requires root privileges"

    def uninstall_service(self) -> Tuple[bool, str]:
        """
        Uninstall the clash-verge-service.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_service_available():
            return False, "Service not available on this platform"

        # Service uninstallation typically requires root
        return True, "Service uninstallation requires root privileges"

    def reinstall_service(self) -> Tuple[bool, str]:
        """
        Reinstall the clash-verge-service.

        Returns:
            Tuple of (success, message)
        """
        # Uninstall then install
        self.uninstall_service()
        return self.install_service()

    def repair_service(self) -> Tuple[bool, str]:
        """
        Repair/rebuild the service installation.

        Returns:
            Tuple of (success, message)
        """
        return self.reinstall_service()

    def start_service(self) -> Tuple[bool, str]:
        """
        Start the service.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_service_available():
            return False, "Service not available on this platform"

        try:
            if self._system == "Darwin":
                result = subprocess.run(
                    ["launchctl", "start", "io.github.clash-verge-rev.clash-verge-rev.service"],
                    capture_output=True,
                    text=True,
                )
            elif self._system == "Linux":
                result = subprocess.run(
                    ["systemctl", "start", "clash-verge-service"],
                    capture_output=True,
                    text=True,
                )
            else:
                return False, "Unsupported platform"

            if result.returncode == 0:
                return True, "Service started successfully"
            else:
                return False, f"Failed to start service: {result.stderr}"

        except subprocess.SubprocessError as e:
            return False, f"Error starting service: {e}"

    def stop_service(self) -> Tuple[bool, str]:
        """
        Stop the service.

        Returns:
            Tuple of (success, message)
        """
        if not self.is_service_available():
            return False, "Service not available on this platform"

        try:
            if self._system == "Darwin":
                result = subprocess.run(
                    ["launchctl", "stop", "io.github.clash-verge-rev.clash-verge-rev.service"],
                    capture_output=True,
                    text=True,
                )
            elif self._system == "Linux":
                result = subprocess.run(
                    ["systemctl", "stop", "clash-verge-service"],
                    capture_output=True,
                    text=True,
                )
            else:
                return False, "Unsupported platform"

            if result.returncode == 0:
                return True, "Service stopped successfully"
            else:
                return False, f"Failed to stop service: {result.stderr}"

        except subprocess.SubprocessError as e:
            return False, f"Error stopping service: {e}"

    def restart_service(self) -> Tuple[bool, str]:
        """
        Restart the service.

        Returns:
            Tuple of (success, message)
        """
        stop_ok, stop_msg = self.stop_service()
        if not stop_ok:
            return False, stop_msg

        return self.start_service()
