"""Unit test for Specs.remote_in."""

import pytest
from unittest.mock import MagicMock, patch
import numpy as np

import spd_controller.Specs.Prodigy as prodigy


# ---- TcpSocketWrapper の完全モック ----
class DummySock:
    def __init__(self):
        self.sent = []
        self.recv_texts = []
        self.timeout_set = None

    def settimeout(self, t):
        self.timeout_set = t

    def connect(self, addr):
        self.connected_to = addr

    def sendtext(self, txt):
        self.sent.append(txt)
        return None

    def recvtext(self, buffsize=None, byte_size=None):
        # 返す値はテストごとに設定
        if self.recv_texts:
            return self.recv_texts.pop(0)
        # データ取得テスト用
        return "!0001 OK ControllerState:finished NumberOfAcquiredPoints:10\n"

    def reset(self):
        self.sent.clear()
        self.recv_texts.clear()


@pytest.fixture
def remote(monkeypatch):
    # TcpSocketWrapperをDummySockに差し替え
    monkeypatch.setattr(prodigy, "TcpSocketWrapper", lambda **kwargs: DummySock())
    return prodigy.RemoteIn()


def test_connect(remote):
    remote.sock = None
    result = remote.connect()
    # コマンド送信内容
    assert "Connect" in remote.sock.sent[0]
    # レスポンスはDummySockから
    assert isinstance(result, str)


def test_sendcommand(remote):
    remote.connect()
    remote.sock.recv_texts = ["!0001 OK\n"]
    result = remote.sendcommand("TestCmd")
    assert remote.sock.sent[-1].endswith("TestCmd")
    assert result == "!0001 OK\n"


def test_disconnect(remote):
    remote.connect()
    remote.sock.recv_texts = ["!0001 OK\n"]
    result = remote.disconnect()
    assert "Disconnect" in remote.sock.sent[-1]
    assert result == "!0001 OK\n"


def test_defineFAT_with_check(remote):
    remote.connect()
    remote.sock.recv_texts = ["!ok\n", "!checkok\n"]
    result = remote.defineFAT(0, 10, 1)
    assert "DefineSpectrumFAT" in remote.sock.sent[-2]
    # assert "DefineSpectrumFAT" in remote.sock.sent[0]
    assert "CheckSpectrumFAT" in remote.sock.sent[-1]
    assert result == "!checkok\n"


def test_defineFAT_without_check(remote):
    remote.connect()
    remote.sock.recv_texts = ["!ok\n"]
    result = remote.defineFAT(0, 10, 1, with_check=False)
    assert "DefineSpectrumFAT" in remote.sock.sent[-1]
    assert len(remote.sock.sent) == 2
    assert result == "!ok\n"


def test_defineSFAT_with_check(remote):
    remote.connect()
    remote.sock.recv_texts = ["!ok\n", "!checkok\n"]
    result = remote.defineSFAT(0, 10)
    assert "DefineSpectrumSFAT" in remote.sock.sent[-2]
    assert "CheckSpectrumSFAT" in remote.sock.sent[-1]
    assert result == "!checkok\n"


def test_checkFAT(remote):
    remote.connect()
    remote.sock.recv_texts = ["!checkfat\n"]
    result = remote.checkFAT(0, 10, 1)
    assert "CheckSpectrumFAT" in remote.sock.sent[-1]
    assert result == "!checkfat\n"


def test_checkSFAT(remote):
    remote.connect()
    remote.sock.recv_texts = ["!checksfat\n"]
    result = remote.checkSFAT(0, 10)
    assert "CheckSpectrumSFAT" in remote.sock.sent[-1]
    assert result == "!checksfat\n"


def test_clear(remote):
    remote.connect()
    remote.sock.recv_texts = ["!clearok\n"]
    result = remote.clear()
    assert remote.data == []
    assert "ClearSpectrum" in remote.sock.sent[-1]
    assert result == "!clearok\n"


def test_get_status(remote):
    remote.connect()
    remote.sock.recv_texts = [
        "!0001 OK ControllerState:finished NumberOfAcquiredPoints:10\n"
    ]
    result = remote.get_status()
    assert "GetAcquisitionStatus" in remote.sock.sent[-1]
    assert isinstance(result, str)


def test_get_data(remote):
    remote.connect()
    # 最初のstatus
    remote.sock.recv_texts = [
        "!0001 OK ControllerState:finished NumberOfAcquiredPoints:3\n",
        "!0001 OK Data:[1.1,2.2,3.3]\n",
    ]
    # statusはfinishedで3点
    remote.data = []
    result = remote.get_data()
    assert remote.data == [1.1, 2.2, 3.3]
    assert result == [1.1, 2.2, 3.3]


def test_get_unique_filepath(tmp_path):
    fpath = tmp_path / "data.txt"
    fpath.write_text("x")
    new_path = prodigy.get_unique_filepath(fpath)
    assert new_path != fpath
    # 2度目もユニーク
    new_path2 = prodigy.get_unique_filepath(new_path)
    assert new_path2 != new_path


