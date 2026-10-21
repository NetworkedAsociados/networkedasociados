#!/usr/bin/env python3
"""Generador del sitio NetworkedAsociados.

Uso:  python build.py      -> crea la carpeta _site lista para publicar.
Para agregar una empresa, app o página edita los archivos de /data (ver README.md).
Sin dependencias externas: solo Python 3.8+.
"""
import json, os, re, shutil, html as H
import bloques as BL
from articulos import A as ARTICULOS
from convertir import convert
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_site')
D = lambda f: json.load(open(os.path.join(ROOT, 'data', f), encoding='utf-8'))
CFG, EMP, APPS, PAGS, REDIR = D('config.json'), D('empresas.json'), D('apps.json'), D('paginas.json'), D('redirecciones.json')
RAW = {p['ruta']: p for p in D('paginas_raw.json')}
R = CFG['redes']; DOM = CFG['dominio']; AUTOR = CFG['autor']
EMPI = {e['id']: e for e in EMP}
for p in PAGS: p.update({k: v for k, v in RAW.get(p['ruta'], {}).items() if k not in p})
PAGI = {p['ruta']: p for p in PAGS}

MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
def fecha(s): y, m, d = s.split('-'); return f'{int(d)} {MES[int(m)-1]} {y}'
esc = H.escape
def rel(out_path):
    depth = out_path.strip('/').count('/')
    return '../' * depth if depth else './'
def url_of(ruta): return ruta.lstrip('/').replace(' ', '%20')
def canon(ruta):
    r = ruta.replace('index.html', '').replace(' ', '%20')
    return DOM + (r if r.startswith('/') else '/' + r)
def first_img(c):
    m = re.search(r'https://blogger\.googleusercontent\.com/[^"\'\s)]+', c or '')
    return m.group(0) if m else ''
def resize(u, s=640): return re.sub(r'/s\d+(-[a-z0-9-]+)?/', f'/s{s}/', u) if u else u
def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

ICON = {
 'broker': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/></svg>',
 'fondeo': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="13" rx="2"/><path d="M16 12h2M3 10h18"/></svg>',
 'peligro': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17h.01"/></svg>',
 'aprende': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 9 10-5 10 5-10 5L2 9z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/></svg>',
 'libro': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h6a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4zM20 4h-6a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h6z"/></svg>',
 'apps': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><path d="M17.5 14v7M14 17.5h7"/></svg>',
 'comunidad': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 20c0-2.5 1-4.5 3-5"/></svg>',
 'arrow': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'search': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
 'menu': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

NAV = [('', 'Inicio', 'inicio'), ('brokers/', 'Brokers', 'brokers'), ('fondeo/', 'Fondeo', 'fondeo'),
       ('zona-de-peligro/', 'Zona de peligro', 'peligro'), ('contenido/', 'Contenido', 'contenido'),
       ('libro/', 'Mi libro', 'libro'), ('aplicaciones/', 'Aplicaciones', 'apps'), ('p/sobre-mi.html', 'Sobre mí', 'sobre')]
NAVSUB = {'brokers': 'Análisis y opiniones', 'fondeo': 'Cuentas financiadas', 'peligro': 'Alertas y riesgos',
          'contenido': 'Guías y experiencias', 'libro': 'La Bitácora Rota', 'apps': 'Mis proyectos', 'sobre': 'Quién está detrás', 'inicio': ''}
SECTION_NAME = {'brokers': 'Brokers', 'fondeo': 'Empresas de fondeo', 'peligro': 'Zona de peligro', 'contenido': 'Contenido',
                'libro': 'Mi libro', 'apps': 'Aplicaciones', 'sobre': 'Sobre mí', 'comunidad': 'Comunidad', 'legal': 'Legal'}
SECTION_URL = {'brokers': 'brokers/', 'fondeo': 'fondeo/', 'peligro': 'zona-de-peligro/', 'contenido': 'contenido/',
               'libro': 'libro/', 'apps': 'aplicaciones/', 'sobre': 'p/sobre-mi.html', 'comunidad': 'comunidad/', 'legal': 'legal/aviso-legal.html'}

DISCLAIMER = ('NetworkedAsociados comparte información, análisis, opiniones y experiencias relacionadas con el trading, los brokers y las empresas de fondeo '
              'con fines informativos y educativos. El contenido no constituye asesoría financiera o de inversión personalizada ni una recomendación individual '
              'para operar o contratar servicios. Las decisiones son responsabilidad de cada persona. La información puede cambiar y debe verificarse con las '
              'fuentes oficiales. El trading y las empresas de fondeo conllevan riesgos y pueden ocasionar pérdidas.')

def header(b, cur):
    links = ''.join(f'<a href="{b}{u}"{" aria-current=\"page\"" if k == cur else ""}{" class=\"nx-danger\"" if k == "peligro" else ""}>{t}</a>' for u, t, k in NAV[1:])
    drawer = ''.join(f'<a href="{b}{u}">{t}<small>{NAVSUB[k]}</small></a>' for u, t, k in NAV)
    return f'''<a class="nx-skip" href="#contenido-principal">Saltar al contenido</a>
<header id="nx-top"><div class="nx-wrap nx-bar">
<a class="nx-brand" href="{b}" aria-label="NetworkedAsociados, inicio"><img src="{b}assets/logo.png" alt="" width="34" height="34"><span>Networked</span></a>
<nav aria-label="Principal">{links}</nav>
<button class="nx-iconbtn nx-search-btn" data-search aria-label="Buscar">{ICON["search"]}<span class="t">Buscar</span><kbd>Ctrl K</kbd></button>
<button class="nx-iconbtn nx-menu" aria-label="Abrir menú" aria-expanded="false">{ICON["menu"]}</button>
<a class="nx-join" href="{b}comunidad/">Únete gratis</a>
</div></header>
<div class="nx-drawer"><div class="nx-wrap">{drawer}<a href="{b}comunidad/">Comunidad<small>Redes y canales</small></a></div></div>
<div class="nx-search" id="nx-search" hidden role="dialog" aria-modal="true" aria-label="Buscar en el sitio"><div class="box">
<input id="nx-q" type="search" placeholder="Busca un broker, empresa o tema…" autocomplete="off" aria-label="Buscar">
<ul id="nx-res"></ul><div class="hint"><span>↑ ↓ para moverte · Enter para abrir</span><span>Esc para cerrar</span></div></div></div>'''

def footer(b):
    return f'''<footer id="nx-foot"><div class="nx-wrap">
<div class="fgrid">
<div><div class="brand"><img src="{b}assets/logo.png" alt="" width="40" height="40">NetworkedAsociados</div>
<p class="slogan">{CFG["eslogan"]}.</p>
<p style="margin-top:10px">Investigación, experiencias reales y herramientas para tu camino como trader.</p></div>
<div><h4>Explorar</h4><ul><li><a href="{b}brokers/">Brokers</a></li><li><a href="{b}fondeo/">Empresas de fondeo</a></li><li><a href="{b}zona-de-peligro/">Zona de peligro</a></li><li><a href="{b}contenido/">Contenido</a></li><li><a href="{b}libro/">Mi libro</a></li><li><a href="{b}aplicaciones/">Aplicaciones</a></li></ul></div>
<div><h4>Comunidad</h4><ul><li><a href="{R["youtube"]}">YouTube</a></li><li><a href="{R["tiktok"]}">TikTok</a></li><li><a href="{R["instagram"]}">Instagram</a></li><li><a href="{R["facebook"]}">Facebook</a></li><li><a href="{R["canal_whatsapp"]}">Canal de WhatsApp</a></li><li><a href="{R["canal_telegram"]}">Canal de Telegram</a></li></ul></div>
<div><h4>Transparencia</h4><ul><li><a href="{b}legal/metodologia.html">Cómo califico</a></li><li><a href="{b}legal/afiliados.html">Enlaces de afiliado</a></li><li><a href="{b}legal/aviso-legal.html">Aviso legal</a></li><li><a href="{b}legal/privacidad.html">Privacidad y cookies</a></li><li><a href="{b}legal/condiciones.html">Condiciones de uso</a></li></ul></div>
</div>
<a class="gamer" href="https://www.johnhansensp.com/" target="_blank" rel="noopener"><span class="gi" aria-hidden="true">🎮</span><span><small>Mi otro mundo</small><b>JohnHansenSP · comunidad de videojuegos y streams</b></span><span class="ga" aria-hidden="true">→</span></a>
<p class="disc">{DISCLAIMER} Algunos enlaces son de afiliado: si te registras con ellos recibo un incentivo, sin costo extra para ti. <a href="{b}legal/afiliados.html">Más detalles</a>.</p>
<p class="disc" style="margin-top:10px;border:0;padding:0">© {date.today().year} NetworkedAsociados · {AUTOR}</p>
</div></footer>'''

def crumbs_html(b, items):
    lis = ''.join((f'<li><a href="{b}{u}">{esc(t)}</a></li>' if u is not None else f'<li aria-current="page">{esc(t)}</li>') for t, u in items)
    return f'<nav aria-label="Ruta"><ol class="crumbs">{lis}</ol></nav>'

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, **({"item": DOM + '/' + u.replace(' ', '%20')} if u is not None else {})}
        for i, (t, u) in enumerate(items)]}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=JetBrains+Mono:wght@500&family=Manrope:wght@400;600;700;800&display=swap">')

