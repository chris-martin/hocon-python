import json
import os

from .. import exceptions


def render_json_string(s):
    """
    public static String renderJsonString(String s)
    """
    return json.dumps(s)


def render_string_unquoted_if_possible(s):
    """
    static String renderStringUnquotedIfPossible(String s)
    """

    # this can quote unnecessarily as long as it never fails to quote when
    # necessary
    if len(s) == 0:
        return render_json_string(s)

    # if it starts with a hyphen or number, we have to quote
    # to ensure we end up with a string and not a number
    first = s[0]
    if first.isdigit() or first == '-':
        return render_json_string(s)

    if s.startswith("include") or s.startswith("true") \
            or s.startswith("false") or s.startswith("null") or "//" in s:
        return render_json_string(s)

    # only unquote if it's pure alphanumeric
    if not all(c.isalnum() or c == '-' for c in s):
        return render_json_string(s)

    return s


def is_whitespace(c):
    """
    static boolean isWhitespace(int codepoint)
    """

    # try to hit the most common ASCII ones first, then the nonbreaking
    # spaces that Java brokenly leaves out of isWhitespace.

    # u202F is the BOM, see
    # http://www.unicode.org/faq/utf_bom.html#BOM
    # we just accept it as a zero-width nonbreaking space.

    return c in u' \n\u00A0\u2007\u202F\uFEFF' or c.isspace()


def unicode_trim(s):
    """
    public static String unicodeTrim(String s)
    """

    # this is dumb because it looks like there aren't any whitespace
    # characters that need surrogate encoding. But, points for
    # pedantic correctness! It's future-proof or something.
    # String.trim() actually is broken, since there are plenty of
    # non-ASCII whitespace characters.
    length = len(s)
    if length == 0:
        return s

    start = 0
    while start < length:
        c = s[start]
        if is_whitespace(c):
            start += 1
        else:
            break

    end = length
    while end > start:
        c = s[end - 1]
        if is_whitespace(c):
            end -= 1
        else:
            break

    return s[start:end]


def extract_initializer_error(e):
    """
    public static ConfigException extractInitializerError(
        ExceptionInInitializerError e)
    """
    cause = getattr(e, 'cause', None)
    if isinstance(cause, exceptions.ConfigException):
        return cause
    else:
        raise e


def join_path(*elements):
    """
    public static String joinPath(String... elements)
    public static String joinPath(List<String> elements)
    """
    return os.path.join(*elements)


def split_path(path):
    """
    public static List<String> splitPath(String path)
    """
    return os.path.split(path)
