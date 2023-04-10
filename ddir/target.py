"""
This module is capable of working with target metadata.

All target metadata is usually stored in a directory called `target.d`, though this can be configured. Each target has
its own subdirectory named after the MD5 hash of the human-friendly target name. Inside that directory is a file called
`target.json` which contains all metadata of that target.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
from json import dumps, loads
from os import listdir, makedirs as mkdir, sep
from os.path import abspath, exists, isdir, isfile
from shutil import rmtree as rmdir
from typing import List

from ddir import ENCODING, ProgramError


@dataclass
class Hash:
    """
    Information on a hash value.

    Attributes:
        - algo: algorithm used to calculate the hash
        - value: calculated hash value
    """

    algo: str
    value: str

    def to_json(self) -> dict:
        """Converts this `Meta` to a JSON dictionary"""

        return {
            'algo': self.algo,
            'value': self.value
        }

    @staticmethod
    def from_dict(data: dict) -> Hash:
        """ Creates an instance of `Meta` based on a JSON dict."""

        if not data.keys() & {'algo', 'value'}:
            raise KeyError(f'Type Hash expects input keys (algo, value). Given were {data.keys()}')

        return Hash(data['algo'], data['value'])


@dataclass
class Target:
    """
    Information on a single target.

    Attributes:
        - name: human-friendly name of the target
        - hash: hash value of the name to be used by the machine
        - this: absolute path of the target's config directory (i.e. the path the `target.json` file is located)
        - path: absolute path of the target
        - fast_mode: whether to use fast mode when creating a diff or not
    """

    name: str
    hash: Hash
    this: str
    path: str
    fast_mode: bool

    def to_json(self) -> dict:
        """Converts this `Target` to a JSON dictionary"""

        return {
            'name': self.name,
            'hash': self.hash.to_json(),
            'this': self.this,
            'path': self.path,
            'fast-mode': self.fast_mode
        }

    @staticmethod
    def from_dict(data: dict) -> Target:
        """Creates an instance of `Target` based on a JSON dict."""

        if not data.keys() & {'name', 'hash', 'this', 'path', 'fast-mode'}:
            raise KeyError(f'Type Target expects input keys (name, hash, this, path, fast-mode). Given were {data.keys()}')

        return Target(
            data['name'],
            Hash.from_dict(data['hash']),
            data['this'],
            data['path'],
            bool(data['fast-mode'])
        )


def load_all(target_d: str) -> List[Target]:
    """
    Loads all targets from a given target directory.

    This means, the directory `target_d` will be scanned for subdirectories containing a `target.json` file. That file
    contains the data in a `Target` object.

    :param target_d: absolute path to the `target.d` directory containing all targets

    :return: a list of targets
    """

    targets = []

    for target_directory_element in listdir(target_d):
        target_directory = sep.join([target_d, target_directory_element])
        if isdir(target_directory):
            for target_file_element in listdir(target_directory):
                target_file = sep.join([target_directory, target_file_element])
                if isfile(target_file) and target_file_element == 'target.json':
                    with open(target_file, 'r', encoding=ENCODING) as target_file_element:
                        raw_json = loads(target_file_element.read().strip())
                        target = Target.from_dict(raw_json)
                        target.this = target_directory
                        targets.append(target)

    return targets


def load(target_d: str, name: str) -> Target:
    """
    Loads a `Target` based on its human-friendly name from a target directory.

    This means, the directory `target_d` will be scanned for subdirectories containing a `target.json` with the
    specified name.

    :param target_d: absolute path to the `target.d` directory containing all targets
    :param name: human-friendly name of the target to load

    :return: a `Target`

    :raises ProgramError: if there is no target with the given name
    """

    for target in load_all(target_d):
        if target.name == name:
            return target

    raise ProgramError.target_not_found(name)


def create(target_d: str, name: str, path: str, fast_mode: bool) -> Target:
    """Creates a new target in a non-interactive mode."""

    hash_name = md5(name.encode(ENCODING)).hexdigest()
    target = Target(
        name,
        Hash('md5', hash_name),
        sep.join([target_d, hash_name]),
        abspath(path),  # Just to be sure we really have the abs path
        fast_mode
    )

    if exists(target.this):
        raise ProgramError.target_already_exists(target.name)

    mkdir(target.this)
    with open(sep.join([target.this, 'target.json']), 'w', encoding=ENCODING) as file:
        file.write(dumps(target.to_json(), indent = 2, separators=(',', ': ')))

    return target


def create_interactive(target_d: str) -> Target:
    """Creates a new target in an interactive mode."""

    target = None
    while target is None:
        name = input('Name: ')
        path = input('Path: ')
        fast_mode = input('Fast mode (Y/n): ') in ('Y', 'y', '')

        if name != '' and path != '':
            target = create(target_d, name, path, fast_mode)
            print(f'Target {target.name} created')

    return target


def delete(target_d: str, name: str) -> None:
    """Deletes a target."""
    target = load(target_d, name)
    rmdir(target.this)
