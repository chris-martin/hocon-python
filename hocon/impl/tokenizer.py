from .. import exceptions, ConfigOrigin, ConfigSyntax


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
    return u'\u0000' <= c and c <= u'\u001F' \
        or u'\u007F' <= c and c <= u'\u009F'


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
                    line_origin(base_origin, line_number),
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
        self.tokens = []  # Queue<Token>
        self.tokens.add(Tokens.START)
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
                return self.input.read()  # todo - this should read a character from the input
            except Exception as e:
                raise exceptions.IO(origin, "read error: " + e.message, e)
        else:
            c = self.buffer.pop()
            return c

    private void putBack(int c) {
        if (buffer.size() > 2) {
            throw new ConfigException.BugOrBroken(
                    "bug: putBack() three times, undesirable look-ahead");
        }
        buffer.push(c);
    }

    static boolean isWhitespace(int c) {
        return ConfigImplUtil.isWhitespace(c);
    }

    static boolean isWhitespaceNotNewline(int c) {
        return c != '\n' && ConfigImplUtil.isWhitespace(c);
    }

    private boolean startOfComment(int c) {
        if (c == -1) {
            return false;
        } else {
            if (allowComments) {
                if (c == '#') {
                    return true;
                } else if (c == '/') {
                    int maybeSecondSlash = nextCharRaw();
                    // we want to predictably NOT consume any chars
                    putBack(maybeSecondSlash);
                    if (maybeSecondSlash == '/') {
                        return true;
                    } else {
                        return false;
                    }
                } else {
                    return false;
                }
            } else {
                return false;
            }
        }
    }

    // get next char, skipping non-newline whitespace
    private int nextCharAfterWhitespace(WhitespaceSaver saver) {
        for (;;) {
            int c = nextCharRaw();

            if (c == -1) {
                return -1;
            } else {
                if (isWhitespaceNotNewline(c)) {
                    saver.add(c);
                    continue;
                } else {
                    return c;
                }
            }
        }
    }

    private ProblemException problem(String message) {
        return problem("", message, null);
    }

    private ProblemException problem(String what, String message) {
        return problem(what, message, null);
    }

    private ProblemException problem(String what, String message, boolean suggestQuotes) {
        return problem(what, message, suggestQuotes, null);
    }

    private ProblemException problem(String what, String message, Throwable cause) {
        return problem(lineOrigin, what, message, cause);
    }

    private ProblemException problem(String what, String message, boolean suggestQuotes,
            Throwable cause) {
        return problem(lineOrigin, what, message, suggestQuotes, cause);
    }

    private static ProblemException problem(ConfigOrigin origin, String what,
            String message,
            Throwable cause) {
        return problem(origin, what, message, false, cause);
    }

    private static ProblemException problem(ConfigOrigin origin, String what, String message,
            boolean suggestQuotes, Throwable cause) {
        if (what == null || message == null)
            throw new ConfigException.BugOrBroken(
                    "internal error, creating bad ProblemException");
        return new ProblemException(Tokens.newProblem(origin, what, message, suggestQuotes,
                cause));
    }

    private static ProblemException problem(ConfigOrigin origin, String message) {
        return problem(origin, "", message, null);
    }

    private static ConfigOrigin lineOrigin(ConfigOrigin baseOrigin,
            int lineNumber) {
        return ((SimpleConfigOrigin) baseOrigin).setLineNumber(lineNumber);
    }

    // ONE char has always been consumed, either the # or the first /, but
    // not both slashes
    private Token pullComment(int firstChar) {
        if (firstChar == '/') {
            int discard = nextCharRaw();
            if (discard != '/')
                throw new ConfigException.BugOrBroken("called pullComment but // not seen");
        }

        StringBuilder sb = new StringBuilder();
        for (;;) {
            int c = nextCharRaw();
            if (c == -1 || c == '\n') {
                putBack(c);
                return Tokens.newComment(lineOrigin, sb.toString());
            } else {
                sb.appendCodePoint(c);
            }
        }
    }

    // chars JSON allows a number to start with
    static final String firstNumberChars = "0123456789-";
    // chars JSON allows to be part of a number
    static final String numberChars = "0123456789eE+-.";
    // chars that stop an unquoted string
    static final String notInUnquotedText = "$\"{}[]:=,+#`^?!@*&\\";

    // The rules here are intended to maximize convenience while
    // avoiding confusion with real valid JSON. Basically anything
    // that parses as JSON is treated the JSON way and otherwise
    // we assume it's a string and let the parser sort it out.
    private Token pullUnquotedText() {
        ConfigOrigin origin = lineOrigin;
        StringBuilder sb = new StringBuilder();
        int c = nextCharRaw();
        while (true) {
            if (c == -1) {
                break;
            } else if (notInUnquotedText.indexOf(c) >= 0) {
                break;
            } else if (isWhitespace(c)) {
                break;
            } else if (startOfComment(c)) {
                break;
            } else {
                sb.appendCodePoint(c);
            }

            // we parse true/false/null tokens as such no matter
            // what is after them, as long as they are at the
            // start of the unquoted token.
            if (sb.length() == 4) {
                String s = sb.toString();
                if (s.equals("true"))
                    return Tokens.newBoolean(origin, true);
                else if (s.equals("null"))
                    return Tokens.newNull(origin);
            } else if (sb.length() == 5) {
                String s = sb.toString();
                if (s.equals("false"))
                    return Tokens.newBoolean(origin, false);
            }

            c = nextCharRaw();
        }

        // put back the char that ended the unquoted text
        putBack(c);

        String s = sb.toString();
        return Tokens.newUnquotedText(origin, s);
    }

    private Token pullNumber(int firstChar) throws ProblemException {
        StringBuilder sb = new StringBuilder();
        sb.appendCodePoint(firstChar);
        boolean containedDecimalOrE = false;
        int c = nextCharRaw();
        while (c != -1 && numberChars.indexOf(c) >= 0) {
            if (c == '.' || c == 'e' || c == 'E')
                containedDecimalOrE = true;
            sb.appendCodePoint(c);
            c = nextCharRaw();
        }
        // the last character we looked at wasn't part of the number, put it
        // back
        putBack(c);
        String s = sb.toString();
        try {
            if (containedDecimalOrE) {
                // force floating point representation
                return Tokens.newDouble(lineOrigin, Double.parseDouble(s), s);
            } else {
                // this should throw if the integer is too large for Long
                return Tokens.newLong(lineOrigin, Long.parseLong(s), s);
            }
        } catch (NumberFormatException e) {
            // not a number after all, see if it's an unquoted string.
            for (char u : s.toCharArray()) {
                if (notInUnquotedText.indexOf(u) >= 0)
                    throw problem(asString(u), "Reserved character '" + asString(u)
                                  + "' is not allowed outside quotes", true /* suggestQuotes */);
            }
            // no evil chars so we just decide this was a string and
            // not a number.
            return Tokens.newUnquotedText(lineOrigin, s);
        }
    }

    private void pullEscapeSequence(StringBuilder sb) throws ProblemException {
        int escaped = nextCharRaw();
        if (escaped == -1)
            throw problem("End of input but backslash in string had nothing after it");

        switch (escaped) {
        case '"':
            sb.append('"');
            break;
        case '\\':
            sb.append('\\');
            break;
        case '/':
            sb.append('/');
            break;
        case 'b':
            sb.append('\b');
            break;
        case 'f':
            sb.append('\f');
            break;
        case 'n':
            sb.append('\n');
            break;
        case 'r':
            sb.append('\r');
            break;
        case 't':
            sb.append('\t');
            break;
        case 'u': {
            // kind of absurdly slow, but screw it for now
            char[] a = new char[4];
            for (int i = 0; i < 4; ++i) {
                int c = nextCharRaw();
                if (c == -1)
                    throw problem("End of input but expecting 4 hex digits for \\uXXXX escape");
                a[i] = (char) c;
            }
            String digits = new String(a);
            try {
                sb.appendCodePoint(Integer.parseInt(digits, 16));
            } catch (NumberFormatException e) {
                throw problem(digits, String.format(
                        "Malformed hex digits after \\u escape in string: '%s'", digits), e);
            }
        }
            break;
        default:
            throw problem(
                    asString(escaped),
                    String.format(
                            "backslash followed by '%s', this is not a valid escape sequence (quoted strings use JSON escaping, so use double-backslash \\\\ for literal backslash)",
                            asString(escaped)));
        }
    }

    private void appendTripleQuotedString(StringBuilder sb) throws ProblemException {
        // we are after the opening triple quote and need to consume the
        // close triple
        int consecutiveQuotes = 0;
        for (;;) {
            int c = nextCharRaw();

            if (c == '"') {
                consecutiveQuotes += 1;
            } else if (consecutiveQuotes >= 3) {
                // the last three quotes end the string and the others are
                // kept.
                sb.setLength(sb.length() - 3);
                putBack(c);
                break;
            } else {
                consecutiveQuotes = 0;
                if (c == -1)
                    throw problem("End of input but triple-quoted string was still open");
                else if (c == '\n') {
                    // keep the line number accurate
                    lineNumber += 1;
                    lineOrigin = origin.setLineNumber(lineNumber);
                }
            }

            sb.appendCodePoint(c);
        }
    }

    private Token pullQuotedString() throws ProblemException {
        // the open quote has already been consumed
        StringBuilder sb = new StringBuilder();
        int c = '\0'; // value doesn't get used
        do {
            c = nextCharRaw();
            if (c == -1)
                throw problem("End of input but string quote was still open");

            if (c == '\\') {
                pullEscapeSequence(sb);
            } else if (c == '"') {
                // end the loop, done!
            } else if (Character.isISOControl(c)) {
                throw problem(asString(c), "JSON does not allow unescaped " + asString(c)
                        + " in quoted strings, use a backslash escape");
            } else {
                sb.appendCodePoint(c);
            }
        } while (c != '"');

        // maybe switch to triple-quoted string, sort of hacky...
        if (sb.length() == 0) {
            int third = nextCharRaw();
            if (third == '"') {
                appendTripleQuotedString(sb);
            } else {
                putBack(third);
            }
        }

        return Tokens.newString(lineOrigin, sb.toString());
    }

    private Token pullPlusEquals() throws ProblemException {
        // the initial '+' has already been consumed
        int c = nextCharRaw();
        if (c != '=') {
            throw problem(asString(c), "'+' not followed by =, '" + asString(c)
                    + "' not allowed after '+'", true /* suggestQuotes */);
        }
        return Tokens.PLUS_EQUALS;
    }

    private Token pullSubstitution() throws ProblemException {
        // the initial '$' has already been consumed
        ConfigOrigin origin = lineOrigin;
        int c = nextCharRaw();
        if (c != '{') {
            throw problem(asString(c), "'$' not followed by {, '" + asString(c)
                    + "' not allowed after '$'", true /* suggestQuotes */);
        }

        boolean optional = false;
        c = nextCharRaw();
        if (c == '?') {
            optional = true;
        } else {
            putBack(c);
        }

        WhitespaceSaver saver = new WhitespaceSaver();
        List<Token> expression = new ArrayList<Token>();

        Token t;
        do {
            t = pullNextToken(saver);

            // note that we avoid validating the allowed tokens inside
            // the substitution here; we even allow nested substitutions
            // in the tokenizer. The parser sorts it out.
            if (t == Tokens.CLOSE_CURLY) {
                // end the loop, done!
                break;
            } else if (t == Tokens.END) {
                throw problem(origin,
                        "Substitution ${ was not closed with a }");
            } else {
                Token whitespace = saver.check(t, origin, lineNumber);
                if (whitespace != null)
                    expression.add(whitespace);
                expression.add(t);
            }
        } while (true);

        return Tokens.newSubstitution(origin, optional, expression);
    }

    private Token pullNextToken(WhitespaceSaver saver) throws ProblemException {
        int c = nextCharAfterWhitespace(saver);
        if (c == -1) {
            return Tokens.END;
        } else if (c == '\n') {
            // newline tokens have the just-ended line number
            Token line = Tokens.newLine(lineOrigin);
            lineNumber += 1;
            lineOrigin = origin.setLineNumber(lineNumber);
            return line;
        } else {
            Token t;
            if (startOfComment(c)) {
                t = pullComment(c);
            } else {
                switch (c) {
                case '"':
                    t = pullQuotedString();
                    break;
                case '$':
                    t = pullSubstitution();
                    break;
                case ':':
                    t = Tokens.COLON;
                    break;
                case ',':
                    t = Tokens.COMMA;
                    break;
                case '=':
                    t = Tokens.EQUALS;
                    break;
                case '{':
                    t = Tokens.OPEN_CURLY;
                    break;
                case '}':
                    t = Tokens.CLOSE_CURLY;
                    break;
                case '[':
                    t = Tokens.OPEN_SQUARE;
                    break;
                case ']':
                    t = Tokens.CLOSE_SQUARE;
                    break;
                case '+':
                    t = pullPlusEquals();
                    break;
                default:
                    t = null;
                    break;
                }

                if (t == null) {
                    if (firstNumberChars.indexOf(c) >= 0) {
                        t = pullNumber(c);
                    } else if (notInUnquotedText.indexOf(c) >= 0) {
                        throw problem(asString(c), "Reserved character '" + asString(c)
                                + "' is not allowed outside quotes", true /* suggestQuotes */);
                    } else {
                        putBack(c);
                        t = pullUnquotedText();
                    }
                }
            }

            if (t == null)
                throw new ConfigException.BugOrBroken(
                        "bug: failed to generate next token");

            return t;
        }
    }

    private void queueNextToken() throws ProblemException {
        Token t = pullNextToken(whitespaceSaver);
        Token whitespace = whitespaceSaver.check(t, origin, lineNumber);
        if (whitespace != null)
            tokens.add(whitespace);

        tokens.add(t);
    }

    @Override
    public boolean hasNext() {
        return !tokens.isEmpty();
    }

    @Override
    public Token next() {
        Token t = tokens.remove();
        if (tokens.isEmpty() && t != Tokens.END) {
            try {
                queueNextToken();
            } catch (ProblemException e) {
                tokens.add(e.problem());
            }
            if (tokens.isEmpty())
                throw new ConfigException.BugOrBroken(
                        "bug: tokens queue should not be empty here");
        }
        return t;
    }

    @Override
    public void remove() {
        throw new UnsupportedOperationException(
                "Does not make sense to remove items from token stream");
    }
}
