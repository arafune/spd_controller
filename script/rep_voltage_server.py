#! /usr/bin/env python3
"""Report voltage measured by Keithlety DMM throught RS232"""

import socket
import threading
from datetime import datetime
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger

import netifaces  # pip install netiface
from dmm2700 import DMM2700

LOGLEVEL = INFO
logger = getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
formatter = Formatter(fmt)
handler = StreamHandler()
handler.setLevel(LOGLEVEL)
logger.setLevel(LOGLEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


# HOST_IP = socket.gethostbyname(socket.gethostname())# "144.213.194.216" # サーバーのIPアドレス

HOST_IP = netifaces.ifaddresses("wlan0")[netifaces.AF_INET][0]["addr"]
logger.info("Host IP is {}".format(HOST_IP))
PORT = 12345  # 使用するポート
CLIENTNUM = 3  # クライアントの接続上限数
DATESIZE = 1024  # 受信データバイト数


class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # サーバー起動
    def run_server(self):

        # server_socketインスタンスを生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(CLIENTNUM)
            print(
                "[{}] run server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            while True:
                # クライアントからの接続要求受け入れ
                client_socket, address = server_socket.accept()
                # print('[{0}] connect client -> address : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), address) )
                client_socket.settimeout(60)
                # クライアントごとにThread起動 send/recvのやり取りをする
                t = threading.Thread(
                    target=self.conn_client, args=(client_socket, address)
                )
                t.setDaemon(True)
                t.start()

    def conn_client(self, client_socket, address):
        with client_socket:
            while True:
                rcv_data = client_socket.recv(DATESIZE)
                if rcv_data:
                    dmm.sendtext("READ?")
                    _, voltage = dmm.recv()
                    client_socket.send(voltage)
                else:
                    break
        logger.debug(
            "[{0}] disconnect client -> address : {1}".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), address
            )
        )


if __name__ == "__main__":
    dmm = DMM2700()
    dmm.conf_voltage()
    SocketServer(HOST_IP, PORT).run_server()
