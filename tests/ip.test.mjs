import test from "node:test";
import assert from "node:assert/strict";
import { addressWindow, indexRows, overlapping } from "../web/ip/model.mjs";

test("exact IPv4 range edges and overlapping blocks", () => {
  const rows = indexRows([
    ["192.0.2.4", "192.0.2.6", "192.0.2.4 – 192.0.2.6", null, "assigned"],
    ["192.0.2.8", "192.0.2.15", "192.0.2.8/29", "2000-01-01", "allocated"],
  ]);
  assert.deepEqual(overlapping(rows, addressWindow("192.0.2.6")), [rows[0]]);
  assert.deepEqual(overlapping(rows, addressWindow("192.0.2.7")), []);
  assert.deepEqual(overlapping(rows, addressWindow("192.0.2.0/28")), rows);
  for (const input of ["192.0.2.1/28", "192.0.2.1/", "192.0.2.1/33", "192.0.2.01", "123"])
    assert.throws(() => addressWindow(input));
});

test("full-width IPv6 integer arithmetic, address family separation, strict prefixes", () => {
  const q = addressWindow("2001:db8::/32");
  assert.equal(q.last - q.first + 1n, 2n ** 96n);
  assert.equal(addressWindow("2001:db8:ffff:ffff:ffff:ffff:ffff:ffff").first, q.last);
  assert.equal(addressWindow("::ffff:192.0.2.1").first, addressWindow("::ffff:c000:201").first);
  const v4 = indexRows([["0.0.0.0", "0.0.0.255", "0.0.0.0/24", null, "assigned"]]);
  assert.deepEqual(overlapping(v4, addressWindow("::/0")), []);
  for (const input of ["::1/129", "::::1", "1:2:3", "fe80::1%eth0", "[::1]:80"])
    assert.throws(() => addressWindow(input));
});
