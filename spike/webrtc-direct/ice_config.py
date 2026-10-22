"""Coturn REST credentials: session-bound lifetime; shared key stays server-side."""
import base64,hashlib,hmac,json,os,secrets,time

def ice_config(deadline,env=None,now=None):
 env=os.environ if env is None else env;now=time.time()if now is None else now
 if not now<deadline<=now+18000:raise ValueError('ICE deadline outside authorized session')
 raw=env.get('T588_TURN_URLS');secret=env.get('T588_TURN_SHARED_SECRET')
 if bool(raw)!=bool(secret):raise ValueError('TURN URL and secret must be configured together')
 servers=[{'urls':'stun:stun.cloudflare.com:3478'}]
 if raw:
  urls=json.loads(raw)
  if not isinstance(urls,list)or not 1<=len(urls)<=4 or any(not isinstance(u,str)or len(u)>512 or not u.startswith(('turn:','turns:'))or any(c in u for c in '\r\n@')for u in urls):raise ValueError('Invalid TURN URLs')
  if len(secret)<32:raise ValueError('TURN shared secret too short')
  username=f'{int(deadline)}:{secrets.token_hex(8)}';credential=base64.b64encode(hmac.new(secret.encode(),username.encode(),hashlib.sha1).digest()).decode()
  servers.append({'urls':urls,'username':username,'credential':credential})
 force=env.get('T588_FORCE_RELAY')=='1'
 if force and not raw:raise ValueError('Relay-only mode needs TURN configuration')
 return {'iceServers':servers,'iceTransportPolicy':'relay'if force else'all'}
