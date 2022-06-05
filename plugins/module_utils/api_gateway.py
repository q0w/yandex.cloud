from __future__ import annotations

from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2 import ListApiGatewayRequest
from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import ApiGatewayServiceStub

from ..module_utils.basic import NotFound


def get_api_gateway_id(client: ApiGatewayServiceStub, folder_id: str, name: str) -> str:
    # get the latest api_gateway
    ags = client.List(ListApiGatewayRequest(folder_id=folder_id, filter=f'name="{name}"')).api_gateways
    if not ags:
        raise NotFound(f'function {name} not found')
    return ags[0].id
