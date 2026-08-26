"""Calculate a pressure-versus-crack-depth screening map."""

import csv
import os

import numpy as np

from .fracture import calculate_case


def build_envelope(base_inputs, crack_depths_mm=None, pressures_mpa=None):
    """Run the same calculation for many crack depths and pressures."""
    if crack_depths_mm is None:
        crack_depths_mm = np.linspace(1, 45, 177)

    if pressures_mpa is None:
        pressures_mpa = np.linspace(2, 25, 185)

    utilisation = np.zeros((len(pressures_mpa), len(crack_depths_mm)))

    for pressure_index in range(len(pressures_mpa)):
        for crack_index in range(len(crack_depths_mm)):
            # Copy the dictionary so the original input values are not changed.
            current_inputs = base_inputs.copy()
            current_inputs["internal_pressure_pa"] = pressures_mpa[pressure_index] * 1e6
            current_inputs["crack_depth_m"] = crack_depths_mm[crack_index] / 1000

            result = calculate_case(current_inputs)
            utilisation[pressure_index, crack_index] = result[
                "toughness_utilisation"
            ]

    return crack_depths_mm, pressures_mpa, utilisation


def write_envelope_csv(crack_depths_mm, pressures_mpa, utilisation, output_file):
    """Save every calculated combination to a CSV file."""
    output_folder = os.path.dirname(output_file)
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["crack_depth_mm", "internal_pressure_mpa", "ki_over_kic"])

        for pressure_index in range(len(pressures_mpa)):
            for crack_index in range(len(crack_depths_mm)):
                writer.writerow(
                    [
                        round(crack_depths_mm[crack_index], 3),
                        round(pressures_mpa[pressure_index], 3),
                        round(utilisation[pressure_index, crack_index], 6),
                    ]
                )
