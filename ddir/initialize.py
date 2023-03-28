"""Initializes a source directory."""

from json import dumps
from os import makedirs as mkdir, sep
from os.path import exists

from ddir import API_VERSION, ENCODING, GlobalConfiguration, ProgramError


def initialize(directory: str) -> None:
    """Initializes an empty ddir source."""
    if exists(directory):
        raise ProgramError.is_ddir(directory)

    ddir = sep.join([directory, '.ddir'])
    mkdir(ddir)

    raw_config = dumps(GlobalConfiguration(API_VERSION, ['.ddir', '.DS_Store']).to_json())
    with open(sep.join([ddir, 'ddir.json']), 'w', encoding=ENCODING) as file:
        file.write(raw_config)

    print('Initialized empty ddir source.')
