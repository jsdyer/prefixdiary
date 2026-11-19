import { byId, element } from "../shared.mjs";
import { addressWindow, indexRows, overlapping } from "./model.mjs";

function link(text, href) {
  const a = element("a", text);
  a.href = href;
  return a;
}

function row(values) {
  const tr = element("tr");
  for (const value of values) {
    const cell = element("td");
    cell.append(value);
    tr.append(cell);
  }
  return tr;
}

async function loadEdition(info) {
  const response = await fetch("./" + info.file);
  if (!response.ok) throw Error("Registry extract unavailable");
  const bytes = new Uint8Array(await response.arrayBuffer());
  const body = bytes[0] === 31 && bytes[1] === 139 ?
    new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip")) : bytes;
  return { ...info, rows: indexRows(await new Response(body).json()) };
}

try {
  const response = await fetch("./status.json");
  if (!response.ok) throw Error("No registry status");
  const meta = await response.json();
  const editions = await Promise.all(meta.editions.map(loadEdition));
  byId("edition").textContent = "Latest report " + meta.latest + " · retrieved " + meta.retrieved + " UTC";
  for (const e of editions) {
    byId("coverage").append(row([e.date, e.ipv4.toLocaleString("en-CA"), e.ipv6.toLocaleString("en-CA"),
      link(e.file.startsWith("latest") ? "Current ARIN file" : "Archived ARIN file", e.source)]));
  }

  function draw() {
    const query = byId("query").value.trim();
    byId("matches").replaceChildren();
    byId("handoff").replaceChildren();
    let range;
    try { range = addressWindow(query); }
    catch (error) { byId("result").textContent = error.message; return; }
    const counts = [];
    for (const edition of editions) {
      const found = overlapping(edition.rows, range);
      counts.push(edition.date + " · " + found.length.toLocaleString("en-CA"));
      for (const r of found.slice(0, 10)) {
        byId("matches").append(row([edition.date, r.block, r.status, r.date || "Unreported"]));
      }
      if (!found.length) byId("matches").append(row([edition.date, "No matching CA registration", "—", "—"]));
      if (found.length > 10) byId("matches").append(row([edition.date, "Showing the first 10 of " +
        found.length.toLocaleString("en-CA") + " overlapping records", "—", "—"]));
    }
    byId("result").textContent = "Matching records for " + query + " by report date: " + counts.join(" / ") + ".";
    byId("handoff").append(link("Inspect the current ARIN RDAP record", "https://rdap.arin.net/registry/ip/" + query),
      " · ", link("Check observed BGP routing", "https://coolcode.ca/routearchaeologist/#" +
        new URLSearchParams({ q: query })), ". Opening a link sends the selected address to that lookup.");
  }

  byId("lookup").addEventListener("submit", (event) => { event.preventDefault(); draw(); });
  for (const button of document.querySelectorAll("[data-ip]")) {
    button.addEventListener("click", () => { byId("query").value = button.dataset.ip; draw(); });
  }
  draw();
} catch {
  byId("edition").textContent = "Could not load the registry extracts. Reload the page to try again.";
}
