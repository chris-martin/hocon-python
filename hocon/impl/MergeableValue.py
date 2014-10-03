from .. import ConfigMergeable


class MergeableValue(ConfigMergeable):
    """
    interface MergeableValue extends ConfigMergeable
    """

    def to_fallback_value(self):
        """
        ConfigValue toFallbackValue();

        Converts a Config to its root object and a ConfigValue to itself.
        """
        raise NotImplementedError
