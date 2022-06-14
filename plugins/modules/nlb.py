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
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import CreateNetworkLoadBalancerRequest
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import DeleteNetworkLoadBalancerRequest
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import GetNetworkLoadBalancerRequest
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import ListNetworkLoadBalancersRequest
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import UpdateNetworkLoadBalancerRequest
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2_grpc import NetworkLoadBalancerServiceStub


def main() -> NoReturn:
    argument_spec = default_arg_spec()
    argument_spec.update(
        {
            'folder_id': {'type': 'str'},
            'network_load_balancer_id': {'type': 'str'},
            'name': {'type': 'str'},
            'description': {'type': 'str'},
            'labels': {'type': 'dict'},
            'region_id': {'type': 'str'},
            'type': {'type': 'str', 'choices': ['EXTERNAL'], 'default': 'EXTERNAL'},
            'listener_specs': {
                'type': 'list',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'port': {'type': 'str', 'required': True},
                    'protocol': {'type': 'str', 'choices': ['TCP', 'UDP'], 'required': True},
                    'target_port': {'type': 'str'},
                    'external_address_spec': {
                        'type': 'dict',
                        'options': {
                            'address': {'type': 'str', 'required': True},
                            'ip_version': {'type': 'str', 'choices': ['IPV4', 'IPV6'], 'required': True},
                        },
                    },
                    'internal_address_spec': {
                        'type': 'dict',
                        'options': {
                            'address': {'type': 'str', 'required': True},
                            'ip_version': {'type': 'str', 'choices': ['IPV4', 'IPV6'], 'required': True},
                            'subnet_id': {'type': 'str', 'required': True},
                        },
                    },
                },
            },
            'attached_target_groups': {
                'type': 'list',
                'options': {
                    'target_group_id': {'type': 'str', 'required': True},
                    'health_checks': {
                        'type': 'list',
                        'options': {
                            'name': {'type': 'str', 'required': True},
                            'interval': {'type': 'str'},
                            'timeout': {'type': 'str'},
                            'unhealthy_threshold': {'type': 'int', 'required': True},
                            'healthy_threshold': {'type': 'int', 'required': True},
                            'tcp_options': {
                                'type': 'dict',
                                'options': {
                                    'port': {'type': 'int', 'required': True},
                                },
                            },
                            'http_options': {
                                'type': 'dict',
                                'options': {
                                    'port': {'type': 'int', 'required': True},
                                    'path': {'type': 'str'},
                                },
                            },
                        },
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
    mutually_exclusive = [
        ('internal_address_spec', 'external_address_spec'),
        ('tcp_options', 'http_options'),
    ]
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
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
    )
    client: NetworkLoadBalancerServiceStub = init_sdk(module).client(NetworkLoadBalancerServiceStub)
    result = {}

    state = module.params['state']
    nlb_id = module.params['network_load_balancer_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    description = module.params['description']
    labels = module.params['labels']
    region_id = module.params['region_id']
    type = module.params['type']
    listener_specs = module.params['listener_specs']
    attached_target_groups = module.params['attached_target_groups']
    if attached_target_groups:
        for g in attached_target_groups:
            if len(g.health_checks) != 1:
                module.fail_json('health_checks: the number of elements must be exactly 1')

    curr_nlb = None
    with log_grpc_error(module):
        if nlb_id:
            curr_nlb = client.Get(GetNetworkLoadBalancerRequest(network_load_balancer_id=nlb_id))
        else:
            nlbs = client.List(
                ListNetworkLoadBalancersRequest(folder_id=folder_id, filter=f'name="{name}"'),
            ).network_load_balancers
            if nlbs:
                curr_nlb = nlbs[0]

    with log_grpc_error(module):
        if state == 'present':
            if curr_nlb:
                resp = client.Update(
                    UpdateNetworkLoadBalancerRequest(
                        network_load_balancer_id=curr_nlb.id,
                        name=name,
                        description=description,
                        labels=labels,
                        listener_specs=listener_specs,
                        attached_target_groups=attached_target_groups,
                    ),
                )
                result.update(MessageToDict(resp))
            else:
                resp = client.Create(
                    CreateNetworkLoadBalancerRequest(
                        folder_id=folder_id,
                        description=description,
                        labels=labels,
                        region_id=region_id,
                        type=type,
                        listener_specs=listener_specs,
                        attached_target_groups=attached_target_groups,
                    ),
                )
                result.update(MessageToDict(resp))
        elif state == 'absent':
            if not curr_nlb:
                module.fail_json(f'networkloadbalancer {nlb_id or name} not found')
            resp = client.Delete(DeleteNetworkLoadBalancerRequest(network_load_balancer_id=curr_nlb.id))
            result.update(MessageToDict(resp))
    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
