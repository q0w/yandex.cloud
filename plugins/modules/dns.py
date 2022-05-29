from __future__ import annotations

from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Callable, Mapping, NoReturn, TypedDict, cast

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.resource import get_resource_by_id, get_resource_by_name

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import (
        CreateDnsZoneRequest,
        DeleteDnsZoneRequest,
        GetDnsZoneRequest,
        ListDnsZonesRequest,
        UpdateDnsZoneRequest,
    )
    from yandex.cloud.dns.v1.dns_zone_service_pb2_grpc import DnsZoneServiceStub


if TYPE_CHECKING:
    from ..module_utils.types import OperationResult


class Visibility(TypedDict):
    network_ids: list[str]


def create_dns(
    client: DnsZoneServiceStub,
    *,
    folder_id: str,
    zone: str,
    name: str | None = None,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
    visibility: Visibility | None = None,
) -> OperationResult:
    if visibility is None:
        req = partial(CreateDnsZoneRequest, public_visibility={})
    else:
        req = partial(CreateDnsZoneRequest, private_visibility=visibility)
    return {
        'CreateDns': MessageToDict(
            client.Create(
                req(
                    folder_id=folder_id,
                    zone=zone,
                    name=name,
                    description=description,
                    labels=labels,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def update_dns(
    client: DnsZoneServiceStub,
    *,
    dns_zone_id: str,
    name: str | None = None,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
    visibility: Visibility | None = None,
) -> OperationResult:
    if visibility is None:
        req = partial(UpdateDnsZoneRequest, public_visibility={})
    else:
        req = partial(UpdateDnsZoneRequest, private_visibility=visibility)
    return {
        'UpdateDns': MessageToDict(
            client.Update(
                req(
                    dns_zone_id=dns_zone_id,
                    name=name,
                    description=description,
                    labels=labels,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def delete_dns(
    client: DnsZoneServiceStub,
    dns_zone_id: str,
) -> OperationResult:
    return {
        'DeleteDns': MessageToDict(
            client.Delete(DeleteDnsZoneRequest(dns_zone_id=dns_zone_id)),
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

    with log_grpc_error(module):
        curr_dns = get_resource_by_id(
            dns_service,
            GetDnsZoneRequest,
            dns_zone_id=dns_zone_id,
        ) or get_resource_by_name(
            dns_service,
            ListDnsZonesRequest,
            folder_id=folder_id,
            name=name,
        )

    if state == 'present':
        if not curr_dns:
            with log_grpc_error(module):
                result.update(
                    create_dns(
                        dns_service,
                        folder_id=folder_id,
                        name=module.params.get('name'),
                        description=module.params.get('description'),
                        zone=module.params.get('zone'),
                        labels=module.params.get('labels'),
                        visibility=visibility,
                    ),
                )
        else:
            with log_grpc_error(module):
                result.update(
                    update_dns(
                        dns_service,
                        dns_zone_id=dns_zone_id,
                        name=module.params.get('name'),
                        description=module.params.get('description'),
                        labels=module.params.get('labels'),
                        visibility=visibility,
                    ),
                )
        changed = True
    elif state == 'absent':
        if not curr_dns:
            cast(Callable[..., NoReturn], module.fail_json)(
                msg=f'dns zone {dns_zone_id or name} not found',
            )
        with log_grpc_error(module):
            result.update(
                delete_dns(dns_service, curr_dns['id']),
            )
        changed = True
    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
