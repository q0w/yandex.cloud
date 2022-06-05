from __future__ import annotations

from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Protocol
from typing import TYPE_CHECKING
from typing import TypedDict

from yandex.cloud.access.access_pb2 import AccessBinding
from yandex.cloud.access.access_pb2 import AccessBindingDelta
from yandex.cloud.access.access_pb2 import REMOVE
from yandex.cloud.access.access_pb2 import SetAccessBindingsRequest
from yandex.cloud.access.access_pb2 import Subject
from yandex.cloud.access.access_pb2 import UpdateAccessBindingsRequest


if TYPE_CHECKING:
    from yandex.cloud.operation.operation_pb2 import Operation
    from grpc import UnaryUnaryMultiCallable


class ABClient(Protocol):
    SetAccessBindings: UnaryUnaryMultiCallable[SetAccessBindingsRequest, Operation]
    UpdateAccessBindings: UnaryUnaryMultiCallable[UpdateAccessBindingsRequest, Operation]


class LikeAB(TypedDict):
    role_id: str
    subject: Mapping[str, str]


def to_ab(d: LikeAB) -> AccessBinding:
    return AccessBinding(role_id=d['role_id'], subject=Subject(id=d['subject']['id'], type=d['subject']['type']))


def set_access_bindings(client: ABClient, resource_id: str, access_bindings: Iterable[AccessBinding]) -> Operation:
    return client.SetAccessBindings(SetAccessBindingsRequest(resource_id=resource_id, access_bindings=access_bindings))


def remove_access_bindings(client: ABClient, resource_id: str, access_bindings: Iterable[AccessBinding]) -> Operation:
    access_binding_deltas = []
    for b in access_bindings:
        access_binding_deltas.append(AccessBindingDelta(action=REMOVE, access_binding=b))

    return client.UpdateAccessBindings(
        UpdateAccessBindingsRequest(resource_id=resource_id, access_binding_deltas=access_binding_deltas),
    )


def default_arg_spec() -> dict[str, dict[str, Any]]:
    return {
        'name': {'type': 'str'},
        'resource_id': {'type': 'str'},
        'folder_id': {'type': 'str'},
        'access_bindings': {
            'type': 'list',
            'required': True,
            'options': {
                'role_id': {'type': 'str', 'required': True},
                'subject': {
                    'type': 'dict',
                    'options': {
                        'id': {'type': 'str', 'required': True},
                        'type': {'type': 'str', 'required': True},
                    },
                },
            },
        },
        'state': {
            'type': 'str',
            'default': 'present',
            'choices': ['present', 'absent'],
        },
    }


def default_required_one_of() -> list[tuple[str, ...]]:
    return [('resource_id', 'name')]


def default_required_by() -> dict[str, str]:
    return {'name': 'folder_id'}
