import socket
import threading
import os
import sys
from collections import defaultdict
from pathlib import Path
import pickle
import json 
import time 
from PIL import Image
import pickle

from trainer import Trainer
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import IoTHubDeviceClient

import random

CONNECTION_server = "HostName=pathak.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=S/afv4/YDirVxtHdnzmRi7gGwIOswE8ci50mKUgkPFs="



class Server(object):
    def __init__(self, HOST='localhost', PORT=7734):
        self.SERVER_HOST = 'localhost'
        self.SERVER_PORT = 7734
        
        self.HOST = HOST
        self.DIR = 'rfc'  # file directory
        Path(self.DIR).mkdir(exist_ok=True)
        self.UPLOAD_PORT = None
        self.version = 0
        self.trainer = Trainer()
        self.version = 0
        self.id = str(random.randint(0,5000))
        self.registry_manager = IoTHubRegistryManager(CONNECTION_server)

        self.h = 100
        self.w = 100
    
    def start(self):
        
        
        os.system('az iot hub device-identity create --device-id %s --hub-name pathak'%(self.id))
        print("ID of the client created = %s"%(self.id) )
        self.CONNECTION_STRING = os.popen("az iot hub device-identity show-connection-string --device-id %s --hub-name pathak -o table"%(self.id)).read()
        self.CONNECTION_STRING = self.CONNECTION_STRING.split()[-1]          


        self.uploader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploader.bind(('', 0))
        self.UPLOAD_PORT = self.uploader.getsockname()[1]
        self.uploader.listen(5)
        print('Listening on the upload port %s' % self.UPLOAD_PORT)

        # uploader_process = threading.Thread(target=self.init_upload)
        print ( "Connecting the Python IoT Hub" )
        client = IoTHubDeviceClient.create_from_connection_string(self.CONNECTION_STRING)
        
        message_listener_thread = threading.Thread(target=self.message_listener, args=(client,))
        message_listener_thread.daemon = True
        message_listener_thread.start()

        # uploader_process.start()
        print("Connected")
        self.cli()


    def message_listener(self, client):
        port = self.UPLOAD_PORT
        host = socket.gethostname()
        while True:
            message = client.receive_message()
            message = str(message.data)
            message = message[2:].split()
            id = message[0]
            source_port = message[1]
            source_host = message[2]
            source_version = message[3]
            data =self.id + " " +  str(self.UPLOAD_PORT) + " " + socket.gethostname() + " " + str(self.version)

            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.connect((source_host, int(source_port)))
            peer.sendall(data.encode('utf-8'))
            
            
    def cli(self):        
        self.command_dict = {'1': self.check_version,
                        '2': self.check_peer,
                        '3': self.look_up,
                        '4': self.train,
                        '5': self.classify,
                        '6': self.download,
                        '7': self.shutdown}                        
        while True:
            try:
                req = input('\n1: Check Model Version\n2: Check Peers\n3: Look up images\n4: Train Image \n5: Classify Image, \n5: Download \n6: Shut Down\nEnter your request: ')
                self.command_dict.setdefault(req, self.invalid_input)()
            except MyException as e:
                print(e)
            except Exception:
                print('System Error.')
            except BaseException:
                self.shutdown()

    
    def check_version(self):
        print("Current Model Version is %d" %(self.version))

    def check_peer(self , display=True):

        print("Listening to peers, Avaliable peers:")
        peers = json.loads(os.popen("az iot hub device-identity list --hub-name pathak -o json").read())
        so_far  = self.version
        for peer  in peers:
            if peer['deviceId'] == self.id:
                continue 
            else:
                DEVICE_ID = peer['deviceId']
                data =self.id + " " +  str(self.UPLOAD_PORT) + " " + socket.gethostname() + " " + str(self.version)
                self.registry_manager.send_c2d_message(DEVICE_ID, data)        
                requester, addr = self.uploader.accept()
                message= requester.recv(1024).decode()
                message = message.split()
                so_far = max(so_far ,  message[3])
                if display:
                    print("Device id (IOT) %s Device id recieved: %s\tPORT: %s\tHOST: %s\tVersion: %s"%(DEVICE_ID, message[0], message[1] , message[2], message[3]))
        return so_far
    
    def look_up(self):
        print ( os.listdir("rfc") ) 


    def train(self):
        so_far = self.check_peer(display=False)
        self.version +=1
        title = "1.png"
        label = 1
        # title = input('Enter image name: ')
        # label = input('Enter label: ')
        
        file = Path('%s/%s' % (self.DIR, title))
        
        image = Image.open(file)
        image = image.resize(( self.h , self.w) )
        
        loss = self.trainer.train(image , label)
        print ("Training Loss %f" , loss)

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
        so_far = self.check_peer(display=False)
        title = "1.png"
        # title = input('Enter image name: ')
        # label = input('Enter label: ')
        file = Path('%s/%s' % (self.DIR, title))
        
        image = Image.open(file)
        image = image.resize(( self.h , self.w) )

        output = self.trainer.evaluate(image )
        print ("Evaluation %f"%(output) )
        return

    
    def download(self):
    	return

    def invalid_input(self):
        raise MyException('Invalid Input.')

    def shutdown(self):
        try:
            print("deleting the device on hub")
            # az iot hub device-identity delete --device-id 1803 --hub-name pathak 
            os.system('az iot hub device-identity delete --device-id %s --hub-name pathak'%(self.id))
            print('\nShutting Down...')
        except Exception:
            print ( "IoT Hub C2D Messaging service sample stopped" )
        os._exit(0)
            



class MyException(Exception):
    pass


if __name__ == '__main__':
    s = Server()
    s.start()
