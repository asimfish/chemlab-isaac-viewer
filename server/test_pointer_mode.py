import asyncio,json,unittest
from unittest.mock import AsyncMock
import bridge
class PointerModeTest(unittest.IsolatedAsyncioTestCase):
 async def test_only_valid_modes_reach_native_page(self):
  w=bridge.Worker(2);w.call=AsyncMock(return_value={})
  task=asyncio.create_task(w.inputs())
  try:
   for mode in ['native','vertical','horizontal','both',"';fetch('https://invalid')//",None]:
    w.input.put_nowait({'type':'controls','mode':mode})
   await asyncio.sleep(.01)
   self.assertEqual(w.call.await_count,4)
   for c,mode in zip(w.call.await_args_list,['native','vertical','horizontal','both']):
    self.assertEqual(c.args[0],'Runtime.evaluate');self.assertEqual(c.args[1]['expression'],'window.__t588PointerMode='+json.dumps(mode))
  finally:task.cancel();await asyncio.gather(task,return_exceptions=True)
if __name__=='__main__':unittest.main()
