const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync(require('path').join(__dirname,'../MonsGeek_FUN60_Ultra_Manual.js'),'utf8').replace(/export /g,'');
function setup({id=2381,version=0x302,marker=[70,54,80,75]}={}){
 let now=0,cmd=0,config=[1,4,4,7,0,128,255];const writes=[],logs=[];
 const c=vm.createContext({Date:{now:()=>now},device:{log:s=>logs.push(s),color:(x,y)=>[x,y,71],send_report:(p,n)=>{assert.equal(n,65);assert.equal(p.length,65);cmd=p[1];const count=cmd===7?8:7;assert.equal(p.slice(1,count+2).reduce((a,b)=>a+b,0)&255,255);writes.push([...p]);if(cmd===7)config=Array.from(p.slice(2,9));},get_report:()=>{const r=Array(65).fill(0);r[1]=cmd;if(cmd===0x8f){r[2]=id&255;r[3]=id>>8;r[8]=version&255;r[9]=version>>8;marker.forEach((v,i)=>r[4+i]=v);}if(cmd===0x87)config.forEach((v,i)=>r[i+2]=v);return r;}}});
 vm.runInContext(source,c);c.Initialize();const tick=(ms=100)=>{now+=ms;c.Render();};for(let i=0;i<12;i++)tick();return {c,tick,writes,logs,config:()=>config};
}
let f=setup();assert.equal(new Set(f.c.LedNames()).size,61);assert.equal(new Set(f.c.LedPositions().map(x=>x.join(','))).size,f.c.LedPositions().length);assert.ok(f.c.LedPositions().every(([x,y])=>Number.isInteger(x)&&Number.isInteger(y)&&x>=0&&x<120&&y>=0&&y<40));assert.ok(f.logs.some(s=>s.includes('61 keys')));
for(let i=0;i<100;i++)f.tick(34);
const stream=f.writes.filter(p=>p[1]===12);assert.ok(stream.length>=700);assert.equal(stream.length%7,0);
for(let i=0;i<stream.length;i++){const p=stream[i],page=i%7;assert.equal(p[3],255);assert.equal(p[4],page);assert.equal(p[5],page===6?42:56);assert.equal(p[6],page===6?2:0);}
const frame=stream.slice(-7).flatMap(p=>p.slice(9,9+p[5]));assert.equal(frame.length,378);assert.deepEqual(frame.slice(3,6),[4,4,71]);assert.deepEqual(frame.slice(79*3,79*3+3),[112,4,71]);assert.deepEqual(frame.slice(83*3,83*3+3),[115,36,71]);
assert.equal(f.writes.filter(p=>p[1]===7).length,1);f.c.Shutdown();assert.deepEqual(f.config(),[1,4,4,7,0,128,255]);
for(const bad of [{id:2307},{version:0x304},{marker:[0,0,0,0]}]){f=setup(bad);assert.equal(f.writes.filter(p=>[7,12].includes(p[1])).length,0);}
console.log('PASS: 61 canvas samples, 100+ frames, exact page format, capability/model/version guards, no per-frame persistent writes, shutdown restore');




