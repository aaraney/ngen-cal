from __future__ import annotations

import dataclasses
import enum
import typing
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Optional,
    Protocol,
    Sequence,
    Union,
    final,
)

from pydantic import BaseModel, Field, PyObject

from ._typing import JsonSerializable

if TYPE_CHECKING:
    from typing import Union


class Scope(str, enum.Enum):
    Both = "both"
    Cal = "cal"
    Bmi = "bmi"


class Parameter(BaseModel):
    """
    The data class for a given parameter.
    """

    name: str = Field(alias="param")
    min: float
    max: float
    init: float
    scope: Scope = Scope.Both
    """
    scope determines if the parameter is:
    - both: adjusted by the calibration algorithm and set over bmi.
    - cal : only adjusted by the calibration algorithm.
    - bmi : only set over bmi.
    """
    transform: Optional[PyObject] = None
    """
    Callback function applied to a parameter to transform or derive a value
    prior to setting it over bmi.

    Transform function must be 1 or 3 shapes. Function argument names must match.
    (float) -> float
    (value: float, parameter: Parameter, parameter_set: SetParameters) -> float
      args must be named `value`, `parameter` and `parameter_set`
    (parameter: Parameter, parameter_set: SetParameters) -> float
      args must be named `parameter` and `parameter_set`

    Optionally, all transform function shapes can be further parameterized with
    keyword arguments specified in the `transform_args` field. For completeness,
    the full accepted forms of transform functions are:
    (float, **kwargs) -> float
    (value: float, parameter: Parameter, parameter_set: SetParameters, **kwargs) -> float
    (parameter: Parameter, parameter_set: SetParameters, **kwargs) -> float
    """
    transform_args: Optional[dict[str, Any]] = None
    """
    Optional keyword arguments passed to transform function on invocation.

    NOTE: "value", "parameter", or "parameter_set" are disallowed keys.
    A RuntimeError is raised if present.
    """

    _transform_type: Optional[type[TransformFn]] = None

    class Config(BaseModel.Config):
        allow_population_by_field_name = True
        underscore_attrs_are_private = True

    # NOTE: guard to avoid clobbering signature
    if not typing.TYPE_CHECKING:

        def __init__(self, **data: Any) -> None:
            super().__init__(**data)
            self.__post_init__()

    @final
    def __post_init__(self) -> None:
        if self.transform is None:
            if self.scope == Scope.Bmi:
                warnings.warn(
                    f"no configured transform fn for {self.scope.value!r} scoped parameter {self.name!r}; using init value.",
                    stacklevel=2,
                )
            return

        self.transform_args = self.transform_args or {}
        _raise_for_forbidden_transform_args(self.transform_args)

        ty = _identify_transform_fn_variant(self.transform)
        if (
            ty in (ValueTransformFn, ValueWithContextTransformFn)
            and self.scope == Scope.Bmi
        ):
            raise RuntimeError(
                f"cannot transform {self.scope.value!r} scoped parameter {self.name!r} w/ non-derived transform fn.\n"
                "must use a transformation function like (parameter: Parameter, parameter_set: SetParameters) -> float.\n"
                "not (float) -> float\n"
                "(value: float, parameter: Parameter, parameter_set: SetParameters) -> float"
            )
        self._transform_type = ty

    def apply_transform(self, parameter_set: SetParameters) -> float:
        param = parameter_set.get(self.name, None)
        if param is None:
            assert self.scope == Scope.Bmi, "invariant"
        if self.transform is None:
            return param.value if param is not None else self.init
        fn = self.transform
        ty = self._transform_type
        kwargs = self.transform_args or {}
        if ty == ValueTransformFn:
            assert param is not None, "invariant handled in __post_init__"
            fn = typing.cast(ValueTransformFn, fn)
            return fn(param.value, **kwargs)
        elif ty == ValueWithContextTransformFn:
            assert param is not None, "invariant handled in __post_init__"
            fn = typing.cast(ValueWithContextTransformFn, fn)
            return fn(
                value=param.value, parameter=self, parameter_set=parameter_set, **kwargs
            )
        elif ty == DerivedValueTransformFn:
            fn = typing.cast(DerivedValueTransformFn, fn)
            return fn(parameter=self, parameter_set=parameter_set, **kwargs)
        else:
            raise AssertionError("unreachable")


Parameters = Sequence[Parameter]


@dataclasses.dataclass
class SetParameter:
    value: float
    param: Parameter


SetParameters = Dict[str, SetParameter]
UnsetParameters = Dict[str, Parameter]


def apply_transforms(
    values: dict[str, float], params: Iterable[Parameter]
) -> dict[str, float]:
    out: dict[str, float] = {}
    set_params, unset_params = parameters(values, params)
    for name, param in set_params.items():
        # skip calibration only parameters
        if param.param.scope == Scope.Cal:
            continue
        value = param.param.apply_transform(set_params)
        out[name] = value

    for name, param in unset_params.items():
        assert param.scope != Scope.Cal, "invariant: cal scoped parameter. {}".format(
            name
        )
        value = param.apply_transform(set_params)
        out[name] = value
    return out