def layout(out, title, desc, body, sec='', cur='', ld=None, head='', img='', robots='index,follow', ogtype='website'):
    b = rel(out)
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    image = img or DOM + '/assets/og.png'
    return f'''<!doctype html>
<html lang="es" data-base="{b}" class="{sec}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon(out)}">
<meta name="theme-color" content="#05080f">
<meta property="og:site_name" content="NetworkedAsociados">
<meta property="og:locale" content="es_LA">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon(out)}">
<meta property="og:image" content="{esc(image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{b}assets/logo.png" type="image/png">
{FONTS}
<link rel="stylesheet" href="{b}assets/site.css">
{head}
{lds}
</head>
<body class="{sec}">
{header(b, cur)}
<div id="contenido-principal"></div>
{body}
{footer(b)}
<script src="{b}assets/site.js" defer></script>
</body>
</html>'''

def write(out, s):
    p = os.path.join(OUT, out.lstrip('/')); ensure(p)
    open(p, 'w', encoding='utf-8').write(s)

# ---------------- componentes ----------------
RIESGO_TXT = {'bajo': 'Riesgo bajo', 'medio': 'Riesgo medio', 'alto': 'Riesgo alto'}
def chip_riesgo(e): return f'<span class="chip r-{e["riesgo"]}">{RIESGO_TXT.get(e["riesgo"], "Sin datos")}</span>'
def stars(n):
    if n is None: return '<span class="stars" style="color:var(--muted)">Sin calificación propia</span>'
    return f'<span class="stars"><span class="bar" aria-hidden="true"><i style="--w:{n/5*100:.0f}%"></i></span>{n:g}/5</span>'
def cal(e): return f"{e['calificacion']:g}/5" if e.get('calificacion') else '—'
def mono(e): return f'<span class="monogram" aria-hidden="true">{esc(e["nombre"][0])}</span>'
def upd(e): p = PAGI.get(e['analisis']); return p['actualizado'] if p else ''
def aff_btn(e, cls='b-acc b-sm'):
    if not e.get('afiliado'): return ''
    return f'<a class="btn {cls}" href="{esc(e["afiliado"])}" rel="sponsored noopener" target="_blank">{esc(e["afiliado_texto"])} <span class="aff-tag">afiliado</span></a>'

def card(e, b, extra=''):
    sec = 'sec-fondeo' if e['tipo'] == 'fondeo' else 'sec-brokers'
    favor = ''.join(f'<li>{esc(x)}</li>' for x in e.get('favor', [])[:3])
    u = upd(e)
    return f'''<article class="card {sec} rv" data-tilt data-tipo="{e["tipo"]}" data-riesgo="{e["riesgo"]}">
<div class="top"><div style="display:flex;gap:12px;align-items:center">{mono(e)}<div><div class="kind">{"Broker" if e["tipo"]=="broker" else "Empresa de fondeo"}</div><h3>{esc(e["nombre"])}</h3></div></div>{chip_riesgo(e)}</div>
{stars(e.get("calificacion"))}
<p class="sum">{esc(e["resumen"])}</p>
<ul>{favor}</ul>{extra}
<div class="actions"><a class="btn b-ghost b-sm" href="{b}{url_of(e["analisis"])}">Ver análisis completo</a>{aff_btn(e)}</div>
<div class="meta">Estado: {esc(e["estado"])}{f" · Actualizado {fecha(u)}" if u else ""}</div>
</article>'''

def alert(e, b):
    why = ''.join(f'<span>{esc(x)}</span>' for x in e.get('motivos', []))
    big = '<div class="big">$6.300</div>' if e['id'] == 'veltrix' else ''
    u = upd(e)
    return f'''<article class="alert rv" data-estado="{esc(e["estado"].split(" ")[0].lower())}">
<span class="beacon" aria-hidden="true"></span>
<div><div class="card-kind" style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#ff8191">{esc(e["estado"])}</div>
<h3>{esc(e["nombre"])}</h3><p style="color:var(--muted);margin-top:6px">{esc(e["resumen"])}</p>
<div class="why">{why}</div>
<div class="ev">Base: {esc(e["evidencia"])}{f" · Revisado {fecha(u)}" if u else ""}</div></div>
<div class="side">{big}{stars(e.get("calificacion"))}<a class="btn b-ghost b-sm" href="{b}{url_of(e["analisis"])}">Ver el caso</a></div>
</article>'''

def yt(vid, title):
    return f'<button class="yt" data-id="{esc(vid)}" aria-label="Reproducir: {esc(title)}"><span class="play" aria-hidden="true"></span><span class="cap">{esc(title)}</span></button>'

def post_card(p, b, big=False):
    img = resize(first_img(open(os.path.join(ROOT, 'contenido', p['ruta'].lstrip('/')), encoding='utf-8').read()), 800)
    style = f' style="background-image:url({esc(img)})"' if img else ' style="background:linear-gradient(135deg,var(--panel2),#0f2d75)"'
    return f'''<a class="post-card rv{" big" if big else ""}" href="{b}{url_of(p["ruta"])}" data-cat="{esc(p["categoria"])}">
<span class="img" role="img" aria-label="{esc(p["titulo"])}"{style}></span>
<span class="body"><span class="cat">{esc(p["categoria"])}</span><h3>{esc(clean_title(p["titulo"]))}</h3><p>{esc(p["descripcion"])}</p><time datetime="{p["publicado"]}">{fecha(p["publicado"])}</time></span></a>'''

def clean_title(t): return re.sub(r'\s*[⭐☆★]+.*$', '', re.sub(r'\s*\(\d/5\)', '', t)).strip(' |"') or t

def join_box(b, title='Sigamos creciendo juntos', lead='Alertas, análisis nuevos y directos. Gratis y sin spam.'):
    return f'''<div class="join rv"><span class="eyebrow">{CFG["eslogan"]}</span><h2>{title}</h2><p class="lead">{lead}</p>
<div class="row"><a class="btn b-wa" href="{R["canal_whatsapp"]}">Canal de WhatsApp</a><a class="btn b-tg" href="{R["canal_telegram"]}">Canal de Telegram</a><a class="btn b-yt" href="{R["youtube"]}">Suscríbete en YouTube</a><a class="btn b-ghost" href="{R["tiktok"]}">TikTok</a><a class="btn b-ghost" href="{R["instagram"]}">Instagram</a></div></div>'''

