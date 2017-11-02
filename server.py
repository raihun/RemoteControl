import socket
import sys
import threading

clist = []


def main(argc, argv):
    # メッセージ入力スレッド
    th = threading.Thread(target=send_loop)
    th.start()

    # サーバ起動
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssock.bind(("0.0.0.0", 25555))  # ポートを変更可能
    ssock.listen(10)

    # クライアント接続待機
    while True:
        try:
            csock, caddr = ssock.accept()
        except KeyboardInterrupt:
            for cinfo in clist:
                cinfo[0].close()
            ssock.close()
            print("Server closed.")
            return

        th = threading.Thread(target=client_loop, args=(csock, caddr))
        th.start()
    return


def client_loop(csock, caddr):
    cname = csock.recv(1024).decode().strip()
    if(len(cname) <= 0):
        csock.close()
        return
    cinfo = [csock, caddr, cname]
    clist.append(cinfo)
    print("Connect: {0}".format(cname))

    while True:
        try:
            recvmsg = csock.recv(1024).decode()
        except KeyboardInterrupt:
            csock.close()
            return
        except OSError:  # killコマンド使用時等
            csock.close()
            return

        if(len(recvmsg) <= 0):
            csock.close()
            break
        print("%s:%s" % (cname, recvmsg))

    print("Disconnect: {0} (by Client)".format(cname))
    clist.remove(cinfo)
    return


def send_loop():
    helpMsg()

    while True:
        # コマンド待機
        try:
            cmd = input()
        except KeyboardInterrupt:
            return

        # リストコマンド
        buf = cmd.split(" ")
        if(buf[0] == "/cmd"):
            for cinfo in clist:
                if(cinfo[2] == buf[1]):
                    print("Command ->", end='')
                    cmd = input()
                    cinfo[0].sendall(cmd.encode())
        elif(buf[0] == "/list"):
            print("---------- Client name list ----------")
            for cinfo in clist:
                print("{0}\t".format(cinfo[2]), end='')
                print(cinfo[1])
        elif(buf[0] == "/close"):
            for cinfo in clist:
                if(cinfo[2] == buf[1]):
                    print("Disconnect: {0} (by /close)".format(cinfo[2]))
                    cinfo[0].close()
                    clist.remove(cinfo)
        elif(buf[0] == "/closeall"):
            for cinfo in clist:
                print("Disconnect: {0} (by /closeall)".format(cinfo[2]))
                cinfo[0].close()
                clist.remove(cinfo)
        elif(buf[0] == "/kill"):
            for cinfo in clist:
                if(cinfo[2] == buf[1]):
                    print("Kill: {0} (by /kill)".format(cinfo[2]))
                    cinfo[0].sendall("/kill".encode())
        elif(buf[0] == "/help"):
            helpMsg()
        else:
            print("Undefined command: {0}".format(buf[0]))

    return


def helpMsg():
    print("Commands: /cmd [Name], /list, ", end='')
    print("/close [Name], /closeall, /kill [Name]")
    print()
    return

if(__name__ == "__main__"):
    main(len(sys.argv), sys.argv)
    sys.exit()
