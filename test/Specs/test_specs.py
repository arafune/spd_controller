"""Unit test for Specs."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from IPython.core.interactiveshell import InteractiveShell
import spd_controller.Specs as specs  # ← モジュール名に合わせてください


###########
# get_tqdm
###########
def test_get_tqdm_cli(monkeypatch):
    # CLI環境: get_ipython()がNoneを返す
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: None)
    tqdm_func = specs.get_tqdm()
    assert tqdm_func is specs.cli_tqdm


def test_get_tqdm_notebook(monkeypatch):
    # specsモジュールのZMQInteractiveShellを継承
    class DummyShell(specs.ZMQInteractiveShell):
        pass

    # specsモジュール内のget_ipythonを直接モック
    monkeypatch.setattr(specs, "get_ipython", lambda: DummyShell())
    tqdm_func = specs.get_tqdm()
    assert hasattr(tqdm_func, "__globals__"), (
        f"{type(tqdm_func)} is not a function object"
    )

    mock_nb_tqdm = MagicMock()
    tqdm_func.__globals__["notebook_tqdm"] = mock_nb_tqdm

    tqdm_func(range(3))
    mock_nb_tqdm.assert_called_once()
    assert mock_nb_tqdm.call_args[1]["leave"] is False


#################
# generate_logfile_path
#################
def test_generate_logfile_path(monkeypatch):
    # notebook名とdatetimeをモック
    monkeypatch.setattr(specs, "get_notebook_name", lambda: "FooBar")
    dt = specs.datetime.datetime(2024, 6, 1, 12, 34, 56, tzinfo=specs.UTC)
    monkeypatch.setattr(specs.datetime, "datetime", MagicMock(now=lambda tz=None: dt))
    path = specs.generate_logfile_path()
    assert isinstance(path, Path)
    assert path.parts[0] == "logs"
    assert "FooBar" in str(path)
    assert "2024-06-01" in str(path)
    assert "12-34-56" in str(path)


##################
# get_notebook_name
##################
def test_get_notebook_name(monkeypatch):
    # 情報がある時
    monkeypatch.setattr(
        specs,
        "get_full_notebook_information",
        lambda: {"session": {"notebook": {"name": "Doping-Analysis.ipynb"}}},
    )
    assert specs.get_notebook_name() == "Doping-Analysis"
    # 情報がない時
    monkeypatch.setattr(specs, "get_full_notebook_information", lambda: None)
    assert specs.get_notebook_name() == "unnamed"


##################
# start_logging
##################


def test_start_logging(monkeypatch, tmp_path):
    # InteractiveShellを明示的に継承
    class DummyShell(InteractiveShell):
        def __init__(self):
            super().__init__()
            self.called = None

        def run_line_magic(self, name, arg):
            self.called = (name, arg)

    dummy_shell = DummyShell()
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: dummy_shell)
    monkeypatch.setattr(specs, "generate_logfile_path", lambda: tmp_path / "foo.log")
    specs.start_logging()
    assert dummy_shell.called is not None
    assert dummy_shell.called[0] == "logstart"
    assert "foo.log" in dummy_shell.called[1]


def test_start_logging_not_interactive(monkeypatch):
    # InteractiveShell以外の場合は何もしない
    monkeypatch.setattr("IPython.core.getipython.get_ipython", lambda: None)
    assert specs.start_logging() is None


##################
# get_full_notebook_information
##################
@pytest.mark.parametrize("passwordless", [True, False])
def test_get_full_notebook_information(monkeypatch, passwordless):
    # 必要な情報をモック
    # - ipykernel.get_connection_file()
    # - serverapp.list_running_servers()
    # - urllib.request.urlopen
    kernel_id = "abcdef"
    # connection_file: kernel-abcdef.json
    monkeypatch.setattr(
        specs.ipykernel, "get_connection_file", lambda: f"kernel-{kernel_id}.json"
    )
    server = {
        "url": "http://localhost:8888/",
        "token": "" if passwordless else "secret-token",
        "password": False if passwordless else True,
        "base_url": "/",
    }
    monkeypatch.setattr(specs.serverapp, "list_running_servers", lambda: [server])
    sessions = [
        {"kernel": {"id": kernel_id}, "notebook": {"name": "test-notebook.ipynb"}}
    ]

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def read(self):
            return b""

    monkeypatch.setattr(specs.json, "load", lambda fp: sessions)
    monkeypatch.setattr(specs.urllib.request, "urlopen", lambda url: None)
    info = specs.get_full_notebook_information()
    assert info is not None
    assert info["server"] == server
    assert info["session"] == sessions[0]


def test_get_full_notebook_information_no_kernel(monkeypatch):
    # ipykernel.get_connection_fileが例外
    monkeypatch.setattr(
        specs.ipykernel,
        "get_connection_file",
        lambda: (_ for _ in ()).throw(specs.MultipleInstanceError()),
    )
    assert specs.get_full_notebook_information() is None


def test_get_full_notebook_information_http_error(monkeypatch):
    # HTTPError発生でもNone
    monkeypatch.setattr(
        specs.ipykernel, "get_connection_file", lambda: "kernel-abcdef.json"
    )
    monkeypatch.setattr(
        specs.serverapp,
        "list_running_servers",
        lambda: [
            {
                "url": "http://localhost:8888/",
                "token": "",
                "password": False,
                "base_url": "/",
            }
        ],
    )
    monkeypatch.setattr(
        specs.urllib.request,
        "urlopen",
        lambda url: (_ for _ in ()).throw(
            specs.HTTPError(url, 404, "Not found", None, None)
        ),
    )
    monkeypatch.setattr(specs.json, "load", lambda x: [])
    assert specs.get_full_notebook_information() is None


def test_get_full_notebook_information_url_error(monkeypatch):
    # URLがhttp/https以外でValueError
    monkeypatch.setattr(
        specs.ipykernel, "get_connection_file", lambda: "kernel-abcdef.json"
    )
    monkeypatch.setattr(
        specs.serverapp,
        "list_running_servers",
        lambda: [
            {
                "url": "file://localhost:8888/",
                "token": "",
                "password": False,
                "base_url": "/",
            }
        ],
    )
    monkeypatch.setattr(specs.urllib.request, "urlopen", lambda url: None)
    monkeypatch.setattr(specs.json, "load", lambda x: [])
    assert specs.get_full_notebook_information() is None
