"""Build Canadian registration extracts from ARIN's extended delegation reports."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import ipaddress
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1] / "web" / "ip"
BASE = "https://ftp.arin.net/pub/stats/arin/"
ARCHIVES = ["20161118", "20201118"]


def source_date(value):
    if value in ("", "00000000"):
        return None
    return datetime.strptime(value, "%Y%m%d").date().isoformat()


def extract(text):
    lines = [line.split("|") for line in text.splitlines() if line and not line.startswith("#")]
    header = lines.pop(0)
    if len(header) != 7 or header[1] != "arin" or not header[0].startswith("2."):
        raise ValueError("Unexpected ARIN header")
    edition = source_date(header[5])
    declared, actual = {}, Counter()
    records = []
    for row in lines:
        if len(row) == 6 and row[-1] == "summary":
            declared[row[2]] = int(row[4])
            continue
        registry, country, family, start, value, issued, status = row[:7]
        if registry != "arin":
            raise ValueError("Unexpected registry")
        actual[family] += 1
        if country != "CA" or family not in ("ipv4", "ipv6") or status not in ("assigned", "allocated"):
            continue
        first = ipaddress.ip_address(start)
        if family != f"ipv{first.version}":
            raise ValueError("Address family mismatch")
        value = int(value)
        if first.version == 4:
            if value <= 0:
                raise ValueError("Invalid address count")
            last = first + (value - 1)
            blocks = list(ipaddress.summarize_address_range(first, last))
            label = str(blocks[0]) if len(blocks) == 1 else f"{first} – {last}"
        else:
            net = ipaddress.IPv6Network((first, value), strict=True)
            last, label = net.broadcast_address, str(net)
        records.append([str(first), str(last), label, source_date(issued), status])
    if not edition or int(header[3]) != sum(actual.values()) or declared != dict(actual):
        raise ValueError("Incomplete ARIN report")
    return edition, records


def refresh(root=ROOT):
    root.mkdir(exist_ok=True)
    previous = json.loads((root / "status.json").read_text()) if (root / "status.json").exists() else {}
    entries = []
    with TemporaryDirectory(dir=root) as folder:
        stage = Path(folder)
        for key in [*ARCHIVES, "latest"]:
            filename = key + ".json.gz"
            url = (BASE + f"archive/{key[:4]}/delegated-arin-extended-{key}.gz"
                   if key != "latest" else BASE + "delegated-arin-extended-latest")
            if key in ARCHIVES and (root / filename).exists():
                saved = next((s for s in previous.get("editions", []) if s["file"] == filename), None)
                if saved:
                    entries.append(saved)
                    continue
            with urlopen(url, timeout=90) as response:
                raw = response.read()
            if raw.startswith(b"\x1f\x8b"):
                raw = gzip.decompress(raw)
            edition, records = extract(raw.decode("utf-8"))
            v4 = sum(":" not in row[0] for row in records)
            v6 = len(records) - v4
            if v4 < 1000 or v6 < 100 or (key in ARCHIVES and source_date(key) != edition):
                raise ValueError("Unexpected Canadian IP coverage or edition")
            if key == "latest" and edition < previous.get("latest", ""):
                raise ValueError("Stale ARIN edition")
            output = json.dumps(records, separators=(",", ":")).encode()
            (stage / filename).write_bytes(gzip.compress(output, mtime=0))
            entries.append({"file": filename, "date": edition, "source": url, "ipv4": v4, "ipv6": v6})
        latest = entries[-1]
        status = {"retrieved": datetime.now(timezone.utc).date().isoformat(), "latest": latest["date"],
                  "count": latest["ipv4"] + latest["ipv6"], "editions": entries}
        (stage / "status.json").write_text(json.dumps(status, separators=(",", ":")) + "\n")
        for path in stage.iterdir():
            path.replace(root / path.name)
    return status


if __name__ == "__main__":
    print(refresh())
