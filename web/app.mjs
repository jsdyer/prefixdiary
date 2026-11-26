import {byId as el, element, option, loadData, csvDownload} from "./shared.mjs";
import {fields,selectRows,changedFields,phoneParts} from "./model.mjs";
const pageSize=35;
let all=[], matches=[], page=0, dataset, currentKey;
let saved=new Set();
try { saved=new Set(JSON.parse(localStorage.getItem("coolcode:prefixdiary:saved"))||[]); } catch {}
function details(key,focus=false) {
  const box=el("record"), attrs=dataset.rows[key];currentKey=key;
  if (!attrs) {box.hidden=true;return;}
  const heading=element("h3",key+" · "+(attrs[2]||attrs[0]));
  const info=element("p",fields.map((name,i)=>attrs[i]?name+" · "+attrs[i]:null).filter(Boolean).join("  |  "));
  const marks=dataset.changes.filter(c=>c[2]===key);
  const note=element("p",marks.length?marks.length+" recorded changes since "+dataset.first:"No recorded changes since the "+dataset.first+" baseline.");
  const button=element("button",saved.has(key)?"Remove saved prefix":"Save prefix");
  button.onclick=()=>{
    if(saved.has(key)) saved.delete(key);else saved.add(key);
    try {localStorage.setItem("coolcode:prefixdiary:saved",JSON.stringify([...saved]));} catch {}
    filter();details(key);
  };
  box.replaceChildren(heading,info,note,...marks.slice(-20).reverse().map(([a,b,,old,next])=>element("p",b+" · "+changedFields(old,next))),button);
  box.hidden=false;
  if(focus) {heading.tabIndex=-1;heading.focus();}
}
function display() {
  el("rows").replaceChildren(...matches.slice(page*pageSize,(page+1)*pageSize).map(([key,d])=>{
    const tr=element("tr"), cell=element("td"), link=element("button",key);
    link.onclick=()=>details(key,true);cell.append(link);tr.append(cell);
    for (const value of [d[2],d[3],d[4],d[0]]) tr.append(element("td",value||"—"));
    return tr;
  }));
  el("summary").textContent=matches.length?matches.length.toLocaleString()+" matches · "+(page*pageSize+1)+"–"+Math.min(matches.length,(page+1)*pageSize):"No matching prefixes.";
  el("prev").disabled=page===0;el("next").disabled=(page+1)*pageSize>=matches.length;
  el("download").disabled=!matches.length;
}
function history(){
  const keys=new Set(matches.map(r=>r[0]));
  const changes=dataset.changes.filter(c=>keys.has(c[2]) || (!c[4] && selectRows([[c[2],c[3]]],el("area").value,el("status").value,el("query").value,el("saved").checked?saved:null).length));
  el("history-note").textContent="Baseline "+dataset.first+" · "+changes.length+" matching changes observed through "+dataset.latest+". Assignment dates above come from the publisher. Changes are dated by the editions in which they appeared.";
  el("history").replaceChildren(...changes.slice(-60).reverse().map(([earlier,later,key,before,after])=>element("p",key+" · "+earlier+" → "+later+" · "+changedFields(before,after))));
}
let blocks;
const blockStatus = {AV:'Available',AF:'Available (future)',AP:'Available (pending)',AS:'Assigned',IS:'In service',BR:'Being recovered',RA:'Recovered / aging'};
function showBlock() {
  const number = phoneParts(el("query").value);
  const note = el("block");
  note.textContent = "";
  if (!number?.block) return;
  if (!blocks) {
    note.textContent = "Thousands-block data is unavailable. The table shows prefix-level assignments.";
    return;
  }
  const details = blocks.rows[number.block];
  if (!details) {
    note.textContent = "No separate thousands-block entry for " + number.block + " in the " + blocks.edition + " CNA edition. See the prefix assignment below.";
    return;
  }
  const [status, holder, codeHolder, assigned] = details;
  note.textContent = [number.block + "xxx", blockStatus[status] || status, holder ? "Block holder: " + holder : "No separate block holder listed",
    codeHolder && "Prefix holder: " + codeHolder, assigned && "Assigned " + assigned, "CNA edition " + blocks.edition].filter(Boolean).join(" · ");
}
function filter(){ page=0;matches=selectRows(all,el("area").value,el("status").value,el("query").value,el("saved").checked?saved:null);el("record").hidden=true;display();history();showBlock(); }
try {
  const [status,records]=await loadData();dataset=records;all=Object.entries(records.rows).sort(([a],[b])=>a.localeCompare(b));
  for(const n of [...new Set(all.map(([key])=>key.slice(0,3)))]) el("area").add(option(n));
  for(const name of [...new Set(all.map(([,d])=>d[0]))].sort()) el("status").add(option(name));
  el("edition").textContent=status.count.toLocaleString()+" prefixes · "+status.areas+" area codes · CNA edition "+status.latest+" · retrieved "+status.retrieved;
  for(const id of ["area","status","saved"]) el(id).onchange=filter;
  el("query").oninput=filter;
  el("prev").onclick=()=>{page--;display()};el("next").onclick=()=>{page++;display()};
  el("download").onclick=()=>csvDownload("prefixdiary-"+dataset.latest+".csv",[["Prefix",...fields],...matches.map(([key,d])=>[key,...d])]);
  el("query").value = document.body.dataset.query || "";
  filter();
  try {
    const response = await fetch(new URL("./blocks.json", import.meta.url));
    if (response.ok) blocks = await response.json();
  } catch { /* Prefix-level records remain available. */ }
  showBlock();
} catch {el("edition").textContent="Unable to load the published snapshot. Try reloading or use the CNA source below.";}
