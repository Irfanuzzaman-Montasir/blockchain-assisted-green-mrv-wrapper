from solcx import compile_standard
from web3 import Web3
import json
from pathlib import Path

# -----------------------------
# Connect to Ganache
# -----------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.is_connected(), "Ganache not running"

account = w3.eth.accounts[0]
print("Using account:", account)

# -----------------------------
# Load Solidity contract
# -----------------------------
contract_path = Path("MRVRegistry.sol")
source_code = contract_path.read_text()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "MRVRegistry.sol": {"content": source_code}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        },
    },
    solc_version="0.8.17",
)

abi = compiled["contracts"]["MRVRegistry.sol"]["MRVRegistry"]["abi"]
bytecode = compiled["contracts"]["MRVRegistry.sol"]["MRVRegistry"]["evm"]["bytecode"]["object"]

# -----------------------------
# Deploy contract
# -----------------------------
MRVRegistry = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = MRVRegistry.constructor().transact({
    "from": account,
    "gas": 3_000_000
})


tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print("MRVRegistry deployed at:", contract_address)

# -----------------------------
# Register a real MRV hash
# -----------------------------
registry = w3.eth.contract(address=contract_address, abi=abi)

mrv_id = "MRV-DEMO-001"

# Example: SHA-256 hex (64 chars)
example_hash_hex = "a" * 64
example_hash_bytes = bytes.fromhex(example_hash_hex)

tx = registry.functions.registerMRV(
    mrv_id,
    example_hash_bytes
).transact({
    "from": account,
    "gas": 300_000
})


w3.eth.wait_for_transaction_receipt(tx)

print("MRV registered on-chain:")
print("  MRV ID:", mrv_id)
print("  Hash :", example_hash_hex)
