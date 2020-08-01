import socket
import re
import subprocess
import sys
from threading import Thread
from parser import ip_parser


def run_command(command):
    try:
        check = subprocess.call(command, shell=True)
        if check in (0, 255):
            out = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        else:
            raise RuntimeError
    except:
        out = "[!] Failed to execute command".encode()
    
    return out


class ClientHandler(Thread):
    def __init__(self, client, upload_destination, command, addr):
        Thread.__init__(self)
        self.client = client
        self.upload_destination = upload_destination
        self.command = command
        self.addr = addr

    def run(self):
        file_buffer = ""
        rcv_len = 1
        while rcv_len:
            rcv = self.client.recv(1024)
            rcv_len = len(rcv)
            file_buffer += rcv.decode()
            if rcv_len < 1024:
                break
        if self.upload_destination:
            with open(self.upload_destination, 'w') as f:
               f.write(file_buffer)
        
        if self.command:
            print("[*] Client (%s:%d) has opened shell" % (self.addr[0], self.addr[1]))
            self.client.send("Shell:".encode())
            while True:
                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += self.client.recv(1024).decode()
                print('[%s:%d]> %s' % (self.addr[0], self.addr[1], cmd_buffer.rstrip('\n')))
                response = run_command(cmd_buffer.rstrip('\n')).decode()
                self.client.send(response.encode())



def port_scaner(target):
    for p in range(1025, 9999):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not s.connect_ex((target, p)):
            return p
    print("[!] No ports are available.")

def server_loop(target, port, upload_destination, command):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not target:
            target = "0:0:0:0"
        if not port:
            port = port_scaner(target)
        if target == "my-ip":
            target = ip_parser()
        server.bind((target, port))
        print('[*] Binded %s:%d' % (target, port))
        server.listen(5)
        print('[*] Listen %s:%d' % (target, port))
        while True:
            client, addr = server.accept()
            print("[*] Successfuly connected %s:%d" % (addr[0], addr[1]))
            client_thread = ClientHandler(client, upload_destination, command, addr)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[!] Aborting connection...")
        server.close()
