"""Bounded native H264 GUI bridge. Public auth is required at edge; test mode bearer is in memory."""
import asyncio, contextlib, json, math, os, secrets, signal, struct, time
from pathlib import Path
from aiohttp import web, ClientSession, WSMsgType

ROOT=Path(__file__).resolve().parent
DEADLINE=float(os.environ.get('T588_SESSION_DEADLINE','1792599115.5804963'))
PRODUCER_SECRET=secrets.token_urlsafe(40)
TEST_SECRET=os.environ.get('T588_TEST_SECRET')
ALLOWED_HOST=os.environ.get('T588_PUBLIC_HOST','')
WORKERS={}; SESSION=None

@web.middleware
async def boundary(req,handler):
    if time.time()>=DEADLINE: raise web.HTTPGone(text='This GPU session has ended.')
    if req.path=='/producer': return await handler(req)
    local=req.host in ('127.0.0.1:18620','localhost:18620')
    if TEST_SECRET and not (req.headers.get('Authorization')=='Bearer '+TEST_SECRET or req.cookies.get('t588_test')==TEST_SECRET):
        raise web.HTTPUnauthorized(text='Authentication required')
    if not TEST_SECRET and not local and req.host!=ALLOWED_HOST:
        raise web.HTTPForbidden(text='Unknown gateway host')
    origin=req.headers.get('Origin')
    if origin and origin not in ('http://127.0.0.1:18620','https://'+ALLOWED_HOST):
        raise web.HTTPForbidden(text='Cross-origin request denied')
    response=await handler(req)
    if TEST_SECRET and req.headers.get('Authorization')=='Bearer '+TEST_SECRET:
        response.set_cookie('t588_test',TEST_SECRET,httponly=True,secure=req.host not in ('127.0.0.1:18620','localhost:18620'),samesite='Strict',max_age=900)
    response.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; connect-src 'self' ws://127.0.0.1:18620 wss:; script-src 'self'; style-src 'self'; frame-ancestors 'none'"})
    return response

class Worker:
    def __init__(self,gpu):
        self.gpu=gpu;self.cdp=None;self.pending={};self.n=0;self.viewer=None;self.queue=asyncio.Queue(maxsize=12)
        self.input=asyncio.Queue(maxsize=128);self.tasks=[];self.frames=0;self.bytes=0;self.dropped=0;self.started=time.time();self.last_view=time.time();self.target=None;self.ready=False
    async def call(self,method,params=None):
        self.n+=1;n=self.n;f=asyncio.get_running_loop().create_future();self.pending[n]=f
        await self.cdp.send_json({'id':n,'method':method,'params':params or {}})
        try: return await asyncio.wait_for(f,8)
        finally:self.pending.pop(n,None)
    async def read_cdp(self):
        async for msg in self.cdp:
            if msg.type!=WSMsgType.TEXT:continue
            m=json.loads(msg.data)
            if m.get('id') in self.pending:
                f=self.pending[m['id']]
                if not f.done():f.set_result(m.get('result',{}))
    async def start(self):
        async with SESSION.put('http://127.0.0.1:18619/json/new?about:blank') as r:page=await r.json()
        self.target=page['id'];self.cdp=await SESSION.ws_connect(page['webSocketDebuggerUrl'],max_msg_size=2**22)
        self.tasks.append(asyncio.create_task(self.read_cdp()))
        await self.call('Page.enable');await self.call('Runtime.enable')
        await self.call('Emulation.setDeviceMetricsOverride',{'width':1600,'height':960,'deviceScaleFactor':1,'mobile':False})
        source=(ROOT/'producer.js').read_text().replace('__GPU__',str(self.gpu)).replace('__SECRET__',PRODUCER_SECRET)
        await self.call('Page.addScriptToEvaluateOnNewDocument',{'source':source})
        await self.call('Page.navigate',{'url':f'http://127.0.0.1:18600/?gpu={self.gpu}'})
        self.tasks.append(asyncio.create_task(self.inputs()))
    async def inputs(self):
        while True:
            m=await self.input.get()
            try:
                typ=m.get('type')
                if typ=='mouse':
                    x=float(m['x']);y=float(m['y'])
                    if not (math.isfinite(x) and math.isfinite(y) and 0<=x<=1 and 0<=y<=1):continue
                    action=m.get('action');button=m.get('button','none')
                    if action not in ('mouseMoved','mousePressed','mouseReleased','mouseWheel') or button not in ('none','left','right','middle'):continue
                    p={'type':action,'x':x*1600,'y':60+y*900,'button':button,'buttons':int(m.get('buttons',0))&7,'modifiers':int(m.get('modifiers',0))&15}
                    if action in ('mousePressed','mouseReleased'):p['clickCount']=min(2,max(1,int(m.get('clickCount',1))))
                    if action=='mouseWheel':p.update(deltaX=max(-500,min(500,float(m.get('dx',0)))),deltaY=max(-500,min(500,float(m.get('dy',0)))))
                    await self.call('Input.dispatchMouseEvent',p)
                elif typ=='key':
                    key=str(m.get('key',''));code=str(m.get('code',''));mods=int(m.get('modifiers',0))&15
                    if len(key)>32 or len(code)>32 or key in ('F5','F11','F12','Meta') or mods&4 or (mods&2 and key.lower() in ('l','t','w','n','r','p','o')):continue
                    action=m.get('action')
                    if action not in ('keyDown','keyUp'):continue
                    p={'type':action,'key':key,'code':code,'windowsVirtualKeyCode':max(0,min(255,int(m.get('keyCode',0)))),'modifiers':mods}
                    if action=='keyDown' and len(key)==1 and not(mods&6):p.update(text=key,unmodifiedText=key)
                    await self.call('Input.dispatchKeyEvent',p)
            except (ValueError,KeyError,TypeError,asyncio.TimeoutError):pass
    async def stats(self):
        r=await self.call('Runtime.evaluate',{'expression':'(async()=>JSON.stringify(await window.__t588Stats()))()','awaitPromise':True,'returnByValue':True})
        return json.loads(r.get('result',{}).get('value','{}'))
    async def close(self):
        if self.cdp:
            with contextlib.suppress(Exception):await self.call('Page.navigate',{'url':'about:blank'})
            await self.cdp.close()
        for t in self.tasks:t.cancel()
        if self.target:
            with contextlib.suppress(Exception):
                async with SESSION.get('http://127.0.0.1:18619/json/close/'+self.target):pass
        if self.viewer:await self.viewer.close()

