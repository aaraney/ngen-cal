from __future__ import annotations

from typing import Literal
from pydantic import Field

from .bmi_formulation import BMIPython


class Dhbv2Mts(BMIPython):
    """A BMIPython implementation for the δHBV2.0 MTS module."""

    python_type: str = "dhbv2.mts_bmi.MtsDeltaModelBmi"
    main_output_variable: Literal[
        "land_surface_water__runoff_volume_flux"
    ] = "land_surface_water__runoff_volume_flux"
    model_name: Literal["dhbv2.0_mts"] = Field(
        "dhbv2.0_mts", alias="model_type_name"
    )
