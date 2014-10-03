"""
FIXME the way the subclasses of Token are private with static isFoo and
accessors is kind of ridiculous.
"""

from .. import exceptions, ConfigOrigin, ConfigValueType

from .ResolveStatus import ResolveStatus
from .Token import Token
from .TokenType import TokenType


class Value(Token):

    def __init__(self, value):
        """
        :param value: AbstractConfigValue
        """
        super(Value, self).__init__(
            token_type=TokenType.value,
            origin=value.origin(),
        )
        self._value = value

    def value(self):
        """
        :return: AbstractConfigValue
        """
        return self._value

    def __unicode__(self):
        v = self.value()
        if v.resolve_status() == ResolveStatus.resolved:
            return "'" + v.unwrapped() + "' (" + v.value_type().name() + ")"
        else:
            return "'<unresolved value>' (" + v.value_type().name() + ")"

    def __repr__(self):
        return "Value(" + unicode(self) + ")"

    def _key(self):
        return super(Value, self)._key() + (self.value(),)


class Line(Token):

    def __init__(self, origin):
        """
        :param origin: ConfigOrigin
        """
        super(Line, self).__init__(
            token_type=TokenType.newline,
            origin=origin,
        )

    def __unicode__(self):
        return "'\\n'@" + self.line_number()

    def __repr__(self):
        return "Line(" + unicode(self) + ")"

    def _key(self):
        return super(Line, self)._key() + (self.line_number(),)


class UnquotedText(Token):
    """
    This is not a Value, because it requires special processing.
    """

    def __init__(self, origin, s):
        """
        :param origin: ConfigOrigin
        :param s: String
        """
        super(UnquotedText, self).__init__(
            token_type=TokenType.unquoted_text,
            origin=origin,
        )
        self._value = s

    def value(self):
        """
        :return: String
        """
        return self._value

    def __unicode__(self):
        return "'" + self.value() + "'"

    def __repr__(self):
        return "UnquotedText(" + unicode(self) + ")"

    def _key(self):
        return super(UnquotedText, self)._key() + (self.value(),)


class Problem(Token):

    def __init__(self, origin, what, message, suggest_quotes, cause):
        """
        :param origin: ConfigOrigin
        :param what: String
        :param message: String
        :param suggest_quotes: boolean
        :param cause: Throwable
        """
        super(Problem, self).__init__(
            token_type=TokenType.problem,
            origin=origin,
        )
        self._what = what
        self._message = message
        self._suggest_quotes = suggest_quotes
        self._cause = cause

    def what(self):
        """
        :return: String
        """
        return self._what

    def message(self):
        """
        :return: String
        """
        return self._message

    def suggest_quotes(self):
        """
        :return: boolean
        """
        return self._suggest_quotes

    def cause(self):
        """
        :return: Throwable
        """
        return self._cause

    def __unicode__(self):
        return '\'' + self.what() + '\'' + " (" + self.message() + ")"

    def __repr__(self):
        return "Problem(" + unicode(self) + ")"

    def _key(self):
        return super(Problem, self)._key() + (
            self.what(),
            self.message(),
            self.suggest_quotes(),
            self.cause(),
        )


class Comment(Token):

    def __init__(self, origin, text):
        """
        :param origin: ConfigOrigin
        :param text: String
        """
        super(Comment, self).__init__(
            token_type=TokenType.comment,
            origin=origin,
        )
        self._text = text

    def text(self):
        """
        :return: String
        """
        return self._text

    def __unicode__(self):
        return "'#" + text + "' (COMMENT)"

    def __repr__(self):
        return "Comment(" + unicode(self) + ")"

    def _key(self):
        return super(Comment, self)._key() + (self.text(),)


class Substitution(Token):
    """
    This is not a Value, because it requires special processing
    """

    def __init__(self, origin, optional, expression):
        """
        :param origin: ConfigOrigin
        :param optional: boolean
        :param expression: List<Token>
        """
        super(Substitution, self).__init__(
            token_type=TokenType.substitution,
            origin=origin,
        )
        self._optional = optional
        self._value = expression

    def optional(self):
        """
        :return: boolean
        """
        return self._optional

    def value(self):
        """
        :return: List<Token>
        """
        return self._value

    def __unicode__(self):
        return "'${" + ''.join([map(unicode, self.value())]) + "}'"

    def __repr__(self):
        return "Substitution(" + unicode(self) + ")"

    def _key(self):
        return super(Substitution, self)._key() + (self.value(),)


def is_value(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, Value)


def get_value(token):
    """
    :param token: Token
    :return: AbstractConfigValue
    """
    if isinstance(token, Value):
        return token.value()
    else:
        raise exceptions.BugOrBroken(
            "tried to get value of non-value token " + token)


def is_value_with_type(t, value_type):
    """
    :param t: Token
    :param value_type: ConfigValueType
    :return: boolean
    """
    return is_value(t) and get_value(t).value_type() == value_type


def is_newline(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, Line)


def is_problem(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, Problem)


def get_problem_what(token):
    """
    :param token: Token
    :return: String
    """
    if isinstance(token, Problem):
        return token.what()
    else:
        raise exceptions.BugOrBroken(
            "tried to get problem what from " + token)


