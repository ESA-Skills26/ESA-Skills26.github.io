(() => {
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- Language (same behaviour as before: EN default, remembered) ---------- */
  const langBtns = $$('[data-lang]');
  function lang(l) {
    root.lang = l; root.dir = l === 'ar' ? 'rtl' : 'ltr';
    $$('[data-en][data-ar]').forEach(e => { e.innerHTML = e.dataset[l]; });
    langBtns.forEach(b => b.classList.toggle('on', b.dataset.lang === l));
    try { localStorage.setItem('esaLang', l); } catch (e) {}
    requestAnimationFrame(moveInk);
    if (window.__reverify) window.__reverify();
  }
  langBtns.forEach(b => b.addEventListener('click', () => lang(b.dataset.lang)));
  let saved = 'en'; try { saved = localStorage.getItem('esaLang') || 'en'; } catch (e) {}
  lang(saved);

  /* ---------- Registration → WhatsApp (unchanged message and number) ---------- */
  const form = $('#leadForm');
  form.addEventListener('submit', e => {
    e.preventDefault();
    const fields = ['name', 'phone', 'email', 'course'].map(id => $('#' + id));
    let firstBad = null;
    fields.forEach(f => {
      const ok = f.checkValidity() && (!f.required || f.value.trim() !== '');
      f.closest('.field').classList.toggle('invalid', !ok);
      if (!ok && !firstBad) firstBad = f;
    });
    if (firstBad) { firstBad.focus(); return; }
    const n = $('#name').value.trim(), p = $('#phone').value.trim(), em = $('#email').value.trim(), c = $('#course').value, l = root.lang;
    const msg = l === 'ar'
      ? ('مرحبًا ESA Academy\nالاسم: ' + n + '\nرقم الهاتف: ' + p + '\n' + (em ? 'البريد الإلكتروني: ' + em + '\n' : '') + 'البرنامج: ' + c)
      : ('Hello ESA Academy\nName: ' + n + '\nPhone: ' + p + '\n' + (em ? 'Email: ' + em + '\n' : '') + 'Program: ' + c);
    const url = 'https://wa.me/201032226160?text=' + encodeURIComponent(msg);
    const btn = $('.submit', form); btn.classList.add('sent');
    setTimeout(() => { location.href = url; }, reduce ? 0 : 450);
  });
  $$('.field input, .field select', form).forEach(f => f.addEventListener('input', () => f.closest('.field').classList.remove('invalid')));
  addEventListener('pageshow', () => $('.submit', form).classList.remove('sent'));

  /* ---------- Program details modal ---------- */
  const modal = $('#courseModal'), hero = $('#modalHero');
  const fill = (id, arr) => { $('#' + id).innerHTML = arr.map(x => '<li>' + x + '</li>').join(''); };
  let lastFocus = null;
  function openCourse(title) {
    const d = courseInfo[title]; if (!d) return;
    const ar = root.lang === 'ar', i = ar ? 1 : 0;
    $('#modalTitle').textContent = ar ? d.ar : title;
    $('#modalIntro').textContent = d.intro[i];
    hero.style.backgroundImage = "url('" + d.img + "')";
    fill('modalLearn', d.learn[i]); fill('modalBenefits', d.benefit[i]); fill('modalCareer', d.career[i]); fill('modalMarket', d.market[i]);
    $('#learnHead').textContent = ar ? 'ماذا ستتعلم' : 'WHAT YOU’LL LEARN';
    $('#benefitHead').textContent = ar ? 'ما الاستفادة' : 'WHY IT MATTERS';
    $('#careerHead').textContent = ar ? 'كيف يؤهلك لسوق العمل' : 'CAREER READINESS';
    $('#marketHead').textContent = ar ? 'لماذا يحتاج السوق لهذه المهارة' : 'WHY THE MARKET NEEDS IT';
    $('#modalRegister').textContent = ar ? 'احجز مقعدك ←' : 'Reserve Your Seat →';
    lastFocus = document.activeElement;
    modal.classList.add('open'); modal.setAttribute('aria-hidden', 'false'); document.body.style.overflow = 'hidden';
    setTimeout(() => $('.modal-close').focus(), 50);
  }
  function closeModal() {
    if (!modal.classList.contains('open')) return;
    modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); document.body.style.overflow = '';
    lastFocus?.focus?.({ preventScroll: true });
  }
  $$('.course').forEach(el => {
    const go = () => openCourse($('h3', el).dataset.en);
    el.addEventListener('click', go);
    el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
  });
  $('.modal-close').onclick = closeModal; $('.modal-backdrop').onclick = closeModal;
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
  $('#modalRegister').addEventListener('click', () => { modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; });

  /* ---------- Certificate verification ----------
     certificates.json holds one encrypted record per certificate.
     A record is found and opened only with the exact ID, so the file
     does not expose the list of trainees or IDs. */
  const vForm = $('#verifyForm'), vOut = $('#verifyResult'), vInput = $('#certId');
  let certDB = null;
  const enc = new TextEncoder();
  const normId = v => v.normalize('NFKC').replace(/[٠-٩]/g, d => d.charCodeAt(0) - 0x660).replace(/[۰-۹]/g, d => d.charCodeAt(0) - 0x6F0).replace(/\s+/g, '').toUpperCase();
  const sha = async s => new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(s)));
  const hex = b => [...b].map(x => x.toString(16).padStart(2, '0')).join('');
  const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  async function loadDB() {
    if (certDB) return certDB;
    const r = await fetch('certificates.json', { cache: 'no-cache' });
    if (!r.ok) throw new Error('db');
    return (certDB = await r.json());
  }
  async function lookup(id) {
    const db = await loadDB();
    const key = hex(await sha('esa-idx|' + db.salt + '|' + id));
    const rec = db.records && db.records[key];
    if (!rec) return null;
    const raw = b64(rec), iv = raw.slice(0, 12), data = raw.slice(12);
    const k = await crypto.subtle.importKey('raw', await sha('esa-key|' + db.salt + '|' + id), 'AES-GCM', false, ['decrypt']);
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, k, data);
    return JSON.parse(new TextDecoder().decode(plain));
  }
  function show(state, html) { vOut.innerHTML = html ? `<div class="vr vr-${state}">${html}</div>` : ''; }
  async function verify(raw) {
    const ar = root.lang === 'ar', id = normId(raw || '');
    const field = vInput.closest('.field');
    if (!id) { field.classList.add('invalid'); vInput.focus(); return; }
    field.classList.remove('invalid');
    show('wait', `<span class="spinner"></span><p>${ar ? 'جارٍ التحقق…' : 'Checking…'}</p>`);
    let rec = null, failed = false;
    try { rec = await lookup(id); } catch (e) { failed = true; }
    await new Promise(r => setTimeout(r, reduce ? 0 : 450));
    if (failed) { show('bad', `<span class="vr-ico"><svg class="ico"><use href="#i-alert"/></svg></span><div><h4>${ar ? 'تعذّر التحقق الآن' : 'Verification is unavailable right now'}</h4><p>${ar ? 'تأكد من اتصالك بالإنترنت وحاول مرة أخرى.' : 'Check your connection and try again.'}</p></div>`); return; }
    if (!rec) { show('bad', `<span class="vr-ico"><svg class="ico"><use href="#i-alert"/></svg></span><div><h4>${ar ? 'لم نجد شهادة بهذا الرقم' : 'No certificate found for this ID'}</h4><p>${ar ? 'راجع الرقم كما هو مكتوب على الشهادة، أو تواصل معنا على 01032226160.' : 'Check the ID exactly as printed on the certificate, or contact us on 01032226160.'}</p></div>`); return; }
    const courseAr = rec.course_ar || (courseInfo[rec.course] && courseInfo[rec.course].ar) || rec.course;
    const rows = [
      [ar ? 'رقم الشهادة' : 'Certificate ID', `<span dir="ltr">${esc(id)}</span>`],
      rec.name ? [ar ? 'اسم المتدرب' : 'Trainee', esc(rec.name)] : null,
      [ar ? 'البرنامج' : 'Program', esc(ar ? courseAr : rec.course)],
      rec.date ? [ar ? 'تاريخ الإصدار' : 'Issued', `<span dir="ltr">${esc(rec.date)}</span>`] : null
    ].filter(Boolean).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
    show('ok', `<span class="vr-ico"><svg class="ico"><use href="#i-check"/></svg></span><div><h4>${ar ? 'رقم صحيح — الشهادة معتمدة' : 'Valid ID — Certificate verified'}</h4><p>${ar ? 'اجتاز المتدرب البرنامج التالي بنجاح في ESA Academy.' : 'This trainee successfully completed the following ESA Academy program.'}</p><dl>${rows}</dl></div>`);
  }
  window.__reverify = () => { if (vOut.innerHTML && vInput.value.trim()) verify(vInput.value); };
  vForm.addEventListener('submit', e => { e.preventDefault(); verify(vInput.value); });
  vInput.addEventListener('input', () => vInput.closest('.field').classList.remove('invalid'));
  // Links such as https://esa-skills26.github.io/?verify=ESA-0001 (for a QR code on the certificate)
  const qv = new URLSearchParams(location.search).get('verify');
  if (qv) { vInput.value = qv; setTimeout(() => { $('#verify').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); verify(qv); }, 600); }

  /* ---------- Header, nav indicator, progress ---------- */
  const header = $('#siteHeader'), bar = $('#progress');
  const navLinks = $$('.links a'), ink = $('.nav-ink');
  const sections = navLinks.map(a => a.getAttribute('href') === '#top' ? $('.hero') : $(a.getAttribute('href')));
  let active = null;
  function moveInk() {
    if (!ink) return;
    const a = active || navLinks[0];
    if (!a || !a.offsetParent) return;
    const r = a.getBoundingClientRect(), pr = a.parentElement.getBoundingClientRect();
    ink.style.width = (r.width - 28) + 'px';
    ink.style.transform = `translateX(${r.left - pr.left + 14}px)`;
    ink.style.opacity = 1;
  }
  function onScroll() {
    const y = scrollY, h = document.documentElement.scrollHeight - innerHeight;
    header.classList.toggle('scrolled', y > 20);
    bar.style.transform = `scaleX(${h > 0 ? y / h : 0})`;
    let cur = navLinks[0];
    sections.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * .4) cur = navLinks[i]; });
    if (cur !== active) { navLinks.forEach(a => a.classList.toggle('active', a === cur)); active = cur; moveInk(); }
    if (!reduce) parallax(y);
  }
  const heroArt = $('.hero-art'), regBg = $('.register-bg'), regSec = $('#register');
  function parallax(y) {
    if (innerWidth > 850 && y < innerHeight * 1.2) heroArt.style.translate = `0 ${y * .18}px`;
    if (regSec) { const r = regSec.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) regBg.style.translate = `0 ${(r.top - innerHeight / 2) * -.08}px`; }
  }
  addEventListener('scroll', () => requestAnimationFrame(onScroll), { passive: true });
  addEventListener('resize', moveInk);
  onScroll();
  document.fonts?.ready.then(moveInk);

  if (reduce) { document.body.classList.add('loaded'); return; }

  /* ---------- Entrance ---------- */
  const heroImg = new Image(); heroImg.src = 'hero-eagle.webp';
  const start = () => requestAnimationFrame(() => document.body.classList.add('loaded'));
  if (heroImg.complete) start(); else { heroImg.onload = heroImg.onerror = start; setTimeout(start, 1500); }
  $$('.hero .reveal-up').forEach((el, i) => { el.style.transitionDelay = (.25 + i * .12) + 's'; setTimeout(() => el.classList.add('in'), 60); });

  /* Count-up for the program number */
  $$('.count').forEach(el => {
    const to = +el.dataset.to; const t0 = performance.now() + 700;
    const tick = now => { const p = Math.min(1, Math.max(0, (now - t0) / 1100)); el.textContent = Math.round(to * (1 - Math.pow(1 - p, 3))); if (p < 1) requestAnimationFrame(tick); };
    el.textContent = '0'; requestAnimationFrame(tick);
  });

  /* ---------- Scroll reveals (staggered per group) ---------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, sibs = [...el.parentElement.children].filter(c => c.matches('.reveal-up, .course'));
      const idx = Math.max(0, sibs.indexOf(el));
      el.style.transitionDelay = (idx % 4) * .09 + 's';
      el.classList.add('in'); io.unobserve(el);
      setTimeout(() => { el.style.transitionDelay = ''; }, 1600);
    });
  }, { threshold: .14, rootMargin: '0px 0px -6% 0px' });
  $$('.reveal-up:not(.hero .reveal-up), .course').forEach(el => io.observe(el));

  /* ---------- Card spotlight + 3D tilt (pointer devices) ---------- */
  if (fine) {
    $$('.course, .about-card').forEach(card => {
      const max = card.classList.contains('course') ? 6 : 8;
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.setProperty('--mx', x * 100 + '%'); card.style.setProperty('--my', y * 100 + '%');
        card.style.transform = `perspective(900px) rotateX(${(.5 - y) * max}deg) rotateY(${(x - .5) * max}deg) translateY(-6px)`;
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
    /* Magnetic primary button */
    $$('.magnetic').forEach(b => {
      b.addEventListener('pointermove', e => { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .18}px, ${(e.clientY - r.top - r.height / 2) * .3}px)`; });
      b.addEventListener('pointerleave', () => { b.style.transform = ''; });
    });
  }
})();
