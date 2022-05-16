from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from google.protobuf.json_format import MessageToDict
from yandex.cloud.access.access_pb2 import (
    SetAccessBindingsRequest,
    UpdateAccessBindingsRequest,
)

if TYPE_CHECKING:
    from google.protobuf.message import Message

    from ..module_utils.types import AccessBinding, Metadata, Operation, OperationResult

    class ABMetadata(Metadata):
        resource_id: str

    class ABOperation(Operation, ABMetadata):
        ...


class ABClient(Protocol):
    def SetAccessBindings(
        self,
        request_serializer: SetAccessBindingsRequest,
    ) -> Message:
        ...

    def UpdateAccessBindings(
        self,
        request_serializer: UpdateAccessBindingsRequest,
    ) -> Message:
        ...


def set_access_bindings(
    client: ABClient,
    *,
    resource_id: str,
    access_bindings: list[AccessBinding],
) -> OperationResult:
    return {
        'SetAccessBindings': MessageToDict(
            client.SetAccessBindings(
                SetAccessBindingsRequest(
                    resource_id=resource_id,
                    access_bindings=access_bindings,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def remove_access_bindings(
    client: ABClient,
    *,
    resource_id: str,
    access_bindings: list[AccessBinding],
) -> OperationResult:
    access_binding_deltas = []
    for b in access_bindings:
        access_binding_deltas.append({'action': 'REMOVE', 'access_binding': b})

    return {
        'RemoveAccessBindings': MessageToDict(
            client.UpdateAccessBindings(
                UpdateAccessBindingsRequest(
                    resource_id=resource_id,
                    access_binding_deltas=access_binding_deltas,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


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
