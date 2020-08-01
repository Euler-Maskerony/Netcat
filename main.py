import sys
import getopt
from client_sender import sender
from server import server_loop
from proxy import proxy_loop

def usage():
    print("-h --help                    Invoke this help page")
    print("-l --listen                  Listen on [target]:[port]")
    print("-t --target=ip               IP")
    print("-p --port=port               Port")
    print("-c --command                 Initialize a command shell")
    print("-u --upload=destination      destination of file to save data")

def main():
    target = ""
    upload_destination = ""
    port = 0
    local_port = 0
    local_host = ""
    remote_port = 0
    remote_host = ""
    listen = False
    command = False
    proxy = False
    buffer = ""
    recieve_first = False
    try:
        if sys.argv[1:] == []:
            usage()
            sys.exit()
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hlt:p:cu:x",
            ["help", "listen", "target=", "port=", "command", "upload=", "proxy", "local_host=", "local_port=", "remote_host=", "remote_port=", "recieve_first"]
        )
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-x", "--proxy"):
            proxy = True
        elif o in ("--local_host"):
            local_host = a
        elif o in ("--local_port"):
            local_port = int(a)
        elif o in ("--remote_host"):
            remote_host = a
        elif o in ("--remote_port"):
            remote_port = int(a)
        elif o in ("--recieve_first"):
            recieve_first = True
        else:
            assert False, "Unexpected argument"
    assert not proxy or (local_host and local_port and remote_host and remote_port), "Wrong arguments set. Type --help for more information."
    
    if not listen and target and port > 0:
        buffer = sys.stdin.read()
        sender(target, port, buffer)
    elif listen:
        server_loop(target, port, upload_destination, command)
    elif proxy:
        proxy_loop(local_host, local_port, remote_host, remote_port, recieve_first)
    else:
        print("[*] Exception! Exiting...")

main()