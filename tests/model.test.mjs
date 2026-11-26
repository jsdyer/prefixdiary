import test from "node:test";
import assert from "node:assert/strict";
import {selectRows,changedFields} from "../web/model.mjs";
const d=[["902-200",["In Service","N","Halifax","NS","Example","1","",""]],["604-200",["Available","N","","","","","",""]]];
test("prefix, town, area and bookmarks combine",()=>{
 assert.equal(selectRows(d,"902","","hali",null).length,1);
 assert.equal(selectRows(d,"","","902200",null)[0][0],"902-200");
 assert.equal(selectRows(d,"604","","",new Set(["902-200"])).length,0);
});
test("assignment edits identify the changed field",()=>assert.match(changedFields(d[0][1],d[1][1]),/Status In Service → Available/));

import {phoneParts} from '../web/model.mjs';
test('ported-number lookup keeps only publicly assigned prefix and thousands block', () => {
  assert.deepEqual(phoneParts('+1 (942) 945-4123'), {prefix:'942-945',block:'942-945-4'});
  assert.deepEqual(phoneParts('902-200'), {prefix:'902-200',block:null});
  assert.equal(phoneParts('Halifax'),null);
});
