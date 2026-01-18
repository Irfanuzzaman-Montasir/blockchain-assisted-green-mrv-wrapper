import time
import numpy as np

from greenmrv import mrv_run


def train_numpy(steps: int = 50, batch_size: int = 32):
    # Very small random MLP-like training on synthetic data (no external deps)
    in_dim = 32 * 32 * 3
    out_dim = 10

    # Initialize weights and simple SGD
    W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.01
    lr = 0.1

    for step in range(steps):
        # random inputs and one-hot targets
        X = np.random.randn(batch_size, in_dim).astype(np.float32)
        y = np.random.randint(0, out_dim, size=(batch_size,))

        # forward: linear + softmax
        logits = X.dot(W)
        # stable softmax
        logits = logits - logits.max(axis=1, keepdims=True)
        exp = np.exp(logits)
        probs = exp / exp.sum(axis=1, keepdims=True)

        # cross-entropy loss and gradient
        one_hot = np.zeros_like(probs)
        one_hot[np.arange(batch_size), y] = 1.0
        loss = -np.sum(one_hot * np.log(probs + 1e-12)) / batch_size

        grad_logits = (probs - one_hot) / batch_size
        grad_W = X.T.dot(grad_logits)

        # SGD step
        W -= lr * grad_W

        if step % 10 == 0:
            print(f"[tiny_train] step={step} loss={loss:.4f}")


if __name__ == "__main__":
    with mrv_run(
        experiment_name="tiny_numpy_model",
        model_name="tiny_mlp",
        dataset_name="synthetic",
        epochs=1,
        batch_size=32,
    ):
        train_numpy(steps=50, batch_size=32)
