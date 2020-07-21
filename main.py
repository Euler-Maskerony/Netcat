import sys
import getopt
from client_sender import sender
from server import server_loop

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
    listen = False
    command = False
    buffer = "lol"
    try:
        if sys.argv[1:] == []:
            usage()
            sys.exit()
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hlt:p:cu:",
            ["help", "listen", "target=", "port=", "command", "upload="]
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
        else:
            assert False, "Unexpected argument"
            usage()
    
    if not listen and target and port > 0:
        buffer = sys.stdin.read()
        sender(target, port, buffer)
    elif listen:
        server_loop(target, port, upload_destination, command)
    else:
        print("[*] Exception! Exiting...")

main()