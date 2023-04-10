"""Main module for the CLI."""

from json import loads
from os import getcwd as pwd, sep
from os.path import exists
from sys import argv, exit as _exit

from ddir import __version__, diff, initialize, legacy, target, ENCODING, GlobalConfiguration, ProgramError


_CURRENT_DIRECTORY = pwd()
_DDIR = sep.join([_CURRENT_DIRECTORY, '.ddir'])
_TARGET_D = sep.join([_DDIR, 'target.d'])


def main():
    """Main."""
    command = argv[1:]
    match command:
        case ['help']: _handle_help()
        case ['version']: _handle_version()
        case ['init']: _handle_init()
        case ['diff', 'create', name]: _handle_diff_create(name)
        case ['diff', 'resolve', name, '--modes', modes]: _handle_diff_resolve(name, modes)
        case ['diff', 'list', name]: _handle_diff_list(name)
        case ['target', 'create']: _handle_target_create()
        case ['target', 'list']: _handle_target_list()
        case ['target', 'delete', name]: _handle_target_delete(name)
        case ['legacy', 'migrate']: _handle_legacy_migrate()
        case _: raise ProgramError.command_not_found(' '.join(command))


def _is_ddir_controlled(func):
    def wrapper(*args, **kwargs):
        if exists(_DDIR):
            func(*args, **kwargs)
        else:
            raise ProgramError.no_ddir(_CURRENT_DIRECTORY)

    return wrapper


def _handle_help() -> None:
    print("""Usage: ddir <commands>

Available commands:
    help                                - show this help
    version                             - show version
    init                                - initialize a source directory
    diff create <name>                  - create a diff for a target
    diff resolve <name> --modes <modes> - resolve a diff for a target
    diff list <name>                    - list all diffs for a target
    target create                       - create a target in interactive mode
    target list                         - list all targets
    target delete <name>                - delete target
    legacy migrate                      - migrate from legacy ddir

The modes work like this: for each type (the order is "+", "-", ">", "<", "?")
a number in the tuple indicates how to handle diffs of that type. There are
the following modes:
    - 0: skip
    - 1: apply (type dependent, see below)
    - 2: choose manually
""")


def _handle_init() -> None:
    initialize.initialize(_DDIR)


def _handle_version() -> None:
    print(f'ddir {__version__.VERSION}')


@_is_ddir_controlled
def _handle_diff_create(name: str) -> None:
    with open(sep.join([_DDIR, 'ddir.json']), 'r', encoding=ENCODING) as file:
        config = GlobalConfiguration.from_dict(loads(file.read()))

        _target = target.load(_TARGET_D, name)
        with diff.DiffFileCreator(sep.join([_TARGET_D, _target.hash.value])) as file:
            diff.create(file, _CURRENT_DIRECTORY, _target.path, _target.fast_mode, config.ignore)


@_is_ddir_controlled
def _handle_diff_resolve(name: str, modes: tuple) -> None:
    _target = target.load(_TARGET_D, name)
    diff_file = diff.ask_for(_target)

    with diff.DiffFileReader(diff_file.path) as parser:
        diff.resolve(parser, tuple(int(c) for c in modes))


@_is_ddir_controlled
def _handle_diff_list(name: str) -> None:
    _target = target.load(_TARGET_D, name)
    diffs = diff.load_diffs_meta(_target.this)

    print(f'Diffs for target {_target.name}:')
    for index, _diff in enumerate(diffs):
        print(f'  {index + 1}: {_diff.creation}')


@_is_ddir_controlled
def _handle_target_create() -> None:
    print(f'Creating a new target for source {_CURRENT_DIRECTORY}')
    target.create_interactive(_TARGET_D)


@_is_ddir_controlled
def _handle_target_list() -> None:
    targets = target.load_all(_TARGET_D)

    if len(targets) == 0:
        print('No targets found.')
    else:
        print(f'Targets for source {_CURRENT_DIRECTORY}:')
        for _target in target.load_all(_TARGET_D):
            print(f'    {_target.name} => {_target.path} ({"fast mode" if _target.fast_mode else "no fast mode"})')


@_is_ddir_controlled
def _handle_target_delete(name: str) -> None:
    target.delete(_TARGET_D, name)
    print(f'Deleted target {name}')


@_is_ddir_controlled
def _handle_legacy_migrate() -> None:
    legacy.migrate(_CURRENT_DIRECTORY, _DDIR, _TARGET_D)


if __name__ == '__main__':
    try:
        main()
    except ProgramError as e:
        print(e.message)
        _exit(e.exit_code)
