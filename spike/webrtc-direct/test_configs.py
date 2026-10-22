import base64,hashlib,hmac,json,time,unittest
from ice_config import ice_config
from relay_launcher import relay_config
class ConfigTest(unittest.TestCase):
 def setUp(self):self.now=1000;self.secret='fixture-secret-'+'a'*32
 def test_rest_auth_matches_coturn(self):
  c=ice_config(1600,{'T588_TURN_URLS':'["turn:relay.example:3478"]','T588_TURN_SHARED_SECRET':self.secret,'T588_FORCE_RELAY':'1'},self.now);s=c['iceServers'][-1]
  self.assertTrue(s['username'].startswith('1600:'));self.assertEqual(s['credential'],base64.b64encode(hmac.new(self.secret.encode(),s['username'].encode(),hashlib.sha1).digest()).decode());self.assertEqual(c['iceTransportPolicy'],'relay')
 def test_partial_or_injected_configuration_fails_closed(self):
  for env in [{'T588_TURN_SHARED_SECRET':self.secret},{'T588_TURN_URLS':'["turn:host"]'},{'T588_FORCE_RELAY':'1'},{'T588_TURN_URLS':'["https://metadata/"]','T588_TURN_SHARED_SECRET':self.secret}]:
   with self.assertRaises(ValueError):ice_config(1600,env,self.now)
 def test_expiry_is_bound_to_session(self):
  for deadline in [999,1000,19001]:
   with self.assertRaises(ValueError):ice_config(deadline,{},self.now)
 def test_production_requires_real_public_ip(self):
  for ip in ['127.0.0.1','10.0.0.1','192.168.1.2']:
   with self.assertRaises(ValueError):relay_config(ip,'127.0.0.1',3478,49152,49215,self.secret)
 def test_lab_cannot_be_exposed(self):
  with self.assertRaises(ValueError):relay_config('8.8.8.8','0.0.0.0',13478,50000,50015,self.secret,lab=True)
 def test_fixed_auth_and_abuse_bounds(self):
  text=relay_config('8.8.8.8','10.1.2.3',3478,49152,49215,self.secret)
  for expected in ['use-auth-secret','no-cli','no-tcp-relay','user-quota=4','external-ip=8.8.8.8/10.1.2.3','denied-peer-ip=169.254.0.0-169.254.255.255']:self.assertIn(expected,text)
 def test_no_config_line_injection(self):
  with self.assertRaises(ValueError):relay_config('8.8.8.8','10.1.2.3',3478,49152,49215,self.secret+'\nno-auth')
if __name__=='__main__':unittest.main()
