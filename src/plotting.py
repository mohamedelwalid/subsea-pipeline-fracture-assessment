"""Plot the pressure-versus-crack-depth screening map."""

import os

import matplotlib.pyplot as plt


def plot_envelope(
    crack_depths_mm,
    pressures_mpa,
    utilisation,
    base_inputs,
    output_file,
):
    """Create and save the coloured operating-envelope figure."""
    figure, axis = plt.subplots(figsize=(10, 6.2))

    # Green: below 60%, amber: 60-80%, red: above 80% of toughness.
    maximum_value = max(1.5, utilisation.max() + 0.01)
    colour_limits = [0, 0.60, 0.80, maximum_value]
    colours = ["#1f9d73", "#f2b84b", "#d9534f"]

    filled_plot = axis.contourf(
        crack_depths_mm,
        pressures_mpa,
        utilisation,
        levels=colour_limits,
        colors=colours,
    )

    # Add lines where K_I/K_IC is 0.60, 0.80 and 1.00.
    contour_lines = axis.contour(
        crack_depths_mm,
        pressures_mpa,
        utilisation,
        levels=[0.60, 0.80, 1.00],
        colors=["white", "#202735", "#202735"],
        linestyles=["--", "--", "-"],
    )
    axis.clabel(
        contour_lines,
        fmt={0.60: "0.60", 0.80: "0.80", 1.00: "K_I = K_IC"},
    )

    # Mark the original 20 mm crack and 10 MPa internal-pressure case.
    axis.scatter(
        base_inputs["crack_depth_m"] * 1000,
        base_inputs["internal_pressure_pa"] / 1e6,
        marker="*",
        s=170,
        color="white",
        edgecolor="#202735",
        label="Default case",
        zorder=5,
    )

    colourbar = figure.colorbar(filled_plot, ax=axis, ticks=[0.30, 0.70, 1.15])
    colourbar.ax.set_yticklabels(["< 0.60", "0.60-0.80", ">= 0.80"])
    colourbar.set_label("Fracture toughness utilisation, K_I/K_IC")

    axis.set_title("Subsea pipeline fracture screening envelope", loc="left", weight="bold")
    axis.set_xlabel("Crack depth, a [mm]")
    axis.set_ylabel("Internal pressure [MPa]")
    axis.grid(color="white", alpha=0.20)
    axis.legend(loc="upper right")

    figure.text(
        0.12,
        0.01,
        "Educational screening model: constant Y = 1.12; not a fitness-for-service assessment.",
        fontsize=9,
        color="#4b5563",
    )
    figure.tight_layout(rect=[0, 0.04, 1, 1])

    output_folder = os.path.dirname(output_file)
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    figure.savefig(output_file, dpi=180)
    plt.close(figure)
