"""Setup script for ddir."""

#!/usr/bin/env python3


from configparser import RawConfigParser

import setuptools


if __name__ == '__main__':
    config = RawConfigParser()
    config.read('setup.cfg')
    version = config.get('metadata', 'version')

    with open('ddir/__version__.py', 'r', encoding='utf-8') as file:
        newText=file.read().replace('development', version)

    with open('ddir/__version__.py', 'w', encoding='utf-8') as file:
        file.write(newText)

    setuptools.setup(
        entry_points={
            'console_scripts': [
                'ddir=ddir.__main__:main',
            ]
        }
    )
