from __future__ import annotations

from typing import Callable, NoReturn, cast

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import get_function_by_name
from ..module_utils.resource import default_arg_spec as ab_default_arg_spec
from ..module_utils.resource import (
    default_required_by,
    default_required_one_of,
    remove_access_bindings,
    set_access_bindings,
)

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


def main():
    argument_spec = {**default_arg_spec(), **ab_default_arg_spec()}
    required_if = default_required_if()

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=default_required_one_of(),
        required_by=default_required_by(),
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)

    result = {}
    changed = False
    state = module.params.get('state')
    function_id = module.params.get('resource_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    access_bindings = module.params.get('access_bindings')

    if not function_id and folder_id and name:
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if not curr_function:
            cast(Callable[..., NoReturn], module.fail_json)(
                msg=f'function {name} not found',
            )
        function_id = curr_function.get('id')

    if state == 'present':
        with log_grpc_error(module):
            result.update(
                set_access_bindings(
                    function_service,
                    resource_id=function_id,
                    access_bindings=access_bindings,
                ),
            )
        changed = True
    elif state == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_access_bindings(
                    function_service,
                    resource_id=function_id,
                    access_bindings=access_bindings,
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
