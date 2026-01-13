"""
Focus Mate dataset ingestion helper.

Usage examples:
    # List available datasets
    python scripts/data_ingest.py list

    # Generate synthetic demo dataset
    python scripts/data_ingest.py ingest synthetic_demo --limit 128

    # Convert local calibration captures
    python scripts/data_ingest.py ingest local_calibration --raw data/raw/local_calibration
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from typing import Optional

from datasets.adapters import ADAPTERS
from datasets.specs import DATASETS, DatasetSpec, get_spec

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"


def list_datasets() -> None:
    rows = []
    for spec in DATASETS.values():
        rows.append(
            {
                "slug": spec.slug,
                "name": spec.name,
                "license": spec.license,
                "homepage": spec.homepage,
                "requires_request": spec.requires_request,
                "notes": spec.notes,
            }
        )
    print(json.dumps(rows, indent=2))


def ingest_dataset(spec: DatasetSpec, raw_dir: Path, out_dir: Path, limit: Optional[int]) -> None:
    adapter = ADAPTERS.get(spec.adapter)
    if adapter is None:
        raise KeyError(f"No adapter registered for {spec.adapter}")

    if spec.requires_request and spec.download_url is None:
        print(
            textwrap.dedent(
                f"""
                Dataset '{spec.name}' requires manual access approval.
                Visit {spec.homepage} to request credentials, then place the
                extracted archive under {raw_dir}. Afterwards, re-run this command.
                """
            ).strip()
        )
        return

    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    adapter(spec, raw_dir, out_dir, limit)


def main():
    parser = argparse.ArgumentParser(description="Focus Mate dataset ingestion")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List dataset catalog")
    list_parser.set_defaults(func=lambda args: list_datasets())

    ingest_parser = sub.add_parser("ingest", help="Ingest a dataset into the unified schema")
    ingest_parser.add_argument("dataset", help="Dataset slug (see `list`)")
    ingest_parser.add_argument("--limit", type=int, default=None, help="Optional max samples")
    ingest_parser.add_argument(
        "--raw",
        type=Path,
        default=None,
        help=f"Directory containing raw files (default: data/raw/<dataset>)",
    )
    ingest_parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"Processed output directory (default: data/processed/<dataset>)",
    )

    def ingest_cmd(args):
        spec = get_spec(args.dataset)
        raw_dir = args.raw or RAW_DIR / spec.slug
        out_dir = args.out or PROCESSED_DIR / spec.slug
        ingest_dataset(spec, raw_dir, out_dir, args.limit)

    ingest_parser.set_defaults(func=ingest_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


