// Headless check of the country product page (front-end spec 0.2): summary layer, cards, filters, issue panel, chain, evidence drawer, labels.
// Usage: npm i jsdom@24.1.3 in a scratch folder, then: NODE_PATH=<that folder>/node_modules node tools/tests/analysis_page_test.js analysis/MKD.html
const fs = require('fs'); const { JSDOM, VirtualConsole } = require('jsdom');
const html = fs.readFileSync(process.argv[2], 'utf8');
let ok = 0, bad = 0; const t = (n, c) => { if (c) ok++; else { bad++; console.log('FAIL', n); } };
function load(hash) {
  const errors = []; const vc = new VirtualConsole(); vc.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://x.test/analysis/MKD.html' + (hash || ''), virtualConsole: vc, pretendToBeVisual: true,
    beforeParse(w) { w.HTMLElement.prototype.scrollIntoView = function () { w.__scrolled = this.id; }; w.scrollTo = function () {}; } });
  return { d: dom.window.document, w: dom.window, errors };
}
let { d, w, errors } = load('');
const EV = JSON.parse(d.getElementById('ev').textContent);
t('no script errors', errors.length === 0); if (errors.length) console.log(errors);
const vis = () => [...d.querySelectorAll('.issue')].filter(c => !c.classList.contains('hidden')).length;
const cnt = () => d.getElementById('f-count').textContent;
const set = (id, v) => { const e = d.getElementById(id); e.value = v; e.dispatchEvent(new w.Event('change')); };
const reset = () => { const c = d.querySelector('.fchip.clear'); if (c) c.click(); };
// Shared header
const head = d.querySelector('header.fe-head');
t('shared header: brand, breadcrumb, switcher, explainer link', head && head.querySelector('.fe-brand') && head.querySelector('.crumbs') && head.querySelector('select') &&
  head.querySelector('a.fe-how').getAttribute('href') === '../tool-explainer.html' && head.querySelector('a.fe-how').textContent === 'How the tool works');
t('switcher: Moldova marked draft, Montenegro not started', /Moldova \(draft\)/.test(head.textContent) && /Montenegro \(not started\)/.test(head.textContent));
t('run status in plain text', d.querySelector('.pagehead .runline').textContent.startsWith('Closed: alpha complete'));
// Summary layer
t('overall assessment labelled agent synthesis', /Agent synthesis, validated at G7/.test(d.querySelector('#overview .overall').textContent));
t('five top priority cards, High first, links resolve', d.querySelectorAll('#overview .tcard').length === 5 &&
  [...d.querySelectorAll('#overview .tcard')].every(a => /Priority High/.test(a.textContent) && d.getElementById(a.getAttribute('href').slice(1))));
t('three summary lists', d.querySelectorAll('#overview .flist').length === 3);
t('improving list = 5', /What is improving \(5\)/.test(d.querySelector('#overview').textContent));
t('banner present', !!d.querySelector('#overview .banner26'));
// Cards and filters
t('48 cards, count text', d.querySelectorAll('.issue').length === 48 && vis() === 48 && cnt() === 'Showing 48 of 48 reform issues');
const pr = [...d.querySelectorAll('.issue')].map(c => c.dataset.priority);
t('default sort by priority', pr.indexOf('Low') > pr.lastIndexOf('High') && pr.indexOf('Medium') > pr.lastIndexOf('High'));
t('cards: definition with EU requirement count, four badges, status chip', [...d.querySelectorAll('.issue')].every(c =>
  /EU requirement/.test(c.querySelector('.req').textContent) && c.querySelectorAll(':scope > .badges .bd').length === 4 && c.querySelector(':scope > .top .sc')));
t('card assessment is the priority reason', [...d.querySelectorAll('.issue')].every(c => c.querySelector(':scope > .assess p').textContent.length > 40));
t('re-review note separate from status', ['RI-FMW-003', 'RI-TEC-017', 'RI-TEC-033'].every(x => /Validated/.test(d.querySelector('#' + x + ' > .top .sc').textContent) &&
  /Flagged for re-review/.test(d.querySelector('#' + x + ' > .top').textContent)) && d.querySelectorAll('.issue > .top .tag').length === 21);
