from __future__ import annotations

from contextlib import suppress
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
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import RemoveScalingPolicyRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import SetScalingPolicyRequest
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import FunctionServiceStub


def main() -> NoReturn:
    argument_spec = default_arg_spec()
    required_if = default_required_if()
    argument_spec.update(
        {
            'name': {'type': 'str'},
            'function_id': {'type': 'str'},
            'folder_id': {'type': 'str'},
            'tag': {'type': 'str', 'required': True},
            'provisioned_instances_count': {'type': 'int'},
            'zone_instances_limit': {'type': 'int'},
            'zone_requests_limit': {'type': 'int'},
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
    )
    client: FunctionServiceStub = init_sdk(module).client(FunctionServiceStub)
    result = {}

    state = module.params['state']
    function_id = module.params['function_id']
    folder_id = module.params['folder_id']
    name = module.params['name']
    tag = module.params['tag']
    pi_count = module.params['provisioned_instances_count']
    zi_limit = module.params['zone_instances_limit']
    zr_limit = module.params['zone_requests_limit']

    if not function_id:
        with log_error(module, NotFound), log_grpc_error(module):
            function_id = get_function_id(client, folder_id, name)

    with log_grpc_error(module):
        if state == 'present':
            resp = client.SetScalingPolicy(
                SetScalingPolicyRequest(
                    function_id=function_id,
                    tag=tag,
                    provisioned_instances_count=pi_count,
                    zone_instances_limit=zi_limit,
                    zone_requests_limit=zr_limit,
                ),
            )
            result.update(MessageToDict(resp))
        elif state == 'absent':
            resp = client.RemoveScalingPolicy(RemoveScalingPolicyRequest(function_id=function_id, tag=tag))
            result.update(MessageToDict(resp))

    module.exit_json(**result, changed=True)


if __name__ == '__main__':
    main()
