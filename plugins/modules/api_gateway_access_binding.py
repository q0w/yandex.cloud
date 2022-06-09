from __future__ import annotations

from contextlib import suppress
from typing import NoReturn

from ..module_utils.api_gateway import get_api_gateway_id
from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_error
from ..module_utils.basic import log_grpc_error
from ..module_utils.basic import NotFound
from ..module_utils.resource import default_arg_spec as ab_default_arg_spec
from ..module_utils.resource import default_required_by
from ..module_utils.resource import default_required_one_of
from ..module_utils.resource import remove_access_bindings
from ..module_utils.resource import set_access_bindings
from ..module_utils.resource import to_ab

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import ApiGatewayServiceStub


def main() -> NoReturn:
    argument_spec = {**default_arg_spec(), **ab_default_arg_spec()}

    module = init_module(
        argument_spec=argument_spec,
        required_if=default_required_if(),
        required_one_of=default_required_one_of(),
        required_by=default_required_by(),
        supports_check_mode=True,
    )

    client: ApiGatewayServiceStub = init_sdk(module).client(ApiGatewayServiceStub)
    result = {}

    state = module.params['state']
    ag_id = module.params['api_gateway_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    abs = [to_ab(ab) for ab in module.params['access_bindings']]

    if not ag_id:
        with log_error(module, NotFound), log_grpc_error(module):
            ag_id = get_api_gateway_id(client, folder_id, name)

    with log_grpc_error(module):
        if state == 'present':
            resp = set_access_bindings(client, ag_id, abs)
            result['SetAccessBindings'] = MessageToDict(resp)
        elif state == 'absent':
            resp = remove_access_bindings(client, ag_id, abs)
            result['RemoveAccessBindings'] = MessageToDict(resp)

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