set('f-pri', 'High'); t('priority High -> 19', vis() === 19 && cnt() === 'Showing 19 of 48 reform issues');
t('filter chip shown', /Priority: High/.test(d.getElementById('f-chips').textContent));
set('f-strand', 'fmw'); t('High + Chapter 2 -> 4', vis() === 4);
d.querySelector('.fchip[data-k="strand"]').click(); t('removing a chip -> 19', vis() === 19);
reset(); t('clear all -> 48', vis() === 48 && !d.getElementById('f-chips').textContent);
set('f-dir', 'improving'); t('improving -> 5', vis() === 5); reset();
set('f-gap', 'open'); t('gap open -> 20', vis() === 20); reset();
set('f-st', 'Validated'); t('status Validated -> 48', vis() === 48); set('f-st', 'Proposed'); t('status Proposed -> 0', vis() === 0); reset();
set('f-comp', 'yes'); t('comparator available -> 3', vis() === 3); reset();
const q = d.getElementById('f-q'); q.value = 'portal'; q.dispatchEvent(new w.Event('input'));
t('search portal finds RI-TEC-036', !d.getElementById('RI-TEC-036').classList.contains('hidden') && vis() < 48);
q.value = 'zzzz'; q.dispatchEvent(new w.Event('input')); t('no match -> 0', vis() === 0); reset();
d.querySelector('nav.top a[data-strand="tec"]').click(); t('nav Technology and AI preset -> 34', vis() === 34);
d.querySelector('nav.top a[data-strand="fmw"]').click(); t('nav Chapter 2 -> 14', vis() === 14); reset();
set('f-u26', 'held'); t('2026 filter: evidence held -> 15', vis() === 15); reset();
t('filter values use display labels', [...d.querySelectorAll('#f-gap option')].map(o => o.textContent).join('|') === 'All|Open|Partly addressed|Largely closed|Insufficient evidence');
// Issue panel and chain
({ d, w, errors } = load('#RI-TEC-028'));
const card = d.getElementById('RI-TEC-028');
t('hash opens the issue panel', card.classList.contains('open') && /›/.test(d.getElementById('crumb-issue').textContent));
t('nine chain steps', card.querySelectorAll('.chain .step').length === 9);
t('stated and assessed marked', card.querySelectorAll('.step.k-stated').length === 3 && card.querySelectorAll('.step.k-assessed').length === 6);
t('panel badges each with a status', card.querySelectorAll('.hbs .hb').length === 4 && [...card.querySelectorAll('.hbs .hb')].every(b => b.querySelector('.sc')));
t('comparator cards in the chain, with country and lesson tag', card.querySelectorAll('.chain .case').length === 3 && [...card.querySelectorAll('.chain .case')].every(c => /Agent synthesis, validated at G6b/.test(c.textContent)));
t('draft country page labelled before link', [...card.querySelectorAll('.chain .case a[href="MDA.html"]')].every(a => /Draft country page/.test(a.textContent)) && card.querySelector('.chain .case a[href="MDA.html"]'));
t('policy options in chain labelled internal draft', card.querySelectorAll('.chain .option').length > 0 && [...card.querySelectorAll('.chain .option')].every(o => /Internal draft/.test(o.textContent)));
t('adoption is not success note', /Adoption is not success/.test(card.textContent));
card.querySelector('.pclose').click(); t('close panel', !card.classList.contains('open') && !d.getElementById('crumb-issue').textContent);
({ d, w } = load('#RI-FMW-012'));
t('issue without comparator: empty states', /No comparator analysis for this issue in this run/.test(d.getElementById('RI-FMW-012').textContent) &&
  /No policy options for this issue in this run/.test(d.getElementById('RI-FMW-012').textContent));
({ d, w } = load(''));
set('f-strand', 'fmw'); w.location.hash = '#RI-TEC-036'; w.dispatchEvent(new w.HashChangeEvent('hashchange'));
t('link to a filtered-out issue resets filters and opens', !d.getElementById('RI-TEC-036').classList.contains('hidden') && d.getElementById('RI-TEC-036').classList.contains('open'));
// Evidence drawer
const evb = d.querySelector('#RI-TEC-036 .evb[data-ev="RI-TEC-036|eu_requirement"]'); evb.click();
const dr = d.getElementById('drawer'), body = d.getElementById('dr-body');
const n = EV.issues['RI-TEC-036'].s.eu_requirement.length;
t('drawer opens for the step', !dr.hidden && body.querySelectorAll('.evw').length === n);
t('at most five visible before Show all', body.querySelectorAll('.evw:not(.hidden)').length === Math.min(5, n));
if (n > 5) { d.getElementById('dr-all').click(); t('show all', body.querySelectorAll('.evw:not(.hidden)').length === n); }
t('three separate labels per item', [...body.querySelectorAll('.evi')].every(e => e.querySelectorAll('.r3 .bd').length === 3 &&
  /Source quality/.test(e.textContent) && /Evidence confidence/.test(e.textContent) && /Relevance/.test(e.textContent)));
const id0 = body.querySelector('.evi .rid').textContent.split(' ')[0];
t('quote matches the recorded text exactly', body.querySelector('.evi .q p').textContent === '“' + EV.items[id0][0] + '”');
d.getElementById('dr-close').click(); t('drawer closes', dr.hidden);
const withC = Object.keys(EV.issues).find(x => EV.issues[x].c.length);
t('validated conflicts exist in the data', !!withC);
if (withC) {
  const c0 = EV.issues[withC].c[0]; const step = Object.keys(EV.issues[withC].s).find(s => EV.issues[withC].s[s].some(r => r[0] === c0[0] || r[0] === c0[1]));
  d.querySelector(`.evb[data-ev="${withC}|${step}"]`).click(); t('conflicting evidence block shown with both sides', body.querySelector('.conflict') && body.querySelectorAll('.conflict .evi').length >= 2);
}
// Labels and integrity
const chips = [...d.querySelectorAll('.sc')].map(s => s.textContent);
t('only the five content labels as status chips', chips.every(c => ['Validated', 'Pending review', 'Proposed', 'Draft', 'Not started'].includes(c)));
t('options labelled internal draft (section)', [...d.querySelectorAll('#options .option')].every(o => /Internal draft/.test(o.textContent)) && d.querySelectorAll('#options .option').length === 10);
t('cases (section) = 9', d.querySelectorAll('#comparators .case').length === 9);
const dvals = new Set([...d.querySelectorAll('.bd[data-type="direction_of_travel"] b')].map(b => b.textContent));
t('direction labels from the stored scale only', [...dvals].every(v => ['New', 'Worsening', 'Persistent', 'Improving', 'Largely resolved', 'Insufficient evidence'].includes(v)));
t('insufficient evidence shown as its own value', [...d.querySelectorAll('.bd.t-ie')].every(b => /Insufficient evidence/.test(b.textContent)) && d.querySelectorAll('.bd.t-ie').length > 0);
// Recorded limit descriptions are shown as written; everything else must name no file
d.querySelectorAll('#evidence details.refs').forEach(e => e.remove());
t('no file names in visible text', !/\.(csv|json)\b/.test(d.body.textContent.replace(d.getElementById('ev').textContent, '')));
console.log(`${ok} passed, ${bad} failed`);
process.exit(bad ? 1 : 0);
