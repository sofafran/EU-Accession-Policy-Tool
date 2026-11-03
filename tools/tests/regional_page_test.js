// Headless check of the regional page analysis.html (E19, front-end spec 0.2): header, country status cards, heatmap, Technology and AI, comparison, links.
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
const done = cards.filter(c => c.querySelector('.top3'));
const sel = d.getElementById('f-country');
t('selector offers exactly the validated countries', sel.querySelectorAll('option[value]:not([value=""])').length === done.length);
t('countries without validated results show status only', cards.filter(c => !done.includes(c)).every(c => /Not started|In progress/.test(c.querySelector('.rs').textContent) && !c.querySelector('.bd')));
const card = cc => cards.find(c => c.dataset.country === cc);
t('North Macedonia: plain run status, cut-off, top three, direction bar', /Closed: alpha complete/.test(card('MKD').textContent) && /Evidence cut-off/.test(card('MKD').textContent) && card('MKD').querySelectorAll('.top3 li').length === 3 && card('MKD').querySelector('.dbar .seg'));
t('Moldova: in progress, draft page link only', /In progress: 7 EU extraction and taxonomy/.test(card('MDA').textContent) && /Draft/.test(card('MDA').textContent) && !card('MDA').querySelector('.top3'));
t('Montenegro: Not started and nothing else', card('MNE').querySelector('.rs').textContent === 'Not started' && !card('MNE').querySelector('a'));
const head = d.querySelector('header.fe-head');
t('shared header with explainer link', head && head.querySelector('a.fe-how').getAttribute('href') === 'tool-explainer.html');
t('only the five content labels as status chips', [...d.querySelectorAll('.sc')].every(s => ['Validated', 'Pending review', 'Proposed', 'Draft', 'Not started'].includes(s.textContent)));
const hm = d.getElementById('hm-all');
t('heatmap: one column, single-country note', hm.querySelectorAll('thead th').length === 1 + done.length && (done.length !== 1 || /Only one country/.test(d.getElementById('pattern').textContent)));
t('heatmap: 12 rows before Show all', hm.querySelectorAll('tbody tr:not(.hidden)').length === 12);
d.querySelector('.hm-all[data-for="hm-all"]').click(); t('heatmap: show all', hm.querySelectorAll('tbody tr.hidden').length === 0);
t('heatmap cells carry text, not colour only', [...hm.querySelectorAll('td.hm-c')].every(c => /Gap:/.test(c.textContent) && c.textContent.trim().length > 8));
t('Technology and AI section with heatmap and caption', d.getElementById('hm-tech') && /made by colleagues, not by the tool/.test(d.getElementById('tech').textContent));

const cols = d.querySelectorAll('#compare thead th[data-country]').length;
t('comparison has one column per validated country', cols === done.length);
const rows = [...d.querySelectorAll('#compare tbody tr')];
const vis = () => rows.filter(r => !r.classList.contains('hidden')).length;
hm.querySelector('a.hm-row').click(); t('heatmap row opens the comparison for that issue', vis() === 1);
d.getElementById('m-reset').click();
const cnt = () => d.getElementById('m-count').textContent;
t('all issues shown, count text', vis() === rows.length && cnt() === `Showing ${rows.length} of ${rows.length} reform issues`);
const set = (id, v) => { const e = d.getElementById(id); if (e.type === 'checkbox') e.checked = v; else e.value = v; e.dispatchEvent(new w.Event('change')); };
set('m-area', 'fmw'); t('area filter: Chapter 2 only', vis() === rows.filter(r => r.dataset.area === 'fmw').length && vis() > 0 && vis() < rows.length);
d.getElementById('m-reset').click(); t('reset', vis() === rows.length);
set('m-hi', true); t('High-priority filter', vis() === rows.filter(r => r.dataset.high).length && vis() > 0);
d.getElementById('m-reset').click();
const q = d.getElementById('m-q'); q.value = 'RI-TEC-036'; q.dispatchEvent(new w.Event('input')); t('search by ID', vis() === 1);
q.value = 'zzzz'; q.dispatchEvent(new w.Event('input')); t('no match -> 0', vis() === 0); d.getElementById('m-reset').click();
// Only validated judgements: every cell is a validated country column, and cells carry priority, direction and gap
const cells = [...d.querySelectorAll('#compare td.cell')];
t('cells only for validated countries', cells.every(c => done.some(k => k.dataset.country === c.dataset.country)));
t('judged cells show priority, direction and gap', cells.filter(c => c.querySelector('.bd')).every(c => c.querySelectorAll('.bd').length === 3) && cells.some(c => c.querySelector('.bd')));
// Links into country pages land on an issue card
const links = [...d.querySelectorAll('#compare td.cell a, .hm td a, #countries .top3 a')];
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
t('headline synthesis labelled', [...d.querySelectorAll('.headline')].every(h => /Agent synthesis, validated at G7/.test(h.textContent)));
console.log(`${ok} passed, ${bad} failed`);
process.exit(bad ? 1 : 0);
