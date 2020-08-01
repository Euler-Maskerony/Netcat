import socket
from threading import Thread
import sys

def recieve(socket):
    try:
        rcv_len = 1024
        buffer = b""
        while rcv_len >= 1024:
            rcv = socket.recv(1024)
            rcv_len = len(rcv)
            buffer += rcv
            if rcv_len < 1024:
                break
        return buffer.decode()
    except:
        print("[!] Failed to recieve data.")
        sys.exit()

def hexdump(buffer, length=16):
    result = []
    digits = 2
    for i in range(0, len(buffer), length):
        s = buffer[i:i+length]
        hexa = ' '.join(['%0*X' % (digits, ord(x)) for x in s])
        text = ''.join([x if 0x20 <= ord(x) <= 0x7F else '.' for x in s])
        result.append("%04X   %-*s   %s" % (i, length*(digits+1), hexa, text))
    print('\n'.join(result))


class ProxyHandler(Thread):
    def __init__(self, client, remote_host, remote_port, recieve_first):
        Thread.__init__(self)
        self.client = client
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.recieve_first = recieve_first
    
    def run(self):
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((self.remote_host, self.remote_port))
        remote_buffer = ""
        if self.recieve_first:
            remote_buffer = recieve(remote)
            print("[==>] %d bytes recieved from remote host." % (len(remote_buffer.encode())))
            hexdump(remote_buffer)
            if len(remote_buffer):
                self.client.send(remote_buffer.encode())
                print("[==>] %d bytes sent to local host." % (len(remote_buffer)))
        
        while True:
            local_buffer = recieve(self.client)
            if len(local_buffer):
                print("[<==] %d bytes recieved from local host." % (len(local_buffer)))
                hexdump(local_buffer)
                remote.send(local_buffer.encode())
                print("[<==] %d bytes sent to remote host." % (len(local_buffer)))
            remote_buffer = recieve(remote)
            if len(remote_buffer):
                print("[==>] %d bytes recieved from remote host." % (len(remote_buffer)))
                hexdump(remote_buffer)
                self.client.send(remote_buffer.encode())
                print("[==>] %d bytes sent to local host." % (len(remote_buffer)))
            if not len(remote_buffer) or not len(local_buffer):
                self.client.close()
                remote.close()
                print("[*] No more data. Closing connection.")

def proxy_loop(local_host, local_port, remote_host, remote_port, recieve_first):
    local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        local.bind((local_host, local_port))
        print("[*] Binded %s:%d" % (local_host, local_port))
        local.listen(5)
        print("[*] Listen %s:%d" % (local_host, local_port))
    except:
        print("[!] Failed to listen on %s:%d" % (local_host, local_port))
        sys.exit()
    while True:
        client, addr = local.accept()
        print("[<==] Recieved incoming connection from %s:%d" % (addr[0], addr[1]))
        proxy_handler = ProxyHandler(client, remote_host, remote_port, recieve_first)
        proxy_handler.start()
