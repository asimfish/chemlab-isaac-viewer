"""T588 bounded encoded-H264 WebRTC spike: authenticated signaling, DTLS media/control."""
import asyncio,contextlib,json,os,struct,time
from fractions import Fraction
from pathlib import Path
import av
from aiohttp import web,ClientSession,WSMsgType
from ice_config import ice_config
from aiortc import RTCPeerConnection,RTCConfiguration,RTCIceServer,RTCSessionDescription,MediaStreamTrack,RTCRtpSender
DEADLINE=float(os.environ['T588_SESSION_DEADLINE']);GPU_DEADLINE=float(os.environ.get('T588_GPU_DEADLINE',str(DEADLINE)));HOST=os.environ.get('T588_RTC_HOST','127.0.0.1:18626');PEERS=set();HTTP=None;FIXTURE=os.environ.get('T588_RTC_FIXTURE')=='1';UPSTREAM='http://127.0.0.1:'+('18720'if FIXTURE else '18620')
class H264Track(MediaStreamTrack):
 kind='video'
 def __init__(self):super().__init__();self.queue=asyncio.Queue(12);self.epoch=None
 async def recv(self):
  data=await self.queue.get();rtp=struct.unpack_from('!I',data,12)[0]
  if self.epoch is None:self.epoch=rtp
  packet=av.Packet(data[24:]);packet.pts=(rtp-self.epoch)&0xffffffff;packet.time_base=Fraction(1,90000);return packet
