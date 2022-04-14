from __future__ import annotations

import contextlib
import json
from typing import Any
from typing import Generator
from typing import Mapping

import grpc
import yandexcloud
from ansible.errors import AnsibleError
from ansible.module_utils.basic import AnsibleModule


def _get_auth_settings(
    params: Mapping[str, str],
) -> dict[str, Any]:
    config = {}
    if params.get('auth_kind') == 'oauth':
        token = params.get('oauth_token')
        if not token:
            raise AnsibleError('oauth_token should be set')
        config['token'] = token

    if params.get('auth_kind') == 'sa_file':
        sa_path = params.get('sa_path')
        sa_content = params.get('sa_content')
        if sa_path:
            with open(sa_path) as f:
                sa_key = json.load(f)
        elif sa_content:
            sa_key = json.loads(sa_content)
        else:
            raise AnsibleError(
                "Either 'sa_path' or 'sa_content' must be set"
                " when 'auth_kind' is set to 'sa_file'",
            )
        config['service_account_key'] = sa_key

    return config


def init_sdk(params: Mapping[str, str]) -> yandexcloud.SDK:
    return yandexcloud.SDK(
        interceptor=yandexcloud.RetryInterceptor(
            max_retry_count=5,
            retriable_codes=[grpc.StatusCode.UNAVAILABLE],
        ),
        **_get_auth_settings(params),
    )


@contextlib.contextmanager
def log_error(module: AnsibleModule) -> Generator[None, None, None]:
    try:
        yield
    except grpc._channel._InactiveRpcError as e:
        (state,) = e.args
        module.fail_json(msg=state.details)
