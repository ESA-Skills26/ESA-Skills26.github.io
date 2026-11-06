(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  const CFG = window.ESA_PASSPORT || {};
  const API = (CFG.API_URL || '').trim();
  const WA = CFG.WHATSAPP || '201032226160';
  const params = new URLSearchParams(location.search);
  const DEMO = params.has('demo');
  const ar = () => root.lang === 'ar';
  const t = (en, a) => (ar() ? a : en);
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const icon = n => `<svg class="ico"><use href="#i-${n}"/></svg>`;

  /* ---------- language (shared with the main site) ---------- */
  const langBtns = $$('[data-lang]');
  let rerender = [];
  function lang(l) {
    root.lang = l; root.dir = l === 'ar' ? 'rtl' : 'ltr';
    $$('[data-en][data-ar]').forEach(e => { e.innerHTML = e.dataset[l]; });
    langBtns.forEach(b => b.classList.toggle('on', b.dataset.lang === l));
    try { localStorage.setItem('esaLang', l); } catch (e) {}
    rerender.forEach(f => f());
  }
  langBtns.forEach(b => b.addEventListener('click', () => lang(b.dataset.lang)));
  let saved = 'en'; try { saved = localStorage.getItem('esaLang') || 'en'; } catch (e) {}

  const wa = msg => 'https://wa.me/' + WA + '?text=' + encodeURIComponent(msg);
  const setWa = () => { $('#ppWa').href = wa(t('Hello ESA Academy, I have a question about ESA Passport.', 'مرحبًا ESA Academy، عندي استفسار عن ESA Passport.')); };
  rerender.push(setWa);

  /* ---------- data access (Google Sheet via Apps Script) ---------- */
  const normId = v => String(v || '').normalize('NFKC')
    .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
    .replace(/\s+/g, '').toUpperCase();

  const SAMPLE = {
    graduate: { ok: true, demo: true, graduate: { id: 'ESA-G26-DEMO1', name_ar: 'اسم الخريج (مثال)', name_en: 'Graduate Name (sample)', tier: 'Graduate', status: 'active', joined: '2026-11-01' },
      certificates: [{ id: 'ESA-CS-0001', program: 'Cybersecurity', date: '2026-10-28', status: 'valid' }] },
    offers: { ok: true, demo: true, items: [{ title_en: 'Sample offer — appears once agreed', title_ar: 'عرض تجريبي — بيظهر بعد الاتفاق', details_en: 'Offers you add to the Offers tab of the sheet show here.', details_ar: 'العروض اللي تضيفها في تبويب Offers في الشيت بتظهر هنا.', partner: 'ESA', valid_until: '2026-12-31', tier: 'Graduate' }] },
    events: { ok: true, demo: true, items: [{ title_en: 'Sample event', title_ar: 'فعالية تجريبية', date: '2026-12-10', place_en: 'Online', place_ar: 'أونلاين', link: '' }] }
  };

  async function api(action, extra = {}) {
    if (!API) return DEMO ? SAMPLE[action] : null;
    const u = new URL(API);
    u.searchParams.set('action', action);
    Object.entries(extra).forEach(([k, v]) => u.searchParams.set(k, v));
    const r = await fetch(u.toString(), { redirect: 'follow' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  /* ---------- card lookup ---------- */
  const out = $('#ppResult'), input = $('#ppId');
  const TIERS = { graduate: ['#4FBF8B', 'badge'], achiever: ['#5B9BE6', 'star'], ambassador: ['#F3AE12', 'crown'] };
  let last = null, lastId = '';
  const fmtDate = d => {
    if (!d) return '—';
    const x = new Date(d); if (isNaN(x)) return esc(d);
    return x.toLocaleDateString(ar() ? 'ar-EG' : 'en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
  };
  const msg = (kind, ic, h, p) => { out.innerHTML = `<div class="pp-msg ${kind}">${icon(ic)}<div><h4>${h}</h4><p>${p}</p></div></div>`; };

  function render() {
    if (!last) return;
    const d = last;
    if (d === 'off') return msg('', 'lock', t('Card lookup opens soon', 'عرض البطاقات هيتفعّل قريب'), t('ESA Passport is being activated. You will receive your Graduate ID in your activation message.', 'جاري تفعيل ESA Passport، وهيوصلك رقم الخريج في رسالة التفعيل.'));
    if (d === 'err') return msg('bad', 'alert', t('We could not reach the service', 'تعذّر الاتصال بالخدمة'), t('Please try again in a moment.', 'جرّب تاني بعد شوية.'));
    if (!d.ok || !d.graduate) return msg('bad', 'alert', t('No graduate found with this ID', 'مفيش خريج بالرقم ده'), t('Check the ID exactly as it appears in your activation message, or contact us on WhatsApp.', 'راجع الرقم زي ما هو مكتوب في رسالة التفعيل، أو كلمنا على واتساب.'));
    const g = d.graduate;
    const active = String(g.status || 'active').toLowerCase() === 'active';
    const tk = String(g.tier || 'Graduate').toLowerCase();
    const [tc, ti] = TIERS[tk] || TIERS.graduate;
    const name = ar() ? (g.name_ar || g.name_en) : (g.name_en || g.name_ar);
    const sub = ar() ? g.name_en : g.name_ar;
    const link = location.origin + location.pathname + '?id=' + encodeURIComponent(g.id);
    const certs = (d.certificates || []);
    const certHtml = certs.length ? certs.map(c => `<li><span class="ci">${icon('file')}</span><div><b>${esc(c.program)}</b><small><span class="mono">${esc(c.id)}</span> · ${fmtDate(c.date)}${String(c.status || 'valid').toLowerCase() !== 'valid' ? ' · ' + t('not valid', 'غير سارية') : ''}</small></div><a href="../?verify=${encodeURIComponent(c.id)}#verify">${t('Verify ↗', 'تحقق ↗')}</a></li>`).join('')
      : `<li><span class="ci">${icon('file')}</span><div><b>${t('No certificates listed yet', 'لا توجد شهادات مسجلة بعد')}</b></div></li>`;
    out.innerHTML = `${d.demo ? `<span class="pp-demo">${t('Sample card — preview only', 'بطاقة تجريبية للعرض فقط')}</span>` : ''}
    <div class="pp-out">
      <div>
        <div class="pp-card" id="ppCard">
          <div class="pp-card-top"><span class="en-lbl">GRADUATE ID</span><img src="esa-logo.webp" alt="ESA" class="pp-card-logo"></div>
          <div class="pp-card-body"><div class="pp-qr" id="ppQr"></div>
            <div class="pp-card-meta"><p class="pp-name" dir="auto">${esc(name)}${sub ? `<small dir="auto">${esc(sub)}</small>` : ''}</p><small>MEMBER NO.</small><strong class="mono">${esc(g.id)}</strong></div></div>
          <div class="pp-card-foot"><span class="pp-tier" style="--tc:${tc}">${icon(ti)}${esc(String(g.tier || 'Graduate').toUpperCase())}</span><span class="pp-status ${active ? '' : 'off'}">${active ? 'ACTIVE' : 'INACTIVE'}</span></div>
        </div>
        <div class="pp-actions">
          <button class="btn btn-gold" id="ppCopy">${icon('link')}<span>${t('Copy card link', 'انسخ رابط البطاقة')}</span></button>
          <button class="btn btn-ghost" id="ppPrint">${icon('print')}<span>${t('Save / print', 'حفظ / طباعة')}</span></button>
          <a class="btn btn-ghost" target="_blank" rel="noopener" href="${wa(t('Hello ESA Academy, I need a correction on my ESA Passport. Graduate ID: ', 'مرحبًا ESA Academy، محتاج تصحيح في بيانات ESA Passport. رقم الخريج: ') + g.id)}">${icon('whatsapp')}<span>${t('Request a correction', 'طلب تصحيح')}</span></a>
        </div>
      </div>
      <div class="pp-panel">
        <h3>${icon('badge')}${active ? t('Verified ESA graduate', 'خريج ESA موثّق') : t('Membership not active', 'العضوية غير مفعّلة')}</h3>
        <div class="pp-meta">
          <div><small>${t('Tier', 'المستوى')}</small><b style="color:${tc}">${esc(g.tier || 'Graduate')}</b></div>
          <div><small>${t('Member since', 'عضو منذ')}</small><b>${fmtDate(g.joined)}</b></div>
          <div><small>${t('Certificates', 'الشهادات')}</small><b>${certs.length}</b></div>
        </div>
        <h3 style="margin-top:22px">${icon('file')}${t('ESA certificates', 'شهادات ESA')}</h3>
        <ul class="pp-certs">${certHtml}</ul>
      </div>
    </div>`;
    const q = $('#ppQr');
    if (window.QRCode) { try { new QRCode(q, { text: link, width: 160, height: 160, colorDark: '#000', colorLight: '#f6f5f2', correctLevel: QRCode.CorrectLevel.M }); } catch (e) { q.classList.add('pp-qr-fake'); } }
    else q.classList.add('pp-qr-fake');
    $('#ppCopy').onclick = async e => {
      try { await navigator.clipboard.writeText(link); } catch (_) { prompt('Link', link); }
      e.currentTarget.querySelector('span').textContent = t('Copied ✓', 'تم النسخ ✓');
    };
    $('#ppPrint').onclick = () => { const c = $('#ppCard'); c.classList.add('pp-print'); window.print(); setTimeout(() => c.classList.remove('pp-print'), 500); };
  }
  rerender.push(render);

  async function lookup(raw) {
    const id = normId(raw);
    if (!id) { input.focus(); return; }
    lastId = id;
    if (!API && !DEMO) { last = 'off'; render(); return; }
    out.innerHTML = `<p class="pp-loading">${t('Checking…', 'جاري البحث…')}</p>`;
    try { last = await api('graduate', { id }); } catch (e) { last = 'err'; }
    if (lastId !== id) return;
    render();
    const u = new URL(location.href); u.searchParams.set('id', id); history.replaceState(null, '', u);
  }
  $('#ppForm').addEventListener('submit', e => { e.preventDefault(); lookup(input.value); });

  /* ---------- offers & events ---------- */
  let offers = null, events = null;
  function renderLists() {
    const pick = (o, k) => (ar() ? (o[k + '_ar'] || o[k + '_en']) : (o[k + '_en'] || o[k + '_ar'])) || '';
    const empty = (en, a) => `<div class="pp-empty">${t(en, a)}</div>`;
    $('#ppOffers').innerHTML = offers && offers.length ? offers.map(o => `<article class="pp-item"><h4>${esc(pick(o, 'title'))}</h4>${pick(o, 'details') ? `<p>${esc(pick(o, 'details'))}</p>` : ''}${pick(o, 'how') ? `<p>${esc(pick(o, 'how'))}</p>` : ''}<div class="row">${o.partner ? `<span class="pp-chip y">${esc(o.partner)}</span>` : ''}${o.tier ? `<span class="pp-chip">${icon('badge')}${esc(o.tier)}+</span>` : ''}${o.valid_until ? `<span class="pp-chip">${icon('cal')}${t('Valid until', 'صالح حتى')} ${fmtDate(o.valid_until)}</span>` : ''}</div></article>`).join('')
      : empty('No offers are published yet. Approved offers will appear here with their conditions.', 'مفيش عروض منشورة لسه. العروض المعتمدة هتظهر هنا بشروطها.');
    $('#ppEvents').innerHTML = events && events.length ? events.map(o => `<article class="pp-item"><h4>${esc(pick(o, 'title'))}</h4><div class="row"><span class="pp-chip y">${icon('cal')}${fmtDate(o.date)}</span>${pick(o, 'place') ? `<span class="pp-chip">${icon('pin')}${esc(pick(o, 'place'))}</span>` : ''}${o.link ? `<a class="pp-chip" href="${esc(o.link)}" target="_blank" rel="noopener">${icon('link')}${t('Details', 'التفاصيل')}</a>` : ''}</div></article>`).join('')
      : empty('No upcoming events right now. Check back soon.', 'مفيش فعاليات قادمة حاليًا. تابعنا قريب.');
  }
  rerender.push(renderLists);
  async function loadLists() {
    try { const o = await api('offers'); offers = o && o.ok ? o.items : []; } catch (e) { offers = []; }
    try { const v = await api('events'); events = v && v.ok ? v.items : []; } catch (e) { events = []; }
    renderLists();
  }

  lang(saved);
  renderLists();
  loadLists();
  const qid = params.get('id');
  if (qid) { input.value = qid; const go = () => { lookup(qid); $('#card').scrollIntoView({ behavior: 'instant', block: 'start' }); }; window.QRCode ? go() : addEventListener('load', go); }
})();
