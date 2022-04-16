from __future__ import annotations

from typing import Any
from typing import cast
from typing import Mapping
from typing import overload
from typing import TYPE_CHECKING
from typing import TypedDict

from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.function import get_function
from ..module_utils.function import Timestamp
from ..module_utils.protobuf import protobuf_to_dict

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        ListFunctionsVersionsRequest,
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

    class ListVersionsParams(TypedDict, total=False):
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

    class _ByFunctionId(ListVersionsParams):
        function_id: Required[str]

    class _ByFolderId(ListVersionsParams):
        folder_id: Required[str]


class Resources(TypedDict):
    memory: int


class Connectivity(TypedDict, total=False):
    network_id: str
    subnet_id: list[str]


# TODO: total=false ?
class Secret(TypedDict):
    id: str
    version_id: str
    key: str
    reference: str
    environment_variable: str


class FunctionVersion(TypedDict, total=False):
    id: str
    function_id: str
    description: str
    created_at: Timestamp
    runtime: str
    entrypoint: str
    resources: Resources
    execution_timeout: Timestamp
    service_account_id: str
    image_size: int
    status: int
    tags: list[str]
    log_group_id: str
    environment: Mapping[str, str]
    connectivity: Connectivity
    named_service_accounts: Mapping[str, str]
    secrets: list[Secret]


# TODO: add 'next_page_token'
class ListFunctionsVersionsResponse(TypedDict, total=False):
    versions: list[FunctionVersion]


def get_version(
    client: FunctionServiceStub,
    function_version_id: str,
) -> FunctionVersion:
    return cast(
        FunctionVersion,
        protobuf_to_dict(
            client.GetVersion(function_version_id=function_version_id),
        ),
    )


@overload
def list_function_versions(
    client: FunctionServiceStub,
    **kwargs: Unpack[_ByFolderId],
) -> ListFunctionsVersionsResponse:
    ...


@overload
def list_function_versions(
    client: FunctionServiceStub,
    **kwargs: Unpack[_ByFunctionId],
) -> ListFunctionsVersionsResponse:
    ...


# TODO: add page_size, page_token, filter
def list_function_versions(client, **kwargs):
    return cast(
        ListFunctionsVersionsResponse,
        protobuf_to_dict(
            client.ListVersions(ListFunctionsVersionsRequest(**kwargs)),
        ),
    )


def main():
    argument_spec = {
        'name': {'type': 'str'},
        'function_id': {'type': 'str'},
        'folder_id': {'type': 'str'},
    }
    required_one_of = [
        ('function_id', 'name', 'folder_id'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    module = init_module(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        required_by=required_by,
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)

    result: dict[str, Any] = {}
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    if function_id:
        with log_grpc_error(module):
            result['ListFunctionsVersions'] = list_function_versions(
                function_service,
                function_id=function_id,
            )
    elif name and folder_id:
        # FIXME: somehow filter by name does not work
        # FIXME: workaround: filter functions by name using ListFunctions
        with log_grpc_error(module):
            curr_function = get_function(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if curr_function:
            with log_grpc_error(module):
                result['ListFunctionsVersions'] = list_function_versions(
                    function_service,
                    function_id=curr_function.get('id'),
                )
    elif folder_id:
        with log_grpc_error(module):
            result['ListFunctionsVersions'] = list_function_versions(
                function_service,
                folder_id=folder_id,
            )

    result['changed'] = False
    if module.check_mode:
        result['msg'] = 'Check mode set but ignored for fact gathering only.'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
