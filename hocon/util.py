"""
Contains static utility methods.
"""

from .impl import util as impl_util


def quote_string(s):
    """
    public static String quoteString(String s)

     * Quotes and escapes a string, as in the JSON specification.
     *
     * @param s
     *            a string
     * @return the string quoted and escaped
     */
    """
    return impl_util.render_json_string(s)


def join_path(*elements):
    """
    public static String joinPath(String... elements)

     * Converts a list of keys to a path expression, by quoting the path
     * elements as needed and then joining them separated by a period. A path
     * expression is usable with a {@link Config}, while individual path
     * elements are usable with a {@link ConfigObject}.
     * <p>
     * See the overview documentation for {@link Config} for more detail on path
     * expressions vs. keys.
     * 
     * @param elements
     *            the keys in the path
     * @return a path expression
     * @throws ConfigException
     *             if there are no elements

    public static String joinPath(List<String> elements)

     * Converts a list of strings to a path expression, by quoting the path
     * elements as needed and then joining them separated by a period. A path
     * expression is usable with a {@link Config}, while individual path
     * elements are usable with a {@link ConfigObject}.
     * <p>
     * See the overview documentation for {@link Config} for more detail on path
     * expressions vs. keys.
     * 
     * @param elements
     *            the keys in the path
     * @return a path expression
     * @throws ConfigException
     *             if the list is empty
    """
    return impl_util.join_path(elements)


def split_path(path):
    """
    public static List<String> splitPath(String path)

     * Converts a path expression into a list of keys, by splitting on period
     * and unquoting the individual path elements. A path expression is usable
     * with a {@link Config}, while individual path elements are usable with a
     * {@link ConfigObject}.
     * <p>
     * See the overview documentation for {@link Config} for more detail on path
     * expressions vs. keys.
     * 
     * @param path
     *            a path expression
     * @return the individual keys in the path
     * @throws ConfigException
     *             if the path expression is invalid
    """
    return impl_util.split_path(path)
