from sys import argv

from ddir import create, init, resolve


def main():
    cmd = argv[1]

    if cmd == 'init':
        init.init_from_args()
    elif cmd == 'create':
        create.create_from_args()
    elif cmd == 'resolve':
        resolve.resolve_from_args()
    else:
        print(f'Command {cmd} unknown')
        exit(-1)


if __name__ == '__main__':
    main()
