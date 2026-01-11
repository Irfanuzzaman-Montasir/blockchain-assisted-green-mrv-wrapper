import time
from greenmrv import mrv_run

def train():
    # Replace with real training loop
    time.sleep(3)

with mrv_run(
    experiment_name="resnet18_cifar10_baseline",
    model_name="ResNet18",
    dataset_name="CIFAR-10",
    # Leave framework auto OR set it; auto is fine
    # framework="auto",
    epochs=90,
    batch_size=128
):
    train()