@web.middleware
async def boundary(req,handler):
 if time.time()>=DEADLINE:raise web.HTTPGone()
 if req.host not in (HOST,'127.0.0.1:18626'):raise web.HTTPForbidden()
 if req.headers.get('Origin')not in(None,'https://'+HOST,'http://127.0.0.1:18626'):raise web.HTTPForbidden()
 # Public access is only through the private authenticated Codespace proxy.
 response=await handler(req);response.headers.update({'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'"});return response
async def signal(req):
 if len(PEERS)>=4:raise web.HTTPServiceUnavailable()
 gpu=req.query.get('gpu');test=gpu is None
 if gpu is not None and not FIXTURE and time.time()>=GPU_DEADLINE:raise web.HTTPGone(text='GPU session expired; CPU network test only')
 if gpu is not None and gpu not in ('0','1','2','3'):raise web.HTTPBadRequest()
 ws=web.WebSocketResponse(max_msg_size=65536,compress=False,heartbeat=10);await ws.prepare(req)
 pc=RTCPeerConnection(RTCConfiguration([RTCIceServer(**s)for s in ice_config(DEADLINE)['iceServers']]));PEERS.add(pc);track=H264Track();dc=None;native=None;tasks=[];last=time.monotonic();kept=False;closing=False;tx=asyncio.Queue(128);mode='native'
 async def close():
  nonlocal closing
  if closing:return
  closing=True;track.stop()
  for t in tasks:
   if t is not asyncio.current_task():t.cancel()
  if native and not native.closed:await native.close()
  await pc.close();PEERS.discard(pc)
  await asyncio.gather(*(t for t in tasks if t is not asyncio.current_task()),return_exceptions=True)
 async def source():
  nonlocal native
  try:
   native=await HTTP.ws_connect(UPSTREAM+'/stream?gpu='+gpu,origin='http://127.0.0.1:18620',max_msg_size=2**21,heartbeat=10)
   await native.send_json({'type':'controls','mode':mode})
   async def transmit():
    while True:await native.send_json(await tx.get())
   tasks.append(asyncio.create_task(transmit()))
   async def heartbeat():
    while True:
     await asyncio.sleep(10);await tx.put({'type':'ping','id':'upstream-heartbeat','client':0})
   tasks.append(asyncio.create_task(heartbeat()))
   async for msg in native:
    if msg.type==WSMsgType.BINARY:
     if len(msg.data)<24 or msg.data[:4]!=b'T588':continue
     if track.queue.full():break
     track.queue.put_nowait(msg.data)
    elif msg.type==WSMsgType.TEXT and dc and dc.readyState=='open':
     if json.loads(msg.data).get('id')!='upstream-heartbeat':dc.send(msg.data)
  except Exception as e:print('RTC_SOURCE_CLOSED',type(e).__name__,flush=True)
  finally:await close()
 @pc.on('datachannel')
 def channel(c):
  nonlocal dc;dc=c
  @c.on('message')
  def message(raw):
   nonlocal last,mode
   if not isinstance(raw,str)or len(raw)>16384:return
   try:m=json.loads(raw)
   except ValueError:return
   if not isinstance(m,dict):return
   last=time.monotonic()
   if m.get('type')=='ping':c.send(json.dumps({'type':'pong','client':m.get('client'),'server':time.time()*1000}));return
   if m.get('type')=='controls':
    if m.get('mode')not in('native','vertical','horizontal','both'):return
    mode=m['mode']
   if not test and m.get('type')in('mouse','key','controls','stats')and native and not native.closed:
    if not tx.full():tx.put_nowait(m)
    else:tasks.append(asyncio.create_task(close()))
 @pc.on('connectionstatechange')
 async def changed():
  if pc.connectionState=='connected'and not test and not any(t.get_name()=='native'for t in tasks):tasks.append(asyncio.create_task(source(),name='native'))
  if pc.connectionState in('failed','closed'):await close()
 async def expiry():
  while time.time()<DEADLINE and time.monotonic()-last<180:await asyncio.sleep(5)
  await close()
 try:
  m=await asyncio.wait_for(ws.receive_json(),15)
  if not isinstance(m,dict)or m.get('type')!='offer'or not isinstance(m.get('sdp'),str)or len(m['sdp'])>60000:raise ValueError()
  if not test:
   pc.addTrack(track)
   for transceiver in pc.getTransceivers():transceiver.setCodecPreferences([c for c in RTCRtpSender.getCapabilities('video').codecs if c.mimeType.lower()=='video/h264'])
  await pc.setRemoteDescription(RTCSessionDescription(sdp=m['sdp'],type='offer'));await pc.setLocalDescription(await pc.createAnswer());await ws.send_json({'type':'answer','sdp':pc.localDescription.sdp})
  tasks.append(asyncio.create_task(expiry()))
  # Signaling may close after ICE succeeds; media/control stay on DTLS until deadline.
  for _ in range(350):
   if pc.connectionState=='connected':kept=True;break
   if pc.connectionState in('failed','closed'):break
   await asyncio.sleep(.1)
 except (ValueError,TypeError,asyncio.TimeoutError):pass
 finally:
  await ws.close()
  if not kept:
   ice=pc.sctp.transport.transport if pc.sctp else None
   print('ICE_PROBE',pc.connectionState,{'local':[(c.type,c.ip,c.port)for c in ice.iceGatherer.getLocalCandidates()]if ice else [],'remote':[(c.type,c.ip,c.port)for c in ice.getRemoteCandidates()]if ice else []},flush=True)
   await close()
 return ws
async def static(req):
 name=req.match_info.get('name')or'index.html'
 if name not in('index.html','client.js','style.css'):raise web.HTTPNotFound()
 if FIXTURE and name=='index.html':return web.Response(text=(Path(__file__).parent/name).read_text().replace('Isaac Sim · 直连测试','CPU TEST · 无 GPU · WebRTC 60fps 验证').replace('ChemLab · WebRTC 直连测试','CPU TEST'),content_type='text/html')
 return web.FileResponse(Path(__file__).parent/name)
async def config(req):return web.json_response(ice_config(DEADLINE))
async def health(req):return web.json_response({'status':'rtc-spike','deadline':DEADLINE,'peers':len(PEERS),'fixture':FIXTURE})
async def lifetime(app):
 global HTTP;HTTP=ClientSession()
 async def die():await asyncio.sleep(max(0,DEADLINE-time.time()));os.kill(os.getpid(),15)
 t=asyncio.create_task(die());yield;t.cancel()
 for pc in list(PEERS):await pc.close()
 await HTTP.close()
app=web.Application(middlewares=[boundary],client_max_size=65536);app.cleanup_ctx.append(lifetime);app.router.add_get('/signal',signal);app.router.add_get('/health',health);app.router.add_get('/config',config);app.router.add_get('/',static);app.router.add_get('/{name}',static)
if __name__=='__main__':web.run_app(app,host='127.0.0.1',port=18626,access_log=None,print=None)
