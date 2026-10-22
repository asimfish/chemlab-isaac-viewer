import asyncio,unittest
import bridge
class MotionQueueTest(unittest.IsolatedAsyncioTestCase):
 def move(self,x,buttons=2,modifiers=0):return {'type':'mouse','action':'mouseMoved','x':x,'y':.3,'buttons':buttons,'modifiers':modifiers}
 async def test_latest_motion_before_release_is_preserved(self):
  q=bridge.MotionQueue(4);down={'type':'mouse','action':'mousePressed'};up={'type':'mouse','action':'mouseReleased'}
  q.put_nowait(down)
  for i in range(100):q.put_nowait(self.move(i))
  q.put_nowait(up);self.assertEqual(q.qsize(),3)
  self.assertIs(await q.get(),down);self.assertEqual((await q.get())['x'],99);self.assertIs(await q.get(),up)
 async def test_modifiers_and_keys_are_ordering_barriers(self):
  q=bridge.MotionQueue(8);items=[self.move(1),self.move(2,modifiers=1),{'type':'key','action':'keyUp'},self.move(3)]
  for item in items:q.put_nowait(item)
  self.assertEqual([await q.get()for _ in items],items)
 async def test_full_transition_queue_reports_overload(self):
  q=bridge.MotionQueue(2)
  for _ in range(2):q.put_nowait({'type':'key','action':'keyDown'})
  with self.assertRaises(asyncio.QueueFull):q.put_nowait({'type':'key','action':'keyUp'})
 async def test_waiting_consumer_is_woken(self):
  q=bridge.MotionQueue(2);task=asyncio.create_task(q.get());await asyncio.sleep(0);q.put_nowait(self.move(1));self.assertEqual((await asyncio.wait_for(task,.1))['x'],1)
if __name__=='__main__':unittest.main()
