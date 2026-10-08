/* Reusable Leaflet point-map adapter. The topic owns event details, not map lifecycle. */
(function(root){
"use strict";
function coordinates(record,latKey="lat",lonKey="lon"){
 const lat=Number(record&&record[latKey]),lon=Number(record&&record[lonKey]);
 return record&&record[latKey]!=null&&record[lonKey]!=null&&Number.isFinite(lat)&&Number.isFinite(lon)&&lat>=-90&&lat<=90&&lon>=-180&&lon<=180?[lat,lon]:null;
}
function createMap(options){
 const {elementId,center=[48.7,31.3],zoom=6,minZoom=5,maxZoom=15,clusterRadius=42,onSelect=()=>{},pointClass="attack-dot"}=options||{};
 const L=root.L;
 if(!L)throw new Error("Leaflet is required");
 if(!elementId)throw new TypeError("Missing map element");
 const map=L.map(elementId,{zoomControl:true,minZoom,maxZoom,worldCopyJump:false}).setView(center,zoom);
 L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:"© OpenStreetMap contributors"}).addTo(map);
 const cluster=L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:clusterRadius,spiderfyOnMaxZoom:true});
 map.addLayer(cluster);
 const overlays=L.layerGroup().addTo(map),markers=new Map();
 function render(items,adapter={}){
  const {idOf=x=>x.id,coordsOf=x=>coordinates(x),onClick=onSelect}=adapter;
  cluster.clearLayers();markers.clear();
  for(const item of items){
   const coords=coordsOf(item),id=idOf(item);
   if(!coords||id==null)continue;
   const icon=L.divIcon({className:"",html:'<div class="'+pointClass+'" style="width:10px;height:10px"></div>',iconSize:[10,10],iconAnchor:[5,5]});
   const marker=L.marker(coords,{icon});marker.on("click",()=>onClick(item,marker));
   cluster.addLayer(marker);markers.set(id,marker);
  }
  setTimeout(()=>map.invalidateSize(),50);
  return markers.size;
 }
 function focus(id,zoomLevel=10){
  const marker=markers.get(id);if(!marker)return false;
  map.setView(marker.getLatLng(),zoomLevel,{animate:true});
  setTimeout(()=>marker.fire("click"),250);return true;
 }
 return Object.freeze({map,cluster,overlays,markers,render,focus,resize(){map.invalidateSize()},destroy(){map.remove();markers.clear()}});
}
const api=Object.freeze({coordinates,createMap});
root.UbikMap=api;
if(typeof module!=="undefined"&&module.exports)module.exports=api;
})(typeof globalThis!=="undefined"?globalThis:this);
