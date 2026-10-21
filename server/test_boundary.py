import asyncio,unittest
from aiohttp.test_utils import TestClient, TestServer
from aiohttp import web
import bridge

class BoundaryTest(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  bridge.TEST_SECRET='test-only-local-fixture';bridge.ALLOWED_HOST='gateway.example'
  self.client=TestClient(TestServer(bridge.make_app()));await self.client.start_server()
 async def asyncTearDown(self):await self.client.close()
 async def test_denied_without_identity(self):
  r=await self.client.get('/health');self.assertEqual(r.status,401)
 async def test_valid_auth_is_http_only_cookie(self):
  r=await self.client.get('/health',headers={'Authorization':'Bearer test-only-local-fixture'});self.assertEqual(r.status,200);self.assertTrue(r.cookies['t588_test']['httponly']);self.assertEqual((await r.json())['gpu_count'],4)
 async def test_wrong_token_denied(self):
  r=await self.client.get('/health',headers={'Authorization':'Bearer wrong'});self.assertEqual(r.status,401)
 async def test_cross_origin_denied_even_with_auth(self):
  r=await self.client.get('/health',headers={'Authorization':'Bearer test-only-local-fixture','Origin':'https://attacker.example'});self.assertEqual(r.status,403)
 async def test_gpu_range_no_arbitrary_targets(self):
  for gpu in ('-1','4','http://169.254.169.254','nan'):
   r=await self.client.get('/stream',params={'gpu':gpu},headers={'Authorization':'Bearer test-only-local-fixture'});self.assertEqual(r.status,400)
 async def test_no_filesystem_export(self):
  for name in ('bridge.py','producer.js','evidence','native_control.mjs'):
   r=await self.client.get('/'+name,headers={'Authorization':'Bearer test-only-local-fixture'});self.assertEqual(r.status,404)
 async def test_public_producer_denied(self):
  r=await self.client.get('/producer',headers={'Origin':'https://gateway.example'});self.assertEqual(r.status,403)
 async def test_session_deadline_fails_closed(self):
  old=bridge.DEADLINE
  try:
   bridge.DEADLINE=1;r=await self.client.get('/health',headers={'Authorization':'Bearer test-only-local-fixture'});self.assertEqual(r.status,410)
  finally:bridge.DEADLINE=old
if __name__=='__main__':unittest.main()
