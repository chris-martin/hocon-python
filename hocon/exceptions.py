import collections


class ConfigException(Exception):
    """
     * All exceptions thrown by the library are subclasses of
     * <code>ConfigException</code>.
    """

    def __init__(self, message, cause=None, origin=None):
        """
        :param message: String
        :param cause: Throwable
        :param origin: ConfigOrigin
        """
        self._message = (message if origin is None else
                         origin.description() + ': ' + message)
        self._cause = cause
        self._origin = origin

    def origin(self):
        """
        public ConfigOrigin origin()

         * Returns an "origin" (such as a filename and line number) for the
         * exception, or null if none is available. If there's no sensible origin
         * for a given exception, or the kind of exception doesn't meaningfully
         * relate to a particular origin file, this returns null. Never assume this
         * will return non-null, it can always return null.
         *
         * @return origin of the problem, or null if unknown/inapplicable
        """
        return self._origin


class WrongType(ConfigException):
    """
     * Exception indicating that the type of a value does not match the type you
     * requested.
    """

    def __init__(self, origin, path=None, message=None, expected=None,
                 actual=None, cause=None):
        """
        :param origin: ConfigOrigin
        :param path: String
        :param message: String
        :param expected: String
        :param actual: String
        :param cause: Throwable
        """
        super(WrongType, self).__init__(
            origin=origin,
            cause=cause,
            message=(message if message is not None else
                     path + " has type " + actual + "rather than " + expected),
        )


class Missing(ConfigException):
    """
     * Exception indicates that the setting was never set to anything, not even
     * null.
    """

    def __init__(self, origin=None, message=None, path=None, cause=None):
        """
        :param origin: ConfigOrigin
        :param message: String
        :param path: String
        :param cause: Throwable
        """
        super(Missing, self).__init__(
            origin=origin,
            cause=cause,
            message=(message if message is not None else
                     "No configuration setting found for key '" + path + "'"),
        )


class Null(Missing):
    """
     * Exception indicates that the setting was treated as missing because it
     * was set to null.
    """

    @classmethod
    def _make_message(cls, path, expected):
        """
        :param path: String
        :param expected: String
        :return: String
        """
        if expected is not None:
            return "Configuration key '" + path \
                + "' is set to null but expected " + expected
        else:
            return "Configuration key '" + path + "' is null"

    def __init__(self, origin, path, expected, cause=None):
        super(Null, self).__init__(
            origin=origin,
            cause=cause,
            message=(Null._make_message(path, expected)),
        )


class BadValue(ConfigException):
    """
     * Exception indicating that a value was messed up, for example you may have
     * asked for a duration and the value can't be sensibly parsed as a
     * duration.
    """

    def __init__(self, path, message, origin=None, cause=None):
        super(BadValue, self).__init__(
            origin=origin,
            cause=cause,
            message=(message if message is not None else
                     "Invalid value at '" + path + "': " + message),
        )


class BadPath(ConfigException):
    """
     * Exception indicating that a path expression was invalid. Try putting
     * double quotes around path elements that contain "special" characters.
    """

    def __init__(self, message, origin=None, path=None, cause=None):
        super(BadPath, self).__init__(
            origin=origin,
            cause=cause,
            message=(message if path is None else
                     "Invalid path '" + path + "': " + message),
        )


class BugOrBroken(ConfigException):
    """
     * Exception indicating that there's a bug in something (possibly the
     * library itself) or the runtime environment is broken. This exception
     * should never be handled; instead, something should be fixed to keep the
     * exception from occurring. This exception can be thrown by any method in
     * the library.
    """

    def __init__(self, message, cause=None):
        super(BugOrBroken, self).__init__(message=message, cause=cause)


class IO(ConfigException):
    """
     * Exception indicating that there was an IO error.
    """

    def __init__(self, message, origin, cause=None):
        super(IO, self).__init__(message=message, origin=origin, cause=cause)


class Parse(ConfigException):
    """
     * Exception indicating that there was a parse error.
     *
    """

    def __init__(self, message, origin, cause=None):
        super(Parse, self).__init__(message=message, origin=origin, cause=cause)


class UnresolvedSubstitution(Parse):
    """
     * Exception indicating that a substitution did not resolve to anything.
     * Thrown by {@link Config#resolve}.
    """

    def __init__(self, origin, detail, cause=None):
        super(UnresolvedSubstitution, self).__init__(
            origin=origin,
            cause=cause,
            message=("Could not resolve substitution to a value: " + detail),
        )


class NotResolved(BugOrBroken):
    """
     * Exception indicating that you tried to use a function that requires
     * substitutions to be resolved, but substitutions have not been resolved
     * (that is, {@link Config#resolve} was not called). This is always a bug in
     * either application code or the library; it's wrong to write a handler for
     * this exception because you should be able to fix the code to avoid it by
     * adding calls to {@link Config#resolve}.
    """

    def __init__(self, message, cause=None):
        super(NotResolved, self).__init__(message=message, cause=cause)


class ValidationProblem(collections.namedtuple('ValidationProblem', ('path', 'origin', 'problem'))):
    """
     * Information about a problem that occurred in {@link Config#checkValid}. A
     * {@link ConfigException.ValidationFailed} exception thrown from
     * <code>checkValid()</code> includes a list of problems encountered.

    :param path: String - the config setting causing the problem.
    :param origin: ConfigOrigin - where the problem occurred (origin may
                   include info on the file, line number, etc.).
    :param problem: String - a description of the problem.
    """


class ValidationFailed(ConfigException):
    """
     * Exception indicating that {@link Config#checkValid} found validity
     * problems. The problems are available via the {@link #problems()} method.
     * The <code>getMessage()</code> of this exception is a potentially very
     * long string listing all the problems found.
    """

    def __init__(self, problems):
        """
        :param problems: Iterable<ValidationProblem>
        """
        super(ValidationFailed, self).__init__(
            self, message=ValidationFailed._make_message(problems))
        self._problems = problems

    def problems(self):
        """
        :return: Iterable<ValidationProblem>
        """
        return self._problems

    @classmethod
    def _make_message(cls, problems):
        """
        :param problems: Iterable<ValidationProblem>
        :return: String
        """
        s = ', '.join([
            '{description}: {path}: {problem}'.format(
                description=p.origin.description(),
                path=p.path,
                problem=p.problem,
            ) for p in self._problems
        ])
        if len(s) == 0:
            raise BugOrBroken(
                "ValidationFailed must have a non-empty list of problems")
        return s


class Generic(ConfigException):
    """
     * Exception that doesn't fall into any other category.
    """

    def __init__(self, message, cause=None):
        super(Generic, self).__init__(message=message, cause=cause)
