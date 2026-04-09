from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any

import httpx


async def _decode(vin: str, api_base_url: str) -> dict[str, Any]:
    url = api_base_url.rstrip("/") + "/decode-vin"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json={"vin": vin})
        resp.raise_for_status()
        return resp.json()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vin-decoder", description="Decode a VIN via AutoVIN API.")
    parser.add_argument("vin", help="17-character VIN")
    parser.add_argument(
        "--api",
        dest="api",
        default=os.environ.get("AUTOVIN_API_URL", "http://localhost:8000"),
        help="API base URL (default: %(default)s or AUTOVIN_API_URL)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args(argv)

    try:
        data = asyncio.run(_decode(args.vin, args.api))
        if args.pretty:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
        return 0
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} {e.response.text}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

