// Headless check of the regional landing page analysis.html (E19): countries, selector, comparison filters, links into country pages.
// Usage: npm i jsdom@24.1.3 in a scratch folder, then:
//   NODE_PATH=<that folder>/node_modules node tools/tests/regional_page_test.js analysis.html analysis
// The second argument is the folder that holds the country pages, used to check that every link lands on an issue card.
const fs = require('fs'); const path = require('path'); const { JSDOM, VirtualConsole } = require('jsdom');
const html = fs.readFileSync(process.argv[2], 'utf8'); const dir = process.argv[3] || 'analysis';
let ok = 0, bad = 0; const t = (n, c) => { if (c) ok++; else { bad++; console.log('FAIL', n); } };
function load(q) {
  const errors = []; const vc = new VirtualConsole(); vc.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://x.test/analysis.html' + (q || ''), virtualConsole: vc, pretendToBeVisual: true,
    beforeParse(w) { w.HTMLElement.prototype.scrollIntoView = function () { w.__scrolled = this.id; }; } });
  return { d: dom.window.document, w: dom.window, errors };
}
let { d, w, errors } = load('');
t('no script errors', errors.length === 0); if (errors.length) console.log(errors);
const navs = [...d.querySelectorAll('nav.top a')];
t('six sections, nav targets exist', navs.length === 6 && navs.every(a => d.getElementById(a.getAttribute('href').slice(1))));
const cards = [...d.querySelectorAll('.ccard')];
t('ten planned countries', cards.length === 10);
const done = cards.filter(c => /Validated/.test(c.textContent));
const sel = d.getElementById('f-country');
t('selector offers exactly the validated countries', sel.querySelectorAll('option[value]:not([value=""])').length === done.length);
t('countries without validated results are labelled', cards.filter(c => !done.includes(c)).every(c => /Not started|Draft/.test(c.textContent)));
const cols = d.querySelectorAll('#compare thead th[data-country]').length;
t('comparison has one column per validated country', cols === done.length);
const rows = [...d.querySelectorAll('#compare tbody tr')];
const vis = () => rows.filter(r => !r.classList.contains('hidden')).length;
const cnt = () => d.getElementById('m-count').textContent;
t('all issues shown, count text', vis() === rows.length && cnt() === `Showing ${rows.length} of ${rows.length} reform issues`);
const set = (id, v) => { const e = d.getElementById(id); if (e.type === 'checkbox') e.checked = v; else e.value = v; e.dispatchEvent(new w.Event('change')); };
set('m-area', 'fmw'); t('area filter: Chapter 2 only', vis() === rows.filter(r => r.dataset.area === 'fmw').length && vis() > 0 && vis() < rows.length);
d.getElementById('m-reset').click(); t('reset', vis() === rows.length);
set('m-hi', true); t('High-priority filter matches the priority section', vis() === d.querySelectorAll('#priority tbody tr').length && vis() > 0);
d.getElementById('m-reset').click();
set('m-theme', 'TECH-AI'); t('theme filter', vis() === rows.filter(r => (' ' + r.dataset.themes + ' ').includes(' TECH-AI ')).length);
d.getElementById('m-reset').click();
const q = d.getElementById('m-q'); q.value = 'RI-TEC-036'; q.dispatchEvent(new w.Event('input')); t('search by ID', vis() === 1);
q.value = 'zzzz'; q.dispatchEvent(new w.Event('input')); t('no match -> 0', vis() === 0); d.getElementById('m-reset').click();
// Only validated judgements: every cell is a validated country column, and cells carry priority, direction and gap
const cells = [...d.querySelectorAll('#compare td.cell')];
t('cells only for validated countries', cells.every(c => done.some(k => k.dataset.country === c.dataset.country)));
t('judged cells show priority, direction and gap', cells.filter(c => c.querySelector('.chip')).every(c => c.querySelectorAll('.chip').length === 3));
// Links into country pages land on an issue card
const links = [...d.querySelectorAll('#compare td.cell a, #priority td.cell a')];
let landed = links.length > 0;
const pages = {};
for (const a of links) {
  const [file, id] = a.getAttribute('href').split('#');
  const f = path.join(dir, path.basename(file));
  pages[f] = pages[f] || (fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : '');
  if (!pages[f].includes(`class="issue" id="${id}"`) && !pages[f].includes(`id="${id}"`)) { landed = false; console.log('no target', a.getAttribute('href')); break; }
}
t('every cell link lands on an issue card on its country page', landed);
if (done.length) {
  const cc = done[0].dataset.country;
  set('f-country', cc);
  const open = d.getElementById('open-country');
  t('choosing a country shows the open-page link', !open.classList.contains('hidden') && open.getAttribute('href') === `analysis/${cc}.html`);
  t('choosing a country narrows headlines', [...d.querySelectorAll('.headline')].every(h => h.classList.contains('hidden') === (h.dataset.country !== cc)));
  t('chosen country card highlighted', d.querySelector(`.ccard[data-country="${cc}"]`).classList.contains('sel'));
  ({ d, w } = load(`?country=${cc}`)); t('?country= preselects', d.getElementById('f-country').value === cc);
}
t('headline per validated country', d.querySelectorAll('.headline').length === done.length);
t('technology themes listed', d.querySelectorAll('#tech .theme').length >= 1);
console.log(`${ok} passed, ${bad} failed`);
