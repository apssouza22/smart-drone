import cv2
import socket
import base64
import pygame
import threading
from common.pygamescreen import PyGameScreen

class RecvThread (threading.Thread):
   def __init__(self, socket, pygame_screen: PyGameScreen):
      threading.Thread.__init__(self)
      self.socket = socket
      self.pygame_screen = pygame_screen
      self.ios_command = {    
          'll': '97',
          'lr': '100',
          'lu': '119',
          'ld': '115',
          'rl': '1073741904',
          'rr': '1073741903',
          'ru': '1073741906',
          'rd': '1073741905',
          'lx': '-1',
          'rx': '-1',
          }
   def run(self):
        while True:
            data = self.socket.recv(2)
            command = int(self.ios_command[data.decode("utf-8")])
            if command == -1:
                for key, fn in self.pygame_screen.controls_keyrelease.items():
                    fn()
            else:
                self.pygame_screen.controls_keypress[command]()
        
class IOSControlManager:
    def __init__(self, enable_ios, host, port, pygame_screen: PyGameScreen):
        self.connected = False
        if enable_ios:
            try:
                self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.clientsocket.connect((host, port))
                self.connected = True
                thread = RecvThread(self.clientsocket, pygame_screen)
                thread.start()
            except:
                print('You should pass correct host:port info here. Try run the iOS project first to get the info')

    def update(self, frame):
        if self.connected:
            encoded, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer)
            self.clientsocket.send(str(len(jpg_as_text)).encode())
            self.clientsocket.sendall(jpg_as_text)