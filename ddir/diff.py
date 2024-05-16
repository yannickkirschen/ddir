"""
This module is capable of working with diffs.

All diffs are stored in `*.diff` files located in each targets subdirectory in
`.ddir/target.d`. Diffs can be created and resolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from hashlib import md5
from os import sep, listdir, mkdir, stat
from os.path import exists, isfile, isdir
from random import randint as rand
from re import match
from shutil import copy2 as cp
from time import localtime, strftime
from typing import List

from ddir import ENCODING, ProgramError
from ddir.target import Target


@dataclass
class Meta:
    """
    Metadata for a diff.

    Attributes:
        - path: absolute path of the diff (the `.diff` file)
        - creation: human-friendly datetime of the creation of the diff
    """

    path: str
    creation: str


class DiffType(Enum):
    """
    Defines the type of a diff.

    The types are defined as following:
        - positive: source element not present in target
        - negative: target element not present in source
        - newer: source element newer than target element
        - older: source element older than target element
        - unknown: we don't know
    """

    POSITIVE = 0, '+', 'copy source to target'
    NEGATIVE = 1, '-', 'copy target to source'
    NEWER = 2, '>', 'override target with source'
    OLDER = 3, '<', 'override source with target'
    UNKNOWN = 4, '?', 'nothing'

    @staticmethod
    def from_symbol(symbol: str) -> DiffType:
        """Creates a `DiffType` based on a symbol."""
        match symbol:
            case '+': return DiffType.POSITIVE
            case '-': return DiffType.NEGATIVE
            case '>': return DiffType.NEWER
            case '<': return DiffType.OLDER
            case '?': return DiffType.UNKNOWN
            case _: raise ValueError(f'Unknown symbol for DiffType: {symbol}.')

    def index(self) -> int:
        """Returns the index of that `DiffType`."""
        return self.value[0]

    def symbol(self) -> str:
        """Returns the symbol of that `DiffType`."""
        return self.value[1]

    def description(self) -> str:
        """Returns the description of that `DiffType`."""
        return self.value[2]

    # pylint: disable=E0307
    def __str__(self) -> str:
        match self.value[0]:
            case 0: return 'positive'
            case 1: return 'negative'
            case 2: return 'newer'
            case 3: return 'older'
            case _: return 'unknown'


@dataclass
class Diff:
    """
    A single diff.

    Attributes:
        - type: type of the diff
        - flag: 'd' if it is a directory, otherwise `f` for file
        - source: absolute source path
        - target: absolute target path
    """

    type: DiffType
    flag: str
    source: str
    target: str

    def to_diff_format(self) -> str:
        """Formats the diff to be stored in a `.diff` file."""
        return f'{self.type.symbol()}:{self.flag}:{self.source}:{self.target}\n'

    @staticmethod
    def from_formatted_string(string: str) -> Diff:
        """Creates a `Diff` from a formatted string."""

        fields = string.split(':')

        if len(fields) != 4:
            raise ValueError(f'Diff "{string}" is invalid. Format is <type>:<element type>:<first element>:<second element>')

        return Diff(DiffType.from_symbol(fields[0]),
                    fields[1],
                    fields[2],
                    fields[3])


class DiffFileCreator:
    """
    Write diffs to a text file.

    When instantiating this class, it will create a file of the form
    "yyyy-mm-dd-rand.diff", where yyyy-mm-dd is the current date and
    rand a random number.

    To learn more about the diff file format, visit https://ddir.yannick.sh/diff-file-format.
    """

    def __init__(self, directory='./'):
        self._file = None
        file_name = f'{date.today()}-{rand(1, 1_000_000_000)}.diff'
        self._file_path = sep.join([directory, file_name])

    def add_diff(self, diff: Diff):
        """Adds a diff to the `.diff` file."""
        self._file.write(diff.to_diff_format())

    def __enter__(self):
        self._file = open(self._file_path, 'w', encoding=ENCODING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()


class DiffFileReader:
    """Reads a `.diff` file."""

    def __init__(self, file_path):
        self._file = None
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
        self._file = open(self._file_path, 'r', encoding=ENCODING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()


def load_diffs_meta(path: str) -> List[Meta]:
    """
    Loads metadata of all diffs.

    :param path: absolute path to scan for `.diff` files.
    """

    diffs = []

    for element in listdir(path):
        diff = sep.join([path, element])
        if isfile(diff) and element.endswith('.diff'):
            creation = stat(diff).st_mtime  # re.sub('-\d*.diff', '', element)
            meta = Meta(diff, strftime('%Y-%m-%d %H:%M:%S', localtime(creation)))
            diffs.append(meta)

    return sorted(diffs, key=lambda diff: diff.creation)


def ask_for(target: Target) -> Meta:
    """Loads all diffs of a target and asks for user input to choose a diff."""

    diffs = load_diffs_meta(target.this)

    print(f'Diffs for target {target.name}:')
    for index, diff in enumerate(diffs):
        print(f'  {index + 1}: {diff.creation}')

    index = -1
    while index == -1:
        selection = input('Choose a diff to resolve: ')
        try:
            index = int(selection) - 1
        except ValueError:
            print('Error: enter a number')

        if index > len(diffs) - 1:
            print('Error: enter a given number')
            index = -1

    return diffs[index]


def create(diff_file: DiffFileCreator, source: str, target: str, fast: bool, ignore: List[str]) -> None:
    """Calculates the diff of two directories and saves it in a diff file.

    :param diff_file: the file to store the diff in
    :param source: directory to use as source for comparisons
    :param target: directory to use as target for comparisons
    :param fast: use fast mode or not (fast mode ignores MD5 if dates are different)
    """

    for element in listdir(source):
        if len([ignored for ignored in [match(ig.replace('*', r'[\w \s]*'), element) for ig in ignore] if ignored is not None]) != 0:
            continue

        source_element = sep.join([source, element])
        target_element = sep.join([target, element])

        if isdir(source_element):
            _create_for_directory(diff_file, source_element, target_element, fast, ignore)
        else:
            _create_for_file(diff_file, source_element, target_element, fast)


def _create_for_directory(diff: DiffFileCreator, source: str, target: str, fast: bool, ignore: List[str]) -> None:
    if not exists(target):
        print(f'directory not in target: {source}')
        diff.add_diff(Diff(DiffType.POSITIVE, 'd', source, target))
    else:
        create(diff, source, target, fast, ignore)


def _create_for_file(diff: DiffFileCreator, source: str, target: str, fast: bool) -> None:
    if not exists(target):
        print(f'file not in target: {source} {target}')
        diff.add_diff(Diff(DiffType.POSITIVE, 'f', source, target))
    else:
        source_last_changed = stat(source).st_mtime
        target_last_changed = stat(target).st_mtime

        source_last_changed_str = datetime.fromtimestamp(source_last_changed).isoformat()
        target_last_changed_str = datetime.fromtimestamp(target_last_changed).isoformat()

        if not _float_sneaky_equals(source_last_changed, target_last_changed) and source_last_changed > target_last_changed:
            print(f'[metadata] files differ: {source} is newer than {target} ({source_last_changed_str} > {target_last_changed_str})')
            diff.add_diff(Diff(DiffType.NEWER, 'f', source, target))
        elif not _float_sneaky_equals(source_last_changed, target_last_changed) and target_last_changed > source_last_changed:
            print(f'[metadata] files differ: {target} is newer than {source} ({target_last_changed_str} > {source_last_changed_str})')
            diff.add_diff(Diff(DiffType.OLDER, 'f', source, target))
        elif not fast:
            with open(source, 'rb', encoding=ENCODING) as source_file, \
                    open(target, 'rb', encoding=ENCODING) as target_file:
                source_md5 = md5(source_file.read()).hexdigest()
                target_md5 = md5(target_file.read()).hexdigest()

                if source_md5 != target_md5:
                    print(f'[content ] files differ: {source}')
                    diff.add_diff(Diff(DiffType.UNKNOWN, 'f', source, target))


def _float_sneaky_equals(a: float, b: float) -> bool:
    a_len_d = len(str(a).split('.')[1])
    b_len_d = len(str(b).split('.')[1])

    if a_len_d == b_len_d:
        return 0 if a == b else 1

    if a_len_d < b_len_d:
        return a == _truncate_float(b, a_len_d)

    return _truncate_float(a, b_len_d) == b


def _truncate_float(f: float, n: int) -> float:
    """Truncates/pads a float f to n decimal places without rounding"""
    s = str(f)
    if 'e' in s or 'E' in s:
        return float(f'{0:.{f}f}')

    i, _, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))


def resolve(reader: DiffFileReader, modes=(0, 0, 0, 0, 0)) -> None:
    """Resolves all diffs from a given diff file.

    The modes work like this: for each type (the order is "+", "-", ">", "<", "?")
    a number in the tuple indicates how to handle diffs of that type. There are
    the following modes:
        - 0: skip
        - 1: apply (type dependent, see below)
        - 2: choose manually

    When choosing to apply diffs, the following will happen:
        - "+", ">", "?": override target element with source element
        - "<": override source element with target element
        - "-": delete target element

    :param reader: reader of the diff file to resolve
    :param modes: the modes to apply when resolving

    :raise ProgramError: if the modes are mal formatted
    """
    if len(modes) != 5 or max(modes) > 3 or min(modes) < 0:
        raise ProgramError.modes_invalid(modes)

    for diff in reader:
        type_index = diff.type.index()
        _copy_with_mode_check(modes[type_index], diff, diff.source, diff.target)


def _get_mode_selection(diff: Diff) -> str:
    print('This diff requires your action:')
    print(f'    type: {str(diff.type)}')
    print(f'    flag: {diff.flag}')
    print(f'    source: {diff.source}')
    print(f'    target: {diff.target}')
    print()
    print(f'Applying will {diff.type.description()}')

    selection = input('Do you want to apply this diff? (y/N) ')
    if selection == 'y':
        return 'y'

    return 'n'


def _get_mode_from_selection(mode: int, diff: Diff) -> int:
    if mode == 2 and _get_mode_selection(diff) == 'y':
        return 1

    return mode


def _copy_file_or_directory(source: str, target: str) -> None:
    if isfile(source):
        cp(source, target)
        print(f'Copied/overridden file {source} to {target}')
    elif isdir(source):
        mkdir(target)

        for file in listdir(source):
            abs_target = sep.join([source, file])
            abs_source = sep.join([target, file])

            cp(abs_target, abs_source)
            print(f'Copied/overridden file {abs_target} to {target}')
    else:
        print(f'{source} does not exist anymore, thus is skipped')


def _copy_with_mode_check(mode: int, diff: Diff, source: str, target: str) -> None:
    mode = _get_mode_from_selection(mode, diff)

    if mode == 0:
        print(f'Skip copy/override {source} to/with {target}')
    elif mode == 1 and diff.type in [DiffType.POSITIVE, DiffType.NEWER, DiffType.UNKNOWN]:
        _copy_file_or_directory(source, target)
    elif mode == 1 and diff.type == DiffType.OLDER:
        _copy_file_or_directory(target, source)  # pylint: disable=W1114
    elif mode == 1 and diff.type == DiffType.NEGATIVE:
        print(f'File {target} should be deleted but deletion is not implemented yet')
