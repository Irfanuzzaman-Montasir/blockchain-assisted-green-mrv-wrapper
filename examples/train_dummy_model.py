import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from greenmrv.core import mrv_run


# -----------------------------
# Simple MLP Model
# -----------------------------
class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, 10)
        )

    def forward(self, x):
        return self.net(x)


def main():
    # -----------------------------
    # Synthetic Dataset
    # -----------------------------
    num_samples = 200_000   # controls runtime
    x = torch.randn(num_samples, 512)
    y = torch.randint(0, 10, (num_samples,))

    dataset = TensorDataset(x, y)
    loader = DataLoader(
        dataset,
        batch_size=256,
        shuffle=True,
        num_workers=0
    )

    # -----------------------------
    # Model + Training Setup
    # -----------------------------
    device = torch.device("cpu")  # force CPU for reproducibility
    model = SimpleMLP().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    # -----------------------------
    # MRV Wrapper (THIS IS THE KEY)
    # -----------------------------
    with mrv_run(
        experiment_name="mlp_synthetic_4min",
        model_name="SimpleMLP",
        dataset_name="SyntheticGaussian",
        epochs=3,
        batch_size=256,
        region="local_grid"
    ):
        model.train()
        for epoch in range(3):
            for batch_x, batch_y in loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)

                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch+1} completed")


if __name__ == "__main__":
    main()
