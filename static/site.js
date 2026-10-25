/* NetworkedAsociados — interacciones compartidas */
(function () {
  var root = document.documentElement;
  var base = root.getAttribute('data-base') || './';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* menú móvil */
  var mb = document.querySelector('.nx-menu'), dr = document.querySelector('.nx-drawer');
  if (mb && dr) mb.addEventListener('click', function () {
    var o = dr.classList.toggle('open'); mb.setAttribute('aria-expanded', o);
    document.body.style.overflow = o ? 'hidden' : '';
  });

  /* búsqueda global */
  var sv = document.getElementById('nx-search'), si = document.getElementById('nx-q'), sl = document.getElementById('nx-res');
  var idx = null, sel = -1;
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function openS() {
    if (!sv) return; sv.hidden = false; si.value = ''; render(''); setTimeout(function () { si.focus(); }, 20);
    if (!idx) fetch(base + 'search.json').then(function (r) { return r.json(); }).then(function (d) { idx = d; render(si.value); })
      .catch(function () { sl.innerHTML = '<li class="empty">No pude cargar el buscador. Recarga la página e inténtalo de nuevo.</li>'; });
  }
  function closeS() { if (sv) sv.hidden = true; }
  function render(q) {
    if (!sl) return;
    if (!idx) { sl.innerHTML = '<li class="empty">Cargando…</li>'; return; }
    var n = norm(q).trim(), words = n.split(/\s+/).filter(Boolean);
    var res = idx.filter(function (x) { var h = norm(x.t + ' ' + x.k + ' ' + x.d); return words.every(function (w) { return h.indexOf(w) > -1; }); }).slice(0, 12);
    if (!n) res = idx.filter(function (x) { return x.f; });
    sel = -1;
    sl.innerHTML = res.length ? res.map(function (x) {
      return '<li><a href="' + base + x.u + '"><span>' + x.t + '</span><small>' + x.s + ' · ' + x.d + '</small></a></li>';
    }).join('') : '<li class="empty">No encontré resultados para "' + q.replace(/[<>&"]/g, '') + '". Prueba con el nombre de la empresa o pídeme el análisis.</li>';
  }
  document.querySelectorAll('[data-search]').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); openS(); }); });
  if (si) {
    si.addEventListener('input', function () { render(si.value); });
    si.addEventListener('keydown', function (e) {
      var a = sl.querySelectorAll('a'); if (!a.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + a.length) % a.length;
        a.forEach(function (x, i) { x.classList.toggle('sel', i === sel); });
      } else if (e.key === 'Enter') { (a[sel] || a[0]).click(); }
    });
  }
  if (sv) sv.addEventListener('click', function (e) { if (e.target === sv) closeS(); });
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openS(); }
    if (e.key === 'Escape') closeS();
  });

  /* revelado al desplazarse: solo lo que está fuera de pantalla al cargar, con respaldo */
  if (!reduce) {
    var wait = [];
    document.querySelectorAll('.rv').forEach(function (el) {
      if (el.getBoundingClientRect().top > innerHeight) { el.classList.add('rv-wait'); wait.push(el); }
    });
    var tick = false;
    function check() {
      tick = false;
      wait = wait.filter(function (el) {
        if (el.getBoundingClientRect().top < innerHeight * 0.94) { el.classList.remove('rv-wait'); return false; }
        return true;
      });
      if (!wait.length) removeEventListener('scroll', onS);
    }
    function onS() { if (!tick) { tick = true; requestAnimationFrame(check); } }
    if (wait.length) { addEventListener('scroll', onS, { passive: true }); addEventListener('resize', onS); }
    setTimeout(function () { wait.forEach(function (el) { el.classList.remove('rv-wait'); }); wait = []; }, 6000);
  }

  /* tarjetas que responden al cursor (solo con puntero fino) */
  if (!reduce && matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('[data-tilt]').forEach(function (c) {
      c.addEventListener('mousemove', function (e) {
        var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        c.style.transform = 'perspective(900px) rotateX(' + (-y * 4) + 'deg) rotateY(' + (x * 5) + 'deg) translateY(-3px)';
      });
      c.addEventListener('mouseleave', function () { c.style.transform = ''; });
    });
  }

  /* videos: miniatura primero, reproductor al tocar */
  document.querySelectorAll('.yt[data-id]').forEach(function (b) {
    b.style.backgroundImage = 'url(https://i.ytimg.com/vi/' + b.dataset.id + '/hqdefault.jpg), linear-gradient(135deg,#1b2d5c,#0e1629 60%,#2a0f18)';
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + b.dataset.id + '?autoplay=1&rel=0';
      f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'; f.allowFullscreen = true;
      f.title = b.getAttribute('aria-label') || 'Video';
      b.innerHTML = ''; b.appendChild(f);
    }, { once: true });
  });

  /* filtros de listados */
  document.querySelectorAll('[data-filter]').forEach(function (wrap) {
    var list = document.querySelectorAll(wrap.dataset.filter), q = wrap.querySelector('input'), none = document.querySelector(wrap.dataset.none);
    var state = {};
    function apply() {
      var t = q ? norm(q.value) : '', shown = 0;
      list.forEach(function (it) {
        var ok = (!t || norm(it.textContent).indexOf(t) > -1);
        Object.keys(state).forEach(function (k) { if (state[k] !== 'all' && it.dataset[k] !== state[k]) ok = false; });
        it.hidden = !ok; if (ok) shown++;
      });
      if (none) none.hidden = shown > 0;
    }
    wrap.querySelectorAll('.seg').forEach(function (seg) {
      var key = seg.dataset.key; state[key] = 'all';
      seg.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () {
          state[key] = b.dataset.v; seg.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); apply();
        });
      });
    });
    if (q) q.addEventListener('input', apply);
  });

  /* detector de estafas */
  var flags = document.getElementById('flags');
  if (flags) {
    var needle = document.getElementById('needle'), v = document.getElementById('verdict'), tx = document.getElementById('vtext'), tot = flags.querySelectorAll('input').length;
    var M = [['Pinta bien', 'Aun así revisa su trayectoria y pide pruebas de retiros.', 'var(--ok)'],
      ['Ojo, investiga más', 'Hay algo raro. Lee los términos y busca pagos comprobados.', 'var(--mid)'],
      ['Riesgo alto', 'Así empezaron las empresas que terminaron en mi Zona de peligro.', 'var(--bad)']];
    flags.addEventListener('change', function () {
      var n = flags.querySelectorAll('input:checked').length; needle.style.left = Math.min(97, n / tot * 97) + '%';
      if (!n) { v.textContent = 'Marca las señales'; v.style.color = ''; tx.textContent = 'Ninguna empresa es 100% segura, pero estas señales casi nunca fallan.'; return; }
      var m = n <= 1 ? M[0] : n <= 2 ? M[1] : M[2]; v.textContent = m[0] + ' · ' + n + '/' + tot; v.style.color = m[2]; tx.textContent = m[1];
    });
  }

  /* pedir un análisis por WhatsApp */
  var aq = document.getElementById('askq'), aa = document.getElementById('aska');
  if (aq && aa) {
    var wa = aa.getAttribute('href').split('?')[0];
    aq.addEventListener('input', function () {
      var q = aq.value.trim();
      aa.href = wa + '?text=' + encodeURIComponent(q ? 'Hola John, ¿puedes analizar ' + q + '?' : 'Hola John, quiero que analices una empresa');
    });
  }

  /* compartir */
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var u = location.href, done = function () { b.textContent = 'Enlace copiado'; setTimeout(function () { b.textContent = 'Copiar enlace'; }, 2000); };
      var fail = function () { b.textContent = 'Copia la dirección de la barra'; };
      if (navigator.clipboard) navigator.clipboard.writeText(u).then(done, fail); else fail();
    });
  });

  /* fondo de red de nodos (inspirado en el logo) */
  document.querySelectorAll('canvas.nx-net').forEach(function (cv) {
    var ctx = cv.getContext('2d'), W, H, P = [], dpr = Math.min(2, window.devicePixelRatio || 1), run = true;
    function size() {
      W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round(Math.min(70, W * H / 16000)); P = [];
      for (var i = 0; i < n; i++) P.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25 });
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < P.length; i++) {
        var a = P[i]; if (!reduce) { a.x += a.vx; a.y += a.vy; if (a.x < 0 || a.x > W) a.vx *= -1; if (a.y < 0 || a.y > H) a.vy *= -1; }
        for (var j = i + 1; j < P.length; j++) {
          var b = P[j], dx = a.x - b.x, dy = a.y - b.y, d = dx * dx + dy * dy;
          if (d < 16000) { ctx.strokeStyle = 'rgba(92,200,255,' + (0.16 * (1 - d / 16000)) + ')'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
        }
        ctx.fillStyle = i % 7 ? 'rgba(160,190,255,.55)' : 'rgba(47,123,255,.95)'; ctx.beginPath(); ctx.arc(a.x, a.y, i % 7 ? 1.4 : 2.4, 0, 7); ctx.fill();
      }
      if (run && !reduce) requestAnimationFrame(draw);
    }
    size(); draw(); addEventListener('resize', size);
    document.addEventListener('visibilitychange', function () { run = !document.hidden; if (run && !reduce) requestAnimationFrame(draw); });
  });

  /* ---------- artículos ---------- */
  /* listas de reproducción */
  document.querySelectorAll('.yt[data-list]').forEach(function (b) {
    b.style.backgroundImage = 'linear-gradient(135deg,#3a0d12,#0e1629)';
    b.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/videoseries?list=' + b.dataset.list + '&autoplay=1&rel=0';
      f.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture'; f.allowFullscreen = true; f.title = b.getAttribute('aria-label') || 'Lista';
      b.innerHTML = ''; b.appendChild(f);
    }, { once: true });
  });
  /* copiar un código */
  document.querySelectorAll('[data-copytext]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.dataset.copytext, ok = function () { b.textContent = 'Copiado'; setTimeout(function () { b.textContent = 'Copiar'; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(v).then(ok, function () { b.textContent = v; }); else b.textContent = v;
    });
  });
  /* barra de lectura, índice activo y barra fija */
  var prog = document.querySelector('.a-prog i'), body = document.querySelector('.a-body'), sticky = document.querySelector('.a-sticky'), hero = document.querySelector('.a-hero');
  var links = [].slice.call(document.querySelectorAll('.a-toc a')), chaps = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  if (sticky) sticky.hidden = false;
  var ttick = false;
  function art() {
    ttick = false;
    if (prog && body) {
      var r = body.getBoundingClientRect(), tot = r.height - innerHeight * .6;
      prog.style.setProperty('--s', Math.max(0, Math.min(1, -r.top / (tot > 0 ? tot : 1))).toFixed(4));
    }
    if (links.length) {
      var cur = -1;
      chaps.forEach(function (c, i) { if (c && c.getBoundingClientRect().top < innerHeight * .35) cur = i; });
      links.forEach(function (a, i) { a.classList.toggle('on', i === cur); });
    }
    if (sticky && hero) {
      var past = hero.getBoundingClientRect().bottom < 0, foot = document.getElementById('nx-foot');
      var nearEnd = foot && foot.getBoundingClientRect().top < innerHeight;
      sticky.classList.toggle('show', past && !nearEnd);
    }
  }
  if (body) { addEventListener('scroll', function () { if (!ttick) { ttick = true; requestAnimationFrame(art); } }, { passive: true }); addEventListener('resize', art); art(); }
  /* cifras que cuentan al aparecer */
  var nums = [].slice.call(document.querySelectorAll('[data-count]'));
  function fmt(el, v) {
    var f = el.dataset.fmt, dec = (f.split(/[.,]/)[1] || '').length, n = parseFloat(el.dataset.count);
    var s = (/\d\.\d{3}/.test(f) || n >= 10000) ? Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') : (/\./.test(f) ? v.toFixed(dec) : Math.round(v).toString());
    el.textContent = el.dataset.pre + s + el.dataset.suf;
  }
  if (!reduce && nums.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return; io.unobserve(en.target);
        var el = en.target, to = parseFloat(el.dataset.count), t0 = null, final = el.textContent;
        if (!(to > 0)) return;
        function step(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1100), e = 1 - Math.pow(1 - k, 3); fmt(el, to * e); if (k < 1) requestAnimationFrame(step); else el.textContent = final; }
        requestAnimationFrame(step);
      });
    }, { threshold: .6 });
    nums.forEach(function (n) { io.observe(n); });
  }

  /* imágenes externas que no cargan: respaldo con la marca */
  document.querySelectorAll('.a-hero img, .a-chap img').forEach(function (img) {
    function bad() { var h = img.closest('figure,.ph,.page') || img.parentNode; h.classList.add('noimg'); img.style.display = 'none'; if (img.classList.contains('a-bg')) img.remove(); }
    if (img.complete && img.naturalWidth === 0 && img.src) bad(); else img.addEventListener('error', bad);
  });

  /* ---------- curso ---------- */
  var tabs = document.querySelectorAll('[data-tab]');
  function showTab(id, push) {
    tabs.forEach(function (t) { var on = t.dataset.tab === id; t.setAttribute('aria-selected', on); document.getElementById(t.dataset.tab).hidden = !on; });
    if (push) try { history.replaceState(null, '', '#' + id); } catch (e) {}
  }
  if (tabs.length) {
    tabs.forEach(function (t) { t.addEventListener('click', function () { showTab(t.dataset.tab, true); }); });
    if (location.hash === '#herramientas') showTab('herramientas');
    var lh = location.hash.match(/^#l\d+-\d+$/);
    if (lh) { var le = document.querySelector(lh[0]); if (le) { le.closest('details').open = true; setTimeout(function () { le.scrollIntoView({ block: 'start' }); }, 50); } }
    document.querySelectorAll('a[href^="#l"]').forEach(function (a) { a.addEventListener('click', function () { var le = document.querySelector(a.getAttribute('href')); if (le) le.closest('details').open = true; }); });
  }
  document.querySelectorAll('[data-play]').forEach(function (b) {
    b.addEventListener('click', function () {
      var p = b.closest('.lesson').querySelector('.lplayer'); if (!p) return;
      p.hidden = !p.hidden; b.querySelector('em').textContent = p.hidden ? 'Ver ahora' : 'Ocultar';
      if (!p.hidden) { var y = p.querySelector('.yt'); if (y && !y.querySelector('iframe')) y.click(); }
    });
  });
  var seenKey = 'nx-curso-vistas', seen = {};
  try { seen = JSON.parse(localStorage.getItem(seenKey) || '{}') || {}; } catch (e) { seen = {}; }
  var boxes = document.querySelectorAll('[data-seen]'), prog = document.querySelector('.cur-prog');
  function updSeen() {
    var n = 0;
    boxes.forEach(function (c) { var on = !!seen[c.dataset.seen]; c.checked = on; c.closest('.lesson').classList.toggle('done', on); if (on) n++; });
    if (prog) {
      var tot = parseInt(prog.dataset.total, 10) || 0, t = prog.querySelector('[data-prog]');
      prog.querySelector('.bar').style.setProperty('--seen', (tot ? n / tot * 100 : 0) + '%');
      if (tot && t) t.textContent = 'Has visto ' + n + ' de ' + tot + ' lecciones publicadas.';
    }
  }
  boxes.forEach(function (c) { c.addEventListener('change', function () { if (c.checked) seen[c.dataset.seen] = 1; else delete seen[c.dataset.seen]; try { localStorage.setItem(seenKey, JSON.stringify(seen)); } catch (e) {} updSeen(); }); });
  if (boxes.length) updSeen();
})();
