from __future__ import annotations

from typing import Callable, NoReturn, cast

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import (
    get_function_by_name,
    list_function_versions_by_function,
)
from ..module_utils.types import OperationResult

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        RemoveFunctionTagRequest,
        SetFunctionTagRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


def set_tag(
    client: FunctionServiceStub,
    *,
    function_version_id: str,
    tag: str,
) -> OperationResult:
    return {
        'SetFunctionTag': MessageToDict(
            client.SetTag(
                SetFunctionTagRequest(
                    function_version_id=function_version_id,
                    tag=tag,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def remove_tag(
    client: FunctionServiceStub,
    *,
    function_version_id: str,
    tag: str,
) -> OperationResult:
    return {
        'RemoveFunctionTag': MessageToDict(
            client.RemoveTag(
                RemoveFunctionTagRequest(
                    function_version_id=function_version_id,
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
            'function_version_id': {'type': 'str'},
            'tag': {'type': 'str', 'required': True},
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        },
    )

    required_one_of = [
        ('function_version_id', 'function_id', 'name'),
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

    result = {}
    changed = False
    state = module.params.get('state')
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    tag = module.params.get('tag')
    function_version_id = module.params.get('function_version_id')

    if not function_version_id:
        if not function_id and folder_id and name:
            # FIXME: Use filter by Function.name in ListVersions
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

        with log_grpc_error(module):
            versions = list_function_versions_by_function(
                function_service,
                function_id=function_id,
            ).get('versions', [])
        if not versions:
            module.fail_json(msg=f'no versions for function {name}')
        function_version_id = versions[0].get('id')

    if state == 'present':
        with log_grpc_error(module):
            result.update(
                set_tag(
                    function_service,
                    function_version_id=function_version_id,
                    tag=tag,
                ),
            )
        changed = True
    elif state == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_tag(
                    function_service,
                    function_version_id=function_version_id,
                    tag=tag,
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
