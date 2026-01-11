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

# If you want more precise

# Blockchain-Assisted-MRV

## Setup Instructions

Follow the steps below to clone the repository and install the required dependencies.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Irfanuzzaman-Montasir/blockchain-assisted-green-mrv-wrapper.git
cd blockchain-assisted-green-mrv-wrapper
```

> ⚠️ **PowerShell note**: If `blockchain-assisted-green-mrv-wrapper` causes issues, use:
>
> ```powershell
> cd .\blockchain-assisted-green-mrv-wrapper
> ```
>
> Or rename the folder:
>
> ```powershell
> Rename-Item "-Blockchain-Assisted-MRV" "Blockchain-Assisted-MRV"
> cd Blockchain-Assisted-MRV
> ```

---

## Step 2: Install Required Python Packages

Make sure you have Python 3 installed and `pip` available.

```bash
pip install codecarbon psutil py-cpuinfo
```

---

## Step 3: Install the Project in Editable Mode

From the project root directory:

```bash
pip install -e .
```

This installs the project in editable (development) mode.

---

## Troubleshooting (Step 2 or Step 3 Errors)

If you encounter SSL or certificate-related errors (for example, referencing `C:\cacert.pem`), follow the steps below.

### 1️⃣ Check if SSL / certificate environment variables are set

Run the following commands in **PowerShell**:

```powershell
echo $env:SSL_CERT_FILE
echo $env:REQUESTS_CA_BUNDLE
```

If either command prints:

```
C:\cacert.pem
```

then this is causing the issue.

---

### 2️⃣ Remove the problematic variables (current session only)

```powershell
Remove-Item Env:SSL_CERT_FILE -ErrorAction SilentlyContinue
Remove-Item Env:REQUESTS_CA_BUNDLE -ErrorAction SilentlyContinue
```

After removing them, retry:

```bash
pip install codecarbon psutil py-cpuinfo
pip install -e .
```

---

## Notes

* These environment variable changes apply **only to the current PowerShell session**.
* If the problem persists across sessions, check your system environment variables or `pip config list`.

---

## ✅ Setup Complete

You should now be able to run and modify the project successfully.

If you face further issues, please open an issue or contact the main


### Now just run the code in Examples files using the wrapper

## The wrapper prints:

# ```MRV ID```
# ```MRV JSON file path```
# ```CodeCarbon CSV path```

## Example run
Run the included demo:
python examples/demo_train.py

