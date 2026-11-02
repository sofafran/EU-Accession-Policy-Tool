// Headless check of the analysis product page (navigation, filters, search, anchors, labels).
// Usage: npm i jsdom@24.1.3 in a scratch folder, then: NODE_PATH=<that folder>/node_modules node tools/tests/analysis_page_test.js analysis.html
const fs = require('fs'); const { JSDOM } = require('jsdom');
const html = fs.readFileSync(process.argv[2], 'utf8');
let ok = 0, bad = 0; const t = (n, c) => { if (c) ok++; else { bad++; console.log('FAIL', n); } };
function load(hash) {
  const errors = [];
  const vc = new (require('jsdom').VirtualConsole)(); vc.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://x.test/analysis.html' + (hash || ''), virtualConsole: vc, pretendToBeVisual: true, beforeParse(win) { win.HTMLElement.prototype.scrollIntoView = function () { win.__scrolled = this.id; }; } });

  dom.window.document.dispatchEvent(new dom.window.Event('DOMContentLoaded'));
  return { dom, d: dom.window.document, w: dom.window, errors };
}
let { d, w, errors } = load('');
t('no script errors', errors.length === 0); if (errors.length) console.log(errors);
const vis = () => [...d.querySelectorAll('.issue')].filter(c => !c.classList.contains('hidden')).length;
const cnt = () => d.getElementById('f-count').textContent;
t('48 cards', d.querySelectorAll('.issue').length === 48);
t('all visible, count text', vis() === 48 && cnt() === 'Showing 48 of 48 reform issues');
t('cards start collapsed', [...d.querySelectorAll('details.more')].every(x => !x.open));
const ids = ['overview','chapter2','tech','priority','comparators','options','evidence'];
t('nav targets exist', [...d.querySelectorAll('nav.top a')].every(a => d.getElementById(a.getAttribute('href').slice(1))) && d.querySelectorAll('nav.top a').length === 7);
t('back to top links', d.querySelectorAll('a.totop').length >= 6 && d.getElementById('top'));
const set = (id, v) => { const e = d.getElementById(id); e.value = v; e.dispatchEvent(new w.Event('change')); };
set('f-pri', 'High'); t('priority High -> 19', vis() === 19 && cnt() === 'Showing 19 of 48 reform issues');
set('f-strand', 'fmw'); t('High + Chapter 2 -> 4', vis() === 4);
t('tech group hidden when empty', d.getElementById('tech').classList.contains('hidden'));
d.getElementById('f-reset').click(); t('reset -> 48', vis() === 48);
set('f-dir', 'improving'); t('improving -> 5', vis() === 5); d.getElementById('f-reset').click();
set('f-gap', 'open'); t('gap open -> 20', vis() === 20); d.getElementById('f-reset').click();
const q = d.getElementById('f-q'); q.value = 'portal'; q.dispatchEvent(new w.Event('input'));
t('search portal finds RI-TEC-036', !d.getElementById('RI-TEC-036').classList.contains('hidden') && vis() < 48);
q.value = 'RI-FMW-001'; q.dispatchEvent(new w.Event('input')); t('search by ID', vis() >= 1 && !d.getElementById('RI-FMW-001').classList.contains('hidden'));
q.value = 'zzzz'; q.dispatchEvent(new w.Event('input')); t('no match -> 0', vis() === 0 && cnt() === 'Showing 0 of 48 reform issues');
d.getElementById('f-reset').click();
d.querySelector('nav.top a[data-strand="tec"]').click(); t('nav Technology filters to tech', vis() === 34 && d.getElementById('f-strand').value === 'tec');
d.querySelector('nav.top a[data-strand="fmw"]').click(); t('nav Chapter 2 filters to fmw', vis() === 14);
({ d, w } = load('#RI-TEC-028'));
t('anchor opens card', d.querySelector('#RI-TEC-028 details.more').open && w.__scrolled === 'RI-TEC-028');
({ d, w } = load(''));
set('f-strand', 'fmw'); w.location.hash = '#RI-TEC-036'; w.dispatchEvent(new w.HashChangeEvent('hashchange'));
t('anchor to hidden card resets filters and opens', !d.getElementById('RI-TEC-036').classList.contains('hidden') && d.querySelector('#RI-TEC-036 details.more').open);
t('options labelled internal draft', [...d.querySelectorAll('.option')].every(o => o.textContent.includes('Internal draft')) && d.querySelectorAll('.option').length === 10);
t('cases labelled agent synthesis', [...d.querySelectorAll('.case')].every(o => o.textContent.includes('Agent synthesis')) && d.querySelectorAll('.case').length === 9);
t('19 priority panels', d.querySelectorAll('.pcard').length === 19);
t('every card has evidence refs', [...d.querySelectorAll('.issue')].every(c => c.querySelector('details.refs code')));
t('every option has evidence refs', [...d.querySelectorAll('.option')].every(c => c.querySelector('details.refs')));
t('no validated wording on options', ![...d.querySelectorAll('.option')].some(o => /validated recommendation/i.test(o.textContent) && !/not validated/i.test(o.textContent)));
set('f-st', 'rereview'); t('status re-review -> 3', vis() === 3); set('f-st', 'analyst'); t('status analyst -> 1', vis() === 1 && !d.getElementById('RI-TEC-017').classList.contains('hidden'));
d.getElementById('f-reset').click(); t('reset clears status', vis() === 48 && d.getElementById('f-st').value === '');
t('every card shows a concise assessment', [...d.querySelectorAll('.issue')].every(c => { const a = c.querySelector(':scope > .assess'); return a && a.textContent.length > 40; }));
t('priority index links resolve', [...d.querySelectorAll('.pindex a')].length === 19 && [...d.querySelectorAll('.pindex a')].every(a => d.getElementById(a.getAttribute('href').slice(1))));
t('overview stat tiles link to sections', [...d.querySelectorAll('.stat a')].every(a => d.getElementById(a.getAttribute('href').slice(1))));
t('summary as bullets', d.querySelectorAll('#overview ul.says li').length >= 5);
t('flagged label visible', d.querySelector('#RI-FMW-003').textContent.includes('Flagged for re-review'));
console.log(`${ok} passed, ${bad} failed`);
