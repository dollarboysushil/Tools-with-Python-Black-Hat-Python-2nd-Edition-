import sys
import socket
import threading
import string



HEX_FILTER = ''

for i in range (256):
    char = chr(i)
    if char in string.printable and not char.isspace():
        HEX_FILTER += char
        #print(f'thisis taken:{char}')
    else:
        #print(f'thisis removed: {char}')
        HEX_FILTER += '.'
        
        
        
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):    # checking if the input is bytes, if so decode to str
        src = src.decode()

    results= list()                 # preparing list to hold each formatted lines of the hex dump
    
    
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
    
    
    
    

def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data= connection.recv(4096)
            if not data:
                break
            
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    #perform packet modifications
    return buffer

def response_handler(buffer):
    # perform packet modifications
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        
    remote_buffer = response_handler(remote_buffer)
    
    if len(remote_buffer):
        print("Sending %d bytes to localhost" % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    
    while True:
        
        # From local to remote
        local_buffer = receive_from(client_socket)
        
        if len(local_buffer):
            line="Received %d bytes from localhost" % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer= request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("Sent to remote.")

        # From remote to local
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer= response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("Send to localhost.")
        
        
        # Break if not more data
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("No more data. Closing Connections.")
            break
        
        
        
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    
    server= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    
    except Exception as e:
        print('problem on bind: %r' % e )
        
        print("Filed to listen on %s:%d" % (local_host, local_port))
        print("Check of other listening sockets or correct permissions")
        sys.exit(0)

        
    print("Listening on %s:%d" % (local_host, local_port))
    server.listen(5)

    
    while True:
        client_socket, addr = server.accept()

        
        # printing local connection information
        line = " received Incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)

        # start a thred to talk to the remote hosts
        proxy_thread = threading.ThreadError(target=proxy_handler, args= (client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()
        
        
    
    
def main():
    
    if len(sys.argv[1:]) !=5:
        print("Usage ./tcp_proxy.py localhost localport", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./tcp_proxy.py 127.0.0.1 9000 10.10.10.10 9000 True")
        sys.exit(0)

    local_host= sys.argv[1]
    local_port = int (sys.argv[2])
    remote_host= (sys.argv[3])
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first= True
    else:
        receive_first = False
        
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
    
    
    
if __name__ == '__main__':
    main()


