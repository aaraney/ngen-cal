from ngen.config.formulation import Formulation
from ngen.config.dhbv2 import Dhbv2Mts


def test_init(dhbv2_params):
    Dhbv2Mts(**dhbv2_params)


def test_no_lib(dhbv2_params):
    dhbv2 = Dhbv2Mts(**dhbv2_params)
    assert "library" not in dhbv2.dict().keys()


def test_dhbv2_formulation(dhbv2_params):
    dhbv2 = Dhbv2Mts(**dhbv2_params)
    f = {"params": dhbv2, "name": "bmi_python"}
    dhbv2_formulation = Formulation(**f)
    _dhbv2 = dhbv2_formulation.params
    assert _dhbv2.name == "bmi_python"
    assert _dhbv2.model_name == "dhbv2.0_mts"
    serialized = _dhbv2.dict(by_alias=True)
    assert serialized["model_type_name"] == "dhbv2.0_mts"
    assert serialized["python_type"] == "dhbv2.mts_bmi.MtsDeltaModelBmi"
    assert serialized["main_output_variable"] == "land_surface_water__runoff_volume_flux"
