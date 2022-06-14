from __future__ import annotations

from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2 import ListNetworkLoadBalancersRequest
from yandex.cloud.loadbalancer.v1.network_load_balancer_service_pb2_grpc import NetworkLoadBalancerServiceStub

from ..module_utils.basic import NotFound


def get_nlb_id(client: NetworkLoadBalancerServiceStub, folder_id: str, name: str) -> str:
    nlbs = client.List(
        ListNetworkLoadBalancersRequest(folder_id=folder_id, filter=f'name="{name}"'),
    ).network_load_balancers
    if not nlbs:
        raise NotFound(f'function {name} not found')
    return nlbs[0].id
