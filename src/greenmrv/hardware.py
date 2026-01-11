from typing import Any, Dict
import psutil
import cpuinfo

def detect_hardware(region: str = "local_grid") -> Dict[str, Any]:
    cpu = cpuinfo.get_cpu_info()
    cpu_name = cpu.get("brand_raw") or cpu.get("brand") or "unknown"

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))

    gpu_type = "unknown"
    num_gpus = 0

    # Best-effort: NVIDIA detection if pynvml is installed
    try:
        import pynvml  # optional
        pynvml.nvmlInit()
        num_gpus = pynvml.nvmlDeviceGetCount()
        if num_gpus > 0:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_type = pynvml.nvmlDeviceGetName(handle).decode("utf-8", errors="ignore")
        pynvml.nvmlShutdown()
    except Exception:
        pass

    return {
        "gpu_type": gpu_type,
        "num_gpus": int(num_gpus),
        "cpu_type": cpu_name,
        "ram_gb": int(ram_gb),
        "region": region
    }
