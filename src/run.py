import argparse
import pickle
import time
import os

from torch.utils.data import DataLoader
import torchvision

from steps import train
from models import DevModel, VanillaConvNet
from dataloaders import GenomeDataset
from steps import build_transforms

parser = argparse.ArgumentParser()

parser.add_argument("--exp", type=str, default="exp/default_exp")

parser.add_argument("--train-data", type=str, default="data/chm20/train.npz")
parser.add_argument("--valid-data", type=str, default="data/chm20/test.npz")

parser.add_argument("--model", type=str, choices=["VanillaConvNet"],
                    default="VanillaConvNet")

parser.add_argument("--num-epochs", type=int, default=99999999)
parser.add_argument("-b", "--batch-size", type=int, default=32)
parser.add_argument("--lr", type=float, default=0.01)
parser.add_argument("--lr-decay", type=int, default=-1)

parser.add_argument("--pos-emb", type=str, choices=["linpos", "trained1",
                                                              "trained2"], default=None)

parser.add_argument("--loss", type=str, default="BCE", choices=["BCE"])

parser.add_argument("--resume", dest="resume", action='store_true')

parser.add_argument("--seq-len", type=int, default=516800)
parser.add_argument("--n-classes", type=int, default=7)

if __name__ == '__main__':

    args = parser.parse_args()

    print(args)
    if args.resume:
        assert (bool(args.exp))
        with open("%s/args.pckl" % args.exp, "rb") as f:
            args = pickle.load(f)
            args.resume = True

    transforms = build_transforms(args)

    train_dataset = GenomeDataset(data=args.train_data, transforms=transforms)
    valid_dataset = GenomeDataset(data=args.valid_data, transforms=transforms)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size)
    valid_loader = DataLoader(valid_dataset, batch_size=args.batch_size)

    # t = time.time()
    # for x in train_loader:
    #     pass
    # print("loop time", time.time() - t)

    if args.model == "VanillaConvNet":
        model = VanillaConvNet(args)
        # model = DevModel(7)
    else:
        raise ValueError()


    if not args.resume:
        if os.path.isdir(args.exp):
            raise Exception("Experiment name " + args.exp +" already exists.")
        os.mkdir(args.exp)
        os.mkdir(args.exp + "/models")

    with open(args.exp + "/args.pckl", "wb") as f:
        pickle.dump(args, f)

    train(model, train_loader, valid_loader, args)