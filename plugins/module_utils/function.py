from __future__ import annotations

from typing import cast
from typing import TYPE_CHECKING
from typing import TypedDict

import grpc
from google.protobuf.json_format import MessageToDict
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    GetFunctionRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    ListFunctionsRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
    FunctionServiceStub,
)

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

    class ListFunctionParams(TypedDict, total=False):
        folder_id: Required[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

    class Function(TypedDict, total=False):
        id: Required[str]
        folder_id: Required[str]
        created_at: Required[str]
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[dict[str, str]]
        log_group_id: Required[str]
        http_invoke_url: Required[str]
        status: Required[str]

    class ScalingPolicy(TypedDict, total=False):
        function_id: Required[str]
        tag: Required[str]
        created_at: NotRequired[str]
        modified_at: NotRequired[str]
        provisioned_instances_count: NotRequired[str]
        zone_instances_limit: NotRequired[str]
        zone_requests_limit: NotRequired[str]

    _Metadata = TypedDict('_Metadata', {'@type': str})

    class FunctionMetadata(_Metadata):
        function_id: str

    # TODO: add 'done', 'result', 'error'
    class _Operation(TypedDict, total=False):
        id: str
        description: NotRequired[str]
        created_at: Required[str]
        created_by: Required[str]
        modified_at: Required[str]
        done: NotRequired[bool]
        metadata: Required[FunctionMetadata]


class GetFunctionParams(TypedDict, total=False):
    folder_id: str
    function_id: str
    name: str


# TODO: add 'next_page_token'
class ListFunctionsResponse(TypedDict, total=False):
    functions: list[Function]


def list_functions(
    client: FunctionServiceStub,
    **kwargs: Unpack[ListFunctionParams],
) -> ListFunctionsResponse:
    return cast(
        ListFunctionsResponse,
        MessageToDict(
            client.List(ListFunctionsRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    )


def _get_function_by_id(
    client: FunctionServiceStub,
    function_id: str,
) -> Function | None:
    try:
        res = client.Get(GetFunctionRequest(function_id=function_id))
    except grpc.RpcError:
        return None
    return cast(
        'Function',
        MessageToDict(res, preserving_proto_field_name=True),
    )


def _get_function_by_name(
    client: FunctionServiceStub,
    folder_id: str,
    name: str,
) -> Function | None:
    fs = list_functions(
        client,
        folder_id=folder_id,
        filter=f'name="{name}"',
    ).get('functions')
    return fs[0] if fs else None


def get_function(
    client: FunctionServiceStub,
    **kwargs: Unpack[GetFunctionParams],
) -> Function | None:
    function_id = kwargs.get('function_id')
    folder_id = kwargs.get('folder_id')
    name = kwargs.get('name')

    if function_id:
        return _get_function_by_id(client, function_id)
    elif folder_id and name:
        return _get_function_by_name(client, folder_id, name)
    return None
