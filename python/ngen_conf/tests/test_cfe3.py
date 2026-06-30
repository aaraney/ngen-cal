import pytest
from ngen.config.formulation import Formulation
from ngen.config.cfe3 import CFE3


def test_init(cfe3_params):
    _cfe3 = CFE3(**cfe3_params)


def test_name_map_default(cfe3_params):
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.name_map["rainfall_depth_m"] == "QINSUR"


def test_name_map_override(cfe3_params):
    cfe3_params["name_map"] = {"rainfall_depth_m": "RAINRATE"}
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.name_map["rainfall_depth_m"] == "RAINRATE"


@pytest.mark.parametrize("forcing", ["csv", "netcdf"], indirect=True)
def test_cfe3_formulation(cfe3_params, forcing):
    cfe3 = CFE3(**cfe3_params)
    f = {"params": cfe3, "name": "bmi_c"}
    cfe3_formulation = Formulation(**f)
    _cfe3 = cfe3_formulation.params
    assert _cfe3.name == "bmi_c"
    assert _cfe3.model_name == "CFE3"


def test_cfe3_model_params(cfe3_params):
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.model_params
    assert cfe3.model_params.gw_discharge_exponent == 6
    assert cfe3.model_params.soil_percolation_rate_limiter == 0.81
