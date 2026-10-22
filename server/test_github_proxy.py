import asyncio,time,unittest
from unittest.mock import patch
import github_proxy as relay
class ProxyTest(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.deadline=patch.object(relay,'DEADLINE',time.time()+60);self.deadline.start();self.addCleanup(self.deadline.stop)
  self.captured=[]
  async def origin(r,w):
   self.captured.append(await r.readuntil(b'\r\n\r\n'));w.write(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK');await w.drain();w.close()
  self.origin=await asyncio.start_server(origin,'127.0.0.1',18622)
  self.server=await asyncio.start_server(relay.forward,'127.0.0.1',0)
  self.port=self.server.sockets[0].getsockname()[1]
 async def asyncTearDown(self):
  self.server.close();self.origin.close();await self.server.wait_closed();await self.origin.wait_closed()
 async def request(self,header):
  r,w=await asyncio.open_connection('127.0.0.1',self.port);w.write(header);await w.drain();response=await asyncio.wait_for(r.read(),3);w.close();return response
 async def test_auth_headers_are_not_forwarded(self):
  raw=('GET /health HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\nX-Github-Token: private-test-fixture\r\nCookie: session=private-test-fixture\r\n\r\n').encode()
  self.assertIn(b'200 OK',await self.request(raw));self.assertNotIn(b'private-test-fixture',self.captured[0]);self.assertIn(relay.ORIGIN_HOST.encode(),self.captured[0])
 async def test_foreign_origin_rejected(self):
  raw=('GET /stream HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\nOrigin: https://attacker.invalid\r\nUpgrade: websocket\r\n\r\n').encode()
  self.assertIn(b'403',await self.request(raw));self.assertFalse(self.captured)
 async def test_unknown_host_rejected(self):
  self.assertIn(b'403',await self.request(b'GET / HTTP/1.1\r\nHost: attacker.invalid\r\n\r\n'))
 async def test_absolute_target_rejected(self):
  raw=('GET http://169.254.169.254/ HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\n\r\n').encode();self.assertIn(b'400',await self.request(raw))
 async def test_websocket_origin_is_normalized_only_after_validation(self):
  raw=('GET /stream?gpu=0 HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\nOrigin: https://'+relay.CODE_HOST+'\r\nUpgrade: websocket\r\n\r\n').encode()
  await self.request(raw);self.assertIn(('Origin: https://'+relay.ORIGIN_HOST).encode(),self.captured[0]);self.assertIn(b'Connection: Upgrade',self.captured[0])
 async def test_github_rewritten_same_origin_is_accepted(self):
  raw=b'GET /viewer.js HTTP/1.1\r\nHost: localhost:18620\r\nOrigin: https://localhost:18620\r\n\r\n'
  self.assertIn(b'200 OK',await self.request(raw));self.assertIn(('Origin: https://'+relay.ORIGIN_HOST).encode(),self.captured[0])
 async def test_websocket_without_origin_is_rejected(self):
  raw=('GET /stream HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\nUpgrade: websocket\r\n\r\n').encode()
  self.assertIn(b'403',await self.request(raw));self.assertFalse(self.captured)
 async def test_expired_session_does_not_contact_origin(self):
  with patch.object(relay,'DEADLINE',0):
   raw=('GET /health HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\n\r\n').encode()
   self.assertIn(b'410 Gone',await self.request(raw));self.assertFalse(self.captured)
 async def test_candidate_port_keeps_host_origin_binding(self):
  with patch.object(relay,'CODE_PORT',18626):
   raw=b'GET /config HTTP/1.1\r\nHost: localhost:18626\r\nOrigin: https://localhost:18626\r\n\r\n'
   self.assertIn(b'200 OK',await self.request(raw))
   self.assertIn(b'403',await self.request(b'GET /config HTTP/1.1\r\nHost: localhost:18620\r\n\r\n'))
 async def test_configured_upstream_is_fixed(self):
  async def origin(r,w):
   await r.readuntil(b'\r\n\r\n');w.write(b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\nConnection: close\r\n\r\nPORT');await w.drain();w.close()
  server=await asyncio.start_server(origin,'127.0.0.1',0)
  try:
   with patch.object(relay,'UPSTREAM_PORT',server.sockets[0].getsockname()[1]):
    raw=('GET /health HTTP/1.1\r\nHost: '+relay.CODE_HOST+'\r\n\r\n').encode();self.assertTrue((await self.request(raw)).endswith(b'PORT'))
  finally:server.close();await server.wait_closed()
if __name__=='__main__':unittest.main()