async def producer(req):
    if req.host!='127.0.0.1:18620' or req.headers.get('Origin')!='http://127.0.0.1:18600':raise web.HTTPForbidden()
    ws=web.WebSocketResponse(max_msg_size=2**21,compress=False,heartbeat=20);await ws.prepare(req)
    try:
        m=await asyncio.wait_for(ws.receive_json(),3)
        if not secrets.compare_digest(str(m.get('secret','')),PRODUCER_SECRET):raise ValueError()
        gpu=m.get('gpu');w=WORKERS.get(gpu)
        if w is None:raise ValueError()
        async for msg in ws:
            if msg.type==WSMsgType.BINARY and len(msg.data)>=24 and msg.data[:4]==b'T588':
                w.frames+=1;w.bytes+=len(msg.data);w.ready=True
                if w.viewer:
                    # Never discard an H264 reference frame and continue its dependents.
                    # Congestion closes the stream; reconnect starts a fresh keyframe.
                    if w.queue.full():
                        print('T588_STREAM_CONGESTED',w.gpu,w.queue.qsize(),flush=True)
                        w.dropped+=1;await w.viewer.close(code=1013,message=b'Network congested; reconnect');break
                    w.queue.put_nowait(msg.data)
    except (ValueError,asyncio.TimeoutError):pass
    finally:await ws.close()
    return ws

async def stream(req):
    try:gpu=int(req.query.get('gpu','0'))
    except ValueError:raise web.HTTPBadRequest()
    if gpu not in range(4):raise web.HTTPBadRequest()
    existing=WORKERS.get(gpu)
    if existing and existing.viewer and not existing.viewer.closed:raise web.HTTPConflict(text='This GPU already has an active viewer.')
    if existing:await existing.close()
    w=Worker(gpu);WORKERS[gpu]=w
    ws=web.WebSocketResponse(max_msg_size=16384,compress=False,heartbeat=15);await ws.prepare(req);w.viewer=ws
    async def push():
        while True:
            data=await w.queue.get()
            await asyncio.wait_for(ws.send_bytes(data),3)
    sender=asyncio.create_task(push())
    try:
        await ws.send_json({'type':'session','gpu':gpu,'deadline':DEADLINE,'width':1600,'height':900})
        await w.start()
        async for msg in ws:
            if msg.type!=WSMsgType.TEXT:continue
            w.last_view=time.time()
            try:m=json.loads(msg.data)
            except ValueError:continue
            if not isinstance(m,dict):continue
            if m.get('type')=='ping':await ws.send_json({'type':'pong','id':m.get('id'),'client':m.get('client'),'server':time.time()*1000})
            elif m.get('type')=='stats':await ws.send_json({'type':'native-stats','stats':await w.stats()})
            elif not w.input.full():w.input.put_nowait(m)
    finally:
        sender.cancel();await asyncio.gather(sender,return_exceptions=True);await w.close()
        if WORKERS.get(gpu) is w:WORKERS.pop(gpu,None)
    return ws

async def static(req):
    name=req.match_info.get('name') or 'index.html'
    if name not in ('index.html','viewer.js','viewer.css'):raise web.HTTPNotFound()
    return web.FileResponse(ROOT.parent/'site'/name)
async def health(req):return web.json_response({'status':'ready','deadline':DEADLINE,'gpu_count':4})
async def lifetime(app):
    global SESSION
    SESSION=ClientSession()
    async def reap():
        while time.time()<DEADLINE:
            await asyncio.sleep(10)
            for w in list(WORKERS.values()):
                if time.time()-w.last_view>180:await w.close()
        os.kill(os.getpid(),signal.SIGTERM)
    t=asyncio.create_task(reap());yield;t.cancel()
    for w in list(WORKERS.values()):await w.close()
    await SESSION.close()
def make_app():
    app=web.Application(middlewares=[boundary],client_max_size=16384)
    app.cleanup_ctx.append(lifetime)
    app.router.add_get('/producer',producer);app.router.add_get('/stream',stream);app.router.add_get('/health',health)
    app.router.add_get('/',static);app.router.add_get('/{name}',static)
    return app
if __name__=='__main__':web.run_app(make_app(),host='127.0.0.1',port=18620,access_log=None,print=None)
