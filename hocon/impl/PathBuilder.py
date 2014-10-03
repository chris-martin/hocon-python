from .. import exceptions

class PathBuilder(object):
    """
    Attributes:

        _keys: Stack<String> -
            the keys are kept "backward" (top of stack is end of path)

        _result: Path
    """

    def __init__(self):
        self._keys = []
        self._result = None

    def _check_can_append(self):
        if self._result is not None:
            raise exceptions.BugOrBroken(
                "Adding to PathBuilder after getting result")

    def append_key(self, key):
        """
        :param key: String
        :return: None
        """
        self._check_can_append()
        self._keys.append(key)

    def append_path(self, path):
        """
        :param path: Path
        :return: None
        """
        self.checkCanAppend()

        first = path.first  # String
        remainder = path.remainder  # path
        while True:
            self._keys.append(first)
            if remainder is not None:
                first = remainder.first
                remainder = remainder.remainder
            else:
                break

    def result(self):
        """
        :return: Path
        """

        # note: if keys is empty, we want to return null, which is a valid
        # empty path
        if self._result is None:
            remainder = None  # Path
            while len(self._keys) != 0:
                key = self._keys.pop()  # String
                remainder = Path(key, remainder)
            self._result = remainder
        return self._result
