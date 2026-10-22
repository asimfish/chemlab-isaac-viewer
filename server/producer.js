// Native SDKs may use absolute or relative motion; reflect both for camera gestures.
// Keep ordinary GUI clicks and drags in their original coordinate system.
function installPointerDirection(win) {
 win.__t588PointerMode='native';let drag=null;
 const names=['clientX','clientY','offsetX','offsetY','movementX','movementY'];
 const original=Object.fromEntries(names.map(name=>[name,Object.getOwnPropertyDescriptor(win.MouseEvent.prototype,name)]));
 const raw=(event,name)=>original[name].get.call(event);
 win.addEventListener('pointerdown',event=>{
  const button=event.buttons&2?2:(event.buttons&1)&&event.altKey?1:0;
  drag=button&&event.target?.id==='remote-video'?{button,clientX:raw(event,'clientX'),clientY:raw(event,'clientY'),offsetX:raw(event,'offsetX'),offsetY:raw(event,'offsetY')}:null;
 },true);
 win.addEventListener('pointermove',event=>{if(!event.buttons)drag=null},true);
 win.addEventListener('blur',()=>{drag=null},true);
 for(const name of names) {
  Object.defineProperty(win.MouseEvent.prototype,name,{...original[name],get(){
   const value=raw(this,name),mode=win.__t588PointerMode,axis=name.slice(-1);
   const reverse=mode==='both'||mode===(axis==='X'?'horizontal':'vertical');
   const camera=drag&&((this.buttons&drag.button)||this.type==='mouseup'||this.type==='pointerup');
   if(!camera||!reverse)return value;
   return name.startsWith('movement')?-value:2*drag[name]-value;
  }});
 }
}
installPointerDirection(window);
(() => {
 // Keep browser focus from scrolling the official client's video under the fixed input transform.
 addEventListener('DOMContentLoaded',()=>{document.documentElement.style.overflow='clip';document.body.style.overflow='clip';window.scrollTo(0,0)},{once:true});
 const focus=HTMLElement.prototype.focus;
 HTMLElement.prototype.focus=function(options){return focus.call(this,this.id==='remote-video'?{...options,preventScroll:true}:options)};
 addEventListener('scroll',()=>{if(scrollX||scrollY)scrollTo(0,0)},true);
 const gpu=__GPU__, secret='__SECRET__';
 const socket=new WebSocket('ws://127.0.0.1:18620/producer');
 socket.onopen=()=>socket.send(JSON.stringify({gpu,secret}));
 window.__t588pcs=[];window.__t588Encoded={frames:0,bytes:0,errors:[],started:Date.now()};let seq=0;
 const Original=window.RTCPeerConnection;
 window.RTCPeerConnection=new Proxy(Original,{construct(Target,args){
  args[0]={...args[0],encodedInsertableStreams:true};const p=new Target(...args);__t588pcs.push(p);
  p.addEventListener('track',e=>{if(e.track.kind!=='video')return;
   try{const streams=e.receiver.createEncodedStreams();
    streams.readable.pipeThrough(new TransformStream({transform(frame,controller){
     const b=new Uint8Array(frame.data);__t588Encoded.frames++;__t588Encoded.bytes+=b.length;
     if(socket.readyState===WebSocket.OPEN){
      if(socket.bufferedAmount>1048576){socket.close();}else{
       const packet=new Uint8Array(24+b.length),v=new DataView(packet.buffer);
       packet.set([84,53,56,56],0);v.setUint8(4,frame.type==='key'?1:0);v.setUint32(8,seq++);v.setUint32(12,frame.timestamp);v.setFloat64(16,Date.now());packet.set(b,24);socket.send(packet);
      }
     }controller.enqueue(frame);
    }})).pipeTo(streams.writable).catch(e=>__t588Encoded.errors.push(String(e)));
   }catch(e){__t588Encoded.errors.push(String(e))}
  });return p;
 }});
 window.__t588Stats=async()=>{const pcs=[];for(const p of __t588pcs){const rows=[];for(const s of(await p.getStats()).values())if(['inbound-rtp','candidate-pair','codec'].includes(s.type))rows.push(s);pcs.push({state:p.connectionState,stats:rows})}return{encoded:__t588Encoded,pcs}};
})();
