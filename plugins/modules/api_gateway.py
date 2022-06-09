from __future__ import annotations

from contextlib import suppress
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_error
from ..module_utils.basic import log_grpc_error

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import CreateApiGatewayRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import DeleteApiGatewayRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import GetApiGatewayRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import ListApiGatewayRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import UpdateApiGatewayRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import ApiGatewayServiceStub


def main() -> NoReturn:
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
            'labels': {'type': 'dict'},
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
    client: ApiGatewayServiceStub = init_sdk(module).client(ApiGatewayServiceStub)
    result = {}

    state = module.params['state']
    ag_id = module.params['api_gateway_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    # TODO: accept raw json/yaml openapi_spec
    openapi_spec = module.params['openapi_spec']
    description = module.params['description']
    labels = module.params['labels']
    connectivity = module.params['connectivity']

    curr_ag = None
    with log_grpc_error(module):
        if ag_id:
            curr_ag = client.Get(GetApiGatewayRequest(api_gateway_id=ag_id))
        else:
            ags = client.List(ListApiGatewayRequest(folder_id=folder_id, filter=f'name="{name}"')).api_gateways
            if ags:
                curr_ag = ags[0]

    with log_grpc_error(module):
        if state == 'present':
            with log_error(module, FileNotFoundError), open(openapi_spec, encoding='utf-8') as f:
                openapi_spec = f.read()
            if curr_ag:
                resp = client.Update(
                    UpdateApiGatewayRequest(
                        api_gateway_id=curr_ag.id,
                        name=name,
                        description=description,
                        labels=labels,
                        connectivity=connectivity,
                        openapi_spec=openapi_spec,
                    ),
                )
                result.update(MessageToDict(resp))
            else:
                resp = client.Create(
                    CreateApiGatewayRequest(
                        folder_id=folder_id,
                        name=name,
                        description=description,
                        labels=labels,
                        connectivity=connectivity,
                        openapi_spec=openapi_spec,
                    ),
                )
                result.update(MessageToDict(resp))

        elif state == 'absent':
            if not curr_ag:
                module.fail_json(f'api gateway {ag_id or name} not found')
            resp = client.Delete(DeleteApiGatewayRequest(api_gateway_id=curr_ag.id))
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
