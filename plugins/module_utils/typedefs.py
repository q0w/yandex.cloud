from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, TypeVar

OperationResult = Dict[str, Dict[str, Any]]

if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required, TypedDict

    Metadata = TypedDict('Metadata', {'@type': str})
    T = TypeVar('T', bound=Metadata)

    # TODO: add 'done', 'result', 'error'
    class Operation(TypedDict, Generic[T], total=False):
        id: str
        description: NotRequired[str]
        created_at: Required[str]
        created_by: Required[str]
        modified_at: Required[str]
        done: NotRequired[bool]
        metadata: Required[T]

    # TODO: total=false?
    class Connectivity(TypedDict):
        network_id: str
        subnet_id: list[str]

    class Subject(TypedDict):
        id: str
        type: str

    class AccessBinding(TypedDict):
        role_id: str
        subject: Subject
