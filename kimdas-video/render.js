// Usage: node render.js stills 5,30,...   |   node render.js video out.mp4 [fps]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [mode, arg, fpsArg] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto('file://' + path.join(__dirname, 'video.html') + '?render');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  const stage = await page.$('#stage');
  if (mode === 'stills') {
    for (const t of arg.split(',')) {
      await page.evaluate(t => render(t), +t);
      await stage.screenshot({ path: `stills/t${t}.jpg`, type: 'jpeg', quality: 80 });
    }
  } else {
    const fps = +(fpsArg || 30);
    const dur = await page.evaluate(() => DURATION);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', arg], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(dur * fps);
    for (let f = 0; f < n; f++) {
      await page.evaluate(t => render(t), f / fps);
      const buf = await stage.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 300 === 0) console.log(`frame ${f}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
