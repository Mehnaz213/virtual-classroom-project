"""
Augmentation utilities for Focus Mate datasets.
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Iterable

import cv2
import numpy as np


def augment_image(image: np.ndarray) -> Iterable[np.ndarray]:
    yield image
    yield cv2.flip(image, 1)
    yield cv2.GaussianBlur(image, (5, 5), 0)
    yield cv2.convertScaleAbs(image, alpha=1.05, beta=10)
    rows, cols, _ = image.shape
    m = np.float32([[1, 0, 5], [0, 1, 5]])
    yield cv2.warpAffine(image, m, (cols, rows))


def process_folder(source: pathlib.Path, target: pathlib.Path) -> None:
    for path in source.glob("*.jpg"):
        image = cv2.imread(str(path))
        for idx, aug in enumerate(augment_image(image)):
            out = target / f"{path.stem}_aug{idx}.jpg"
            cv2.imwrite(str(out), aug)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply synthetic augmentations.")
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--target", type=pathlib.Path, required=True)
    args = parser.parse_args()

    args.target.mkdir(parents=True, exist_ok=True)
    process_folder(args.source, args.target)
    print("Augmentation complete.")


if __name__ == "__main__":
    main()


