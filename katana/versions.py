"""
Python 2 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2017 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""

from __future__ import absolute_import

import re

from functools import cmp_to_key
from itertools import zip_longest

from .errors import KatanaError

__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2017 KUSANAGI S.L. (http://kusanagi.io)"

# Regexp to remove duplicated '*' in versions
DUPLICATES = re.compile(r'(\*)\1+')

# Regexp to check version pattern for invalid chars
INVALID_PATTERN = re.compile(r'[^a-zA-Z0-9*.,_-]')


class InvalidVersionPattern(KatanaError):
    """Exception raised when a version pattern is not valid."""

    message = 'Invalid version pattern: "{}"'

    def __init__(self, pattern):
        super(InvalidVersionPattern, self).__init__(
            message=self.message.format(pattern)
            )
        self.pattern = pattern


class VersionNotFound(KatanaError):
    """Exception raised when a version is not found."""

    message = 'Service version not found for pattern: "{}"'

    def __init__(self, pattern):
        super(VersionNotFound, self).__init__(
            message=self.message.format(pattern)
            )
        self.pattern = pattern


class VersionString(object):
    def __init__(self, version):
        # Validate pattern characters
        if INVALID_PATTERN.search(version):
            raise InvalidVersionPattern(version)

        # Remove duplicated special chars from version
        self.__version = DUPLICATES.sub(r'\1', version)

        if '*' in self.__version:
            # Create a pattern to be use for cmparison
            self.__pattern = re.compile(re.sub(r'\*+', '[^*.]+', self.version))
        else:
            self.__pattern = None

    @property
    def version(self):
        return self.__version

    @property
    def pattern(self):
        return self.__pattern

    @staticmethod
    def compare_none(part1, part2):
        if part1 == part2:
            return 0
        elif part2 is None:
            # The one that DO NOT have more parts is greater
            return 1
        else:
            return -1

    @staticmethod
    def compare_sub_parts(sub1, sub2):
        # Sub parts are equal
        if sub1 == sub2:
            return 0

        # Check if any sub part is an integer
        is_integer = [False, False]
        for idx, value in enumerate((sub1, sub2)):
            try:
                int(value)
            except ValueError:
                is_integer[idx] = False
            else:
                is_integer[idx] = True

        # Compare both sub parts according to their type
        if is_integer[0] != is_integer[1]:
            # One is an integer. The integer is higher than the non integer.
            # Check if the first sub part is an integer, and if so it means
            # sub2 is lower than sub1.
            return -1 if is_integer[0] else 1

        # Both sub parts are of the same type
        return 1 if sub1 < sub2 else -1

    @classmethod
    def compare(cls, ver1, ver2):
        # Versions are equal
        if ver1 == ver2:
            return 0

        for part1, part2 in zip_longest(ver1.split('.'), ver2.split('.')):
            # One of the parts is None
            if part1 is None or part2 is None:
                return cls.compare_none(part1, part2)

            for sub1, sub2 in zip_longest(part1.split('-'), part2.split('-')):
                # One of the sub parts is None
                if sub1 is None or sub2 is None:
                    result = cls.compare_none(sub1, sub2)
                    if not result:
                        # Sub parts are equal, continue with next part
                        break

                    # Sub parts are different
                    return result

                # Both sub parts have a value
                result = cls.compare_sub_parts(sub1, sub2)
                if result:
                    # Sub parts are not equal
                    return result

        # By default return that versions are equal
        return 0

    def match(self, version):
        if not self.pattern:
            return self.version == version
        else:
            return self.pattern.fullmatch(version) is not None

    def resolve(self, versions):
        valid_versions = [ver for ver in versions if self.match(ver)]
        if not valid_versions:
            raise VersionNotFound(self.pattern)

        valid_versions.sort(key=cmp_to_key(self.compare))
        return valid_versions[0]
