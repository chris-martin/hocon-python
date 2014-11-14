from .. import exceptions, ConfigSyntax, ConfigMergeable, ConfigObject, \
    ConfigOrigin, ConfigRenderOptions, ConfigValue, ConfigValueType

from .AbstractConfigValue import AbstractConfigValue
from .SimpleConfig import SimpleConfig
from . import SimpleConfigOrigin


class AbstractConfigObject(AbstractConfigValue, ConfigObject):
    """
    Fields:
      - config: SimpleConfig
    """

    def __init__(self, origin):
        """
        :param origin: ConfigOrigin
        """
        super(AbstractConfigObject, self).__init__(origin)
        self.config = SimpleConfig(self)

    def to_config(self):
        """
        :return: SimpleConfig
        """
        return self.config

    def to_fallback_value(self):
        """
        :return: AbstractConfigObject
        """
        return self

    def with_only_key(self, key):
        """
        :param key: string
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def without_key(self, key):
        """
        :param key: string
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def with_key_value(self, key, value):
        """
        This was called withValue in Java, renamed to avoid overloading

        :param key: string
        :param value: ConfigValue
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def with_only_path_or_none(self, path):
        """
        :param path: Path
        :return: AbstractConfigObject or None
        """
        raise NotImplementedError

    def with_only_path(self, path):
        """
        :param path: Path
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def without_path(self, path):
        """
        :param path: Path
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def with_path_value(self, path, value):
        """
        This was called withValue in Java, renamed to avoid overloading

        :param path: Path
        :param value: ConfigValue
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def peek_assuming_resolved(self, key, original_path):
        """
        Looks up the key with no transformation or type conversion of any
        kind, and returns None if the key is not present. The object must be
        resolved; use attemptPeekWithPartialResolve() if it is not.

        :param key: string
        :param original_path: Path
        :return: AbstractConfigValue - the unmodified raw value or null
        """
        try:
            return self.attempt_peek_with_partial_resolve(key)
        except exceptions.NotResolved as e:
            raise ConfigImpl.improve_not_resolved(original_path, e)

    def attempt_peek_with_partial_resolve(self, key):
        """
        Look up the key on an only-partially-resolved object, with no
        transformation or type conversion of any kind; if 'this' is not resolved
        then try to look up the key anyway if possible.

        :param key: string - key to look up
        :return: AbstractConfigValue - the value of the key, or None if known not to exist
        :raises exceptions.NotResolved:
                if can't figure out key's value or can't know whether it exists
        """
        raise NotImplementedError

    def peek_path(self, path, context=None):
        """
        If context is not None:
            Looks up the path with no transformation, type conversion, or exceptions
            (just returns None if path not found). Does however resolve the path, if
            resolver is not None.

        If context is None:
            Looks up the path. Doesn't do any resolution, will throw if any is
            needed.

        :param path: Path
        :param context: ResolveContext
        :return: AbstractConfigValue
        :raises NotPossibleToResolve:
                if context is not None and resolution fails
        """
        if context is not None:
            return peek_path(self, path, context)
        else:
            try:
                return peek_path(self, path)
            except NotPossibleToResolve:
                raise exceptions.BugOrBroken(
                    "NotPossibleToResolve happened though we "
                    "had no ResolveContext in peek_path")

    def value_type(self):
        """
        :return: ConfigValueType
        """
        return ConfigValueType.OBJECT

    def new_copy(self, origin, status=None):
        """
        :param status: ResolveStatus - should default to ``self.resolve_status()``
        :param origin: ConfigOrigin
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def construct_delayed_merge(self, origin, stack):
        """
        :param origin: ConfigOrigin
        :param stack: List<AbstractConfigValue>
        :return: AbstractConfigObject
        """
        return ConfigDelayedMergeObject(origin, stack)

    def merged_with_object(self, fallback):
        """
        :param fallback: AbstractConfigObject
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def with_fallback(self, mergeable):
        """
        :param mergeable: ConfigMergeable
        :return: AbstractConfigObject
        """
        return super(AbstractConfigObject, self).with_fallback(mergeable)

    def resolve_substitutions(self, context):
        """
        :param context: ResolveContext
        :return: AbstractConfigObject
        :raises NotPossibleToResolve:
        """
        raise NotImplementedError

    def relativized(self, prefix):
        """
        :param prefix: Path
        :return: AbstractConfigObject
        """
        raise NotImplementedError

    def get(self, key):
        """
        :param key: Object
        :return: AbstractConfigValue
        """
        raise NotImplementedError

    def render(self, indent, at_root, options):
        """
        :param indent: int
        :param at_root: boolean
        :param options: ConfigRenderOptions
        :return: string

        protected abstract void render(StringBuilder sb, int indent,
            boolean atRoot, ConfigRenderOptions options)
        """
        raise NotImplementedError


def peek_path(self, path, context=None):
    """
    as a side effect, peekPath() will have to resolve all parents of the
    child being peeked, but NOT the child itself. Caller has to resolve
    the child itself if needed.

    :param self: AbstractConfigObject
    :param path: Path
    :param context: ResolveContext
    :return: AbstractConfigValue
    :raises NotPossibleToResolve:
    """
    try:
        if context is not None:
            return peek_path_with_context(self, path, context)
        else:
            return peek_path_without_context(self, path)

    except exceptions.NotResolved as e:
        raise ConfigImpl.improve_not_resolved(path, e)


def peek_path_with_context(self, path, context):
    """
    walk down through the path resolving only things along that
    path, and then recursively call ourselves with no resolve context.
    """
    partially_resolved = context.restrict(path).resolve(self)
    if isinstance(partially_resolved, AbstractConfigObject):
        return peek_path(partially_resolved, path)
    else:
        raise exceptions.BugOrBroken(
            "resolved object to non-object {} to {}"
            .format(self, partially_resolved))


def peek_path_without_context(self, path):
    """
    with no resolver, we'll fail if anything along the path can't
    be looked at without resolving.
    """
    next = path.remainder()
    v = self.attempt_peek_with_partial_resolve(path.first())

    if next is None:
        return v
    if isinstance(v, AbstractConfigObject):
        return peek_path(v, next)


def merge_origins(stack):
    """
    :param stack: Collection<? extends AbstractConfigValue>
    :return: ConfigOrigin
    """

    if len(stack) == 0:
        raise exceptions.BugOrBroken("can't merge origins on empty list")

    origins = []  # List<ConfigOrigin>
    first_origin = None  # ConfigOrigin
    num_merged = 0

    for v in stack:
        if first_origin is None:
            first_origin = v.origin()

        if isinstance(v, AbstractConfigObect) and \
                v.resolve_status == ResolveStatus.resolved and v.is_empty():
            # don't include empty files or the .empty() config in the
            # description, since they are likely to be "implementation details"
            pass
        else:
            origins.append(v.origin())
            num_merged += 1

    if num_merged == 0:
        # the configs were all empty, so just use the first one
        origins.append(first_origin)

    return SimpleConfigOrigin.merge_origins(origins)
