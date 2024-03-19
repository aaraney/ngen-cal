import typing
from pathlib import Path
from typing import TYPE_CHECKING

import typing_extensions
from ngen.config.init_config.utils import FloatUnitPair
from pydantic import BaseModel

if TYPE_CHECKING:
    from ngen.config_gen.hook_providers import HookProvider

from ngen.config.init_config.soil_freeze_thaw import IceFractionScheme
from ngen.config.init_config.soil_freeze_thaw import (
    SoilFreezeThaw as SoilFreezeThawConfig,
)
from ngen.config.init_config.value_unit_pair import ListUnitPair, ValueUnitPair

Hours: typing_extensions.TypeAlias = int

class SoilFreezeThaw:
    def __init__(self, simulation_duration: Hours, ice_fraction_scheme: IceFractionScheme):
        self.data = dict()
        self.data["end_time"] = ValueUnitPair(value=simulation_duration, unit="h")
        self.data["ice_fraction_scheme"] = ValueUnitPair(value=ice_fraction_scheme, unit="")

        # defaults
        self.data["dt"] = ValueUnitPair(value=1, unit="h")
        self.data["soil_moisture_bmi"] = True
        self.data["verbosity"] = "none"

    def hydrofabric_linked_data_hook(
        self, version: str, divide_id: str, data: typing.Dict[str, typing.Any]
    ) -> None:
        self.data["smcmax"] = FloatUnitPair(value=data["smcmax_soil_layers_stag=1"], unit="m/m")
        self.data["b"] = FloatUnitPair(value=data["bexp_soil_layers_stag=1"], unit="")
        self.data["satpsi"] = FloatUnitPair(value=data["psisat_soil_layers_stag=1"], unit="m")
        self.data["quartz"] = FloatUnitPair(value=data["quartz_soil_layers_stag=1"], unit="")
        self.data["soil_z"] = ListUnitPair
        self.data["soil_temperature"] = ListUnitPair

        self.data["soil_moisture_content"]
        self.data["bottom_boundary_temp"]
        self.data["top_boundary_temp"]

    def visit(self, hook_provider: "HookProvider") -> None:
        hook_provider.provide_hydrofabric_linked_data(self)

    def build(self) -> BaseModel:
        return SoilFreezeThawConfig(**self.data)


if __name__ == "__main__":
    from functools import partial
    from pathlib import Path

    import geopandas as gpd
    import pandas as pd
    from ngen.config_gen.file_writer import DefaultFileWriter
    from ngen.config_gen.generate import generate_configs
    from ngen.config_gen.hook_providers import DefaultHookProvider

    hf_file = "/Users/austinraney/Downloads/nextgen_09.gpkg"
    hf_lnk_file = "/Users/austinraney/Downloads/nextgen_09.parquet"

    hf: gpd.GeoDataFrame = gpd.read_file(hf_file, layer="divides")
    hf_lnk_data: pd.DataFrame = pd.read_parquet(hf_lnk_file)

    hook_provider = DefaultHookProvider(hf=hf, hf_lnk_data=hf_lnk_data)
    file_writer = DefaultFileWriter("./config/")

    simulation_duration_in_hours = 24 * 31
    ice_fraction_scheme = IceFractionScheme.Schaake
    soil_freeze_thaw = partial(
        SoilFreezeThaw,
        ice_fraction_scheme=ice_fraction_scheme,
        simulation_duration=simulation_duration_in_hours,
    )

    from ngen.config_gen.models.cfe import Cfe
    from ngen.config_gen.models.pet import Pet

    generate_configs(
        hook_providers=hook_provider,
        hook_objects=[soil_freeze_thaw, Cfe, Pet],
        file_writer=file_writer,
    )
