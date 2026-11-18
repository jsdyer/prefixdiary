"""Record changes between complete Canadian Numbering Administrator editions."""
from datetime import date, datetime, timezone
import csv
import gzip
import io
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'web'
SOURCE = 'https://cnac.ca/data/COCodeStatus_ALL.zip'
FIELDS = ['NPA','CO Code (NXX)','Status','Pooled','Exchange Area','Province','Company','OCN','Date Assigned','Remarks']


def parse(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        source = archive.read('COCodeStatus_ALL.csv').decode('cp1252')
    reader = csv.reader(io.StringIO(source))
    if next(reader) != FIELDS:
        raise ValueError('Unexpected CNA column headings')
    edition = date.fromisoformat(next(reader)[-1]).isoformat()
    rows = {}
    for npa, code, *attributes in reader:
        if not re.fullmatch('[2-9][0-9]{2}', npa) or not re.fullmatch('[2-9][0-9]{2}', code) or len(attributes) != 8:
            raise ValueError('Invalid code record')
        key = npa + '-' + code
        if key in rows:
            raise ValueError('Duplicate prefix '+key)
        rows[key] = attributes
    counts = {}
    for key in rows:
        counts[key[:3]] = counts.get(key[:3], 0) + 1
    if len(counts) < 40 or any(n != 800 for n in counts.values()):
        raise ValueError('Incomplete national edition')
    return edition, rows


def compare(last, new, earlier, later):
    return [[earlier,later,key,last.get(key),new.get(key)] for key in sorted(last.keys() | new.keys()) if last.get(key) != new.get(key)]


def update(payload, path=ROOT):
    edition, rows = parse(payload)
    packed = path/'records.json.gz'
    doc = json.loads(gzip.decompress(packed.read_bytes())) if packed.exists() else {}
    first = doc.get('first', edition)
    changes = doc.get('changes', [])
    if doc:
        if edition < doc['latest']:
            raise ValueError('Refusing older edition')
        if {k[:3] for k in doc['rows']} - {k[:3] for k in rows}:
            raise ValueError('An entire published area code disappeared; review the change')
        changes += compare(doc['rows'], rows, doc['latest'], edition)
    document = dict(first=first,latest=edition,rows=rows,changes=changes)
    body=json.dumps(document,ensure_ascii=False,separators=(',',':')).encode()
    packed.with_suffix('.tmp').write_bytes(gzip.compress(body,mtime=0))
    packed.with_suffix('.tmp').replace(packed)
    stats=dict(retrieved=datetime.now(timezone.utc).date().isoformat(),latest=edition,first=first,count=len(rows),areas=len(set(k[:3] for k in rows)),changes=len(changes))
    (path/'status.json').write_text(json.dumps(stats, indent=2)+'\n')


if __name__=='__main__':
    req=Request(SOURCE,headers={'User-Agent':'CoolCode Prefix Diary (+https://coolcode.ca/prefixdiary/)'})
    with urlopen(req,timeout=50) as response:
        update(response.read())
