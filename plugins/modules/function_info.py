from __future__ import annotations

from contextlib import suppress
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Mapping
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_error
from ..module_utils.basic import log_grpc_error
from ..module_utils.basic import NotFound
from ..module_utils.function import get_function_id

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.access.access_pb2 import ListAccessBindingsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionOperationsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionsVersionsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionTagHistoryRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListRuntimesRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListScalingPoliciesRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub


ListResult = Dict[str, Dict[str, Any]]


def iter_callables(
    d: Mapping[str, Callable[..., ListResult]],
    query: str,
) -> Generator[Callable[..., ListResult], None, None]:
    if d.get(query):
        yield d[query]
    else:
        yield from d.values()


def main() -> NoReturn:
    argument_spec = default_arg_spec()
    required_if = default_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'tag': {'type': 'str', 'default': '$latest'},
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
    client: FunctionServiceStub = init_sdk(module).client(FunctionServiceStub)
    result: dict[str, Any] = {}

    function_id: str = module.params['function_id']
    folder_id: str = module.params['folder_id']
    name = module.params['name']
    tag = module.params['tag']
    query = module.params['query']

    by_function_id = {
        'versions': lambda: MessageToDict(client.ListVersions(ListFunctionsVersionsRequest(function_id=function_id))),
        'policy': lambda: MessageToDict(
            client.ListScalingPolicies(ListScalingPoliciesRequest(function_id=function_id)),
        ),
        'tags': lambda: MessageToDict(
            client.ListTagHistory(ListFunctionTagHistoryRequest(function_id=function_id, tag=tag)),
        ),
        'access_bindings': lambda: MessageToDict(
            client.ListAccessBindings(ListAccessBindingsRequest(resource_id=function_id)),
        ),
        'operations': lambda: MessageToDict(
            client.ListOperations(ListFunctionOperationsRequest(function_id=function_id)),
        ),
        'runtimes': lambda: MessageToDict(client.ListRuntimes(ListRuntimesRequest())),
    }

    by_folder_id = {
        'versions': lambda: MessageToDict(client.ListVersions(ListFunctionsVersionsRequest(folder_id=folder_id))),
        'runtimes': lambda: MessageToDict(client.ListRuntimes(ListRuntimesRequest())),
    }

    if not function_id and name:
        with log_error(module, NotFound), log_grpc_error(module):
            function_id = get_function_id(client, folder_id, name)

    if function_id:
        for f in iter_callables(by_function_id, query):
            with log_grpc_error(module):
                result.update(f())
    else:
        for f in iter_callables(by_folder_id, query):
            with log_grpc_error(module):
                result.update(f())

    if module.check_mode:
        result['msg'] = 'check mode set but ignored for fact gathering only'

    module.exit_json(**result, changed=False)


if __name__ == '__main__':
    main()
