import json
from pathlib import Path
from web3 import Web3
import streamlit as st

from greenmrv.integrity import compute_mrv_sha256

# -------------------------------
# Ganache Configuration
# -------------------------------
GANACHE_RPC = "http://127.0.0.1:7545"

# -------------------------------
# Smart Contract ABI (minimal)
# -------------------------------
MRV_REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "mrvId", "type": "string"}],
        "name": "getMRV",
        "outputs": [
            {"internalType": "bytes32", "name": "hash", "type": "bytes32"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "address", "name": "submitter", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


def get_onchain_hash(contract_address: str, mrv_id: str) -> bytes:
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to Ganache")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=MRV_REGISTRY_ABI,
    )

    hash_bytes, _, _ = contract.functions.getMRV(mrv_id).call()
    return hash_bytes


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="MRV Verifier", layout="centered")

st.title("🔍 Blockchain-Assisted MRV Verifier")
st.write("Verify the integrity of ML emission reports using blockchain.")

uploaded_file = st.file_uploader("Upload MRV JSON file", type=["json"])
mrv_id = st.text_input("Enter MRV ID")

if uploaded_file and mrv_id:
    try:
        mrv_json = json.load(uploaded_file)

        # -------------------------------
        # Recompute hash
        # -------------------------------
        recomputed_hash = compute_mrv_sha256(mrv_json)

        st.subheader("Computed Hash")
        st.code(recomputed_hash)

        integrity = mrv_json.get("integrity", {})
        contract_address = integrity.get("contract_address")

        if not contract_address or contract_address == "not_registered":
            st.error("No blockchain contract address found in MRV JSON.")
            st.stop()

        # -------------------------------
        # Query blockchain
        # -------------------------------
        onchain_hash_bytes = get_onchain_hash(contract_address, mrv_id)
        onchain_hash_hex = onchain_hash_bytes.hex()

        st.subheader("On-chain Hash")
        st.code(onchain_hash_hex)

        # -------------------------------
        # Compare
        # -------------------------------
        if recomputed_hash == onchain_hash_hex:
            st.success("✅ VALID: MRV record is authentic and untampered.")
        else:
            st.error("❌ TAMPERED: MRV JSON does not match blockchain record.")

    except Exception as e:
        if "MRV not found" in str(e):
            st.warning("⚠ NOT FOUND: MRV ID not registered on blockchain.")
        else:
            st.error(f"Verification failed: {e}")
