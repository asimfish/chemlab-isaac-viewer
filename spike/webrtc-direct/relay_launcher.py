"""Launch coturn with a memory-only REST secret and fixed, bounded configuration."""
import argparse,ipaddress,os,signal,subprocess,time,ctypes

def relay_config(public_ip,relay_ip,port,minimum,maximum,secret,lab=False,cert=None,key=None,tls_port=5349):
 pub=ipaddress.IPv4Address(public_ip);local=ipaddress.IPv4Address(relay_ip)
 if lab:
  if not pub.is_loopback or not local.is_loopback:raise ValueError('Lab listener must remain loopback')
 elif not pub.is_global:raise ValueError('A global public IPv4 is required')
 if not 1024<=port<=65535 or not 1024<=minimum<=maximum<=65535 or maximum-minimum>255:raise ValueError('Invalid bounded port range')
 if len(secret)<32 or '\n'in secret or '\r'in secret:raise ValueError('Invalid REST secret')
 lines=[f'listening-ip={local}',f'relay-ip={local}',f'listening-port={port}',f'min-port={minimum}',f'max-port={maximum}','relay-threads=2','realm=chemlab-t588','fingerprint','use-auth-secret',f'static-auth-secret={secret}','total-quota=32','user-quota=4','max-bps=4000000','bps-capacity=12000000','no-cli','no-multicast-peers','no-tcp-relay','no-dtls','no-stdout-log','log-file=/dev/null','pidfile=/dev/null']
 if public_ip!=relay_ip:lines.append(f'external-ip={pub}/{local}')
 if lab:lines+=['allow-loopback-peers']
 else:
  for lower,upper in [('0.0.0.0','0.255.255.255'),('10.0.0.0','10.255.255.255'),('100.64.0.0','100.127.255.255'),('127.0.0.0','127.255.255.255'),('169.254.0.0','169.254.255.255'),('172.16.0.0','172.31.255.255'),('192.168.0.0','192.168.255.255'),('224.0.0.0','255.255.255.255')]:lines.append(f'denied-peer-ip={lower}-{upper}')
 if bool(cert)!=bool(key):raise ValueError('Both TLS certificate and private-key paths are required')
 if cert:
  for path in [cert,key]:
   if not os.path.isabs(path)or '\n'in path or '\r'in path or not os.path.isfile(path):raise ValueError('Invalid exact TLS file')
  if not 1024<=tls_port<=65535:raise ValueError('Invalid TLS port')
  lines.extend([f'tls-listening-port={tls_port}',f'cert={cert}',f'pkey={key}'])
 else:lines.append('no-tls')
 return '\n'.join(lines)+'\n'

def memory_config_fd(config):
 if hasattr(os,'memfd_create'):fd=os.memfd_create('t588-turn-config',0)
 else:
  libc=ctypes.CDLL(None,use_errno=True);create=libc.memfd_create;create.argtypes=[ctypes.c_char_p,ctypes.c_uint];create.restype=ctypes.c_int;fd=create(b't588-turn-config',0)
  if fd<0:raise OSError(ctypes.get_errno(),'memfd_create failed')
 os.fchmod(fd,0o600);os.write(fd,config.encode());os.lseek(fd,0,os.SEEK_SET);return fd

def launch(binary,config,deadline,env=None):
 if not time.time()<deadline<=time.time()+18000:raise ValueError('Finite relay deadline required')
 fd=memory_config_fd(config)
 child_env=dict(os.environ if env is None else env)
 for name in ['T588_TURN_SHARED_SECRET','ZENITH_API_TOKEN','GITHUB_TOKEN','GH_TOKEN']:child_env.pop(name,None)
 p=subprocess.Popen([binary,'-c',f'/proc/self/fd/{fd}'],pass_fds=(fd,),env=child_env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 os.close(fd)
 try:p.wait(timeout=max(1,deadline-time.time()))
 except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=8)
 return p.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--public-ip',required=True);p.add_argument('--relay-ip',required=True);p.add_argument('--port',type=int,default=3478);p.add_argument('--min-port',type=int,default=49152);p.add_argument('--max-port',type=int,default=49215);p.add_argument('--cert');p.add_argument('--key');p.add_argument('--tls-port',type=int,default=5349);p.add_argument('--seconds',type=int,default=1800);a=p.parse_args()
 if not 1<=a.seconds<=18000:raise SystemExit('Invalid finite duration')
 c=relay_config(a.public_ip,a.relay_ip,a.port,a.min_port,a.max_port,os.environ['T588_TURN_SHARED_SECRET'],cert=a.cert,key=a.key,tls_port=a.tls_port)
 raise SystemExit(launch(a.binary,c,time.time()+a.seconds))
