import socket
import time
import threading
import os
import sys
from collections import defaultdict

import pickle
import torch

import json 

class Server(object):
    def __init__(self, HOST='', PORT=7734, V='P2P-CI/1.0'):
        self.SERVER_HOST = 'localhost'
        self.SERVER_PORT = 7734
        self.V = V
        self.peers = {}
        self.lock = threading.Lock()
        # self.count = 0 
        # self.temp = 0
    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.SERVER_HOST, self.SERVER_PORT))
            self.s.listen(5)
            print('Server %s is listening on port %s' %
                  (self.V, self.SERVER_PORT))
            while True:
                soc, addr = self.s.accept()
                print('%s:%s connected' % (addr[0], addr[1]))
                # self.count +=1
                # self.temp = self.count 
                thread = threading.Thread( target=self.handler, args=(soc, addr))
                thread.start()
        except KeyboardInterrupt:
            print('\nShutting down the server..\nGood Bye!')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)


    # connect with a client
    def handler(self, soc, addr):
        # keep recieve request from client

        req = soc.recv(1024).decode()
        print('Recieve request:\n%s' % req)
        lines = req.splitlines()
        host = lines[1].split(None, 1)[1]
        port = lines[0].split(None, 1)[1]
        self.peers[req] = 1
        while True:
            result = json.dumps(self.peers) 
            result += "****"
            # import pdb
            # pdb.set_trace()
            try:
                soc.sendall(result.encode())
            except:
                print(host , " \t " , port, "client doesnt exit")
                del self.peers[lines]
                return 
            time.sleep(1)
    

if __name__ == '__main__':
    s = Server()
    s.start()
