"""
Select low-confidence samples for manual labeling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract low-confidence frames for review.")
    parser.add_argument("--events", type=Path, required=True, help="JSONL of engagement events")
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--out", type=Path, required=True, help="Output queue JSONL")
    args = parser.parse_args()

    queued = 0
    with args.events.open("r", encoding="utf-8") as src, args.out.open("w", encoding="utf-8") as dst:
        for line in src:
            event = json.loads(line)
            labels = event.get("labels", [])
            top = max(labels, key=lambda x: x.get("confidence", 0.0), default=None)
            if not top or top.get("confidence", 0.0) > args.threshold:
                continue
            dst.write(json.dumps(event) + "\n")
            queued += 1
    print(f"[active_learning] queued {queued} samples below confidence {args.threshold}")


if __name__ == "__main__":
    main()

"""
Select low-confidence samples for manual review.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter low-confidence live events for labeling.")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--output", type=Path, default=Path("review_queue.jsonl"))
    args = parser.parse_args()

    selected = 0
    with args.events.open() as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            event = json.loads(line)
            labels = event.get("labels", [])
            top = labels[0] if labels else {"confidence": 1.0}
            if top["confidence"] <= args.threshold:
                dst.write(line)
                selected += 1
    print(f"Queued {selected} samples for review -> {args.output}")


if __name__ == "__main__":
    main()


