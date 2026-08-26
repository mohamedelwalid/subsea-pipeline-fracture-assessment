"""Simple analytical fracture-mechanics calculations.

The calculations use SI units internally:
- pressure and stress in Pa
- lengths in m
- stress intensity in Pa*sqrt(m)
"""

from math import pi, sqrt


def default_inputs():
    """Return the input values used in the original course exercise."""
    return {
        "internal_pressure_pa": 10.0e6,
        "water_depth_m": 200.0,
        "seawater_density_kg_m3": 1000.0,
        "gravity_m_s2": 9.81,
        "inner_radius_m": 0.50,
        "wall_thickness_m": 0.050,
        "crack_depth_m": 0.020,
        "youngs_modulus_pa": 210.0e9,
        "poisson_ratio": 0.30,
        "yield_strength_pa": 450.0e6,
        "fracture_toughness": 50.0e6,
        "geometry_factor": 1.12,
    }


def check_inputs(inputs):
    """Stop the calculation if the main dimensions or material values are invalid."""
    positive_values = [
        "internal_pressure_pa",
        "water_depth_m",
        "seawater_density_kg_m3",
        "gravity_m_s2",
        "inner_radius_m",
        "wall_thickness_m",
        "crack_depth_m",
        "youngs_modulus_pa",
        "yield_strength_pa",
        "fracture_toughness",
        "geometry_factor",
    ]

    for name in positive_values:
        if inputs[name] <= 0:
            raise ValueError(name + " must be positive")

    if inputs["poisson_ratio"] < 0 or inputs["poisson_ratio"] >= 0.5:
        raise ValueError("poisson_ratio must be between 0 and 0.5")

    if inputs["crack_depth_m"] >= inputs["wall_thickness_m"]:
        raise ValueError("crack depth must be smaller than wall thickness")


def hydrostatic_pressure(density, gravity, depth):
    return density * gravity * depth


def hoop_stress(net_pressure, mean_radius, wall_thickness):
    # External pressure greater than internal pressure closes rather than opens
    # the assumed Mode I crack, so negative opening stress is set to zero.
    opening_pressure = max(net_pressure, 0.0)
    return opening_pressure * mean_radius / wall_thickness


def stress_intensity_factor(stress, crack_depth, geometry_factor):
    return geometry_factor * stress * sqrt(pi * crack_depth)


def plastic_zone_sizes(stress_intensity, yield_strength):
    ratio_squared = (stress_intensity / yield_strength) ** 2
    plane_strain_zone = ratio_squared / (6 * pi)
    plane_stress_zone = ratio_squared / (2 * pi)
    return plane_strain_zone, plane_stress_zone


def minimum_plane_strain_size(fracture_toughness, yield_strength):
    return 2.5 * (fracture_toughness / yield_strength) ** 2


def calculate_case(inputs):
    """Calculate stresses, K_I and the screening checks for one case."""
    check_inputs(inputs)

    external_pressure = hydrostatic_pressure(
        inputs["seawater_density_kg_m3"],
        inputs["gravity_m_s2"],
        inputs["water_depth_m"],
    )
    net_pressure = inputs["internal_pressure_pa"] - external_pressure
    mean_radius = inputs["inner_radius_m"] + inputs["wall_thickness_m"] / 2

    stress = hoop_stress(
        net_pressure,
        mean_radius,
        inputs["wall_thickness_m"],
    )
    stress_intensity = stress_intensity_factor(
        stress,
        inputs["crack_depth_m"],
        inputs["geometry_factor"],
    )
    plane_strain_zone, plane_stress_zone = plastic_zone_sizes(
        stress_intensity,
        inputs["yield_strength_pa"],
    )
    minimum_size = minimum_plane_strain_size(
        inputs["fracture_toughness"],
        inputs["yield_strength_pa"],
    )

    remaining_wall = inputs["wall_thickness_m"] - inputs["crack_depth_m"]
    smallest_crack_dimension = min(inputs["crack_depth_m"], remaining_wall)
    smallest_plane_strain_dimension = min(
        inputs["wall_thickness_m"],
        inputs["crack_depth_m"],
        remaining_wall,
    )

    results = {
        "external_pressure_pa": external_pressure,
        "net_pressure_pa": net_pressure,
        "hoop_stress_pa": stress,
        "stress_intensity": stress_intensity,
        "toughness_utilisation": stress_intensity / inputs["fracture_toughness"],
        "plastic_zone_strain_m": plane_strain_zone,
        "plastic_zone_stress_m": plane_stress_zone,
        "plane_strain_min_size_m": minimum_size,
        "thin_wall_valid": inputs["inner_radius_m"] / inputs["wall_thickness_m"] >= 10,
        "elastic_stress_valid": stress < inputs["yield_strength_pa"],
        "plane_strain_size_valid": smallest_plane_strain_dimension >= minimum_size,
        # This 10% rule is an educational screening check, not a design-code limit.
        "small_scale_yielding_valid": plane_strain_zone <= 0.10 * smallest_crack_dimension,
    }

    return results


def pressure_for_utilisation(inputs, target_utilisation):
    """Calculate internal pressure for a chosen K_I/K_IC value."""
    check_inputs(inputs)

    if target_utilisation <= 0:
        raise ValueError("target utilisation must be positive")

    target_stress_intensity = target_utilisation * inputs["fracture_toughness"]
    required_stress = target_stress_intensity / (
        inputs["geometry_factor"] * sqrt(pi * inputs["crack_depth_m"])
    )

    mean_radius = inputs["inner_radius_m"] + inputs["wall_thickness_m"] / 2
    required_net_pressure = (
        required_stress * inputs["wall_thickness_m"] / mean_radius
    )
    external_pressure = hydrostatic_pressure(
        inputs["seawater_density_kg_m3"],
        inputs["gravity_m_s2"],
        inputs["water_depth_m"],
    )

    return required_net_pressure + external_pressure
