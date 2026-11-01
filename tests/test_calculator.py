import unittest
from src.calculator import calculate_subnet, plan_vlsm, summarize_subnets, detect_overlap

class TestSubnetCalculator(unittest.TestCase):
    def test_calculate_standard_c(self):
        info = calculate_subnet("192.0.2.0/24")
        self.assertEqual(info.network_address, "192.0.2.0")
        self.assertEqual(info.broadcast_address, "192.0.2.255")
        self.assertEqual(info.usable_hosts, 254)
        self.assertEqual(info.wildcard_mask, "0.0.0.255")
        self.assertEqual(info.first_usable, "192.0.2.1")
        self.assertEqual(info.last_usable, "192.0.2.254")

    def test_rfc3021_p2p(self):
        info = calculate_subnet("198.51.100.0/31")
        self.assertEqual(info.usable_hosts, 2)
        self.assertEqual(info.first_usable, "198.51.100.0")
        self.assertEqual(info.last_usable, "198.51.100.1")

    def test_vlsm_planning(self):
        reqs = [("Servers", 50), ("Workstations", 100), ("Management", 10)]
        plan = plan_vlsm("10.10.0.0/23", reqs)
        self.assertEqual(len(plan), 3)

        self.assertEqual(plan[0]["name"], "Workstations")
        self.assertEqual(plan[0]["allocated_subnet"], "10.10.0.0/25")
        self.assertEqual(plan[1]["name"], "Servers")
        self.assertEqual(plan[1]["allocated_subnet"], "10.10.0.128/26")

    def test_summarization(self):
        subnets = ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"]
        summary = summarize_subnets(subnets)
        self.assertEqual(summary, ["192.168.0.0/22"])

    def test_overlap_detection(self):
        subnets = ["10.0.0.0/16", "10.0.1.0/24", "192.168.1.0/24"]
        overlaps = detect_overlap(subnets)
        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0], ("10.0.0.0/16", "10.0.1.0/24"))

if __name__ == "__main__":
    unittest.main()
