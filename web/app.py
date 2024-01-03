import socket
import threading
from flask import Flask, render_template, jsonify, request, send_file, Response
from io import BytesIO
import cv2

app = Flask(__name__, static_url_path='', static_folder='static')


result_img_queue = []
result_queue = []


@app.route('/', methods=['GET'])
def hello_world():
    if request.method != 'GET':
        response = jsonify({'message': 'Method not allowed'})
        response.status_code = 405
        return response

    return render_template('index.html')


@app.route('/image/<int:frame>', methods=['GET'])
def get_image(frame):
    if request.method != 'GET':
        response = jsonify({'message': 'Method not allowed'})
        response.status_code = 405
        return response

    if len(result_img_queue) == 0:
        response = jsonify({'message': 'No image in queue'})
        response.status_code = 404
        return response

    if frame > len(result_img_queue) - 1:
        response = jsonify({'message': 'Index out of range'})
        response.status_code = 404
        return response

    img_bytes = result_img_queue[frame]
    return send_file(BytesIO(img_bytes), mimetype='image/jpeg')


@app.route('/result/<int:frame>', methods=['GET'])
def get_result(frame):
    if request.method != 'GET':
        response = jsonify({'message': 'Method not allowed'})
        response.status_code = 405
        return response

    if len(result_img_queue) == 0:
        response = jsonify({'message': 'No result in queue'})
        response.status_code = 404
        return response

    if frame > len(result_img_queue) - 1:
        response = jsonify({'message': 'Index out of range'})
        response.status_code = 404
        return response

    response = jsonify({'result': result_queue[frame]})
    response.status_code = 200
    return response


def udp_socket_server(ip, port):
    UDP_IP = ip
    UDP_PORT = port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_IP, UDP_PORT))

    print("Start UDP listener: " + ip + ":" + str(port))

    try:
        while True:
            data, addr = sock.recvfrom(65536)
            if not data:
                sock.sendto("True".encode(), addr)
                break
            # TODO: 處理接收到的資料
            # print(f"Received data from {addr}: {data.decode('utf-8')}")
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        sock.close()
    return


def handle_image(img):
    try:
        _, img_encoded = cv2.imencode('.jpg', img)
        img_bytes = img_encoded.tobytes()

        result_img_queue.append(img_bytes)
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
            target=udp_socket_server, args=("0.0.0.0", 8101))
        udp_thread.daemon = True
        udp_thread.start()

        video_thread = threading.Thread(target=read_video)
        app.run(debug=True, host="0.0.0.0", port=8100)

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        udp_thread.join()
