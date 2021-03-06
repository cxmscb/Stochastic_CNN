from __future__ import print_function
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.multiprocessing as mp

from train import train,micro_train

# Training settings
# ==============================================================================
parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                    help='input batch size for training (default: 64)')
parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                    help='input batch size for testing (default: 1000)')
parser.add_argument('--epochs', type=int, default=100, metavar='N',
                    help='number of epochs to train (default: 10)')
# ------------------------------------------------------------------------------
parser.add_argument('--SGD_lr', type=float, default=0.0005, metavar='LR',
                    help='SGD learning rate (default: 0.01)')
parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                    help='SGD momentum (default: 0.5)')
parser.add_argument('--Adam_lr', type=float, default=0.001, metavar='LR',
                    help='Adam learning rate (default: 0.01)')
# ------------------------------------------------------------------------------
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='disables CUDA training')
# ------------------------------------------------------------------------------
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--num_train', type=int, default=1, metavar='N',
                    help='how many training times to use (default: 1)')
# ==============================================================================

class SCSF_Net(nn.Module):
    def __init__(self):
        super(SCSF_Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(1440, 10)

    def forward(self, x):
        # stride – the stride of the window. Default value is kernel_size, thus it is 2 here.
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = self.conv2_drop(x)
        x = x.view(-1, 1440)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        return F.log_softmax(x, dim=1)

class DCDF_Net(nn.Module):
    def __init__(self):
        super(DCDF_Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        # stride (the stride of the window) : Default value is kernel_size, thus it is 2 here.
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        # stride (the stride of the window) : Default value is kernel_size, thus it is 2 here.
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

if __name__ == '__main__':
    args = parser.parse_args()
    torch.manual_seed(args.seed)
    
    use_cuda = not args.no_cuda and torch.cuda.is_available()

    device=torch.device("cuda" if use_cuda else "cpu")

    # model = SCSF_Net()

    # # model.share_memory().to(device) # gradients are allocated lazily, so they are not shared here 

    # train(args,model,device)
    
    # torch.save(model.state_dict(),"./C10F1440.pkl")

    model_re=SCSF_Net()
    model_re.load_state_dict(torch.load("./C10F1440.pkl"))

    layer_id=0
    for child in model_re.children():
        layer_id +=1
        print("layer Id: "+str(layer_id), child)
        for param in child.parameters():
            param.requires_grad = False

    model_re.fc1.weight.requires_grad= True
    model_re.fc1.bias.requires_grad=True

    # for param in model_re.parameters():
    #     print(param)
    #     param.requires_grad = False
    
    # num_ftrs=model_re.fc1.in_features
    # model_re.fc1=nn.Linear(num_ftrs,10)

    micro_train(args,model_re,device)