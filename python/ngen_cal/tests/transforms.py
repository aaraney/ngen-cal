from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ngen.cal.parameter import Parameter, SetParameters


def derive(
    parameter: Parameter,
    parameter_set: SetParameters,
    source: str,
) -> float:
    p = parameter_set[source]
    return p.value
