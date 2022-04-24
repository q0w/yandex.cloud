# TODO: SetTag
# TODO: RemoveTag
from __future__ import annotations

from typing import Any

from google.protobuf.json_format import MessageToDict

from ..module_utils.basic import (
    get_base_arg_spec,
    get_base_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import (
    get_function_by_name,
    list_function_versions_by_function,
)

try:
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
) -> dict[str, dict[str, Any]]:
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
) -> dict[str, dict[str, Any]]:
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
    argument_spec = get_base_arg_spec()
    required_if = get_base_required_if()
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

    result: dict[str, Any] = {}
    state = module.params.get('state')
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    tag = module.params.get('tag')
    function_version_id = module.params.get('function_version_id')

    if not function_version_id:
        if function_id:
            versions = list_function_versions_by_function(
                function_service,
                function_id=function_id,
            ).get('versions', [])
        else:
            # FIXME: Use filter by Function.name in ListVersions
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
    elif state == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_tag(
                    function_service,
                    function_version_id=function_version_id,
                    tag=tag,
                ),
            )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
