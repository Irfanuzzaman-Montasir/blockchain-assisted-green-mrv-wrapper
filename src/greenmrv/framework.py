from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import importlib.util

def _pkg_installed(pkg: str) -> bool:
    return importlib.util.find_spec(pkg) is not None

def _pkg_version(dist_name: str) -> Optional[str]:
    try:
        import importlib.metadata as md
        return md.version(dist_name)
    except Exception:
        return None

@dataclass(frozen=True)
class FrameworkInfo:
    name: str
    version: str

def detect_framework() -> FrameworkInfo:
    """
    Detect common ML frameworks based on installed packages.
    Priority: PyTorch -> TensorFlow -> JAX -> unknown
    """
    if _pkg_installed("torch"):
        return FrameworkInfo("PyTorch", _pkg_version("torch") or "unknown")

    if _pkg_installed("tensorflow"):
        return FrameworkInfo("TensorFlow", _pkg_version("tensorflow") or "unknown")

    if _pkg_installed("jax"):
        return FrameworkInfo("JAX", _pkg_version("jax") or "unknown")

    return FrameworkInfo("unknown", "unknown")
