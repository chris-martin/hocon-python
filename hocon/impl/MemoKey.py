import collections


class MemoKey(collections.namedtuple('MemoKey',
        ('value_id', 'restrict_to_child_or_null'))):
    """
    The key used to memoize already-traversed nodes when resolving substitutions.

    :param value_id: id(AbstractConfigValue)
    :param restrict_to_child_or_null: Path
    """

    def __new__(cls, value, restrict_to_child_or_null):

        if isinstance(value, AbstractConfigValue):
            value_id = id(value)
        elif isinstance(value, int):
            value_id = value
        else:
            raise ValueError('Expected AbstractConfigValue or int, got ' + value)

        return super(MemoKey, cls).__new__(
            value_id,
            restrict_to_child_or_null
        )
