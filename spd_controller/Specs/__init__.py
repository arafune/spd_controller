"""Top level module for Specs."""

from __future__ import annotations

from datetime import UTC
import datetime
from pathlib import Path
import json
import urllib.request
from urllib.error import HTTPError
from typing import TypedDict, Required

from traitlets.config import MultipleInstanceError
import ipykernel
from jupyter_server import serverapp


module_name = __name__


class ServerInfo(TypedDict, total=False):
    base_url: str
    password: bool
    pid: int
    port: int
    root_dir: str
    secure: bool
    sock: str
    token: str
    url: str
    version: str


class SessionInfo(TypedDict, total=False):
    id: str
    path: str
    name: str
    type: str
    kernel: dict[str, str | int]
    notebook: Required[dict[str, str]]


class NoteBookInfomation(TypedDict, total=True):
    server: ServerInfo
    session: SessionInfo


def start_logging() -> None:
    """
    Starts logging IPython session to a file.

    This function checks if the current IPython instance is an InteractiveShell.
    If it is, it generates a log file path, creates the necessary directories,
    and starts logging the session to the generated log file.
    """
    from IPython.core.getipython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell

    ipython = get_ipython()
    if isinstance(ipython, InteractiveShell):
        log_path: Path = generate_logfile_path()
        log_path.parent.mkdir(exist_ok=True)
        _ = ipython.run_line_magic("logstart", f"-o -t {str(log_path)}")


def generate_logfile_path() -> Path:
    """Generates a time and date qualified path for the notebook log file."""
    full_name = "{}_{}_{}.log".format(
        get_notebook_name(),
        datetime.datetime.now(tz=datetime.UTC).date().isoformat(),
        datetime.datetime.now(UTC).time().isoformat().split(".")[0].replace(":", "-"),
    )
    return Path("logs") / full_name


def get_notebook_name() -> str:
    """Gets the unqualified name of the running Jupyter notebook if not password protected.

    As an example, if you were running a notebook called "Doping-Analysis.ipynb"
    this would return "Doping-Analysis".

    If no notebook is running for this kernel or the Jupyter session is password protected, we
    can only return None.
    """
    jupyter_info = get_full_notebook_information()
    if jupyter_info:
        return Path(jupyter_info["session"]["notebook"]["name"]).stem
    return "unnamed"


def get_full_notebook_information() -> NoteBookInfomation | None:
    """Javascriptless method to fetch current notebook sessions and the one matching this kernel.

    Returns:
        NoteBookInfomation | None : The full information of the notebook if available. If the
        notebook information is not available, return None.
    """
    try:
        connection_file = Path(ipykernel.get_connection_file()).stem
    except (MultipleInstanceError, RuntimeError):
        return None

    kernel_id = (
        connection_file.split("-", 1)[1] if "-" in connection_file else connection_file
    )

    servers = serverapp.list_running_servers()
    for server in servers:
        try:
            passwordless = not server["token"] and not server["password"]
            url = (
                server["url"]
                + "api/sessions"
                + ("" if passwordless else "?token={}".format(server["token"]))
            )
            if not url.startswith(("http:", "https:")):
                msg = "URL must start with 'http:' or 'https:'"
                raise ValueError(msg)
            sessions = json.load(urllib.request.urlopen(url))
            for sess in sessions:
                if sess["kernel"]["id"] == kernel_id:
                    return {
                        "server": server,
                        "session": sess,
                    }
        except (KeyError, TypeError):
            pass
        except HTTPError:
            pass
    return None
