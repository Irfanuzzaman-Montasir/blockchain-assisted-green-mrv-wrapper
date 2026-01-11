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

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def default_out_dir() -> str:
    # Works on local/VSCode and Colab (writes inside current working directory)
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
    # user can provide these, but they are optional
    experiment_name: str = "experiment_run",
    model_name: str = "unknown",
    dataset_name: str = "unknown",

    # framework/framework_version become automatic if not provided
    framework: Optional[str] = None,
    framework_version: Optional[str] = None,

    # training params optional
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,

    region: str = "local_grid",
    out_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Usage:
        from greenmrv import mrv_run
        with mrv_run(experiment_name="...", model_name="...", dataset_name="..."):
            train()
    After exiting, MRV JSON is written to mrv_records/<mrv_id>.json
    """
    try:
        from codecarbon import EmissionsTracker
    except Exception:
        raise RuntimeError("codecarbon not installed. Run: pip install codecarbon")

    # Auto-detect framework/version if user didn't provide
    if framework is None or framework.strip() == "" or framework.lower() == "auto":
        fw = detect_framework()
        framework = fw.name
        framework_version = framework_version or fw.version
    else:
        # If user gave framework but no version, attempt to find its version
        if framework_version is None:
            name = framework.lower()
            if name in {"pytorch", "torch"}:
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

    mrv_id = f"MRV-{uuid.uuid4()}"
    out_dir = out_dir or default_out_dir()
    ensure_dir(out_dir)

    hardware = detect_hardware(region=region)

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
        co2_kg = None
        try:
            co2_kg = tracker.stop()  # often returns emissions in kg
        except Exception:
            co2_kg = None

        duration_seconds = int(round(time.time() - t0))
        end_time = utc_now_iso()

        # Parse CSV to get energy_kwh and (fallback) emissions
        parsed = parse_codecarbon_csv(codecarbon_csv)
        energy_kwh = parsed["energy_kwh"]

        if co2_kg is None and parsed["co2_kg"] is not None:
            co2_kg = parsed["co2_kg"]

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

        json_path = os.path.join(out_dir, f"{mrv_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(mrv_json, f, indent=2, ensure_ascii=False)

        info["json_path"] = json_path
        info["mrv_json"] = mrv_json

        # Make it user-friendly: print automatically
        print(f"[greenmrv] MRV ID: {mrv_id}")
        print(f"[greenmrv] MRV JSON saved: {json_path}")
        print(f"[greenmrv] CodeCarbon CSV: {codecarbon_csv}")
