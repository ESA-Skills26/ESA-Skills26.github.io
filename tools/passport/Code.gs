/**
 * ESA Passport — Google Sheets back end (Google Apps Script web app)
 *
 * Paste this file into Extensions → Apps Script of the ESA Passport sheet,
 * run setup() once, then Deploy → New deployment → Web app
 * (Execute as: Me · Who has access: Anyone) and put the /exec URL in
 * passport/config.js → API_URL.
 *
 * What the website can read (and nothing else):
 *   ?action=graduate&id=ESA-G26-XXXXX → name, tier, status, joined date and that graduate's certificates
 *   ?action=offers                     → active, unexpired offers
 *   ?action=events                     → active, upcoming events
 * Phone, email, consent and notes columns are never sent to the website.
 */

const TABS = {
  Graduates: ['graduate_id', 'name_ar', 'name_en', 'tier', 'status', 'joined_date', 'phone', 'email', 'marketing_consent', 'notes'],
  Certificates: ['certificate_id', 'graduate_id', 'program', 'issue_date', 'status'],
  Offers: ['active', 'title_ar', 'title_en', 'details_ar', 'details_en', 'how_ar', 'how_en', 'partner', 'tier', 'valid_until'],
  Events: ['active', 'title_ar', 'title_en', 'date', 'place_ar', 'place_en', 'link']
};
const TIER_ORDER = ['graduate', 'achiever', 'ambassador'];

/* ---------------- web app ---------------- */
function doGet(e) {
  const p = (e && e.parameter) || {};
  let out;
  try {
    if (p.action === 'graduate') out = getGraduate_(p.id);
    else if (p.action === 'offers') out = cached_('offers', getOffers_);
    else if (p.action === 'events') out = cached_('events', getEvents_);
    else out = { ok: false, error: 'unknown action' };
  } catch (err) {
    out = { ok: false, error: 'server' };
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}

function getGraduate_(rawId) {
  const id = normId_(rawId);
  if (!/^[A-Z0-9-]{4,40}$/.test(id)) return { ok: false };
  const g = rows_('Graduates').find(r => normId_(r.graduate_id) === id);
  if (!g) return { ok: false };
  const status = String(g.status || 'active').trim().toLowerCase();
  const graduate = { id: id, name_ar: str_(g.name_ar), name_en: str_(g.name_en), tier: tierName_(g.tier), status: status, joined: date_(g.joined_date) };
  if (status !== 'active') return { ok: true, graduate: { id: id, status: status, tier: graduate.tier, name_ar: graduate.name_ar, name_en: graduate.name_en }, certificates: [] };
  const certificates = rows_('Certificates')
    .filter(c => normId_(c.graduate_id) === id && str_(c.certificate_id))
    .map(c => ({ id: normId_(c.certificate_id), program: str_(c.program), date: date_(c.issue_date), status: str_(c.status || 'valid').toLowerCase() }));
  return { ok: true, graduate: graduate, certificates: certificates };
}

function getOffers_() {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const items = rows_('Offers').filter(r => isYes_(r.active) && (!r.valid_until || new Date(r.valid_until) >= today)).map(r => ({
    title_ar: str_(r.title_ar), title_en: str_(r.title_en), details_ar: str_(r.details_ar), details_en: str_(r.details_en),
    how_ar: str_(r.how_ar), how_en: str_(r.how_en), partner: str_(r.partner), tier: r.tier ? tierName_(r.tier) : '', valid_until: date_(r.valid_until)
  }));
  return { ok: true, items: items };
}

function getEvents_() {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const items = rows_('Events').filter(r => isYes_(r.active) && r.date && new Date(r.date) >= today)
    .sort((a, b) => new Date(a.date) - new Date(b.date)).map(r => ({
      title_ar: str_(r.title_ar), title_en: str_(r.title_en), date: date_(r.date), place_ar: str_(r.place_ar), place_en: str_(r.place_en), link: /^https?:\/\//.test(str_(r.link)) ? str_(r.link) : ''
    }));
  return { ok: true, items: items };
}

/* ---------------- sheet menu & helpers for the team ---------------- */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('ESA Passport')
    .addItem('Create / check tabs', 'setup')
    .addItem('Generate missing Graduate IDs', 'generateIds')
    .addItem('Copy card link for selected row', 'cardLink')
    .addToUi();
}

