"""PlanMark V1.10 browser QA: UI, backwards compatibility and mock PDF writer workflow.
The writer stub tests state transitions, NOT actual PDF binary validity."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(__file__).with_name('index.html').read_text()
MOCK='''() => {
class P {constructor(w,h,rot=0){this.w=w;this.h=h;this.rot=rot;}
 getWidth(){return this.w;}getHeight(){return this.h;} getRotation(){return {angle:this.rot};}setRotation(o){this.rot=o.angle;}setMediaBox(x,y,w,h){this.w=w;this.h=h;}setCropBox(x,y,w,h){this.w=w;this.h=h;}
 drawRectangle(){}drawText(){}drawLine(){}drawCircle(){}
 serialize(){return {w:this.w,h:this.h,rot:this.rot};}}
class D {constructor(){this.pages=[];this.catalog={get:()=>null,set:()=>{},delete:()=>{}};}static async create(){return new D();}static async load(bytes){const d=new D();const v=JSON.parse(new TextDecoder().decode(bytes));d.pages=v.pages.map(x=>new P(x.w,x.h,x.rot));return d;}
 addPage(o){const p=o instanceof P?o:new P(o[0],o[1]);this.pages.push(p);return p;}
 async copyPages(src,indices){return indices.map(i=>new P(src.getPages()[i].w,src.getPages()[i].h,src.getPages()[i].rot));}
 getPageCount(){return this.pages.length;}getPages(){return this.pages;}getPage(i){return this.pages[i];}setProducer(){}setCreator(){}
 async save(){return new TextEncoder().encode(JSON.stringify({pages:this.pages.map(x=>x.serialize()),pad:'a'.repeat(200)}));}}
window.PDFLib={PDFDocument:D,PDFName:{of:s=>s},PDFHexString:{fromText:s=>s},StandardFonts:{Helvetica:'H'},degrees:n=>({angle:n}),rgb:()=>({})};
window.pdfjsLib={GlobalWorkerOptions:{}};
openPdfWithWorkerFallback=async bytes=>{
 const o=JSON.parse(new TextDecoder().decode(bytes));return {numPages:o.pages.length,async getPage(i){const page=o.pages[i-1];return {getViewport({scale}){const turned=page.rot%180!==0;return {width:(turned?page.h:page.w)*scale,height:(turned?page.w:page.h)*scale,convertToPdfPoint:(x,y)=>[x,y]};},render(){return {promise:Promise.resolve()}}}}};
};
}'''
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1320,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content(HTML,wait_until='domcontentloaded');await page.wait_for_timeout(250)
  await page.evaluate(MOCK)
  # Add one annotation and one page link to check stable identity.
  await page.evaluate('''()=>{const id=state.activeDocumentId;state.pages[3].push({id:'MARK-4',type:'rect',x:20,y:25,w:40,h:50,style:{stroke:'#f00',fill:'none'}});state.references.push({referenceId:'R-4',sourceDocumentId:id,targetDocumentId:id,targetPageIndex:3,referenceLabel:'Page 4'});state.index=1;}''')
  await page.evaluate('window.PlanMarkV110.open("blank")')
  await page.locator('#pmBlankSize').select_option('A3');await page.locator('#pmOrientation').select_option('landscape')
  await page.locator('#pmBlankCount').fill('2')
  await page.locator('#pmDoAction').click();await page.wait_for_timeout(250)
  after=await page.evaluate('''()=>({n:state.pages.length,pid:state.documents[0].pageIds.length,marks:state.pages.map(p=>p.map(x=>x.id)),ref:state.references[0].targetPageIndex,sizes:state.pageSizes.slice(2,4),msg:document.getElementById('pmOrgStatus').innerText})''')
  print('INSERT:',after)
  assert after['n']==6 and after['marks'][5]==['MARK-4'] and after['ref']==5 and after['pid']==6,after
  # Select two marked pages and move them to the front.
  await page.evaluate('''()=>{window.PlanMarkV110.internal.selected=new Set([4,5]);}''')
  await page.locator('[data-pmorg-tab="move"]').click();await page.locator('#pmMoveTo').fill('1');await page.locator('#pmDoAction').click();await page.wait_for_timeout(220)
  moved=await page.evaluate('''()=>({page:state.pages.findIndex(p=>p.some(x=>x.id==='MARK-4')),ref:state.references[0].targetPageIndex,ids:state.documents[0].pageIds.length})''')
  print('MOVE:',moved);assert moved['page']==1 and moved['ref']==1,moved
  await page.locator('#pmUndoPages').click();await page.wait_for_timeout(180)
  undo=await page.evaluate('''()=>({n:state.pages.length,ref:state.references[0].targetPageIndex,page:state.pages.findIndex(p=>p.some(x=>x.id==='MARK-4'))})''')
  print('UNDO:',undo);assert undo['ref']==5 and undo['page']==5,undo
  await page.locator('#pmRedoPages').click();await page.wait_for_timeout(180)
  redo=await page.evaluate('''()=>({ref:state.references[0].targetPageIndex,page:state.pages.findIndex(p=>p.some(x=>x.id==='MARK-4'))})''')
  print('REDO:',redo);assert redo['ref']==1 and redo['page']==1,redo
  await page.evaluate('window.__answers=[];window.confirm=()=>true;')
  await page.locator('[data-pmorg-tab="delete"]').click()
  await page.locator('#pmRange').fill('2');await page.locator('#pmDoAction').click();await page.wait_for_timeout(220)
  deleted=await page.evaluate('''()=>({n:state.pages.length,missing:state.references[0].targetPageMissing,index:state.references[0].targetPageIndex,marks:state.pages.flat().map(x=>x.id)})''')
  print('DELETE:',deleted);assert deleted['n']==5 and deleted['missing'] and deleted['index']==-1 and not deleted['marks'],deleted
  print('ERRORS:',errors)
  assert not errors,errors
  await browser.close()
if __name__=='__main__':asyncio.run(main())
