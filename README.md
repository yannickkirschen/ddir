# ddir

[![Lint commit message](https://github.com/yannickkirschen/ddir/actions/workflows/commit-lint.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/commit-lint.yml)
[![pytest](https://github.com/yannickkirschen/ddir/actions/workflows/push.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/push.yml)
[![release](https://github.com/yannickkirschen/ddir/actions/workflows/release.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/release.yml)
[![GitHub release](https://img.shields.io/github/release/yannickkirschen/ddir.svg)](https://github.com/yannickkirschen/ddir/releases/)

`ddir` is a command line tool to calculate diffs between two directories and
resolve them.

Check out the [diff file format](#the-diff-file-format) as well.

## Installation

`pip install ddir`

This will install a binary called `ddir` on your `PATH` that you can execute.
Depending on your system, you may need sudo/admin permissions.

## Usage

```txt
Usage: ddir <commands>

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
```

## Fast mode

If you just want to compare change dates of files and not their content
(md5 hash), you can use the fast mode. Set that option when creating a target.

## Modes to resolve

The modes work like this: for each type (the order is `+`, `-`, `>`, `<`, `?`)
a number in the tuple indicates how to handle diffs of that type. There are
the following modes:

- 0: skip
- 1: apply (type dependent, see below)
- 2: choose manually

When choosing to apply diffs, the following will happen:

- `+`, `>`, `?`: override destination element with source element
- `<`: override source element with destination element
- `-`: delete destination element

## The diff file format

A diff file stores the differences between a file or a directory at a source
compared to a destination.

### Specification

We call a file or a directory an **element**. The type of one element is either
`d` for *directory* or `f` for *file*.

We differentiate between five diff types:

- `+` (**positive diff**): an element exists in the source but not the
  destination
- `-` (**negative diff**): an element exists in the destination but not
  the source
- `>` (**newer diff**): the source element is newer than the destination element
- `<` (**older diff**): the source element is older than the destination element
- `?` (**unknown diff**): the elements are somehow different, but we can't
  categorize them; used if files differ but change dates are equal; requires
  manual resolution

The diff file is a newline-separated text file with each line containing an
individual diff. Each line has the format:

`{diff type}:{element type}:{first element}:{second element}`
