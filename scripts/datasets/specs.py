"""
Dataset catalog for Focus Mate gaze/attention training.

Each dataset entry enumerates licensing, recommended download source,
and internal adapter used to convert raw data into the unified schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    slug: str
    homepage: str
    license: str
    download_url: Optional[str]
    requires_request: bool
    adapter: str
    notes: str = ""


DATASETS: Dict[str, DatasetSpec] = {
    "gazecapture": DatasetSpec(
        name="GazeCapture",
        slug="gazecapture",
        homepage="https://gazecapture.csail.mit.edu/",
        license="Research-only, registration required",
        download_url=None,
        requires_request=True,
        adapter="gazecapture",
        notes="Largest mobile gaze dataset; request access via MIT form.",
    ),
    "mpiigaze": DatasetSpec(
        name="MPIIGaze",
        slug="mpiigaze",
        homepage="https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-estimation/mpiigaze",
        license="Non-commercial, request required",
        download_url=None,
        requires_request=True,
        adapter="mpiigaze",
        notes="High-resolution laptop gaze dataset; download after signing EULA.",
    ),
    "columbia": DatasetSpec(
        name="Columbia Gaze",
        slug="columbia",
        homepage="http://www.cs.columbia.edu/CAVE/databases/columbia_gaze/",
        license="Non-commercial",
        download_url="http://www.cs.columbia.edu/CAVE/databases/columbia_gaze/ColumbiaGazeDataSet.zip",
        requires_request=False,
        adapter="columbia",
        notes="Contains labeled eye contact directions; direct download available.",
    ),
    "ethxgaze": DatasetSpec(
        name="ETH-XGaze",
        slug="ethxgaze",
        homepage="https://ait.ethz.ch/projects/2020/xgaze/",
        license="Research, request required",
        download_url=None,
        requires_request=True,
        adapter="ethxgaze",
        notes="Large-scale multi-view dataset.",
    ),
    "openeds": DatasetSpec(
        name="OpenEDS",
        slug="openeds",
        homepage="https://research.fb.com/openeds-2020-challenge/",
        license="CC BY-NC 4.0 (registration)",
        download_url=None,
        requires_request=True,
        adapter="openeds",
        notes="Eye segmentation dataset; useful for eye-openness estimation.",
    ),
    "local_calibration": DatasetSpec(
        name="Local Calibration Captures",
        slug="local_calibration",
        homepage="local",
        license="User-provided",
        download_url=None,
        requires_request=False,
        adapter="local_calibration",
        notes="Frames captured via scripts/local_capture.",
    ),
    "synthetic_demo": DatasetSpec(
        name="Synthetic Demo",
        slug="synthetic_demo",
        homepage="generated",
        license="Apache-2.0",
        download_url=None,
        requires_request=False,
        adapter="synthetic_demo",
        notes="Procedurally generated samples for CI/dev validation.",
    ),
}


def get_spec(slug_or_name: str) -> DatasetSpec:
    key = slug_or_name.lower()
    if key in DATASETS:
        return DATASETS[key]
    for spec in DATASETS.values():
        if spec.name.lower() == key:
            return spec
    raise KeyError(f"Unknown dataset '{slug_or_name}'. Known: {list(DATASETS)}")


AdapterFn = Callable[[DatasetSpec, Path, Path, Optional[int]], None]


