import pathlib

import pytest
import pydantic
from ngen.cal.ngen import (
    Ngen,
    NgenBase,
    NgenExplicit,
    NgenIndependent,
    NgenStrategy,
    NgenUniform,
)


def test_NgenExplicit_strategy_default_value():
    # construct object without validation.
    o = NgenExplicit.construct()
    assert o.strategy == NgenStrategy.explicit


def test_NgenIndependent_strategy_default_value():
    # construct object without validation.
    o = NgenIndependent.construct()
    assert o.strategy == NgenStrategy.independent


def test_NgenUniform_strategy_default_value():
    # construct object without validation.
    o = NgenUniform.construct()
    assert o.strategy == NgenStrategy.uniform


def test_NgenBase_verify_realization(ngen_config: Ngen):
    # session level pytest fixture. take deep copy to avoid pollution
    config = ngen_config.__root__.copy(deep=True)
    assert isinstance(config, NgenBase)

    assert config.ngen_realization is not None, "should have already raised if not None"
    config.ngen_realization.output_root = pathlib.Path("./output_root")

    with pytest.raises(pydantic.ValidationError):
        Ngen.parse_obj(dict(config))


def test_log_bmi_parameter_space(tmp_path: pathlib.Path):
    import pandas as pd

    iteration = 0
    space_id = None
    path = tmp_path / NgenBase.bmi_parameter_space_filename(space_id)
    params = pd.DataFrame({"model": ["test"], "param": ["p"], "value": [1]})
    NgenBase.log_bmi_parameter_space(
        i=iteration, id=space_id, params_df=params, path=tmp_path
    )
    expect = pd.DataFrame({"model": ["test"], "param": ["p"], str(iteration): [1]})
    got = pd.read_parquet(path)
    assert got.equals(expect)


def test_log_bmi_parameter_space_warns(tmp_path: pathlib.Path):
    import pandas as pd

    iteration = 0
    space_id = None
    path = tmp_path / NgenBase.bmi_parameter_space_filename(space_id)
    params = pd.DataFrame({"model": ["test"], "param": ["p"], "value": [1]})
    NgenBase.log_bmi_parameter_space(
        i=iteration, id=space_id, params_df=params, path=tmp_path
    )
    new = pd.DataFrame({"model": ["test"], "param": ["p"], "value": [2]})
    with pytest.warns(UserWarning):
        NgenBase.log_bmi_parameter_space(
            i=iteration, id=space_id, params_df=new, path=tmp_path
        )
    expect = pd.DataFrame({"model": ["test"], "param": ["p"], str(iteration): [2]})
    got = pd.read_parquet(path)
    assert got.equals(expect)
