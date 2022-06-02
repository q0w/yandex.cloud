from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, List, Literal, Mapping, TypedDict, TypeVar, overload

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)

with suppress(ImportError):
    from google.protobuf.duration_pb2 import Duration
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import (
        CreateNetworkLoadBalancerRequest,
    )
    from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2_grpc import (
        NetworkLoadBalancerServiceStub,
    )

# FIXME: "internal" is not available
NetworkLoadBalancerType = Literal['EXTERNAL']
Protocol = Literal['TCP', 'UDP']
IpVersion = Literal['IPV4', 'IPV6']


if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required, TypeGuard

    class ExternalAddressSpec(TypedDict):
        address: str
        ip_version: IpVersion

    class InternalAddressSpec(ExternalAddressSpec):
        subnet_id: str

    class _ListenerSpec(TypedDict, total=False):
        name: Required[str]
        port: Required[int]
        protocol: Required[Protocol]
        target_port: NotRequired[int]

    class ExternalListenerSpec(_ListenerSpec):
        external_address_spec: Required[ExternalAddressSpec]

    class InternalListenerSpec(_ListenerSpec):
        internal_address_spec: Required[InternalAddressSpec]

    class TcpOptions(TypedDict):
        port: int

    class HttpOptions(TcpOptions, total=False):
        path: NotRequired[str]

    class _HealthCheck(TypedDict, total=False):
        name: Required[str]
        interval: NotRequired[Duration]
        timeout: NotRequired[Duration]
        unhealthy_threshold: Required[int]
        healthy_threshold: Required[int]

    H = TypeVar('H', bound=_HealthCheck)
    HealthCheckList = List[H]

    class TcpHealthCheck(_HealthCheck):
        tcp_options: Required[TcpOptions]

    class HttpHealthCheck(_HealthCheck):
        http_options: Required[HttpOptions]

    class AttachedTargetGroup(TypedDict, total=False):
        target_group_id: Required[str]
        health_checks: Required[
            HealthCheckList[TcpHealthCheck] | HealthCheckList[HttpHealthCheck]
        ]


@overload
def is_health_check_list(
    val: list[TcpHealthCheck],
) -> TypeGuard[HealthCheckList[TcpHealthCheck]]:
    ...


@overload
def is_health_check_list(
    val: list[HttpHealthCheck],
) -> TypeGuard[HealthCheckList[HttpHealthCheck]]:
    ...


def is_health_check_list(
    val: list[TcpHealthCheck] | list[HttpHealthCheck],
) -> TypeGuard[HealthCheckList[TcpHealthCheck]] | TypeGuard[
    HealthCheckList[HttpHealthCheck]
]:
    return len(val) == 1


def validate_attached_target_group(
    module: AnsibleModule,
    group: AttachedTargetGroup,
) -> None:
    if not is_health_check_list(group['health_checks']):
        module.fail_json('health_checks: the number of elements must be exactly 1')


def create(
    client: NetworkLoadBalancerServiceStub,
    *,
    folder_id: str,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
    region_id: str | None = None,
    type: NetworkLoadBalancerType = 'EXTERNAL',
    listener_specs: list[InternalListenerSpec]
    | list[ExternalListenerSpec]
    | None = None,
    attached_target_groups: list[AttachedTargetGroup] | None = None,
):
    return {
        'CreateNetworkLoadBalancer': MessageToDict(
            client.Create(
                CreateNetworkLoadBalancerRequest(
                    folder_id=folder_id,
                    description=description,
                    labels=labels,
                    region_id=region_id,
                    type=type,
                    listener_specs=listener_specs,
                    attached_target_groups=attached_target_groups,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def main():
    argument_spec = default_arg_spec()
    argument_spec.update(
        {
            'folder_id': {'type': 'str'},
            'network_load_balancer_id': {'type': 'str'},
            'name': {'type': 'str'},
            'description': {'type': 'str'},
            'labels': {'type': 'dict', 'elements': 'str'},
            'region_id': {'type': 'str'},
            'type': {'type': 'str', 'default': 'EXTERNAL'},
            'listener_specs': {
                'type': 'list',
                'options': {
                    'name': {'type': 'str', 'required': True},
                    'port': {'type': 'str', 'required': True},
                    'protocol': {'type': 'str', 'required': True},
                    'target_port': {'type': 'str'},
                    'external_address_spec': {
                        'type': 'dict',
                        'options': {
                            'address': {'type': 'str', 'required': True},
                            'ip_version': {'type': 'str', 'required': True},
                        },
                    },
                    'internal_address_spec': {
                        'type': 'dict',
                        'options': {
                            'address': {'type': 'str', 'required': True},
                            'ip_version': {'type': 'str', 'required': True},
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
    sdk = init_sdk(module)
    nlb_service = sdk.client(NetworkLoadBalancerServiceStub)

    result = {}
    changed = False
    folder_id = module.params.get('folder_id')
    attached_target_groups: list[AttachedTargetGroup] = module.params.get(
        'attached_target_groups',
    )
    if attached_target_groups:
        for g in attached_target_groups:
            validate_attached_target_group(module, g)

    with log_grpc_error(module):
        result.update(
            create(
                nlb_service,
                folder_id=folder_id,
                description=module.params.get('description'),
                labels=module.params.get('labels'),
                region_id=module.params.get('region_id'),
                type=module.params.get('type'),
                listener_specs=module.params.get('listener_specs'),
                attached_target_groups=module.params.get('attached_target_groups'),
            ),
        )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
