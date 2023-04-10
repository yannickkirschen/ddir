"""
This module is capable of working with legacy data models.

Its purpose is to migrate old source configurations to the latest version.
"""

from json import dumps
from os import sep, listdir, remove as rm
from os.path import exists, isfile
from shutil import copy2 as cp

from ddir import API_VERSION, ENCODING, GlobalConfiguration, target

def migrate(path: str, ddir: str, target_d: str) -> None:
    """Determines the current API version and upgrades to the latest one."""

    if exists(ddir) and not exists(target_d):
        print(f'Directory {path} under control of ddir v1. Migrating to v2 ...')
        _v1_to_v2(ddir, target_d)
        print('Migration complete')
    elif exists(target_d):
        print(f'Directory {path} already under control of ddir v2')
    else:
        print(f'Directory {path} is not under control of ddir or not able to migrate')


def _v1_to_v2(ddir: str, target_d: str) -> None:
    # Create .ddir/ddir.json with API version v2
    raw_config = dumps(GlobalConfiguration(API_VERSION, ignore=['.ddir', '.DS_Store']).to_json())
    with open(sep.join([ddir, 'ddir.json']), 'w', encoding=ENCODING) as file:
        file.write(raw_config)

    # Create target for the one and only existing destination (if it exists)
    destination_file = sep.join([ddir, 'destination'])
    fast_mode_file = sep.join([ddir, 'fast_mode'])

    if exists(destination_file):
        destination: str
        fast_mode: bool

        with open(destination_file, 'r', encoding=ENCODING) as dest:
            destination = dest.read().strip()
            print(f'Destination {destination} will result in a new target')

            fast_mode: bool
            if exists(fast_mode_file):
                with open(fast_mode_file, 'r', encoding=ENCODING) as fast:
                    fast_mode = fast.read().strip() == 'on'
                    print(f'Fast mode is {fast_mode}')
                rm(fast_mode_file)
            else:
                fast_mode = False
                print('Fast mode not defined, so inferring no fast mode')

            _target = target.create(target_d, 'default', destination, fast_mode)
            for element in listdir(ddir):
                diff = sep.join([ddir, element])
                if isfile(diff) and element.endswith('.diff'):
                    cp(diff, _target.this)
                    rm(diff)
                    print(f'Copied diff {element} to {_target.this}')

            rm(destination_file)
            print(f'Created target {_target.name}')
    else:
        print('There was no destination set, so no target is created')
