"""Core analytical fracture-mechanics calculations.

SI units are used internally. Stress intensity has units Pa*sqrt(m).
"""

from dataclasses import dataclass
from math import pi, sqrt


@dataclass(frozen=True)
class AssessmentInput:
    internal_pressure_pa: float = 10.0e6
    water_depth_m: float = 200.0
    seawater_density_kg_m3: float = 1000.0
    gravity_m_s2: float = 9.81
    inner_radius_m: float = 0.50
    wall_thickness_m: float = 0.050
    crack_depth_m: float = 0.020
    youngs_modulus_pa: float = 210.0e9
    poisson_ratio: float = 0.30
    yield_strength_pa: float = 450.0e6
    fracture_toughness: float = 50.0e6
    geometry_factor: float = 1.12

    def __post_init__(self) -> None:
        positive = {
            "internal_pressure_pa": self.internal_pressure_pa,
            "water_depth_m": self.water_depth_m,
            "seawater_density_kg_m3": self.seawater_density_kg_m3,
            "gravity_m_s2": self.gravity_m_s2,
            "inner_radius_m": self.inner_radius_m,
            "wall_thickness_m": self.wall_thickness_m,
            "crack_depth_m": self.crack_depth_m,
            "youngs_modulus_pa": self.youngs_modulus_pa,
            "yield_strength_pa": self.yield_strength_pa,
            "fracture_toughness": self.fracture_toughness,
            "geometry_factor": self.geometry_factor,
        }
        for name, value in positive.items():
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
        if not 0.0 <= self.poisson_ratio < 0.5:
            raise ValueError("poisson_ratio must be in the range [0, 0.5)")
        if self.crack_depth_m >= self.wall_thickness_m:
            raise ValueError("crack_depth_m must be smaller than wall_thickness_m")


@dataclass(frozen=True)
class AssessmentResult:
    external_pressure_pa: float
    net_pressure_pa: float
    hoop_stress_pa: float
    stress_intensity: float
    toughness_utilisation: float
    plastic_zone_strain_m: float
    plastic_zone_stress_m: float
    plane_strain_min_size_m: float
    thin_wall_valid: bool
    elastic_stress_valid: bool
    plane_strain_size_valid: bool
    small_scale_yielding_valid: bool


def hydrostatic_pressure(density_kg_m3: float, gravity_m_s2: float, depth_m: float) -> float:
    return density_kg_m3 * gravity_m_s2 * depth_m


def hoop_stress(net_pressure_pa: float, mean_radius_m: float, thickness_m: float) -> float:
    """Return tensile thin-wall hoop stress; compression does not open the crack."""
    return max(net_pressure_pa, 0.0) * mean_radius_m / thickness_m


def mode_i_stress_intensity(stress_pa: float, crack_depth_m: float, geometry_factor: float) -> float:
    return geometry_factor * stress_pa * sqrt(pi * crack_depth_m)


def irwin_plastic_zones(stress_intensity: float, yield_strength_pa: float) -> tuple[float, float]:
    ratio_squared = (stress_intensity / yield_strength_pa) ** 2
    plane_strain = ratio_squared / (6.0 * pi)
    plane_stress = ratio_squared / (2.0 * pi)
    return plane_strain, plane_stress


def astm_plane_strain_min_size(fracture_toughness: float, yield_strength_pa: float) -> float:
    return 2.5 * (fracture_toughness / yield_strength_pa) ** 2


def internal_pressure_for_utilisation(case: AssessmentInput, target_utilisation: float) -> float:
    """Return internal pressure at a selected K_I/K_IC screening boundary."""
    if target_utilisation <= 0.0:
        raise ValueError("target_utilisation must be positive")
    target_k = target_utilisation * case.fracture_toughness
    required_stress = target_k / (
        case.geometry_factor * sqrt(pi * case.crack_depth_m)
    )
    mean_radius = case.inner_radius_m + 0.5 * case.wall_thickness_m
    required_net_pressure = required_stress * case.wall_thickness_m / mean_radius
    external_pressure = hydrostatic_pressure(
        case.seawater_density_kg_m3, case.gravity_m_s2, case.water_depth_m
    )
    return required_net_pressure + external_pressure


def assess_case(case: AssessmentInput) -> AssessmentResult:
    external = hydrostatic_pressure(
        case.seawater_density_kg_m3, case.gravity_m_s2, case.water_depth_m
    )
    net = case.internal_pressure_pa - external
    mean_radius = case.inner_radius_m + 0.5 * case.wall_thickness_m
    stress = hoop_stress(net, mean_radius, case.wall_thickness_m)
    stress_intensity = mode_i_stress_intensity(
        stress, case.crack_depth_m, case.geometry_factor
    )
    plastic_strain, plastic_stress = irwin_plastic_zones(
        stress_intensity, case.yield_strength_pa
    )
    min_size = astm_plane_strain_min_size(
        case.fracture_toughness, case.yield_strength_pa
    )
    remaining_ligament = case.wall_thickness_m - case.crack_depth_m

    # A common screening rule requires the plastic zone to be small relative to
    # both crack depth and remaining ligament. The 10% limit is explicit rather
    # than presented as a code acceptance criterion.
    ssy_reference = min(case.crack_depth_m, remaining_ligament)

    return AssessmentResult(
        external_pressure_pa=external,
        net_pressure_pa=net,
        hoop_stress_pa=stress,
        stress_intensity=stress_intensity,
        toughness_utilisation=stress_intensity / case.fracture_toughness,
        plastic_zone_strain_m=plastic_strain,
        plastic_zone_stress_m=plastic_stress,
        plane_strain_min_size_m=min_size,
        thin_wall_valid=case.inner_radius_m / case.wall_thickness_m >= 10.0,
        elastic_stress_valid=stress < case.yield_strength_pa,
        plane_strain_size_valid=min(
            case.wall_thickness_m, case.crack_depth_m, remaining_ligament
        )
        >= min_size,
        small_scale_yielding_valid=plastic_strain <= 0.10 * ssy_reference,
    )
