# Prefix Diary

[Open Prefix Diary](https://coolcode.ca/prefixdiary/) to search geographic Canadian NPA–NXX codes and see how their published assignments change over time. Choose 604 or 902, an exchange, a carrier or a status. Select a prefix to inspect its OCN, source assignment date, remarks and observed changes.

<!-- coolcode:guide -->
Search 902 and Halifax for telephone assignments. In Canadian IP registrations, compare UBC’s IPv4 block or BCNET’s IPv6 block in the 2016, 2020 and latest ARIN editions, then open its observed routing history.
<!-- /coolcode:guide -->

## Understanding the diary

The first complete national snapshot is the baseline. Later imports compare all eight published attributes by prefix and record both the earlier and later edition dates. A difference happened between two observations. The source assignment date is a separate field. An old assignment can first appear on the day monitoring begins. Same-date corrections can also appear. The diary shows the latest 60 changes matching your filters, with up to 20 more recent changes for a selected prefix. The CSV download includes all current matches. Saved prefixes are stored in this browser.

A prefix identifies a numbering resource. Number portability and the size of exchange areas mean that this data cannot establish a subscriber’s address or current carrier. Special, available and protected codes can lack an exchange or company. Company and pooling information is shown as supplied.

## Canadian IP registrations

[Open the IP directory](https://coolcode.ca/prefixdiary/ip/). Enter an IPv4 address, IPv6 address or aligned CIDR block to compare overlapping registrations in three reports. Try UBC (137.82.0.0), Dalhousie (129.173.0.0) or BCNET (2607:f8f0::). The extracts run in the browser. Following the RDAP link opens the current registration. Following the Route Archaeologist link looks up the address in public BGP observations.

The importer reads ARIN’s extended delegation reports of November 18, 2016 and November 18, 2020 and the latest report. It checks the file and per-family record counts before selecting Canadian IPv4 and IPv6 rows marked allocated or assigned. It preserves whole IPv4 ranges even when a range spans several CIDR blocks. IPv6 values are prefix lengths. The table counts matching records and displays up to ten per edition. The CA code describes the registered organization’s economy. A missing match means no overlapping qualifying Canadian row in that report. Holder names for the three examples come from the linked ARIN RDAP records.

The report date identifies the edition. The registration date can be unknown or can refer to an original registration at another registry. The observed reports do not establish when an intervening classification or range change occurred. Block counts include ranges of different sizes. Device locations and the number of users cannot be derived from them.

[ARIN report description](https://www.arin.net/reference/research/statistics/nro_stats/) · [report archive](https://ftp.arin.net/pub/stats/arin/archive/) · [exchange format](https://www.apnic.net/about-apnic/corporate-documents/documents/resource-guidelines/rir-statistics-exchange-format/).

## Data and maintenance

The [Canadian Numbering Administrator](https://cnac.ca/co_codes/co_code_status.htm) publishes a national [CO Code Status ZIP](https://cnac.ca/data/COCodeStatus_ALL.zip) on weekday nights. The publisher’s date comes from the CSV header record. The separate retrieved date records a successful UTC download. The Tuesday–Saturday GitHub Action follows the expected weekday-night Canadian publications. An older, duplicate-key or incomplete directory is rejected.

Run `python3 scripts/refresh.py` to fetch and compare telephone records and `python3 scripts/refresh_ip.py` for the ARIN extracts. The weekday workflow checks both sources. The IP importer reuses the two validated fixed archives and updates the latest report. Keep the previous `web/records.json.gz` when running it so observed history carries forward. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests` and `python3 scripts/build.py`. The site works from the committed snapshot and keeps searches in your browser.
