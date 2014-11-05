from .. import exceptions, ConfigOrigin, ConfigSyntax
from . import tokens, Tokens, util
from .TokenType import TokenType


# this exception should not leave this file
class ProblemException(Exception):

    def __init__(self, problem):
        """
        :param problem: Token
        """
        self.problem = problem


def is_iso_control_character(c):
    """
    A character is considered to be an ISO control character if its code is in
    the range '\u0000' through '\u001F' or in the range '\u007F' through '\u009F'.
    http://docs.oracle.com/javase/7/docs/api/java/lang/Character.html#isISOControl(int)
    """
    return (u'\u0000' <= c <= u'\u001F') or (u'\u007F' <= c <= u'\u009F')


def as_string(c):
    """
    :param c: character
    :return: String
    """
    if c == '\n':
        return "newline"
    elif c == '\t':
        return "tab"
    elif c == u"\u0003":
        return "end of file"
    elif is_iso_control_character(c):
        return "control character " + hex(ord(c))
    else:
        return c


def tokenize(origin, input, flavor):
    """
    Tokenizes a Reader. Does not close the reader; you have to arrange to do
    that after you're done with the returned iterator.

    :param origin: ConfigOrigin
    :param input: Reader
    :param flavor: ConfigSyntax
    :return: Iterator<Token>
    """
    return TokenIterator(origin, input, flavor != ConfigSyntax.json)


def is_simple_value(t):
    """
    :param t: Token
    :return: boolean
    """
    return Tokens.is_substitution(t) or Tokens.is_unquoted_text(t) \
        or Tokens.is_value(t)


def is_whitespace_not_newline(c):
    """
    :param c: character
    :return: boolean
    """
    return c != '\n' and util.is_whitespace(c)


# chars JSON allows a number to start with
first_number_chars = "0123456789-"

# chars JSON allows to be part of a number
number_chars = "0123456789eE+-."

# chars that stop an unquoted string
not_in_unquoted_text = "$\"{}[]:=,+#`^?!@*&\\"


class WhitespaceSaver(object):
    """
    Attributes:

        whitespace: StringBuilder
            Has to be saved inside value concatenations,

        last_token_was_simple_value: boolean
            May need to value-concat with next value,
    """

    def __init__(self):
        self.whitespace = ''
        self.last_token_was_simple_value = False

    def add(self, c):
        if self.last_token_was_simple_value:
            self.whitespace += c

    def check(self, t, base_origin, line_number):
        """
        :param t: Token
        :param base_origin: ConfigOrigin
        :param line_number: int
        :return: Token
        """
        if is_simple_value(t):
            return self.next_is_a_simple_value(base_origin, line_number)
        else:
            self.next_is_not_a_simple_value()
            return None

    def next_is_not_a_simple_value(self):
        """
        Called if the next token is not a simple value;
        discards any whitespace we were saving between simple values.
        """
        self.last_token_was_simple_value = False
        self.whitespace = ''

    def next_is_a_simple_value(self, base_origin, line_number):
        """
        Called if the next token IS a simple value,
        so creates a whitespace token if the previous token also was.

        :param base_origin: ConfigOrigin
        :param line_number: int
        :return: Token
        """
        if self.last_token_was_simple_value:
            # Need to save whitespace between the two so
            # the parser has the option to concatenate it.
            if len(self.whitespace) > 0:
                t = Tokens.new_unquoted_text(
                    base_origin.set_line_number(line_number),
                    unicode(self.whitespace))
                self.whitespace = ''  # reset
                return t
            else:
                # self.last_token_was_simple_value = True still
                return None
        else:
            self.last_token_was_simple_value = True
            self.whitespace = ''
            return None


