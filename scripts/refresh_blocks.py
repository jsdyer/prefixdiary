"""Read CNA's national thousands-block edition and retain only public assignment fields."""
import csv
from datetime import date
import io
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from zipfile import ZipFile

SOURCE = 'https://cnac.ca/data/COBlockStatus_ALL.zip'
DEFAULT = Path(__file__).resolve().parents[1] / 'web/blocks.json'


def parse_blocks(payload):
    with ZipFile(io.BytesIO(payload)) as archive:
        member = archive.getinfo('COBlockStatus_ALL.csv')
        if member.file_size > 25_000_000:
            raise ValueError('Unexpectedly large CNA block edition')
        text = archive.read(member).decode('cp1252')
    reader = csv.DictReader(io.StringIO(text))
    fields = {'NPA', 'NXX', 'X', 'Status', 'Block Holder', 'Code Holder', 'Remarks', 'Assigned Date'}
    if not fields.issubset(reader.fieldnames or []):
        raise ValueError('Unexpected block column layout')
    edition = date.fromisoformat(next(reader)['Remarks']).isoformat()
    rows = {}
    for row in reader:
        key = '-'.join(row[field] for field in ('NPA','NXX','X'))
        if not re.fullmatch(r'[2-9][0-9]{2}-[2-9][0-9]{2}-[0-9]', key) or key in rows:
            raise ValueError('Invalid block key')
        if not row['Status'].strip():
            raise ValueError('Missing block status')
        rows[key] = [row['Status'], row['Block Holder'], row['Code Holder'], row['Assigned Date']]
    if not rows:
        raise ValueError('Empty block edition')
    return {'edition': edition, 'rows': rows}


def refresh_blocks(path=DEFAULT):
    request = Request(SOURCE, headers={'User-Agent':'CoolCode Prefix Diary (+https://coolcode.ca/prefixdiary/)'})
    with urlopen(request,timeout=45) as response:
        payload = response.read(10_000_001)
    if len(payload) > 10_000_000:
        raise ValueError('CNA block archive exceeded download limit')
    edition = parse_blocks(payload)
    if path.is_file() and json.loads(path.read_text())['edition'] > edition['edition']:
        raise ValueError('Refusing older thousands-block edition')
    pending = path.with_suffix('.tmp')
    pending.write_text(json.dumps(edition, ensure_ascii=False, separators=(',', ':')) + '\n')
    pending.replace(path)
