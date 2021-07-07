import cv2
import socket
import base64

class IOSControlManager:
    def __init__(self, enable_ios, host, port):
        self.connected = False
        if enable_ios:
            try:
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientsocket.connect((host, port))
                self.connected = True
            except:
                print('You should pass correct host:port info here. Try run the iOS project first to get the info')

    def update(self, frame):
        if self.connected:
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            self.clientsocket.send(str(len(jpg_as_text)).encode())
            self.clientsocket.sendall(jpg_as_text)
