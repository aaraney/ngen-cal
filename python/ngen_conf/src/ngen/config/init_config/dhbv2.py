from __future__ import annotations

from typing import Optional

from ngen.init_config import format_serializers
from ngen.init_config import serializer_deserializer as serde
from ngen.init_config.units import CommonUnits, Field


class Dhbv2Mts(serde.YamlSerializerDeserializer):
    """Per-catchment init config for the δHBV2.0 MTS BMI
    (``dhbv2.mts_bmi.MtsDeltaModelBmi``).

    Source: https://github.com/mhpi/dhbv2

    Field names match the BMI config keys. Fields present in the input
    data are emitted; absent fields are excluded from output. The BMI
    initializes unset static variables to 0.0 and normalizes them
    against training statistics.
    """

    aridity: Optional[float] = Field(None, units=CommonUnits.Dimensionless, description="aridity index")
    # NOTE: the BMI source (mts_bmi.py _static_input_vars) declares meanP and ETPOT_Hargr
    # as `mm d-1`, but the model was trained on annual values based on the
    # normalization statistics (meanP ~1,000,
    # ETPOT_Hargr ~1,000 — plausible as mm/yr, not mm/d).
    # Pass annual values in mm yr-1; do not convert to daily.
    meanP: Optional[float] = Field(None, units="mm/year", description="mean annual precipitation")
    ETPOT_Hargr: Optional[float] = Field(None, units="mm/year", description="Hargreaves PET")
    NDVI: Optional[float] = Field(
        None, units=CommonUnits.Dimensionless, description="normalized difference vegetation index"
    )
    FW: Optional[float] = Field(None, units="mm/day", description="free water")

    meanslope: Optional[float] = Field(None, units="meter/kilometer", description="basin mean slope")
    meanelevation: Optional[float] = Field(None, units=CommonUnits.Meter, description="basin mean elevation")

    meanTa: Optional[float] = Field(None, units="degC", description="mean annual temperature")
    seasonality_P: Optional[float] = Field(
        None, units=CommonUnits.Dimensionless, description="precipitation seasonality"
    )
    seasonality_PET: Optional[float] = Field(
        None, units=CommonUnits.Dimensionless, description="PET seasonality"
    )

    SoilGrids1km_sand: Optional[float] = Field(None, units="percent")
    SoilGrids1km_clay: Optional[float] = Field(None, units="percent")
    SoilGrids1km_silt: Optional[float] = Field(None, units="percent")

    HWSD_clay: Optional[float] = Field(None, units="percent")
    HWSD_gravel: Optional[float] = Field(None, units="percent")
    HWSD_sand: Optional[float] = Field(None, units="percent")
    HWSD_silt: Optional[float] = Field(None, units="percent")

    T_clay: Optional[float] = Field(None, units="percent")
    T_gravel: Optional[float] = Field(None, units="percent")
    T_sand: Optional[float] = Field(None, units="percent")
    T_silt: Optional[float] = Field(None, units="percent")

    glaciers: Optional[float] = Field(None, units="percent", description="glacier fraction")
    permafrost: Optional[float] = Field(
        None, units=CommonUnits.Dimensionless, description="permafrost fraction"
    )
    snow_fraction: Optional[float] = Field(None, units="percent", description="snow fraction")
    snowfall_fraction: Optional[float] = Field(None, units="percent", description="snowfall fraction")

    permeability: Optional[float] = Field(None, units="meter**2", description="bedrock permeability")
    Porosity: Optional[float] = Field(
        None, units=CommonUnits.Dimensionless, description="active-layer porosity"
    )

    uparea: Optional[float] = Field(None, units="kilometer**2", description="upstream area")
    catchsize: Optional[float] = Field(None, units="kilometer**2", description="catchment area")
    lengthkm: Optional[float] = Field(None, units="kilometer", description="stream network length")

    model_dir: str = "/home/ec2-user/models/dhbv_2_mts"
    verbose: bool = False

    def to_yaml_str(self) -> str:
        return format_serializers.to_yaml_str(self.dict(by_alias=True, exclude_none=True))

    class Config(serde.YamlSerializerDeserializer.Config):
        fields = {
            "aridity": {"description": "aridity index [-]"},
            "meanP": {"description": "mean annual precipitation [mm yr-1]"},
            "ETPOT_Hargr": {"description": "Hargreaves PET [mm yr-1]"},
            "NDVI": {"description": "normalized difference vegetation index [-]"},
            "FW": {"description": "free water [mm d-1]"},
            "meanslope": {"description": "basin mean slope [m km-1]"},
            "meanelevation": {"description": "basin mean elevation [m]"},
            "meanTa": {"description": "mean annual temperature [degC]"},
            "seasonality_P": {"description": "precipitation seasonality [-]"},
            "seasonality_PET": {"description": "PET seasonality [-]"},
            "SoilGrids1km_sand": {"description": "SoilGrids sand composition [percent]"},
            "SoilGrids1km_clay": {"description": "SoilGrids clay composition [percent]"},
            "SoilGrids1km_silt": {"description": "SoilGrids silt composition [percent]"},
            "HWSD_clay": {"description": "HWSD clay composition [percent]"},
            "HWSD_gravel": {"description": "HWSD gravel composition [percent]"},
            "HWSD_sand": {"description": "HWSD sand composition [percent]"},
            "HWSD_silt": {"description": "HWSD silt composition [percent]"},
            "T_clay": {"description": "textured soil clay fraction [percent]"},
            "T_gravel": {"description": "textured soil gravel fraction [percent]"},
            "T_sand": {"description": "textured soil sand fraction [percent]"},
            "T_silt": {"description": "textured soil silt fraction [percent]"},
            "glaciers": {"description": "glacier fraction [percent]"},
            "permafrost": {"description": "permafrost fraction [-]"},
            "snow_fraction": {"description": "snow fraction [percent]"},
            "snowfall_fraction": {"description": "snowfall fraction [percent]"},
            "permeability": {"description": "bedrock permeability [m2]"},
            "Porosity": {"description": "active-layer porosity [-]"},
            "uparea": {"description": "upstream area [km2]"},
            "catchsize": {"description": "catchment area [km2]"},
            "lengthkm": {"description": "stream network length [km]"},
            "model_dir": {"description": "path to dhbv2 model weights directory"},
            "verbose": {"description": "enable verbose logging"},
        }
