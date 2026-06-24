from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional, Union

from ngen.init_config import serializer_deserializer as serde
from pydantic import root_validator

from ngen.init_config.units import Field

from .utils import CSList

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class CFE3(serde.IniSerializerDeserializer):
    """CFE v3 init config model.

    CFE v3 has significant changes from v2:
    - All parameter names are more descriptive and self-documenting
    - Unit changes (satdk in cm/h, satpsi in cm, etc.)
    - GIUH is now the only surface routing method
    - DSBM (Discrete Soil Moisture) support
    - New state variables with `state_` prefix
    - New control parameters
    """

    # Version & Controls
    cfe_config_version: Literal["3.0"] = "3.0"
    """CFE config file version.

    units: -
    """

    control_model_timestep_h: float = Field(default=1.0, units="h")
    """Model timestep in hours.

    units: h
    bounds: > 0
    """

    control_input_forcing_filename: Literal["BMI"] = "BMI"
    """Input forcing filename. Set to 'BMI' for BMI coupling.

    units: -
    """

    control_total_num_simulation_timesteps: int = Field(default=0, ge=0)
    """Total number of simulation timesteps. Set to 0 to run until forcing file ends.

    units: -
    bounds: >= 0
    """

    control_verbosity: int = Field(default=1, ge=0, le=3)
    """Verbosity level for output.

    units: -
    bounds: 0-3
    """

    control_soil_simulate_freeze_thaw_true_false: bool = False
    """Enable/disable soil freeze-thaw simulation.

    units: -
    """

    control_soil_simulate_discrete_soil_moisture_true_false: bool = True
    """Enable/disable discrete soil moisture (DSBM) simulation.

    units: -
    """

    control_et_deepest_root_zone_discretization: int = Field(default=4, ge=1)
    """Deepest root zone discretization for ET calculation.

    units: -
    bounds: >= 1
    """

    control_soil_use_lookup_table_num_points: int = Field(default=5, ge=0)
    """Number of points for soil lookup table.

    units: -
    bounds: >= 0
    """

    # Catchment (optional metadata)
    catchment_id: Optional[str] = None
    """Catchment identifier (optional string).

    units: -
    """

    catchment_latitude_decimal_degree: Optional[float] = None
    """Catchment latitude in decimal degrees.

    units: decimal_degree
    """

    catchment_longitude_decimal_degree: Optional[float] = None
    """Catchment longitude in decimal degrees.

    units: decimal_degree
    """

    catchment_elevation: Optional[float] = Field(default=None, units="m")
    """Catchment elevation.

    units: m
    """

    catchment_area_km2: Optional[float] = Field(default=None, units="km2")
    """Catchment area.

    units: km2
    """

    catchment_impervious_fraction_0_1: float = Field(default=0.0, ge=0, le=1)
    """Fraction of catchment that is impervious.

    units: -
    bounds: 0-1
    """

    # Soil
    soil_depth_m: float = Field(units="m")
    """Soil depth.

    units: m
    bounds: > 0
    """

    soil_clapp_hornberger_exponent_b: float
    """Clapp-Hornberger exponent for soil water retention curve.

    units: -
    """

    soil_sat_hydraulic_conductivity_cm_per_h: float = Field(units="cm/h")
    """Saturated hydraulic conductivity.

    units: cm/h
    bounds: > 0
    """

    soil_sat_capillary_head_cm: float = Field(units="cm")
    """Saturated capillary head.

    units: cm
    bounds: > 0
    """

    soil_effective_porosity: float = Field(ge=0, le=1)
    """Effective soil porosity.

    units: -
    bounds: 0-1
    """

    soil_wilting_point_moisture_content: Optional[float] = None
    """Wilting point soil moisture content (auto-calculated if missing).

    units: -
    bounds: 0-1
    """

    soil_field_capacity_Pcap_over_Patm_0_1: float = Field(default=0.33, ge=0, le=1)
    """Field capacity as ratio of capillary pressure to atmospheric pressure.

    units: -
    bounds: 0-1
    """

    soil_ice_content_impervious_threshold: float = Field(default=0.0, ge=0, le=1)
    """Ice content threshold for impervious soil.

    units: -
    bounds: 0-1
    """

    soil_reservoir_rate_const_to_subsurface_lateral_flow: float = Field(
        default=0.01, units="1/h"
    )
    """Rate constant for subsurface lateral flow from soil reservoir.

    units: 1/h
    bounds: >= 0
    """

    soil_to_gw_percolation_rate_limiter_0_1: float = Field(ge=0, le=1)
    """Rate limiter for percolation from soil to groundwater.

    units: -
    bounds: 0-1
    """

    # State (initial conditions)
    state_soil_reservoir_init_storage_m: float = Field(units="m")
    """Initial soil reservoir storage.

    units: m
    bounds: >= 0
    """

    state_gw_reservoir_init_storage_m: float = Field(units="m")
    """Initial groundwater reservoir storage.

    units: m
    bounds: >= 0
    """

    state_surface_routing_init_giuh_convolution_queue_m: CSList[float] = Field(
        units="m"
    )
    """Initial GIUH convolution queue storage (one value per GIUH ordinate).

    units: m
    bounds: >= 0
    """

    state_subsurface_routing_init_nash_cascade_storage_m: CSList[float] = Field(
        units="m"
    )
    """Initial subsurface routing Nash cascade storage.

    units: m
    bounds: >= 0
    """

    # Groundwater
    gw_reservoir_max_storage_m: float = Field(units="m")
    """Maximum groundwater reservoir storage.

    units: m
    bounds: > 0
    """

    gw_discharge_coeff_m_per_timestep: float = Field(units="m/h")
    """Groundwater discharge coefficient.

    units: m/h
    bounds: >= 0
    """

    gw_discharge_exponent: float = Field(ge=1.0, le=8.0)
    """Groundwater discharge exponent.

    units: -
    bounds: 1-8
    """

    # Partitioning
    partitioning_scheme_name: Literal["SCHAAKE", "XINANJIANG"]
    """Surface water partitioning scheme name.

    units: -
    """

    # Xinanjiang (conditional - only used when partitioning_scheme_name=XINANJIANG)
    partitioning_xinanjiang_tension_water_inflection_point: Optional[float] = Field(None, gte=0.001, lte=0.017)
    """Xinanjiang tension water inflection point parameter.

    units: -
    bounds: 0-1
    """

    partitioning_xinanjiang_tension_water_soil_moist_distrib_exponent: Optional[
        float
    ] = None
    """Xinanjiang tension water soil moisture distribution exponent.

    units: -
    bounds: >= 0
    """

    partitioning_xinanjiang_free_water_soil_moist_distrib_exponent: Optional[
        float
    ] = None
    """Xinanjiang free water soil moisture distribution exponent.

    units: -
    bounds: >= 0
    """

    # Surface Routing (GIUH only)
    surface_routing_num_giuh_ordinates: int
    """Number of GIUH ordinates.

    units: -
    bounds: > 0
    """

    surface_routing_giuh_ordinates: CSList[float]
    """GIUH ordinates (must sum to 1.0).

    units: -
    bounds: >= 0
    """

    # Subsurface Routing
    subsurface_routing_nash_reservoir_time_constant_k: float = Field(
        default=0.03, units="1/h"
    )
    """Subsurface routing Nash reservoir time constant.

    units: 1/h
    bounds: >= 0
    """

    @root_validator
    def validate_giuh_convolution_queue_length(cls, values):
        """Validate that GIUH convolution queue length matches number of ordinates."""
        num_ordinates = values.get("surface_routing_num_giuh_ordinates")
        queue = values.get("state_surface_routing_init_giuh_convolution_queue_m")
        if num_ordinates is not None and queue is not None:
            # CSList stores data in __root__
            queue_list = queue.__root__ if hasattr(queue, "__root__") else queue
            if len(queue_list) != num_ordinates:
                raise ValueError(
                    f"GIUH convolution queue length ({len(queue_list)}) must match "
                    f"number of GIUH ordinates ({num_ordinates})"
                )
        return values

    class Config(serde.IniSerializerDeserializer.Config):
        no_section_headers = True
        space_around_delimiters = False
        preserve_key_case = True
        allow_population_by_field_name = True

        fields = {
            # Catchment metadata
            "catchment_impervious_fraction_0_1": {
                "alias": "catchment_impervious_fraction_0-1"
            },
            # Controls
            "control_et_deepest_root_zone_discretization": {
                "alias": "control_ET_deepest_root_zone_discretization"
            },
            # Soil
            "soil_clapp_hornberger_exponent_b": {
                "alias": "soil_Clapp_Hornberger_exponent_b"
            },
            "soil_to_gw_percolation_rate_limiter_0_1": {
                "alias": "soil_to_gw_percolation_rate_limiter_0_to_1"
            },
            # Partitioning
            "partitioning_xinanjiang_tension_water_inflection_point": {
                "alias": "partitioning_Xinanjiang_tension_water_inflection_point"
            },
            "partitioning_xinanjiang_tension_water_soil_moist_distrib_exponent": {
                "alias": "partitioning_Xinanjiang_tension_water_soil_moist_distrib_exponent"
            },
            "partitioning_xinanjiang_free_water_soil_moist_distrib_exponent": {
                "alias": "partitioning_Xinanjiang_free_water_soil_moist_distrib_exponent"
            },
        }

    def dict(
        self,
        *,
        include: AbstractSetIntStr | MappingIntStrAny | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | None = None,
        by_alias: bool = False,
        skip_defaults: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> DictStrAny:
        """Override dict to exclude None values by default."""
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none or True,
        )
