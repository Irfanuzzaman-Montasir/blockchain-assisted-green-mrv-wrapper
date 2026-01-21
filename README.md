# Blockchain-Assisted Green MRV Wrapper

A lightweight Python wrapper for **Measurement–Reporting–Verification (MRV)** of Machine Learning workloads. 

This tool measures the energy consumption and CO₂ emissions of any ML training script, generates a standardized **MRV JSON** record, and **anchors the record's integrity hash on a local Ethereum blockchain (Ganache)**.

## Features

- **Universal Wrapper**: Works with PyTorch, TensorFlow, JAX, or any Python code.
- **Automated Tracking**: Uses [CodeCarbon](https://codecarbon.io/) to measure hardware energy usage (GPU/CPU/RAM).
- **Auto-Detection**: Automatically detects ML frameworks, hardware specs, and library versions.
- **Blockchain Anchoring**: Computes a canonical SHA-256 hash of the MRV record and registers it on a local blockchain (Ganache) to prove integrity.
- **Verification UI**: Includes a Streamlit app to verify that an MRV JSON file matches its on-chain record.

---

## Prerequisites

1.  **Python 3.9+**
2.  **Ganache** (for local blockchain simulation)
    *   Download [Ganache UI](https://trufflesuite.com/ganache/)
    *   **OR** install Ganache CLI: `npm install -g ganache`

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Irfanuzzaman-Montasir/blockchain-assisted-green-mrv-wrapper.git
cd blockchain-assisted-green-mrv-wrapper
```

### 2. Install dependencies

Install the required Python packages:

```bash
pip install codecarbon psutil py-cpuinfo web3 py-solc-x streamlit
```

### 3. Install the package in editable mode

```bash
pip install -e .
```

---

## Usage

### 1. Start Ganache
Before running any code, you must have a local Ganache blockchain running.

*   **GUI**: Open Ganache and click "Quickstart". Ensure it is running on `http://127.0.0.1:7545`.
*   **CLI**: Run `ganache-cli -p 7545` (or just `ganache`).

### 2. Run an Experiment
You can wrap your training loop with `mrv_run`. See `examples/train_dummy_model.py` for a complete example.

**Run the example:**
```bash
python examples/train_dummy_model.py
```

**What happens?**
1.  The wrapper connects to Ganache and deploys a new `MRVRegistry` Smart Contract (for this run).
2.  It tracks energy usage during the training.
3.  After training, it saves the **MRV JSON** to `mrv_records/`.
4.  It computes the SHA-256 hash of the record.
5.  It sends a transaction to Ganache to register the hash.
6.  The final JSON includes the **Transaction Hash** and **Contract Address**.

### 3. Verify the Record
To verify that an MRV record hasn't been tampered with, use the included Streamlit app.

```bash
streamlit run src/greenmrv/verify_streamlit.py
```

*   Upload the generated JSON file from `mrv_records/`.
*   Enter the `mrv_id` (found inside the JSON or printed in the console).
*   The app will recompute the hash and check the blockchain to ensure it matches.

---

## Project Structure

*   `src/greenmrv`: Core package source code.
    *   `core.py`: Main logic for the wrapper.
    *   `blockchain_ganache.py`: Handles Ganache connection and contract validation.
    *   `verify_streamlit.py`: Verification UI.
    *   `ganache_chain/`: Contains the Solidity Smart Contract (`MRVRegistry.sol`).
*   `examples`: Example scripts showing how to use the wrapper.
*   `mrv_records`: Output directory for generated MRV JSONs and CSVs.

## Integration

To use this in your own project:

```python
from greenmrv import mrv_run

# Wrap your training code
with mrv_run(
    experiment_name="my_model_v1",
    framework="PyTorch",  # Optional: auto-detected if omitted
    epochs=10
):
    # Your actual training loop here
    train_model()
```
