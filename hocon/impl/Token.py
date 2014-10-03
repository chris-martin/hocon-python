from .. import exceptions, ConfigOrigin


class Token(object):

    def __init__(self, token_type, origin=None, debug_string=None):
        """
        :param token_type: TokenType
            This is None for singleton tokens like COMMA or OPEN_CURLY.
        :param origin: ConfigOrigin
        :param debug_string: String
        """
        self._token_type = token_type
        self._debug_string = debug_string
        self._origin = origin

    def token_type(self):
        return self._token_type

    def origin(self):
        """
        Code is only supposed to call origin() on token types that are
        expected to have an origin.

        :return: ConfigOrigin
        """
        if self._origin is None:
            raise exceptions.BugOrBroken(
                "tried to get origin from token that doesn't have one: "
                + self)
        return self._origin

    def line_number(self):
        """
        :return: int
        """
        if self._origin is not None:
            return self._origin.line_number()
        else:
            return -1

    def __unicode__(self):
        if self._debug_string is not None:
            return self._debug_string
        else:
            return self._token_type.name()

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "Token(" + unicode(self) + ")"

    def _key(self):
        # origin is deliberately left out
        return (self._token_type,)

    def __eq__(self, other):
        return isinstance(other, Token) and self._key() == other._key()

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._key())
