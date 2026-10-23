
// Requires the ID2381 V302 F6PK RAM-streaming firmware patch.

export function Name(){return "MonsGeek FUN60 Ultra (Live Per-Key)";}
export function VendorId(){return 0x3151;}
export function ProductId(){return 0x502d;}
export function Publisher(){return "Personal custom plugin";}
export function Type(){return "hid";}
export function DeviceType(){return "keyboard";}

// Automatically prevent SignalRGB from controlling the keyboard
// while MonsGeek Driver v4 is running.
// SignalRGB initializes the plugin again after the driver closes.
export function ConflictingProcesses(){
 return ["MonsGeek Driver v4.exe"];
}

export function Size(){return [120,40];}
export function DefaultPosition(){return [0,0];}
export function DefaultScale(){return 1;}

export function Validate(e){
 return e.interface===2&&e.usage_page===65535&&e.usage===2;
}

// Eighth-key grid preserves ANSI key centers without integer rounding.
const keys=[
 [1,"Esc",4,4],[7,"1",12,4],[13,"2",20,4],[19,"3",28,4],[25,"4",36,4],[31,"5",44,4],[37,"6",52,4],[43,"7",60,4],[49,"8",68,4],[55,"9",76,4],[61,"0",84,4],[67,"Minus",92,4],[73,"Equals",100,4],[79,"Backspace",112,4],
 [2,"Tab",6,12],[8,"Q",16,12],[14,"W",24,12],[20,"E",32,12],[26,"R",40,12],[32,"T",48,12],[38,"Y",56,12],[44,"U",64,12],[50,"I",72,12],[56,"O",80,12],[62,"P",88,12],[68,"Left bracket",96,12],[74,"Right bracket",104,12],[80,"Backslash",114,12],
 [3,"Caps Lock",7,20],[9,"A",18,20],[15,"S",26,20],[21,"D",34,20],[27,"F",42,20],[33,"G",50,20],[39,"H",58,20],[45,"J",66,20],[51,"K",74,20],[57,"L",82,20],[63,"Semicolon",90,20],[69,"Quote",98,20],[81,"Enter",111,20],
 [4,"Left Shift",9,28],[16,"Z",22,28],[22,"X",30,28],[28,"C",38,28],[34,"V",46,28],[40,"B",54,28],[46,"N",62,28],[52,"M",70,28],[58,"Comma",78,28],[64,"Period",86,28],[70,"Slash",94,28],[76,"Right Shift",109,28],
 [5,"Left Ctrl",5,36],[17,"Windows",15,36],[23,"Left Alt",25,36],[41,"Space",55,36],[65,"Right Alt",85,36],[71,"Fn",95,36],[77,"Menu",105,36],[83,"Right Ctrl",115,36]
];

// Display-only pixels fill each keycap;
// hardware still samples only its center.
const keyWidths=[
 ...Array(13).fill(8),16,12,
 ...Array(12).fill(8),12,14,
 ...Array(11).fill(8),18,18,
 ...Array(10).fill(8),22,10,10,10,50,10,10,10,10
];

const displayPixels=[];

keys.forEach((key,i)=>{
 const left=key[2]-keyWidths[i]/2+1;

 for(let y=key[3]-3;y<key[3]+3;y++){
  for(let x=left;x<left+keyWidths[i]-2;x++){
   displayPixels.push([key[1],x,y]);
  }
 }
});

export function LedNames(){
 return displayPixels.map(p=>p[0]);
}

export function LedPositions(){
 return displayPixels.map(p=>[p[1],p[2]]);
}

export function DeviceMessages(){
 return [{
  property:"Experimental firmware",
  message:"Live per-key streaming",
  tooltip:"Requires ID2381 V302 with the F6PK patch. Frames update RAM without saving custom colors to flash."
 }];
}

export function ControllableParameters(){
 return [];
}

let phase="stopped";
let due=0;
let modeDeadline=0;
let original=null;
let switched=false;
let nextFrame=0;

function packet(header,n=7,body=[]){
 const p=new Array(65).fill(0);

 header.forEach((v,i)=>{
  p[i+1]=v;
 });

 let sum=0;

 for(let i=1;i<=n;i++){
  sum+=p[i];
 }

 p[n+1]=(255-sum)&255;

 body.forEach((v,i)=>{
  p[i+9]=v;
 });

 return p;
}

function query(cmd,next){
 device.send_report(packet([cmd]),65);
 phase=next;
 due=Date.now()+70;
}

function read(cmd){
 const raw=device.get_report([0],65);

 if(!raw||raw.length<10){
  throw Error("No device reply");
 }

 const r=raw[0]===0
  ?raw.slice(1)
  :raw;

 if(r[0]!==cmd){
  throw Error(
   "Unexpected reply; close MonsGeek tools"
  );
 }

 return r;
}

function restore(){
 if(switched&&original){
  switched=false;
  device.send_report(
   packet([7,...original],8),
   65
  );
 }
}

function fail(e){
 phase="error";

 try{
  restore();
 }catch(_){}

 device.log(
  "FUN60 per-key stopped: "+String(e)
 );
}

export function Initialize(){


 phase="stopped";
 original=null;
 switched=false;
 nextFrame=0;

 try{
  query(0x8f,"identity");
 }catch(e){
  fail(e);
 }
}

export function Render(){

 if(
  phase==="error"||
  phase==="stopped"||
  Date.now()<due
 ){
  return;
 }

 try{

  if(phase==="identity"){

   const r=read(0x8f);

   if(
    (r[1]|r[2]<<8)!==2381||
    (r[7]|r[8]<<8)!==0x302||
    r.slice(3,7).join(",")!=="70,54,80,75"
   ){
    throw Error(
     "F6PK firmware marker missing; no streaming sent"
    );
   }

   query(0x87,"capture");

  }else if(phase==="capture"){

   original=read(0x87).slice(1,8);
   switched=true;

   device.send_report(
    packet([7,13,4,4,7,0,128,255],8),
    65
   );

   phase="mode-query";
   modeDeadline=Date.now()+600;
   due=Date.now()+150;

  }else if(phase==="mode-query"){

   query(0x87,"mode-read");

  }else if(phase==="mode-read"){

   if(read(0x87)[1]!==13){
    if(Date.now()<modeDeadline){phase="mode-query";due=Date.now()+70;return;}
    throw Error(
     "User-picture mode was not accepted"
    );
   }

   phase="live";

   device.log(
    "FUN60 F6PK ready: 61 keys follow the current canvas effect; frames update RAM only."
   );

  }else if(
   phase==="live"&&
   Date.now()>=nextFrame
  ){

   const frame=new Array(378).fill(0);

   for(const k of keys){

    const rgb=device.color(
     k[2],
     k[3]
    );

    if(
     !rgb||
     rgb.length<3||
     !rgb.slice(0,3).every(Number.isFinite)
    ){
     throw Error(
      "Invalid canvas color"
     );
    }

    for(let c=0;c<3;c++){
     frame[k[0]*3+c]=Math.max(
      0,
      Math.min(
       255,
       Math.round(rgb[c])
      )
     );
    }
   }

   for(let page=0;page<7;page++){

    const body=frame.slice(
     page*56,
     (page+1)*56
    );

    device.send_report(
     packet(
      [
       12,
       0,
       255,
       page,
       body.length,
       page===6?2:0
      ],
      7,
      body
     ),
     65
    );
   }

   nextFrame=Date.now()+33;
  }

 }catch(e){
  fail(e);
 }
}

export function Shutdown(){
 phase="stopped";
 try{restore();}catch(_){}
}
