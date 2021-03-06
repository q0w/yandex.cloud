from __future__ import annotations

import zipfile
from contextlib import suppress
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_error
from ..module_utils.basic import log_grpc_error
from ..module_utils.basic import NotFound
from ..module_utils.basic import validate_zip
from ..module_utils.function import get_function_id

with suppress(ImportError):
    from google.protobuf.duration_pb2 import Duration
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import CreateFunctionVersionRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub


def main() -> NoReturn:
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
    client: FunctionServiceStub = init_sdk(module).client(FunctionServiceStub)
    result = {}

    function_id = module.params['function_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    package = module.params['package']
    content = module.params['content']
    version_id = module.params['version_id']
    kw = {
        'runtime': module.params['runtime'],
        'entrypoint': module.params['entrypoint'],
        'resources': module.params['resources'],
        'service_account_id': module.params['service_account_id'],
        'description': module.params['description'],
        'environment': module.params['environment'],
        'tag': module.params['tag'],
        'connectivity': module.params['connectivity'],
        'named_service_accounts': module.params['named_service_accounts'],
        'secrets': module.params['secrets'],
    }

    execution_timeout = Duration()
    with log_error(module, ValueError):
        execution_timeout.FromJsonString(module.params['execution_timeout'])
    kw['execution_timeout'] = execution_timeout

    if not function_id:
        with log_error(module, NotFound), log_grpc_error(module):
            function_id = get_function_id(client, folder_id, name)
    kw['function_id'] = function_id

    if package:
        kw['package'] = package
    elif content:
        with log_error(module, FileNotFoundError, zipfile.BadZipfile):
            validate_zip(module, module.params['content'])
        with log_error(module, FileNotFoundError), open(content, 'rb') as f:
            kw['content'] = f.read()
    elif version_id:
        kw['version_id'] = version_id

    with log_grpc_error(module):
        resp = client.CreateVersion(CreateFunctionVersionRequest(**kw))
        result['CreateFunctionVersion'] = MessageToDict(resp)

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
