"""Fixed-target HTTP/WebSocket relay behind a private GitHub Codespaces port."""
import asyncio,contextlib,os,time
CODE_HOST=os.environ.get('T588_CODE_HOST','gateway.invalid')
ORIGIN_HOST=os.environ.get('T588_ORIGIN_HOST','origin.invalid')
DEADLINE=1792599115.5804963
LIMIT=asyncio.Semaphore(64)
DROP={'authorization','cookie','x-github-token','x-forwarded-access-token','cf-access-jwt-assertion'}
async def error(writer,status):
 writer.write(('HTTP/1.1 '+status+'\r\nConnection: close\r\nContent-Length: 0\r\n\r\n').encode());await writer.drain()
async def forward(reader,writer):
 upstream=None
 try:
  async with LIMIT:
   raw=await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'),8)
   if time.time()>=DEADLINE:await error(writer,'410 Gone');return
   if len(raw)>16384:await error(writer,'431 Request Header Fields Too Large');return
   lines=raw.decode('latin1').split('\r\n');first=lines[0].split(' ')
   if len(first)!=3 or first[0]!='GET' or not first[1].startswith('/') or first[1].startswith('//') or first[2]!='HTTP/1.1':await error(writer,'400 Bad Request');return
   rows=[];hosts=[];origins=[];ws=False
   for line in lines[1:]:
    if not line:continue
    if ':'not in line:raise ValueError()
    name,value=line.split(':',1);key=name.lower();value=value.strip()
    if key=='host':hosts.append(value)
    if key=='origin':origins.append(value)
    if key in ('content-length','transfer-encoding'):raise ValueError()
    if key=='upgrade' and value.lower()=='websocket':ws=True
    if key not in DROP and key not in ('host','origin','connection'):rows.append((name,value))
   if len(hosts)!=1 or hosts[0]not in (CODE_HOST,'127.0.0.1:18620','localhost:18620'):await error(writer,'403 Forbidden');return
   # GitHub rewrites same-origin HTTPS requests to this exact local origin.
   # Foreign origins remain unchanged and must still be rejected.
   if origins and not (len(origins)==1 and origins[0] in ('https://'+CODE_HOST,'https://localhost:18620')):await error(writer,'403 Forbidden');return
   if ws and not origins:await error(writer,'403 Forbidden');return
   rows.append(('Host',ORIGIN_HOST));rows.append(('Connection','Upgrade' if ws else 'close'))
   if origins:rows.append(('Origin','https://'+ORIGIN_HOST))
   try:ur,upstream=await asyncio.wait_for(asyncio.open_connection('127.0.0.1',18622),5)
   except (OSError,asyncio.TimeoutError):await error(writer,'503 Service Unavailable');return
   upstream.write((lines[0]+'\r\n'+''.join(k+': '+v+'\r\n'for k,v in rows)+'\r\n').encode('latin1'));await upstream.drain()
   async def copy(source,target):
    while True:
     data=await asyncio.wait_for(source.read(65536),90)
     if not data:return
     target.write(data);await asyncio.wait_for(target.drain(),5)
   tasks=[asyncio.create_task(copy(reader,upstream)),asyncio.create_task(copy(ur,writer))]
   try:await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
   finally:
    for t in tasks:t.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
 except (ValueError,asyncio.IncompleteReadError,asyncio.LimitOverrunError,asyncio.TimeoutError,ConnectionError):pass
 finally:
  if upstream:upstream.close()
  writer.close()
  with contextlib.suppress(Exception):await writer.wait_closed()
async def main():
 if CODE_HOST=='gateway.invalid' or ORIGIN_HOST=='origin.invalid':raise RuntimeError('Missing fixed deployment hosts')
 server=await asyncio.start_server(forward,'127.0.0.1',18620,limit=16385)
 print('T588_CODE_RELAY_READY http://localhost:18620 deadline='+str(DEADLINE),flush=True)
 async with server:await asyncio.sleep(max(0,DEADLINE-time.time()))
if __name__=='__main__':asyncio.run(main())
