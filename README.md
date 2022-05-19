# ddir

[![Lint commit message](https://github.com/yannickkirschen/ddir/actions/workflows/commit-lint.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/commit-lint.yml)
[![Release Drafter](https://github.com/yannickkirschen/ddir/actions/workflows/release-drafter.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/release-drafter.yml)
[![pytest](https://github.com/yannickkirschen/ddir/actions/workflows/push.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/push.yml)
[![release](https://github.com/yannickkirschen/ddir/actions/workflows/release.yml/badge.svg)](https://github.com/yannickkirschen/ddir/actions/workflows/release.yml)
[![GitHub license](https://img.shields.io/github/license/yannickkirschen/ddir.svg)](https://github.com/yannickkirschen/ddir/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/release/yannickkirschen/ddir.svg)](https://github.com/yannickkirschen/ddir/releases/)

`ddir` is a command line tool to calculate diffs between two directories and
resolve them.

Check out the [diff file format](docs/diff-file-format.md) as well.

## Usage

### Initialize

This will create a directory `.ddir` in the source directory where all diffs
will be stored as well as a reference to the destination directory.

`ddir init --source <path> --destination <path>`

### Create diff

This will traverse the source directory, compare it to the destination
directory and store ste diff in `.ddir`.

`ddir create --source <path>`

### Resolve diff

This will iterate through all diffs in a given diff file and apply them
according to given modes.

`ddir resolve --source <path> --file 2022-05-19-806383729.diff --modes xxxxx`

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
