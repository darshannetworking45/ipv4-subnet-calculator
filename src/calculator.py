"""IPv4 calculation and VLSM engine."""
import ipaddress
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class SubnetDetails:
    cidr: str
    network_address: str
    broadcast_address: str
    netmask: str
    wildcard_mask: str
    prefix_length: int
    total_hosts: int
    usable_hosts: int
    first_usable: Optional[str]
    last_usable: Optional[str]
    binary_netmask: str

    def to_dict(self):
        return self.__dict__

def calculate_subnet(network_str: str) -> SubnetDetails:
    try:
        net = ipaddress.IPv4Network(network_str, strict=False)
    except Exception as e:
        raise ValueError(f"Invalid network format '{network_str}': {e}")

    wildcard_int = int(net.netmask) ^ 0xFFFFFFFF
    wildcard = str(ipaddress.IPv4Address(wildcard_int))

    if net.prefixlen == 32:
        usable = 1
        first_ip = str(net.network_address)
        last_ip = str(net.network_address)
        bcast = str(net.network_address)
    elif net.prefixlen == 31:
        usable = 2
        first_ip = str(net.network_address)
        last_ip = str(net.network_address + 1)
        bcast = "N/A (RFC 3021 Point-to-Point)"
    else:
        usable = max(0, net.num_addresses - 2)
        first_ip = str(net.network_address + 1)
        last_ip = str(net.broadcast_address - 1)
        bcast = str(net.broadcast_address)

    bin_mask = ".".join(f"{int(octet):08b}" for octet in str(net.netmask).split("."))

    return SubnetDetails(
        cidr=str(net),
        network_address=str(net.network_address),
        broadcast_address=bcast,
        netmask=str(net.netmask),
        wildcard_mask=wildcard,
        prefix_length=net.prefixlen,
        total_hosts=net.num_addresses,
        usable_hosts=usable,
        first_usable=first_ip,
        last_usable=last_ip,
        binary_netmask=bin_mask
    )

def plan_vlsm(base_cidr: str, requirements: List[Tuple[str, int]]) -> List[Dict]:
    """
    Plan VLSM allocating subnets for requested host counts.
    requirements: list of (name, host_count)
    """
    base_net = ipaddress.IPv4Network(base_cidr)

    sorted_reqs = sorted(requirements, key=lambda x: x[1], reverse=True)

    current_ip = int(base_net.network_address)
    allocations = []

    for name, hosts in sorted_reqs:

        needed_addresses = hosts + 2
        prefix = 32 - math.ceil(math.log2(needed_addresses))
        if prefix > 30:
            prefix = 30

        block_size = 2 ** (32 - prefix)

        if current_ip % block_size != 0:
            current_ip = ((current_ip // block_size) + 1) * block_size

        candidate_net = ipaddress.IPv4Network((current_ip, prefix))
        if not candidate_net.subnet_of(base_net):
            raise ValueError(f"Supernet {base_cidr} exhausted when allocating {name} ({hosts} hosts)")

        details = calculate_subnet(str(candidate_net))
        allocations.append({
            "name": name,
            "required_hosts": hosts,
            "allocated_subnet": str(candidate_net),
            "usable_capacity": details.usable_hosts,
            "wasted_hosts": details.usable_hosts - hosts,
            "first_usable": details.first_usable,
            "last_usable": details.last_usable
        })
        current_ip += block_size

    return allocations

def summarize_subnets(subnets: List[str]) -> List[str]:
    nets = [ipaddress.IPv4Network(s.strip()) for s in subnets]
    collapsed = ipaddress.collapse_addresses(nets)
    return [str(c) for c in collapsed]

def detect_overlap(subnets: List[str]) -> List[Tuple[str, str]]:
    nets = [ipaddress.IPv4Network(s.strip()) for s in subnets]
    overlaps = []
    for i in range(len(nets)):
        for j in range(i + 1, len(nets)):
            if nets[i].overlaps(nets[j]):
                overlaps.append((str(nets[i]), str(nets[j])))
    return overlaps
