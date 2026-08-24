"""Parameter sweep and CSV export for the operating envelope."""

import csv
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from .fracture import AssessmentInput, assess_case


@dataclass(frozen=True)
class Envelope:
    crack_depths_mm: np.ndarray
    internal_pressures_mpa: np.ndarray
    utilisation: np.ndarray


def build_envelope(
    base_case: AssessmentInput,
    crack_depths_mm: np.ndarray | None = None,
    internal_pressures_mpa: np.ndarray | None = None,
) -> Envelope:
    if crack_depths_mm is None:
        crack_depths_mm = np.linspace(1.0, 45.0, 177)
    if internal_pressures_mpa is None:
        internal_pressures_mpa = np.linspace(2.0, 25.0, 185)

    utilisation = np.empty((len(internal_pressures_mpa), len(crack_depths_mm)))
    for pressure_index, pressure_mpa in enumerate(internal_pressures_mpa):
        for crack_index, crack_mm in enumerate(crack_depths_mm):
            case = replace(
                base_case,
                internal_pressure_pa=float(pressure_mpa) * 1e6,
                crack_depth_m=float(crack_mm) / 1000.0,
            )
            utilisation[pressure_index, crack_index] = assess_case(case).toughness_utilisation

    return Envelope(
        crack_depths_mm=np.asarray(crack_depths_mm),
        internal_pressures_mpa=np.asarray(internal_pressures_mpa),
        utilisation=utilisation,
    )


def write_envelope_csv(envelope: Envelope, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["crack_depth_mm", "internal_pressure_mpa", "ki_over_kic"])
        for pressure_index, pressure_mpa in enumerate(envelope.internal_pressures_mpa):
            for crack_index, crack_mm in enumerate(envelope.crack_depths_mm):
                writer.writerow(
                    [
                        f"{crack_mm:.3f}",
                        f"{pressure_mpa:.3f}",
                        f"{envelope.utilisation[pressure_index, crack_index]:.6f}",
                    ]
                )

