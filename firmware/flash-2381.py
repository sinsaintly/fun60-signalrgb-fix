"""ID2381-specific HID flasher. Dry run by default. Based on ry5088-flasher protocol."""
from pathlib import Path
import argparse,sys,time,json,hashlib,struct
p=Path(__file__).parent
if not __debug__: raise SystemExit('Run without Python -O: validation checks are required.')
try:
 import hid
except ImportError:
 raise SystemExit('Install dependency: py -3 -m pip install hidapi')
ap=argparse.ArgumentParser();ap.add_argument('--arm',action='store_true');ap.add_argument('--stock',action='store_true');ap.add_argument('--recover-model-2381',action='store_true',help='Bootloader recovery only: explicitly confirm this unit was previously verified as model 2381');args=ap.parse_args()
stock=p/'stock-ID2381-V302.bin';candidate=p/'ID2381-V302-F6PK.bin'
manifest=json.loads((p/'manifest.json').read_text())
image=stock if args.stock else candidate
data=image.read_bytes();expected=manifest['base_sha256'] if args.stock else manifest['patched_sha256']
assert hashlib.sha256(data).hexdigest()==expected
assert data[0x5000:0x5000+len(b'AT32F405 8KMKB')]==b'AT32F405 8KMKB'
assert 0x5208<len(data)<0x28000
sp,rv=struct.unpack_from('<II',data,0x5200)
assert 0x20000000<=sp<=0x20020000 and rv&1 and 0x08005200<=rv&~1<0x08028000
payload=data[0x5000:];padded=payload+b'\xff'*((-len(payload))%64)
count=len(padded)//64;checksum=sum(padded)&0xffffff
log=[]
def record(event,**kw):
 entry={'event':event,**kw};log.append(entry);print(json.dumps(entry),flush=True)
 (p/('flash-stock-log.json' if args.stock else 'flash-patch-log.json')).write_text(json.dumps(log,indent=2))
def find(pid,up,usage=None):
 ds=[x for x in hid.enumerate(0x3151,pid) if x['usage_page']==up and (usage is None or x['usage']==usage)]
 assert len(ds)<=1,'Ambiguous device selection'
 return ds[0] if ds else None
def open_device(info):
 d=hid.device();d.open_path(info['path']);return d
def send(d,frame):
 assert len(frame)==64
 n=d.send_feature_report(bytes([0])+bytes(frame));assert n==65,('short write',n)
def header(parts):
 a=bytearray(64);a[:len(parts)]=parts;a[7]=(255-sum(a[:7]))&255;return a
def recv(d):
 a=bytes(d.get_feature_report(0,65));return a[1:] if a and a[0]==0 else a
def identity(info):
 d=open_device(info)
 try:send(d,header([0x8f]));time.sleep(.08);r=recv(d)
 finally:d.close()
 assert r[:3]==bytes([0x8f,0x4d,9]),'Wrong model identity'
 return r
def wait(pid,up,usage=None,seconds=20):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  info=find(pid,up,usage)
  if info:return info
  time.sleep(.25)
 return None

import subprocess,os
if os.name=='nt':
 processes=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,check=True).stdout.lower()
 if any(name in processes for name in ['signalrgb.exe','monsgeek driver v4.exe','iot_manager_rs.exe']):
  raise SystemExit('Fully exit SignalRGB, MonsGeek and iot_manager_rs before running this tool.')
normal=find(0x502d,0xffff,2);boot=find(0x502a,0xff01)
assert normal or boot,'Keyboard not found in normal or bootloader mode'
if not normal and not args.recover_model_2381:
 raise SystemExit('Bootloader-only device: model cannot be identified. Recovery requires --recover-model-2381 and prior verified model identity.')
if normal:
 r=identity(normal);record('identity',model=2381,version=r[7:9].hex(),marker=r[3:7].hex())
 assert r[7:9] in (b'\x04\x03',b'\x02\x03'),'Unexpected firmware'
record('plan',image=str(image),sha256=expected,slice_bytes=len(payload),chunks=count,checksum=hex(checksum),armed=args.arm)
if not args.arm:sys.exit(0)
if normal:
 d=open_device(normal)
 try:
  send(d,header([0xc5,0x3a]));time.sleep(.1)
  try:send(d,header([0x7f,0x55,0xaa,0x55,0xaa]))
  except OSError as e:record('reset_transfer',message=str(e))
 finally:d.close()
 boot=wait(0x502a,0xff01)
 assert boot,'Bootloader did not enumerate; no firmware stream sent'
record('bootloader_ready')
d=open_device(boot)
try:
 start=bytearray(64);start[:2]=b'\xba\xc0';start[2:4]=count.to_bytes(2,'little');start[4:7]=len(payload).to_bytes(3,'little')
 send(d,start);time.sleep(.03)
 for i in range(count):
  send(d,padded[i*64:i*64+64]);time.sleep(.002)
  if i%250==0:record('transfer',sent=i+1,total=count)
 time.sleep(.03)
 complete=bytearray(64);complete[:2]=b'\xba\xc2';complete[2:4]=count.to_bytes(2,'little');complete[4:7]=checksum.to_bytes(3,'little')
 try:send(d,complete)
 except OSError as e:record('completion_transfer',message=str(e))
 time.sleep(.06)
 try:
  ack=recv(d);record('ack',raw=ack.hex())
  assert not (len(ack)>4 and ack[0]==0xab and ack[4]==0xaa),'Bootloader rejected image'
 except OSError:record('ack_unavailable_after_reset')
finally:d.close()
normal=wait(0x502d,0xffff,2)
assert normal,'Keyboard did not return to normal mode; recovery required'
r=identity(normal)
assert r[7:9]==b'\x02\x03','Post-flash version mismatch'
assert r[3:7]==(bytes(4) if args.stock else b'F6PK'),'Post-flash capability marker mismatch'
record('verified',model=2381,version='0302',marker=r[3:7].hex())