SOC_ICON = {
 'youtube': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .6 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .4-4.8 31 31 0 0 0-.4-4.8zM9.7 15.1V8.9l5.8 3.1z"/></svg>',
 'tiktok': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.6 2h-3.4v13.4a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.1a6.4 6.4 0 1 0 5.4 6.3V8.6a8 8 0 0 0 4.6 1.5V6.7a4.7 4.7 0 0 1-4.6-4.7z"/></svg>',
 'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor"/></svg>',
 'facebook': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 8.5V6.8c0-.8.5-1 .9-1h2.4V2h-3.3C10.4 2 9.6 4.6 9.6 6.3v2.2H7.5v3.9h2.1V22H14v-9.6h2.9l.4-3.9z"/></svg>',
 'whatsapp': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15l-1.4 5 5.1-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.4-.7-2.8-1.1-4.6-4-4.8-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2.1 1-2.4c.3-.3.6-.3.8-.3h.6c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .5l-.4.6-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.4 1.8 2.2 1.2 1.1 2.2 1.4 2.6 1.6.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.7-.1l2 1c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>',
 'telegram': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.9 4.3 18.8 19c-.2 1-.8 1.3-1.7.8l-4.6-3.4-2.2 2.1c-.3.3-.5.5-1 .5l.3-4.7 8.6-7.8c.4-.3-.1-.5-.6-.2L7 13l-4.6-1.4c-1-.3-1-1 .2-1.5L20.5 3c.8-.3 1.6.2 1.4 1.3z"/></svg>',
 'linkedin': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm7 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/></svg>',
}
SOCIAL = [
 ('youtube', 'YouTube', '@NetworkedAsociados', 'Análisis completos, directos y el podcast Cachetadas de Verdad.', 'Suscribirme'),
 ('tiktok', 'TikTok', '@networkedasociados', 'Videos cortos: alertas rápidas, opiniones y psicotrading.', 'Seguir'),
 ('instagram', 'Instagram', '@networkedasociados', 'Historias, novedades del día a día y avances del proceso.', 'Seguir'),
 ('facebook', 'Facebook', 'networkedasociadosoficial', 'Publicaciones y comunidad en Facebook.', 'Seguir'),
 ('canal_whatsapp', 'Canal de WhatsApp', 'NetworkedAsociados', 'Te llegan primero las alertas y los análisis nuevos.', 'Unirme'),
 ('canal_telegram', 'Canal de Telegram', '@NetworkedAsociadosInfo', 'Avisos, novedades y enlaces importantes.', 'Unirme'),
 ('linkedin', 'LinkedIn', 'John Hansen Silva Peña', 'Mi perfil profesional: banca, finanzas y trading.', 'Conectar'),
]
def follow_box(b, title='Sígueme en redes', lead='Elige dónde prefieres seguirme. En cada red comparto algo distinto.', compact=False):
    items = ''
    for k, name, handle, desc, cta in SOCIAL:
        if not R.get(k): continue
        ico = SOC_ICON['whatsapp' if k == 'canal_whatsapp' else 'telegram' if k == 'canal_telegram' else k]
        items += (f'<a class="soc s-{k.replace("canal_", "")}" href="{R[k]}" target="_blank" rel="noopener"><span class="si" aria-hidden="true">{ico}</span>'
                  f'<span class="st"><b>{name}</b><small>{esc(handle)}</small><em>{esc(desc)}</em></span><span class="sc">{cta}</span></a>')
    cls = ' compact' if compact else ''
    return (f'<div class="follow{cls} rv"><canvas class="nx-net" aria-hidden="true"></canvas><div class="fh"><span class="eyebrow">{CFG["eslogan"]}</span>'
            f'<h2>{title}</h2><p class="lead">{lead}</p></div><div class="socs">{items}</div></div>')

def ask_box():
    return f'''<div class="ask rv"><div><span class="eyebrow">Tú eliges el próximo análisis</span><h2 class="h" style="font-size:clamp(1.6rem,3.4vw,2.3rem);margin-top:10px">¿Qué empresa quieres que revise?</h2>
<p class="lead" style="margin-top:8px">Escribe el nombre y me llega directo por WhatsApp. Las más pedidas las investigo primero.</p></div>
<div class="row"><input id="askq" type="text" placeholder="Ej: un broker o fondeo que te ofrecieron" aria-label="Nombre de la empresa"><a class="btn b-wa" id="aska" href="{R["whatsapp_directo"]}?text=Hola%20John%2C%20quiero%20que%20analices%20una%20empresa" target="_blank" rel="noopener">Pedir análisis</a></div></div>'''

DETECTOR = '''<div class="det">
<div class="flags" id="flags">
<label class="flag"><input type="checkbox" id="f1">Prometen ganancias fijas o "garantizadas"</label>
<label class="flag"><input type="checkbox" id="f2">Ganas más trayendo referidos que operando</label>
<label class="flag"><input type="checkbox" id="f3">No tiene años de trayectoria que puedas verificar</label>
<label class="flag"><input type="checkbox" id="f4">Las reglas son ambiguas o cambian cuando ganas</label>
<label class="flag"><input type="checkbox" id="f5">Los retiros tardan o siempre hay una excusa</label>
<label class="flag"><input type="checkbox" id="f6">El soporte no responde o desaparece</label>
</div>
<div class="meter" aria-live="polite"><div class="gauge"><div class="needle" id="needle"></div></div>
<p class="verdict" id="verdict">Marca las señales</p><p id="vtext">Ninguna empresa es 100% segura, pero estas señales casi nunca fallan.</p>
<p style="font-size:13px">Es una guía rápida basada en los casos que he vivido, no un veredicto sobre una empresa concreta.</p></div>
</div>'''

def shead(b, sec, h1, lead, crumbs, extra=''):
    return f'''<section class="shead"><canvas class="nx-net" aria-hidden="true"></canvas><div class="nx-wrap">
{crumbs_html(b, crumbs)}<span class="eyebrow" style="margin-top:22px">{SECTION_NAME.get(sec, "")}</span>
<h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div></section>'''

# ---------------- artículos internos ----------------
def slug(t):
    import unicodedata
    t = unicodedata.normalize('NFD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:40] or 'seccion'

def auto_article(raw, p):
    """Para artículos nuevos sin versión escrita en articulos.py: convierte el HTML de Blogger al diseño nuevo."""
    _, blocks = convert(raw)
    caps, cur, used = [], None, set()
    for x in blocks:
        if x['t'] == 'h2':
            sid = slug(x['text']); sid = sid if sid not in used else sid + str(len(used)); used.add(sid)
            cur = BL.cap(sid, '', x['text']); caps.append(cur); continue
        if cur is None: cur = BL.cap('inicio', '', 'Introducción'); caps.append(cur)
        t = x['t']; add = cur['bloques'].append
        if t == 'h3': add(BL.HTML(f'<h3 class="a-sub">{esc(x["text"])}</h3>'))
        elif t == 'p': add(BL.P(x['html']))
        elif t == 'list': add(BL.Lista(*x['items']))
        elif t == 'quote': add(BL.HTML(f'<figure class="a-quote"><blockquote>{x["html"]}</blockquote></figure>'))
        elif t == 'buttons': add(BL.Botones(*[(i['text'], i['href'], 'b-ghost') for i in x['items']]))
        elif t == 'image': add(BL.Imagen(x['src'], x.get('alt', '')))
        elif t == 'video': add(BL.Playlist(x['list'], 'Ver la lista') if x.get('list') and not x.get('id') else BL.Video(x['id'], clean_title(p['titulo'])))
    return dict(hero=dict(kicker=SECTION_NAME.get(p['seccion'], ''), titulo=clean_title(p['titulo']), lead=p['descripcion']), caps=caps)

def ring(e):
    n = e.get('calificacion')
    if not n: return '<div class="ring none"><b><small>Sin calificación propia</small></b></div>'
    return (f'<div class="ring r-{e["riesgo"]}" style="--p:{n/5*100:.0f}" role="img" aria-label="Calificación {n:g} de 5"><svg viewBox="0 0 120 120" aria-hidden="true">'
            f'<circle cx="60" cy="60" r="52"/><circle class="v" cx="60" cy="60" r="52" pathLength="100"/></svg><b>{n:g}<small>/5</small></b></div>')

def src(u, b): return u if u.startswith('http') else b + u
def absimg(u): return u if not u or u.startswith('http') else DOM + '/' + u

def art_hero(p, e, h, b, crumbs, mins):
    bg = f'<img class="a-bg" src="{esc(src(h["img"], b))}" alt="" aria-hidden="true" decoding="async">' if h.get('img') else ''
    if e:
        side = f'''<aside class="a-hud{" danger" if e["zona"] == "peligro" else ""}"><div class="hud-top"><span>{"Ficha de investigación" if e["zona"] == "catalogo" else "Expediente"}</span><span class="live">● {esc(e["estado"].split(" ·")[0])}</span></div>
{ring(e)}<dl><dt>Tipo</dt><dd>{"Broker" if e["tipo"] == "broker" else "Empresa de fondeo"}</dd><dt>Riesgo</dt><dd>{chip_riesgo(e)}</dd><dt>Base</dt><dd>{esc(e["evidencia"])}</dd>{f"<dt>Desde</dt><dd>{esc(e['fundado'])}</dd>" if e.get("fundado") else ""}<dt>Revisado</dt><dd>{fecha(p["actualizado"])}</dd></dl>
<p class="note">{"Mi opinión y experiencia, no asesoría financiera." if e["zona"] == "catalogo" else "¿Tienes información nueva? <a href='" + R["telegram_directo"] + "'>Envíala aquí</a>."}</p></aside>'''
    elif h.get('cover'):
        pr = h.get('precio')
        side = f'''<div class="a-book"><div class="cover"><div class="page" role="img" aria-label="Portada: {esc(h["titulo"])}"><img src="{esc(src(h["cover"], b))}" alt="" decoding="async"></div></div>
{f'<div class="price"><b>{pr[0]}</b><s>{pr[1]}</s></div><span class="chip r-bajo">{esc(pr[2])}</span>' if pr else ""}</div>'''
    elif h.get('foto'):
        side = f'''<div class="a-player"><div class="ph"><img src="{esc(src(h["foto"], b))}" alt="{esc(h["titulo"])}" decoding="async"></div><div class="lvl"><span>Nivel</span><b>Trader · Creador · Ajedrecista</b></div>
<div class="bars"><div><span>Disciplina</span><i style="--w:90%"></i></div><div><span>Transparencia</span><i style="--w:96%"></i></div><div><span>Constancia</span><i style="--w:88%"></i></div></div><p class="note">Barras decorativas, no son una medición.</p></div>'''
    elif h.get('chat'):
        side = BL.block(BL.Chat(*h['chat']), b)
    elif h.get('img'):
        side = f'<figure class="a-frame"><img src="{esc(src(h["img"], b))}" alt="{esc(h["titulo"])}" decoding="async"></figure>'
    else:
        side = f'<div class="a-emblem" aria-hidden="true"><span class="orbit"><i></i></span><span class="orbit o2"><i></i></span><img src="{b}assets/logo.png" alt="" width="260" height="260"></div>'
    chips = ''.join(f'<span>{esc(c)}</span>' for c in h.get('chips', []))
    btns = ''.join(BL.btn(x, b) for x in h.get('botones', []))
    return f'''<section class="a-hero{" danger" if e and e["zona"] == "peligro" else ""}">{bg}<canvas class="nx-net" aria-hidden="true"></canvas>
<div class="nx-wrap"><div class="a-hero-in">{crumbs_html(b, crumbs)}<span class="eyebrow">{esc(h.get("kicker", ""))}</span>
<h1>{esc(h["titulo"])}</h1><p class="lead">{esc(h["lead"])}</p>{f'<div class="a-chips">{chips}</div>' if chips else ""}{f'<div class="a-btns">{btns}</div>' if btns else ""}
<p class="a-meta"><span>Por {AUTOR}</span><span>Actualizado {fecha(p["actualizado"])}</span><span>⏱ {mins} min de lectura</span></p></div>
<div class="a-side">{side}</div></div></section>'''

ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "NetworkedAsociados", "url": DOM + '/',
       "logo": DOM + '/assets/logo.png', "slogan": CFG['eslogan'],
       "sameAs": [v for k, v in R.items() if v and k in ('youtube', 'tiktok', 'instagram', 'facebook', 'linkedin')],
       "founder": {"@type": "Person", "name": AUTOR}}

