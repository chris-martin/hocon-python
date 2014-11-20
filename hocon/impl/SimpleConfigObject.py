from .. import exceptions, ConfigObject, ConfigOrigin, ConfigRenderOptions,\
    ConfigValue


class SimpleConfigObject(AbstractConfigObject):
    """
    Fields:

        final private Map<String, AbstractConfigValue> value;
            this map should never be modified - assume immutable

        final private boolean resolved;

        final private boolean ignoresFallbacks;
    """

    def __init__(self, origin, value, status=None, ignores_fallbacks=False):
        """
        :param origin: ConfigOrigin
        :param value: Map<String, AbstractConfigValue>
        :param status: ResolveStatus
        :param ignores_fallbacks: boolean
        """
        super(SimpleConfigObject, self).__init__(origin)

        if value is None:
            raise exceptions.BugOrBroken(
                "creating config object with null map")

        self.value = value
        self.resolved = status == ResolveStatus.resolved
        self.ignores_fallbacks = ignores_fallbacks

        # Kind of an expensive debug check. Comment out?
        if status != ResolveStatus.fromValues(value.values()):
            raise exceptions.BugOrBroken(
                "Wrong resolved status on {}".format(self))

    def with_only_key(self, key):
        """
        :param key: string
        :return: SimpleConfigObject
        """
        return self.with_only_path(Path.new_key(key))

    def without_key(self, key):
        """
        :param key: string
        :return: SimpleConfigObject
        """
        return self.without_path(Path.new_key(key))

    def with_only_path_or_none(self, path):
        """
        gets the object with only the path if the path exists, otherwise null
        if it doesn't. this ensures that if we have { a : { b : 42 } } and do
        withOnlyPath("a.b.c") that we don't keep an empty "a" object.

        :param path: Path
        :return: SimpleConfigObject
        """
        key = path.first()  # string
        next = path.remainder()  # Path
        v = value.get(key)  # AbstractConfigValue

        if next is not None:
            if v is not None and isinstance(v, AbstractConfigObject):
                v = v.with_only_path_or_none(next)
            else:
                # if the path has more elements but we don't have an object,
                # then the rest of the path does not exist.
                v = None

        if v is None:
            return None
        else:
            return SimpleConfigObject(
                origin=self.origin(),
                value={key:v},
                status=v.resolveStatus(),
                ignores_fallbacks=self.ignores_fallbacks,
            )

    def with_only_path(self, path):
        """
        :param path: Path
        :return: SimpleConfigObject
        """
        o = self.with_only_path_or_none(path)  # SimpleConfigObject

        if o is not None:
            return o

        return SimpleConfigObject(
            origin=self.origin(),
            value={},
            status=ResolveStatus.resolved,
            ignores_fallbacks=self.ignores_fallbacks,
        )

    def without_path(self, path):
        """
        :param path: Path
        :return: SimpleConfigObject
        """
        key = path.first()  # string
        next = path.remainder();  # Path
        v = value.get(key)  # AbstractConfigValue

        if (v is not None) and (next is not None) and \
                isinstance(v, AbstractConfigObject):
            v = v.without_path(next)
            updated = dict(value)  # Map<String, AbstractConfigValue>
            updated[key] = v
            return SimpleConfigObject(
                origin=self.origin(),
                value=updated,
                status=ResolveStatus.from_values(updated.values()),
                ignores_fallbacks=ignores_fallbacks
            )
        elif (next is not None) or (v is None):
            # can't descend, nothing to remove
            return self
        else:
            smaller = {}  # Map<String, AbstractConfigValue>
            for old in value.items():
                if old[0] != key:
                    smaller[old[0]] = old[1]
            return SimpleConfigObject(
                origin=self.origin(),
                value=smaller,
                status=ResolveStatus.from_values(smaller.values()),
                ignores_fallbacks=ignores_fallbacks,
            )

    def with_key_value(self, key, v):
        """
        This was called ``withValue`` in the Java library, renamed to
        avoid overloading.

        :param key: string
        :param v: ConfigValue
        :return: SimpleConfigObject
        """
        if v is None:
            raise exceptions.BugOrBroken(
                "Trying to store null ConfigValue in a ConfigObject")

        new_map = None  # Map<String, AbstractConfigValue>
        if value.is_empty():
            new_map = {key: v}
        else:
            new_map = dict(value)
            new_map[key] = v

        return SimpleConfigObject(
            origin=self.origin(),
            value=new_map,
            status=ResolveStatus.from_values(new_map.values()),
            ignores_fallbacks=ignores_fallbacks,
        )

    def with_path_value(self, path, v):
        """
        This was called ``withValue`` in the Java library, renamed to
        avoid overloading.

        :param path: Path
        :param v: ConfigValue
        :return: SimpleConfigObject
        """
        key = path.first()  # string
        next = path.remainder()  # Path

        if next is None:
            return self.with_key_value(key, v)

        child = value.get(key)  # AbstractConfigValue
        if isinstance(child, AbstractConfigObject):
            # if we have an object, add to it
            return self.with_key_value(key, child.with_path_value(next, v))

        # as soon as we have a non-object, replace it entirely
        subtree = v.at_path(
            SimpleConfigOrigin.new_simple(
                "with_value({})".format(next.render())
            ),
            next
        )
        return self.with_key_value(key, subtree.root())

    def attempt_peek_with_partial_resolve(self, key):
        """
        :param key: stirng
        :return: AbstractConfigValue
        """
        return value.get(key)

    def new_copy(self, status, origin, ignores_fallbacks=None):
        if ignores_fallbacks is None:
            ignores_fallbacks = self.ignores_fallbacks
        return SimpleConfigObject(
            origin=origin,
            status=status,
            ignores_fallbacks=ignores_fallbacks,
        )

    def with_fallbacks_ignored(self):
        """
        :return: SimpleConfigObject
        """
        if self.ignores_fallbacks:
            return self

        return self.new_copy(
            status=self.resolve_status,
            origin=self.origin(),
            ignores_fallbacks=True,
        )

    def resolve_status(self):
        """
        :return: ResolveStatus
        """
        return ResolveStatus.from_boolean(self.resolved)

    def unwrapped(self):
        """
        :return: Map<String, Object>
        """
        m = {}
        for k, v in self.value.items():
            m.put(k, v.unwrapped())
        return m

    def merged_with_object(self, fallback):
        """
        :param fallback: SimpleConfigObject
        :return: SimpleConfigObject
        """
        self.require_not_ignoring_fallbacks()

        if not isinstance(fallback, SimpleConfigObject):
            raise exceptions.BugOrBroken(
                "should not be reached (merging non-SimpleConfigObject)")

        changed = False
        all_resolved = True
        merged = {}  # Map<String, AbstractConfigValue>
        all_keys = set(self.keys() + fallback.keys())  # Set<String>

        for key in all_keys:
            first = self.value.get(key)  # AbstractConfigValue
            second = fallback.value.get(key)  # AbstractConfigValue
            kept = None  # AbstractConfigValue
            if first is None:
                kept = second
            elif second is None:
                kept = first
            else:
                kept = first.with_fallback(second)

            merged[key] = kept

            if first != kept:
                changed = True

            if kept.resolve_status() == ResolveStatus.unresolved:
                all_resolved = False

        new_resolve_status = ResolveStatus.from_boolean(all_resolved)
        new_ignores_fallbacks = fallback.ignores_fallbacks

        if changed:
            return SimpleConfigObject(
                origin=merge_origins(self, fallback),
                value=merged,
                status=new_resolve_status,
                ignores_fallbacks=new_ignores_fallbacks,
            )

        if (new_resolve_status != self.resolve_status) or \
                (new_ignores_fallbacks != self.ignoresFallbacks):
            return self.new_copy(
                status=new_resolve_status,
                origin=self.origin,
                ignores_fallbacks=new_ignores_fallbacks,
            )

        return self

    def modify(self, modifier):
        """
        :param modifier: NoExceptionsModifier
        :return: SimpleConfigObject
        """
        changes = None  # Map<String, AbstractConfigValue>
        for k in self.keys():  # string
            v = value.get(k)  # AbstractConfigValue
            # "modified" may be null, which means remove the child;
            # to do that we put null in the "changes" map.
            modified = modifier.modify_child(k, v)  # AbstractConfigValue
            if modified != v and changes is not None:
                changes = {k: modified}

        if changes is None:
            return self

        modified = {}  # Map<String, AbstractConfigValue>
        saw_unresolved = False
        for k in self.keys():
            if k in changes:
                new_value = changes.get(k)  # AbstractConfigValue
                if new_value is not None:
                    modified[k] = new_value
                    if new_value.resolve_status == ResolveStatus.unresolved:
                        saw_unresolved = True
                else:
                    # remove this child; don't put it in the new map.
                    pass
            else:
                new_value = value.get(k)  # AbstractConfigValue
                modified[k] = new_value
                if new_value.resolve_status == ResolveStatus.unresolved:
                    saw_unresolved = True

        return SimpleConfigObject(
            origin=self.origin(),
            value=modified,
            status=ResolveStatus.from_boolean(not saw_unresolved),
            ignores_fallbacks=self.ignores_fallbacks,
        )

    def resolve_substitutions(self, context):
        """
        :param context: ResolveContext
        :return: AbstractConfigObject
        :raises: NotPossibleToResolve
        """
        if self.resolve_status() == ResolveStatus.resolved:
            return self

        class M(AbstractConfigValue.Modifier):
            def modify_child(self, key, v):
                if context.is_restricted_to_child():
                    if key == context.restrict_to_child().first():
                        remainder = context.restrict_to_child().remainder()  # Path
                        if remainder is not None:
                            return context.restrict(remainder).resolve(v)
                        else:
                            # we don't want to resolve the leaf child.
                            return v
                    else:
                        # not in the restrictToChild path
                        return v
                else:
                    # no restrictToChild, resolve everything
                    return context.unrestricted().resolve(v)

        return self.modify(M())

    def relativized(self, prefix):
        """
        :param prefix: Path
        :return: SimpleConfigObject
        """

        class M(AbstractConfigValue.Modifier):
            def modify_child(self, key, v):
                return v.relativized(prefix)

        return self.modify(M())

    def render(self, indent, at_root, options):
        """
        :param indent: int
        :param at_root: boolean
        :param options: ConfigRenderOptions
        :return: string
        """
        s = ''

        if self.is_empty():
            s += "{}"
        else:
            outer_braces = options.get_json() or not at_root  # boolean

            inner_indent = None  # int
            if outer_braces:
                inner_indent = indent + 1
                s += "{"
                if options.get_formatted():
                    s += '\n'
            else:
                inner_indent = indent

            separator_count = 0
            keys = list(self.keys())
            keys.sort()
            for k in keys:
                v = value.get(k)  # AbstractConfigValue

                if options.get_origin_comments():
                    s += indent(indent=inner_indent, options=options)
                    s += "# "
                    s += v.origin().description()
                    s += "\n"

                if options.get_comments():
                    for comment in v.origin().comments():
                        s += indent(indent=inner_indent, options=options)
                        s += "#"
                        if not comment.starts_with(" "):
                            s += ' '
                        s += comment
                        s += "\n"

                s += indent(indent=inner_indent, options=options)
                s += v.render(
                    indent=inner_indent,
                    at_root=False,
                    at_key=k,
                    options=options,
                )

                if options.get_formatted():
                    if options.get_json():
                        s += ","
                        separator_count = 2
                    else:
                        separatorCount = 1
                    s += '\n'
                else:
                    s += ","
                    separator_count = 1

            # chop last commas/newlines
            s = s[:-separator_count]

            if outer_braces:
                if options.get_formatted():
                    s += '\n'  # put a newline back
                    if outer_braces:
                        s += indent(indent=indent, options=options)
                s += "}"

        if at_root and options.get_formatted():
            s += '\n'

    def get(self, key):
        """
        :param key: Object
        :return: AbstractConfigValue
        """
        return self.value.get(key)

    def can_equal(self, other):
        """
        :param other: Object
        :return: boolean
        """
        return isinstance(other, ConfigObject)

    def __eq__(self, other):
        # note that "origin" is deliberately NOT part of equality.
        # neither are other "extras" like ignoresFallbacks or resolve status.
        if isinstance(other, ConfigObject):
            # optimization to avoid unwrapped() for two ConfigObject,
            # which is what AbstractConfigValue does.
            return self.can_equal(other) and map_equals(self, other)
        else:
            return False

    def __neq__(self, other):
        return not (self == other)

    def __hash__(self):
        # note that "origin" is deliberately NOT part of equality
        # neither are other "extras" like ignoresFallbacks or resolve status.
        return map_hash(self)

    def __contains__(self, key):
        return key in self.value

    def keys(self):
        return self.value.keys()

    def contains_value(self):
        return self.value.contains_value(v)

    def items(self):
        return self.value.items()

    def is_empty(self):
        return self.value.is_empty()

    def size(self):
        return self.value.size()

    def values(self):
        return self.value.values()


