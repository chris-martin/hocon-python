from enum import Enum


class ConfigValueType(Enum('ConfigValueType', (
    'object', 'list', 'number', 'boolean', 'null', 'string'
))):
    """
    The type of a configuration value (following the <a
    href="http://json.org">JSON</a> type schema).
    """
