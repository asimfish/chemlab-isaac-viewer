import asyncio,unittest
from unittest.mock import patch
import github_proxy as relay
class ProxyTest(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
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
if __name__=='__main__':unittest.main()
