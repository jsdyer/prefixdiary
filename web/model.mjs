export const fields = ["Status","Pooled","Exchange","Province","Company","OCN","Date assigned","Remarks"];
export function phoneParts(value) {
  const text = value.trim();
  if (!/^(?:\+?1[ .()-]*)?[0-9(][0-9 ().-]*$/.test(text)) return null;
  let digits = text.replace(/\D/g, "");
  if ((digits.length === 11 || text.startsWith("+1")) && digits.startsWith("1")) digits = digits.slice(1);
  if (!/^[2-9]\d{2}[2-9]\d{2}(?:\d|\d{4})?$/.test(digits)) return null;
  const prefix = digits.slice(0,3) + "-" + digits.slice(3,6);
  return {prefix, block: digits.length > 6 ? prefix + "-" + digits[6] : null};
}

export function selectRows(rows,area,status,query,saved) {
  const needle = phoneParts(query)?.prefix || query.trim().toLowerCase();
  return rows.filter(([key,fields])=>
    (!area || key.startsWith(area+"-")) && (!status || fields[0]===status) &&
    (!saved || saved.has(key)) && (!needle || [key,...fields].join(" ").toLowerCase().includes(needle)));
}
export function changedFields(before,after) {
  if (!before) return "First listed · "+after[0];
  if (!after) return "Removed from the edition";
  return fields.flatMap((label,i)=>before[i]===after[i]?[]:[label+" "+(before[i]||"—")+" → "+(after[i]||"—")]).join(" · ");
}
