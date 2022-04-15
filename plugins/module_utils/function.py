from __future__ import annotations

from typing import cast
from typing import TYPE_CHECKING
from typing import TypedDict

import grpc
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    GetFunctionRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    ListFunctionsRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
    FunctionServiceStub,
)

from ..module_utils.protobuf import protobuf_to_dict

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

    class ListFunctionParams(TypedDict, total=False):
        folder_id: Required[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]


class GetFunctionParams(TypedDict, total=False):
    folder_id: str
    function_id: str
    name: str


class Timestamp(TypedDict, total=False):
    seconds: int
    nanos: int


class Metadata(TypedDict):
    type_url: str
    value: bytes


class Function(TypedDict, total=False):
    id: str
    folder_id: str
    created_at: Timestamp
    name: str
    description: str
    labels: dict[str, str]
    log_group_id: str
    http_invoke_url: str
    status: int


# TODO: add 'next_page_token'
class ListFunctionsResponse(TypedDict, total=False):
    functions: list[Function]


def list_functions(
    client: FunctionServiceStub,
    **kwargs: Unpack[ListFunctionParams],
) -> ListFunctionsResponse:
    return cast(
        ListFunctionsResponse,
        protobuf_to_dict(client.List(ListFunctionsRequest(**kwargs))),
    )


def _get_function_by_id(
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


def _get_function_by_name(
    client: FunctionServiceStub,
    folder_id: str,
    name: str,
) -> Function | None:
    fs = list_functions(
        client,
        folder_id=folder_id,
        filter=f'name="{name}"',
    )
    if fs and 'functions' in fs:
        func = fs['functions'][0]
    else:
        func = None
    return func


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
    else:
        return None
