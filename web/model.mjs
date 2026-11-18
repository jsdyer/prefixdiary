export const fields = ["Status","Pooled","Exchange","Province","Company","OCN","Date assigned","Remarks"];
export function selectRows(rows,area,status,query,saved) {
  const needle=query.trim().toLowerCase().replace(/^(\d{3})[ -]?(\d{3})$/,"$1-$2");
  return rows.filter(([key,fields])=>
    (!area || key.startsWith(area+"-")) && (!status || fields[0]===status) &&
    (!saved || saved.has(key)) && (!needle || [key,...fields].join(" ").toLowerCase().includes(needle)));
}
export function changedFields(before,after) {
  if (!before) return "First listed · "+after[0];
  if (!after) return "Removed from the edition";
  return fields.flatMap((label,i)=>before[i]===after[i]?[]:[label+" "+(before[i]||"—")+" → "+(after[i]||"—")]).join(" · ");
}
