# IPv4 Subnet and VLSM Calculator

Calculates IPv4 network details, plans variable-length subnet allocations, summarizes adjacent networks, and detects overlaps.

## Main entry points

- `src.calculator.SubnetDetails` (`to_dict`)
- `src.calculator.calculate_subnet()`
- `src.calculator.plan_vlsm()`
- `src.calculator.summarize_subnets()`
- `src.calculator.detect_overlap()`
- `src.cli.main()`

## Run the tests

```bash
python -m unittest discover -s tests -v
```

The project uses the Python standard library; no third-party package is required.

## Scope

The calculator uses Python `ipaddress` and returns calculated data; it does not allocate addresses in a live IPAM service.
