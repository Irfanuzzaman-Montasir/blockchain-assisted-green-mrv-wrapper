from typing import Any, Dict, Optional

def build_mrv_json(
    *,
    mrv_id: str,
    experiment_name: str,
    model_name: str,
    dataset_name: str,
    framework: str,
    framework_version: str,
    epochs: Optional[int],
    batch_size: Optional[int],
    hardware: Dict[str, Any],
    measurement_tool: str,
    tool_version: str,
    energy_kwh: Optional[float],
    co2_kg: Optional[float],
    duration_seconds: int,
    start_time: str,
    end_time: str
) -> Dict[str, Any]:
    return {
        "schema_version": "0.1",
        "mrv_id": mrv_id,

        "experiment": {
            "experiment_name": experiment_name,
            "model_name": model_name,
            "dataset_name": dataset_name
        },

        "training": {
            "framework": framework,
            "framework_version": framework_version,
            "epochs": epochs,
            "batch_size": batch_size
        },

        "hardware": hardware,

        "energy_emissions": {
            "measurement_tool": measurement_tool,
            "tool_version": tool_version,
            "energy_kwh": energy_kwh,
            "co2_kg": co2_kg,
            "duration_seconds": duration_seconds
        },

        "timestamps": {
            "start_time": start_time,
            "end_time": end_time
        },

        # for 2nd update , blockchain info etc.
        "integrity": {
            "hash_alg": "sha256",
            "json_canonicalization": "sort_keys=true, separators=(',',':')",
            "json_sha256": "not_computed_yet",
            "blockchain_network": "not_registered",
            "contract_address": "not_registered",
            "tx_hash": "not_registered"
        }
    }
