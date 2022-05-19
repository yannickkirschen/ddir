import hashlib
import os

import cli_args

from ddir import Diff, DiffFileCreator, DiffType, Flag

cli_args.from_schema({
    'description': 'Get the diff of two directories.',
    'arguments': [
        {
            'short': 's',
            'long': 'source',
            'var': 'DIRECTORY',
            'help': 'The source directory controlled by ddir (ddir init)',
            'default': '',
            'type': 'str'
        }
    ]
})


def create(diff_file: DiffFileCreator, source: str, destination: str):
    """Calculates the diff of two directories and saves it in a diff file.

    :param diff_file: the file to store the diff in
    :param source: directory to use as source for comparisons
    :param destination: directory to use as destination for comparisons
    """

    for element in os.listdir(source):
        if element == '.ddir':
            continue

        source_element = os.sep.join([source, element])
        destination_element = os.sep.join([destination, element])

        if os.path.isdir(source_element):
            if not os.path.exists(destination_element):
                print(f'directory not in destination: {source_element}')
                diff_file.add_diff(Diff(DiffType.POSITIVE, Flag.DIRECTORY, source_element, destination_element))
            else:
                create(diff_file, source_element, destination_element)
        else:
            if not os.path.exists(destination_element):
                print(f'file not in destination: {source_element} {destination_element}')
                diff_file.add_diff(Diff(DiffType.POSITIVE, Flag.FILE, source_element, destination_element))
            else:
                source_md5 = hashlib.md5(open(source_element, 'rb').read()).hexdigest()
                destination_md5 = hashlib.md5(open(destination_element, 'rb').read()).hexdigest()

                if source_md5 != destination_md5:
                    source_last_changed = os.stat(source_element).st_mtime
                    destination_last_changed = os.stat(destination_element).st_mtime

                    if source_last_changed > destination_last_changed:
                        print(f'files differ: {source_element} is newer than {destination_element}')
                        diff_file.add_diff(Diff(DiffType.NEWER, Flag.FILE, source_element, destination_element))
                    elif destination_last_changed > source_last_changed:
                        print(f'files differ: {destination_element} is newer than {source_element}')
                        diff_file.add_diff(Diff(DiffType.OLDER, Flag.FILE, source_element, destination_element))
                    else:
                        print(f'files differ: {source_element} (change dates are equal)')
                        diff_file.add_diff(Diff(DiffType.UNKNOWN, Flag.FILE, source_element, destination_element))


def create_from_args():
    abs_source = os.path.abspath(cli_args.argv['source'])

    dest_file = os.sep.join([abs_source, '.ddir', 'destination'])
    if os.path.exists(dest_file):
        with open(dest_file, 'r') as file:
            abs_destination = file.read().strip()
    else:
        print(f'Directory {abs_source} not controlled by ddir. Execute ddir init before.')
        exit(-1)

    with DiffFileCreator(os.sep.join([abs_source, '.ddir'])) as file:
        create(file, abs_source, abs_destination)
