import socket
import threading
import os
import sys
from collections import defaultdict
from pathlib import Path
import pickle
import json 
import torch
from PIL import Image
import pickle


PORTS = (5000 , 6000) 

class Server(object):
    def __init__(self, HOST='localhost', PORT=7734, V='P2P-CI/1.0'):
        self.SERVER_HOST = 'localhost'
        self.SERVER_PORT = 7734
        
        self.HOST = HOST
        self.V = V
        self.DIR = 'rfc'  # file directory
        Path(self.DIR).mkdir(exist_ok=True)
        self.UPLOAD_PORT = None
        self.shareable = True
        self.version = 0
        self.lock = threading.Lock()
        self.h = 100
        self.w = 100
        
        # element: {(host,port), set[rfc #]}
        self.peers = {}
        # element: {RFC #, (title, set[(host, port)])}
        self.rfcs = {}        
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

        # interactive shell
        thread = threading.Thread(target=self.server_peer_data(), args=())
        thread.start()

        thread = threading.Thread(target=self.cli(), args=())
        thread.start()

        self.uploader.listen(5)
        while True:
            soc, addr = self.uploader.accept()
            print('%s:%s connected' % (addr[0], addr[1]))
            thread = threading.Thread(target=self.handler, args=(soc, addr))
            thread.start()
            
        
    def server_peer_data(self):
        while True :
            result = self.server.recv(1024).decode()
            result = result.split("****")[-2]
            self.peers = json.loads(result)
        sys.exit()

        
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

        for i in range(PORTS[0] , PORTS[1]):
            result_of_check = self.uploader.connect_ex(('', i))
            if result_of_check == 0:
                print("available port %s" %(i))
                self.uploader.bind(('', i))
                break

        self.UPLOAD_PORT = self.uploader.getsockname()[1]
        self.uploader.close()

    def upload_image(self, num=None, title=None):
        
        title = "1.png"
        label = 1
        # title = input('Enter image name: ')
        # label = input('Enter label: ')
        file = Path('%s/%s' % (self.DIR, title))
        print(file)
        image = Image.open(file)
        image = image.resize(( self.h , self.w) ) 

        import pdb
        pdb.set_trace()
        
        dest = ('<broadcast>',10100)
        msg = "------"
        self.uploader.sendto(msg.encode(), dest)
        # self.uploader.sendto(, dest)
        # image.show()
        data_string = pickle.dumps(image, -1) 
        # data_loaded = pickle.loads(data_string)
        if not file.is_file():
            raise MyException('File Not Exit!')
        # msg = {"label" : label , "data": data_string , "host": socket.gethostname(), "POST": self.UPLOAD_PORT}
        msg = 'UPLOAD  %s\n' % ( self.V)
        msg += 'Host: %s\n' % socket.gethostname()
        msg += 'Post: %s\n' % self.UPLOAD_PORT
        msg += 'Label: %s\n' % str(label)
        # msg += 'Data: %s\n' % data_string
        # import pdb
        # pdb.set_trace()
        # !c = "%s"%(data_string)
        # data_loaded = pickle.loads(str.encode(c))
        # print(data_string)
        print(len(data_string))
        self.server.sendall(msg.encode('utf-8'))
        self.server.sendall(data_string)

        res = self.server.recv(1024).decode()
        print('Recieve response: \n%s' % res)


    def classify(self):
    	return

    def look_up(self):
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
