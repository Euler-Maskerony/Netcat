import socket
import re
import subprocess
from threading import Thread


def run_command(command):
    try:
        out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        out = "Failed to execute command"
    
    return out


class ClientHandler(Thread):
    def __init__(self, client, upload_destination, command, addr):
        Thread.__init__(self)
        self.client = client
        self.upload_destination = upload_destination
        self.command = command
        self.addr = addr

    def run(self):
        if self.upload_destination:
            file_buffer = ""
            rcv_len = 1
            while rcv_len:
                rcv = self.client.recv(1024)
                rcv_len = len(rcv)
                file_buffer += rcv.decode()
                if rcv_len < 1024:
                    break
            print(file_buffer)
            with open(self.upload_destination, 'w') as f:
               f.write(file_buffer)
        
        if self.command:
            print("<Client (%s:%d) has opened shell>" % (self.addr[0], self.addr[1]))
            self.client.send("Shell:".encode())
            while True:
                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += self.client.recv(1024).decode()
                response = run_command(cmd_buffer.rstrip('\n')).decode()
                self.client.send(response.encode())



def port_scaner(target):
    for p in range(1025, 9999):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not s.connect_ex((target, p)):
            return p

def server_loop(target, port, upload_destination, command):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not target:
            target = "0:0:0:0"
        if not port:
            port = port_scaner(target)
        server.bind((target, port))
        print('Binded %s:%d' % (target, port))
        server.listen(5)
        print('Listen %s:%d' % (target, port))
        while True:
            client, addr = server.accept()
            print("Successfuly connected %s:%d" % (addr[0], addr[1]))
            client_thread = ClientHandler(client, upload_destination, command, addr)
            client_thread.start()
    except KeyboardInterrupt:
        print("Aborting connection...")
        server.close()
        