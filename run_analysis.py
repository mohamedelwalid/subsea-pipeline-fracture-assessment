"""Run the default calculation and create the CSV file and figure."""

from src.envelope import build_envelope, write_envelope_csv
from src.fracture import calculate_case, default_inputs, pressure_for_utilisation
from src.plotting import plot_envelope


def pass_or_fail(value):
    if value:
        return "PASS"
    return "FAIL"


def main():
    inputs = default_inputs()
    result = calculate_case(inputs)

    print("Subsea pipeline fracture assessment - default case")
    print(f"External pressure:       {result['external_pressure_pa'] / 1e6:8.3f} MPa")
    print(f"Net pressure:            {result['net_pressure_pa'] / 1e6:8.3f} MPa")
    print(f"Hoop stress:             {result['hoop_stress_pa'] / 1e6:8.3f} MPa")
    print(f"K_I:                     {result['stress_intensity'] / 1e6:8.3f} MPa sqrt(m)")
    print(f"K_I / K_IC:              {result['toughness_utilisation']:8.3f}")
    print(f"Plastic zone, strain:    {result['plastic_zone_strain_m'] * 1e3:8.3f} mm")
    print(f"Plastic zone, stress:    {result['plastic_zone_stress_m'] * 1e3:8.3f} mm")
    print("Thin-wall check:        ", pass_or_fail(result["thin_wall_valid"]))
    print("Elastic stress check:   ", pass_or_fail(result["elastic_stress_valid"]))
    print("Plane-strain size check:", pass_or_fail(result["plane_strain_size_valid"]))
    print("SSY screening check:    ", pass_or_fail(result["small_scale_yielding_valid"]))

    print("\nPressure boundaries at the default 20 mm crack depth:")
    for limit in [0.60, 0.80, 1.00]:
        pressure = pressure_for_utilisation(inputs, limit)
        print(f"  K_I / K_IC = {limit:4.2f}: {pressure / 1e6:8.3f} MPa internal pressure")

    crack_depths_mm, pressures_mpa, utilisation = build_envelope(inputs)

    csv_file = "results/operating_envelope.csv"
    image_file = "results/operating_envelope.png"

    write_envelope_csv(crack_depths_mm, pressures_mpa, utilisation, csv_file)
    plot_envelope(
        crack_depths_mm,
        pressures_mpa,
        utilisation,
        inputs,
        image_file,
    )

    print("\nWrote " + csv_file)
    print("Wrote " + image_file)


if __name__ == "__main__":
    main()