class TokenIterator(object):

    def __init__(self, origin, input, allow_comments):
        """
        :param origin: ConfigOrigin
        :param input: Reader
        :param allow_comments: boolean
        """

        self.origin = origin  # SimpleConfigOrigin
        self.input = input
        self.allow_comments = allow_comments
        self.buffer = []  # LinkedList<Integer>
        self.line_number = 1  # nonfinal
        self.line_origin = origin.set_line_number(line_number)  # nonfinal
        self.tokens = [Tokens.START]  # Queue<Token>
        self.whitespace_saver = WhitespaceSaver()

    def next_char_raw(self):
        """
        This should ONLY be called from nextCharSkippingComments
        or when inside a quoted string, or when parsing a sequence
        like ${ or +=, everything else should use nextCharSkippingComments().

        :return: int
        """
        if len(self.buffer) == 0:
            try:
                return self.input.read()
            except Exception as e:
                raise exceptions.IO(origin, "read error: " + e.message, e)
        else:
            c = self.buffer.pop()
            return c

    def put_back(self, c):
        """
        :param c: character
        """
        if len(self.buffer) > 2:
            raise exceptions.BugOrBroken(
                "bug: putBack() three times, undesirable look-ahead")
        self.buffer.push(c)

    def start_of_comment(self, c):
        """
        :param c: character
        :return: boolean
        """
        if c is None:  # todo - is None the file.read() equivalent of codepoint -1?
            return False
        if not allowComments:
            return False
        if c == '#':
            return True
        if c != '/':
            return False
        maybe_second_slash = self.next_char_raw()
        # we want to predictably NOT consume any chars
        self.put_back(maybe_second_slash)
        return maybe_second_slash == '/'

    def next_char_after_whitespace(self, saver):
        """
        get next char, skipping non-newline whitespace

        :param saver: WhitespaceSaver
        :return: character
        """
        while True:
            c = self.next_char_raw()
            if c is None:
                return None  # todo - is None the file.read() equivalent of codepoint -1?
            if util.is_whitespace_not_newline(c):
                saver.add(c)
                continue
            return c

    def problem(self, message, what="", origin=None, cause=None,
                suggest_quotes=False):
        """
        :param message: String
        :param what: String
        :param origin: ConfigOrigin
        :param cause: Throwable
        :param suggest_quotes: boolean
        :return: ProblemException
        """
        if origin is None:
            origin = self.line_origin
        if (what is None) or (message is None):
            raise exceptions.BugOrBroken(
                "internal error, creating bad ProblemException")
        return ProblemException(tokens.new_problem(
            origin=origin, what=what, message=message,
            suggest_quotes=suggest_quotes, cause=cause))

    def pull_comment(self, first_char):
        """
        ONE char has always been consumed, either the # or the first /, but
        not both slashes

        :param first_char: character
        :return: Token
        """
        if firstChar == '/':
            discard = self.next_char_raw()
            if (discard != '/'):
                raise exception.BugOrBroken("called pullComment but // not seen")

        s = ''
        while True:
            c = self.next_char_raw()
            if c == -1 or c == '\n':
                self.put_back(c)
                return Tokens.new_comment(origin=self.line_origin, text=s)
            s += c

    def pull_unquoted_text(self):
        """
        The rules here are intended to maximize convenience while
        avoiding confusion with real valid JSON. Basically anything
        that parses as JSON is treated the JSON way and otherwise
        we assume it's a string and let the parser sort it out.

        :return: Token
        """
        origin = self.line_rigin
        s = ''
        c = self.next_char_raw()
        while True:
            if c is None:  # todo - is None the file.read() equivalent of codepoint -1?
                break
            if not_in_unquoted_text.index(c) >= 0:
                break
            if util.is_whitespace(c):
                break
            if self.start_of_comment(c):
                break
            s += c

            # we parse true/false/null tokens as such no matter
            # what is after them, as long as they are at the
            # start of the unquoted token.
            if len(s) == 4:
                if s == "true":
                    return tokens.new_boolean(origin=origin, value=True)
                if s == "null":
                    return tokens.new_null(origin=origin)
            elif len(s) == 5:
                if s == "false":
                    return tokens.new_boolean(origin=origin, value=False)

            c = self.next_char_raw()

        # put back the char that ended the unquoted text
        self.put_back(c)

        return tokens.new_unquoted_text(origin=origin, s=s)

    def pull_number(self, first_char):
        """
        :param first_char: character
        :return: Token
        :raises ProblemException:
        """
        s = first_char
        contained_decimal_or_e = False
        c = self.next_char_raw()
        while (c is not None) and (c in number_chars):  # todo - is None the file.read() equivalent of codepoint -1?
            if c in '.eE':
                contained_decimal_or_e = True
            s += c
            c = self.next_char_raw()

        # the last character we looked at wasn't part of the number, put it back
        self.put_back(c)

        try:
            if contained_decimal_or_e:
                # force floating point representation
                return tokens.new_double(
                    origin=self.line_origin, value=float(s), original_text=s)
            else:
                return tokens.new_int(
                    origin=self.line_origin, value=int(s), original_text=s)

        except ValueError:
            # not a number after all, see if it's an unquoted string.
            for u in s:
                if u in not_in_unquoted_text:
                    raise self.problem(
                        what=u,
                        message="Reserved character '{}' is not allowed "
                                "outside quotes".format(u),
                        suggest_quotes=True,
                    )
            # no evil chars so we just decide this was a string and not a number.
            return tokens.new_unquoted_text(origin=self.line_origin, s=s)

    def pull_escape_sequence(self):
        """
        :return: string
        :raises ProblemException:
        """
        escaped = self.next_char_raw()
        if escaped is None:  # todo - is None the file.read() equivalent of codepoint -1?
            raise self.problem(message="End of input but backslash "
                                       "in string had nothing after it")

        if escaped in '"\\/':
            return escaped

        if escaped == 'b':
            return '\b'
        if escaped == 'f':
            return '\f'
        if escaped == 'n':
            return '\n'
        if escaped == 'r':
            return '\r'
        if escaped == 't':
            return '\t'

        if escaped == 'u':
            digits = ''
            for _ in range(4):
                c = self.next_char_raw()
                if c is None:
                    raise self.problem(message="End of input but expecting 4 "
                                               "hex digits for \\uXXXX escape")
                digits += c

            try:
                return eval('u"\\u{}"'.format(s))  # todo - this is terrible
            except Exception as e:
                raise self.problem(
                    what=digits,
                    message="Malformed hex digits after \\u escape in string: '{}'".format(digits),
                    cause=e
                )
        raise self.problem(
            what=escaped,
            message="backslash followed by '{}', this is not a valid escape "
                    "sequence (quoted strings use JSON escaping, so use "
                    "double-backslash \\\\ for literal backslash)".format(escaped))

    def pull_triple_quoted_string(self):
        """
        we are after the opening triple quote and need to consume the
        close triple

        :return: string
        :raises ProblemException:
        """
        s = ''
        consecutive_quotes = 0
        while True:
            c = self.next_char_raw()

            if c == '"':
                consecutive_quotes += 1
            elif consecutive_quotes >= 3:
                # the last three quotes end the string and the others are kept.
                s = s[:-3]
                self.put_back(c)
                break
            else:
                consecutive_quotes = 0
                if c is None:  # todo - is None the file.read() equivalent of codepoint -1?
                    raise self.problem(
                        message="End of input but triple-quoted string "
                                "was still open"
                    )
                if c == '\n':
                    # keep the line number accurate
                    self.line_number += 1
                    line_origin = origin.set_line_number(self.line_number)

            s += c

        return s

    def pull_quoted_string(self):
        """
        the open quote has already been consumed

        :return: Token
        :raises ProblemException:
        """

        s = ''

        while True:
            c = self.next_char_raw()
            if c is None:  # todo - is None the file.read() equivalent of codepoint -1?
                raise self.problem(message="End of input but string "
                                           "quote was still open")

            if c == '\\':
                s += self.pull_escape_sequence()
            elif c == '"':
                break
            elif is_iso_control_character(c):
                raise self.problem(
                    what=c,
                    message="JSON does not allow unescaped {} in quoted "
                            "strings, use a backslash escape".format(c))
            else:
                s += c

        # maybe switch to triple-quoted string, sort of hacky...
        if len(s) == 0:
            third = self.next_char_raw()
            if third == '"':
                s += self.pull_triple_quoted_string()
            else:
                self.put_back(third)

        return tokens.new_string(origin=self.line_origin, value=s)

    def pull_plus_equals(self):
        """
        the initial '+' has already been consumed

        :return: Token
        :raises ProblemException:
        """
        c = self.next_char_raw()
        if c != '=':
            raise self.problem(
                what=c,
                message="'+' not followed by =, '{}' not allowed after '+'".format(c),
                suggest_quotes=True)

        return TokenType.plus_equals

    def pull_substitution(self):
        """
        the initial '$' has already been consumed

        :return: Token
        :raises ProblemException:
        """
        origin = self.line_origin
        c = self.next_char_raw()
        if c != '{':
            raise self.problem(
                what=c,
                message="'$' not followed by {, '{}' not allowed after '$'".format(c),
                suggest_quotes=True)

        c = self.next_char_raw()
        optional = c == '?'
        if not optional:
            self.put_back(c)

        saver = WhitespaceSaver()
        expression = []  # List<Token>

        while True:
            t = self.pull_next_token(saver)

            # note that we avoid validating the allowed tokens inside
            # the substitution here; we even allow nested substitutions
            # in the tokenizer. The parser sorts it out.
            if t == Tokens.CLOSE_CURLY:
                break
            elif t == Tokens.END:
                raise self.problem(
                    origin=origin,
                    message="Substitution ${ was not closed with a }")
            else:
                whitespace = saver.check(
                    t=t, base_origin=origin, line_number=self.line_number)
                if whitespace is not None:
                    expression.append(whitespace)
                expression.append(t)

        return tokens.new_substitution(
            origin=origin, optional=optional, expression=expression)

    def pull_next_token(self, saver):
        """
        :param saver: WhitespaceSaver
        :return: Token
        :raises ProblemException:
        """
        c = self.next_char_after_whitespace(saver)
        if c is None:  # todo - is None the file.read() equivalent of codepoint -1?
            return Tokens.END

        if c == '\n':
            # newline tokens have the just-ended line number
            line = tokens.new_line(origin=self.line_origin)
            self.line_number += 1
            self.line_origin = origin.set_line_number(self.line_number)
            return line

        t = None
        if self.start_of_comment(c):
            t = self.pull_comment(c)
        else:
            if c == '"':
                t = self.pull_quoted_string()
            elif c == '$':
                t = self.pull_substitution()
            elif c == ':':
                t = Tokens.COLON
            elif c == ',':
                t = Tokens.COMMA
            elif c == '=':
                t = Tokens.EQUALS
            elif c == '{':
                t = Tokens.OPEN_CURLY
            elif c == '}':
                t = Tokens.CLOSE_CURLY
            elif c == '[':
                t = Tokens.OPEN_SQUARE
            elif c == ']':
                t = Tokens.CLOSE_SQUARE
            elif c == '+':
                t = self.pull_plus_equals()

            if t is None:
                if c in first_number_chars:
                    t = self.pull_number(c)
                elif c in not_in_unquoted_text:
                    raise self.problem(
                        what=c,
                        message="Reserved character '{}' is not allowed outside quotes",
                        suggest_quotes=True)
                else:
                    self.put_back(c)
                    t = self.pull_unquoted_text()

        if t is None:
            raise exceptions.BugOrBroken("bug: failed to generate next token")

        return t

    def queue_next_token(self):
        """
        :raises ProblemException:
        """
        t = self.pull_next_token(self.whitespace_saver)
        whitespace = self.whitespace_saver.check(
            t=t, base_origin=self.origin, line_number=self.line_number)
        if whitespace is not None:
            self.tokens.append(whitespace)

        self.tokens.append(t)

    # todo should ``has_next`` and ``next`` implement python's iterator protocol instead?

    def has_next(self):
        """
        :return: boolean
        """
        return len(self.tokens) != 0

    def next(self):
        """
        :return: Token
        """
        (t, self.tokens) = (self.tokens[0], self.tokens[1:])  # todo is there a better way to do a queue?

        if (not self.has_next()) and (t != Tokens.END):
            try:
                self.queue_next_token()
            except ProblemException as e:
                tokens.append(e.problem)
            if not self.has_next():
                raise exceptions.BugOrBroken(
                    "bug: tokens queue should not be empty here");

        return t
