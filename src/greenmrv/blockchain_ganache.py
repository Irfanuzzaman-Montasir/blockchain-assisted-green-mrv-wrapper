from web3 import Web3
from solcx import compile_standard
from pathlib import Path
from typing import Dict, Any

# ---- Ganache configuration ----
GANACHE_RPC = "http://127.0.0.1:7545"
SOLC_VERSION = "0.8.17"


def deploy_or_load_contract() -> Dict[str, Any]:
    """
    Deploy MRVRegistry contract to Ganache.
    In prototype mode, we deploy once per run.
    Returns contract instance + address.
    """
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC))
    assert w3.is_connected(), "Ganache not running"

    account = w3.eth.accounts[0]

    contract_path = Path(__file__).parent / "MRVRegistry.sol"
    source_code = contract_path.read_text()

    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {
                "MRVRegistry.sol": {"content": source_code}
            },
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "evm.bytecode"]}
                }
            },
        },
        solc_version=SOLC_VERSION,
    )

    abi = compiled["contracts"]["MRVRegistry.sol"]["MRVRegistry"]["abi"]
    bytecode = compiled["contracts"]["MRVRegistry.sol"]["MRVRegistry"]["evm"]["bytecode"]["object"]

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx_hash = contract.constructor().transact({
        "from": account,
        "gas": 3_000_000
    })
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "w3": w3,
        "contract": w3.eth.contract(
            address=receipt.contractAddress,
            abi=abi
        ),
        "address": receipt.contractAddress,
        "account": account
    }


def register_mrv_hash(
    *,
    mrv_id: str,
    sha256_hex: str,
    contract_ctx: Dict[str, Any]
) -> str:
    """
    Register MRV hash on-chain.
    Returns transaction hash.
    """
    contract = contract_ctx["contract"]
    account = contract_ctx["account"]

    hash_bytes = bytes.fromhex(sha256_hex)

    tx = contract.functions.registerMRV(
        mrv_id,
        hash_bytes
    ).transact({
        "from": account,
        "gas": 300_000
    })

    receipt = contract_ctx["w3"].eth.wait_for_transaction_receipt(tx)
    return receipt.transactionHash.hex()
