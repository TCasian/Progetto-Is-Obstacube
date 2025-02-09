import torch
from torch.utils.tensorboard import SummaryWriter
import torchvision.models as models
from tensorboard import program
import os
import time

tb = program.TensorBoard()
logdir = os.path.join(os.getcwd(), 'runs')
tb.configure(argv=[None, '--logdir', logdir])
url = tb.launch()
print(f"TensorBoard avviato all'indirizzo: {url}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("TensorBoard chiuso.")