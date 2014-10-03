from .. import ConfigIncluder, ConfigIncluderFile, ConfigIncluderURL, \
    ConfigIncluderClasspath


class FullIncluder(ConfigIncluder, ConfigIncluderFile, ConfigIncluderURL,
            ConfigIncluderClasspath):
    pass
