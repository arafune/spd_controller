#! /usr/bin/env python3
import time
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from spd_controller import SocketClient

HOST_IP = "144.213.194.216"  # 接続するサーバーのIPアドレス
PORT = 12345  # 接続するサーバーのポート


# TODO:
# 表示するMaxlength を引数で指定できるように（ default は100で良いけど）


plt.style.use("fivethirtyeight")
voltages: list[float] = []
maxlength = 100


fig = plt.figure()
ax = fig.add_subplot(111)


def rtplot(i: int) -> None:
    if len(voltages) > 100:
        voltages.pop(0)
    voltages.append(float(client.send_recv(" ")) * (-1000))
    plt.cla()
    ax.plot(voltages, linewidth=1)
    ax.text(
        0.9,
        0.9,
        "{:.2f}".format(voltages[-1]),
        fontsize=28,
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
    )
    ax.set_label("Current")


if __name__ == "__main__":
    client = SocketClient(HOST_IP, PORT)
    ani = FuncAnimation(plt.gcf(), rtplot, interval=10)
    plt.tight_layout()
    plt.ylabel("Current")
    plt.show()
