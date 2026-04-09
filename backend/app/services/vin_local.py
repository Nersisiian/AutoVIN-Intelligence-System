from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


_WMI_COUNTRY_PREFIX = {
    "1": "United States",
    "4": "United States",
    "5": "United States",
    "2": "Canada",
    "3": "Mexico",
    "J": "Japan",
    "K": "South Korea",
    "L": "China",
    "S": "United Kingdom",
    "V": "France / Spain",
    "W": "Germany",
    "Y": "Sweden / Finland",
    "Z": "Italy",
    "T": "Switzerland",
    "M": "India / Thailand",
}

# Very common WMIs; this is intentionally small but useful.
_WMI_MAKE = {
    "1HG": "Honda",
    "1FA": "Ford",
    "1F": "Ford",
    "1C4": "Jeep",
    "1G1": "Chevrolet",
    "1G": "General Motors",
    "1N4": "Nissan",
    "1N": "Nissan",
    "2HG": "Honda",
    "2T3": "Toyota",
    "3FA": "Ford",
    "3VW": "Volkswagen",
    "JHM": "Honda",
    "JTD": "Toyota",
    "JT": "Toyota",
    "KMH": "Hyundai",
    "KNA": "Kia",
    "SAL": "Land Rover",
    "SHH": "Honda",
    "WAU": "Audi",
    "WBA": "BMW",
    "WDB": "Mercedes-Benz",
    "WVW": "Volkswagen",
    "YV1": "Volvo",
}

# VIN year code mapping for 1980-2039 cycles (A=1980, ... Y=2000, 1=2001 ... 9=2009, A=2010 ...)
_YEAR_CODES = "ABCDEFGHJKLMNPRSTVWXY123456789"


def _decode_year(year_code: str) -> Optional[int]:
    year_code = year_code.upper()
    if year_code not in _YEAR_CODES:
        return None
    idx = _YEAR_CODES.index(year_code)
    # Two cycles: 1980-2009 (30 years) and 2010-2039. Choose the newer plausible cycle.
    year_1980 = 1980 + idx
    year_2010 = 2010 + idx
    # Pick the most plausible year relative to "now".
    # VIN year repeats every 30 years; choose the candidate closest to current year,
    # but never more than 1 year in the future (new model-year rollover tolerance).
    now_year = datetime.now(tz=timezone.utc).year
    candidates = [year_1980, year_2010]
    candidates = [y for y in candidates if y <= now_year + 1]
    if not candidates:
        # If both are in the future (rare), fall back to the older cycle.
        return year_1980
    return max(candidates)


@dataclass(frozen=True)
class LocalVinDecode:
    vin: str
    wmi: str
    vds: str
    vis: str
    make: Optional[str]
    year: Optional[int]
    country_of_origin: Optional[str]


def decode_vin_locally(vin: str) -> LocalVinDecode:
    wmi = vin[0:3]
    vds = vin[3:9]
    vis = vin[9:17]
    year_code = vin[9]

    country = _WMI_COUNTRY_PREFIX.get(vin[0], None)
    make = _WMI_MAKE.get(wmi) or _WMI_MAKE.get(wmi[0:2])  # fallback for broad WMIs
    year = _decode_year(year_code)

    return LocalVinDecode(
        vin=vin,
        wmi=wmi,
        vds=vds,
        vis=vis,
        make=make,
        year=year,
        country_of_origin=country,
    )
