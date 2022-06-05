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
from ..module_utils.function import get_function_id
from ..module_utils.resource import default_arg_spec as ab_default_arg_spec
from ..module_utils.resource import default_required_by
from ..module_utils.resource import default_required_one_of
from ..module_utils.resource import remove_access_bindings
from ..module_utils.resource import set_access_bindings
from ..module_utils.resource import to_ab

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub


def main() -> NoReturn:
    argument_spec = {**default_arg_spec(), **ab_default_arg_spec()}
    required_if = default_required_if()

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=default_required_one_of(),
        required_by=default_required_by(),
        supports_check_mode=True,
    )
    client: FunctionServiceStub = init_sdk(module).client(FunctionServiceStub)
    result = {}

    state = module.params['state']
    function_id = module.params['function_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    abs = [to_ab(ab) for ab in module.params['access_bindings']]

    if not function_id:
        with log_error(module, NotFound), log_grpc_error(module):
            function_id = get_function_id(client, folder_id, name)

    with log_grpc_error(module):
        if state == 'present':
            resp = set_access_bindings(client, function_id, abs)
            result.update(MessageToDict(resp))
        elif state == 'absent':
            resp = remove_access_bindings(client, function_id, abs)
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
