from __future__ import annotations

import zipfile
from contextlib import suppress
from typing import TYPE_CHECKING, Mapping

from ..module_utils.basic import (
    default_arg_spec,
    default_required_if,
    init_module,
    init_sdk,
    log_error,
    log_grpc_error,
    validate_zip,
)
from ..module_utils.function import get_function_by_name

with suppress(ImportError):
    from google.protobuf.duration_pb2 import Duration
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionVersionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )

if TYPE_CHECKING:
    from ..module_utils.types import OperationResult


def create_version_by_package(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Mapping[str, int],
    execution_timeout: Duration,
    service_account_id: str | None = None,
    package: Mapping[str, str],
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Mapping[str, str | list[str]] | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Mapping[str, str]] | None = None,
) -> OperationResult:
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
            preserving_proto_field_name=True,
        ),
    }


def create_version_by_content(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Mapping[str, int],
    execution_timeout: Duration,
    service_account_id: str | None = None,
    content: bytes,
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Mapping[str, str | list[str]] | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Mapping[str, str]] | None = None,
) -> OperationResult:
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
            preserving_proto_field_name=True,
        ),
    }


def create_version_by_version_id(
    client: FunctionServiceStub,
    *,
    function_id: str,
    runtime: str,
    entrypoint: str,
    resources: Mapping[str, int],
    execution_timeout: Duration,
    service_account_id: str | None = None,
    version_id: str,
    description: str | None = None,
    environment: Mapping[str, str] | None = None,
    tag: list[str] | None = None,
    connectivity: Mapping[str, str | list[str]] | None = None,
    named_service_accounts: Mapping[str, str] | None = None,
    secrets: list[Mapping[str, str]] | None = None,
) -> OperationResult:
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
            preserving_proto_field_name=True,
        ),
    }


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
            'service_account_id': {'type': 'str'},
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

    result = {}
    execution_timeout = Duration()
    with log_error(module, ValueError):
        execution_timeout.FromJsonString(module.params.get('execution_timeout'))

    if (
        not module.params['function_id']
        and module.params['folder_id']
        and module.params['name']
    ):
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=module.params['folder_id'],
                name=module.params['name'],
            )
        if not curr_function:
            module.fail_json(f'function {module.params["name"]} not found')
        module.params['function_id'] = curr_function['id']

    if module.params['package'] is not None:
        with log_grpc_error(module):
            result.update(
                create_version_by_package(
                    function_service,
                    function_id=module.params['function_id'],
                    runtime=module.params['runtime'],
                    entrypoint=module.params['entrypoint'],
                    resources=module.params['resources'],
                    execution_timeout=execution_timeout,
                    service_account_id=module.params['service_account_id'],
                    description=module.params['description'],
                    environment=module.params['environment'],
                    tag=module.params['tag'],
                    connectivity=module.params['connectivity'],
                    named_service_accounts=module.params['named_service_accounts'],
                    secrets=module.params['secrets'],
                    package=module.params['package'],
                ),
            )
    elif module.params['content'] is not None:
        with log_error(module, FileNotFoundError, zipfile.BadZipfile):
            validate_zip(module, module.params['content'])
        with log_error(module, FileNotFoundError), open(
            module.params['content'],
            'rb',
        ) as f:
            module.params['content'] = f.read()
        with log_grpc_error(module):
            result.update(
                create_version_by_content(
                    function_service,
                    function_id=module.params['function_id'],
                    runtime=module.params['runtime'],
                    entrypoint=module.params['entrypoint'],
                    resources=module.params['resources'],
                    execution_timeout=execution_timeout,
                    service_account_id=module.params['service_account_id'],
                    description=module.params['description'],
                    environment=module.params['environment'],
                    tag=module.params['tag'],
                    connectivity=module.params['connectivity'],
                    named_service_accounts=module.params['named_service_accounts'],
                    secrets=module.params['secrets'],
                    content=module.params['content'],
                ),
            )
    elif module.params['version_id'] is not None:
        with log_grpc_error(module):
            result.update(
                create_version_by_version_id(
                    function_service,
                    function_id=module.params['function_id'],
                    runtime=module.params['runtime'],
                    entrypoint=module.params['entrypoint'],
                    resources=module.params['resources'],
                    execution_timeout=execution_timeout,
                    service_account_id=module.params['service_account_id'],
                    description=module.params['description'],
                    environment=module.params['environment'],
                    tag=module.params['tag'],
                    connectivity=module.params['connectivity'],
                    named_service_accounts=module.params['named_service_accounts'],
                    secrets=module.params['secrets'],
                    version_id=module.params['version_id'],
                ),
            )
    changed = True
    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
