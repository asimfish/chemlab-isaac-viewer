"""Exercise real stream handler with slow native statistics and timestamp input delivery."""
import asyncio,importlib.util,json,pathlib,statistics,time
from unittest.mock import patch
from aiohttp.test_utils import TestClient,TestServer
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_bridge',ROOT/'server/bridge.py');bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
class Worker:
 last=None
 def __init__(self,gpu):
  Worker.last=self;self.gpu=gpu;self.viewer=None;self.queue=asyncio.Queue(maxsize=12);self.input=asyncio.Queue(maxsize=128);self.stats_entered=asyncio.Event();self.received=asyncio.Queue();self.tasks=[]
 async def start(self):
  async def consume():
   while True:await self.input.get();await self.received.put(time.perf_counter())
  self.tasks.append(asyncio.create_task(consume()))
 async def stats(self):
  self.stats_entered.set();await asyncio.sleep(.3);return {'synthetic_slow_stats_ms':300}
 async def close(self):
  for t in self.tasks:t.cancel()
  await asyncio.gather(*self.tasks,return_exceptions=True)
  if self.viewer and not self.viewer.closed:await self.viewer.close()
async def main():
 samples=[]
 with patch.object(bridge,'Worker',Worker),patch.object(bridge,'DEADLINE',time.time()+120),patch.object(bridge,'TEST_SECRET','fixture-only'):
  async with TestClient(TestServer(bridge.make_app()))as client:
   for i in range(13):
    async with client.ws_connect('/stream?gpu=0',headers={'Authorization':'Bearer fixture-only'})as ws:
     await ws.receive_json();w=Worker.last;await ws.send_json({'type':'stats'});await asyncio.wait_for(w.stats_entered.wait(),2)
     start=time.perf_counter();await ws.send_json({'type':'mouse','action':'mousePressed','x':.1,'y':.1,'button':'left','buttons':1});arrived=await asyncio.wait_for(w.received.get(),2);samples.append((arrived-start)*1000)
    await asyncio.sleep(.005)
 vals=sorted(samples[3:]);out={'warmups':3,'samples_ms':samples[3:],'p50_ms':statistics.median(vals),'p95_ms':vals[int(len(vals)*.95)],'stdev_ms':statistics.stdev(vals),'fixture':'real stream handler; native CDP stats takes300ms; no network/GPU'}
 target=pathlib.Path(__import__('sys').argv[1]);target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
asyncio.run(main())
