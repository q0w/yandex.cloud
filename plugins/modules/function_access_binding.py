from __future__ import annotations

from typing import Any, TypedDict

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
    from yandex.cloud.access.access_pb2 import (
        SetAccessBindingsRequest,
        UpdateAccessBindingsRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass


class Subject(TypedDict):
    id: str
    type: str


class AccessBinding(TypedDict):
    role_id: str
    subject: Subject


def set_access_bindings(
    client: FunctionServiceStub,
    *,
    function_id: str,
    access_bindings: list[AccessBinding],
) -> dict[str, dict[str, Any]]:
    return {
        'SetAccessBindings': MessageToDict(
            client.SetAccessBindings(
                SetAccessBindingsRequest(
                    resource_id=function_id,
                    access_bindings=access_bindings,
                ),
            ),
        ),
    }


def remove_access_bindings(
    client: FunctionServiceStub,
    *,
    function_id: str,
    access_bindings: list[AccessBinding],
) -> dict[str, dict[str, Any]]:
    access_binding_deltas = []
    for b in access_bindings:
        access_binding_deltas.append({'action': 'REMOVE', 'access_binding': b})

    return {
        'RemoveAccessBindings': MessageToDict(
            client.UpdateAccessBindings(
                UpdateAccessBindingsRequest(
                    resource_id=function_id,
                    access_binding_deltas=access_binding_deltas,
                ),
            ),
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
            'access_bindings': {
                'type': 'list',
                'required': True,
                'options': {
                    'role_id': {'type': 'str', 'required': True},
                    'subject': {
                        'type': 'dict',
                        'options': {
                            'id': {'type': 'str', 'required': True},
                            'type': {'type': 'str', 'required': True},
                        },
                    },
                },
            },
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
    changed = False
    state = module.params.get('state')
    function_id = module.params.get('function_id')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    access_bindings = module.params.get('access_bindings')

    if not function_id and folder_id and name:
        with log_grpc_error(module):
            curr_function = get_function_by_name(
                function_service,
                folder_id=folder_id,
                name=name,
            )
        if not curr_function:
            module.fail_json(msg=f'function {name} not found')
            # FIXME: add stubs
            raise AssertionError('unreachable')
        function_id = curr_function.get('id')

    if state == 'present':
        with log_grpc_error(module):
            result.update(
                set_access_bindings(
                    function_service,
                    function_id=function_id,
                    access_bindings=access_bindings,
                ),
            )
        changed = True
    elif state == 'absent':
        with log_grpc_error(module):
            result.update(
                remove_access_bindings(
                    function_service,
                    function_id=function_id,
                    access_bindings=access_bindings,
                ),
            )
        changed = True

    module.exit_json(**result, changed=changed)


if __name__ == '__main__':
    main()
