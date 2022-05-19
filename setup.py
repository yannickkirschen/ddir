#!/usr/bin/env python3


import setuptools

if __name__ == '__main__':
    setuptools.setup(
        entry_points={
            'console_scripts': [
                'ddir=ddir.__main__:main',
            ]
        }
    )
