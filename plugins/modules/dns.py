from __future__ import annotations

from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Callable, Mapping, NoReturn, TypedDict, cast, overload

from ..module_utils.api_gateway import get_api_gateway_by_name
from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import (
        CreateDnsZoneRequest,
        UpdateDnsZoneRequest,
    )
    from yandex.cloud.dns.v1.dns_zone_service_pb2_grpc import DnsZoneServiceStub


if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required, Unpack

    from ..module_utils.types import OperationResult

    class _DnsKwargs(TypedDict, total=False):
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[Mapping[str, str]]

    class _CreateDnsKwargs(_DnsKwargs):
        folder_id: Required[str]
        zone: Required[str]

    class _UpdateDnsKwargs(_DnsKwargs):
        # TODO: update_mask
        dns_zone_id: Required[str]

    class PrivateUpdateDnsKwargs(_UpdateDnsKwargs):
        private_visibility: Required[PrivateVisibility]

    class PublicUpdateDnsKwargs(_UpdateDnsKwargs):
        public_visibility: Required[Mapping]

    class PrivateCreateDnsKwargs(_CreateDnsKwargs):
        private_visibility: Required[PrivateVisibility]

    class PublicCreateDnsKwargs(_CreateDnsKwargs):
        public_visibility: Required[Mapping]


class PrivateVisibility(TypedDict):
    network_ids: list[str]


@overload
def create(
    client: DnsZoneServiceStub,
    **kwargs: Unpack[PrivateCreateDnsKwargs],  # type: ignore[misc]
) -> OperationResult:
    ...


@overload
def create(  # type: ignore[misc]
    client: DnsZoneServiceStub,
    **kwargs: Unpack[PublicCreateDnsKwargs],  # type: ignore[misc]
) -> OperationResult:
    ...


def create(client: DnsZoneServiceStub, **kwargs):
    return {
        'CreateDns': MessageToDict(
            client.Create(CreateDnsZoneRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    }


@overload
def update(
    client: DnsZoneServiceStub,
    **kwargs: Unpack[PublicUpdateDnsKwargs],  # type: ignore[misc]
) -> OperationResult:
    ...


@overload
def update(  # type: ignore[misc]
    client: DnsZoneServiceStub,
    **kwargs: Unpack[PrivateUpdateDnsKwargs],  # type: ignore[misc]
) -> OperationResult:
    ...


def update(client: DnsZoneServiceStub, **kwargs):
    return {
        'UpdateDns': MessageToDict(
            client.Update(UpdateDnsZoneRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    }


def main():
    argument_spec = default_arg_spec()
    argument_spec.update(
        {
            'folder_id': {'type': 'str'},
            'dns_zone_id': {'type': 'str'},
            'name': {'type': 'str'},
            'description': {'type': 'str'},
            'zone': {'type': 'str', 'required': True},
            'labels': {'type': 'dict', 'elements': 'str'},
            'visibility': {
                'type': 'dict',
                'options': {
                    'network_ids': {
                        'type': 'list',
                        'elements': 'str',
                        'required': True,
                    },
                },
                'default': {},
            },
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        },
    )
    required_if = default_required_if()
    required_one_of = [
        ('dns_zone_id', 'name', 'folder_id'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    module = init_module(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        required_by=required_by,
        required_if=required_if,
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    dns_service = sdk.client(DnsZoneServiceStub)

    result = {}
    dns_zone_id = module.params.get('dns_zone_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    visibility = module.params.get('visibility')
    state = module.params.get('state')
    changed = False

    if state == 'present':
        if not visibility:
            with log_grpc_error(module):
                result.update(
                    create(
                        dns_service,
                        folder_id=folder_id,
                        zone=module.params.get('zone'),
                        labels=module.params.get('labels'),
                        public_visibility=visibility,
                    ),
                )
        else:
            with log_grpc_error(module):
                result.update(
                    create(
                        dns_service,
                        folder_id=folder_id,
                        zone=module.params.get('zone'),
                        labels=module.params.get('labels'),
                        private_visibility=visibility,
                    ),
                )
        with log_grpc_error(module):
            result.update(
                update(
                    dns_service,
                    dns_zone_id=folder_id,
                    public_visibility={},
                ),
            )

    elif state == 'absent':
        pass


if __name__ == '__main__':
    main()
