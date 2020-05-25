import torch
from torch import nn
from torch.nn import functional as F





class MODEL(nn.Module):
    def __init__(self):
        super(MODEL, self).__init__()
        
        self.conv1 = nn.Conv2d(3, 32, [5,5]) 
        self.mp1 = nn.MaxPool2d(3)

        self.conv2 = nn.Conv2d(32, 64, [5,5]) 
        self.mp2 = nn.MaxPool2d(3)

        self.gap = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(64, 2 )
        
        
    def forward(self, x):

        x = self.conv1(x)
        x = self.mp1(x)
        x = F.relu(x)

        x = self.conv2(x)
        x = self.mp2(x)
        x = F.relu(x)


        x = self.gap(x).squeeze(-1).squeeze(-1)
        x = self.classifier(x)
        return x
