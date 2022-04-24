from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict, cast

import grpc
from google.protobuf.json_format import MessageToDict
from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
    GetFunctionRequest,
    ListFunctionsRequest,
    ListFunctionsVersionsRequest,
)
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
    FunctionServiceStub,
)

if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required

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


class ListFunctionsResponse(TypedDict, total=False):
    functions: list[Function]
    next_page_token: str


def list_functions(
    client: FunctionServiceStub,
    *,
    folder_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListFunctionsResponse:
    return cast(
        ListFunctionsResponse,
        MessageToDict(
            client.List(
                ListFunctionsRequest(
                    folder_id=folder_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    )


def get_function_by_id(
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


def get_function_by_name(
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


# TODO: page_size, page_token, filter
def list_function_versions_by_function(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> dict[str, Any]:
    return MessageToDict(
        client.ListVersions(
            ListFunctionsVersionsRequest(
                function_id=function_id,
                page_size=page_size,
                page_token=page_token,
                filter=filter,
            ),
        ),
        preserving_proto_field_name=True,
    )


# TODO: page_size, page_token
def list_function_versions_by_folder(
    client: FunctionServiceStub,
    *,
    folder_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> dict[str, Any]:
    return MessageToDict(
        client.ListVersions(
            ListFunctionsVersionsRequest(
                folder_id=folder_id,
                page_size=page_size,
                page_token=page_token,
                filter=filter,
            ),
        ),
        preserving_proto_field_name=True,
    )
