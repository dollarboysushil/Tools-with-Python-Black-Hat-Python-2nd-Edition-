import socket

target_host = '127.0.0.1'
target_port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET == for IPv4 ; socket.SOCK_STREAM == for TCP connection


client.connect((target_host, target_port))
client.send(b"Hello from client") 

response = client.recv(4096) # receiving up to 4096 bytes of data. (headers + HTML)


print(response.decode())
client.close