def get_problem_message(token):
    """
    :param token: Token
    :return: String
    """
    if isinstance(token, Problem):
        return token.message()
    else:
        raise exceptions.BugOrBroken(
            "tried to get problem message from " + token)


def get_problem_suggest_quotes(token):
    """
    :param token: Token
    :return: boolean
    """
    if isinstance(token, Problem):
        return token.suggest_quotes()
    else:
        raise exceptions.BugOrBroken(
            "tried to get problem suggestQuotes from " + token)


def get_problem_cause(token):
    """
    :param token: Token
    :return: Throwable
    """
    if isinstance(token, Problem):
        return token.cause()
    else:
        raise exceptions.BugOrBroken(
            "tried to get problem cause from " + token)


def is_comment(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, Comment)


def get_comment_text(token):
    """
    :param token: Token
    :return: String
    """
    if isinstance(token, Comment):
        return token.text()
    else:
        raise exceptions.BugOrBroken(
            "tried to get comment text from " + token)


def is_unquoted_text(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, UnquotedText)


def get_unquoted_text(token):
    """
    :param token: Token
    :return: String
    """
    if isinstance(token, UnquotedText):
        return token.value()
    else:
        raise exceptions.BugOrBroken(
            "tried to get unquoted text from " + token)


def is_substitution(token):
    """
    :param token: Token
    :return: boolean
    """
    return isinstance(token, Substitution)


def get_substitution_path_expression(token):
    """
    :param token: Token
    :return: List<Token>
    """
    if isinstance(token, Substitution):
        return token.value()
    else:
        raise exceptions.BugOrBroken(
            "tried to get substitution from " + token)


def get_substitution_optinal(token):
    """
    :param token: Token
    :return: boolean
    """
    if isinstance(token, Substitution):
        return token.optional()
    else:
        raise exceptions.BugOrBroken(
            "tried to get substitution optionality from " + token)


START = Token.new_without_origin(TokenType.start, "start of file")
END = Token.new_without_origin(TokenType.end, "end of file")
COMMA = Token.new_without_origin(TokenType.comma, "','")
EQUALS = Token.new_without_origin(TokenType.equals, "'='")
COLON = Token.new_without_origin(TokenType.colon, "':'")
OPEN_CURLY = Token.new_without_origin(TokenType.open_curly, "'{'")
CLOSE_CURLY = Token.new_without_origin(TokenType.close_curly, "'}'")
OPEN_SQUARE = Token.new_without_origin(TokenType.open_square, "'['")
CLOSE_SQUARE = Token.new_without_origin(TokenType.close_square, "']'")
PLUS_EQUALS = Token.new_without_origin(TokenType.plus_equals, "'+='")


def new_line(origin):
    """
    :param origin: ConfigOrigin
    :return: Token
    """
    return Line(origin)


def new_problem(origin, what, message, suggest_quotes, cause):
    """
    :param origin: ConfigOrigin
    :param what: String
    :param message: String
    :param suggest_quotes: boolean
    :param cause: Throwable
    :return: Token
    """
    return Problem(origin=origin, what=what, message=message,
                   suggest_quotes=suggest_quotes, cause=cause)


def new_comment(origin, text):
    """
    :param origin: ConfigOrigin
    :param text: String
    :return: Token
    """
    return Comment(origin=origin, text=text)


def new_unquoted_text(origin, s):
    """
    :param origin: ConfigOrigin
    :param s: String
    :return: Token
    """
    return UnquotedText(origin=origin, s=s)


def new_substitution(origin, optional, expression):
    """
    :param origin: ConfigOrigin
    :param optional: boolean
    :param expression: List<Token>
    :return: Token
    """
    return Substitution(origin=origin, optional=optional,
                        expression=expression)


def new_value(value):
    """
    :param value: AbstractConfigValue
    :return: Token
    """
    return Value(value)


def new_string(origin, value):
    """
    :param origin: ConfigOrigin
    :param value: String
    :return: Token
    """
    return ConfigString(origin=origin, value=value)


def new_int(origin, value, original_text):
    """
    :param origin: ConfigOrigin
    :param value: int
    :param original_text: String
    :return: Token
    """
    return new_value(ConfigNumber.new_number(
        origin=origin, value=value, original_text=original_text))


def new_double(origin, value, original_text):
    """
    :param origin: ConfigOrigin
    :param value: double
    :param original_text: String
    :return: Token
    """
    return new_value(ConfigNumber.new_number(
        origin=origin, value=value, original_text=original_text))


def new_long(origin, value, original_text):
    """
    :param origin: ConfigOrigin
    :param value: long
    :param original_text: String
    :return: Token
    """
    return new_value(ConfigNumber.new_number(
        origin=origin, value=value, original_text=original_text))


def new_null(origin):
    """
    :param origin: ConfigOrigin
    :return: token
    """
    return new_value(ConfigNull(origin))


def new_boolean(origin, value):
    """
    :param origin: ConfigOrigin
    :param value: boolean
    :return: Token
    """
    return new_value(ConfigBoolean(origin=origin, value=value))
