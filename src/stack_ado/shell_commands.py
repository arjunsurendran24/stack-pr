from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path

if sys.version_info >= (3, 13):
    # Unpack moved to typing
    from typing import Any, Union
else:
    from typing import Union

    from typing_extensions import Any


logger = getLogger(__name__)

ShellCommand = Iterable[Union[str, Path]]


def run_shell_command(
    cmd: ShellCommand,
    *,
    quiet: bool,
    check: bool = True,
    dry_run: bool = False,
    **kwargs: Any,  # noqa: ANN401
) -> subprocess.CompletedProcess:
    """Runs a shell command using the arguments provided.

    This is essentially a wrapper around subprocess.run, with more reasonable
    default arguments, and some debug logging.

    Args:
        cmd: shell command to run.
        check: see subprocess.run for semantics.
        dry_run: if True, print the command instead of executing it.
        **kwargs: see subprocess.run for semantics
            (https://docs.python.org/3/library/subprocess.html#subprocess.run).

    Returns:
        A subprocess.CompletedProcess object.
    """
    if "shell" in kwargs:
        raise ValueError("shell support has been removed")
    cmd_str = subprocess.list2cmdline(cmd)

    if dry_run:
        print(f"[DRY RUN] {cmd_str}")
        # Return a mock CompletedProcess object
        return subprocess.CompletedProcess(
            args=list(map(str, cmd)),
            returncode=0,
            stdout=b"" if kwargs.get("capture_output") else None,
            stderr=b"" if kwargs.get("capture_output") else None,
        )

    if quiet:
        kwargs.update({"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL})
    logger.debug("Running: %s", cmd)
    return subprocess.run(list(map(str, cmd)), **kwargs, check=check)


def get_command_output(
    cmd: ShellCommand,
    **kwargs: Any,  # noqa: ANN401
) -> str:
    """A wrapper over run_shell_command that captures stdout into a string.

    Args:
        cmd: shell command to run.
        **kwargs: see run_shell_command for semantics. Passing capture_output is
            not allowed.

    Returns:
        Captured stdout of the command as a string.

    Raises:
        ValueError: if the capture_output keyword argument is specified.
    """
    if "capture_output" in kwargs:
        raise ValueError("Cannot pass capture_output when using get_command_output")
    proc = run_shell_command(cmd, capture_output=True, quiet=False, **kwargs)
    return str(proc.stdout.decode("utf-8").rstrip())