# ---------------- páginas ----------------
def build():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'static'), os.path.join(OUT, 'assets'))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    open(os.path.join(OUT, 'CNAME'), 'w').write(DOM.split('//')[1] + '\n')
    sitemap, index = [], []

    brokers = [e for e in EMP if e['zona'] == 'catalogo' and e['tipo'] == 'broker']
    fondeo = [e for e in EMP if e['zona'] == 'catalogo' and e['tipo'] == 'fondeo']
    peligro = [e for e in EMP if e['zona'] == 'peligro']
    contenido = sorted(PAGS, key=lambda p: p['publicado'], reverse=True)
    best = max([e for e in brokers if e.get('calificacion')], key=lambda e: e['calificacion'])

    # ---- inicio ----
    b = './'
    mini_b = ''.join(f'<div><span>{esc(e["nombre"])}</span>{stars(e["calificacion"])}</div>' for e in brokers)
    mini_p = ''.join(f'<div><span>{esc(e["nombre"])}</span><span style="color:#ff8191;font-size:12px">{esc(e["estado"].split(" ·")[0])}</span></div>' for e in peligro[:3])
    home = f'''<main class="nx">
<section class="hero"><canvas class="nx-net" aria-hidden="true"></canvas>
<div class="nx-glow" style="width:520px;height:520px;right:-120px;top:-160px;background:rgba(47,123,255,.25)"></div>
<div class="nx-wrap">
<div><span class="eyebrow">Hola, soy John · NetworkedAsociados</span>
<h1>Tu próxima decisión empieza con <em>mejor información.</em></h1>
<p class="slogan">{CFG["eslogan"]}.</p>
<p class="lead">Pruebo brokers y empresas de fondeo con mi propio dinero y te cuento lo que pasa: quién paga, quién no y qué vigilar. Investigación, experiencias reales y herramientas para tu camino como trader.</p>
<button class="bigsearch" data-search aria-label="Buscar en el sitio">{ICON["search"]}<span>¿Qué empresa estás evaluando?</span><b>Buscar</b></button>
<div class="quick"><a href="{b}brokers/">Mejores brokers</a><a href="{b}zona-de-peligro/">¿Es estafa?</a><a href="{b}fondeo/">Cuentas de fondeo</a><a href="{b}libro/">Mi libro</a></div>
</div>
<div class="emblem" aria-hidden="true"><span class="orbit"><i></i></span><span class="orbit o2"><i></i></span>
<img src="{b}assets/logo.png" alt="" width="360" height="360">
<span class="tag t1"><small>Mejor calificado</small>{esc(best["nombre"])} · {best["calificacion"]:g}/5</span>
<span class="tag t2"><small>Alertas activas</small>{len(peligro)} empresas</span>
<span class="tag t3"><small>Trayectoria</small>+11 años en internet</span></div>
</div></section>

<section class="nx-wrap sec">
<div class="head"><div><span class="eyebrow">Elige tu ruta</span><h2>¿Por dónde quieres empezar?</h2><p class="lead">Cada área tiene su propia investigación. Entra a la que te interese y profundiza a tu ritmo.</p></div></div>
<div class="routes">
<a class="route r-brokers rv" href="{b}brokers/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["broker"]}</span><h3>Explorar brokers</h3><p>Descubre y compara plataformas donde he operado con dinero real.</p><div class="mini">{mini_b}</div><span class="stat">{len(brokers)} ANALIZADOS</span></a>
<a class="route r-fondeo rv" href="{b}fondeo/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["fondeo"]}</span><h3>Empresas de fondeo</h3><p>Evaluaciones, condiciones y mi experiencia con cuentas financiadas.</p><span class="stat">{len(fondeo)} EN CATÁLOGO</span></a>
<a class="route r-peligro rv" href="{b}zona-de-peligro/" data-tilt><span class="pulse" aria-hidden="true"></span><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["peligro"]}</span><h3>Zona de peligro</h3><p>Empresas con incumplimientos documentados, alertas y riesgos.</p><div class="mini">{mini_p}</div><span class="stat">{len(peligro)} ALERTAS</span></a>
<a class="route r-aprende rv" href="{b}contenido/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["aprende"]}</span><h3>Aprende y mejora</h3><p>Guías, experiencias, psicología del trading y el curso que viene.</p></a>
<a class="route r-libro rv" href="{b}libro/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["libro"]}</span><h3>Mi libro</h3><p>La Bitácora Rota y Una Promesa: de $1,70 en mi cuenta al camino de regreso.</p></a>
<a class="route r-apps rv" href="{b}aplicaciones/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["apps"]}</span><h3>Aplicaciones</h3><p>BitacoraNetBot, RABOTE y las herramientas que estoy creando.</p></a>
<a class="route r-comunidad rv" href="{b}comunidad/" data-tilt><span class="go">{ICON["arrow"]}</span><span class="ico">{ICON["comunidad"]}</span><h3>Comunidad</h3><p>Acompáñame en redes y entérate primero de cada alerta.</p></a>
</div></section>

<section class="nx-wrap sec sec-brokers" style="padding-top:0">
<div class="head"><div><span class="eyebrow">Selección</span><h2>Dónde opero hoy</h2><p class="lead">Resumen rápido. El análisis completo está en cada ficha.</p></div><a class="more" href="{b}brokers/">Ver todos</a></div>
<div class="rail">{"".join(card(e, b) for e in brokers + fondeo)}</div></section>

<section class="nx-wrap sec sec-peligro" style="padding-top:0">
<div class="head"><div><span class="eyebrow">Alertas recientes</span><h2>Antes de depositar, revisa esto</h2></div><a class="more" href="{b}zona-de-peligro/">Ir a la Zona de peligro</a></div>
<div style="display:grid;gap:12px">{"".join(alert(e, b) for e in peligro[:3])}</div></section>

<section class="nx-wrap sec sec-peligro" style="padding-top:0"><div class="head"><div><span class="eyebrow">Pruébalo</span><h2>Detector de señales de riesgo</h2><p class="lead">¿Te ofrecieron un proyecto? Marca lo que te suena.</p></div></div>{DETECTOR}</section>

<section class="nx-wrap sec sec-contenido" style="padding-top:0">
<div class="head"><div><span class="eyebrow">Recomendado</span><h2>Para leer con calma</h2></div><a class="more" href="{b}contenido/">Todo el contenido</a></div>
<div class="feat">{post_card(PAGI["/2026/03/el-libro-que-resume-4-anos-enfrentando.html"], b, True)}<div style="display:grid;gap:16px">{post_card(PAGI["/2026/03/cachetadas de verdad.html"], b)}{post_card(PAGI["/2026/08/bitacoranetbot.html"], b)}</div></div></section>

<section class="nx-wrap sec" style="padding-top:0">
<div class="head"><div><span class="eyebrow">En video</span><h2>Mira los análisis</h2></div><a class="more" href="{R["youtube"]}">Canal de YouTube</a></div>
<div class="vids">{"".join(yt(v["id"], v["titulo"]) for v in CFG["videos_destacados"][:3])}</div></section>

<section class="nx-wrap sec" style="padding-top:0">{ask_box()}</section>
<section class="nx-wrap sec" style="padding-top:0">{follow_box(b)}</section>
</main>'''
    ld = [ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": "NetworkedAsociados", "url": DOM + '/', "inLanguage": "es"}]
    write('/index.html', layout('/index.html', 'NetworkedAsociados | Análisis de brokers, fondeo y alertas de riesgo',
        'Análisis reales de brokers y empresas de fondeo, alertas de riesgo y educación para traders. Experiencia documentada por John Hansen Silva Peña.',
        home, cur='inicio', ld=ld)); sitemap.append(('/', date.today().isoformat()))

    # ---- brokers ----
    def hub_catalog(out, sec, items, h1, lead, extra_html, cur, desc):
        b = rel(out)
        rows = ''.join(f'<tr><td><a href="{b}{url_of(e["analisis"])}">{esc(e["nombre"])}</a></td><td class="num">{cal(e)}</td><td>{chip_riesgo(e)}</td><td>{esc(e["estado"])}</td><td class="num">{esc(e.get("fundado") or "—")}</td><td>{esc(e["evidencia"])}</td></tr>' for e in items)
        body = f'''<main class="nx">{shead(b, sec, h1, lead, [("Inicio", ""), (SECTION_NAME[sec], None)])}
<section class="nx-wrap sec">
<div class="toolbar" data-filter=".cards .card" data-none="#none"><input type="search" placeholder="Busca por nombre o característica…" aria-label="Filtrar">
<div class="seg" data-key="riesgo" role="group" aria-label="Riesgo"><button data-v="all" aria-pressed="true">Todos</button><button data-v="bajo" aria-pressed="false">Riesgo bajo</button><button data-v="medio" aria-pressed="false">Riesgo medio</button></div></div>
<div class="cards">{"".join(card(e, b) for e in items)}</div>
<p class="noresults" id="none" hidden>No hay resultados con ese filtro. ¿Quieres que la analice? <a href="{b}comunidad/#pedir" style="color:var(--cyan)">Pídemela</a>.</p>
</section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">Comparar</span><h2>Lado a lado</h2><p class="lead">Solo comparo datos que he documentado. Lo que no tengo verificado aparece con un guion.</p></div><a class="more" href="{b}legal/metodologia.html">Cómo califico</a></div>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Nombre</th><th>Calificación</th><th>Riesgo</th><th>Estado</th><th>Desde</th><th>Base del análisis</th></tr></thead><tbody>{rows}</tbody></table></div></section>
{extra_html}
<section class="nx-wrap sec" style="padding-top:0">{ask_box()}</section></main>'''
        ld = [crumbs_ld([("Inicio", ""), (SECTION_NAME[sec], None)]),
              {"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "url": canon(out), "description": desc}]
        write(out, layout(out, f'{h1} | NetworkedAsociados', desc, body, sec='sec-' + sec, cur=cur, ld=ld))
        sitemap.append((out.replace('index.html', ''), date.today().isoformat()))

    b1 = '../'
    hub_catalog('/brokers/index.html', 'brokers', brokers, 'Brokers que he probado',
        'Plataformas donde he operado con mi dinero, calificadas con el mismo criterio. Te muestro lo bueno, lo pendiente y el enlace oficial.',
        f'<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p>¿Buscas la página original de brokers y fondeo con mi metodología completa? Sigue disponible.</p><a class="btn b-ghost b-sm" href="{b1}p/brokers.html">Ver página original</a></div></section>',
        'brokers', 'Opiniones y análisis de brokers: Weltrade, Deriv y Bridge Markets. Calificación, riesgo y experiencia real de un trader.')
    hub_catalog('/fondeo/index.html', 'fondeo', fondeo, 'Empresas de fondeo',
        'Cuentas financiadas que conozco de primera mano. Antes de pagar una evaluación, revisa también las que terminaron en la Zona de peligro.',
        f'''<section class="nx-wrap sec sec-peligro" style="padding-top:0"><div class="head"><div><span class="eyebrow">Ojo con estas</span><h2>Fondeos con alertas</h2></div><a class="more" href="{b1}zona-de-peligro/">Ver Zona de peligro</a></div>
<div style="display:grid;gap:12px">{"".join(alert(e, b1) for e in peligro if e["tipo"] == "fondeo")}</div></section>''',
        'fondeo', 'Opiniones y análisis de empresas de fondeo: The5ers, Bridge Markets ProFirm y alertas sobre fondeos que dejaron de pagar.')

    # ---- zona de peligro ----
    out = '/zona-de-peligro/index.html'; b = rel(out)
    body = f'''<main class="nx">{shead(b, "peligro", "Zona de peligro", "Empresas con incumplimientos, cierres o señales de riesgo. Diferencio lo que viví, lo que reportó la comunidad y lo que sigue en investigación.", [("Inicio", ""), ("Zona de peligro", None)])}
<section class="nx-wrap sec">
<div class="toolbar" data-filter=".alerts .alert" data-none="#none"><input type="search" placeholder="Busca una empresa…" aria-label="Filtrar alertas"></div>
<div class="alerts" style="display:grid;gap:14px">{"".join(alert(e, b) for e in peligro)}</div>
<p class="noresults" id="none" hidden>No tengo esa empresa en la lista. Eso no la hace segura: <a href="{b}comunidad/#pedir" style="color:var(--cyan)">pídeme que la revise</a>.</p></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">Cómo leer los estados</span><h2>Qué significa cada alerta</h2></div><a class="more" href="{b}legal/metodologia.html#riesgo">Criterios de riesgo</a></div>
<div class="legend">
<div><b>Riesgo elevado</b>Incumplimientos graves documentados y la empresa dejó de operar.</div>
<div><b>Alertas documentadas</b>Problemas concretos que viví o comprobé, con evidencia publicada.</div>
<div><b>Inactiva o cerrada</b>Dejó de operar, sin soporte ni comunicación.</div>
<div><b>En investigación</b>Señales que merecen revisión. Todavía no hay conclusión.</div></div>
<p class="lead" style="margin-top:16px;font-size:15px">Cada caso indica su base: experiencia personal, seguimiento de la comunidad o reportes de terceros. Una mala experiencia no equivale por sí sola a una conclusión de fraude.</p></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">Pruébalo</span><h2>Detector de señales de riesgo</h2></div></div>{DETECTOR}</section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p><b style="color:var(--fg)">¿Tienes información o representas a una de estas empresas?</b> Si algún dato está desactualizado o puedes aportar pruebas, escríbeme. Reviso cada solicitud y actualizo la ficha si corresponde.</p><a class="btn b-tg b-sm" href="{R["telegram_directo"]}">Enviar información o corrección</a></div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p>La lista de seguimiento original, con su sistema de estrellas, sigue disponible.</p><a class="btn b-ghost b-sm" href="{b}p/precaucion-con-estas-empresas.html">Ver lista original</a></div></section>
</main>'''
    write(out, layout(out, 'Zona de peligro: alertas sobre brokers y fondeos | NetworkedAsociados',
        'Alertas sobre empresas de fondeo y brokers con impagos, cierres o señales de riesgo: FX Live Capital, Veltrix Funding, NeoFondeo y TopTen.',
        body, sec='sec-peligro', cur='peligro', ld=[crumbs_ld([("Inicio", ""), ("Zona de peligro", None)])])); sitemap.append(('/zona-de-peligro/', date.today().isoformat()))

    # ---- contenido (aprende) ----
    out = '/contenido/index.html'; b = rel(out)
    learn = [p for p in contenido if p['seccion'] in ('contenido', 'libro', 'apps') and p['ruta'] != '/p/contenido-de-valor.html']
    body = f'''<main class="nx">{shead(b, "contenido", "Aprende y mejora", "El curso gratuito está en camino. Mientras tanto, aquí tienes el podcast, el libro y las herramientas para trabajar tu proceso.", [("Inicio", ""), ("Contenido", None)])}
<section class="nx-wrap sec">
<div class="course rv"><canvas class="nx-net" aria-hidden="true"></canvas>
<div class="c-in"><div class="c-l"><span class="c-badge"><i></i>Próximamente</span>
<h2>Curso de trading gratuito</h2>
<p class="lead">No será un curso más. Será el mismo proceso real que llevo documentando durante años, explicado paso a paso para que puedas entenderlo y aplicarlo.</p>
<div class="c-state"><span>Estado</span><b>En preparación</b><span>Precio</span><b>Gratis</b></div>
<div class="a-btns"><a class="btn b-wa" href="{R["canal_whatsapp"]}" target="_blank" rel="noopener">Avísame por WhatsApp</a><a class="btn b-tg" href="{R["canal_telegram"]}" target="_blank" rel="noopener">Avísame por Telegram</a><a class="btn b-ghost" href="{b}p/contenido-de-valor.html">Lo que viene</a></div></div>
<div class="c-r"><div class="c-mod"><span>01</span><div><b>📘 Curso de trading</b><p>El proceso completo, explicado desde la experiencia real y sin promesas irreales.</p></div></div>
<div class="c-mod"><span>02</span><div><b>🎬 Psicotrading en corto</b><p>Ideas y aprendizajes directos para afrontar mejor el día a día del trading.</p></div></div>
<div class="c-mod"><span>03</span><div><b>🎯 Nuevas actividades</b><p>Proyectos y experiencias que iremos revelando poco a poco.</p></div></div></div></div></div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">Mientras tanto</span><h2>Aprende con lo que ya está listo</h2><p class="lead">Podcast, libro y herramientas para trabajar tu psicología y tu disciplina.</p></div></div>
<div class="cards">{"".join(post_card(p, b) for p in learn)}</div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p><b style="color:var(--fg)">¿Buscas análisis de empresas?</b> Están en su propia sección, con calificación y nivel de riesgo.</p><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn b-ghost b-sm" href="{b}brokers/">Brokers</a><a class="btn b-ghost b-sm" href="{b}fondeo/">Fondeo</a><a class="btn b-ghost b-sm" href="{b}zona-de-peligro/">Zona de peligro</a></div></div></section>
<section class="nx-wrap sec" style="padding-top:0">{follow_box(b, "Entérate primero cuando salga el curso")}</section></main>'''
    write(out, layout(out, 'Aprende trading: curso gratuito, podcast y libro | NetworkedAsociados',
        'Curso de trading gratuito (próximamente), el podcast Cachetadas de Verdad, el libro La Bitácora Rota y herramientas para tu disciplina como trader.', body, sec='sec-contenido', cur='contenido',
        ld=[crumbs_ld([("Inicio", ""), ("Contenido", None)])])); sitemap.append(('/contenido/', date.today().isoformat()))

    # ---- libro ----
    out = '/libro/index.html'; b = rel(out)
    lp = PAGI['/2026/03/el-libro-que-resume-4-anos-enfrentando.html']
    cover = b + 'assets/libro-portada.jpg'; cover_abs = DOM + '/assets/libro-portada.jpg'
    buy = R['whatsapp_directo'] + '?text=Quiero%20adquirir%20el%20libro%20La%20Bit%C3%A1cora%20Rota'
    body = f'''<main class="nx">
<section class="shead"><div class="nx-wrap">{crumbs_html(b, [("Inicio", ""), ("Mi libro", None)])}
<div class="book" style="margin-top:28px">
<div class="cover"><div class="page" role="img" aria-label="Portada del libro La Bitácora Rota y Una Promesa" style="background-image:url({cover})"></div></div>
<div><span class="eyebrow">Mi libro</span><h1 style="margin:14px 0 12px">La Bitácora Rota y Una Promesa</h1>
<p class="lead">No es un libro de estrategias. Es la historia real de cómo caer al fondo y encontrar el camino de regreso.</p>
<div class="price" style="margin-top:20px"><b>$6 USD</b><s>$12 USD</s><span class="chip r-bajo">Oferta de lanzamiento</span></div>
<p style="color:var(--muted);margin-top:6px">Entrega digital · respuesta inmediata por WhatsApp</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:20px"><a class="btn b-acc" href="{buy}" target="_blank" rel="noopener">Quiero el libro</a><a class="btn b-ghost" href="https://bit.ly/4uvOz4s" target="_blank" rel="noopener">Leer el primer capítulo gratis</a></div>
</div></div></div></section>
<section class="nx-wrap sec"><div class="book" style="grid-template-columns:1fr 1fr"><div><span class="eyebrow">$1,70</span><p class="quote" style="margin-top:14px">El saldo más bajo de mi cuenta de trading. Ahí entendí que el mercado no era el problema.</p></div>
<div>{yt("_OFl26Eu-8o", "De qué trata el libro")}</div></div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">Dentro del libro</span><h2>Lo que vas a entender</h2></div></div>
<div class="learn"><div><b>Mentalidad real</b><p>Lo que pasa de verdad cuando tienes dinero en riesgo y las emociones toman el control.</p></div>
<div><b>Errores documentados</b><p>Sobreconfianza, revenge trading, romper el plan. Sin filtros.</p></div>
<div><b>Psicología de trading</b><p>El juego no ocurre en los gráficos, ocurre en tu cabeza.</p></div>
<div><b>Proceso sin humo</b><p>Disciplina documentada en tiempo real, sin resultados editados.</p></div></div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p>Sobre el autor: {AUTOR}, profesional en Banca y Finanzas, +7 años en trading y +11 años creando contenido.</p><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn b-ghost b-sm" href="{b}p/sobre-mi.html">Conocer al autor</a><a class="btn b-ghost b-sm" href="{b}{url_of(lp["ruta"])}">Página completa del libro</a></div></div></section>
</main>'''
    ld = [crumbs_ld([("Inicio", ""), ("Mi libro", None)]),
          {"@context": "https://schema.org", "@type": "Book", "name": "La Bitácora Rota y Una Promesa", "author": {"@type": "Person", "name": AUTOR},
           "image": cover_abs, "inLanguage": "es", "bookFormat": "https://schema.org/EBook"}]
    write(out, layout(out, 'La Bitácora Rota y Una Promesa · libro de John Hansen | NetworkedAsociados',
        'La historia real de un trader que llegó a $1,70 en su cuenta y encontró el camino de regreso. Psicología, errores y disciplina sin humo.',
        body, sec='sec-libro', cur='libro', ld=ld, img=cover_abs)); sitemap.append(('/libro/', date.today().isoformat()))

    # ---- aplicaciones ----
    out = '/aplicaciones/index.html'; b = rel(out)
    stcls = {'Disponible': 'st-disponible', 'En pruebas': 'st-pruebas', 'En desarrollo': 'st-desarrollo', 'En planificación': 'st-plan'}
    def app(a):
        href = a['enlace'] if a['enlace'].startswith('http') else b + url_of(a['enlace'])
        return f'''<article class="app rv" data-tilt><span class="chip st {stcls.get(a["estado"], "st-plan")}">{esc(a["estado"])}</span>
<div class="kind" style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)">{esc(a["tipo"])}</div>
<h3>{esc(a["nombre"])}</h3><p>{esc(a["descripcion"])}</p><ul>{"".join(f"<li>{esc(f)}</li>" for f in a["funciones"])}</ul>
<a class="btn b-acc b-sm" href="{href}">{esc(a["enlace_texto"])}</a></article>'''
    body = f'''<main class="nx">{shead(b, "apps", "Aplicaciones y proyectos", "Herramientas y juegos que estoy construyendo para la comunidad. Algunos ya puedes usarlos y otros están en camino.", [("Inicio", ""), ("Aplicaciones", None)])}
<section class="nx-wrap sec"><div class="apps">{"".join(app(a) for a in APPS)}</div></section>
<section class="nx-wrap sec" style="padding-top:0">{follow_box(b, "Sigue la evolución de cada proyecto")}</section></main>'''
    write(out, layout(out, 'Aplicaciones y proyectos digitales | NetworkedAsociados',
        'BitacoraNetBot, RABOTE y NetworkedAPP: las herramientas y proyectos digitales de NetworkedAsociados.', body, sec='sec-apps', cur='apps',
        ld=[crumbs_ld([("Inicio", ""), ("Aplicaciones", None)])])); sitemap.append(('/aplicaciones/', date.today().isoformat()))

    # ---- comunidad ----
    out = '/comunidad/index.html'; b = rel(out)
    body = f'''<main class="nx">{shead(b, "comunidad", "Acompáñame en redes", "Aquí publico primero las alertas, los análisis nuevos y los directos. Elige dónde prefieres seguirme.", [("Inicio", ""), ("Comunidad", None)])}
<section class="nx-wrap sec">{follow_box(b, "Acompáñame donde prefieras", "Cada red tiene su propio contenido. Los canales de WhatsApp y Telegram son los más rápidos para las alertas.")}</section>
<section class="nx-wrap sec" style="padding-top:0"><div class="head"><div><span class="eyebrow">En video</span><h2>Videos destacados</h2></div><a class="more" href="{R["youtube"]}">Ver el canal</a></div>
<div class="vids">{"".join(yt(v["id"], v["titulo"]) for v in CFG["videos_destacados"])}</div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta"><p><b style="color:var(--fg)">Podcast Cachetadas de Verdad.</b> Entrevistas a traders sobre sus errores y su psicología.</p><a class="btn b-yt b-sm" href="{R["podcast_playlist"]}">Ver episodios</a></div></section>
<section class="nx-wrap sec" style="padding-top:0"><div class="fixcta gamer-cta"><p><b style="color:var(--fg)">🎮 ¿También eres gamer?</b> Mis transmisiones y la comunidad de videojuegos van aparte, en JohnHansenSP.</p><a class="btn b-ghost b-sm" href="https://www.johnhansensp.com/" target="_blank" rel="noopener">Ir a JohnHansenSP</a></div></section>
<section class="nx-wrap sec" id="pedir" style="padding-top:0">{ask_box()}</section></main>'''
    write(out, layout(out, 'Comunidad NetworkedAsociados: redes y canales', 'Sígueme en YouTube, TikTok, Instagram y únete a los canales de WhatsApp y Telegram de NetworkedAsociados.',
        body, sec='sec-contenido', cur='', ld=[crumbs_ld([("Inicio", ""), ("Comunidad", None)])])); sitemap.append(('/comunidad/', date.today().isoformat()))

    # ---- legal ----
    P = lambda t: f'<span class="pend">PENDIENTE: {t}</span>'
    legal = {
     'aviso-legal': ('Aviso legal', 'Información sobre el titular del sitio y el carácter informativo del contenido.', f'''
<h2>Titular del sitio</h2><p>Este sitio es operado por {AUTOR}, bajo la marca NetworkedAsociados.</p>
<p>Correo de contacto: {P("correo electrónico de contacto")}. Ciudad y país: {P("ciudad y país del titular")}.</p>
<h2>Carácter del contenido</h2><p>{DISCLAIMER}</p>
<h2>Opiniones y experiencias</h2><p>Los análisis combinan hechos verificables, experiencias personales y opiniones. Cada ficha indica la base de su evaluación. Las calificaciones reflejan mi criterio y mi experiencia en una fecha determinada; no son certificaciones oficiales.</p>
<h2>Rectificaciones</h2><p>Si consideras que alguna información es inexacta o está desactualizada, escríbeme por <a href="{R["telegram_directo"]}">Telegram</a> o <a href="{R["whatsapp_directo"]}">WhatsApp</a> con las pruebas disponibles. Reviso cada solicitud y actualizo el contenido cuando corresponde.</p>
<p>Este texto es una base informativa y no reemplaza la revisión de un profesional del derecho.</p>'''),
     'privacidad': ('Política de privacidad y cookies', 'Qué datos se tratan al visitar NetworkedAsociados y qué servicios de terceros intervienen.', f'''
<h2>Datos que recibo</h2><p>Este sitio no tiene formularios de registro ni guarda datos personales en un servidor propio. Cuando me escribes por WhatsApp o Telegram, esos datos se tratan dentro de esas plataformas según sus propias políticas.</p>
<h2>Servicios de terceros</h2><ul><li>Google Fonts, para cargar las tipografías.</li><li>YouTube (modo de privacidad mejorada), solo cuando decides reproducir un video.</li><li>Las imágenes de algunos análisis se cargan desde los servidores de Blogger (Google).</li><li>Herramienta de analítica: {P("indica si usarás Google Analytics u otra; hoy no hay ninguna instalada")}.</li></ul>
<h2>Cookies</h2><p>El sitio no instala cookies propias. Algunos servicios de terceros pueden hacerlo cuando interactúas con ellos, por ejemplo al reproducir un video. El buscador interno no guarda tus búsquedas.</p>
<h2>Enlaces externos</h2><p>Los enlaces a brokers, empresas de fondeo y redes sociales llevan a sitios con sus propias políticas de privacidad.</p>
<h2>Responsable y contacto</h2><p>{AUTOR}. Correo: {P("correo electrónico para temas de privacidad")}.</p>'''),
     'condiciones': ('Condiciones de uso', 'Condiciones para usar el contenido de NetworkedAsociados.', f'''
<h2>Uso del contenido</h2><p>Puedes leer, compartir y enlazar el contenido citando la fuente. No está permitido copiarlo completo ni presentarlo como propio.</p>
<h2>Sin garantía de resultados</h2><p>{DISCLAIMER}</p>
<h2>Productos propios</h2><p>El libro y las aplicaciones tienen sus propias condiciones de compra o uso, indicadas en cada página.</p>
<h2>Cambios</h2><p>Estas condiciones pueden actualizarse. Última revisión: {fecha(date.today().isoformat())}.</p>'''),
     'afiliados': ('Enlaces de afiliado y conflictos de interés', 'Cómo funcionan los enlaces de afiliado de NetworkedAsociados y qué relaciones comerciales existen.', f'''
<h2>Cómo funcionan</h2><p>Algunos botones llevan un código de afiliado y aparecen marcados con la etiqueta «afiliado». Si te registras con ellos, recibo un incentivo sin costo adicional para ti.</p>
<h2>Relaciones actuales</h2><ul>{"".join(f"<li>{esc(e['nombre'])}</li>" for e in EMP if e.get("afiliado"))}</ul>
<p>Con Bridge Markets ProFirm trabajo además como equipo: acompaño a quienes se unen a través de mi enlace.</p>
<h2>Independencia</h2><p>Tener un enlace de afiliado no cambia mis calificaciones. Bridge Markets llegó a tener 1/5 en mi análisis original y sigue «En observación». Si una empresa con la que tengo relación comercial incumple, lo publico.</p>
<p>Otras relaciones o patrocinios: {P("declara aquí patrocinios o pagos adicionales, si existen")}.</p>'''),
     'metodologia': ('Cómo califico: metodología y criterios de riesgo', 'Criterios con los que NetworkedAsociados evalúa brokers y empresas de fondeo, y cómo asigna niveles de riesgo.', f'''
<h2>Qué evalúo</h2><p>El mismo criterio para brokers, cuentas de fondeo y cualquier proyecto nuevo:</p>
<ul><li><b>Trayectoria:</b> tiempo operando y presencia documentada.</li><li><b>Transparencia operativa:</b> claridad de reglas, condiciones y comunicación.</li><li><b>Experiencia documentada:</b> lo que viví directamente o se reportó públicamente.</li><li><b>Soporte y condiciones:</b> atención, retiros y disponibilidad de información.</li></ul>
<h2>Escala de calificación</h2><ul><li>5/5 · Excelente</li><li>4/5 · Buena</li><li>3/5 · En observación</li><li>2/5 · No recomendada</li><li>1/5 · Evitar</li></ul>
<p>Las calificaciones pueden cambiar si una empresa corrige problemas, compensa a los afectados o modifica sus condiciones. Cuando cambia, explico qué pasó.</p>
<h2 id="riesgo">Niveles de riesgo</h2><ul><li><b>Riesgo bajo:</b> sin incumplimientos en mi experiencia y con trayectoria verificable.</li><li><b>Riesgo medio:</b> puntos pendientes de confirmar o cambios recientes que sigo de cerca.</li><li><b>Riesgo alto:</b> incumplimientos documentados, cierre o señales graves.</li></ul>
<h2>Tipos de evidencia</h2><p>Cada ficha indica su base: experiencia personal, experiencia documentada con pruebas o video, seguimiento de la comunidad o reportes de traders. Una mala experiencia no equivale por sí sola a una conclusión de fraude.</p>'''),
    }
    for slug, (t, desc, txt) in legal.items():
        out = f'/legal/{slug}.html'; b = rel(out)
        body = f'<main class="nx">{shead(b, "legal", esc(t), esc(desc), [("Inicio", ""), ("Legal", None)])}<section class="nx-wrap sec"><div class="prose">{txt}</div></section></main>'
        write(out, layout(out, f'{t} | NetworkedAsociados', desc, body, ld=[crumbs_ld([("Inicio", ""), (t, None)])])); sitemap.append((out, date.today().isoformat()))
        index.append(dict(t=t, s='Legal', d=desc, k='', u=out.lstrip('/')))

    # ---- páginas internas (análisis, artículos) con el diseño nuevo ----
    for p in PAGS:
        out = p['ruta']; b = rel(out)
        raw = open(os.path.join(ROOT, 'contenido', out.lstrip('/')), encoding='utf-8').read()
        sec = p['seccion']; e = EMPI.get(p.get('empresa'))
        crumbs = [("Inicio", "")] + ([(SECTION_NAME[sec], SECTION_URL[sec])] if sec in SECTION_URL and SECTION_URL[sec] != out.lstrip('/') else []) + [(e['nombre'] if e else clean_title(p['titulo']), None)]
        art = ARTICULOS.get(out) or auto_article(raw, p)
        h = art['hero']; caps = art['caps']
        html_caps = BL.chapters(caps, b)
        html_caps = html_caps.replace('{{ALERTAS}}', '<div class="a-alerts">' + ''.join(alert(x, b) for x in EMP if x['zona'] == 'peligro') + '</div>')
        for tipo in ('broker', 'fondeo'):
            html_caps = html_caps.replace('{{CARDS:%s}}' % tipo, '<div class="cards">' + ''.join(card(x, b) for x in EMP if x['zona'] == 'catalogo' and x['tipo'] == tipo) + '</div>')
        mins = max(2, round(len(re.sub(r'<[^>]+>', ' ', html_caps).split()) / 200))
        hero = art_hero(p, e, h, b, crumbs, mins)
        sticky = ''
        aff = next((x for x in h.get('botones', []) if len(x) > 3 and x[3] == 'afiliado'), None)
        if aff:
            sticky = f'<div class="a-sticky" hidden><div class="nx-wrap"><span><b>{esc(e["nombre"] if e else h["titulo"])}</b>{f" · {cal(e)}" if e and e.get("calificacion") else ""}</span>{BL.btn(aff, b)}</div></div>'
        rel_items = [x for x in PAGS if x['ruta'] != out and x['seccion'] == sec][:3]
        if len(rel_items) < 3: rel_items += [x for x in PAGS if x['ruta'] != out and x not in rel_items and x['seccion'] != 'sobre'][:3 - len(rel_items)]
        share_u = canon(out)
        after = f'''<section class="nx-wrap after">
<div class="share"><span>Compartir:</span><a class="btn b-wa b-sm" href="https://wa.me/?text={esc(share_u)}" target="_blank" rel="noopener">WhatsApp</a><a class="btn b-tg b-sm" href="https://t.me/share/url?url={esc(share_u)}" target="_blank" rel="noopener">Telegram</a><a class="btn b-ghost b-sm" href="https://www.facebook.com/sharer/sharer.php?u={esc(share_u)}" target="_blank" rel="noopener">Facebook</a><button class="btn b-ghost b-sm" data-copy>Copiar enlace</button></div>
{follow_box(b, "¿Te sirvió? Sígueme", "Te aviso apenas publique un análisis nuevo o salga una alerta.", compact=True)}
<div><span class="eyebrow">Sigue investigando</span><div class="cards" style="margin-top:14px">{"".join(post_card(x, b) for x in rel_items)}</div></div>
</section>'''
        body = f'''<div class="a-prog" aria-hidden="true"><i></i></div><main class="nx art">{hero}
<div class="nx-wrap a-layout">{BL.toc(caps) if len(caps) > 2 else "<div></div>"}<div class="a-body">{html_caps}
<p class="a-disc">Contenido informativo basado en mi experiencia y en información pública. No es asesoría financiera. <a href="{b}legal/metodologia.html">Cómo califico</a> · <a href="{b}legal/afiliados.html">Enlaces de afiliado</a></p></div></div>
{after}</main>{sticky}'''
        img = absimg(h.get('img') or h.get('cover') or h.get('foto')) or resize(first_img(raw), 1200)
        ld = [crumbs_ld([(t, u) for t, u in crumbs]),
              {"@context": "https://schema.org", "@type": "Article", "headline": clean_title(p['titulo'])[:110], "description": p['descripcion'],
               "datePublished": p['publicado'], "dateModified": p['actualizado'], "inLanguage": "es", "mainEntityOfPage": canon(out),
               "author": {"@type": "Person", "name": AUTOR, "url": DOM + '/p/sobre-mi.html'},
               "publisher": {"@type": "Organization", "name": "NetworkedAsociados", "logo": {"@type": "ImageObject", "url": DOM + '/assets/logo.png'}},
               **({"image": img} if img else {})}]
        if p['seccion'] == 'sobre': ld[1] = {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": {"@type": "Person", "name": AUTOR, "url": canon(out), "image": img, "sameAs": ORG["sameAs"]}}
        ct = clean_title(p["titulo"])
        title = ct + ('' if ':' in ct else (': análisis y opinión' if e and e['zona'] == 'catalogo' else (': alerta y experiencia' if e else ''))) + ' | NetworkedAsociados'
        cur = {'brokers': 'brokers', 'fondeo': 'fondeo', 'peligro': 'peligro', 'contenido': 'contenido', 'libro': 'libro', 'apps': 'apps', 'sobre': 'sobre'}[sec]
        secc = 'sec-' + (sec if sec in ('brokers', 'fondeo', 'peligro', 'contenido', 'libro', 'apps') else 'contenido')
        write(out, layout(out, title, p['descripcion'], body, sec=secc, cur=cur, ld=ld, img=img, ogtype='article'))
        sitemap.append((out, p['actualizado']))
        index.append(dict(t=clean_title(p['titulo']), s=SECTION_NAME.get(sec, ''), d=p['descripcion'][:120], k=p['categoria'] + ' ' + (e['nombre'] if e else '') + ' ' + h['titulo'], u=url_of(out), f=bool(e)))

    # índice de búsqueda: empresas y secciones
    for e in EMP:
        index.insert(0, dict(t=e['nombre'], s='Zona de peligro' if e['zona'] == 'peligro' else ('Broker' if e['tipo'] == 'broker' else 'Empresa de fondeo'),
                             d=f'{e["estado"]} · ' + (f'{e["calificacion"]:g}/5' if e.get('calificacion') else 'sin calificación'), k=e['resumen'], u=url_of(e['analisis']), f=True))
    for k in ('brokers', 'fondeo', 'peligro', 'contenido', 'libro', 'apps', 'comunidad'):
        index.append(dict(t=SECTION_NAME[k], s='Sección', d=NAVSUB.get(k, 'Redes y canales'), k='', u=SECTION_URL[k]))
    seen, idx2 = set(), []
    for x in index:
        if (x['t'], x['u']) in seen: continue
        seen.add((x['t'], x['u'])); idx2.append(x)
    json.dump(idx2, open(os.path.join(OUT, 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    # redirecciones (las URL viejas apuntan a la nueva ubicación)
    for old, new in REDIR.items():
        b = rel(old); target = b + new.lstrip('/')
        write(old, f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Redirigiendo…</title><link rel="canonical" href="{DOM}{new}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={target}"></head><body><p>Esta página se movió. <a href="{target}">Continuar</a>.</p><script>location.replace("{target}")</script></body></html>')

    # 404
    body = f'''<main class="nx"><section class="shead"><canvas class="nx-net" aria-hidden="true"></canvas><div class="nx-wrap" style="padding-block:80px">
<span class="eyebrow">Error 404</span><h1>Esta página no existe</h1><p class="lead">Puede que la haya movido o eliminado. Búscala o vuelve al inicio.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:22px"><button class="btn b-acc" data-search>Buscar en el sitio</button><a class="btn b-ghost" href="/">Ir al inicio</a></div></div></section></main>'''
    p404 = layout('/404.html', 'Página no encontrada | NetworkedAsociados', 'La página que buscas no existe.', body, robots='noindex')
    write('/404.html', p404.replace('data-base="./"', 'data-base="/"').replace('href="./', 'href="/').replace('src="./', 'src="/'))

    # sitemap y robots
    sm = ''.join(f'<url><loc>{DOM}{u.replace(" ", "%20")}</loc><lastmod>{d}</lastmod></url>\n' for u, d in sitemap)
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {DOM}/sitemap.xml\n')
    print(f'Listo: {len(sitemap)} páginas en el sitemap, {len(REDIR)} redirecciones, {len(idx2)} entradas en el buscador.')

if __name__ == '__main__':
    build()
