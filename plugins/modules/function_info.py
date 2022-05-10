from __future__ import annotations

from typing import Any, Callable, Generator

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import (
    get_function_by_name,
    list_function_versions_by_folder,
    list_function_versions_by_function,
)

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.access.access_pb2 import ListAccessBindingsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        GetFunctionVersionRequest,
        ListFunctionOperationsRequest,
        ListFunctionTagHistoryRequest,
        ListRuntimesRequest,
        ListScalingPoliciesRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


def get_version(
    client: FunctionServiceStub,
    function_version_id: str,
) -> dict[str, Any]:
    return MessageToDict(
        client.GetVersion(
            GetFunctionVersionRequest(
                function_version_id=function_version_id,
            ),
        ),
        preserving_proto_field_name=True,
    )


# TODO: check page_size, page_token
def list_scaling_policies(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'ListScalingPolicies': MessageToDict(
            client.ListScalingPolicies(
                ListScalingPoliciesRequest(
                    function_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                ),
            ),
            preserving_proto_field_name=True,
        ),
    }


# TODO: check page_size, page_token, filter
def list_tag_history(
    client: FunctionServiceStub,
    *,
    function_id: str,
    tag: str = '$latest',
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'ListFunctionTagHistory': MessageToDict(
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
    }


def list_runtimes(client: FunctionServiceStub) -> dict[str, dict[str, Any]]:
    return {
        'ListRuntimes': MessageToDict(
            client.ListRuntimes(ListRuntimesRequest()),
        ),
    }


# TODO: check page_size, page_token
def list_access_bindings(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'ListAccessBindings': MessageToDict(
            client.ListAccessBindings(
                ListAccessBindingsRequest(
                    resource_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                ),
            ),
        ),
    }


def list_operations(
    client: FunctionServiceStub,
    *,
    function_id: str,
    page_size: int | None = None,
    page_token: str | None = None,
    filter: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'ListFunctionOperations': MessageToDict(
            client.ListOperations(
                ListFunctionOperationsRequest(
                    function_id=function_id,
                    page_size=page_size,
                    page_token=page_token,
                    filter=filter,
                ),
            ),
        ),
    }


def _iter_callables(
    key: str,
    callables: dict[str, Callable[..., dict[str, dict[str, Any]]]],
) -> Generator[Callable[..., dict[str, dict[str, Any]]], None, None]:
    f = callables.get(key)
    if f:
        yield f
    else:
        yield from callables.values()


def main():
    argument_spec = default_arg_spec()
    required_if = default_required_if()
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
            ('query', 'all', ('function_id', 'name', 'folder_id'), True),
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

    callables_by_function: dict[str, Callable[..., dict[str, dict[str, Any]]]] = {
        'versions': lambda c, **kwargs: {
            'ListFunctionsVersions': list_function_versions_by_function(c, **kwargs),
        },
        'policy': list_scaling_policies,
        'tags': list_tag_history,
        'access_bindings': list_access_bindings,
        'operations': list_operations,
        'runtimes': lambda c, **kwargs: list_runtimes(c),
    }

    callables_by_folder: dict[str, Callable[..., dict[str, dict[str, Any]]]] = {
        'versions': lambda c, **kwargs: {
            'ListFunctionsVersions': list_function_versions_by_folder(c, **kwargs),
        },
        'runtimes': lambda c, **kwargs: list_runtimes(c),
    }

    if function_id:
        with log_grpc_error(module):
            for f in _iter_callables(query, callables_by_function):
                result.update(f(function_service, function_id=function_id))

    elif name and folder_id:
        # FIXME: somehow filter by name does not work
        # FIXME: workaround: filter functions by name using ListVersions
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if curr_function:
            with log_grpc_error(module):
                for f in _iter_callables(query, callables_by_function):
                    result.update(
                        f(function_service, function_id=curr_function.get('id')),
                    )

    elif folder_id:
        with log_grpc_error(module):
            for f in _iter_callables(query, callables_by_folder):
                result.update(f(function_service, folder_id=folder_id))

    result['changed'] = False
    if module.check_mode:
        result['msg'] = 'Check mode set but ignored for fact gathering only.'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
