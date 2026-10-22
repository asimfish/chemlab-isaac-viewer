"""Task-local transport policy; never modify desktop or global proxy settings."""
import os
PROXY_NAMES=('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy')
def direct_command(args):
 if os.environ.get('T588_PROXY_MODE','direct')=='system':return list(args)
 return ['/usr/bin/env']+sum((['-u',k]for k in PROXY_NAMES),[])+list(args)
def browser_flags():
 return [] if os.environ.get('T588_PROXY_MODE','direct')=='system' else ['--no-proxy-server']

if __name__=='__main__':
 import sys
 if len(sys.argv)<2:raise SystemExit('Usage: transport_policy.py COMMAND [ARGS...]')
 argv=direct_command(sys.argv[1:]);os.execvp(argv[0],argv)
