from model import MODEL
import torch 
from torch.autograd import Variable
from torch import nn
import torchvision.transforms as transforms
import json 

class Trainer:
	def __init__(self):
		self.model = MODEL()
		self.transform  = transforms.Compose([
            transforms.Resize((100, 100), interpolation=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

		self.optimizer = torch.optim.Adam( self.model.parameters(), lr=0.0001)
		self.logsoftmax = nn.LogSoftmax(dim=1)

	def preprocess(self,img):
		return self.transform(img)

	def loss(self, output, label, epsilon=1e-6 , ):
		log_probs = self.logsoftmax(output)
		targets = torch.zeros(log_probs.size()).scatter_(1, label.unsqueeze(0).unsqueeze(1).data, 1)
		targets = (1 - epsilon) * targets + epsilon / 2
		loss = (- targets * log_probs).mean(0).sum()
		return loss

	def train(self, x, label):
		self.model.train()

		x = self.preprocess(x).unsqueeze(0)
		x, label = Variable(x), Variable(torch.tensor(label))
		
		output=  self.model(x)
		loss = self.loss(output, label)
		
		self.optimizer.zero_grad()
		loss.backward()
		self.optimizer.step()

		return loss.item()

	def loss(self, output, label, epsilon=1e-6 ):
		log_probs = self.logsoftmax(output)
		targets = torch.zeros(log_probs.size()).scatter_(1, label.unsqueeze(0).unsqueeze(1).data, 1)
		targets = (1 - epsilon) * targets + epsilon / 2
		loss = (- targets * log_probs).mean(0).sum()
		return loss

	def evaluate(self, x ):
		self.model.eval()
		x = self.preprocess(x).unsqueeze(0)
		x= Variable(x)
		output =  self.model(x)

		return output.argmax().item()

	def package(self, path ):
		state_dict = self.model.state_dict()
		# result =  json.dumps(state_dict) 
		torch.save(state_dict, path)

	def load_package(self, path ):
		checkpoint = torch.load(path)
		self.model.load_state_dict(checkpoint,  strict=True)
		
		
		
