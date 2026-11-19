from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from refresh_ip import extract


class RegistryTests(unittest.TestCase):
    example = """2.3|arin|1|4|19700101|20201118|-0500
arin|*|ipv4|*|3|summary
arin|*|ipv6|*|1|summary
arin|CA|ipv4|192.0.2.4|3|00000000|assigned|1
arin|US|ipv4|198.51.100.0|256|20001231|allocated|2
arin|CA|ipv6|2001:db8::|48|20110613|allocated|3
arin|CA|ipv4|255.255.255.255|1|20110613|assigned|4
"""

    def test_dates_families_non_cidr_range_and_scope(self):
        edition, rows = extract(self.example)
        self.assertEqual(edition, "2020-11-18")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ["192.0.2.4", "192.0.2.6", "192.0.2.4 – 192.0.2.6", None, "assigned"])
        self.assertEqual(rows[1][2:], ["2001:db8::/48", "2011-06-13", "allocated"])
        self.assertEqual(rows[2][2], "255.255.255.255/32")

    def test_truncated_report_and_invalid_networks_rejected(self):
        for modified in (self.example.replace("|4|19700101", "|5|19700101"),
                         self.example.replace("ipv4|*|3|summary", "ipv4|*|2|summary"),
                         self.example.replace("2001:db8::|48", "2001:db8::1|48")):
            with self.assertRaises(ValueError):
                extract(modified)
