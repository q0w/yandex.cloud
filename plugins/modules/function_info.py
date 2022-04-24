from __future__ import annotations

from typing import Any
from typing import cast
from typing import Mapping
from typing import overload
from typing import TYPE_CHECKING
from typing import TypedDict

from ..module_utils.basic import get_base_arg_spec
from ..module_utils.basic import get_base_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error
from ..module_utils.function import get_function

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        ListFunctionsVersionsRequest,
        ListScalingPoliciesRequest,
        ListFunctionTagHistoryRequest,
        ListRuntimesRequest,
        GetFunctionVersionRequest,
        ListFunctionOperationsRequest,
    )
    from yandex.cloud.access.access_pb2 import ListAccessBindingsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
    from google.protobuf.json_format import MessageToDict
except ImportError:
    pass

if TYPE_CHECKING:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack

    from ..module_utils.function import ScalingPolicy
    from ..module_utils.function import _Operation
    from ..module_utils.function import _Metadata

    class ListVersionsParams(TypedDict, total=False):
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

    class ListScalingPoliciesParams(TypedDict, total=False):
        function_id: Required[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]

    class _ByFunctionId(ListVersionsParams):
        function_id: Required[str]

    class _ByFolderId(ListVersionsParams):
        folder_id: Required[str]

    class ListTagsParams(TypedDict, total=False):
        function_id: Required[str]
        tag: NotRequired[str]
        page_size: NotRequired[int]
        page_token: NotRequired[str]
        filter: NotRequired[str]

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

    class Operation(_Operation):
        response: NotRequired[_Metadata]


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


class ListFunctionsVersionsResponse(TypedDict, total=False):
    versions: list[FunctionVersion]
    next_page_token: str


class ListScalingPoliciesResponse(TypedDict, total=False):
    scaling_policies: list[ScalingPolicy]
    next_page_token: str


class FunctionTagHistoryRecord(TypedDict):
    function_id: str
    tag: str
    function_version_id: str
    effective_from: str
    effective_to: str


class ListFunctionTagHistoryResponse(TypedDict, total=False):
    function_tag_history_record: list[FunctionTagHistoryRecord]
    next_page_token: str


class ListRuntimesResponse(TypedDict):
    runtimes: list[str]


class Subject(TypedDict):
    id: str
    type: str


class AccessBinding(TypedDict):
    role_id: str
    subject: Subject


class ListAccessBindingsResponse(TypedDict, total=False):
    access_bindings: list[AccessBinding]
    next_page_token: str


class ListFunctionOperationsResponse(TypedDict, total=False):
    operations: list[Operation]
    next_page_token: str


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


