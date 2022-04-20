from __future__ import annotations

from typing import Any
from typing import cast
from typing import Mapping
from typing import overload
from typing import TYPE_CHECKING
from typing import TypedDict

from google.protobuf.json_format import MessageToDict

from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.function import get_function

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        ListFunctionsVersionsRequest,
        ListScalingPoliciesRequest,
        GetFunctionVersionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass

if TYPE_CHECKING:
    from ..module_utils.function import ScalingPolicy
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

    class ListVersionsParams(TypedDict, total=False):
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

    # TODO: add 'next_page_token'
    class ListFunctionsVersionsResponse(TypedDict, total=False):
        versions: list[FunctionVersion]

    class ListScalingPoliciesParams(TypedDict, total=False):
        function_id: Required[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]

    class _ByFunctionId(ListVersionsParams):
        function_id: Required[str]

    class _ByFolderId(ListVersionsParams):
        folder_id: Required[str]

    class FunctionVersion(TypedDict, total=False):
        id: Required[str]
        function_id: Required[str]
        description: NotRequired[str]
        created_at: Required[str]
        runtime: Required[str]
        entrypoint: Required[str]
        resources: Required[Resources]
        execution_timeout: Required[str]
        service_account_id: Required[str]
        image_size: Required[str]
        status: Required[str]
        tags: Required[list[str]]
        log_group_id: Required[str]
        environment: NotRequired[Mapping[str, str]]
        connectivity: NotRequired[Connectivity]
        named_service_accounts: NotRequired[Mapping[str, str]]
        secrets: NotRequired[list[Secret]]


class Resources(TypedDict):
    memory: str


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


# TODO: add 'next_page_token: str'
class ListScalingPoliciesResponse(TypedDict, total=False):
    scaling_policies: list[ScalingPolicy]


def get_version(
    client: FunctionServiceStub,
    function_version_id: str,
) -> FunctionVersion:
    return cast(
        'FunctionVersion',
        MessageToDict(
            client.GetVersion(
                GetFunctionVersionRequest(
                    function_version_id=function_version_id,
                ),
            ),
            preserving_proto_field_name=True,
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
        'ListFunctionsVersionsResponse',
        MessageToDict(
            client.ListVersions(ListFunctionsVersionsRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    )


def list_scaling_policies(
    client: FunctionServiceStub,
    **kwargs: Unpack[ListScalingPoliciesParams],
) -> ListScalingPoliciesResponse:
    return cast(
        'ListScalingPoliciesResponse',
        MessageToDict(
            client.ListScalingPolicies(ListScalingPoliciesRequest(**kwargs)),
            preserving_proto_field_name=True,
        ),
    )


@overload
def get_details(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[ListScalingPoliciesParams],
) -> dict[str, Any]:
    ...


@overload
def get_details(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[_ByFolderId],
) -> dict[str, Any]:
    ...


@overload
def get_details(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[_ByFunctionId],
) -> dict[str, Any]:
    ...


def get_details(client, query, **kwargs):
    result: dict[str, Any] = {}
    if query == 'versions':
        result['ListFunctionsVersions'] = list_function_versions(
            client,
            **kwargs,
        )
    elif query == 'policy':
        result['ListScalingPolicies'] = list_scaling_policies(client, **kwargs)

    elif query == 'all':
        result['ListScalingPolicies'] = list_scaling_policies(client, **kwargs)
        result['ListFunctionsVersions'] = list_function_versions(
            client,
            **kwargs,
        )
    return result


def main():
    argument_spec = {
        'name': {'type': 'str'},
        'function_id': {'type': 'str'},
        'folder_id': {'type': 'str'},
        'query': {
            'type': 'str',
            'required': False,
            'choices': ['all', 'versions', 'policy', 'tags'],
            'default': 'all',
        },
    }
    required_one_of = [
        ('function_id', 'name', 'folder_id'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    required_if = [
        ('query', 'policy', ('function_id', 'name'), True),
        ('query', 'all', ('function_id', 'name'), True),
        ('query', 'versions', ('function_id', 'name', 'folder_id'), True),
    ]
    module = init_module(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        required_by=required_by,
        required_if=required_if,
        supports_check_mode=True,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)

    result: dict[str, Any] = {}
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    query = module.params.get('query')

    if function_id:
        with log_grpc_error(module):
            result.update(
                get_details(function_service, query, function_id=function_id),
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
                result.update(
                    get_details(
                        function_service,
                        query,
                        function_id=curr_function.get('id'),
                    ),
                )
    elif folder_id:
        with log_grpc_error(module):
            result.update(
                get_details(
                    function_service,
                    query,
                    folder_id=folder_id,
                ),
            )

    result['changed'] = False
    if module.check_mode:
        result['msg'] = 'Check mode set but ignored for fact gathering only.'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
