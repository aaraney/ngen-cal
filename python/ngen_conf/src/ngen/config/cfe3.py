from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field

from .bmi_formulation import BMIC


class CFE3Params(BaseModel):
    """Class for validating CFE3 Parameters"""

    soil_effective_porosity: Optional[float]
    """Effective soil porosity (dimensionless)."""
    soil_saturated_hydraulic_conductivity: Optional[float]
    """Saturated hydraulic conductivity (cm/h)."""
    soil_percolation_rate_limiter: Optional[float]
    """Percolation rate limiter 0-1 (dimensionless)."""
    soil_clapp_hornberger_b: Optional[float]
    """Clapp-Hornberger exponent (dimensionless)."""
    soil_lateral_flow_k: Optional[float]
    """Lateral flow rate constant (h-1)."""
    subsurface_nash_k: Optional[float]
    """Subsurface Nash cascade time constant (h-1)."""
    gw_discharge_coefficient: Optional[float]
    """Groundwater discharge coefficient (m/s)."""
    gw_discharge_exponent: Optional[float]
    """Groundwater discharge exponent (dimensionless)."""
    gw_max_storage_m: Optional[float]
    """Maximum groundwater storage (m)."""
    soil_saturated_capillary_head: Optional[float]
    """Saturated capillary head (cm)."""
    soil_field_capacity_fraction: Optional[float]
    """Field capacity Pcap/Patm (dimensionless)."""
    # Xinanjiang
    xinanjiang_inflection_a: Optional[float]
    """Xinanjiang tension water inflection point."""
    xinanjiang_shape_b: Optional[float]
    """Xinanjiang tension water shape parameter."""
    xinanjiang_shape_x: Optional[float]
    """Xinanjiang free water shape parameter."""

    class Config(BaseModel.Config):
        allow_population_by_field_name = True
        fields = {
            "soil_clapp_hornberger_b": {
                "alias": "soil_Clapp_Hornberger_b"
            },
            "soil_lateral_flow_k": {"alias": "soil_lateral_flow_K"},
            "subsurface_nash_k": {"alias": "subsurface_nash_K"},
            "xinanjiang_inflection_a": {
                "alias": "Xinanjiang_inflection_a"
            },
            "xinanjiang_shape_b": {"alias": "Xinanjiang_shape_b"},
            "xinanjiang_shape_x": {"alias": "Xinanjiang_shape_x"},
        }


class CFE3(BMIC):
    """A BMIC implementation for the CFE v3 ngen module.
    """
    model_params: Optional[CFE3Params]
    main_output_variable: str = "discharge_m"
    registration_function: str = "register_bmi_cfe"
    model_name: Literal["CFE3"] = Field("CFE3", alias="model_type_name")

    # variable name mappings for CFE3 inputs
    _variable_names_map = {
        "rainfall_depth_m": "QINSUR"
    }
