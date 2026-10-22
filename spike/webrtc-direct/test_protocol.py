import asyncio,os,struct,time,unittest
from unittest.mock import patch
from aiohttp import web,ClientSession,WSMsgType
from aiohttp.test_utils import TestClient,TestServer
os.environ.setdefault('T588_SESSION_DEADLINE',str(time.time()+600))
import server
class PacketTest(unittest.IsolatedAsyncioTestCase):
 async def test_encoded_payload_is_forwarded_without_reencode_and_wraps(self):
  t=server.H264Track();raw=b'\x00\x00\x00\x01\x65payload'
  for n,stamp in enumerate([0xfffffff0,0x20]):
   t.queue.put_nowait(struct.pack('!4sB3xIId',b'T588',int(n==0),n,stamp,time.time()*1000)+raw);p=await t.recv();self.assertEqual(bytes(p),raw);self.assertEqual(p.pts,0 if n==0 else 48);self.assertEqual(str(p.time_base),'1/90000')
  t.stop()
class BoundaryTest(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.patches=[patch.object(server,'DEADLINE',time.time()+60),patch.object(server,'HOST','rtc.example'),patch.object(server,'PEERS',set()),patch.object(server,'FIXTURE',False),patch.object(server,'GPU_DEADLINE',time.time()-1)]
  for p in self.patches:p.start();self.addCleanup(p.stop)
  a=web.Application(middlewares=[server.boundary]);a.router.add_get('/health',server.health);a.router.add_get('/signal',server.signal);self.client=TestClient(TestServer(a));await self.client.start_server()
 async def asyncTearDown(self):await self.client.close()
 async def test_foreign_host_and_origin_denied(self):
  for headers in [{'Host':'attacker.example'},{'Host':'rtc.example','Origin':'https://attacker.example'}]:
   r=await self.client.get('/health',headers=headers);self.assertEqual(r.status,403)
 async def test_expired_gpu_cannot_be_reused_in_cpu_test(self):
  r=await self.client.get('/signal?gpu=2',headers={'Host':'rtc.example'});self.assertEqual(r.status,410);self.assertFalse(server.PEERS)
 async def test_invalid_gpu_does_not_create_peer(self):
  r=await self.client.get('/signal?gpu=99',headers={'Host':'rtc.example'});self.assertIn(r.status,[400,410]);self.assertFalse(server.PEERS)
 async def test_invalid_offer_closes_and_releases_peer(self):
  w=await self.client.ws_connect('/signal',headers={'Host':'rtc.example','Origin':'https://rtc.example'});await w.send_json({'type':'answer','sdp':'invalid'});reply=await asyncio.wait_for(w.receive(),2);self.assertIn(reply.type,[WSMsgType.CLOSE,WSMsgType.CLOSED]);await w.close()
  for _ in range(20):
   if not server.PEERS:break
   await asyncio.sleep(.01)
  self.assertFalse(server.PEERS)
if __name__=='__main__':unittest.main()
