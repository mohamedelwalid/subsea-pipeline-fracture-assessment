import math
import unittest
from dataclasses import replace

from src.fracture import (
    AssessmentInput,
    assess_case,
    astm_plane_strain_min_size,
    hydrostatic_pressure,
    internal_pressure_for_utilisation,
)


class FractureAssessmentTests(unittest.TestCase):
    def test_default_external_pressure(self) -> None:
        self.assertAlmostEqual(hydrostatic_pressure(1000.0, 9.81, 200.0), 1.962e6)

    def test_default_case_matches_hand_calculation(self) -> None:
        result = assess_case(AssessmentInput())
        self.assertAlmostEqual(result.hoop_stress_pa / 1e6, 84.399, places=3)
        self.assertAlmostEqual(result.stress_intensity / 1e6, 23.69, places=2)
        self.assertAlmostEqual(result.toughness_utilisation, 23.69 / 50.0, places=3)

    def test_original_plane_strain_size_check_fails_due_to_crack_depth(self) -> None:
        case = AssessmentInput()
        result = assess_case(case)
        self.assertAlmostEqual(result.plane_strain_min_size_m * 1000.0, 30.864, places=3)
        self.assertFalse(result.plane_strain_size_valid)

    def test_stress_intensity_scales_with_square_root_of_crack_depth(self) -> None:
        base = AssessmentInput(crack_depth_m=0.010)
        doubled = replace(base, crack_depth_m=0.020)
        ratio = assess_case(doubled).stress_intensity / assess_case(base).stress_intensity
        self.assertAlmostEqual(ratio, math.sqrt(2.0), places=12)

    def test_external_pressure_above_internal_gives_no_mode_i_opening(self) -> None:
        case = AssessmentInput(internal_pressure_pa=1.0e6)
        result = assess_case(case)
        self.assertLess(result.net_pressure_pa, 0.0)
        self.assertEqual(result.hoop_stress_pa, 0.0)
        self.assertEqual(result.stress_intensity, 0.0)

    def test_invalid_crack_depth_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AssessmentInput(crack_depth_m=0.050)

    def test_astm_minimum_size(self) -> None:
        minimum = astm_plane_strain_min_size(50.0e6, 450.0e6)
        self.assertAlmostEqual(minimum, 0.0308641975308642)

    def test_pressure_boundary_reproduces_target_utilisation(self) -> None:
        base = AssessmentInput()
        pressure = internal_pressure_for_utilisation(base, 0.80)
        boundary_case = replace(base, internal_pressure_pa=pressure)
        self.assertAlmostEqual(assess_case(boundary_case).toughness_utilisation, 0.80)

    def test_non_positive_target_utilisation_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            internal_pressure_for_utilisation(AssessmentInput(), 0.0)


if __name__ == "__main__":
    unittest.main()
