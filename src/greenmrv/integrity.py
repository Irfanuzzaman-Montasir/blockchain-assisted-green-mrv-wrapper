import json
import hashlib
from typing import Any, Dict

INTEGRITY_FIELD_NAME = "integrity"


def canonicalize_mrv_json(mrv_json: Dict[str, Any]) -> bytes:
    """
    Canonicalize MRV JSON for deterministic hashing.

    Rules:
    - Remove the 'integrity' field entirely
    - Sort all keys recursively
    - Remove whitespace
    - UTF-8 encoding

    Returns:
        bytes: canonical byte representation
    """
    # Defensive shallow copy
    data = dict(mrv_json)

    # Remove integrity section if present
    data.pop(INTEGRITY_FIELD_NAME, None)

    canonical_str = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return canonical_str.encode("utf-8")


def compute_mrv_sha256(mrv_json: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of canonical MRV JSON.

    Returns:
        str: lowercase hex digest
    """
    canonical_bytes = canonicalize_mrv_json(mrv_json)
    return hashlib.sha256(canonical_bytes).hexdigest()
