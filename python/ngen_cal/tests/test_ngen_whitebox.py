from __future__ import annotations

import typing

import ngen.cal.ngen as ngen
import ngen.cal.parameter as parameter


def test_split_calibrated_and_derived_parameters():
    parameters = {
        "empty": [],
        "mod_a": [parameter.Parameter(param="a", min=0, max=1, init=0.5)],
        "mod_b": [
            parameter.Parameter(
                param="both", min=-1, max=1, init=0, scope=parameter.Scope.Both
            ),
            parameter.Parameter(
                param="cal", min=-1, max=1, init=0, scope=parameter.Scope.Cal
            ),
            parameter.Parameter(
                param="bmi", min=-1, max=1, init=0, scope=parameter.Scope.Bmi
            ),
        ],
    }

    expect_calibrated = {
        "mod_a": [parameter.Parameter(param="a", min=0, max=1, init=0.5)],
        "mod_b": [
            parameter.Parameter(
                param="both", min=-1, max=1, init=0, scope=parameter.Scope.Both
            ),
            parameter.Parameter(
                param="cal", min=-1, max=1, init=0, scope=parameter.Scope.Cal
            ),
        ],
    }
    expect_derived = {
        "mod_b": [
            parameter.Parameter(
                param="bmi", min=-1, max=1, init=0, scope=parameter.Scope.Bmi
            ),
        ]
    }

    calibrated, derived = ngen._split_calibrated_and_derived_parameters(parameters)
    assert calibrated == expect_calibrated
    assert derived == expect_derived


def double(
    parameter: parameter.Parameter, parameter_set: parameter.SetParameters, source: str
):
    return parameter_set[source].value * 2


def test_parameters():
    values = {
        "both": 0.5,
        "both_double": 0.7,
        "cal": 1,
    }
    parameters = {
        "mod_b": [
            parameter.Parameter(
                param="both", min=-1, max=1, init=0, scope=parameter.Scope.Both
            ),
            parameter.Parameter(
                param="both_double",
                min=-1,
                max=1,
                init=0,
                scope=parameter.Scope.Both,
                transform=lambda x: x * 2,
            ),
            parameter.Parameter(
                param="cal", min=-1, max=1, init=0, scope=parameter.Scope.Cal
            ),
            parameter.Parameter(
                param="bmi", min=-1, max=1, init=0, scope=parameter.Scope.Bmi
            ),
            parameter.Parameter(
                param="cal_double",
                min=-1,
                max=1,
                init=0,
                scope=parameter.Scope.Bmi,
                transform=double,
                transform_args={"source": "cal"},
            ),
        ],
    }

    expect = {
        "both": 0.5,
        "both_double": 1.4,
        "bmi": 0,
        "cal_double": 2,
    }
    calibrated, derived = ngen._split_calibrated_and_derived_parameters(parameters)
    import itertools
    import collections

    mods = collections.ChainMap(calibrated, derived)
    out = {}
    for mod in mods:
        params = itertools.chain(calibrated.get(mod, []) + derived.get(mod, []))
        # NOTE: each transformation only has access to parameters of the same model
        #       or, should we just give them the whole parameter space?
        ps = parameter.apply_transforms(values, params)
        out.update(ps)
    assert out == expect


def test_parameter_application():

    def value(value: float) -> float:
        return value

    def transform(
        value: float,
        parameter: parameter.Parameter,
        parameter_set: parameter.SetParameters,
    ) -> float:
        p = parameter_set[parameter.name]
        assert value == p.value
        return value

    def derivation(
        parameter: parameter.Parameter,
        parameter_set: parameter.SetParameters,
    ) -> float:
        p = parameter_set[parameter.name]
        return p.value

    def value_w_kwargs(value: float, expect: float) -> float:
        assert value == expect
        return value

    def transform_w_kwargs(
        value: float,
        parameter: parameter.Parameter,
        parameter_set: parameter.SetParameters,
        expect: float,
    ) -> float:
        value = transform(value, parameter, parameter_set)
        return value_w_kwargs(value, expect)

    def derivation_w_kwargs(
        parameter: parameter.Parameter,
        parameter_set: parameter.SetParameters,
        expect: float,
    ) -> float:
        value = derivation(parameter, parameter_set)
        return value_w_kwargs(value, expect)

    def fn(
        f: parameter.TransformFn, **kwargs
    ) -> dict[str, typing.Any | parameter.TransformFn]:
        return {"fn": f, **kwargs}

    def param(
        name: str,
        transform: parameter.TransformFn | None = None,
        transform_args: dict[str, typing.Any] | None = None,
    ) -> parameter.Parameter:
        return parameter.Parameter(
            param=name,
            min=0,
            max=1,
            init=0.5,
            transform=transform,
            transform_args=transform_args,
        )

    expect_value = 0.42
    expect = {"p": expect_value}
    transforms: list[dict[str, typing.Any | parameter.TransformFn]] = [
        fn(value),
        fn(transform),
        fn(derivation),
        fn(value_w_kwargs, expect=expect_value),
        fn(transform_w_kwargs, expect=expect_value),
        fn(derivation_w_kwargs, expect=expect_value),
    ]
    for tf in transforms:
        fn: parameter.TransformFn = tf.pop("fn")
        p = param(name="p", transform=fn, transform_args=tf)
        params = [p]
        tfs = parameter.apply_transforms(expect, params)
        assert tfs == expect
