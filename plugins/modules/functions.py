from __future__ import annotations

import sys
from typing import Any
from typing import Mapping
from typing import TypedDict

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.protobuf import protobuf_to_dict
from ..module_utils.yc import init_module
from ..module_utils.yc import init_sdk
from ..module_utils.yc import log_grpc_error

try:
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        CreateFunctionRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2 import (
        ListFunctionsRequest,
    )
    from yandex.cloud.serverless.functions.v1.function_service_pb2_grpc import (
        FunctionServiceStub,
    )
except ImportError:
    pass

if sys.version_info >= (3, 11):
    from typing import NotRequired
    from typing import Required
    from typing import Unpack
else:
    from typing_extensions import NotRequired
    from typing_extensions import Required
    from typing_extensions import Unpack


class CreateFunctionParams(TypedDict):
    folder_id: Required[str]
    name: NotRequired[str]
    description: NotRequired[str]
    labels: NotRequired[Mapping[str, str]]


class ListFunctionParams(TypedDict):
    folder_id: Required[str]
    page_size: NotRequired[int]
    page_token: NotRequired[str]
    filter: NotRequired[str]


def list_functions(
    client: FunctionServiceStub,
    **kwargs: Unpack[ListFunctionParams],
):
    return client.List(ListFunctionsRequest(**kwargs))


def create_function(
    module: AnsibleModule,
    client: FunctionServiceStub,
    **kwargs: Unpack[CreateFunctionParams],
) -> dict[str, Any]:
    with log_grpc_error(module):
        res = client.Create(CreateFunctionRequest(**kwargs))
    return protobuf_to_dict(res)


def main() -> None:
    argument_spec = dict(
        name=dict(
            type='str',
        ),
        auth_kind=dict(
            type='str',
            choices=['oauth', 'sa_file'],
            required=True,
        ),
        oauth_token=dict(type='str'),
        sa_path=dict(type='str'),
        sa_content=dict(type='str'),
        folder_id=dict(type='str', required=True),
    )

    required_if = [
        (
            'auth_kind',
            'sa_file',
            ('sa_path', 'sa_content'),
            True,
        ),
    ]

    module = init_module(
        argument_spec=argument_spec,
        required_if=required_if,
    )
    sdk = init_sdk(module)
    function_service = sdk.client(FunctionServiceStub)
    result = {}
    result['CreateFunction'] = create_function(
        module,
        function_service,
        folder_id=module.params.get('folder_id'),
        name=module.params.get('name'),
    )
    module.exit_json(**result)


if __name__ == '__main__':
    main()
