class ResolveMemos(object):
    """
     * This exists because we have to memoize resolved substitutions as we go
     * through the config tree; otherwise we could end up creating multiple copies
     * of values or whole trees of values as we follow chains of substitutions.
    """

    def __init__(self):

        # Map<MemoKey, AbstractConfigValue>
        # Note that we can resolve things to undefined (represented as None,
        # rather than ConfigNull) so this map can have None values.
        self._memos = {}

    def get(self, key):
        """
        :param key: MemoKey
        :return: AbstractConfigValue
        """
        return self._memos.get(key)

    def put(self, key, value):
        """
        :param key: MemoKey
        :param value: AbstractConfigValue
        :return: None
        """
        self._memos[key] = value
