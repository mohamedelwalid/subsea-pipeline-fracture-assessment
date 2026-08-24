"""Run the default fracture-assessment case and generate project outputs."""

from pathlib import Path

from src.fracture import AssessmentInput, assess_case, internal_pressure_for_utilisation
from src.envelope import build_envelope, write_envelope_csv
from src.plotting import plot_operating_envelope


def main() -> None:
    case = AssessmentInput()
    result = assess_case(case)

    print("Subsea pipeline fracture assessment - default case")
    print(f"External pressure:       {result.external_pressure_pa / 1e6:8.3f} MPa")
    print(f"Net pressure:            {result.net_pressure_pa / 1e6:8.3f} MPa")
    print(f"Hoop stress:             {result.hoop_stress_pa / 1e6:8.3f} MPa")
    print(f"K_I:                     {result.stress_intensity / 1e6:8.3f} MPa sqrt(m)")
    print(f"K_I / K_IC:              {result.toughness_utilisation:8.3f}")
    print(f"Plastic zone, strain:    {result.plastic_zone_strain_m * 1e3:8.3f} mm")
    print(f"Plastic zone, stress:    {result.plastic_zone_stress_m * 1e3:8.3f} mm")
    print(f"Thin-wall check:         {'PASS' if result.thin_wall_valid else 'FAIL'}")
    print(f"Elastic stress check:    {'PASS' if result.elastic_stress_valid else 'FAIL'}")
    print(f"Plane-strain size check: {'PASS' if result.plane_strain_size_valid else 'FAIL'}")
    print(f"SSY screening check:     {'PASS' if result.small_scale_yielding_valid else 'FAIL'}")
    print("\nPressure boundaries at the default 20 mm crack depth:")
    for limit in (0.60, 0.80, 1.00):
        pressure = internal_pressure_for_utilisation(case, limit)
        print(f"  K_I / K_IC = {limit:4.2f}: {pressure / 1e6:8.3f} MPa internal pressure")

    envelope = build_envelope(case)
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    write_envelope_csv(envelope, output_dir / "operating_envelope.csv")
    plot_operating_envelope(envelope, case, output_dir / "operating_envelope.png")
    print(f"\nWrote {output_dir / 'operating_envelope.csv'}")
    print(f"Wrote {output_dir / 'operating_envelope.png'}")


if __name__ == "__main__":
    main()