def list_function_versions_by_folder(
    client: FunctionServiceStub,
    *,
    folder_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListFunctionsVersionsResponse:
    return cast(
        ListFunctionsVersionsResponse,
        MessageToDict(
            client.ListVersions(
                ListFunctionsVersionsRequest(
                    folder_id=folder_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    )


def list_function_versions_by_function(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListFunctionsVersionsResponse:
    return cast(
        ListFunctionsVersionsResponse,
        MessageToDict(
            client.ListVersions(
                ListFunctionsVersionsRequest(
                    function_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    )


# TODO: check page_size, page_token
def list_scaling_policies(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> ListScalingPoliciesResponse:
    return cast(
        ListScalingPoliciesResponse,
        MessageToDict(
            client.ListScalingPolicies(
                ListScalingPoliciesRequest(
                    function_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    )


# TODO: check page_size, page_token, filter
def list_tag_history(
    client: FunctionServiceStub,
    *,
    function_id: str,
    tag: str = '$latest',
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListFunctionTagHistoryResponse:
    return cast(
        ListFunctionTagHistoryResponse,
        MessageToDict(
            client.ListTagHistory(
                ListFunctionTagHistoryRequest(
                    function_id=function_id,
                    tag=tag,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
        ),
    )


def list_runtimes(client: FunctionServiceStub) -> ListRuntimesResponse:
    return cast(
        ListRuntimesResponse,
        MessageToDict(
            client.ListRuntimes(ListRuntimesRequest()),
        ),
    )


# TODO: check page_size, page_token
def list_access_bindings(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> ListAccessBindingsResponse:
    return cast(
        ListAccessBindingsResponse,
        MessageToDict(
            client.ListAccessBindings(
                ListAccessBindingsRequest(
                    resource_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                ),
            ),
        ),
    )


def list_operations(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> ListFunctionOperationsResponse:
    return cast(
        'ListFunctionOperationsResponse',
        MessageToDict(
            client.ListOperations(
                ListFunctionOperationsRequest(
                    function_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
        ),
    )


@overload
def get_details_by_function(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[ListScalingPoliciesParams],
) -> dict[str, Any]:
    ...


@overload
def get_details_by_function(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[_ByFunctionId],
) -> dict[str, Any]:
    ...


@overload
def get_details_by_function(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[ListTagsParams],
) -> dict[str, Any]:
    ...


def get_details_by_function(client, query, **kwargs):
    result: dict[str, Any] = {}
    if query == 'versions':
        result['ListFunctionsVersions'] = list_function_versions_by_function(
            client,
            **kwargs,
        )
    elif query == 'policy':
        result['ListScalingPolicies'] = list_scaling_policies(
            client,
            **kwargs,
        )
    elif query == 'tags':
        result['ListFunctionTagHistory'] = list_tag_history(client, **kwargs)
    elif query == 'access_bindings':
        result['ListAccessBindings'] = list_access_bindings(client, **kwargs)
    elif query == 'operations':
        result['ListFunctionOperations'] = list_operations(client, **kwargs)
    elif query == 'runtimes':
        result['ListRuntimes'] = list_runtimes(client)
    elif query == 'all':
        result['ListFunctionsVersions'] = list_function_versions_by_folder(
            client,
            **kwargs,
        )
        result['ListScalingPolicies'] = list_scaling_policies(
            client,
            **kwargs,
        )
        result['ListFunctionTagHistory'] = list_tag_history(client, **kwargs)
        result['ListAccessBindings'] = list_access_bindings(client, **kwargs)
        result['ListFunctionOperations'] = list_operations(client, **kwargs)
        result['ListRuntimes'] = list_runtimes(client)
    return result


def get_details_by_folder(
    client: FunctionServiceStub,
    query: str,
    **kwargs: Unpack[_ByFolderId],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if query == 'versions':
        result['ListFunctionsVersions'] = list_function_versions_by_folder(
            client,
            **kwargs,
        )
    elif query == 'runtimes':
        result['ListRuntimes'] = list_runtimes(client)
    elif query == 'all':
        result['ListFunctionsVersions'] = list_function_versions_by_folder(
            client,
            **kwargs,
        )
        result['ListRuntimes'] = list_runtimes(client)
    return result


def main():
    argument_spec = get_base_arg_spec()
    required_if = get_base_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'query': {
                'type': 'str',
                'required': False,
                'choices': [
                    'all',
                    'versions',
                    'policy',
                    'tags',
                    'runtimes',
                    'access_bindings',
                    'operations',
                ],
                'default': 'all',
            },
        },
    )
    required_one_of = [
        ('function_id', 'name', 'folder_id'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    required_if.extend(
        [
            ('query', 'policy', ('function_id', 'name'), True),
            ('query', 'all', ('function_id', 'name'), True),
            ('query', 'versions', ('function_id', 'name', 'folder_id'), True),
            ('query', 'tags', ('function_id', 'name'), True),
            ('query', 'access_bindings', ('function_id', 'name'), True),
            ('query', 'operations', ('function_id', 'name'), True),
        ],
    )
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
                get_details_by_function(
                    function_service,
                    query,
                    function_id=function_id,
                ),
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
                    get_details_by_function(
                        function_service,
                        query,
                        function_id=curr_function.get('id'),
                    ),
                )
    elif folder_id:
        with log_grpc_error(module):
            result.update(
                get_details_by_folder(
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
