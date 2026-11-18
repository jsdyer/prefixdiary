# Prefix Diary

[Open Prefix Diary](https://coolcode.ca/prefixdiary/) to search geographic Canadian NPA–NXX codes and see how their published assignments change over time. Choose 604 or 902, an exchange, a carrier or a status. Select a prefix to inspect its OCN, source assignment date, remarks and observed changes.

<!-- coolcode:guide -->
Choose 902 and search Halifax to see which companies hold prefixes in that exchange. Save individual prefixes to revisit them and watch later changes to their published status or assignment.
<!-- /coolcode:guide -->

## Understanding the diary

The first complete national snapshot is the baseline. Later imports compare all eight published attributes by prefix and record both the earlier and later edition dates. A difference happened between two observations. The source assignment date is a separate field. An old assignment can first appear on the day monitoring begins. Same-date corrections can also appear. The diary shows the latest 60 changes matching your filters, with up to 20 more recent changes for a selected prefix. The CSV download includes all current matches. Saved prefixes are stored in this browser.

A prefix identifies a numbering resource. Number portability and the size of exchange areas mean that this data cannot establish a subscriber’s address or current carrier. Special, available and protected codes can lack an exchange or company. Company and pooling information is shown as supplied.

## Data and maintenance

The [Canadian Numbering Administrator](https://cnac.ca/co_codes/co_code_status.htm) publishes a national [CO Code Status ZIP](https://cnac.ca/data/COCodeStatus_ALL.zip) on weekday nights. The publisher’s date comes from the CSV header record. The separate retrieved date records a successful UTC download. The Tuesday–Saturday GitHub Action follows the expected weekday-night Canadian publications. An older, duplicate-key or incomplete directory is rejected.

Run `python3 scripts/refresh.py` to fetch and compare records. Keep the previous `web/records.json.gz` when running it so observed history carries forward. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests` and `python3 scripts/build.py`. The site works from the committed snapshot and keeps searches in your browser.
