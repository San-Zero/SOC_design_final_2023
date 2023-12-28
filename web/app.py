import os
import random
import json
import pandas as pd
import socket
import threading
from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__, static_url_path='', static_folder='static')


result_img_queue = []
result_queue = []


@app.route('/')
def hello_world():
    return render_template('index.html')


def udp_socket_server(ip, port):
    UDP_IP = ip
    UDP_PORT = port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))

    print("Start UDP listener: " + ip + ":" + str(port))

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if not data:
                sock.sendto("True".encode(), addr)
                break
            print(f"Received data from {addr}: {data.decode('utf-8')}")
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        sock.close()
    return


def handle_image(img):
    try:
        result_img_queue.append(img)
        return True
    except Exception as e:
        print(e)
        return False


def handle_result(result):
    try:
        result_queue.append(result)
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    try:
        udp_thread = threading.Thread(
            target=udp_socket_server, args=("0.0.0.0", 8001))
        udp_thread.daemon = True
        udp_thread.start()

        app.run(debug=True, host="0.0.0.0", port=8000)

    except Exception as e:
        print(e)
