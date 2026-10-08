/* Pure temporal state and monthly aggregation, reusable by any topic. */
(function(root){
"use strict";
const DATE=/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/;
function validDate(s){
 if(typeof s!=="string"||!DATE.test(s))return false;
 const [y,m,d]=s.split("-").map(Number);
 return new Date(Date.UTC(y,m,0)).getUTCDate()>=d;
}
function monthBounds(month){
 if(typeof month!=="string"||!/^\d{4}-(0[1-9]|1[0-2])$/.test(month))throw new TypeError("Invalid month");
 const [y,m]=month.split("-").map(Number);
 return Object.freeze({from:month+"-01",to:month+"-"+String(new Date(Date.UTC(y,m,0)).getUTCDate()).padStart(2,"0")});
}
function normalizeRange(from="",to=""){
 if(from&&!validDate(from))throw new TypeError("Invalid start date");
 if(to&&!validDate(to))throw new TypeError("Invalid end date");
 return Object.freeze(from&&to&&from>to?{from:to,to:from}:{from,to});
}
function contains(date,range){
 if(!range.from&&!range.to)return true;
 return validDate(date)&&(!range.from||date>=range.from)&&(!range.to||date<=range.to);
}
function monthlyCounts(items,dateOf=item=>item.date){
 const counts=new Map();
 for(const item of items){const date=dateOf(item);if(!validDate(date))continue;const month=date.slice(0,7);counts.set(month,(counts.get(month)||0)+1)}
 return [...counts].sort(([a],[b])=>a.localeCompare(b)).map(([month,count])=>Object.freeze({month,count}));
}
function createTemporalState(onChange=()=>{}){
 let range=normalizeRange();
 return Object.freeze({
  getRange(){return range},
  setRange(from="",to=""){range=normalizeRange(from,to);onChange(range);return range},
  selectMonth(month){const bounds=monthBounds(month);return this.setRange(bounds.from,bounds.to)},
  clear(){return this.setRange()},
  matches(date){return contains(date,range)},
  filter(items,dateOf=item=>item.date){return items.filter(item=>contains(dateOf(item),range))}
 });
}
const api=Object.freeze({validDate,monthBounds,normalizeRange,contains,monthlyCounts,createTemporalState});
root.UbikTemporal=api;
if(typeof module!=="undefined"&&module.exports)module.exports=api;
})(typeof globalThis!=="undefined"?globalThis:this);
