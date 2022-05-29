from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, cast, overload

with suppress(ImportError):
    import grpc
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.access.access_pb2 import (
        SetAccessBindingsRequest,
        UpdateAccessBindingsRequest,
    )

if TYPE_CHECKING:
    from google.protobuf.message import Message
    from google.protobuf.reflection import GeneratedProtocolMessageType
    from typing_extensions import Required, TypeGuard, Unpack

    from ..module_utils.types import (
        AccessBinding,
        Metadata,
        Operation,
        OperationResult,
        Resource,
    )

    class ABMetadata(Metadata):
        resource_id: str

    class ABOperation(Operation, ABMetadata):
        ...

    class GetFunction(TypedDict):
        function_id: Required[str]

    class GetApiGateway(TypedDict):
        api_gateway_id: Required[str]

    class GetDns(TypedDict):
        dns_zone_id: Required[str]


class ABClient(Protocol):
    def SetAccessBindings(
        self,
        request_serializer: GeneratedProtocolMessageType,
    ) -> Message:
        ...

    def UpdateAccessBindings(
        self,
        request_serializer: GeneratedProtocolMessageType,
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


class ResourceClient(Protocol):
    def Get(self, request_serializer: GeneratedProtocolMessageType) -> Message:
        ...

    def List(self, request_serializer: GeneratedProtocolMessageType) -> Message:
        ...


def is_resource_list(val: list[Resource] | str) -> TypeGuard[list[Resource]]:
    return bool(val) and isinstance(val, list)


@overload
def get_resource_by_id(
    client: ResourceClient,
    request_serializer: GeneratedProtocolMessageType,
    **kwargs: Unpack[GetFunction],  # type: ignore[misc]
) -> Resource | None:
    ...


@overload
def get_resource_by_id(  # type: ignore[misc]
    client: ResourceClient,
    request_serializer: GeneratedProtocolMessageType,
    **kwargs: Unpack[GetApiGateway],  # type: ignore[misc]
) -> Resource | None:
    ...


@overload
def get_resource_by_id(  # type: ignore[misc]
    client: ResourceClient,
    request_serializer: GeneratedProtocolMessageType,
    **kwargs: Unpack[GetDns],  # type: ignore[misc]
) -> Resource | None:
    ...


def get_resource_by_id(
    client,
    request_serializer,
    **kwargs,
) -> Resource | None:
    with suppress(grpc.RpcError):
        return cast(
            'Resource',
            MessageToDict(
                client.Get(request_serializer(**kwargs)),
                preserving_proto_field_name=True,
            ),
        )
    return None


def list_resources(
    client: ResourceClient,
    request_serializer: GeneratedProtocolMessageType,
    folder_id: str,
    filter: str,
):
    return MessageToDict(
        client.List(request_serializer(folder_id=folder_id, filter=filter)),
        preserving_proto_field_name=True,
    )


def get_resource_by_name(
    client: ResourceClient,
    request_serializer: GeneratedProtocolMessageType,
    *,
    folder_id: str,
    name: str,
) -> Resource | None:
    resources = list_resources(
        client,
        request_serializer,
        folder_id,
        f'name="{name}"',
    )

    r: list[Resource] | str = next(iter(resources.values()), [])
    return r[0] if is_resource_list(r) else None
