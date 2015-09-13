
class AbstractConfigValue(ConfigValue, MergeableValue):
    """
    abstract class AbstractConfigValue implements ConfigValue, MergeableValue

    Trying very hard to avoid a parent reference in config values; when you have
    a tree like this, the availability of parent() tends to result in a lot of
    improperly-factored and non-modular code. Please don't add parent().

    Fields:

        _origin - SimpleConfigOrigin
    """

    def __init__(self, origin):
        self._origin = origin


    def origin(self):
        return self._origin

    def resolve_substitutions(self, context):
        """
        Called only by ResolveContext.resolve().

        :param context: ResolveContext
                    state of the current resolve
        :return: AbstractConfigValue - a new value if there were changes,
            or self if no changes
        :raises NotPossibleToResolve:
        """
        return self

    def resolve_status(self):
        """
        :return: ResolveStatus
        """
        return ResolveStatus.resolved

    def relativized(self, prefix):
        """
        This is used when including one file in another; the included file is
        relativized to the path it's included into in the parent file. The point
        is that if you include a file at foo.bar in the parent, and the included
        file as a substitution ${a.b.c}, the included substitution now needs to
        be ${foo.bar.a.b.c} because we resolve substitutions globally only after
        parsing everything.

        :param prefix: Path
        :return : AbstractConfigValue - value relativized to the given path or
            the same value if nothing to do
        """
        return self

    def to_fallback_value(self):
        """
        :return: AbstractConfigValue
        """
        return self

    def new_copy(self, origin):
        """
        protected abstract AbstractConfigValue newCopy(ConfigOrigin origin)
        """
        raise NotImplementedError

    def ignores_fallbacks(self):
        """
        protected boolean ignoresFallbacks()

        this is virtualized rather than a field because only some subclasses
        really need to store the boolean, and they may be able to pack it
        with another boolean to save space.
        """

        # if we are not resolved, then somewhere in this value there's
        # a substitution that may need to look at the fallbacks.
        return self.resolve_status() == ResolveStatus.resolved

    def with_fallbacks_ignored(self):
        """
        protected AbstractConfigValue withFallbacksIgnored()
        """
        if self.ignores_fallbacks():
            return self

        raise exceptions.BugOrBroken(
            "value class doesn't implement forced fallback-ignoring " + self)

    def require_not_ignoring_fallbacks(self):
        """
        protected final void requireNotIgnoringFallbacks()

        the withFallback() implementation is supposed to avoid calling
        mergedWith* if we're ignoring fallbacks.

        """
        if self.ignores_fallbacks():
            raise exceptions.BugOrBroken(
                "method should not have been called with ignoresFallbacks=true "
                + str(type(self))
            )

    def construct_delayed_merge(self, origin, stack):
        """
        protected AbstractConfigValue constructDelayedMerge(ConfigOrigin origin,
            List<AbstractConfigValue> stack)
        """
        return ConfigDelayedMerge(origin=origin, stack=stack)

    def merged_with_the_unmergeable(self, fallback, stack=None):
        """
        protected final AbstractConfigValue mergedWithTheUnmergeable(
            Collection<AbstractConfigValue> stack, Unmergeable fallback)

        protected AbstractConfigValue mergedWithTheUnmergeable(
            Unmergeable fallback)
        """
        self.require_not_ignoring_fallbacks()

        if stack is None:
            stack = [self]

        # if we turn out to be an object, and the fallback also does,
        # then a merge may be required; delay until we resolve.
        new_stack = []  # List<AbstractConfigValue>
        new_stack.add_all(stack)
        new_stack.add_all(fallback.unmerged_values())
        return self.construct_delayed_merge(
            AbstractConfigObject.merge_origins(new_stack),
            new_stack
        )

    def delay_merge(self, stack, fallback):
        """
        private final AbstractConfigValue delayMerge(
            Collection<AbstractConfigValue> stack, AbstractConfigValue fallback)
        """
        # if we turn out to be an object, and the fallback also does,
        # then a merge may be required.
        # if we contain a substitution, resolving it may need to look
        # back to the fallback.
        new_stack = []  # List<AbstractConfigValue>
        new_stack.add_all(stack)
        new_stack.add(fallback)
        return self.construct_delayed_merge(
            AbstractConfigObject.merge_origins(new_stack),
            new_stack
        )

    def merged_with_object(self, stack, fallback):
        """
        protected final AbstractConfigValue mergedWithObject(
            Collection<AbstractConfigValue> stack, AbstractConfigObject fallback)
        """
        self.require_not_ignoring_fallbacks()

        if instanceof(self, AbstractConfigObject):
            raise exceptions.BugOrBroken(
                "Objects must reimplement mergedWithObject")

        return self.merged_with_non_object(stack, fallback)

    def merged_with_non_object(self, stack, fallback):
        """
        protected final AbstractConfigValue mergedWithNonObject(
            Collection<AbstractConfigValue> stack, AbstractConfigValue fallback)
        """
        self.require_not_ignoring_fallbacks()

        if resolveStatus() == ResolveStatus.resolved:
            # falling back to a non-object doesn't merge anything, and also
            # prohibits merging any objects that we fall back to later.
            # so we have to switch to ignoresFallbacks mode.
            return self.with_fallbacks_ignored()
        else:
            # if unresolved, we may have to look back to fallbacks as part of
            # the resolution process, so always delay
            return self.delay_merge(stack, fallback)

    protected AbstractConfigValue mergedWithObject(AbstractConfigObject fallback):
        requireNotIgnoringFallbacks()

        return mergedWithObject(Collections.singletonList(self), fallback)

    protected AbstractConfigValue mergedWithNonObject(AbstractConfigValue fallback):
        requireNotIgnoringFallbacks()

        return mergedWithNonObject(Collections.singletonList(self), fallback)

    public AbstractConfigValue withOrigin(ConfigOrigin origin):
        if (self.origin == origin)
            return self
        else
            return newCopy(origin)

    // this is only overridden to change the return type
    @Override
    public AbstractConfigValue withFallback(ConfigMergeable mergeable):
        if (ignoresFallbacks()):
            return self
        } else:
            ConfigValue other = ((MergeableValue) mergeable).toFallbackValue()

            if (other instanceof Unmergeable):
                return mergedWithTheUnmergeable((Unmergeable) other)
            } else if (other instanceof AbstractConfigObject):
                return mergedWithObject((AbstractConfigObject) other)
            } else:
                return mergedWithNonObject((AbstractConfigValue) other)

    protected boolean canEqual(Object other):
        return other instanceof ConfigValue

    @Override
    public boolean equals(Object other):
        // note that "origin" is deliberately NOT part of equality
        if (other instanceof ConfigValue):
            return canEqual(other)
                    && (self.valueType() ==
                            ((ConfigValue) other).valueType())
                    && ConfigImplUtil.equalsHandlingNull(self.unwrapped(),
                            ((ConfigValue) other).unwrapped())
        } else:
            return false

    @Override
    public int hashCode():
        // note that "origin" is deliberately NOT part of equality
        Object o = self.unwrapped()
        if (o == null)
            return 0
        else
            return o.hashCode()

    @Override
    public final String toString():
        StringBuilder sb = new StringBuilder()
        render(sb, 0, true /* atRoot */, null /* atKey */, ConfigRenderOptions.concise())
        return getClass().getSimpleName() + "(" + sb.toString() + ")"

    protected static void indent(StringBuilder sb, int indent, ConfigRenderOptions options):
        if (options.getFormatted()):
            int remaining = indent
            while (remaining > 0):
                sb.append("    ")
                --remaining

    protected void render(StringBuilder sb, int indent, boolean atRoot, String atKey, ConfigRenderOptions options):
        if (atKey != null):
            String renderedKey
            if (options.getJson())
                renderedKey = ConfigImplUtil.renderJsonString(atKey)
            else
                renderedKey = ConfigImplUtil.renderStringUnquotedIfPossible(atKey)

            sb.append(renderedKey)

            if (options.getJson()):
                if (options.getFormatted())
                    sb.append(" : ")
                else
                    sb.append(":")
            } else:
                # in non-JSON we can omit the colon or equals before an object
                if (self instanceof ConfigObject):
                    if (options.getFormatted())
                        sb.append(' ')
                } else:
                    sb.append("=")

        render(sb, indent, atRoot, options)

    protected void render(StringBuilder sb, int indent, boolean atRoot, ConfigRenderOptions options):
        Object u = unwrapped()
        sb.append(u.toString())

    @Override
    public final String render():
        return render(ConfigRenderOptions.defaults())

    @Override
    public final String render(ConfigRenderOptions options):
        StringBuilder sb = new StringBuilder()
        render(sb, 0, true, null, options)
        return sb.toString()

    // toString() is a debugging-oriented string but this is defined
    // to create a string that would parse back to the value in JSON.
    // It only works for primitive values (that would be a single token)
    // which are auto-converted to strings when concatenating with
    // other strings or by the DefaultTransformer.
    String transformToString():
        return null

    SimpleConfig atKey(ConfigOrigin origin, String key):
        Map<String, AbstractConfigValue> m = Collections.singletonMap(key, self)
        return (new SimpleConfigObject(origin, m)).toConfig()

    @Override
    public SimpleConfig atKey(String key):
        return atKey(SimpleConfigOrigin.newSimple("atKey(" + key + ")"), key)

    SimpleConfig atPath(ConfigOrigin origin, Path path):
        Path parent = path.parent()
        SimpleConfig result = atKey(origin, path.last())
        while (parent != null):
            String key = parent.last()
            result = result.atKey(origin, key)
            parent = parent.parent()
        return result

    @Override
    public SimpleConfig atPath(String pathExpression):
        SimpleConfigOrigin origin = SimpleConfigOrigin.newSimple("atPath(" + pathExpression + ")")
        return atPath(origin, Path.newPath(pathExpression))


