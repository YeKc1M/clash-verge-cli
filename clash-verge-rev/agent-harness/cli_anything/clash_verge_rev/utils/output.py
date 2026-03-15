"""
Output formatting utilities for CLI results.

Handles formatting output as JSON or human-readable text.
"""

import json
from typing import Any, Dict, List, Optional, Union


class OutputFormatter:
    """
    Formats CLI output for human or machine consumption.

    Supports:
    - JSON output (--json flag)
    - Human-readable tables and lists
    - Colored output for terminals
    """

    def __init__(self, use_json: bool = False, use_color: Optional[bool] = None):
        """
        Initialize OutputFormatter.

        Args:
            use_json: If True, output as JSON
            use_color: If True, use ANSI colors. Auto-detected if None.
        """
        self.use_json = use_json
        if use_color is None:
            # Auto-detect based on TTY
            import sys
            use_color = sys.stdout.isatty()
        self.use_color = use_color and not use_json

    def output(self, data: Any, success: bool = True, message: Optional[str] = None) -> str:
        """
        Format data for output.

        Args:
            data: Data to format (dict, list, or primitive)
            success: Whether the operation was successful
            message: Optional message to include

        Returns:
            Formatted string
        """
        if self.use_json:
            return self._format_json(data, success, message)
        else:
            return self._format_human(data, success, message)

    def _format_json(self, data: Any, success: bool, message: Optional[str]) -> str:
        """Format as JSON."""
        result = {
            "success": success,
            "data": data if data is not None else {},
        }
        if message:
            result["message"] = message
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _format_human(self, data: Any, success: bool, message: Optional[str]) -> str:
        """Format for human reading."""
        lines = []

        # Status message
        if message:
            if success:
                lines.append(self._green(f"✓ {message}"))
            else:
                lines.append(self._red(f"✗ {message}"))
        elif not success:
            lines.append(self._red("✗ Operation failed"))

        # Data formatting
        if data is not None:
            formatted_data = self._format_data_human(data)
            if formatted_data:
                lines.append(formatted_data)

        return "\n".join(lines)

    def _format_data_human(self, data: Any, indent: int = 0) -> str:
        """Recursively format data for human output."""
        if data is None:
            return ""

        if isinstance(data, dict):
            return self._format_dict(data, indent)

        if isinstance(data, list):
            return self._format_list(data, indent)

        return str(data)

    def _format_dict(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary as key-value pairs."""
        if not data:
            return ""

        lines = []
        prefix = "  " * indent

        # Calculate column width for alignment
        max_key_len = max(len(str(k)) for k in data.keys()) if data else 0

        for key, value in data.items():
            key_str = self._cyan(f"{key}:")
            key_str = f"{prefix}{key_str:<{max_key_len + 3}}"

            if isinstance(value, (dict, list)) and value:
                lines.append(f"{key_str}")
                nested = self._format_data_human(value, indent + 1)
                if nested:
                    lines.append(nested)
            else:
                value_str = self._format_value(value)
                lines.append(f"{key_str} {value_str}")

        return "\n".join(lines)

    def _format_list(self, data: List[Any], indent: int = 0) -> str:
        """Format list items."""
        if not data:
            return ""

        lines = []
        prefix = "  " * indent

        for i, item in enumerate(data):
            if isinstance(item, dict):
                # Check if it's a simple item that can be on one line
                if len(item) <= 3 and all(not isinstance(v, (dict, list)) for v in item.values()):
                    parts = [f"{k}={self._format_value(v)}" for k, v in item.items()]
                    lines.append(f"{prefix}- {', '.join(parts)}")
                else:
                    lines.append(f"{prefix}- Item {i + 1}:")
                    nested = self._format_data_human(item, indent + 1)
                    if nested:
                        lines.append(nested)
            else:
                value_str = self._format_value(item)
                lines.append(f"{prefix}- {value_str}")

        return "\n".join(lines)

    def _format_value(self, value: Any) -> str:
        """Format a single value with type-appropriate coloring."""
        if value is None:
            return self._dim("null")

        if isinstance(value, bool):
            return self._green("true") if value else self._red("false")

        if isinstance(value, (int, float)):
            return self._yellow(str(value))

        if isinstance(value, str):
            return value

        return str(value)

    def _green(self, text: str) -> str:
        """Green text."""
        return f"\033[32m{text}\033[0m" if self.use_color else text

    def _red(self, text: str) -> str:
        """Red text."""
        return f"\033[31m{text}\033[0m" if self.use_color else text

    def _yellow(self, text: str) -> str:
        """Yellow text."""
        return f"\033[33m{text}\033[0m" if self.use_color else text

    def _cyan(self, text: str) -> str:
        """Cyan text."""
        return f"\033[36m{text}\033[0m" if self.use_color else text

    def _dim(self, text: str) -> str:
        """Dim text."""
        return f"\033[2m{text}\033[0m" if self.use_color else text


def format_output(data: Any, json_mode: bool = False, success: bool = True, message: Optional[str] = None) -> str:
    """
    Convenience function to format output.

    Args:
        data: Data to format
        json_mode: If True, output as JSON
        success: Whether operation was successful
        message: Optional message

    Returns:
        Formatted string
    """
    formatter = OutputFormatter(use_json=json_mode)
    return formatter.output(data, success, message)
