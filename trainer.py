from model import MODEL
import torch 




def trainer():

x = torch.rand(1,3,100,100)


m = MODEL()
m(x)