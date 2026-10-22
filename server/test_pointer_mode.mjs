import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
class MouseEvent {constructor(p){this.p=p}get clientX(){return this.p.x}get clientY(){return this.p.y}get offsetX(){return this.p.x}get offsetY(){return this.p.y}get movementX(){return this.p.dx}get movementY(){return this.p.dy}get buttons(){return this.p.buttons}get altKey(){return this.p.altKey}get target(){return{id:'remote-video'}}get type(){return this.p.type}}
const listeners={},window={MouseEvent,addEventListener:(name,fn)=>listeners[name]=fn},context={window};vm.createContext(context);
const source=fs.readFileSync(new URL('./producer.js',import.meta.url),'utf8');vm.runInContext(source.slice(0,source.indexOf('(() => {')),context);
for(const [mode,expected]of[['native',[4,6]],['vertical',[4,-6]],['horizontal',[-4,6]],['both',[-4,-6]]]){
 window.__t588PointerMode=mode;
 for(const gesture of[{buttons:2},{buttons:1,altKey:true}]){
  listeners.pointerdown(new MouseEvent({...gesture,type:'pointerdown',x:250,y:350}));
  const event=new MouseEvent({...gesture,type:'pointermove',x:254,y:356,dx:4,dy:6});
  assert.deepEqual([event.movementX,event.movementY],expected);
  assert.deepEqual([event.offsetX,event.offsetY],[250+expected[0],350+expected[1]]);
  const up=new MouseEvent({buttons:0,type:'mouseup',x:254,y:356});
  assert.deepEqual([up.offsetX,up.offsetY],[250+expected[0],350+expected[1]],'release must not snap back while held');
 }
 for(const buttons of[0,1,4]){
  listeners.pointerdown(new MouseEvent({buttons,x:250,y:350,type:'pointerdown'}));
  const event=new MouseEvent({buttons,type:'pointermove',x:254,y:356,dx:4,dy:6});
  assert.deepEqual([event.movementX,event.movementY],[4,6]);assert.deepEqual([event.offsetX,event.offsetY],[254,356]);
 }
}
console.log('Camera relative/absolute direction, button release, and ordinary GUI coordinates passed');
