"""Visualisation of the pressure-versus-crack-depth screening envelope."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

from .envelope import Envelope
from .fracture import AssessmentInput


def plot_operating_envelope(
    envelope: Envelope, base_case: AssessmentInput, output_path: Path
) -> None:
    colours = ["#1f9d73", "#f2b84b", "#d9534f"]
    limits = [0.0, 0.60, 0.80, max(1.50, float(envelope.utilisation.max()) + 0.01)]
    cmap = ListedColormap(colours)
    norm = BoundaryNorm(limits, cmap.N)

    figure, axis = plt.subplots(figsize=(10.0, 6.2), constrained_layout=True)
    field = axis.pcolormesh(
        envelope.crack_depths_mm,
        envelope.internal_pressures_mpa,
        envelope.utilisation,
        cmap=cmap,
        norm=norm,
        shading="auto",
    )
    contours = axis.contour(
        envelope.crack_depths_mm,
        envelope.internal_pressures_mpa,
        envelope.utilisation,
        levels=[0.60, 0.80, 1.00],
        colors=["white", "#202735", "#202735"],
        linewidths=[1.3, 1.6, 1.6],
        linestyles=["--", "--", "-"],
    )
    axis.clabel(
        contours,
        fmt={0.60: "0.60", 0.80: "0.80", 1.00: r"$K_I = K_{IC}$"},
    )
    axis.scatter(
        [base_case.crack_depth_m * 1000.0],
        [base_case.internal_pressure_pa / 1e6],
        marker="*",
        s=170,
        color="white",
        edgecolor="#202735",
        linewidth=1.0,
        label="Default case",
        zorder=5,
    )

    colourbar = figure.colorbar(field, ax=axis, ticks=[0.30, 0.70, 1.15])
    colourbar.ax.set_yticklabels(["< 0.60", "0.60-0.80", ">= 0.80"])
    colourbar.set_label("Fracture toughness utilisation, $K_I/K_{IC}$")

    axis.set_title("Subsea pipeline fracture screening envelope", loc="left", weight="bold")
    axis.set_xlabel("Crack depth, a [mm]")
    axis.set_ylabel("Internal pressure [MPa]")
    axis.grid(color="white", alpha=0.20, linewidth=0.8)
    axis.legend(loc="upper right")
    axis.text(
        0.01,
        -0.16,
        "Educational screening model: constant Y = 1.12; not a fitness-for-service assessment.",
        transform=axis.transAxes,
        fontsize=9,
        color="#4b5563",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
