from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Mapping,
    NoReturn,
    TypedDict,
    cast,
    overload,
)

from google.protobuf.duration_pb2 import Duration

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_grpc_error,
)
from ..module_utils.function import get_function_by_name

try:
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionVersionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass

if TYPE_CHECKING:
    from typing_extensions import NotRequired, Required

    class Package(TypedDict, total=False):
        bucket_name: Required[str]
        object_name: Required[str]
        sha256: NotRequired[str]


class Resources(TypedDict):
    memory: int


# TODO: total=false?
class Connectivity(TypedDict):
    network_id: str
    subnet_id: list[str]


# TODO: total=false?
class Secret(TypedDict):
    id: str
    version_id: str
    key: str
    environment_variable: str


def create_version_by_package(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Resources,
    execution_timeout: Duration,
    service_account_id: str | None = None,
    package: Package,
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Connectivity | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Secret] | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'CreateFunctionVersion': MessageToDict(
            client.CreateVersion(
                CreateFunctionVersionRequest(
                    function_id=function_id,
                    runtime=runtime,
                    entrypoint=entrypoint,
                    resources=resources,
                    execution_timeout=execution_timeout,
                    service_account_id=service_account_id,
                    package=package,
                    description=description,
                    environment=environment,
                    tag=tag,
                    connectivity=connectivity,
                    named_service_accounts=named_service_accounts,
                    secrets=secrets,
                ),
            ),
        ),
    }


def create_version_by_content(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Resources,
    execution_timeout: Duration,
    service_account_id: str | None = None,
    content_file: str,
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Connectivity | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Secret] | None = None,
) -> dict[str, dict[str, Any]]:
    with open(content_file, 'rb') as f:
        content = f.read()
    return {
        'CreateFunctionVersion': MessageToDict(
            client.CreateVersion(
                CreateFunctionVersionRequest(
                    function_id=function_id,
                    runtime=runtime,
                    entrypoint=entrypoint,
                    resources=resources,
                    execution_timeout=execution_timeout,
                    service_account_id=service_account_id,
                    content=content,
                    description=description,
                    environment=environment,
                    tag=tag,
                    connectivity=connectivity,
                    named_service_accounts=named_service_accounts,
                    secrets=secrets,
                ),
            ),
        ),
    }


def create_version_by_version_id(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Resources,
    execution_timeout: Duration,
    service_account_id: str | None = None,
    version_id: str,
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Connectivity | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Secret] | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        'CreateFunctionVersion': MessageToDict(
            client.CreateVersion(
                CreateFunctionVersionRequest(
                    function_id=function_id,
                    runtime=runtime,
                    entrypoint=entrypoint,
                    resources=resources,
                    execution_timeout=execution_timeout,
                    service_account_id=service_account_id,
                    version_id=version_id,
                    description=description,
                    environment=environment,
                    tag=tag,
                    connectivity=connectivity,
                    named_service_accounts=named_service_accounts,
                    secrets=secrets,
                ),
            ),
        ),
    }


class _Package(TypedDict, total=False):
    bucket_name: str
    object_name: str
    sha256: str


class _Content(TypedDict):
    content: str


class _Version(TypedDict):
    version_id: str


@overload
def _get_callable(
    params: _Package,
    callables: dict[str, Callable[..., partial[dict[str, dict[str, Any]]]]],
) -> partial[dict[str, dict[str, Any]]]:
    ...


@overload
def _get_callable(
    params: _Content,
    callables: dict[str, Callable[..., partial[dict[str, dict[str, Any]]]]],
) -> partial[dict[str, dict[str, Any]]]:
    ...


@overload
def _get_callable(
    params: _Version,
    callables: dict[str, Callable[..., partial[dict[str, dict[str, Any]]]]],
) -> partial[dict[str, dict[str, Any]]]:
    ...


def _get_callable(
    params,
    callables,
):
    for k, v in callables.items():
        if params[k]:
            return v(params[k])


def main():
    argument_spec = default_arg_spec()
    required_if = default_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'runtime': {'type': 'str', 'required': True},
            'resources': {
                'type': 'dict',
                'required': True,
                'options': {
                    'memory': {'type': 'int', 'required': True},
                },
            },
            'entrypoint': {'type': 'str', 'required': True},
            'description': {'type': 'str'},
            'execution_timeout': {'type': 'str', 'required': True},
            'package': {
                'type': 'dict',
                'options': {
                    'bucket_name': {'type': 'str', 'required': True},
                    'object_name': {'type': 'str', 'required': True},
                    'sha256': {'type': 'str'},
                },
            },
            'content': {'type': 'str'},
            'version_id': {'type': 'str'},
            'environment': {'type': 'dict', 'elements': 'str'},
            'tag': {'type': 'list', 'elements': 'str'},
            'connectivity': {
                'type': 'dict',
                'options': {
                    'network_id': {'type': 'str', 'required': True},
                    'subnet_id': {'type': 'list', 'elements': 'str', 'required': True},
                },
            },
            'named_service_accounts': {'type': 'dict', 'elements': 'str'},
            'secrets': {
                'type': 'list',
                'options': {
                    # required?
                    'id': {'type': 'str', 'required': True},
                    'version_id': {'type': 'str', 'required': True},
                    'key': {'type': 'str', 'required': True},
                    'environment_variable': {'type': 'str', 'required': True},
                },
            },
        },
    )

    required_one_of = [
        ('function_id', 'name'),
        ('package', 'content', 'version_id'),
    ]
    required_by = {
        'name': 'folder_id',
    }
    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
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
    execution_timeout = Duration()
    execution_timeout.FromJsonString(module.params.get('execution_timeout'))

    callables: dict[str, Callable[..., partial[dict[str, dict[str, Any]]]]] = {
        'package': lambda package: partial(create_version_by_package, package=package),
        'content': lambda content: partial(
            create_version_by_content,
            content_file=content,
        ),
        'version_id': lambda version_id: partial(
            create_version_by_version_id,
            version_id=version_id,
        ),
    }

    f = _get_callable(module.params, callables)

    if not function_id and folder_id and name:
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if not curr_function:
            cast(Callable[..., NoReturn], module.fail_json)(
                msg=f'function {name} not found',
            )
        function_id = curr_function.get('id')

    with log_grpc_error(module):
        result.update(
            f(
                function_service,
                function_id=function_id,
                runtime=module.params.get('runtime'),
                entrypoint=module.params.get('entrypoint'),
                resources=module.params.get('resources'),
                execution_timeout=execution_timeout,
                service_account_id=module.params.get('service_account_id'),
                description=module.params.get('description'),
                environment=module.params.get('environment'),
                tag=module.params.get('tag'),
                connectivity=module.params.get('connectivity'),
                named_service_accounts=module.params.get('named_service_accounts'),
                secrets=module.params.get('secrets'),
            ),
        )

    changed = True
    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
