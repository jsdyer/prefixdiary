"""Generate crawlable working examples from the same form as the main page."""
from html import escape
import json
import gzip
import re


def render_pages(stage, tool, pages):
    source = (stage / "index.html").read_text(encoding="utf-8")
    for path, title, description, defaults in pages:
        folder = stage / path
        folder.mkdir(exist_ok=True)
        url = "https://coolcode.ca" + tool["url"] + (path + "/" if path else "")
        page = re.sub(r"<title>.*?</title>", lambda _: "<title>" + escape(title) + " · CoolCode</title>", source, count=1)
        page = re.sub(r'<meta name="description" content="[^"]*">', lambda _: '<meta name="description" content="' + escape(description) + '">', page, count=1)
        page = re.sub(r'<link rel="canonical"[^>]*>|<meta property="og:[^>]*>', "", page)
        head = '<link rel="canonical" href="' + escape(url) + '">'
        for prop, value in (("title", title), ("type", "website"), ("url", url), ("description", description)):
            head += '<meta property="og:' + prop + '" content="' + escape(value) + '">'
        schema = {"@context":"https://schema.org","@type":"WebApplication","name":title,"url":url,"description":description,"operatingSystem":"Any","applicationCategory":"UtilitiesApplication","offers":{"@type":"Offer","price":"0","priceCurrency":"CAD"}}
        page = page.replace("</head>", head + '<script type="application/ld+json">' + json.dumps(schema).replace("<", "\\u003c") + "</script></head>", 1)
        if path:
            page = re.sub(r'((?:href|src)=")\./', r'\1../', page)
            page = re.sub(r"(<h1(?: [^>]*)?>).*?</h1>", lambda m: m[1] + escape(title) + "</h1>", page, count=1, flags=re.S)
            page = page.replace("<!-- example-intro -->", '<p class="example-intro">' + escape(description) + '</p>', 1)
            attrs = "".join(' data-' + key + '="' + escape(value) + '"' for key, value in defaults.items())
            page = page.replace("<body", "<body" + attrs, 1)
        if defaults.get("query"):
            records = json.loads(gzip.decompress((stage / "records.json.gz").read_bytes()))
            matching = [(key, row) for key, row in sorted(records["rows"].items()) if defaults["query"].lower() in " ".join([key, *row]).lower()]
            preview = "".join("<tr>" + "".join("<td>" + escape(value or "—") + "</td>" for value in (key, row[2], row[3], row[4], row[0])) + "</tr>" for key, row in matching[:12])
            page = page.replace('id="query" type="search"', 'id="query" value="' + escape(defaults["query"]) + '" type="search"')
            page = page.replace('<tbody id="rows"></tbody>', '<tbody id="rows">' + preview + "</tbody>")
            page = page.replace('id="summary" class="summary" role="status"></p>', 'id="summary" class="summary" role="status">' + str(len(matching)) + " matching prefixes in the " + escape(records["latest"]) + " edition.</p>")
        (folder / "index.html").write_text(page, encoding="utf-8")

PAGES = [('',
  'Canadian Phone Prefix Lookup',
  'Paste a Canadian phone number or search by city to find its numbering-block assignment, '
  'exchange and province.',
  {}),
 ('halifax-phone-prefixes',
  'Halifax Phone Prefixes & Exchange Assignments',
  'Browse Halifax exchanges across area codes, see which companies hold the assignments, and open '
  'a row to read its dated history.',
  {'query': 'Halifax'}),
 ('vancouver-phone-prefixes',
  'Vancouver Phone Prefixes & Exchange Assignments',
  'Find Vancouver telephone exchanges across overlapping BC area codes. Paste a number to inspect '
  'its prefix and a published thousands-block assignment where available.',
  {'query': 'Vancouver'})]
