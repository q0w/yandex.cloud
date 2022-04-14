from __future__ import annotations

import contextlib
import json
import traceback
from typing import Any
from typing import Generator
from typing import Iterable
from typing import Mapping
from typing import TYPE_CHECKING
from typing import TypedDict

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

HAS_YANDEX = False
try:
    import grpc
    import yandexcloud
except ImportError:
    YANDEX_ERR = traceback.format_exc()
else:
    HAS_YANDEX = True

if TYPE_CHECKING:
    from typing_extensions import Unpack
    from typing_extensions import NotRequired
    from typing_extensions import Required


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
                sa_key = json.load(f)
        elif sa_content:
            sa_key = json.loads(sa_content)
        else:
            module.fail_json(
                "Either 'sa_path' or 'sa_content' must be set"
                " when 'auth_kind' is set to 'sa_file'",
            )
        config['service_account_key'] = sa_key

    return config


def init_sdk(module: AnsibleModule) -> yandexcloud.SDK:
    return yandexcloud.SDK(
        interceptor=yandexcloud.RetryInterceptor(
            max_retry_count=5,
            retriable_codes=[grpc.StatusCode.UNAVAILABLE],
        ),
        **_get_auth_settings(module),
    )


@contextlib.contextmanager
def log_grpc_error(module: AnsibleModule) -> Generator[None, None, None]:
    try:
        yield
    except grpc._channel._InactiveRpcError as e:
        (state,) = e.args
        module.fail_json(msg=state.details)


class ModuleParams(TypedDict):
    argument_spec: Required[Mapping[str, Any]]
    bypass_checks: NotRequired[bool]
    no_log: NotRequired[bool]
    mutually_exclusive: NotRequired[list[tuple[str, ...]]]
    required_together: NotRequired[list[tuple[str, ...]]]
    required_one_of: NotRequired[list[tuple[str, ...]]]
    required_if: NotRequired[list[tuple[str, ...]]]
    required_by: NotRequired[dict[str, Iterable[str]]]


def init_module(**kwargs: Unpack[ModuleParams]):
    module = AnsibleModule(**kwargs)
    if not HAS_YANDEX:
        module.fail_json(
            msg=missing_required_lib('yandexcloud'),
            exception=YANDEX_ERR,
        )
    return module
