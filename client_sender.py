import sys
import socket
from parser import ip_parser

def sender(target, port, buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if target == 'my-ip':
            target = ip_parser()
        client.connect((target, port))
        print('Connected %s:%d' % (target, port))
        if len(buffer):
            client.send(buffer.encode())
            print("Sended")
        
        while True:
            rcv_data = ""
            rcv_len = 1

            while rcv_len:
                rcv = client.recv(1024).decode()
                rcv_data += rcv
                rcv_len = len(rcv)

                if rcv_len < 1024:
                    break

            print(rcv_data)

            buffer = input()
            buffer += '\n'
            client.send(buffer.encode())
    except Exception as err:
        print(err)
        print('[!] Exception! Exiting...')
        client.close()
