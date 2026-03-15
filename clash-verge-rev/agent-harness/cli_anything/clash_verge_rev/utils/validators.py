"""
Input validation utilities.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse


def validate_profile_name(name: str) -> Tuple[bool, str]:
    """
    Validate a profile name.

    Args:
        name: Profile name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Profile name cannot be empty"

    if len(name) > 100:
        return False, "Profile name too long (max 100 characters)"

    # Allow alphanumeric, spaces, hyphens, underscores, dots
    if not re.match(r"^[\w\s\-_.]+$", name):
        return False, "Profile name contains invalid characters"

    return True, ""


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate a URL for profile import.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            return False, "URL must have a scheme (http:// or https://)"

        if parsed.scheme not in ("http", "https"):
            return False, "URL scheme must be http or https"

        if not parsed.netloc:
            return False, "URL must have a host"

        return True, ""

    except Exception as e:
        return False, f"Invalid URL: {e}"


def validate_port(port: int) -> Tuple[bool, str]:
    """
    Validate a port number.

    Args:
        port: Port number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(port, int):
        return False, "Port must be an integer"

    if port < 1 or port > 65535:
        return False, "Port must be between 1 and 65535"

    # Check for reserved ports
    if port < 1024:
        return True, "Warning: Port < 1024 requires elevated privileges"

    return True, ""


def validate_delay_test_url(url: Optional[str]) -> Tuple[bool, str]:
    """
    Validate a delay test URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return True, ""  # Empty is valid (uses default)

    return validate_url(url)


def validate_yaml_content(content: str) -> Tuple[bool, str]:
    """
    Validate YAML content.

    Args:
        content: YAML content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content:
        return False, "Content cannot be empty"

    try:
        import yaml
        yaml.safe_load(content)
        return True, ""
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {e}"
    except ImportError:
        return True, ""  # Can't validate without PyYAML
