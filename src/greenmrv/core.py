import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .hardware import detect_hardware
from .schema import build_mrv_json
from .framework import detect_framework
from .codecarbon_csv import parse_codecarbon_csv
from .integrity import compute_mrv_sha256
from .blockchain_ganache import deploy_or_load_contract, register_mrv_hash


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def default_out_dir() -> str:
    return os.path.join(os.getcwd(), "mrv_records")


def get_pkg_version(pkg_name: str) -> str:
    try:
        import importlib.metadata as md
        return md.version(pkg_name)
    except Exception:
        return "unknown"


@contextmanager
def mrv_run(
    *,
    experiment_name: str = "experiment_run",
    model_name: str = "unknown",
    dataset_name: str = "unknown",
    framework: Optional[str] = None,
    framework_version: Optional[str] = None,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    region: str = "local_grid",
    out_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Usage:
        from greenmrv import mrv_run

        with mrv_run(
            experiment_name="resnet18_cifar10",
            model_name="ResNet18",
            dataset_name="CIFAR-10",
            epochs=90,
            batch_size=128
        ):
            train()

    Full pipeline:
    - Measure emissions
    - Build MRV JSON
    - Canonical SHA-256 hash
    - Register hash on Ganache
    - Save final JSON with blockchain proof
    """

    try:
        from codecarbon import EmissionsTracker
    except Exception:
        raise RuntimeError("codecarbon not installed. Run: pip install codecarbon")

    # -------------------------------
    # Framework auto-detection
    # -------------------------------
    if framework is None or framework.strip() == "" or framework.lower() == "auto":
        fw = detect_framework()
        framework = fw.name
        framework_version = fw.version
    elif framework_version is None:
        name = framework.lower()
        if name in {"torch", "pytorch"}:
            framework = "PyTorch"
            framework_version = get_pkg_version("torch")
        elif name in {"tensorflow", "tf"}:
            framework = "TensorFlow"
            framework_version = get_pkg_version("tensorflow")
        elif name == "jax":
            framework = "JAX"
            framework_version = get_pkg_version("jax")
        else:
            framework_version = "unknown"

    # -------------------------------
    # Identifiers & directories
    # -------------------------------
    mrv_id = f"MRV-{uuid.uuid4()}"
    out_dir = out_dir or default_out_dir()
    ensure_dir(out_dir)

    hardware = detect_hardware(region=region)

    # -------------------------------
    # Blockchain init (ONCE per run)
    # -------------------------------
    blockchain_ctx = deploy_or_load_contract()

    start_time = utc_now_iso()
    t0 = time.time()

    codecarbon_csv = os.path.join(out_dir, f"{mrv_id}_codecarbon.csv")

    tracker = EmissionsTracker(
        project_name=experiment_name,
        output_dir=out_dir,
        output_file=f"{mrv_id}_codecarbon.csv",
        log_level="error"
    )

    tracker.start()

    info: Dict[str, Any] = {
        "mrv_id": mrv_id,
        "json_path": None,
        "mrv_json": None,
        "codecarbon_csv": codecarbon_csv
    }

    try:
        yield info

    finally:
        # -------------------------------
        # Stop measurement
        # -------------------------------
        try:
            co2_kg = tracker.stop()
        except Exception:
            co2_kg = None

        duration_seconds = int(round(time.time() - t0))
        end_time = utc_now_iso()

        # -------------------------------
        # Parse CodeCarbon output
        # -------------------------------
        parsed = parse_codecarbon_csv(codecarbon_csv)
        energy_kwh = parsed["energy_kwh"]

        if co2_kg is None and parsed["co2_kg"] is not None:
            co2_kg = parsed["co2_kg"]

        # -------------------------------
        # Build MRV JSON (pre-blockchain)
        # -------------------------------
        mrv_json = build_mrv_json(
            mrv_id=mrv_id,
            experiment_name=experiment_name,
            model_name=model_name,
            dataset_name=dataset_name,
            framework=framework,
            framework_version=framework_version or "unknown",
            epochs=epochs,
            batch_size=batch_size,
            hardware=hardware,
            measurement_tool="CodeCarbon",
            tool_version=get_pkg_version("codecarbon"),
            energy_kwh=energy_kwh,
            co2_kg=float(co2_kg) if co2_kg is not None else None,
            duration_seconds=duration_seconds,
            start_time=start_time,
            end_time=end_time
        )

        # -------------------------------
        # Canonical hash
        # -------------------------------
        mrv_hash = compute_mrv_sha256(mrv_json)
        mrv_json["integrity"]["json_sha256"] = mrv_hash

        # -------------------------------
        # Register hash on Ganache
        # -------------------------------
        tx_hash = register_mrv_hash(
            mrv_id=mrv_id,
            sha256_hex=mrv_hash,
            contract_ctx=blockchain_ctx
        )

        mrv_json["integrity"].update({
            "blockchain_network": "ganache-local",
            "contract_address": blockchain_ctx["address"],
            "tx_hash": tx_hash
        })

        # -------------------------------
        # Save FINAL MRV JSON
        # -------------------------------
        json_path = os.path.join(out_dir, f"{mrv_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(mrv_json, f, indent=2, ensure_ascii=False)

        info["json_path"] = json_path
        info["mrv_json"] = mrv_json

        # -------------------------------
        # Logs
        # -------------------------------
        print(f"[greenmrv] MRV ID: {mrv_id}")
        print(f"[greenmrv] SHA-256: {mrv_hash}")
        print(f"[greenmrv] Blockchain TX: {tx_hash}")
        print(f"[greenmrv] Contract: {blockchain_ctx['address']}")
        print(f"[greenmrv] MRV JSON saved: {json_path}")
        print(f"[greenmrv] CodeCarbon CSV: {codecarbon_csv}")
