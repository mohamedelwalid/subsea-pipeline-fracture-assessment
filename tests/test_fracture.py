import math
import unittest

from src.fracture import (
    calculate_case,
    default_inputs,
    hydrostatic_pressure,
    minimum_plane_strain_size,
    pressure_for_utilisation,
)


class FractureAssessmentTests(unittest.TestCase):
    def test_default_external_pressure(self):
        self.assertAlmostEqual(hydrostatic_pressure(1000, 9.81, 200), 1.962e6)

    def test_default_case_matches_hand_calculation(self):
        result = calculate_case(default_inputs())
        self.assertAlmostEqual(result["hoop_stress_pa"] / 1e6, 84.399, places=3)
        self.assertAlmostEqual(result["stress_intensity"] / 1e6, 23.69, places=2)
        self.assertAlmostEqual(result["toughness_utilisation"], 23.69 / 50, places=3)

    def test_plane_strain_size_check_fails_for_default_crack(self):
        result = calculate_case(default_inputs())
        self.assertAlmostEqual(result["plane_strain_min_size_m"] * 1000, 30.864, places=3)
        self.assertFalse(result["plane_strain_size_valid"])

    def test_stress_intensity_scales_with_square_root_of_crack_depth(self):
        first_case = default_inputs()
        first_case["crack_depth_m"] = 0.010

        second_case = default_inputs()
        second_case["crack_depth_m"] = 0.020

        first_result = calculate_case(first_case)
        second_result = calculate_case(second_case)
        ratio = second_result["stress_intensity"] / first_result["stress_intensity"]
        self.assertAlmostEqual(ratio, math.sqrt(2), places=12)

    def test_external_pressure_above_internal_gives_no_crack_opening(self):
        inputs = default_inputs()
        inputs["internal_pressure_pa"] = 1.0e6
        result = calculate_case(inputs)
        self.assertLess(result["net_pressure_pa"], 0)
        self.assertEqual(result["hoop_stress_pa"], 0)
        self.assertEqual(result["stress_intensity"], 0)

    def test_invalid_crack_depth_is_rejected(self):
        inputs = default_inputs()
        inputs["crack_depth_m"] = 0.050
        with self.assertRaises(ValueError):
            calculate_case(inputs)

    def test_minimum_plane_strain_size(self):
        minimum = minimum_plane_strain_size(50.0e6, 450.0e6)
        self.assertAlmostEqual(minimum, 0.0308641975308642)

    def test_pressure_boundary_reproduces_target_utilisation(self):
        inputs = default_inputs()
        pressure = pressure_for_utilisation(inputs, 0.80)
        inputs["internal_pressure_pa"] = pressure
        result = calculate_case(inputs)
        self.assertAlmostEqual(result["toughness_utilisation"], 0.80)

    def test_non_positive_target_utilisation_is_rejected(self):
        with self.assertRaises(ValueError):
            pressure_for_utilisation(default_inputs(), 0)


if __name__ == "__main__":
    unittest.main()