def test_parse_analyzer_parameter_int():
    s = '!0016 OK: Name:"NumNonEnergyChannels" Value:200\n'
    key, val = prodigy.parse_analyzer_parameter(s)
    assert key == "NumNonEnergyChannels"
    assert val == 200


def test_parse_analyzer_parameter_float():
    s = '!0016 OK: Name:"NumNonEnergyChannels" Value:2.5\n'
    key, val = prodigy.parse_analyzer_parameter(s)
    assert key == "NumNonEnergyChannels"
    assert val == 2.5


def test_save_data(remote, tmp_path, monkeypatch):
    # itxとdataをモック
    monkeypatch.setattr(
        prodigy,
        "itx",
        lambda data, param, spectrum_id, comment, measure_mode: "DATA",
    )
    remote.data = [1.1, 2.2, 3.3]
    remote.param = {"X": 1}
    fname = tmp_path / "test.itx"
    remote.save_data(str(fname), 1, "cmt", "FAT")
    assert fname.exists()
    assert fname.read_text() == "DATA"
    # 既存ファイルの時は別名になる
    remote.save_data(str(fname), 1, "cmt", "FAT")
    # ファイルが2つできていること
    files = list(tmp_path.glob("test*.itx"))
    assert len(files) >= 2


def test_scan(remote, monkeypatch):
    # start/get_data/clearのモック
    monkeypatch.setattr(remote, "start", lambda setsafeafter=True: "OK")
    monkeypatch.setattr(remote, "get_data", lambda: [1.0, 2.0, 3.0])
    monkeypatch.setattr(remote, "clear", lambda: "OK")
    remote.data = []
    result = remote.scan(num_scan=2)
    # 2回分を合算
    assert result == [2.0, 4.0, 6.0]
    assert remote.data == [2.0, 4.0, 6.0]


def test_set_excitation_energy(remote, monkeypatch):
    monkeypatch.setattr(
        remote, "sendcommand", lambda cmd: '!005 OK: Name: "ex_energy" Value:123.4\n'
    )
    monkeypatch.setattr(
        remote,
        "get_excitation_energy",
        lambda: remote.param.update({"ExcitationEnergy": 123.4}),
    )
    _ = remote.set_excitation_energy(123.4)
    assert remote.param["ExcitationEnergy"] == 123.4


def test_validate(remote, monkeypatch):
    remote.connect()
    # sendcommand, get_analyzer_parameter, get_non_energy_channel_infoをモック
    monkeypatch.setattr(
        remote, "sendcommand", lambda cmd: "!001 OK Key:ExcitationEnergy:123.4"
    )
    monkeypatch.setattr(remote, "get_analyzer_parameter", lambda: None)
    monkeypatch.setattr(remote, "get_non_energy_channel_info", lambda: None)
    remote.param = {"ExcitationEnergy": 100.0}
    result = remote.validate()
    assert isinstance(result, str)


def test_set_safe_state(remote):
    remote.connect()
    remote.sock.recv_texts = ["!safe"]
    result = remote.set_safe_state()
    assert "SetSafeState" in remote.sock.sent[-1]
    assert result == "!safe"


def test_get_non_energy_channel_info(remote):
    remote.connect()
    remote.sock.recv_texts = ['!000F OK: ValueType:doubl Unit:"deg"  Min:10  Max:20\n']
    remote.param = {}
    remote.get_non_energy_channel_info()
    assert remote.param["Angle_Unit"] == "deg"
    assert remote.param["Angle_min"] == 10
    assert remote.param["Angle_max"] == 20


# setup_fat/setup_sfatなどのテストは、clear/set_excitation_energy/defineFAT/checkFAT等をモックすればOK
def test_setup_fat(remote, monkeypatch):
    monkeypatch.setattr(remote, "clear", lambda: "OK")
    monkeypatch.setattr(remote, "set_excitation_energy", lambda energy: "OK")
    monkeypatch.setattr(remote, "defineFAT", lambda **kwargs: "DEF")
    monkeypatch.setattr(remote, "checkFAT", lambda **kwargs: "CHK")
    result = remote.setup_fat(
        excitation_energy=123.4,
        start_energy=0.0,
        end_energy=10.0,
        step=1.0,
    )
    assert result == ("DEF", "CHK")


def test_setup_sfat(remote, monkeypatch):
    monkeypatch.setattr(remote, "clear", lambda: "OK")
    monkeypatch.setattr(remote, "set_excitation_energy", lambda energy: "OK")
    monkeypatch.setattr(remote, "defineSFAT", lambda **kwargs: "DEF")
    monkeypatch.setattr(remote, "checkSFAT", lambda **kwargs: "CHK")
    result = remote.setup_sfat(
        excitation_energy=123.4,
        start_energy=0.0,
        end_energy=10.0,
        samples=2,
    )
    assert result == ("DEF", "CHK")
