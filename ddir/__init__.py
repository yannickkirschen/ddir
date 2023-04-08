"""Initializer."""

from __future__ import annotations

from dataclasses import dataclass


API_VERSION = 'v2'
ENCODING = 'utf-8'


@dataclass
class GlobalConfiguration:
    """
    Contains the content of `.ddir/ddir.json`

    Attributes:
        - api_version: version string that indicates which version the `.ddir` directory is formatted in
        - ignore: list of paths that should be ignored by ddir (regex)
    """
    api_version: str
    ignore: list[str]

    def to_json(self) -> dict:
        """Converts this `GlobalConfiguration` to a JSON dictionary"""

        return {
            'api-version': self.api_version,
            'ignore': self.ignore
        }

    @staticmethod
    def from_dict(data: dict) -> GlobalConfiguration:
        """ Creates an instance of `GlobalConfiguration` based on a JSON dict."""

        if not data.keys() & {'api-version', 'ignore'}:
            raise KeyError(f'Type GlobalConfiguration expects input keys (api-version, ignore). Given were {data.keys()}')

        return GlobalConfiguration(data['api-version'], data['ignore'])


class ProgramError(Exception):
    """A generic program error containing a message."""
    _message = ''
    _exit_code = 1

    def __init__(self, message='Error while executing the program', exit_code=1):
        super().__init__(message)
        self._message = message
        self._exit_code = exit_code

    @property
    def message(self) -> str:
        """Getter for the message."""
        return self._message

    @property
    def exit_code(self) -> int:
        """Getter for the exit code"""
        return self._exit_code

    @staticmethod
    def command_not_found(command: str) -> ProgramError:
        """Creates a `ProgramError` containing a message that a command could not be parsed."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   call of <ddir {command}>
   Result:  failed during parsing commands
   Reason:  unknown command "{command}" (exit code 100)
   Details: The command you entered does not exist or misses arguments.
            Try <ddir help> to get all available commands.
""", 100)

    @staticmethod
    def no_ddir(current_d: str) -> ProgramError:
        """Creates a `ProgramError` containing a message that the current directory is not controlled by ddir."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   a command that requires "{current_d} to be controlled by ddir
   Result:  failed during precondition check (exit code 2)
   Reason:  the current directory must be controlled by ddir to execute commands
   Details: {current_d} is not controlled by ddir.
            Execute <ddir init> to initialize it as a source.
""", 2)

    @staticmethod
    def is_ddir(current_d: str) -> ProgramError:
        """Creates a `ProgramError` containing a message that the current directory is already controlled by ddir."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   a command that requires "{current_d} is not controlled by ddir
   Result:  failed during precondition check (exit code 3)
   Reason:  the current directory is already controlled by directory
   Details: {current_d} is controlled by ddir. You cannot re-initialize it.
""", 3)

    @staticmethod
    def target_not_found(target: str) -> ProgramError:
        """Creates a `ProgramError` containing a message that a given target could not be found."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   a command that requires a target name as input
   Result:  failed while finding the target (exit code 10)
   Reason:  the target "{target}" does not exist
   Details: {target} is absent.
            Try using an existing target or list all targets with <ddir target list>.
""", 10)

    @staticmethod
    def target_already_exists(target: str) -> ProgramError:
        """Creates a `ProgramError` containing a message that a given target already exists."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   name of a target to create
   Result:  failed while creating the target (exit code 11)
   Reason:  the target "{target}" already exists
   Details: {target} is already present.
            Try using a different name or list all targets with <ddir target list>.
""", 11)

    @staticmethod
    def modes_invalid(modes: tuple) -> ProgramError:
        """Creates a `ProgramError` containing a message that given modes are invalid."""
        return ProgramError(f"""
🚧 Oops! An error occurred 🚧

   Input:   modes to resolve a diff
   Result:  failed while interpreting the modes (exit code 20)
   Reason:  modes {modes} are invalid
   Details: {modes} does not conform to the format of modes.
            There must be exactly five modes (provided {len(modes)}) and modes must be
            between 0 and 3 (provided: {min(modes)} and {max(modes)})
""", 11)
