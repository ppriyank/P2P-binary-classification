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
import tqdm
from trainer import Trainer
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import IoTHubDeviceClient

import random

import boto3
import os 

location = "us-east-1"

os.environ['AWS_PROFILE'] = "Profile1"
os.environ['AWS_DEFAULT_REGION'] = location

bucket_name = "ppriyankbucketdemo"

file = open("../cred.txt","r") 
CONNECTION_server = file.read()
file.close()
BUFFER_SIZE = 4096


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
        
        self.lock = threading.Lock()
        self.h = 100
        self.w = 100
        self.s3 = boto3.client('s3')
        # self.s3 = boto3.client('s3', region_name=location)

        print("Conntected to AWS")
        # response = s3.list_buckets()
        print ()
    
    def start(self):
        try:
            self.registry_manager = IoTHubRegistryManager(CONNECTION_server)
            os.system('az iot hub device-identity create --device-id %s --hub-name pathak'%(self.id))
            print("ID of the client created = %s"%(self.id) )
            print ( "Connecting the Python IoT Hub" )
            self.CONNECTION_STRING = os.popen("az iot hub device-identity show-connection-string --device-id %s --hub-name pathak -o table"%(self.id)).read()
            self.CONNECTION_STRING = self.CONNECTION_STRING.split()[-1]          
            client = IoTHubDeviceClient.create_from_connection_string(self.CONNECTION_STRING)
        except Exception as e:
            print ( "Problems with IOT HUB" )
            os._exit(0)
        print("Connected")    
        self.uploader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploader.bind(('', 0))
        self.UPLOAD_PORT = self.uploader.getsockname()[1]
        self.uploader.listen(5)
        print('Listening on the upload port %s' % self.UPLOAD_PORT)

        message_listener_thread = threading.Thread(target=self.message_listener, args=(client,))
        message_listener_thread.daemon = True
        message_listener_thread.start()
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

            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer.connect((source_host, int(source_port)))

            if len(message) == 5:
                filename = self.DIR + "/" + 'checkpoint.pth.tar'
                self.trainer.package(filename)
                filesize = os.path.getsize(filename)
                peer.send( str(filesize).encode())
                
                send_size = 0 
                with open(filename, "rb") as f:
                    while send_size < int(filesize):
                        bytes_read = f.read(BUFFER_SIZE)
                        peer.sendall(bytes_read)
                        send_size += len(bytes_read)        
            else:
                data =self.id + " " +  str(self.UPLOAD_PORT) + " " + socket.gethostname() + " " + str(self.version)
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
                req = input('\n1: Check Model Version\n2: Check Peers\n3: Look up storage \n4: Train Image \n5: Classify Image \n6: Download \n7: Shut Down\nEnter your request: ')
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
        if display:
            print("Listening to peers, Avaliable peers:")
        peers = json.loads(os.popen("az iot hub device-identity list --hub-name pathak -o json").read())
        so_far  = self.version
        device_id  = 0
        for peer  in peers:
            if peer['deviceId'] == self.id:
                continue 
            else:
                DEVICE_ID = peer['deviceId']
                data = self.id + " " +  str(self.UPLOAD_PORT) + " " + socket.gethostname() + " " + str(self.version) 
                try:
                    self.registry_manager.send_c2d_message(DEVICE_ID, data)        
                    requester, addr = self.uploader.accept()
                    message= requester.recv(1024).decode()
                    message = message.split()
                    if int(message[3]) > so_far:
                        so_far = int(message[3])
                        device_id = DEVICE_ID
                    if display:
                        print("Device id (IOT) %s Device id recieved: %s\tPORT: %s\tHOST: %s\tVersion: %s"%(DEVICE_ID, message[0], message[1] , message[2], message[3]))
                except Exception as e:
                    print("peer information not available, most likely due to token expiry")
                    return self.version , self.id

        return so_far , device_id
    
    def look_up(self):
        print ("Local Storage")
        print ( os.listdir("rfc") ) 
        files = []
        print ("Looking Cloud Storage")
        # import pdb
        # pdb.set_trace()
        
        s3_result =  self.s3.list_objects_v2(Bucket=bucket_name, Delimiter = "/")
        if 'Contents' not in s3_result and 'CommonPrefixes' not in s3_result:
            print ("empty bucket")
        else:
            files = []
            if s3_result.get('Contents'):
                    for key in s3_result['Contents']:
                        print ("Downloading " ,key['Key'])
                        metadata = self.s3.head_object(Bucket=bucket_name, Key=key['Key'])
                        files.append((key['Key'],metadata["Metadata"]["label"]) )
                        with open(self.DIR + "/"  + key['Key'], 'wb') as f:
                            self.s3.download_fileobj(bucket_name, key['Key'], f)

        print ("UPDATED Local Storage")
        print ( os.listdir("rfc") ) 

    def train(self):
        self.download()
        # title = "1.png"
        # label = 1
        title = input('Enter image name: ')
        label = input('Enter label: ')
        
        filename = self.DIR + "/" + title        
        self.s3.upload_file( filename, bucket_name, title, ExtraArgs={'Metadata': {'label': str(label)}})
        file = Path('%s/%s' % (self.DIR, title))
        
        image = Image.open(file)
        image = image.resize(( self.h , self.w) )
        label = int(label)
        loss = self.trainer.train(image , label)
        print ("Training Loss %f" %(loss) ) 
        self.version +=1

        # image.show()
        # data_string = pickle.dumps(image, -1) 
        # # data_loaded = pickle.loads(data_string)
        # if not file.is_file():
        #     raise MyException('File Not Exit!')
        # # msg = {"label" : label , "data": data_string , "host": socket.gethostname(), "POST": self.UPLOAD_PORT}
        # # data_loaded = pickle.loads(str.encode(c))
        # self.server.sendall(msg.encode('utf-8'))
        # self.server.sendall(data_string)
        # res = self.server.recv(1024).decode()
        # print('Recieve response: \n%s' % res)


    def classify(self):
        # cmp --silent ./rfc/checkpoint.pth.tar ../rfc/checkpoint.pth.tar || echo "files are different"
        self.download()
        # title = "1.png"
        title = input('Enter image name: ')
        # label = input('Enter label: ')
        file = Path('%s/%s' % (self.DIR, title))
        
        image = Image.open(file)
        image = image.resize(( self.h , self.w) )
        output = self.trainer.evaluate(image )
        print ("Predicted Label  %d"%(output) )
        return

    
    def download(self):
        print("Searching peers for latest model version")
        so_far , device_id = self.check_peer(display=False)
        filename = self.DIR + "/" + 'checkpoint.pth.tar'
        if int(so_far) > self.version:
            print("Latest Version Located on device" , device_id)
            self.version = int(so_far)
            data = self.id + " " +  str(self.UPLOAD_PORT) + " " + socket.gethostname() + " " + str(self.version) + " q" 
            self.registry_manager.send_c2d_message(device_id, data)        
            requester, addr = self.uploader.accept()
            filesize = requester.recv(1024).decode()
            rec_size = 0 
            with open(filename, "wb") as f:
                while rec_size < int(filesize):
                    bytes_read = requester.recv(BUFFER_SIZE)
                    f.write(bytes_read)
                    rec_size += len(bytes_read)        
            print("Model Download complete" )
            self.trainer.load_package(filename)
        else:
            print("Current Version is already the latest" )
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
