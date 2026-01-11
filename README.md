# Blockchain-Assisted Green MRV Wrapper (Python Wrapper - v0.1)

A lightweight Python wrapper for **Measurement–Reporting–Verification (MRV)** of Machine Learning workloads.

This repository currently implements **Part 1 (Python wrapper)**:
- Wraps any training code (PyTorch/TensorFlow/JAX or anything)
- Uses **CodeCarbon** to measure energy consumption and CO₂ emissions
- Auto-collects hardware metadata (CPU/RAM/GPU if available)
- Auto-detects ML framework + version
- Generates a standardized **MRV JSON** record and saves it to a file

> ✅ Next update (later): canonical hashing + blockchain anchoring (immutable proof).

---

## Why this project exists

Current ML carbon reporting is often:
- self-reported
- stored locally (mutable)
- not independently verifiable

This project moves toward **verifiable ML sustainability reporting** by producing a standardized MRV record that can later be hashed and anchored on-chain.

---

## What the wrapper does (current version)

### Workflow
1. User runs Python training code
2. Wrapper starts CodeCarbon tracking
3. Training runs normally
4. Wrapper stops tracking
5. Wrapper generates an MRV JSON file
6. Wrapper saves MRV JSON to disk

### Output files
After running, you will get:

mrv_records/
MRV-<uuid>.json
MRV-<uuid>_codecarbon.csv


- `MRV-<uuid>.json` = standardized MRV record (main artifact)
- `MRV-<uuid>_codecarbon.csv` = raw CodeCarbon output (for audit / parsing energy_kwh)

---

## Installation

### Requirements
- Python **3.9+**
- Works in: VS Code / local machine / Google Colab

### Install dependencies
In your environment:

## bash
```pip install codecarbon psutil py-cpuinfo```

## Optional (for better NVIDIA GPU detection):

```pip install pynvml```

### Install this package (editable mode)

From the project root:

```pip install -e . ```

### Now just run the code in Examples files using the wrapper

## The wrapper prints:

# ```MRV ID```
# ```MRV JSON file path```
# ```CodeCarbon CSV path```

## Example run
Run the included demo:
python examples/demo_train.py


## Expected output:

[greenmrv] MRV ID: MRV-...
[greenmrv] MRV JSON saved: .../mrv_records/MRV-....json
[greenmrv] CodeCarbon CSV: .../mrv_records/MRV-...._codecarbon.csv

