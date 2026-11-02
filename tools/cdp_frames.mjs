// Capture a short sequence of JPEG frames around an interaction on dmcg.co,
// via CDP on an already-running headless Chromium.
//
// Usage: node tools/cdp_frames.mjs PORT OUTDIR
// Steps: load home -> hover first project card -> click it (case-study open
// transition) -> scroll the case study -> open the About overlay.
const [port, outDir] = process.argv.slice(2);
const fs = await import('node:fs');
const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result ?? m.error); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 55 }); fs.writeFileSync(`${outDir}/${name}.jpg`, Buffer.from(r.data, 'base64')); console.log('frame', name); };
const evalv = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true }))?.result?.value;
const mouse = (type, x, y) => send('Input.dispatchMouseEvent', { type, x, y, button: type === 'mouseMoved' ? 'none' : 'left', clickCount: type === 'mouseMoved' ? 0 : 1 });

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'https://dmcg.co/' });
await sleep(7000);
const rect = await evalv(`(()=>{const r=document.querySelector('.project-grid-card__media').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
await mouse('mouseMoved', rect.x, rect.y);
await sleep(1200);
await shot('t1-hover');
await mouse('mousePressed', rect.x, rect.y); await mouse('mouseReleased', rect.x, rect.y);
await sleep(120); await shot('t2-open-120ms');
await sleep(250); await shot('t3-open-370ms');
await sleep(2500); await shot('t4-open-settled');
console.log('url now', await evalv('location.pathname'));
await evalv(`(()=>{const s=[...document.querySelectorAll('.case-study-page')].pop(); if(s) s.scrollBy(0, innerHeight*1.6); return !!s})()`);
await sleep(1500); await shot('t5-case-scrolled');
console.log('dock html', (await evalv(`(document.querySelector('[class*=case-study-dock]')||{}).className`)));
await send('Page.close').catch(() => {}); ws.close(); process.exit(0);
