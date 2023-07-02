import socket
import sys
from threading import Thread

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = '127.0.0.1'
port = 8081
server.connect((ip_address, port))

client_id = int(server.recv(2048).decode().split()[-1])
print("Connected to server with ID", client_id)


def send_msg(sock):
    while True:
        message = input()
        sock.send((str(client_id) + ":" + message).encode())


def recv_msg(sock):
    while True:
        data = sock.recv(2048)
        sys.stdout.write(data.decode())


Thread(target=send_msg, args=(server,)).start()
Thread(target=recv_msg, args=(server,)).start()

while True:
    pass

server.close()
