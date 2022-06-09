from __future__ import annotations

from contextlib import suppress
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import CreateDnsZoneRequest
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import DeleteDnsZoneRequest
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import GetDnsZoneRequest
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import ListDnsZonesRequest
    from yandex.cloud.dns.v1.dns_zone_service_pb2 import UpdateDnsZoneRequest
    from yandex.cloud.dns.v1.dns_zone_service_pb2_grpc import DnsZoneServiceStub


def main() -> NoReturn:
    argument_spec = default_arg_spec()
    argument_spec.update(
        {
            'folder_id': {'type': 'str'},
            'dns_zone_id': {'type': 'str'},
            'name': {'type': 'str'},
            'description': {'type': 'str'},
            'zone': {'type': 'str', 'required': True},
            'labels': {'type': 'dict'},
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
    client: DnsZoneServiceStub = init_sdk(module).client(DnsZoneServiceStub)
    result = {}

    state = module.params['state']
    dns_zone_id = module.params['dns_zone_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    zone = module.params['zone']
    kw = {
        'name': name,
        'description': module.params['description'],
        'labels': module.params['labels'],
    }
    if module.params['visibility']:
        kw['private_visibility'] = module.params['visibility']
    else:
        kw['public_visibility'] = {}

    # check if the dns exists
    curr_dns = None
    with log_grpc_error(module):
        if dns_zone_id:
            curr_dns = client.Get(GetDnsZoneRequest(dns_zone_id=dns_zone_id))
        else:
            zones = client.List(ListDnsZonesRequest(folder_id=folder_id, filter=f'name="{name}"')).dns_zones
            if zones:
                curr_dns = zones[0]

    with log_grpc_error(module):
        if state == 'present':
            if curr_dns:
                kw['dns_zone_id'] = dns_zone_id
                resp = client.Update(UpdateDnsZoneRequest(**kw))
                result.update(MessageToDict(resp))
            else:
                kw['folder_id'] = folder_id
                kw['zone'] = zone
                resp = client.Create(CreateDnsZoneRequest(**kw))
                result.update(MessageToDict(resp))

        elif state == 'absent':
            if not curr_dns:
                module.fail_json(f'dns zone {dns_zone_id or name} not found')
            resp = client.Delete(DeleteDnsZoneRequest(dns_zone_id=curr_dns.id))
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
