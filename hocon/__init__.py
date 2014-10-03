"""
An API for loading and using configuration files, see
<a href="https://github.com/typesafehub/config/">the project site</a>
for more information.

Typically you would load configuration with a static method from
{@link com.typesafe.config.ConfigFactory} and then use
it with methods in the {@link com.typesafe.config.Config} interface.
Configuration may be in the form of JSON files,
Java properties, or
<a href="https://github.com/typesafehub/config/blob/master/HOCON.md">HOCON files</a>;
you may also build your own configuration in code or from your own file formats.

An application can simply call {@link com.typesafe.config.ConfigFactory#load()}
and place its configuration in "application.conf" on the classpath.
If you use the default configuration from
{@link com.typesafe.config.ConfigFactory#load()} there's no need to pass a
configuration to your libraries and frameworks, as long as they all default
to this same default, which they should.

Example code
------------

Example application code:
<a href="https://github.com/typesafehub/config/tree/master/examples/java/simple-app/src/main">Java</a> and
<a href="https://github.com/typesafehub/config/tree/master/examples/scala/simple-app/src/main">Scala</a>.

Showing a couple of more special-purpose features, a more complex example:
<a href="https://github.com/typesafehub/config/tree/master/examples/java/complex-app/src/main">Java</a> and
<a href="https://github.com/typesafehub/config/tree/master/examples/scala/complex-app/src/main">Scala</a>.

A library or framework should ship a file "reference.conf" in its jar, and
allow an application to pass in a {@link com.typesafe.config.Config} to be
used for the library. If no {@link com.typesafe.config.Config} is provided,
call {@link com.typesafe.config.ConfigFactory#load()} to get the default one.
Typically a library might offer two constructors, one with a
<code>Config</code> parameter and one which uses
{@link com.typesafe.config.ConfigFactory#load()}.

Example library code:
<a href="https://github.com/typesafehub/config/tree/master/examples/java/simple-lib/src/main">Java</a> and
<a href="https://github.com/typesafehub/config/tree/master/examples/scala/simple-lib/src/main">Scala</a>.

Check out the full
<a href="https://github.com/typesafehub/config/tree/master/examples">examples directory on GitHub</a>.

What else to read:
------------------

The overview documentation for interface {@link com.typesafe.config.Config}.

The <a href="https://github.com/typesafehub/config/blob/master/README.md">README</a>
for the library.

If you want to use <code>.conf</code> files in addition to
<code>.json</code> and <code>.properties</code>, see the
<a href="https://github.com/typesafehub/config/blob/master/README.md">README</a>
for some short examples and the full
<a href="https://github.com/typesafehub/config/blob/master/HOCON.md">HOCON spec</a>
for the long version.
"""