static class NotPossibleToResolve extends Exception:
    """
    This exception means that a value is inherently not resolveable, at the
    moment the only known cause is a cycle of substitutions. This is a
    checked exception since it's internal to the library and we want to be
    sure we handle it before passing it out to public API. This is only
    supposed to be thrown by the target of a cyclic reference and it's
    supposed to be caught by the ConfigReference looking up that reference,
    so it should be impossible for an outermost resolve() to throw this.

    Contrast with ConfigException.NotResolved which just means nobody called
    resolve().
    """
    private static final long serialVersionUID = 1L

    final private String traceString

    NotPossibleToResolve(ResolveContext context):
        super("was not possible to resolve")
        self.traceString = context.traceString()

    String traceString():
        return traceString


protected interface Modifier:
    // keyOrNull is null for non-objects
    AbstractConfigValue modifyChildMayThrow(String keyOrNull, AbstractConfigValue v)
            throws Exception

protected abstract class NoExceptionsModifier implements Modifier:
    @Override
    public final AbstractConfigValue modifyChildMayThrow(String keyOrNull, AbstractConfigValue v)
            throws Exception:
        try:
            return modifyChild(keyOrNull, v)
        } catch (RuntimeException e):
            throw e
        } catch(Exception e):
            throw new ConfigException.BugOrBroken("Unexpected exception", e)

    abstract AbstractConfigValue modifyChild(String keyOrNull, AbstractConfigValue v)
