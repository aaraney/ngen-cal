from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import TypeAlias

JsonSerializable: TypeAlias = Union[
    Dict[str, "JsonSerializable"], List["JsonSerializable"], str, int, float, bool, None
]
