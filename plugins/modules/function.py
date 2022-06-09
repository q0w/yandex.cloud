from __future__ import annotations

from contextlib import suppress
from typing import NoReturn

from ..module_utils.basic import default_arg_spec
from ..module_utils.basic import default_required_if
from ..module_utils.basic import init_module
from ..module_utils.basic import init_sdk
from ..module_utils.basic import log_grpc_error

with suppress(ImportError):
    from google.protobuf.json_format import MessageToDict
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import CreateFunctionRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import DeleteFunctionRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import GetFunctionRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import ListFunctionsRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import UpdateFunctionRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub


def main() -> NoReturn:
    argument_spec = default_arg_spec()
    required_if = default_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'description': {'type': 'str'},
            'labels': {'type': 'dict'},
            'state': {
                'type': 'str',
                'default': 'present',
                'choices': ['present', 'absent'],
            },
        },
    )
    required_one_of = [
        ('function_id', 'name'),
    ]
    required_together = [
        ('name', 'folder_id'),
    ]

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
        required_one_of=required_one_of,
        required_together=required_together,
    )
    client: FunctionServiceStub = init_sdk(module).client(FunctionServiceStub)
    result = {}

    state = module.params['state']
    function_id = module.params['function_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    description = module.params['description']
    labels = module.params['labels']

    # check if the function exists
    curr_function = None
    with log_grpc_error(module):
        if function_id:
            curr_function = client.Get(GetFunctionRequest(function_id=function_id))
        else:
            functions = client.List(ListFunctionsRequest(folder_id=folder_id, filter=f'name="{name}"')).functions
            if functions:
                curr_function = functions[0]

    with log_grpc_error(module):
        if state == 'present':
            if curr_function:
                resp = client.Update(
                    UpdateFunctionRequest(
                        function_id=curr_function.id,
                        name=name,
                        description=description,
                        labels=labels,
                    ),
                )
                result.update(MessageToDict(resp))
            else:
                resp = client.Create(
                    CreateFunctionRequest(folder_id=folder_id, name=name, description=description, labels=labels),
                )
                result.update(MessageToDict(resp))

        elif state == 'absent':
            if not curr_function:
                module.fail_json(f'function {function_id or name} not found')
            resp = client.Delete(DeleteFunctionRequest(function_id=curr_function.id))
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
