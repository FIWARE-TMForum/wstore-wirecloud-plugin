
import regex
from six import string_types


class Version(object):

    version_re = regex.compile(r'^([1-9]\d*|0)((?:\.(?:[1-9]\d*|0))*)(?:(a|b|rc)([1-9]\d*))?$')

    def __init__(self, vstring, reverse=False):

        match = self.version_re.match(vstring)

        if not match:
            raise ValueError("invalid version number '%s'" % vstring)

        (major, patch, prerelease, prerelease_num) = match.group(1, 2, 3, 4)

        if patch:
            self.version = tuple(map(int, [major] + patch[1:].split('.')))
        else:
            self.version = (int(major),)

        if prerelease:
            self.prerelease = (prerelease, int(prerelease_num))
        else:
            self.prerelease = None

        self.reverse = reverse

    def __cmp__(self, other):

        if isinstance(other, string_types):
            other = Version(other)

        if not isinstance(other, Version):
            raise ValueError("invalid version number '%s'" % other)

        maxlen = max(len(self.version), len(other.version))
        compare = cmp(self.version + (0,)*(maxlen - len(self.version)), other.version + (0,)*(maxlen - len(other.version)))

        if compare == 0:

            # case 1: neither has prerelease; they're equal
            if not self.prerelease and not other.prerelease:
                compare = 0

            # case 2: self has prerelease, other doesn't; other is greater
            elif self.prerelease and not other.prerelease:
                compare = -1

            # case 3: self doesn't have prerelease, other does: self is greater
            elif not self.prerelease and other.prerelease:
                compare = 1

            # case 4: both have prerelease: must compare them!
            elif self.prerelease and other.prerelease:
                compare = cmp(self.prerelease, other.prerelease)

        return compare if not self.reverse else (compare * -1)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0
