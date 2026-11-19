function integerAddress(text) {
  if (text.includes(":")) {
    if (!/^[0-9a-f:.]+$/i.test(text)) throw Error("Enter an IPv6 address without a zone or port.");
    let groups;
    try {
      groups = new URL("http://[" + text + "]/").hostname.slice(1, -1).split("::");
    } catch { throw Error("Check the IPv6 address."); }
    const left = groups[0] ? groups[0].split(":") : [];
    const right = groups[1] ? groups[1].split(":") : [];
    const words = [...left, ...Array(8 - left.length - right.length).fill("0"), ...right];
    return { bits: 128, value: BigInt("0x" + words.map((s) => s.padStart(4, "0")).join("")) };
  }
  const parts = text.split(".");
  if (parts.length !== 4 || parts.some((s) => !/^(0|[1-9]\d{0,2})$/.test(s) || Number(s) > 255))
    throw Error("Enter a dotted IPv4 address or a colon-separated IPv6 address.");
  return { bits: 32, value: parts.reduce((n, s) => n * 256n + BigInt(s), 0n) };
}

export function addressWindow(query) {
  const parts = query.trim().split("/");
  const { bits, value } = integerAddress(parts[0]);
  const length = parts.length === 1 ? bits : Number(parts[1]);
  if (parts.length > 2 || (parts.length === 2 && !/^(0|[1-9]\d*)$/.test(parts[1])) || length > bits)
    throw Error("Choose a prefix length between 0 and " + bits + ".");
  const size = 1n << BigInt(bits - length);
  if (value % size) throw Error("For CIDR notation, enter the first address of the network.");
  return { bits, first: value, last: value + size - 1n };
}

export function indexRows(rows) {
  return rows.map(([first, last, block, date, status]) => {
    const start = integerAddress(first);
    return { bits: start.bits, first: start.value, last: integerAddress(last).value, block, date, status };
  });
}

export function overlapping(rows, range) {
  return rows.filter((r) => r.bits === range.bits && r.first <= range.last && r.last >= range.first);
}