def parameters(
    values: dict[str, float], params: Iterable[Parameter]
) -> tuple[SetParameters, UnsetParameters]:
    values = values.copy()
    set_params: SetParameters = {}
    unset_params: UnsetParameters = {}
    for param in params:
        value = values.pop(param.name, None)
        if param.scope == Scope.Bmi:
            assert value is None, (
                "invariant: bmi scoped parameter in param scoped context. {}".format(
                    param.name
                )
            )
            unset_params[param.name] = param
            continue

        assert value is not None, (
            "invariant: tracked parameter not present. expected: {}".format(param.name)
        )
        set_params[param.name] = SetParameter(value=value, param=param)

    # parameters that we don't 'calibrate' / track but are present.
    # note, their scope is 'bmi'.
    for name, value in values.items():
        param = Parameter(param=name, min=value, max=value, init=value, scope=Scope.Bmi)
        set_params[name] = SetParameter(value=value, param=param)
    return set_params, unset_params


def _identify_transform_fn_variant(fn: TransformFn) -> type[TransformFn]:
    import inspect

    sig = inspect.signature(fn)
    if len(sig.parameters) == 0:
        raise RuntimeError(
            f"invalid transform function, {fn.__qualname__!r}\n"
            "transform function must be 1 or 3 shapes:\n"
            "(float) -> float\n"
            "(value: float, parameter: Parameter, parameter_set: SetParameters) -> float\n"
            "  args must be named `value`, `parameter`, and `parameter_set`\n"
            "(parameter: Parameter, parameter_set: SetParameters) -> float\n"
            "  args must be named `parameter` and `parameter_set`\n"
            f"got () -> {sig.return_annotation}"
        )
    transform_fn_required = {"value", "parameter", "parameter_set"}
    derive_fn_required = {"parameter", "parameter_set"}
    if transform_fn_required.issubset(sig.parameters):
        return ValueWithContextTransformFn
    elif derive_fn_required.issubset(sig.parameters):
        return DerivedValueTransformFn
    else:
        return ValueTransformFn


def _raise_for_forbidden_transform_args(d: dict[str, JsonSerializable]) -> None:
    callback_arg_names = ("value", "parameter", "parameter_set")
    for name in callback_arg_names:
        if name in d:
            message = (
                f"forbidden `transform_args` key, {name!r}."
                f"`transform` function argument names {callback_arg_names} are not allowed as `transform_args`"
            )
            raise RuntimeError(message)


class ValueTransformFn(Protocol):
    """
    Callback function invoked with the parameter's calibrated value. The
    function can optionally have other keyword args so long as they have
    defaults _or_ they are provided via `Parameter.transform_args`.

    NOTE: / encodes that the function's first arg is a float regardless of its
    name.
    """

    def __call__(self, value: float, /) -> float: ...


class ValueWithContextTransformFn(Protocol):
    """
    Callback function invoked with the parameter, its calibrated value, and the
    set of parameters in the calibration space. The function can optionally
    have other keyword args so long as they have defaults _or_ they are
    provided via `Parameter.transform_args`.

    NOTE: / and * encode that the function must have keyword-settable arguments
    named `value`, `parameter`, and `parameter_set` where declaration order
    doesn't matter.
    """

    def __call__(
        self,
        /,
        *,
        value: float,
        parameter: Parameter,
        parameter_set: SetParameters,
    ) -> float: ...


class DerivedValueTransformFn(Protocol):
    """
    Callback function invoked with the parameter and the set of parameters in
    the calibration space. The function can optionally have other keyword args
    so long as they have defaults _or_ they are provided via
    `Parameter.transform_args`.

    NOTE: / and * encode that the function must have keyword-settable arguments
    named `parameter` and `parameter_set` where declaration order doesn't
    matter.
    """

    def __call__(
        self,
        /,
        *,
        parameter: Parameter,
        parameter_set: SetParameters,
    ) -> float: ...


class ValueTransformFnKwargs(Protocol):
    def __call__(
        self,
        value: float,
        /,
        **kwargs: JsonSerializable,
    ) -> float: ...


class ValueWithContextTransformFnKwargs(Protocol):
    def __call__(
        self,
        /,
        *,
        value: float,
        parameter: Parameter,
        parameter_set: SetParameters,
        **kwargs: JsonSerializable,
    ) -> float: ...


class DerivedValueTransformFnKwargs(Protocol):
    def __call__(
        self,
        /,
        *,
        parameter: Parameter,
        parameter_set: SetParameters,
        **kwargs: JsonSerializable,
    ) -> float: ...


TransformFn = Union[
    ValueTransformFn,
    ValueWithContextTransformFn,
    DerivedValueTransformFn,
    ValueTransformFnKwargs,
    ValueWithContextTransformFnKwargs,
    DerivedValueTransformFnKwargs,
]
