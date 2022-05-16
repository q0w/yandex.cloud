from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, TypedDict, cast

import grpc
from google.protobuf.json_format import MessageToDict
from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import (
    GetApiGatewayRequest,
    ListApiGatewayRequest,
)
from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import (
    ApiGatewayServiceStub,
)

if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required

    from ..module_utils.typedefs import Connectivity

    class ApiGateway(TypedDict, total=False):
        id: Required[str]
        folder_id: Required[str]
        created_at: Required[str]
        name: NotRequired[str]
        description: NotRequired[str]
        labels: NotRequired[Mapping[str, str]]
        status: Required[str]
        domain: Required[str]
        log_group_id: Required[str]
        attached_domains: NotRequired[list[Mapping[str, str | bool]]]
        connectivity: NotRequired[Connectivity]


class ListApiGatewayResponse(TypedDict, total=False):
    api_gateways: list[ApiGateway]
    next_page_token: str


def list_api_gateways(
    client: ApiGatewayServiceStub,
    *,
    folder_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListApiGatewayResponse:
    return cast(
        ListApiGatewayResponse,
        MessageToDict(
            client.List(
                ListApiGatewayRequest(
                    folder_id=folder_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    )


def get_api_gateway_by_id(
    client: ApiGatewayServiceStub,
    id: str,
) -> ApiGateway | None:
    try:
        res = client.Get(GetApiGatewayRequest(api_gateway_id=id))
    except grpc.RpcError:
        return None
    return cast(
        'ApiGateway',
        MessageToDict(res, preserving_proto_field_name=True),
    )


def get_api_gateway_by_name(
    client: ApiGatewayServiceStub,
    folder_id: str,
    name: str,
) -> ApiGateway | None:
    fs = list_api_gateways(
        client,
        folder_id=folder_id,
        filter=f'name="{name}"',
    ).get('api_gateways')
    return fs[0] if fs else None