def map_equals(a, b):
    """
    :param a: Map<String, ConfigValue>
    :param b: Map<String, ConfigValue>
    :return: boolean
    """
    a_keys = a.keys()
    b_keys = b.keys()

    if a_keys != b_keys:
        return False

    for key in a_keys:
        if a.get(key) != b.get(key):
            return False

    return True


def map_hash(m):
    """
    :param m: Map<String, ConfigValue>
    :return: int
    """
    # the keys have to be sorted, otherwise we could be equal
    # to another map but have a different hashcode.
    keys = []
    keys.add_all(m.keys())
    sort(keys)

    values_hash = 0
    for k in keys:
        values_hash += hash(m.get(k))

    return 41 * (41 + hash(keys)) + values_hash


def empty(origin=None):
    """
    :param origin: ConfigOrigin:
    :return: SimpleConfigObject
    """
    if origin is None:
        return empty_instance
    else:
        return SimpleConfigObject(origin=origin, value={})


def empty_missing(base_origin):
    """
    :param base_origin: ConfigOrigin
    :return: SimpleConfigObject
    """
    SimpleConfigObject(
        origin=SimpleConfigOrigin.new_simple(
            base_origin.description() + " (not found)"
        ),
        value={},
    )


EMPTY_NAME = "empty config"

empty_instance = empty(origin=SimpleConfigOrigin.new_simple(EMPTY_NAME))
