import pytest
from pydantic import ValidationError
from ngen.config.formulation import Formulation
from ngen.config.cfe3 import CFE3
from ngen.config.init_config.cfe3 import CFE3 as CFE3Init


def test_init(cfe3_params):
    cfe3 = CFE3(**cfe3_params)


def test_name_map_default(cfe3_params):
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.name_map["atmosphere_water__liquid_equivalent_precipitation_rate"] == "QINSUR"


def test_name_map_override(cfe3_params):
    cfe3_params["name_map"] = {
        "atmosphere_water__liquid_equivalent_precipitation_rate": "RAINRATE"
    }
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.name_map["atmosphere_water__liquid_equivalent_precipitation_rate"] == "RAINRATE"


@pytest.mark.parametrize("forcing", ["csv", "netcdf"], indirect=True)
def test_cfe3_formulation(cfe3_params, forcing):
    cfe3 = CFE3(**cfe3_params)
    f = {"params": cfe3, "name": "bmi_c"}
    cfe3_formulation = Formulation(**f)
    _cfe3 = cfe3_formulation.params
    assert _cfe3.name == "bmi_c"
    assert _cfe3.model_name == "CFE"


def test_cfe3_model_params(cfe3_params):
    cfe3 = CFE3(**cfe3_params)
    assert cfe3.model_params
    assert cfe3.model_params.expon == 42
    assert cfe3.model_params.slope == 0.42


def test_cfe3_init_giuh_convolution_queue_length_mismatch(cfe3_init_config: str):
    """GIUH convolution queue length must match surface_routing_num_giuh_ordinates."""
    # Use the test config but change the convolution queue to have 2 elements
    # instead of 5 (num_giuh_ordinates=5), triggering the validator.
    ini = cfe3_init_config.replace(
        "state_surface_routing_init_giuh_convolution_queue_m=0.0,0.0,0.0,0.0,0.0",
        "state_surface_routing_init_giuh_convolution_queue_m=0.0,0.0",
    )
    with pytest.raises(ValidationError) as exc_info:
        CFE3Init.from_ini_str(ini)
    assert "GIUH convolution queue length" in str(exc_info.value)
