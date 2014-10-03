"""
Contains static methods for creating {@link Config} instances.

<p>
See also {@link ConfigValueFactory} which contains static methods for
converting Java values into a {@link ConfigObject}. You can then convert a
{@code ConfigObject} into a {@code Config} with {@link ConfigObject#toConfig}.

<p>
The static methods with "load" in the name do some sort of higher-level
operation potentially parsing multiple resources and resolving substitutions,
while the ones with "parse" in the name just create a {@link ConfigValue}
from a resource and nothing else.

<p> You can find an example app and library <a
href="https://github.com/typesafehub/config/tree/master/examples">on
GitHub</a>.  Also be sure to read the <a
href="package-summary.html#package_description">package
overview</a> which describes the big picture as shown in those
examples.
"""

from . import impl


def empty(origin_description=None):
    """
    public static Config empty()

     * Gets an empty configuration. See also {@link #empty(String)} to create an
     * empty configuration with a description, which may improve user-visible
     * error messages.
     *
     * @return an empty configuration

    public static Config empty(String originDescription)

     * Gets an empty configuration with a description to be used to create a
     * {@link ConfigOrigin} for this <code>Config</code>. The description should
     * be very short and say what the configuration is, like "default settings"
     * or "foo settings" or something. (Presumably you will merge some actual
     * settings into this empty config using {@link Config#withFallback}, making
     * the description more useful.)
     *
     * @param originDescription
     *            description of the config
     * @return an empty configuration
    """
    return impl.ConfigImpl.empty_config(origin_description)


def system_environment():
    """
    public static Config systemEnvironment()

     * Gets a <code>Config</code> containing the system's environment variables.
     * This method can return a global immutable singleton.
     *
     * <p>
     * Environment variables are used as fallbacks when resolving substitutions
     * whether or not this object is included in the config being resolved, so
     * you probably don't need to use this method for most purposes. It can be a
     * nicer API for accessing environment variables than raw
     * {@link java.lang.System#getenv(String)} though, since you can use methods
     * such as {@link Config#getInt}.
     *
     * @return system environment variables parsed into a <code>Config</code>
    """
    return impl.ConfigImpl.env_variables_as_config()


def parse_file(f, options=None):
    """
    :param f: a filelike object
    :param options: ConfigParseOptions
    :return: Config
    """
    if options is None:
        options = ConfigParseOptions.defaults()
    return impl.Parseable.new_file(f, options).parse().to_config()


def parse_url(url, options=None):
    """
    :param url: String
    :param options: ConfigParseOptions
    :return: Config
    """
    if options is None:
        options = ConfigParseOptions.defaults()
    return impl.Parseable.new_url(url, options).parse().to_config()


def parse_path(path, options=None):
    """
    :param path: String - filesystem path
    :param options: ConfigParseOptions
    :return: Config
    """
    if options is None:
        options = ConfigParseOptions.defaults()
    return impl.ConfigImpl.parse_path(path, options).to_config()


def parse_path_any_syntax(path_basename, options=None):
    """
     * Parses a file with a flexible extension. If the <code>fileBasename</code>
     * already ends in a known extension, this method parses it according to
     * that extension (the file's syntax must match its extension). If the
     * <code>fileBasename</code> does not end in an extension, it parses files
     * with all known extensions and merges whatever is found.
     *
     * <p>
     * In the current implementation, the extension ".conf" forces
     * {@link ConfigSyntax#CONF}, ".json" forces {@link ConfigSyntax#JSON}, and
     * ".properties" forces {@link ConfigSyntax#PROPERTIES}. When merging files,
     * ".conf" falls back to ".json" falls back to ".properties".
     *
     * <p>
     * Future versions of the implementation may add additional syntaxes or
     * additional extensions. However, the ordering (fallback priority) of the
     * three current extensions will remain the same.
     *
     * <p>
     * If <code>options</code> forces a specific syntax, this method only parses
     * files with an extension matching that syntax.
     *
     * <p>
     * If {@link ConfigParseOptions#getAllowMissing options.getAllowMissing()}
     * is true, then no files have to exist; if false, then at least one file
     * has to exist.

    :param file_basename: String - a filename with or without extension
    :param options: ConfigParseOptions
    :return: Config - the parsed configuration
    """
    if options is None:
        options = ConfigParseOptions.defaults()
    return impl.ConfigImpl.parse_path_any_syntax(path_basename, options) \
        .to_config()


    public static Config parseString(String s, ConfigParseOptions options) {
        return Parseable.newString(s, options).parse().toConfig();
    }

    public static Config parseString(String s) {
        return parseString(s, ConfigParseOptions.defaults());
    }

    /**
     * Creates a {@code Config} based on a {@link java.util.Map} from paths to
     * plain Java values. Similar to
     * {@link ConfigValueFactory#fromMap(Map,String)}, except the keys in the
     * map are path expressions, rather than keys; and correspondingly it
     * returns a {@code Config} instead of a {@code ConfigObject}. This is more
     * convenient if you are writing literal maps in code, and less convenient
     * if you are getting your maps from some data source such as a parser.
     *
     * <p>
     * An exception will be thrown (and it is a bug in the caller of the method)
     * if a path is both an object and a value, for example if you had both
     * "a=foo" and "a.b=bar", then "a" is both the string "foo" and the parent
     * object of "b". The caller of this method should ensure that doesn't
     * happen.
     *
     * @param values
     * @param originDescription
     *            description of what this map represents, like a filename, or
     *            "default settings" (origin description is used in error
     *            messages)
     * @return the map converted to a {@code Config}
     */
    public static Config parseMap(Map<String, ? extends Object> values,
            String originDescription) {
        return ConfigImpl.fromPathMap(values, originDescription).toConfig();
    }

    /**
     * See the other overload of {@link #parseMap(Map, String)} for details,
     * this one just uses a default origin description.
     *
     * @param values
     * @return the map converted to a {@code Config}
     */
    public static Config parseMap(Map<String, ? extends Object> values) {
        return parseMap(values, null);
    }
