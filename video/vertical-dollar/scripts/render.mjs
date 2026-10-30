import {createServer} from 'vite';
import puppeteer from 'puppeteer-core';
import {access,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {execFileSync} from 'node:child_process';

const args=process.argv.slice(2);
const value=key=>{const i=args.indexOf(key);return i<0?undefined:args[i+1];};
const start=Number(value('--start')??0),frames=Number(value('--frames')??(3600-start)),name=value('--name')??'project';
const chunkSize=64;
if(!Number.isInteger(start)||start<0||!Number.isInteger(frames)||frames<2||start+frames>3600||!/^[a-zA-Z0-9_-]+$/.test(name))throw Error('Expected --start >= 0, --frames >= 2, start + frames <= 3600, and a simple --name');
const candidates=[process.env.CHROME_PATH,process.env.PUPPETEER_EXECUTABLE_PATH,...['chromium','chromium-browser','google-chrome','google-chrome-stable'].map(x=>{try{return execFileSync('which',[x],{encoding:'utf8'}).trim();}catch{return undefined;}}),'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',process.env.PROGRAMFILES&&`${process.env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`].filter(Boolean);
let executablePath;for(const candidate of candidates){try{await access(candidate);executablePath=candidate;break;}catch{}}
if(!executablePath)throw Error('Chrome/Chromium not found. Set CHROME_PATH to its executable.');
const out=resolve('output',name);try{if((await readdir(out)).some(x=>/^\d{6}\.png$/.test(x)))throw Error(`PNG frames already exist in ${out}; choose a clean output folder to avoid stale frames.`);}catch(e){if(e.code!=='ENOENT')throw e;}
const server=await createServer({server:{host:'127.0.0.1',port:0}});let browser;
try {
  await server.listen();const addr=server.httpServer.address();
  console.log(`Rendering ${frames} frames at 1080x1920, 60 fps to ${out}`);
  // Restart Chromium regularly to bound WebGL/PNG-export memory on long renders.
  for(let offset=0;offset<frames;offset+=chunkSize){
    const count=Math.min(chunkSize,frames-offset);
    // Motion Canvas exports two frames for a one-frame range. Absorb a lone
    // remainder into the previous batch (see count calculation below).
    if(count===1)break;
    const take=frames-offset===chunkSize+1?chunkSize+1:count;
    browser=await puppeteer.launch({executablePath,headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader',...(process.env.CHROME_NO_SANDBOX==='1'?['--no-sandbox']:[])]});
    const page=await browser.newPage();
    let rejectBrowser;const browserFailure=new Promise((_,reject)=>{rejectBrowser=reject;});
    page.on('pageerror',error=>rejectBrowser(error));
    browser.on('disconnected',()=>rejectBrowser(new Error('Browser disconnected during render.')));
    page.on('console',message=>{if(message.type()==='error')console.error('Browser:',message.text());});
    const batchStart=start+offset;
    console.log(`Rendering frames ${batchStart}–${batchStart+take-1}`);
    await Promise.race([page.goto(`http://127.0.0.1:${addr.port}/render.html?start=${batchStart}&frames=${take}&name=${name}`,{waitUntil:'networkidle0',timeout:120000}),browserFailure]);
    await Promise.race([page.waitForFunction(()=>document.documentElement.dataset.render!==undefined,{timeout:0,polling:1000}),browserFailure]);
    const state=await page.evaluate(()=>({state:document.documentElement.dataset.render,message:document.getElementById('status')?.textContent}));
    if(state.state!=='complete')throw Error(state.message??'Render failed');
    await browser.close();browser=undefined;
    if(take>count)offset++;
  }
  const files=(await readdir(out)).filter(x=>/^\d{6}\.png$/.test(x));
  if(files.length!==frames)throw Error(`Expected ${frames} frames; found ${files.length}.`);
  console.log(`Done: ${files.length} PNGs in ${out}`);
} finally {await browser?.close();await server.close();}
