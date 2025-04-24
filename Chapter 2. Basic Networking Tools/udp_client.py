import socket

hostname = '127.0.0.1'
port = 53

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

client.sendto(b"XYZ",(hostname,port))

data, addr = client.recvfrom(4096)


print (data.decode())
client.close()


