import collections


class ConfigResolveOptions(collections.namedtuple('ConfigResolveOptions',
        ('use_system_environment', 'allow_unresolved'))):
    """
    A set of options related to resolving substitutions. Substitutions use the
    <code>${foo.bar}</code> syntax and are documented in the <a
    href="https://github.com/typesafehub/config/blob/master/HOCON.md">HOCON</a>
    spec.
    <p>
    Typically this class would be used with the method
    {@link Config#resolve(ConfigResolveOptions)}.
    <p>
    This object is immutable, so the "setters" return a new object.
    <p>
    Here is an example of creating a custom {@code ConfigResolveOptions}:

    <pre>
        ConfigResolveOptions options = ConfigResolveOptions.defaults()
            .setUseSystemEnvironment(false)
    </pre>
    <p>
    In addition to {@link ConfigResolveOptions#defaults}, there's a prebuilt
    {@link ConfigResolveOptions#noSystem} which avoids looking at any system
    environment variables or other external system information. (Right now,
    environment variables are the only example.)

    :param use_system_environment: boolean
        Whether the options enable use of system environment variables.
        True to resolve substitutions falling back to environment variables.

    :param allow_unresolved: boolean
        By default, unresolved substitutions are an error. If unresolved
        substitutions are allowed, then a future attempt to use the unresolved
        value may fail, but {@link Config#resolve(ConfigResolveOptions)} itself
        will not throw. True to silently ignore unresolved substitutions.
    """

    @classmethod
    def defaults(cls):
        """
        Returns the default resolve options. By default the system environment
        will be used and unresolved substitutions are not allowed.

        @return the default resolve options
        """
        return ConfigResolveOptions(
            use_system_environment=True,
            allow_unresolved=False,
        )

    @classmethod
    def no_system(cls):
        """
        Returns resolve options that disable any reference to "system" data
        (currently, this means environment variables).

        @return the resolve options with env variables disabled
        """
        return ConfigResolveOptions.defaults() \
            .set_use_system_environment(False)

    def set_use_system_environment(self, value):
        """
        Returns options with use of environment variables set to the given value.

        :param value: boolean
            true to resolve substitutions falling back to environment variables.
        :return: ConfigResolveOptions
        """
        return self._replace(use_system_environment=value)

    def set_allow_unresolved(self, value):
        """
        Returns options with "allow unresolved" set to the given value. By
        default, unresolved substitutions are an error. If unresolved
        substitutions are allowed, then a future attempt to use the unresolved
        value may fail, but {@link Config#resolve(ConfigResolveOptions)} itself
        will now throw.

        :param value: boolean
            true to silently ignore unresolved substitutions.
        :return: ConfigResolveOptions
        @since 1.2.0
        """
        return self._replace(allow_unresolved=value)
