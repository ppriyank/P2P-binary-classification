import socket
import threading
import os
import sys
from collections import defaultdict
from pathlib import Path
import pickle
import json 

from PIL import Image
import pickle

from trainer import Trainer

class Server(object):
    def __init__(self, HOST='localhost', PORT=7734):
        self.SERVER_HOST = 'localhost'
        self.SERVER_PORT = 7734
        
        self.HOST = HOST
        self.DIR = 'rfc'  # file directory
        Path(self.DIR).mkdir(exist_ok=True)
        self.UPLOAD_PORT = None
        self.shareable = True
        self.version = 0
        self.lock = threading.Lock()
        self.peers = {}
        self.trainer = Trainer()
        self.version = 0

    def start(self):
        # connect to server
        uploader_process = threading.Thread(target=self.init_upload)
        uploader_process.start()
        while self.UPLOAD_PORT is None:
            pass
        print('Listening on the upload port %s' % self.UPLOAD_PORT)

        print('Connecting to the server %s:%s' % (self.SERVER_HOST, self.SERVER_PORT))
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.connect((self.SERVER_HOST, self.SERVER_PORT))
            header = "PORT: %s\nHOST: %s"%(self.UPLOAD_PORT, self.HOST)
            self.server.sendall(header.encode())
        except Exception:
            print('Server Not Available.')
            return
        print("Connected")
        # interactive shell
        self.cli()


    def cli(self):        
        self.command_dict = {'1': self.upload_image,
                        '2': self.classify,
                        '3': self.look_up,
                        '4': self.download,
                        '5': self.shutdown}                        
        # max_index = max(self.command_dict.keys())
        while True:
            try:
                req = input('\n1: Upload Image \n2: Classify Image,\n3: Look Up model Version,\n4: Download \n5: Shut Down\nEnter your request: ')
                self.command_dict.setdefault(req, self.invalid_input)()
            except MyException as e:
                print(e)
            except Exception:
                print('System Error.')
            except BaseException:
                self.shutdown()

    def init_upload(self):
        # listen upload port
        self.uploader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploader.bind(('', 0))
        self.UPLOAD_PORT = self.uploader.getsockname()[1]
        self.uploader.listen(5)

        while True:
            requester, addr = self.uploader.accept()
            requester.sendall(str(self.version).encode())
            # handler = threading.Thread(
            #     target=self.handle_upload, args=(requester, addr))
            # handler.start()
        self.uploader.close()


    def upload_image(self, num=None, title=None):
        self.look_up(disply=False)
        self.version +=1
        title = "1.png"
        label = 1
        # title = input('Enter image name: ')
        # label = input('Enter label: ')
        file = Path('%s/%s' % (self.DIR, title))
        print(file)
        image = Image.open(file)
        # image = image.resize(( self.h , self.w) )
        # import pdb
        # pdb.set_trace()
        
        self.trainer.train(image , label)
        
        

            
            
        
        # self.uploader.sendto(, dest)
        # image.show()
        # data_string = pickle.dumps(image, -1) 
        # # data_loaded = pickle.loads(data_string)
        # if not file.is_file():
        #     raise MyException('File Not Exit!')
        # # msg = {"label" : label , "data": data_string , "host": socket.gethostname(), "POST": self.UPLOAD_PORT}
        # msg = 'UPLOAD  %s\n' % ( self.V)
        # msg += 'Host: %s\n' % socket.gethostname()
        # msg += 'Post: %s\n' % self.UPLOAD_PORT
        # msg += 'Label: %s\n' % str(label)
        # # msg += 'Data: %s\n' % data_string
        # # import pdb
        # # pdb.set_trace()
        # # !c = "%s"%(data_string)
        # # data_loaded = pickle.loads(str.encode(c))
        # # print(data_string)
        # print(len(data_string))
        # self.server.sendall(msg.encode('utf-8'))
        # self.server.sendall(data_string)

        # res = self.server.recv(1024).decode()
        # print('Recieve response: \n%s' % res)


    def classify(self):
    	return

    def look_up(self , disply=True):
        print(self.UPLOAD_PORT ,  self.version)
        result = self.server.recv(1024).decode()
        result = result.split("****")[-2]
        self.peers = json.loads(result)
        for key in self.peers.keys():
            lines = key.splitlines()
            host = lines[1].split(None, 1)[1]
            port = int(lines[0].split(None, 1)[1])
            if port == self.UPLOAD_PORT:
                continue 
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.connect((host, port))
            version = peer.recv(1024).decode()
            if version == '' :
                continue 
            if disply:
                print(port,  version)
            if version > self.version:
                self.version = version
        return

    def download(self):
    	return

    def invalid_input(self):
        raise MyException('Invalid Input.')

    def shutdown(self):
        print('\nShutting Down...')
        self.server.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)



class MyException(Exception):
    pass


if __name__ == '__main__':
    s = Server()
    s.start()
