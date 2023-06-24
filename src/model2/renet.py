import torch
torch.cuda.current_device()
import torch.nn as nn
import torch.nn.functional as F
import Unet
from Unet import DownsampleLayer, UpSampleLayer




def make_model(args, parent=False):
    return Mainnet(args)

class Mainnet(nn.Module):
    def __init__(self, args):
        super(Mainnet, self).__init__()
        self.renet = Renet()
        self.lenet = Lenet()
        self.scale = Scale()
        self.cnt = 0
        self.device = torch.device('cpu' if args.cpu else 'cuda')


    def forward(self,  input_r, input_l, a,input):
        b, _,_,_ = input_r.shape
        al = a.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3).expand(b, 1, 1, 1).to(self.device)
        scale = self.scale(input)
        R = self.renet(input_r,scale)
        L = self.lenet(input_l, al)
        return R, L,scale


class Scale(nn.Module):
    def __init__(self):
        super(Scale, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=64,kernel_size=3, padding=1, padding_mode='reflect', bias=True),
            nn.LeakyReLU(inplace=True),
            nn.Conv2d(in_channels=64, out_channels=1, kernel_size=1, padding=0, padding_mode='reflect', bias=True),
            nn.Sigmoid(),
        )
    def forward(self, x):
        out = self.conv1(x)
        return out

class Lenet(nn.Module):
    def __init__(self):
        super(Lenet, self).__init__()
        self.relu = nn.ReLU(inplace=True)
        self.res1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1, padding_mode='reflect', bias=True),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=32, out_channels=1, kernel_size=3, padding=1, padding_mode='reflect', bias=True),
        )
        self.res2 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1, padding_mode='reflect', bias=True),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=32, out_channels=1, kernel_size=3, padding=1, padding_mode='reflect', bias=True),
        )
        self.scale = nn.Sequential(
            nn.Linear(1, 100, bias=True),
            nn.ReLU(inplace=True),
            nn.Linear(100, 1, bias=True),
            nn.Sigmoid()
        )
    def forward(self, input, a):
        scale = self.scale(a)
        res1 = self.res1(input)
        out1 = self.relu(input + 1*res1)
        out2 = self.relu(out1 + scale * self.res2(out1))
        return out2


class Renet(nn.Module):
    def __init__(self):
        super(Renet, self).__init__()
        self.relu = nn.ReLU(inplace=True)
        self.channels =4
        self.res1 = nn.Sequential(
                                   nn.Conv2d(self.channels, 32, kernel_size=3, stride=1, padding=1,
                                             dilation=1, padding_mode='reflect'),
                                   nn.ReLU(),
                                   nn.Conv2d(32, self.channels, kernel_size=3, stride=1, padding=1,
                                             dilation=1, padding_mode='reflect'),
                                   )
        self.res2 = nn.Sequential(
            nn.Conv2d(self.channels, 32, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
            nn.ReLU(),
            nn.Conv2d(32, self.channels, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
        )
        self.res3 = nn.Sequential(
            nn.Conv2d(self.channels, 32, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
            nn.ReLU(),
            nn.Conv2d(32, self.channels, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
        )
        self.res4 = nn.Sequential(
            nn.Conv2d(self.channels, 32, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
            nn.ReLU(),
            nn.Conv2d(32, self.channels, kernel_size=3, stride=1, padding=1,
                      dilation=1, padding_mode='reflect'),
        )
    def forward(self, input,a):
        input = torch.cat((input,a),dim=1)
        out1 = self.relu(input + 1. * self.res1(input))
        out2 = self.relu(out1 + 1.*self.res2(out1))
        out3 = self.relu(out2 + 1. * self.res3(out2))
        out4 = self.relu(out3 + 1 * self.res4(out3))
        return out4[:,:3,:,:]