/** Creates the four tabs with their headers (safe to run again). */
function setup() {
  const ss = SpreadsheetApp.getActive();
  Object.keys(TABS).forEach(name => {
    const sh = ss.getSheetByName(name) || ss.insertSheet(name);
    const head = TABS[name];
    if (sh.getLastRow() === 0) sh.getRange(1, 1, 1, head.length).setValues([head]);
    sh.getRange(1, 1, 1, head.length).setFontWeight('bold').setBackground('#F3AE12').setFontColor('#000000');
    sh.setFrozenRows(1);
  });
  const g = ss.getSheetByName('Graduates');
  const rule = list => SpreadsheetApp.newDataValidation().requireValueInList(list, true).build();
  g.getRange('D2:D').setDataValidation(rule(['Graduate', 'Achiever', 'Ambassador']));
  g.getRange('E2:E').setDataValidation(rule(['active', 'suspended']));
  ss.getSheetByName('Certificates').getRange('E2:E').setDataValidation(rule(['valid', 'revoked']));
  ['Offers', 'Events'].forEach(n => ss.getSheetByName(n).getRange('A2:A').setDataValidation(rule(['yes', 'no'])));
}

/** Fills empty graduate_id cells with random, non-guessable IDs such as ESA-G26-7KQ4M. */
function generateIds() {
  const sh = SpreadsheetApp.getActive().getSheetByName('Graduates');
  const n = sh.getLastRow() - 1; if (n < 1) return;
  const data = sh.getRange(2, 1, n, 3).getValues();
  const used = new Set(data.map(r => normId_(r[0])).filter(String));
  const yy = String(new Date().getFullYear()).slice(-2);
  const ABC = '23456789ABCDEFGHJKMNPQRSTUVWXYZ';
  let made = 0;
  data.forEach((r, i) => {
    if (r[0] || !(r[1] || r[2])) return;
    let id;
    do { id = 'ESA-G' + yy + '-' + Array.from({ length: 5 }, () => ABC[Math.floor(Math.random() * ABC.length)]).join(''); } while (used.has(id));
    used.add(id); sh.getRange(i + 2, 1).setValue(id); made++;
  });
  SpreadsheetApp.getUi().alert(made + ' Graduate ID(s) created.');
}

/** Shows the public card link for the selected graduate row (for the activation message). */
function cardLink() {
  const sh = SpreadsheetApp.getActiveSheet();
  const id = normId_(sh.getRange(sh.getActiveRange().getRow(), 1).getValue());
  SpreadsheetApp.getUi().alert(id ? 'https://esa-skills26.github.io/passport/?id=' + id : 'Select a row in the Graduates tab first.');
}

/* ---------------- internals ---------------- */
function rows_(name) {
  const sh = SpreadsheetApp.getActive().getSheetByName(name);
  if (!sh || sh.getLastRow() < 2) return [];
  const v = sh.getDataRange().getValues();
  const head = v.shift().map(h => String(h).trim().toLowerCase());
  return v.filter(r => r.some(c => c !== '')).map(r => Object.fromEntries(head.map((h, i) => [h, r[i]])));
}
function cached_(key, fn) {
  const c = CacheService.getScriptCache(), hit = c.get(key);
  if (hit) return JSON.parse(hit);
  const val = fn(); c.put(key, JSON.stringify(val), 300); return val;
}
function normId_(v) {
  return String(v == null ? '' : v).normalize('NFKC')
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/\s+/g, '').toUpperCase();
}
function str_(v) { return v == null ? '' : String(v).trim(); }
function isYes_(v) { return ['yes', 'y', 'true', '1', 'نعم', 'active'].indexOf(str_(v).toLowerCase()) > -1 || v === true; }
function date_(v) {
  if (!v) return '';
  if (Object.prototype.toString.call(v) === '[object Date]') return Utilities.formatDate(v, 'Africa/Cairo', 'yyyy-MM-dd');
  return str_(v);
}
function tierName_(v) {
  const k = str_(v).toLowerCase();
  return TIER_ORDER.indexOf(k) > -1 ? k.charAt(0).toUpperCase() + k.slice(1) : 'Graduate';
}
