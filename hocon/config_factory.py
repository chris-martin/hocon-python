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


    /**
     * Converts a Java {@link java.util.Properties} object to a
     * {@link ConfigObject} using the rules documented in the <a
     * href="https://github.com/typesafehub/config/blob/master/HOCON.md">HOCON
     * spec</a>. The keys in the <code>Properties</code> object are split on the
     * period character '.' and treated as paths. The values will all end up as
     * string values. If you have both "a=foo" and "a.b=bar" in your properties
     * file, so "a" is both the object containing "b" and the string "foo", then
     * the string value is dropped.
     *
     * <p>
     * If you want to have <code>System.getProperties()</code> as a
     * ConfigObject, it's better to use the {@link #systemProperties()} method
     * which returns a cached global singleton.
     *
     * @param properties
     *            a Java Properties object
     * @param options
     * @return the parsed configuration
     */
    public static Config parseProperties(Properties properties,
            ConfigParseOptions options) {
        return Parseable.newProperties(properties, options).parse().toConfig();
    }

    public static Config parseProperties(Properties properties) {
        return parseProperties(properties, ConfigParseOptions.defaults());
    }

    public static Config parseReader(Reader reader, ConfigParseOptions options) {
        return Parseable.newReader(reader, options).parse().toConfig();
    }

    public static Config parseReader(Reader reader) {
        return parseReader(reader, ConfigParseOptions.defaults());
    }

    public static Config parseURL(URL url, ConfigParseOptions options) {
        return Parseable.newURL(url, options).parse().toConfig();
    }

    public static Config parseURL(URL url) {
        return parseURL(url, ConfigParseOptions.defaults());
    }

    public static Config parseFile(File file, ConfigParseOptions options) {
        return Parseable.newFile(file, options).parse().toConfig();
    }

    public static Config parseFile(File file) {
        return parseFile(file, ConfigParseOptions.defaults());
    }

    /**
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
     *
     * @param fileBasename
     *            a filename with or without extension
     * @param options
     *            parse options
     * @return the parsed configuration
     */
    public static Config parseFileAnySyntax(File fileBasename,
            ConfigParseOptions options) {
        return ConfigImpl.parseFileAnySyntax(fileBasename, options).toConfig();
    }

    public static Config parseFileAnySyntax(File fileBasename) {
        return parseFileAnySyntax(fileBasename, ConfigParseOptions.defaults());
    }

    /**
     * Parses all resources on the classpath with the given name and merges them
     * into a single <code>Config</code>.
     *
     * <p>
     * If the resource name does not begin with a "/", it will have the supplied
     * class's package added to it, in the same way as
     * {@link java.lang.Class#getResource}.
     *
     * <p>
     * Duplicate resources with the same name are merged such that ones returned
     * earlier from {@link ClassLoader#getResources} fall back to (have higher
     * priority than) the ones returned later. This implies that resources
     * earlier in the classpath override those later in the classpath when they
     * configure the same setting. However, in practice real applications may
     * not be consistent about classpath ordering, so be careful. It may be best
     * to avoid assuming too much.
     *
     * @param klass
     *            <code>klass.getClassLoader()</code> will be used to load
     *            resources, and non-absolute resource names will have this
     *            class's package added
     * @param resource
     *            resource to look up, relative to <code>klass</code>'s package
     *            or absolute starting with a "/"
     * @param options
     *            parse options
     * @return the parsed configuration
     */
    public static Config parseResources(Class<?> klass, String resource,
            ConfigParseOptions options) {
        return Parseable.newResources(klass, resource, options).parse()
                .toConfig();
    }

    public static Config parseResources(Class<?> klass, String resource) {
        return parseResources(klass, resource, ConfigParseOptions.defaults());
    }

    /**
     * Parses classpath resources with a flexible extension. In general, this
     * method has the same behavior as
     * {@link #parseFileAnySyntax(File,ConfigParseOptions)} but for classpath
     * resources instead, as in {@link #parseResources}.
     *
     * <p>
     * There is a thorny problem with this method, which is that
     * {@link java.lang.ClassLoader#getResources} must be called separately for
     * each possible extension. The implementation ends up with separate lists
     * of resources called "basename.conf" and "basename.json" for example. As a
     * result, the ideal ordering between two files with different extensions is
     * unknown; there is no way to figure out how to merge the two lists in
     * classpath order. To keep it simple, the lists are simply concatenated,
     * with the same syntax priorities as
     * {@link #parseFileAnySyntax(File,ConfigParseOptions) parseFileAnySyntax()}
     * - all ".conf" resources are ahead of all ".json" resources which are
     * ahead of all ".properties" resources.
     *
     * @param klass
     *            class which determines the <code>ClassLoader</code> and the
     *            package for relative resource names
     * @param resourceBasename
     *            a resource name as in {@link java.lang.Class#getResource},
     *            with or without extension
     * @param options
     *            parse options (class loader is ignored in favor of the one
     *            from klass)
     * @return the parsed configuration
     */
    public static Config parseResourcesAnySyntax(Class<?> klass, String resourceBasename,
            ConfigParseOptions options) {
        return ConfigImpl.parseResourcesAnySyntax(klass, resourceBasename,
                options).toConfig();
    }

    public static Config parseResourcesAnySyntax(Class<?> klass, String resourceBasename) {
        return parseResourcesAnySyntax(klass, resourceBasename, ConfigParseOptions.defaults());
    }

    /**
     * Parses all resources on the classpath with the given name and merges them
     * into a single <code>Config</code>.
     *
     * <p>
     * This works like {@link java.lang.ClassLoader#getResource}, not like
     * {@link java.lang.Class#getResource}, so the name never begins with a
     * slash.
     *
     * <p>
     * See {@link #parseResources(Class,String,ConfigParseOptions)} for full
     * details.
     *
     * @param loader
     *            will be used to load resources by setting this loader on the
     *            provided options
     * @param resource
     *            resource to look up
     * @param options
     *            parse options (class loader is ignored)
     * @return the parsed configuration
     */
    public static Config parseResources(ClassLoader loader, String resource,
            ConfigParseOptions options) {
        return parseResources(resource, options.setClassLoader(loader));
    }

    public static Config parseResources(ClassLoader loader, String resource) {
        return parseResources(loader, resource, ConfigParseOptions.defaults());
    }

    /**
     * Parses classpath resources with a flexible extension. In general, this
     * method has the same behavior as
     * {@link #parseFileAnySyntax(File,ConfigParseOptions)} but for classpath
     * resources instead, as in
     * {@link #parseResources(ClassLoader,String,ConfigParseOptions)}.
     *
     * <p>
     * {@link #parseResourcesAnySyntax(Class,String,ConfigParseOptions)} differs
     * in the syntax for the resource name, but otherwise see
     * {@link #parseResourcesAnySyntax(Class,String,ConfigParseOptions)} for
     * some details and caveats on this method.
     *
     * @param loader
     *            class loader to look up resources in, will be set on options
     * @param resourceBasename
     *            a resource name as in
     *            {@link java.lang.ClassLoader#getResource}, with or without
     *            extension
     * @param options
     *            parse options (class loader ignored)
     * @return the parsed configuration
     */
    public static Config parseResourcesAnySyntax(ClassLoader loader, String resourceBasename,
            ConfigParseOptions options) {
        return ConfigImpl.parseResourcesAnySyntax(resourceBasename, options.setClassLoader(loader))
                .toConfig();
    }

    public static Config parseResourcesAnySyntax(ClassLoader loader, String resourceBasename) {
        return parseResourcesAnySyntax(loader, resourceBasename, ConfigParseOptions.defaults());
    }

    /**
     * Like {@link #parseResources(ClassLoader,String,ConfigParseOptions)} but
     * uses thread's current context class loader if none is set in the
     * ConfigParseOptions.
     */
    public static Config parseResources(String resource, ConfigParseOptions options) {
        ConfigParseOptions withLoader = ensureClassLoader(options, "parseResources");
        return Parseable.newResources(resource, withLoader).parse().toConfig();
    }

    /**
     * Like {@link #parseResources(ClassLoader,String)} but uses thread's
     * current context class loader.
     */
    public static Config parseResources(String resource) {
        return parseResources(resource, ConfigParseOptions.defaults());
    }

    /**
     * Like
     * {@link #parseResourcesAnySyntax(ClassLoader,String,ConfigParseOptions)}
     * but uses thread's current context class loader.
     */
    public static Config parseResourcesAnySyntax(String resourceBasename, ConfigParseOptions options) {
        return ConfigImpl.parseResourcesAnySyntax(resourceBasename, options).toConfig();
    }

    /**
     * Like {@link #parseResourcesAnySyntax(ClassLoader,String)} but uses
     * thread's current context class loader.
     */
    public static Config parseResourcesAnySyntax(String resourceBasename) {
        return parseResourcesAnySyntax(resourceBasename, ConfigParseOptions.defaults());
    }

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
