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

# from trainer import Trainer
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import IoTHubDeviceClient

import random 



CONNECTION_STRING_server = "HostName=pathak.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=c28TK/cpUTYqeRdPFhEiKt/j5Bx27Kw+8JeWj70kgtY="



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
        # self.trainer = Trainer()
        self.version = 0
        self.id = str(random.randint(0,5000))
        
        os.system('az iot hub device-identity create --device-id %s --hub-name pathak'%(self.id))
        string = os.popen("az iot hub device-identity show-connection-string --device-id %s --hub-name pathak -o table"%(self.id)).read()
        self.CONNECTION_STRING = string.split()[-1]  

    def start(self):
        # connect to server
        uploader_process = threading.Thread(target=self.init_upload)

        print ( "Starting the Python IoT Hub, listening to peers" )
        client = IoTHubDeviceClient.create_from_connection_string(self.CONNECTION_STRING)
        
        message_listener_thread = threading.Thread(target=self.message_listener, args=(client,))
        message_listener_thread.daemon = True
        message_listener_thread.start()

        uploader_process.start()
        print('Listening on the upload port %s' % self.UPLOAD_PORT)

        print('Connecting to the IOT HUB')
        registry_manager = IoTHubRegistryManager(CONNECTION_STRING_server)
        # self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
        #     self.server.connect((self.SERVER_HOST, self.SERVER_PORT))
            header = "%s %s 1"%(self.UPLOAD_PORT, self.HOST)
            registry_manager.send_c2d_message(self.id, header)
        except Exception:
            print ( "IoT Hub C2D Messaging service sample stopped" )
            return
        print("Connected")
        # interactive shell
        # self.cli()


    def message_listener(self, client):
        while True:
            print("======")
            message = client.receive_message()
            message = str(message)[2:].split()
            host = message[1]
            port = int(message[0])
            status = message[2][:1]
            # import pdb
            # pdb.set_trace()
            print(port)
            if port == self.UPLOAD_PORT:
                continue
            if status == "1":
                self.peers[(port ,host)] = 1
                print("\nNew Peer added PORT %d"%(port))
            else:
                del self.peers[(port ,host)]
                print("\nPeer deleted PORT %d"%(port))
            
            print(message)
            
    def cli(self):        
        self.command_dict = {'1': self.upload_image,
                        '2': self.classify,
                        '3': self.look_up,
                        '4': self.download,
                        '5': self.shutdown}                        
        # max_index = max(self.command_dict.keys())
        # import pdb
        # pdb.set_trace()
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
        
        # self.trainer.train(image , label)
        
        

            
            
        
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
        print("deleting the device on hub")
        os.system('az iot hub device-identity delete --device-id %s --hub-name pathak'%(self.id))
        print('\nShutting Down...')
        self.server.close()
        try:
            header = "%s %s 0"%(self.UPLOAD_PORT, self.HOST)
            registry_manager.send_c2d_message(DEVICE_ID, header)
        except Exception:
            print ( "IoT Hub C2D Messaging service sample stopped" )
            return
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)



class MyException(Exception):
    pass


if __name__ == '__main__':
    s = Server()
    s.start()
