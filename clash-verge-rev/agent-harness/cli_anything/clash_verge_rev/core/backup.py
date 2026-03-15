"""
Backup management for Clash Verge Rev.

Creates and restores local backups of configuration files.
"""

import os
import shutil
import tarfile
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import zipfile

from .config import ConfigManager


@dataclass
class BackupFile:
    """Represents a backup file."""
    filename: str
    path: Path
    size: int
    created: datetime
    is_valid: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "path": str(self.path),
            "size": self.size,
            "size_human": self._format_size(self.size),
            "created": self.created.isoformat(),
            "created_human": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "is_valid": self.is_valid,
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class BackupError(Exception):
    """Base exception for backup errors."""
    pass


class BackupNotFoundError(BackupError):
    """Raised when a backup file is not found."""
    pass


class BackupManager:
    """
    Manages local backups of Clash Verge Rev configuration.

    Creates timestamped backups containing:
    - verge.yaml
    - profiles.yaml
    - config.yaml
    - Profile files in profiles/
    - DNS config if present
    """

    BACKUP_PREFIX = "clash-verge-rev-backup"

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize BackupManager.

        Args:
            config_manager: ConfigManager instance. Creates new if not provided.
        """
        self.config = config_manager or ConfigManager()
        self.backup_dir = self.config.get_backup_dir()

    def _generate_backup_filename(self) -> str:
        """Generate a timestamped backup filename with microsecond for uniqueness."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{self.BACKUP_PREFIX}-{timestamp}.zip"

    def create_backup(self) -> BackupFile:
        """
        Create a new backup of all configuration files.

        Returns:
            BackupFile with backup details

        Raises:
            BackupError: If backup creation fails
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        filename = self._generate_backup_filename()
        backup_path = self.backup_dir / filename

        try:
            # Create zip archive
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
                config_dir = self.config.get_config_dir()

                # Add main config files
                for config_file in [
                    self.config.VERGE_CONFIG,
                    self.config.PROFILE_YAML,
                    self.config.CLASH_CONFIG,
                    self.config.DNS_CONFIG,
                ]:
                    file_path = config_dir / config_file
                    if file_path.exists():
                        zf.write(file_path, config_file)

                # Add profiles directory
                profiles_dir = self.config.get_profiles_dir()
                if profiles_dir.exists():
                    for profile_file in profiles_dir.iterdir():
                        if profile_file.is_file():
                            arcname = f"profiles/{profile_file.name}"
                            zf.write(profile_file, arcname)

            stat = backup_path.stat()
            return BackupFile(
                filename=filename,
                path=backup_path,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_mtime),
            )

        except Exception as e:
            # Clean up partial backup
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Failed to create backup: {e}") from e

    def list_backups(self) -> List[BackupFile]:
        """
        List all available backups.

        Returns:
            List of BackupFile objects sorted by creation time (newest first)
        """
        if not self.backup_dir.exists():
            return []

        backups = []
        for file_path in self.backup_dir.iterdir():
            if file_path.is_file() and file_path.name.startswith(self.BACKUP_PREFIX):
                try:
                    stat = file_path.stat()
                    backups.append(BackupFile(
                        filename=file_path.name,
                        path=file_path,
                        size=stat.st_size,
                        created=datetime.fromtimestamp(stat.st_mtime),
                    ))
                except (OSError, ValueError):
                    # Skip invalid files
                    continue

        # Sort by creation time (newest first)
        backups.sort(key=lambda b: b.created, reverse=True)
        return backups

    def get_backup(self, filename: str) -> BackupFile:
        """
        Get a specific backup by filename.

        Args:
            filename: Name of the backup file

        Returns:
            BackupFile object

        Raises:
            BackupNotFoundError: If backup doesn't exist
        """
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise BackupNotFoundError(f"Backup not found: {filename}")

        stat = backup_path.stat()
        return BackupFile(
            filename=filename,
            path=backup_path,
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_mtime),
        )

    def delete_backup(self, filename: str) -> bool:
        """
        Delete a backup file.

        Args:
            filename: Name of the backup file to delete

        Returns:
            True if deleted successfully

        Raises:
            BackupNotFoundError: If backup doesn't exist
        """
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise BackupNotFoundError(f"Backup not found: {filename}")

        backup_path.unlink()
        return True

    def restore_backup(self, filename: str, force: bool = False) -> bool:
        """
        Restore configuration from a backup.

        Args:
            filename: Name of the backup file to restore
            force: If True, overwrite existing files without prompting

        Returns:
            True if restored successfully

        Raises:
            BackupNotFoundError: If backup doesn't exist
            BackupError: If restoration fails
        """
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise BackupNotFoundError(f"Backup not found: {filename}")

        # Create a backup of current state first (unless force)
        if not force:
            try:
                self.create_backup()
            except BackupError:
                # Continue even if pre-backup fails
                pass

        try:
            with zipfile.ZipFile(backup_path, "r") as zf:
                config_dir = self.config.get_config_dir()

                # Extract files
                for member in zf.namelist():
                    target_path = config_dir / member

                    # Ensure parent directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Extract file
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)

            return True

        except Exception as e:
            raise BackupError(f"Failed to restore backup: {e}") from e

    def import_backup(self, source_path: Path) -> str:
        """
        Import an external backup file into the backup directory.

        Args:
            source_path: Path to the external backup file

        Returns:
            Filename of the imported backup

        Raises:
            BackupError: If import fails
        """
        if not source_path.exists():
            raise BackupNotFoundError(f"Source file not found: {source_path}")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate new filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.BACKUP_PREFIX}-imported-{timestamp}.zip"
        target_path = self.backup_dir / filename

        try:
            shutil.copy2(source_path, target_path)
            return filename
        except Exception as e:
            raise BackupError(f"Failed to import backup: {e}") from e

    def export_backup(self, filename: str, destination: Path) -> bool:
        """
        Export a backup to an external location.

        Args:
            filename: Name of the backup to export
            destination: Destination path for the export

        Returns:
            True if exported successfully

        Raises:
            BackupNotFoundError: If backup doesn't exist
            BackupError: If export fails
        """
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise BackupNotFoundError(f"Backup not found: {filename}")

        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, destination)
            return True
        except Exception as e:
            raise BackupError(f"Failed to export backup: {e}") from e

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backups, keeping only the specified number.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            Number of backups removed
        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            return 0

        removed = 0
        for backup in backups[keep_count:]:
            try:
                backup.path.unlink()
                removed += 1
            except OSError:
                pass

        return removed
