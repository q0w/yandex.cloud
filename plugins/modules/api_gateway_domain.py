from __future__ import annotations

from contextlib import suppress
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_error
from ..module_utils.basic import log_grpc_error
from ..module_utils.basic import NotFound

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from module_utils.api_gateway import get_api_gateway_id
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import AddDomainRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import RemoveDomainRequest
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import ApiGatewayServiceStub


def main() -> NoReturn:
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
    client: ApiGatewayServiceStub = init_sdk(module).client(ApiGatewayServiceStub)
    result = {}

    state = module.params['state']
    ag_id = module.params['api_gateway_id']
    domain_id = module.params['domain_id']
    folder_id = module.params['folder_id']
    name = module.params['name']

    if not ag_id:
        with log_error(module, NotFound), log_grpc_error(module):
            ag_id = get_api_gateway_id(client, folder_id, name)

    with log_grpc_error(module):
        if state == 'present':
            resp = client.AddDomain(AddDomainRequest(api_gateway_id=ag_id, domain_id=domain_id))
            result.update(MessageToDict(resp))

        elif state == 'absent':
            resp = client.RemoveDomain(RemoveDomainRequest(api_gateway_id=ag_id, domain_id=domain_id))
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
