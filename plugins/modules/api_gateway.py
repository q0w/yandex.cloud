from __future__ import annotations

from typing import Any, Callable, Mapping, NoReturn, cast

from ..module_utils.api_gateway import get_api_gateway_by_id, get_api_gateway_by_name
from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_error,
    log_grpc_error,
)
from ..module_utils.typedefs import Connectivity

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import (
        CreateApiGatewayRequest,
        DeleteApiGatewayRequest,
        UpdateApiGatewayRequest,
    )
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import (
        ApiGatewayServiceStub,
    )
except ImportError:
    pass


# TODO: accept raw json/yaml openapi_spec
def create_api_gateway(
    client: ApiGatewayServiceStub,
    *,
    folder_id: str,
    name: str | None = None,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
    openapi_spec: str,
    connectivity: Connectivity | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'CreateApiGateway': MessageToDict(
            client.Create(
                CreateApiGatewayRequest(
                    folder_id=folder_id,
                    name=name,
                    description=description,
                    labels=labels,
                    openapi_spec=openapi_spec,
                    connectivity=connectivity,
                ),
            ),
        ),
    }


# TODO: accept raw json/yaml openapi_spec
# TODO: update_mask
def update_api_gateway(
    client: ApiGatewayServiceStub,
    *,
    api_gateway_id: str,
    name: str | None,
    description: str | None,
    labels: Mapping[str, str] | None = None,
    openapi_spec: str | None = None,
    connectivity: Connectivity | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'UpdateApiGateway': MessageToDict(
            client.Update(
                UpdateApiGatewayRequest(
                    api_gateway_id=api_gateway_id,
                    name=name,
                    description=description,
                    labels=labels,
                    openapi_spec=openapi_spec,
                    connectivity=connectivity,
                ),
            ),
        ),
    }


def delete_api_gateway(
    client: ApiGatewayServiceStub,
    api_gateway_id: str,
) -> dict[str, dict[str, Any]]:
    return {
        'DeleteApiGateway': MessageToDict(
            client.Delete(DeleteApiGatewayRequest(api_gateway_id=api_gateway_id)),
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
            'description': {'type': 'str'},
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
            'openapi_spec': {'type': 'str'},
            'labels': {'type': 'dict', 'elements': 'str'},
            'connectivity': {
                'type': 'dict',
                'options': {
                    'network_id': {'type': 'str', 'required': True},
                    'subnet_id': {'type': 'list', 'elements': 'str', 'required': True},
                },
            },
        },
    )

    required_if.append(
        ('state', 'present', ('openapi_spec',), False),
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

    result: dict[str, Any] = {}
    api_gateway_id = module.params.get('api_gateway_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    changed = False
    state = module.params.get('state')

    with log_grpc_error(module):
        curr_api_gateway = get_api_gateway_by_id(
            gateway_service,
            api_gateway_id,
        ) or get_api_gateway_by_name(gateway_service, folder_id, name)

    if state == 'present':
        with log_error(module), open(
            module.params.get('openapi_spec'),
            encoding='utf-8',
        ) as f:
            openapi_spec = f.read()
        if not curr_api_gateway:
            with log_grpc_error(module):
                result.update(
                    create_api_gateway(
                        client=gateway_service,
                        folder_id=folder_id,
                        name=name,
                        description=module.params.get('description'),
                        labels=module.params.get('labels'),
                        connectivity=module.params.get('connectivity'),
                        openapi_spec=openapi_spec,
                    ),
                )
        else:
            with log_grpc_error(module):
                result.update(
                    update_api_gateway(
                        client=gateway_service,
                        api_gateway_id=curr_api_gateway['id'],
                        name=name,
                        description=module.params.get('description'),
                        labels=module.params.get('labels'),
                        connectivity=module.params.get('connectivity'),
                        openapi_spec=openapi_spec,
                    ),
                )
        changed = True
    elif state == 'absent':
        if not curr_api_gateway:
            cast(Callable[..., NoReturn], module.fail_json)(
                msg=f'api gateway {api_gateway_id or name} not found',
            )
        with log_grpc_error(module):
            delete_api_gateway(gateway_service, curr_api_gateway['id'])
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
