from __future__ import annotations

from typing import TypedDict


# TODO: total=false?
class Connectivity(TypedDict):
    network_id: str
    subnet_id: list[str]
