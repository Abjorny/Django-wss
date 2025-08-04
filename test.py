import socket
import cv2
import numpy as np
import struct

cap1 = cv2.VideoCapture(0)  

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)

def start_server(host='0.0.0.0', port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(1)
        print(f"[INFO] Сервер слушает {host}:{port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"[INFO] Подключено: {addr}")
                cmd = conn.recv(4)
                if cmd == b'GETI':
                    try:
                        ret1, frame = cap1.read()
                        _, img_encoded = cv2.imencode('.jpg', frame)
                        img_bytes = img_encoded.tobytes()
                        conn.sendall(struct.pack('>I', len(img_bytes)))  # Отправляем длину
                        conn.sendall(img_bytes) 
                        print(f"[INFO] Изображение отправлено ({len(img_bytes)} байт)")
                    except Exception as e:
                        print(f"[ERROR] {e}")
                else:
                    print("[WARN] Неизвестная команда")

if __name__ == "__main__":
    start_server()
