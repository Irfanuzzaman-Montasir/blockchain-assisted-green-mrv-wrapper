import csv
from typing import Optional, Dict, Any

ENERGY_COL_CANDIDATES = [
    "energy_consumed", "energy_consumed(kwh)", "energy_kwh", "energy"
]
EMISSIONS_COL_CANDIDATES = [
    "emissions", "emissions_kg", "co2_kg", "emissions (kgco2eq)"
]

def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        s = str(x).strip()
        if s == "" or s.lower() in {"nan", "none"}:
            return None
        return float(s)
    except Exception:
        return None

def parse_codecarbon_csv(csv_path: str) -> Dict[str, Optional[float]]:
    """
    Reads last row from CodeCarbon CSV and extracts:
      - energy_kwh
      - co2_kg

    Returns: {"energy_kwh": <float|None>, "co2_kg": <float|None>}
    """
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r]
            if not rows:
                return {"energy_kwh": None, "co2_kg": None}

            last = rows[-1]
            normalized = {k.strip().lower(): v for k, v in last.items() if k}

            energy_kwh = None
            co2_kg = None

            for cand in ENERGY_COL_CANDIDATES:
                key = cand.lower()
                if key in normalized:
                    energy_kwh = _to_float(normalized[key])
                    break

            for cand in EMISSIONS_COL_CANDIDATES:
                key = cand.lower()
                if key in normalized:
                    co2_kg = _to_float(normalized[key])
                    break

            return {"energy_kwh": energy_kwh, "co2_kg": co2_kg}

    except FileNotFoundError:
        return {"energy_kwh": None, "co2_kg": None}
    except Exception:
        return {"energy_kwh": None, "co2_kg": None}
