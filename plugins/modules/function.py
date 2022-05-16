from __future__ import annotations

from typing import Mapping

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import get_function_by_id, get_function_by_name
from ..module_utils.types import OperationResult

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionRequest,
        DeleteFunctionRequest,
        UpdateFunctionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


def delete_function(
    client: FunctionServiceStub,
    function_id: str,
) -> OperationResult:
    return {
        'DeleteFunction': MessageToDict(
            client.Delete(DeleteFunctionRequest(function_id=function_id)),
            preserving_proto_field_name=True,
        ),
    }


def create_function(
    client: FunctionServiceStub,
    *,
    folder_id: str,
    name: str | None = None,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
) -> OperationResult:
    return {
        'CreateFunction': MessageToDict(
            client.Create(
                CreateFunctionRequest(
                    folder_id=folder_id,
                    name=name,
                    description=description,
                    labels=labels,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


# TODO: add update_mask
def update_function(
    client: FunctionServiceStub,
    *,
    function_id: str,
    name: str | None = None,
    description: str | None = None,
    labels: Mapping[str, str] | None = None,
) -> OperationResult:
    return {
        'UpdateFunction': MessageToDict(
            client.Update(
                UpdateFunctionRequest(
                    function_id=function_id,
                    name=name,
                    description=description,
                    labels=labels,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


def main() -> None:
    # TODO: NoReturn
    # TODO: manipulate "changed" state after success
    # TODO: check_mode
    # TODO: add arg_spec labels, update_mask
    argument_spec = default_arg_spec()
    required_if = default_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'description': {'type': 'str'},
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
    required_together = [
        ('name', 'folder_id'),
    ]

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=required_one_of,
        required_together=required_together,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)
    result = {}

    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    with log_grpc_error(module):
        curr_function = get_function_by_id(
            function_service,
            function_id=function_id,
        ) or get_function_by_name(
            function_service,
            folder_id=folder_id,
            name=name,
        )

    if module.params.get('state') == 'present':
        if curr_function:
            with log_grpc_error(module):
                resp = update_function(
                    function_service,
                    function_id=curr_function.get('id')
                    or module.params.get('function_id'),
                    # TODO: 'update_mask'
                    name=module.params.get('name'),
                    description=module.params.get('description'),
                    labels=module.params.get('labels'),
                )
        else:
            with log_grpc_error(module):
                resp = create_function(
                    function_service,
                    folder_id=module.params.get('folder_id'),
                    name=module.params.get('name'),
                )
        result.update(resp)

    elif module.params.get('state') == 'absent' and curr_function is not None:
        with log_grpc_error(module):
            resp = delete_function(
                function_service,
                curr_function.get('id') or module.params.get('function_id'),
            )
        result.update(resp)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
