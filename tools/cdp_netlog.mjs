// Load a URL in an already-running headless Chromium (started with
// --remote-debugging-port=PORT) and record network requests, transfer sizes,
// console messages and a few page metrics via the Chrome DevTools Protocol.
//
// Usage: node tools/cdp_netlog.mjs PORT URL WIDTH HEIGHT MOBILE(0|1) OUT.json [SCROLL(0|1)]
// Uses Node's global fetch + WebSocket (Node >= 22). Executes nothing from raw/.
const [port, url, w, h, mobile, out, scroll] = process.argv.slice(2);
const fs = await import('node:fs');

const targets = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(targets.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0;
const pending = new Map();
const reqs = new Map();
const consoleMsgs = [];
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result ?? m.error); pending.delete(m.id); return; }
  const p = m.params;
  switch (m.method) {
    case 'Network.requestWillBeSent':
      reqs.set(p.requestId, { url: p.request.url, method: p.request.method, type: p.type, initiator: p.initiator?.type, t: p.timestamp });
      break;
    case 'Network.responseReceived': {
      const r = reqs.get(p.requestId) || {};
      Object.assign(r, { status: p.response.status, mime: p.response.mimeType, protocol: p.response.protocol,
        encoding: p.response.headers['content-encoding'] || p.response.headers['Content-Encoding'] || '',
        cache: p.response.headers['x-vercel-cache'] || '', server: p.response.headers['server'] || '' });
      reqs.set(p.requestId, r);
      break;
    }
    case 'Network.loadingFinished': {
      const r = reqs.get(p.requestId); if (r) r.bytes = p.encodedDataLength; break;
    }
    case 'Network.loadingFailed': {
      const r = reqs.get(p.requestId); if (r) r.failed = p.errorText; break;
    }
    case 'Runtime.consoleAPICalled':
      consoleMsgs.push({ type: p.type, text: p.args.map((a) => a.value ?? a.description ?? '').join(' ').slice(0, 300) });
      break;
    case 'Log.entryAdded':
      consoleMsgs.push({ type: p.entry.level, text: (p.entry.text || '').slice(0, 300), url: p.entry.url });
      break;
    case 'Runtime.exceptionThrown':
      consoleMsgs.push({ type: 'exception', text: p.exceptionDetails?.exception?.description?.slice(0, 300) });
      break;
  }
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

await send('Network.enable');
// Cold load without bypassing the in-memory cache (setCacheDisabled would
// re-request duplicate <img>/preload URLs and inflate the counts).
await send('Network.clearBrowserCache');
await send('Runtime.enable');
await send('Log.enable');
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: mobile === '1' ? 3 : 1, mobile: mobile === '1' });
if (mobile === '1') await send('Emulation.setTouchEmulationEnabled', { enabled: true });
// Observe LCP/CLS from the start of navigation.
await send('Page.addScriptToEvaluateOnNewDocument', { source: `
  window.__m={lcp:0,lcpEl:'',cls:0};
  new PerformanceObserver(l=>{for(const e of l.getEntries()){__m.lcp=e.startTime;__m.lcpEl=(e.element&&(e.element.tagName+'.'+(e.element.className||'')).slice(0,80))||e.url||''}}).observe({type:'largest-contentful-paint',buffered:true});
  new PerformanceObserver(l=>{for(const e of l.getEntries()){if(!e.hadRecentInput)__m.cls+=e.value}}).observe({type:'layout-shift',buffered:true});` });
await send('Page.navigate', { url });
await sleep(9000);
if (scroll === '1') {
  for (let i = 0; i < 12; i++) {
    await send('Runtime.evaluate', { expression: `(()=>{const s=[...document.querySelectorAll('.case-study-page,.case-widget--home,.about-overlay__scroller')].filter(e=>e.scrollHeight>e.clientHeight).pop()||document.scrollingElement; s.scrollBy(0, innerHeight*0.9); return s.className||'doc'})()` });
    await sleep(700);
  }
  await sleep(2000);
}
const metrics = await send('Runtime.evaluate', { returnByValue: true, expression: `(()=>{
  const nav=performance.getEntriesByType('navigation')[0]||{};
  const fcp=(performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime;
  const imgs=[...document.images]; const vids=[...document.querySelectorAll('video')];
  const fonts=[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight);
  const cs=getComputedStyle(document.body);
  return {title:document.title, ttfb:nav.responseStart, domContentLoaded:nav.domContentLoadedEventEnd, load:nav.loadEventEnd,
    fcp, lcp:__m.lcp, lcpEl:__m.lcpEl, cls:__m.cls, domNodes:document.getElementsByTagName('*').length,
    imgs:imgs.length, imgsComplete:imgs.filter(i=>i.complete&&i.naturalWidth).length,
    imgCurrentSrcSample:imgs.slice(0,4).map(i=>i.currentSrc.slice(-60)), videos:vids.length,
    videosPlaying:vids.filter(v=>!v.paused).length, videoSrcs:vids.slice(0,3).map(v=>v.currentSrc.slice(-50)), fonts,
    bodyBg:cs.backgroundColor, bodyColor:cs.color, bodyFont:cs.fontFamily,
    scrollW:document.documentElement.scrollWidth, innerW:innerWidth,
    h:[...document.querySelectorAll('h1,h2,h3')].map(e=>e.tagName+':'+e.textContent.trim().slice(0,40)).slice(0,20)}})()` });
const list = [...reqs.values()];
const total = list.reduce((a, r) => a + (r.bytes || 0), 0);
const byType = {};
for (const r of list) { const k = r.type || 'Other'; byType[k] = byType[k] || { n: 0, bytes: 0 }; byType[k].n++; byType[k].bytes += r.bytes || 0; }
const hosts = {};
for (const r of list) { try { const hh = new URL(r.url).host; hosts[hh] = (hosts[hh] || 0) + 1; } catch {} }
const result = { url, viewport: `${w}x${h}`, mobile: mobile === '1', scrolled: scroll === '1', requests: list.length, totalBytes: total, byType, hosts,
  metrics: metrics?.result?.value, console: consoleMsgs, requestsList: list.map((r) => ({ ...r, url: r.url.slice(0, 220) })) };
fs.writeFileSync(out, JSON.stringify(result, null, 1));
console.log(JSON.stringify({ requests: result.requests, totalKB: Math.round(total / 1024), byType, hosts, metrics: result.metrics, console: consoleMsgs.slice(0, 15) }, null, 1));
await send('Page.close').catch(() => {});
ws.close();
process.exit(0);
