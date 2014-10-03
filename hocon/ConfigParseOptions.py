import collections


class ConfigParseOptions(collections.nametuple('ConfigParseOptions', (
    'syntax', 'origin_description', 'allow_missing', 'includer'
))):
    """
    A set of options related to parsing.

    <p>
    This object is immutable, so the "setters" return a new object.

    <p>
    Here is an example of creating a custom {@code ConfigParseOptions}:

    <pre>
        ConfigParseOptions options = ConfigParseOptions.defaults()
            .setSyntax(ConfigSyntax.JSON)
            .setAllowMissing(false)
    </pre>

    :param syntax: ConfigSyntax
        The file format. If set to null, try to guess from any available
        filename extension; if guessing fails, assume {@link ConfigSyntax#CONF}.

    :param origin_description: String
        A description for the thing being parsed. In most cases this will be
        set up for you to something like the filename, but if you provide just an
        input stream you might want to improve on it. Set to null to allow the
        library to come up with something automatically. This description is the
        basis for the {@link ConfigOrigin} of the parsed values.

    :param allow_missing: boolean
        Set to false to throw an exception if the item being parsed (for example
        a file) is missing. Set to true to just return an empty document in that
        case.

    :param includer: ConfigIncluder
        A ConfigIncluder which customizes how includes are handled.
    """

    @classmethod
    def defaults(cls):
        """
        :return: ConfigParseOptions
        """
        return ConfigParseOptions(
            syntax=None,
            origin_decription=None,
            allow_missing=True,
            includer=None,
        )

    def set_syntax(self, syntax):
        """
        Set the file format. If set to null, try to guess from any available
        filename extension; if guessing fails, assume {@link ConfigSyntax#CONF}.

        @param syntax
                   a syntax or {@code null} for best guess
        @return options with the syntax set

        :param syntax: ConfigSyntax
        :return: ConfigParseOptions
        """
        return self._replace(syntax=syntax)

    def set_origin_description(self, origin_description):
        """
        Set a description for the thing being parsed. In most cases this will be
        set up for you to something like the filename, but if you provide just an
        input stream you might want to improve on it. Set to null to allow the
        library to come up with something automatically. This description is the
        basis for the {@link ConfigOrigin} of the parsed values.

        @param originDescription
        @return options with the origin description set

        :param origin_description: String
        :return: ConfigParseOptions
        """
        return self._replace(origin_description=origin_description)

    def _with_fallback_origin_description(self, origin_description):
        if self.origin_description is None:
            return self.replace(origin_description=origin_description)
        else:
            return self

    def set_allow_missing(self, allow_missing):
        """
        Set to false to throw an exception if the item being parsed (for example
        a file) is missing. Set to true to just return an empty document in that
        case.

        @param allowMissing
        @return options with the "allow missing" flag set

        :param allow_missing: Boolean
        :return: ConfigParseOptions
        """
        return self._replace(allow_missing=allow_missing)

    def set_includer(self, includer):
        """
        Set a ConfigIncluder which customizes how includes are handled.

        @param includer
        @return new version of the parse options with different includer

        :param includer: ConfigIncluder
        :return: ConfigParseOptions
        """
        return self._replace(includer=includer)

    def prepend_includer(self, includer):
        """
        :param includer: ConfigIncluder
        :return: ConfigParseOptions
        """
        if self.includer is not None:
            return self.set_includer(includer.with_fallback(self.includer))
        else:
            return self.set_includer(includer)

    def append_includer(self, includer):
        """
        :param includer: ConfigIncluder
        :return: ConfigParseOptions
        """
        if self.includer is not None:
            return self.set_includer(self.includer.with_fallback(includer))
        else:
            return self.set_includer(includer)
