import collections

from .. import exceptions

from . import util


class Path(collections.namedtuple('Path', ('first', 'remainder'))):
    """
    :param first: String

    :param remainder: Path
        Path minus the first element or None if no more elements.
    """

    @classmethod
    def of_elements(cls, *elements):
        if len(elements) == 0:
            raise exceptions.BugOrBroken("empty path")
        first = elements[0]
        if len(elements) > 1:
            pb = PathBuilder()
            for el in elements:
                pb.append_key(el)
            remainder = pb.result()
        else:
            remainder = None
        return Path(first, remainder)

    @classmethod
    def of_paths(cls, *paths):
        """
        Append all the paths in the list together into one path.

        Path(List<Path> pathsToConcat)
        Path(Iterator<Path> i)
        """

        if len(paths) == 0:
            raise exceptions.BugOrBroken("empty path")

        pb = PathBuilder()
        if paths[0].remainder is not None:
            pb.append_path(paths[0].remainder)

        for p in paths[1:]:
            pb.append_path(p)

        return Path(paths[0].first, pb.result())

    def parent(self):
        """
        :return: Path
            path minus the last element or None if we have just one element
        """

        if self.remainder is None:
            return None

        pb = PathBuilder()
        p = self
        while p.remainder is not None:
            pb.append_key(p.first)
            p = p.remainder
        return pb.result()

    def last(self):
        """
        :return: String - last element in the path
        """
        p = self
        while p.remainder is not None:
            p = p.remainder
        return p.first

    def prepend(self, to_prepend):
        """
        :param to_prepend: Path
        :return: Path
        """
        pb = PathBuilder()
        pb.append_path(to_prepend)
        pb.append_path(self)
        return pb.result()

    def length(self):
        """
        :return: int
        """
        count = 1
        p = self.remainder
        while p is not None:
            count += 1
            p = p.remainder
        return count

    def remove_from_front(self, remove_from_front):
        """
        Path subPath(int removeFromFront)

        :param remove_from_front: int
        :return: Path
        """
        count = remove_from_front
        p = self
        while p is not None and count > 0:
            count -= 1
            p = p.remainder
        return p


    def sub_path(self, first_index, last_index):
        """
        Path subPath(int firstIndex, int lastIndex)

        :param first_index: int
        :param last_index: int
        :return: Path
        """
        if last_index < first_index:
            raise exceptions.BugOrBroken("bad call to subPath")

        from_path = self.remove_from_front(first_index)
        pb = PathBuilder()
        count = last_index - first_index
        while count > 0:
            count -= 1
            pb.append_key(from_path.first)
            from_path = from_path.remainder
            if from_path is None:
                raise exceptions.BugOrBroken(
                    "subPath lastIndex out of range " + last_index)
        return pb.result()

    @classmethod
    def has_funky_chars(cls, s):
        """
        :param s: String
        :return: boolean
        """

        # This doesn't have a very precise meaning, just to reduce
        # noise from quotes in the rendered path for average cases.
        length = len(s)

        if length == 0:
            return False

        # If the path starts with something that could be a number,
        # we need to quote it because the number could be invalid,
        # for example it could be a hyphen with no digit afterward
        # or the exponent "e" notation could be mangled.
        first = s[0]
        if not first.isalpha():
            return True

        for c in s[1:]:
            if c.isalnum() or c in '-_':
                continue
            else:
                return True
        return False

    def __repr__(self):
        """
        public String toString()
        """
        return "Path(" + unicode(self) + ")"

    def __unicode__(self):
        """
        String render()
        """
        if Path.has_funky_chars(self.first) or len(self.first) == 0:
            s = util.render_json_string(self.first)
        else:
            s = self.first

        if remainder is not None:
            s += "." + unicode(self.remainder)

        return s

    @classmethod
    def new_key(cls, key):
        """
        :param key: String
        :return: Path
        """
        return Path(key, None)

    @classmethod
    def new_path(cls, path):
        """
        :param path: String
        :return: Path
        """
        return Parser.parse_path(path)
