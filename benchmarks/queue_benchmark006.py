import asyncio,importlib.util,json,pathlib,statistics,sys,time
root=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('subject',sys.argv[1]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
async def trial():
 w=module.Worker(2);done=asyncio.Event();calls=[]
 async def call(method,p):
  calls.append(p['type']);await asyncio.sleep(.0167)
  if p['type']=='mouseReleased':done.set()
  return {}
 w.call=call;task=asyncio.create_task(w.inputs())
 def event(action,x):return {'type':'mouse','action':action,'x':x,'y':.3,'button':'right'if action!='mouseMoved'else 'none','buttons':0 if action=='mouseReleased'else 2}
 try:
  w.input.put_nowait(event('mousePressed',.3));await asyncio.sleep(.025)
  for i in range(30):w.input.put_nowait(event('mouseMoved',.3+i/1000));await asyncio.sleep(.004)
  start=time.perf_counter();w.input.put_nowait(event('mouseReleased',.329));await asyncio.wait_for(done.wait(),2)
  return {'release_wait_ms':(time.perf_counter()-start)*1000,'native_dispatches':len(calls),'release_delivered':calls[-1]=='mouseReleased'}
 finally:task.cancel();await asyncio.gather(task,return_exceptions=True)
async def main():
 rows=[]
 for i in range(13):rows.append({'trial':i,'warmup':i<3,**await trial()})
 a=sorted(r['release_wait_ms']for r in rows if not r['warmup']);out={'workload':'30 consecutive mouse moves delivered every4ms, CDP service16.7ms, followed by release; WAN-burst replay, not native end-to-end','rows':rows,'p50':statistics.median(a),'p95':a[int(len(a)*.95)]};pathlib.Path(sys.argv[2]).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if k!='rows'}))
asyncio.run(main())
