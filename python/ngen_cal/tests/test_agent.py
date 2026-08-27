"""
Test suite for reading and manipulating ngen configration files
"""

from __future__ import annotations

import contextlib
import json
import pathlib
import typing
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd  # type: ignore
import pytest

if TYPE_CHECKING:
    from ngen.cal.agent import Agent


@pytest.mark.usefixtures("agent", "realization_config")
def test_update_config(agent: "Agent", realization_config: str) -> None:
    """
    Ensure that update config properly updates and serializes the config
    """
    i = 0
    params = pd.DataFrame({"model": "CFE", "0": 4.2, "param": "some_param"}, index=[0])
    id = "tst-1"
    agent.job.workdir = Path(realization_config).parent
    agent.update_config(i, params, id)
    with open(realization_config) as fp:
        data = json.load(fp)
    assert (
        data["catchments"][id]["formulations"][0]["params"]["model_params"][
            "some_param"
        ]
        == 4.2
    )

    df = pd.read_parquet(
        agent.job.workdir / f"ngen_cal_{id}_bmi_parameter_df_state.parquet"
    )
    assert df.to_dict() == params.to_dict()


parameter_transformation_tests = [
    (
        "data/cal_params/simple.yaml",
        {
            "bmi_c": {"nom::bmi": 1.0, "nom::both": 1.0},
            "bmi_fortran": {"nom::bmi": 1.0, "nom::both": 1.0},
        },
    ),
    (
        "data/cal_params/transform.yaml",
        {
            "bmi_c": {"topmodel::both": 1.0, "topmodel::bmi": 50.0},
            "bmi_fortran": {"nom::both": 3, "nom::bmi": 50.0},
        },
    ),
]


@pytest.mark.parametrize("ngen_cal_config,expect", parameter_transformation_tests)
def test_update_configs_parameter_transformations(
    tmp_path: pathlib.Path,
    ngen_cal_config: str,
    expect: dict[str, dict[str, float]],
):
    """
    Test parameter transformations are correctly applied.
    """
    import shutil
    import sys

    import yaml

    from ngen.cal import General, Model
    from ngen.cal.ngen import Ngen

    test_dir = pathlib.Path(__file__).resolve().parent
    # add test dir path to PYTHONPATH so functions in transforms.py are found.
    sys.path.append(str(test_dir))
    config = test_dir / ngen_cal_config
    data_dir = config.parent

    conf = yaml.safe_load(config.read_text())
    with pushd(data_dir):
        _resolve_relative_paths(conf)

    with pushd(tmp_path):
        general = General.parse_obj(conf["general"])
        general.workdir = tmp_path

        # copy test realization to tmp_dir
        shutil.copy(conf["model"]["realization"], tmp_path)
        realization = tmp_path / pathlib.Path(conf["model"]["realization"]).name
        conf["model"]["realization"] = realization
        model = Model.parse_obj(conf)

        assert isinstance(model.model, Ngen)
        m = model.model.unwrap()

        params = []
        for model, ps in m.params.items():
            for p in ps:
                params.append({"model": model, "0": p.init, "param": p.name})

        params_df = pd.DataFrame(params)
        m.update_config(0, params_df, None)

        with open(realization, "r") as fp:
            data = json.load(fp)
        ps = _realization_params_from_dict(data)
        assert ps == expect


@contextlib.contextmanager
def pushd(p: pathlib.Path):
    import os

    old = os.getcwd()
    os.chdir(p)
    try:
        yield
    finally:
        os.chdir(old)


def _resolve_relative_paths(d: dict[str, typing.Any]):
    for k, v in d.items():
        if isinstance(v, dict):
            _resolve_relative_paths(v)
            continue
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    _resolve_relative_paths(x)
        elif isinstance(v, str) and (v.startswith("./") or v.startswith("../")):
            v = pathlib.Path(v).absolute()
            d[k] = v


def _module_params_from_dict(f: dict[str, typing.Any]) -> dict[str, dict[str, float]]:
    def formulation_params(f: dict[str, typing.Any]) -> dict[str, float]:
        return f.get("params", {}).get("model_params", {})

    if f["name"] == "bmi_multi":
        return {
            module["name"]: params
            for module in f.get("params", {}).get("modules", [])
            if (params := formulation_params(module))
        }
    else:
        return {f["name"]: formulation_params(f)}


def _realization_params_from_dict(
    d: dict[str, typing.Any],
) -> dict[str, dict[str, float]]:
    out = {}
    for formulation in d.get("global", {}).get("formulations", []):
        params = _module_params_from_dict(formulation)
        out.update(params)
    return out
