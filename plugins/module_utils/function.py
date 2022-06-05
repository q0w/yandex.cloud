from __future__ import annotations

from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionsRequest
from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionsVersionsRequest
from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub

from ..module_utils.basic import NotFound


def get_function_id(client: FunctionServiceStub, folder_id: str, name: str) -> str:
    # get the latest function
    functions = client.List(ListFunctionsRequest(folder_id=folder_id, filter=f'name="{name}"')).functions
    if not functions:
        raise NotFound(f'function {name} not found')
    return functions[0].id


def get_function_version_id(client, function_id) -> str:
    # get latest version
    versions = client.ListVersions(ListFunctionsVersionsRequest(function_id=function_id)).versions
    if not versions:
        raise NotFound(f'no versions for function {function_id}')
    return versions[0].id
