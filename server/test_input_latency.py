import asyncio,time,unittest
from unittest.mock import patch
from aiohttp.test_utils import TestClient,TestServer
import bridge
class NativeFixture:
 last=None
 def __init__(self,gpu):
  NativeFixture.last=self;self.viewer=None;self.queue=asyncio.Queue(maxsize=12);self.input=asyncio.Queue(maxsize=128);self.started=asyncio.Event();self.release=asyncio.Event();self.received=asyncio.Event();self.tasks=[];self.calls=0;self.active=0
 async def start(self):
  async def consume():await self.input.get();self.received.set()
  self.tasks=[asyncio.create_task(consume())]
 async def stats(self):
  self.calls+=1;self.active+=1;self.started.set()
  try:await self.release.wait();return {'fixture':True}
  finally:self.active-=1
 async def close(self):
  for t in self.tasks:t.cancel()
  await asyncio.gather(*self.tasks,return_exceptions=True)
  if self.viewer and not self.viewer.closed:await self.viewer.close()
class InputLatencyTest(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.patches=[patch.object(bridge,'Worker',NativeFixture),patch.object(bridge,'DEADLINE',time.time()+60),patch.object(bridge,'TEST_SECRET','fixture-only'),patch.object(bridge,'WORKERS',{})]
  for p in self.patches:p.start();self.addCleanup(p.stop)
  self.client=TestClient(TestServer(bridge.make_app()));await self.client.start_server();self.ws=await self.client.ws_connect('/stream?gpu=0',headers={'Authorization':'Bearer fixture-only'});await self.ws.receive_json();self.worker=NativeFixture.last
 async def asyncTearDown(self):
  await self.ws.close()
  for _ in range(100):
   if not bridge.WORKERS:break
   await asyncio.sleep(.01)
  await self.client.close()
 async def test_input_delivered_while_stats_remains_blocked(self):
  await self.ws.send_json({'type':'stats'});await self.worker.started.wait();await self.ws.send_json({'type':'mouse','action':'mousePressed','x':.1,'y':.1,'button':'left','buttons':1})
  await asyncio.wait_for(self.worker.received.wait(),.25);self.assertFalse(self.worker.release.is_set())
 async def test_repeated_snapshots_coalesce_and_cancel_on_disconnect(self):
  await self.ws.send_json({'type':'stats'});await self.worker.started.wait()
  for _ in range(20):await self.ws.send_json({'type':'stats'})
  await self.ws.send_json({'type':'ping','id':1,'client':1});reply=await self.ws.receive_json();self.assertEqual(reply['type'],'pong');self.assertEqual(self.worker.calls,1)
  await self.ws.close()
  for _ in range(50):
   if not self.worker.active:break
   await asyncio.sleep(.01)
  self.assertEqual(self.worker.active,0)
if __name__=='__main__':unittest.main()
