from __future__ import annotations

import os
import random
from dataclasses import dataclass
from datetime import date
from enum import Enum

__all__ = [
    'create',
    'resolve',
    'Diff',
    'DiffType',
    'DiffFileCreator',
    'DiffFileParser',
    'Flag'
]

ALLOWED_DIFF_TYPES = ('+', '-', '>', '<', '?')
ALLOWED_FLAGS = ('d', 'f')


def _directory_flag(element: str) -> str:
    return 'd' if os.path.isdir(element) else 'f'


class DiffFileCreator:
    """
    Write diffs to a text file.

    When instantiating this class, it will create a file of the form
    "yyyy-mm-dd-rand.diff", where yyyy-mm-dd is the current date and
    rand a random number.

    To learn more about the diff file format, visit https://ddir.yannick.sh/diff-file-format.
    """

    def __init__(self, directory='./'):
        file_name = f'{date.today()}-{random.randint(1, 1_000_000_000)}.diff'
        self._file_path = os.sep.join([directory, file_name])

    def add_diff(self, diff: Diff):
        self._file.write(diff.to_diff_format())

    def __enter__(self):
        self._file = open(self._file_path, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def __str__(self):
        return self._file_path

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self._file_path == other

    def __hash__(self):
        return self._file_path.__hash__()


class DiffType(Enum):
    POSITIVE = 0
    NEGATIVE = 1
    NEWER = 2
    OLDER = 3
    UNKNOWN = 4

    def to_diff_format(self) -> str:
        return ('+', '-', '>', '<', '?')[self.value]

    @staticmethod
    def from_diff_format(diff_type: str):
        if diff_type not in ALLOWED_DIFF_TYPES:
            raise ValueError(f'Types must be one of {ALLOWED_DIFF_TYPES} and not {diff_type}')

        if diff_type == '+':
            return DiffType.POSITIVE

        if diff_type == '-':
            return DiffType.NEGATIVE

        if diff_type == '>':
            return DiffType.NEWER

        if diff_type == '<':
            return DiffType.OLDER

        if diff_type == '?':
            return DiffType.UNKNOWN

    def __str__(self):
        if self.value == 0:
            return 'positive'

        if self.value == 1:
            return 'negative'

        if self.value == 2:
            return 'newer'

        if self.value == 3:
            return 'older'

        if self.value == 4:
            return 'unknown'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, DiffType):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__()


class Flag(Enum):
    DIRECTORY = 0
    FILE = 1

    def to_diff_format(self) -> str:
        return ('d', 'f')[self.value]

    @staticmethod
    def from_diff_format(flag: str):
        if flag not in ALLOWED_FLAGS:
            raise ValueError(f'Flags must be one of {ALLOWED_DIFF_TYPES} and not {flag}')

        return Flag.DIRECTORY if flag == 'd' else Flag.FILE

    def __str__(self):
        return 'directory' if self == self.value == 0 else 'file'


@dataclass
class Diff:
    type: DiffType
    flag: Flag
    source: str
    destination: str

    def to_diff_format(self) -> str:
        return f'{self.type.to_diff_format()}:{self.flag.to_diff_format()}:{self.source}:{self.destination}\n'

    @staticmethod
    def from_formatted_string(s: str) -> Diff:
        fields = s.split(':')

        if len(fields) != 4:
            raise ValueError(f'Diff "{s}" is invalid. Format is <type>:<element type>:<first element>:<second element>')

        if fields[0] not in ALLOWED_DIFF_TYPES:
            raise ValueError(f'Types must be one of {ALLOWED_DIFF_TYPES} and not {fields[0]}')

        return Diff(DiffType.from_diff_format(fields[0]),
                    Flag.from_diff_format(fields[1]),
                    fields[2],
                    fields[3])


class DiffFileParser:
    def __init__(self, file_path):
        self._file_path = file_path
        self._diff_at_current_iteration = None

    def __iter__(self):
        return self

    def __next__(self) -> Diff:
        line = self._file.__next__().strip()

        if line == '':
            line = self.__next__()

        self._diff_at_current_iteration = Diff.from_formatted_string(line)
        return self._diff_at_current_iteration

    def __enter__(self):
        self._file = open(self._file_path, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def __str__(self):
        return self._file_path

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self._file_path == other

    def __hash__(self):
        return self._file_path.__hash__()
