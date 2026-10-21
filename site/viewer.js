const $=s=>document.querySelector(s),canvas=$('#screen');
const gpu=Number(new URLSearchParams(location.search).get('gpu')||0);
if(!Number.isInteger(gpu)||gpu<0||gpu>3)throw Error('Invalid GPU');
for(const a of document.querySelectorAll('nav a'))if(a.search===`?gpu=${gpu}`)a.classList.add('active');
let closeInfo=null;
let ws,decoder,writer,generator,waitingKey=true,lastSeq=-1,clockOffset=null,epoch=0,received=0,frames=0,drawn=0,bytes=0,errors=[],pending=new Map(),samples=[],rtt=[],receivePresent=[],transit=[],decodeQueueMax=0,pings=0,start=0,lastStats=null;
window.__viewerMetrics={};
function status(s){$('#status').textContent=s}
function codecFromKey(b){for(let i=0;i<b.length-8;i++){let n=0;if(b[i]===0&&b[i+1]===0&&b[i+2]===0&&b[i+3]===1)n=i+4;else if(b[i]===0&&b[i+1]===0&&b[i+2]===1)n=i+3;if(n&&(b[n]&31)===7)return 'avc1.'+[...b.slice(n+1,n+4)].map(v=>v.toString(16).padStart(2,'0')).join('')}throw Error('H264 SPS missing')}
function send(m){if(ws?.readyState===1)ws.send(JSON.stringify(m))}
function connect(){
 if(!('VideoDecoder'in window)||!('MediaStreamTrackGenerator'in window)){status('请使用支持 WebCodecs 的 Chrome / Edge');return}
 if(ws?.readyState===1){ws.close();return}
 closeInfo=null;waitingKey=true;lastSeq=-1;epoch=0;pending.clear();frames=0;drawn=0;received=0;bytes=0;errors=[];rtt=[];receivePresent=[];transit=[];decodeQueueMax=0;generator?.stop();if(decoder?.state!=='closed')decoder?.close();
 generator=new MediaStreamTrackGenerator({kind:'video'});writer=generator.writable.getWriter();canvas.srcObject=new MediaStream([generator]);canvas.play().catch(()=>{});
 decoder=new VideoDecoder({output:frame=>{const now=performance.now();const item=pending.get(frame.timestamp);if(item){receivePresent.push(now-item.at);if(clockOffset!==null)transit.push(Date.now()+clockOffset-item.server);pending.delete(frame.timestamp)}frames++;$('#hint').hidden=true;if(writer.desiredSize<=0){frame.close();return}writer.write(frame).then(()=>frame.close(),()=>frame.close());},error:e=>{errors.push(String(e));status('视频解码失败，请重新连接');waitingKey=true;}});
 ws=new WebSocket(`${location.protocol==='https:'?'wss:':'ws:'}//${location.host}/stream?gpu=${gpu}`);ws.binaryType='arraybuffer';start=performance.now();
 ws.onopen=()=>{status('正在载入官方界面');$('#connect').textContent='断开';canvas.focus()};
 ws.onclose=e=>{closeInfo={code:e.code,reason:e.reason,atSeconds:(performance.now()-start)/1000};status('已断开 · 可重新连接');$('#connect').textContent='连接'};
 ws.onerror=()=>status('连接失败');
 ws.onmessage=e=>{
  if(typeof e.data==='string'){const m=JSON.parse(e.data);if(m.type==='session')$('#expiry').textContent='本次渲染结束：'+new Date(m.deadline*1000).toLocaleString();
   if(m.type==='pong'){const elapsed=Date.now()-m.client;rtt.push(elapsed);samples.push({rtt:elapsed,offset:m.server-(m.client+Date.now())/2});samples=samples.slice(-30);clockOffset=[...samples].sort((a,b)=>a.rtt-b.rtt)[0].offset;}
   if(m.type==='native-stats')lastStats=m.stats;return;}
  const packet=new DataView(e.data);if(packet.byteLength<24||packet.getUint32(0)!==0x54353838)return;
  const key=packet.getUint8(4)===1,seq=packet.getUint32(8),rtp=packet.getUint32(12),server=packet.getFloat64(16),b=new Uint8Array(e.data,24);
  received++;bytes+=b.length;
  if(lastSeq>=0&&seq!==lastSeq+1){errors.push('sequence gap');waitingKey=true}lastSeq=seq;
  if(waitingKey){if(!key)return;decoder.configure({codec:codecFromKey(b),codedWidth:1600,codedHeight:900,optimizeForLatency:true,hardwareAcceleration:'prefer-software'});waitingKey=false;epoch=rtp;status(`GPU ${gpu} · 已连接`)}
  // RTP timestamp clock is90kHz. Sequence is preserved; never drop reference frames.
  const timestamp=Math.round(((rtp-epoch)>>>0)*1000000/90000);pending.set(timestamp,{at:performance.now(),server});
  decodeQueueMax=Math.max(decodeQueueMax,decoder.decodeQueueSize);
  try{decoder.decode(new EncodedVideoChunk({type:key?'key':'delta',timestamp,data:b}))}catch(e){errors.push(String(e));waitingKey=true}
  if(pending.size>600){errors.push('decoder stalled');ws.close()}
 };
}
function presented(){drawn++;canvas.requestVideoFrameCallback(presented)}canvas.requestVideoFrameCallback(presented);
const percentile=(v,p)=>v.length?[...v].sort((a,b)=>a-b)[Math.min(v.length-1,Math.floor(v.length*p))]:null;
setInterval(()=>{if(ws?.readyState===1){send({type:'ping',id:++pings,client:Date.now()});if(pings%5===0)send({type:'stats'})}
 const sec=(performance.now()-start)/1000;window.__viewerMetrics={gpu,connected:ws?.readyState===1,close:closeInfo,frames,drawn,received,bytes,seconds:sec,mbps:sec>0?bytes*8/sec/1e6:0,fps:sec>0?frames/sec:0,rtt:{n:rtt.length,p50:percentile(rtt.slice(3),.5),p95:percentile(rtt.slice(3),.95)},receiveToDecode:{n:receivePresent.length,p50:percentile(receivePresent.slice(3),.5),p95:percentile(receivePresent.slice(3),.95)},estimatedRelayToDecode:{n:transit.length,p50:percentile(transit,.5),p95:percentile(transit,.95),note:'Clock offset estimated by minimum RTT; excludes GPU encode and private WebRTC leg; decode completion is not glass-to-glass display.'},decodeQueueMax,errors,native:lastStats};
 receivePresent=receivePresent.slice(-1800);transit=transit.slice(-1800);rtt=rtt.slice(-300);
 $('#metrics').textContent=`${Math.round(window.__viewerMetrics.fps)} fps · ${window.__viewerMetrics.mbps.toFixed(2)} Mbps · 往返 ${window.__viewerMetrics.rtt.p50??'—'} ms`;
},1000);
const mods=e=>(e.altKey?1:0)|(e.ctrlKey?2:0)|(e.metaKey?4:0)|(e.shiftKey?8:0);
function point(e){const r=canvas.getBoundingClientRect();return{x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))}}
let lastMove=0;
for(const [event,action]of[['pointermove','mouseMoved'],['pointerdown','mousePressed'],['pointerup','mouseReleased']])canvas.addEventListener(event,e=>{e.preventDefault();if(event==='pointermove'&&performance.now()-lastMove<16)return;lastMove=performance.now();if(event==='pointerdown'){canvas.focus();canvas.setPointerCapture(e.pointerId)}send({type:'mouse',action,...point(e),button:action==='mouseMoved'?'none':['left','middle','right'][e.button],buttons:e.buttons,modifiers:mods(e),clickCount:Math.min(2,e.detail||1)})});
canvas.addEventListener('wheel',e=>{e.preventDefault();send({type:'mouse',action:'mouseWheel',...point(e),dx:e.deltaX,dy:e.deltaY,modifiers:mods(e)})},{passive:false});
canvas.addEventListener('contextmenu',e=>e.preventDefault());
for(const [event,action]of[['keydown','keyDown'],['keyup','keyUp']])canvas.addEventListener(event,e=>{e.preventDefault();send({type:'key',action,key:e.key,code:e.code,keyCode:e.keyCode,modifiers:mods(e)})});
$('#connect').onclick=connect;$('#fullscreen').onclick=()=>canvas.requestFullscreen();
window.addEventListener('pagehide',()=>ws?.close());
