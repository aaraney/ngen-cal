from __future__ import annotations

import pathlib
from datetime import datetime

import pytest
from ngen.cal.ngen import NgenBase
from ngen.cal.ngen_hooks.ngen_output import TrouteOutput
from ngen.config.realization import NgenRealization

data_dir = pathlib.Path(__file__).parent / "data/troute_output/"


@pytest.fixture
def ngen_cal_model_config() -> NgenBase:
    # NOTE: validation skipped and only fields required for
    # `TrouteOutput.ngen_cal_model_configure` are implemented
    realization = NgenRealization.parse_file(
        data_dir / "example_realization_config.json"
    )
    base = NgenBase.construct()
    base.ngen_realization = realization
    return base


troute_output_variants = (
    data_dir / "flowveldepth.csv",
    data_dir / "flowveldepth.parquet",
    data_dir / "troute_output.csv",
    data_dir / "troute_output.nc",
)


@pytest.mark.parametrize("file", troute_output_variants)
def test_ngen_cal_model_output(file: pathlib.Path, ngen_cal_model_config: NgenBase):
    import hypy

    output = TrouteOutput(file)

    # setup plugin
    output.ngen_cal_model_configure(config=ngen_cal_model_config)

    nexus_id = "nex-2420800"
    contributing_features = ["cat-2420800"]
    hydrolocation = hypy.HydroLocation(realized_nexus=nexus_id)
    contributing_catchments = [hypy.Catchment(id, {}) for id in contributing_features]
    nexus = hypy.Nexus(
        nexus_id=nexus_id,
        hydro_location=hydrolocation,
        contributing_catchments=contributing_catchments,
    )

    df = output.get_output(nexus=nexus)
    assert df is not None, "expect to receive pd.Series"

    dt = datetime.fromisoformat("2023-04-02 01:00:00")
    assert df[dt] == 0.0

    # testing data is for a single day
    assert len(df) == 24
