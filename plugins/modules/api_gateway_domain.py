from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NoReturn, cast

from ..module_utils.api_gateway import get_api_gateway_by_name
from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import (
        AddDomainRequest,
        RemoveDomainRequest,
    )
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import (
        ApiGatewayServiceStub,
    )
except ImportError:
    pass

if TYPE_CHECKING:
    from ..module_utils.typedefs import OperationResult


def add_domain(
    client: ApiGatewayServiceStub,
    *,
    api_gateway_id: str,
    domain_id: str,
) -> OperationResult:
    return {
        'AddDomain': MessageToDict(
            client.AddDomain(
                AddDomainRequest(api_gateway_id=api_gateway_id, domain_id=domain_id),
            ),
            preserving_proto_field_name=True,
        ),
    }


def remove_domain(
    client: ApiGatewayServiceStub,
    *,
    api_gateway_id: str,
    domain_id: str,
) -> OperationResult:
    return {
        'RemoveDomain': MessageToDict(
            client.RemoveDomain(
                RemoveDomainRequest(api_gateway_id=api_gateway_id, domain_id=domain_id),
            ),
            preserving_proto_field_name=True,
        ),
    }


def main():
    argument_spec = default_arg_spec()
    required_if = default_required_if()

    argument_spec.update(
        {
            'name': {'type': 'str'},
            'api_gateway_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'domain_id': {'type': 'str', 'required': True},
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        },
    )

    required_one_of = [
        ('api_gateway_id', 'name'),
    ]

    required_together = [
        ('name', 'folder_id'),
    ]

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=required_one_of,
        required_together=required_together,
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    gateway_service = sdk.client(ApiGatewayServiceStub)

    result = {}
    api_gateway_id = module.params.get('api_gateway_id')
    domain_id = module.params.get('domain_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    changed = False
    state = module.params.get('state')

    if not api_gateway_id and folder_id and name:
        with log_grpc_error(module):
            api_gateway = get_api_gateway_by_name(
                gateway_service,
                folder_id=folder_id,
                name=name,
            )
        if not api_gateway:
            cast(Callable[..., NoReturn], module.fail_json)(
                msg=f'Api gateway {name} not found',
            )
        api_gateway_id = api_gateway.get('id')

    if state == 'present':
        with log_grpc_error(module):
            result.update(
                add_domain(
                    gateway_service,
                    api_gateway_id=api_gateway_id,
                    domain_id=domain_id,
                ),
            )
        changed = True
    elif state == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_domain(
                    gateway_service,
                    api_gateway_id=api_gateway_id,
                    domain_id=domain_id,
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
