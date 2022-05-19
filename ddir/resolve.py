import os
import shutil

import cli_args

from ddir import Diff, DiffFileParser, DiffType

cli_args.from_schema({
    'description': 'Resolve the diff of two directories.',
    'arguments': [
        {
            'short': 'f',
            'long': 'file',
            'var': 'FILE',
            'help': 'The diff file to resolve',
            'default': '',
            'type': 'str'
        },
        {
            'short': 's',
            'long': 'source',
            'var': 'DIRECTORY',
            'help': 'The source directory controlled by ddir (ddir init)',
            'default': '',
            'type': 'str'
        },
        {
            'short': 'm',
            'long': 'modes',
            'var': 'MODES',
            'help': 'The modes to apply when resolving the diffs',
            'default': '',
            'type': 'str'
        }
    ]
})

_mode_apply_actions_txt = {
    DiffType.POSITIVE: 'copy source to destination',
    DiffType.NEGATIVE: 'copy destination to source',
    DiffType.NEWER: 'override destination with source',
    DiffType.OLDER: 'override source with destination',
    DiffType.UNKNOWN: 'nothing'
}


def _get_mode_selection(diff: Diff):
    print('This diff requires your action:')
    print(f'    type: {diff.type}')
    print(f'    flag: {diff.flag}')
    print(f'    source: {diff.source}')
    print(f'    destination: {diff.destination}')
    print()
    print(f'Applying will {_mode_apply_actions_txt[diff.type]}')

    selection = input('Do you want to apply this diff? (y/N)')
    if selection == 'y':
        return 'y'

    return 'n'


def _get_mode_from_selection(mode: int, diff: Diff):
    if mode == 2 and _get_mode_selection(diff) == 'y':
        return 1

    return mode


def _copy_file_or_directory(source: str, destination: str):
    if os.path.isfile(source):
        shutil.copy(source, destination)
        print(f'Copied/overridden file {source} to {destination}')
    elif os.path.isdir(source):
        os.mkdir(destination)

        for file in os.listdir(source):
            abs_destination = os.sep.join([source, file])
            abs_source = os.sep.join([destination, file])

            shutil.copy(abs_destination, abs_source)
            print(f'Copied/overridden file {abs_destination} to {destination}')
    else:
        print(f'{source} does not exist anymore, thus is skipped')


def _copy_with_mode_check(mode: int, diff: Diff, source: str, destination: str):
    mode = _get_mode_from_selection(mode, diff)

    if mode == 0:
        print(f'Skip copy/override {source} to/with {destination}')
    elif mode == 1:
        _copy_file_or_directory(source, destination)


def resolve(diff_parser: DiffFileParser, modes=(0, 0, 0, 0, 0)):
    """Resolves all diffs from a given diff file.

    The modes work like this: for each type (the order is "+", "-", ">", "<", "?")
    a number in the tuple indicates how to handle diffs of that type. There are
    the following modes:
        - 0: skip
        - 1: apply (type dependent, see below)
        - 2: choose manually

    When choosing to apply diffs, the following will happen:
        - "+", ">", "?": override destination element with source element
        - "<": override source element with destination element
        - "-": delete destination element

    :param diff_parser: parser of the diff file to resolve
    :param modes: the modes to apply when resolving
    """
    if len(modes) != 5:
        raise ValueError(f'There must be exactly five modes (provided {len(modes)})')

    if max(modes) > 3 or min(modes) < 0:
        raise ValueError('Modes must be between x and y')

    for diff in diff_parser:
        if diff.type == DiffType.POSITIVE:
            _copy_with_mode_check(modes[0], diff, diff.source, diff.destination)
        elif diff.type == DiffType.NEGATIVE:
            _copy_with_mode_check(modes[1], diff, diff.destination, diff.source)
        elif diff.type == DiffType.NEWER:
            _copy_with_mode_check(modes[2], diff, diff.destination, diff.source)
        elif diff.type == DiffType.OLDER:
            _copy_with_mode_check(modes[3], diff, diff.destination, diff.source)
        elif diff.type == DiffType.UNKNOWN:
            pass


def resolve_from_args():
    abs_source = os.path.abspath(cli_args.argv['source'])

    dest_file = os.sep.join([abs_source, '.ddir', 'destination'])
    if not os.path.exists(dest_file):
        print(f'Directory {abs_source} not controlled by ddir. Execute ddir init before.')
        exit(-1)

    with DiffFileParser(os.sep.join([abs_source, '.ddir', cli_args.argv['file']])) as parser:
        resolve(parser, tuple(int(c) for c in cli_args.argv['modes']))
