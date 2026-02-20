from __future__ import annotations

import typing
import logging

import pydantic
import pydantic.fields

if typing.TYPE_CHECKING:
    import pint
    from typing import Any
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, NoArgAnyCallable

class UnitAwareFieldInfo(pydantic.fields.FieldInfo):
    """
    Thin wrapper around a `pydantic.fields.FieldInfo` that adds unit information.
    """

    def __init__(self, unit: str | pint.Unit):
        super().__init__(units=unit)

    def __call__(
        self,
        default: Any = pydantic.fields.Undefined,
        *,
        default_factory: NoArgAnyCallable | None = None,
        alias: str | None = None,
        title: str | None = None,
        description: str | None = None,
        exclude: AbstractSetIntStr | MappingIntStrAny | Any | None = None,
        include: AbstractSetIntStr | MappingIntStrAny | Any | None = None,
        const: bool | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
        multiple_of: float | None = None,
        allow_inf_nan: bool | None = None,
        max_digits: int | None = None,
        decimal_places: int | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        allow_mutation: bool = True,
        regex: str | None = None,
        discriminator: str | None = None,
        repr: bool = True,
        **extra: Any,
    ) -> typing.Any:
        """
        Turn the UnitAwareFieldInfo into a pydantic.fields.FieldInfo.
        Use like pydantic.fields.Field function (same method signature).
        """
        return pydantic.Field(
            default=default,
            default_factory=default_factory,
            alias=alias,
            title=title,
            description=description,
            exclude=exclude,
            include=include,
            const=const,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            multiple_of=multiple_of,
            allow_inf_nan=allow_inf_nan,
            max_digits=max_digits,
            decimal_places=decimal_places,
            min_items=min_items,
            max_items=max_items,
            unique_items=unique_items,
            min_length=min_length,
            max_length=max_length,
            allow_mutation=allow_mutation,
            regex=regex,
            discriminator=discriminator,
            repr=repr,
            **self.extra,
            **extra,
        )


def Unit(unit: str | "pint.Unit") -> Any:
    """
    Return a type-erased UnitAwareFieldInfo.

    Example:
        class Foo(pydantic.BaseModel):
            bar: int = Unit("meter")
    """
    return UnitAwareFieldInfo(unit)


def _unit(unit: str) -> tuple[UnitAwareFieldInfo, Any]:
    """
    Return a UnitAwareFieldInfo and type erased UnitAwareFieldInfo from a str.


    Example:
        MeterField, Meter = _unit("meter")

        class Foo(pydantic.BaseModel):
            bar: int = Meter # type checker happy
            baz: int = MeterField(default=42) # type checker happy

            quox: int = Meter(gt=0) # type checker sad, but works
    """
    field = UnitAwareFieldInfo(unit=unit)
    return field, field


# Common units
MeterField, Meter = _unit("meter")
SecondField, Second = _unit("second")
KelvinField, Kelvin = _unit("kelvin")
DimensionlessField, Dimensionless = _unit("dimensionless")
PercentField, Percent = _unit("percent")
FractionalPercentField, FractionalPercent = _unit("hectopercent")
