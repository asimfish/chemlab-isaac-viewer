(() => {
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
