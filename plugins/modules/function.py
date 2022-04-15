from __future__ import annotations

from typing import cast
from typing import Mapping
from typing import TYPE_CHECKING
from typing import TypedDict

from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.function import get_function
from ..module_utils.function import init_module
from ..module_utils.function import Metadata
from ..module_utils.function import Timestamp
from ..module_utils.protobuf import protobuf_to_dict

try:
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

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

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


# TODO: add 'done', 'result', 'error'
class Operation(TypedDict, total=False):
    id: str
    description: str
    created_at: Timestamp
    created_by: str
    modified_at: Timestamp
    metadata: Metadata
    response: Metadata


def delete_function(
    client: FunctionServiceStub,
    function_id: str,
) -> Operation:
    return cast(
        Operation,
        protobuf_to_dict(
            client.Delete(DeleteFunctionRequest(function_id=function_id)),
        ),
    )


def create_function(
    client: FunctionServiceStub,
    **kwargs: Unpack[CreateFunctionParams],
) -> Operation:
    return cast(
        Operation,
        protobuf_to_dict(client.Create(CreateFunctionRequest(**kwargs))),
    )


def update_function(
    client: FunctionServiceStub,
    **kwargs: Unpack[UpdateFunctionParams],
) -> Operation:
    return cast(
        Operation,
        protobuf_to_dict(client.Update(UpdateFunctionRequest(**kwargs))),
    )


# TODO: GetVersion
# TODO: GetVersionByTag
# TODO: ListVersions
# TODO: SetTag
# TODO: RemoveTag
# TODO: ListTagHistory
# TODO: CreateVersion
# TODO: ListRuntimes
# TODO: ListOperations
# TODO: ListAccessBindings
# TODO: SetAccessBindings
# TODO: UpdateAccessBindings
# TODO: ListScalingPolicies
# TODO: SetScalingPolicy
# TODO: RemoveScalingPolicy
def main() -> None:
    # TODO: NoReturn
    # TODO: manipulate "changed" state after success
    # TODO: check_mode
    argument_spec = dict(
        description=dict(type='str'),
        state=dict(
            type='str',
            default='present',
            choices=['present', 'absent'],
        ),
    )

    module = init_module(argument_spec=argument_spec)
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)
    result = {}

    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    curr_function = log_grpc_error(module)(get_function)(
        function_service,
        function_id=function_id,
        folder_id=folder_id,
        name=name,
    )

    if module.params.get('state') == 'present':
        if curr_function:
            resp = log_grpc_error(module)(update_function)(
                function_service,
                function_id=curr_function.get('id')
                or module.params.get('function_id'),
                # TODO: 'update_mask'
                name=module.params.get('name'),
                description=module.params.get('description'),
                labels=module.params.get('labels'),
            )
            # TODO: Fix decoding bytes for json.dumps
            resp.pop('metadata')
            resp.pop('response')
            result['UpdateFunction'] = resp
        else:
            result['CreateFunction'] = log_grpc_error(module)(create_function)(
                function_service,
                folder_id=module.params.get('folder_id'),
                name=module.params.get('name'),
            )

    elif module.params.get('state') == 'absent' and curr_function is not None:
        result['DeleteFunction'] = log_grpc_error(module)(delete_function)(
            function_service,
            curr_function.get('id') or module.params.get('function_id'),
        )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
