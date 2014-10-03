from enum import Enum


class ConfigSyntax(Enum('ConfigSyntax', ('json', 'conf', 'properties'))):
    """
    The syntax of a character stream (<a href="http://json.org">JSON</a>, <a
    href="https://github.com/typesafehub/config/blob/master/HOCON.md">HOCON</a>
    aka ".conf", or <a href=
    "http://download.oracle.com/javase/7/docs/api/java/util/Properties.html#load%28java.io.Reader%29"
    >Java properties</a>).

    Values:

        json
            Pedantically strict <a href="http://json.org">JSON</a> format; no
            comments, no unexpected commas, no duplicate keys in the same object.
            Associated with the <code>.json</code> file extension and
            <code>application/json</code> Content-Type.

        conf
            The JSON-superset <a
            href="https://github.com/typesafehub/config/blob/master/HOCON.md"
            >HOCON</a> format. Associated with the <code>.conf</code> file extension
            and <code>application/hocon</code> Content-Type.

        properties
            Standard <a href=
            "http://download.oracle.com/javase/7/docs/api/java/util/Properties.html#load%28java.io.Reader%29"
            >Java properties</a> format. Associated with the <code>.properties</code>
            file extension and <code>text/x-java-properties</code> Content-Type.
    """
