from __future__ import annotations

import contextlib
import json
import traceback
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
    Iterable,
    Mapping,
    MutableMapping,
    TypedDict,
)

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

HAS_YANDEX = False
try:
    import grpc
    import yandexcloud
except ImportError:
    YANDEX_ERR = traceback.format_exc()
else:
    HAS_YANDEX = True

if TYPE_CHECKING:
    from typing_extensions import (  # type: ignore[attr-defined]
        NotRequired,
        Required,
        Unpack,
    )

    class ModuleParams(TypedDict, total=False):
        argument_spec: Required[MutableMapping[str, Any]]
        bypass_checks: NotRequired[bool]
        no_log: NotRequired[bool]
        mutually_exclusive: NotRequired[list[tuple[str, ...]]]
        required_together: NotRequired[list[tuple[str, ...]]]
        required_one_of: NotRequired[list[tuple[str, ...]]]
        add_file_common_args: NotRequired[bool]
        supports_check_mode: NotRequired[bool]
        required_if: NotRequired[list[tuple[str, str, tuple[str, ...], bool]]]
        required_by: NotRequired[Mapping[str, Iterable[str]]]


def _get_auth_settings(
    module: AnsibleModule,
) -> dict[str, Any]:
    config = {}
    if module.params.get('auth_kind') == 'oauth':
        token = module.params.get('oauth_token')
        if not token:
            module.fail_json('oauth_token should be set')
        config['token'] = token

    if module.params.get('auth_kind') == 'sa_file':
        sa_path = module.params.get('sa_path')
        sa_content = module.params.get('sa_content')
        if sa_path:
            with open(sa_path) as f:
                config['service_account_key'] = json.load(f)
        elif sa_content:
            config['service_account_key'] = json.loads(sa_content)
        else:
            module.fail_json(
                "Either 'sa_path' or 'sa_content' must be set"
                " when 'auth_kind' is set to 'sa_file'",
            )

    return config


def get_base_arg_spec() -> dict[str, Any]:
    return {
        'auth_kind': {
            'type': 'str',
            'choices': ['oauth', 'sa_file'],
            'required': True,
        },
        'oauth_token': {'type': 'str'},
        'sa_path': {'type': 'str'},
        'sa_content': {'type': 'str'},
    }


def get_base_required_if() -> list[tuple[str, str, tuple[str, ...], bool]]:
    return [('auth_kind', 'sa_file', ('sa_path', 'sa_content'), True)]


def init_sdk(module: AnsibleModule) -> yandexcloud.SDK:
    return yandexcloud.SDK(
        interceptor=yandexcloud.RetryInterceptor(
            max_retry_count=5,
            retriable_codes=[grpc.StatusCode.UNAVAILABLE],
        ),
        **_get_auth_settings(module),
    )


def init_module(**params: Unpack[ModuleParams]) -> AnsibleModule:
    module = AnsibleModule(**params)
    if not HAS_YANDEX:
        module.fail_json(
            msg=missing_required_lib('yandexcloud'),
            exception=YANDEX_ERR,
        )
    return module


@contextlib.contextmanager
def log_grpc_error(module: AnsibleModule) -> Generator[None, None, None]:
    try:
        yield
    except grpc.RpcError as e:
        (state,) = e.args
        module.fail_json(msg=state.details)
