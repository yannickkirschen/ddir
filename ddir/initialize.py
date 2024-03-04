"""Initializes a source directory."""

from json import dumps
from os import makedirs as mkdir, sep
from os.path import exists

from ddir import API_VERSION, ENCODING, GlobalConfiguration, ProgramError


def initialize(ddir: str) -> None:
    """Initializes an empty ddir source."""
    if exists(ddir):
        raise ProgramError.is_ddir(ddir)

    mkdir(ddir)

    raw_config = dumps(GlobalConfiguration(API_VERSION, ['.ddir', 'venv', '.DS_Store']).to_json(),
                       indent=2, separators=(',', ': '))
    with open(sep.join([ddir, 'ddir.json']), 'w', encoding=ENCODING) as file:
        file.write(raw_config)

    print('Initialized empty ddir source.')
