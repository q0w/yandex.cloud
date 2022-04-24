from __future__ import annotations

from typing import cast
from typing import Mapping
from typing import TYPE_CHECKING
from typing import TypedDict

from ..module_utils.basic import get_base_arg_spec
from ..module_utils.basic import get_base_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.function import get_function

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionRequest,
        DeleteFunctionRequest,
        UpdateFunctionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
    from google.protobuf.json_format import MessageToDict
except ImportError:
    pass

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

    from ..module_utils.function import _Operation
    from ..module_utils.function import _Metadata
    from ..module_utils.function import Function

    class CreateFunctionParams(TypedDict, total=False):
        folder_id: Required[str]
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[Mapping[str, str]]

    class UpdateFunctionParams(TypedDict, total=False):
        function_id: Required[str]
        # TODO: update_mask
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[Mapping[str, str]]

    class FunctionOperationResponse(_Metadata, Function):
        ...

    class FunctionOperation(_Operation):
        response: NotRequired[FunctionOperationResponse]


def delete_function(
    client: FunctionServiceStub,
    function_id: str,
) -> FunctionOperation:
    return cast(
        'FunctionOperation',
        MessageToDict(
            client.Delete(DeleteFunctionRequest(function_id=function_id)),
            preserving_proto_field_name=True,
        ),
    )


def create_function(
    client: FunctionServiceStub,
    **kwargs: Unpack[CreateFunctionParams],
) -> FunctionOperation:
    return cast(
        'FunctionOperation',
        MessageToDict(
            client.Create(CreateFunctionRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    )


def update_function(
    client: FunctionServiceStub,
    **kwargs: Unpack[UpdateFunctionParams],
) -> FunctionOperation:
    return cast(
        'FunctionOperation',
        MessageToDict(
            client.Update(UpdateFunctionRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    )


# TODO: GetVersion
# TODO: GetVersionByTag
# TODO: SetTag
# TODO: RemoveTag
# TODO: ListTagHistory
# TODO: CreateVersion
# TODO: ListOperations
# TODO: ListAccessBindings
# TODO: SetAccessBindings
# TODO: UpdateAccessBindings
def main() -> None:
    # TODO: NoReturn
    # TODO: manipulate "changed" state after success
    # TODO: check_mode
    argument_spec = get_base_arg_spec()
    required_if = get_base_required_if()
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
        curr_function = get_function(
            function_service,
            function_id=function_id,
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
            result['UpdateFunction'] = resp
        else:
            with log_grpc_error(module):
                result['CreateFunction'] = create_function(
                    function_service,
                    folder_id=module.params.get('folder_id'),
                    name=module.params.get('name'),
                )

    elif module.params.get('state') == 'absent' and curr_function is not None:
        with log_grpc_error(module):
            result['DeleteFunction'] = delete_function(
                function_service,
                curr_function.get('id') or module.params.get('function_id'),
            )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
