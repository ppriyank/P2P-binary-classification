from model import MODEL
import torch 
from torch.autograd import Variable
from torch import nn
import torchvision.transforms as transforms

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
	# def package(self):
	# 	state_dict = model.module.state_dict()
	# 	save_checkpoint({
                       
 #                            'state_dict': state_dict,
 #                       }, is_best, osp.join(args.save_dir, args.arch+ "_" + args.name + "_"  +args.opt+ '_checkpoint_ep' + str(epoch+1) + '.pth.tar')) 

	# 	def save_checkpoint(state, is_best, fpath='checkpoint.pth.tar'):
 #    mkdir_if_missing(osp.dirname(fpath))
 #    matching_file = fpath.split("ep")[0].split("/")[-1]
 #    dir_ =  osp.dirname(fpath)
 #    for f in os.listdir(dir_):
 #        if re.search(matching_file, f):
 #            os.remove(os.path.join(dir_, f))            
 #    torch.save(state, fpath)