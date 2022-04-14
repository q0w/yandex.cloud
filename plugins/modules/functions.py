from __future__ import annotations

from typing import cast
from typing import Mapping
from typing import TYPE_CHECKING
from typing import TypedDict

import grpc

from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.protobuf import protobuf_to_dict

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionRequest,
        ListFunctionsRequest,
        GetFunctionRequest,
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

    class ListFunctionParams(TypedDict, total=False):
        folder_id: Required[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

    class UpdateFunctionParams(TypedDict, total=False):
        function_id: Required[str]
        # TODO: update_mask
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[Mapping[str, str]]


# TODO: rename
class Time(TypedDict):
    seconds: int
    nanos: int


class Metadata(TypedDict):
    type_url: str
    value: bytes


class Function(TypedDict, total=False):
    id: str
    folder_id: str
    created_at: Time
    name: str
    description: str
    labels: dict[str, str]
    log_group_id: str
    http_invoke_url: str
    status: int


# TODO: add 'done', 'result', 'error'
class Operation(TypedDict, total=False):
    id: str
    description: str
    created_at: Time
    created_by: str
    modified_at: Time
    metadata: Metadata
    response: Metadata


# TODO: add 'next_page_token'
class ListFunctionsResponse(TypedDict):
    functions: list[Function]


def get_function(
    client: FunctionServiceStub,
    function_id: str,
) -> Function | None:
    func = None
    try:
        res = client.Get(GetFunctionRequest(function_id=function_id))
    except grpc._channel._InactiveRpcError:
        return func
    else:
        return cast(Function, protobuf_to_dict(res))


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


def list_functions(
    client: FunctionServiceStub,
    **kwargs: Unpack[ListFunctionParams],
) -> ListFunctionsResponse:
    return cast(
        ListFunctionsResponse,
        protobuf_to_dict(client.List(ListFunctionsRequest(**kwargs))),
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


def main() -> None:
    # TODO: manipulate "changed" state after success
    argument_spec = dict(
        name=dict(
            type='str',
        ),
        description=dict(type='str'),
        function_id=dict(type='str'),
        state=dict(
            type='str',
            default='present',
            choices=['present', 'absent'],
        ),
        auth_kind=dict(
            type='str',
            choices=['oauth', 'sa_file'],
            required=True,
        ),
        oauth_token=dict(type='str'),
        sa_path=dict(type='str'),
        sa_content=dict(type='str'),
        folder_id=dict(type='str', required=True),
    )

    required_if = [
        (
            'auth_kind',
            'sa_file',
            ('sa_path', 'sa_content'),
            True,
        ),
    ]

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)
    result = {}

    function_id = module.params.get('function_id')
    name = module.params.get('name')
    curr_function = None

    if function_id:
        curr_function = get_function(
            function_service,
            function_id,
        )
    elif name:
        fs = log_grpc_error(module)(list_functions)(
            function_service,
            folder_id=module.params.get('folder_id'),
            filter=f'name="{name}"',
        )
        if fs and 'functions' in fs:
            curr_function = fs['functions'][0]

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
