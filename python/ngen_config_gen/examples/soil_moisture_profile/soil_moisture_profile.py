from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from ngen.config_gen.hook_providers import HookProvider

from ngen.config.init_config.soil_moisture_profile import (
    SoilMoistureProfile as SoilMoistureProfileConfig,
)
from ngen.config.init_config.soil_moisture_profile import (
    soil_moisture_profile_option as SoilMoistureProfileOption,
    soil_storage_model as SoilStorageModel,
    water_table_based_method as WaterTableBasedMethod,
)
from ngen.config.init_config.utils import CSList


class SoilMoistureProfile:
    def __init__(
        self,
        soil_storage_model: SoilStorageModel,
        soil_moisture_profile_option: SoilMoistureProfileOption | None = None,
        water_table_based_method: WaterTableBasedMethod | None = None,
    ):
        """
        `soil_storage_model`:
            if 'conceptual', conceptual models are used for computing the soil moisture  profile (e.g., CFE).
            If 'layered', layered-based soil moisture models are used (e.g., LGAR).
            If 'topmodel', topmodel's variables are used.

        `soil_moisture_profile_option`:
            Needed if soil_storage_model = 'layered'.

        `water_table_based_method`:
            Needed if soil_storage_model = 'topmodel'.
        """
        self.data = dict()
        self.data["soil_storage_model"] = soil_storage_model
        self.data["soil_moisture_profile_option"] = soil_moisture_profile_option
        self.data["water_table_based_method"] = water_table_based_method

        # defaults
        self.data["verbosity"] = "none"
        # not sure if this is right? found here
        # https://github.com/NOAA-OWP/SoilMoistureProfiles/blob/2d61b86a3d7010be93af0d67f4d01fa6d0993029/configs/config_layered.txt#L5
        self.data["soil_z"] = CSList[float](__root__=[x / 10 for x in range(1, 21)])

        # Required if soil_storage_model = `layered`.
        # not sure if this is right? found here
        # https://github.com/NOAA-OWP/SoilMoistureProfiles/blob/2d61b86a3d7010be93af0d67f4d01fa6d0993029/configs/config_layered.txt#L8
        self.data["soil_depth_layers"] = CSList[float](__root__=[0.4, 1.75, 2.0])

        # Required if soil_storage_model = `conceptual`.
        # not sure if this is right? found here
        # https://github.com/NOAA-OWP/SoilMoistureProfiles/blob/2d61b86a3d7010be93af0d67f4d01fa6d0993029/configs/config_conceptual.txt#L6
        self.data["soil_storage_depth"] = 2.0

        # implicit defaults
        # self.data["water_table_depth"] = 6.0
        # self.data["soil_moisture_fraction_depth"] = 0.4

    def hydrofabric_linked_data_hook(
        self, version: str, divide_id: str, data: typing.Dict[str, typing.Any]
    ) -> None:
        self.data["smcmax"] = CSList[float](
            __root__=[
                data["smcmax_soil_layers_stag=1"],
                data["smcmax_soil_layers_stag=2"],
                data["smcmax_soil_layers_stag=3"],
                data["smcmax_soil_layers_stag=4"],
            ]
        )
        self.data["b"] = data["bexp_soil_layers_stag=1"]
        self.data["satpsi"] = data["psisat_soil_layers_stag=1"]

    def visit(self, hook_provider: "HookProvider") -> None:
        hook_provider.provide_hydrofabric_linked_data(self)

    def build(self) -> BaseModel:
        return SoilMoistureProfileConfig(**self.data)


if __name__ == "__main__":
    from functools import partial

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

    # `soil_storage_model`:
    #     if 'conceptual', conceptual models are used for computing the soil moisture  profile (e.g., CFE).
    #     If 'layered', layered-based soil moisture models are used (e.g., LGAR).
    #     If 'topmodel', topmodel's variables are used.
    #
    # `soil_moisture_profile_option`:
    #     Needed if soil_storage_model = 'layered'.
    #
    # `water_table_based_method`:
    #     Needed if soil_storage_model = 'topmodel'.
    soil_storage_model: SoilStorageModel = "conceptual"
    soil_moisture_profile_option = None
    water_table_based_method = None
    soil_moisture_profile = partial(
        SoilMoistureProfile,
        soil_storage_model=soil_storage_model,
        soil_moisture_profile_option=soil_moisture_profile_option,
        water_table_based_method=water_table_based_method,
    )

    from ngen.config_gen.models.cfe import Cfe
    from ngen.config_gen.models.pet import Pet

    generate_configs(
        hook_providers=hook_provider,
        hook_objects=[soil_moisture_profile, Cfe, Pet],
        file_writer=file_writer,
    )
