import os

import cli_args

cli_args.from_schema({
    'description': 'Initialize a directory to be controlled by ddir.',
    'arguments': [
        {
            'short': 's',
            'long': 'source',
            'var': 'DIRECTORY',
            'help': 'The source directory controlled by ddir',
            'default': './',
            'type': 'str'
        },
        {
            'short': 'd',
            'long': 'destination',
            'var': 'DIRECTORY',
            'help': 'The destination directory to be controlled by ddir',
            'default': '',
            'type': 'str'
        },
        {
            'short': 'f',
            'long': 'fast',
            'var': 'FAST',
            'help': 'Do not check md5 hash (on/off)',
            'default': 'off',
            'type': 'str'
        }
    ]
})


def init(source: str, destination: str, fast: bool):
    dot_dir = os.sep.join([source, '.ddir'])
    if not os.path.exists(dot_dir):
        os.mkdir(dot_dir)

        with open(os.sep.join([dot_dir, 'destination']), 'w') as file:
            file.write(f'{destination}')

        with open(os.sep.join([dot_dir, 'fast_mode']), 'w') as file:
            fast_mode = 'on' if fast else 'off'
            file.write(fast_mode)
            print(f'Fast mode is {fast_mode}')

        print(f'Initialized {source}')
    else:
        print(f'Directory {source} is already under control of ddir')
        exit(0)


def init_from_args():
    init(os.path.abspath(cli_args.argv['source']),
         os.path.abspath(cli_args.argv['destination']),
         cli_args.argv['fast'])
