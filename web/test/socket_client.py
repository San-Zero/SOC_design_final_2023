import socket
import time

UDP_IP = '127.0.0.1'
UDP_PORT = 8001

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        time.sleep(1)
        message = "Hello, World2!"
        socket.sendto(message.encode(), (UDP_IP, UDP_PORT))
except KeyboardInterrupt:
    socket.close()
