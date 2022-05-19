# The diff file format

A diff file stores the differences between a file or a directory at a source
compared to a destination.

## Specification

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
