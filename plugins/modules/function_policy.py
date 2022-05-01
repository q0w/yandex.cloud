from __future__ import annotations

from typing import Any

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import get_function_by_name

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        RemoveScalingPolicyRequest,
        SetScalingPolicyRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


def set_scaling_policy(
    client: FunctionServiceStub,
    *,
    function_id: str,
    tag: str,
    provisioned_instances_count: int | None = None,
    zone_instances_limit: int | None = None,
    zone_requests_limit: int | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'SetScalingPolicy': MessageToDict(
            client.SetScalingPolicy(
                SetScalingPolicyRequest(
                    function_id=function_id,
                    tag=tag,
                    provisioned_instances_count=provisioned_instances_count,
                    zone_instances_limit=zone_instances_limit,
                    zone_requests_limit=zone_requests_limit,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def remove_scaling_policy(
    client: FunctionServiceStub,
    *,
    function_id: str,
    tag: str,
) -> dict[str, dict[str, Any]]:
    return {
        'RemoveScalingPolicy': MessageToDict(
            client.RemoveScalingPolicy(
                RemoveScalingPolicyRequest(
                    function_id=function_id,
                    tag=tag,
                ),
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
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'tag': {'type': 'str', 'required': True},
            'provisioned_instances_count': {'type': 'int'},
            'zone_instances_limit': {'type': 'int'},
            'zone_requests_limit': {'type': 'int'},
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        },
    )

    required_one_of = [
        ('function_id', 'name'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=required_one_of,
        required_by=required_by,
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)

    result: dict[str, Any] = {}
    changed = False
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    tag = module.params.get('tag')
    provisioned_instances_count = module.params.get('provisioned_instances_count')
    zone_instances_limit = module.params.get('zone_instances_limit')
    zone_requests_limit = module.params.get('zone_requests_limit')

    if not function_id and folder_id and name:
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if not curr_function:
            module.fail_json(msg=f'function {name} not found')
            # FIXME: add stubs
            raise AssertionError('unreachable')
        function_id = curr_function.get('id')

    if module.params.get('state') == 'present':
        with log_grpc_error(module):
            result.update(
                set_scaling_policy(
                    function_service,
                    function_id=function_id,
                    tag=tag,
                    provisioned_instances_count=provisioned_instances_count,
                    zone_instances_limit=zone_instances_limit,
                    zone_requests_limit=zone_requests_limit,
                ),
            )
        changed = True
    elif module.params.get('state') == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_scaling_policy(
                    function_service,
                    function_id=function_id,
                    tag=tag,
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
