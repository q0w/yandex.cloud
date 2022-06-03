from __future__ import annotations

from contextlib import suppress

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.resource import default_arg_spec as ab_default_arg_spec
from ..module_utils.resource import (
    default_required_by,
    default_required_one_of,
    get_resource_by_name,
    remove_access_bindings,
    set_access_bindings,
)

with suppress(ImportError):
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import (
        ListApiGatewayRequest,
    )
    from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import (
        ApiGatewayServiceStub,
    )


def main():
    argument_spec = {**default_arg_spec(), **ab_default_arg_spec()}

    module = init_module(
        argument_spec=argument_spec,
        required_if=default_required_if(),
        required_one_of=default_required_one_of(),
        required_by=default_required_by(),
        supports_check_mode=True,
    )

    gateway_service = init_sdk(module).client(ApiGatewayServiceStub)

    result = {}
    changed = False

    if (
        not module.params['api_gateway_id']
        and module.params['folder_id']
        and module.params['name']
    ):
        with log_grpc_error(module):
            api_gateway = get_resource_by_name(
                gateway_service,
                ListApiGatewayRequest,
                folder_id=module.params['folder_id'],
                name=module.params['name'],
            )
        if not api_gateway:
            module.fail_json(f'Api gateway {module.params["name"]} not found')
        module.params['api_gateway_id'] = api_gateway['id']

    if module.params['state'] == 'present':
        with log_grpc_error(module):
            result.update(
                set_access_bindings(
                    gateway_service,
                    resource_id=module.params['api_gateway_id'],
                    access_bindings=module.params['access_bindings'],
                ),
            )
        changed = True
    elif module.params['state'] == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_access_bindings(
                    gateway_service,
                    resource_id=module.params['api_gateway_id'],
                    access_bindings=module.params['access_bindings'],
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
