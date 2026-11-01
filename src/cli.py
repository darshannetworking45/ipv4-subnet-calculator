"""CLI entry point for IPv4 calculator."""
import argparse
import json
from src.calculator import calculate_subnet, plan_vlsm, summarize_subnets, detect_overlap

def main():
    parser = argparse.ArgumentParser(description="IPv4 Subnet Calculator and VLSM Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    calc_p = subparsers.add_parser("info", help="Inspect subnet details")
    calc_p.add_argument("cidr", help="Network CIDR (e.g., 192.168.1.0/24)")

    vlsm_p = subparsers.add_parser("vlsm", help="VLSM planning")
    vlsm_p.add_argument("--base", required=True, help="Base supernet (e.g., 10.0.0.0/20)")
    vlsm_p.add_argument("--reqs", nargs="+", required=True, help="Format: Name:HostCount (e.g. LAN1:100 LAN2:50)")

    overlap_p = subparsers.add_parser("overlap", help="Check overlap between subnets")
    overlap_p.add_argument("subnets", nargs="+", help="Subnets list")

    args = parser.parse_args()

    if args.command == "info":
        details = calculate_subnet(args.cidr)
        for k, v in details.to_dict().items():
            print(f"{k.replace('_', ' ').title():<22}: {v}")

    elif args.command == "vlsm":
        reqs = []
        for r in args.reqs:
            parts = r.split(":")
            reqs.append((parts[0], int(parts[1])))
        res = plan_vlsm(args.base, reqs)
        print(f"{'NAME':<12} {'REQUIRED':<10} {'ALLOCATED':<18} {'USABLE':<8} {'RANGE':<32}")
        print("-" * 80)
        for row in res:
            rng = f"{row['first_usable']} - {row['last_usable']}"
            print(f"{row['name']:<12} {row['required_hosts']:<10} {row['allocated_subnet']:<18} {row['usable_capacity']:<8} {rng:<32}")

    elif args.command == "overlap":
        conflicts = detect_overlap(args.subnets)
        if conflicts:
            print("Detected overlaps:")
            for c1, c2 in conflicts:
                print(f"  Conflict: {c1} <--> {c2}")
        else:
            print("No overlaps detected. Subnets are mutually exclusive.")

if __name__ == "__main__":
    main()
