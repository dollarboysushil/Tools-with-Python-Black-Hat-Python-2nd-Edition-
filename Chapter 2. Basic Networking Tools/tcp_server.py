import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 9999



server.bind((host, port))
server.listen(5) # max 5 incomming connections in the queue


print(f"Server is listening on {host}:{port}")


while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address} established!")

    
    data = client_socket.recv(4096)

    if data:
        print(f"Received: {data.decode()}")

        client_socket.send(b"Hello from server!")

        
        
    client_socket.close()