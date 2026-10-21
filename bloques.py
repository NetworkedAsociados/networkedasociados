"""Bloques de contenido para los artículos de NetworkedAsociados.

Cada artículo (ver articulos.py) es una lista de capítulos. Cada capítulo tiene bloques:
textos, cifras, tarjetas, pasos, videos, botones… Este archivo los convierte en HTML
con el diseño del sitio. No necesitas tocarlo para escribir un artículo nuevo.
"""
import html as H, re

esc = H.escape

# ---------------- constructores (lo que usas en articulos.py) ----------------
def cap(id, kicker, titulo, *bloques, tono=None):
    """Capítulo: aparece en el índice lateral."""
    return {'t': 'cap', 'id': id, 'kicker': kicker, 'titulo': titulo, 'bloques': list(bloques), 'tono': tono}
def P(html): return {'t': 'p', 'html': html}
def Grande(html): return {'t': 'big', 'html': html}
def Cifras(*items): return {'t': 'stats', 'items': items}          # (valor, etiqueta[, tono])
def Lista(*items, tono='ok'): return {'t': 'checks', 'items': items, 'tono': tono}
def ProsContras(pros, contras, t1='A favor', t2='A considerar'): return {'t': 'pc', 'pros': pros, 'contras': contras, 't1': t1, 't2': t2}
def Tarjetas(*items, cols=3): return {'t': 'tiles', 'items': items, 'cols': cols}   # (icono, título, texto[, enlace])
def Pasos(*items): return {'t': 'steps', 'items': items}            # (título, texto)
def Ficha(*items): return {'t': 'specs', 'items': items}            # (clave, valor)
def Nota(tono, titulo, html): return {'t': 'note', 'tono': tono, 'titulo': titulo, 'html': html}   # tono: info, ok, warn, bad
def Video(id, titulo): return {'t': 'video', 'id': id, 'titulo': titulo}
def Videos(*items): return {'t': 'videos', 'items': items}          # (id, título)
def Playlist(lista, titulo): return {'t': 'playlist', 'list': lista, 'titulo': titulo}
def Cita(texto, autor=''): return {'t': 'quote', 'texto': texto, 'autor': autor}
def Botones(*items): return {'t': 'btns', 'items': items}           # (texto, enlace, estilo[, 'afiliado'])
def Llamado(titulo, texto, *botones, nota=''): return {'t': 'cta', 'titulo': titulo, 'texto': texto, 'btns': botones, 'nota': nota}
def Planes(*items): return {'t': 'plans', 'items': items}           # dict(nombre, etiqueta, puntos, destacado)
def Preguntas(*items): return {'t': 'faq', 'items': items}          # (pregunta, respuesta)
def Versus(t1, t2, *filas): return {'t': 'vs', 't1': t1, 't2': t2, 'filas': filas}
def Imagen(src, alt, pie=''): return {'t': 'img', 'src': src, 'alt': alt, 'pie': pie}
def Chat(*lineas): return {'t': 'chat', 'lineas': lineas}           # ('bot'|'yo', texto)
def Codigo(etiqueta, valor): return {'t': 'code', 'etiqueta': etiqueta, 'valor': valor}
def HTML(html): return {'t': 'raw', 'html': html}

# ---------------- render ----------------
INTERNAL = ('https://www.networkedasociados.com', 'http://www.networkedasociados.com', 'https://networkedasociados.com')
MOVED = {'/p/bridge-profirm.html': '/2026/06/bridgeprofirm.html', '/2026/04/copytrade.html': '/brokers/'}

def link(href, b):
    """Enlaces internos relativos; los externos quedan iguales."""
    for d in INTERNAL:
        if href.startswith(d): href = href[len(d):] or '/'
    if href.startswith('/'):
        href = MOVED.get(href, href)
        return b + href.lstrip('/').replace(' ', '%20')
    return href

def fix_links(s, b):
    return re.sub(r'href="([^"]+)"', lambda m: f'href="{esc(link(H.unescape(m.group(1)), b), quote=True)}"' + (' target="_blank" rel="noopener"' if m.group(1).startswith('http') and 'networkedasociados.com' not in m.group(1) else ''), s)

def btn(item, b):
    text, href, style = item[0], item[1], item[2] if len(item) > 2 else 'b-acc'
    aff = len(item) > 3 and item[3] == 'afiliado'
    ext = href.startswith('http') and 'networkedasociados.com' not in href
    attrs = (' target="_blank" rel="' + ('sponsored noopener' if aff else 'noopener') + '"') if ext else ''
    tag = ' <span class="aff-tag">afiliado</span>' if aff else ''
    return f'<a class="btn {style}" href="{esc(link(href, b), quote=True)}"{attrs}>{esc(text)}{tag}</a>'

def yt(vid, title):
    return f'<button class="yt" data-id="{esc(vid)}" aria-label="Reproducir: {esc(title)}"><span class="play" aria-hidden="true"></span><span class="cap">{esc(title)}</span></button>'

def count_attr(v):
    if re.fullmatch(r'(19|20)\d\d', v): return ''
    m = re.match(r'^([^\d]*)([\d.,]+)(.*)$', v)
    if not m: return ''
    num = m.group(2).replace('.', '').replace(',', '.') if re.search(r'\d\.\d{3}', m.group(2)) else m.group(2).replace(',', '')
    try: float(num)
    except ValueError: return ''
    return f' data-count="{num}" data-pre="{esc(m.group(1))}" data-suf="{esc(m.group(3))}" data-fmt="{esc(m.group(2))}"'

def block(x, b):
    t = x['t']; F = lambda s: fix_links(s, b)
    if t == 'p': return f'<p>{F(x["html"])}</p>'
    if t == 'big': return f'<p class="a-big">{F(x["html"])}</p>'
    if t == 'stats':
        cells = ''.join(f'<div class="a-stat t-{s[2] if len(s) > 2 else "acc"}"><b{count_attr(s[0])}>{esc(s[0])}</b><span>{esc(s[1])}</span></div>' for s in x['items'])
        return f'<div class="a-stats">{cells}</div>'
    if t == 'checks':
        return f'<ul class="a-checks t-{x["tono"]}">' + ''.join(f'<li>{F(i)}</li>' for i in x['items']) + '</ul>'
    if t == 'pc':
        L = lambda a: ''.join(f'<li>{F(i)}</li>' for i in a)
        return f'<div class="a-pc"><div class="pro"><h3>{esc(x["t1"])}</h3><ul>{L(x["pros"])}</ul></div><div class="con"><h3>{esc(x["t2"])}</h3><ul>{L(x["contras"])}</ul></div></div>'
    if t == 'tiles':
        out = []
        for it in x['items']:
            ico, tit, txt = it[0], it[1], it[2]; href = it[3] if len(it) > 3 else None
            inner = f'{f"<span class=ico>{ico}</span>" if ico else ""}<h3>{esc(tit)}</h3>{f"<p>{F(txt)}</p>" if txt else ""}'
            out.append(f'<a class="a-tile" href="{esc(link(href, b), quote=True)}">{inner}</a>' if href else f'<div class="a-tile">{inner}</div>')
        return f'<div class="a-tiles c{x["cols"]}">{"".join(out)}</div>'
    if t == 'steps':
        return '<ol class="a-steps">' + ''.join(f'<li><span class="n">{i+1:02d}</span><div><h3>{esc(s[0])}</h3><p>{F(s[1])}</p></div></li>' for i, s in enumerate(x['items'])) + '</ol>'
    if t == 'specs':
        return '<dl class="a-specs">' + ''.join(f'<div><dt>{esc(k)}</dt><dd>{F(v)}</dd></div>' for k, v in x['items']) + '</dl>'
    if t == 'note':
        return f'<aside class="a-note t-{x["tono"]}">{f"<b>{esc(x["titulo"])}</b>" if x["titulo"] else ""}<p>{F(x["html"])}</p></aside>'
    if t == 'video': return f'<div class="a-video">{yt(x["id"], x["titulo"])}<a class="a-ytlink" href="https://youtu.be/{esc(x["id"])}" target="_blank" rel="noopener">Abrir en YouTube ↗</a></div>'
    if t == 'videos': return '<div class="a-videos">' + ''.join(yt(i, tt) for i, tt in x['items']) + '</div>'
    if t == 'playlist':
        return (f'<div class="a-video"><button class="yt" data-list="{esc(x["list"])}" aria-label="Reproducir: {esc(x["titulo"])}"><span class="play" aria-hidden="true"></span>'
                f'<span class="cap">{esc(x["titulo"])}</span></button></div>')
    if t == 'quote':
        return f'<figure class="a-quote"><blockquote>{esc(x["texto"])}</blockquote>{f"<figcaption>{esc(x["autor"])}</figcaption>" if x["autor"] else ""}</figure>'
    if t == 'btns': return '<div class="a-btns">' + ''.join(btn(i, b) for i in x['items']) + '</div>'
    if t == 'cta':
        return (f'<div class="a-cta"><canvas class="nx-net" aria-hidden="true"></canvas><div class="in"><h3>{esc(x["titulo"])}</h3><p>{F(x["texto"])}</p>'
                f'<div class="a-btns">{"".join(btn(i, b) for i in x["btns"])}</div>{f"<small>{F(x["nota"])}</small>" if x["nota"] else ""}</div></div>')
    if t == 'plans':
        out = ''
        for pl in x['items']:
            out += (f'<div class="a-plan{" hot" if pl.get("destacado") else ""}">{f"<span class=tag>{esc(pl["etiqueta"])}</span>" if pl.get("etiqueta") else ""}'
                    f'<h3>{esc(pl["nombre"])}</h3><ul>{"".join(f"<li>{esc(i)}</li>" for i in pl["puntos"])}</ul></div>')
        return f'<div class="a-plans">{out}</div>'
    if t == 'faq':
        return '<div class="a-faq">' + ''.join(f'<details><summary>{esc(q)}</summary><p>{F(a)}</p></details>' for q, a in x['items']) + '</div>'
    if t == 'vs':
        rows = ''.join(f'<tr><td>{esc(l)}</td><td>{esc(r)}</td></tr>' for l, r in x['filas'])
        return f'<div class="a-vs"><table><thead><tr><th>{esc(x["t1"])}</th><th>{esc(x["t2"])}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    if t == 'img':
        return f'<figure class="a-img"><img src="{esc(x["src"])}" alt="{esc(x["alt"])}" loading="lazy" decoding="async">{f"<figcaption>{esc(x["pie"])}</figcaption>" if x["pie"] else ""}</figure>'
    if t == 'chat':
        return '<div class="a-chat"><div class="bar"><span class="av">BN</span><div><b>BitacoraNetBot</b><small>bot · en línea</small></div></div><div class="msgs">' + ''.join(
            f'<p class="m {w}">{esc(s)}</p>' for w, s in x['lineas']) + '</div></div>'
    if t == 'code':
        return f'<div class="a-code"><span>{esc(x["etiqueta"])}</span><b>{esc(x["valor"])}</b><button class="btn b-ghost b-sm" data-copytext="{esc(x["valor"])}">Copiar</button></div>'
    if t == 'raw': return F(x['html'])
    raise ValueError('Bloque desconocido: ' + t)

def chapters(caps, b):
    out = []
    for i, c in enumerate(caps):
        tone = f' t-{c["tono"]}' if c.get('tono') else ''
        inner = ''.join(block(x, b) for x in c['bloques'])
        out.append(f'<section class="a-chap rv{tone}" id="{c["id"]}"><header><span class="num" aria-hidden="true">{i+1:02d}</span>'
                   f'<div><span class="kick">{esc(c["kicker"])}</span><h2>{esc(c["titulo"])}</h2></div></header>{inner}</section>')
    return ''.join(out)

def toc(caps):
    return '<nav class="a-toc" aria-label="En esta página"><p>En esta página</p><ol>' + ''.join(
        f'<li><a href="#{c["id"]}"><span>{i+1:02d}</span>{esc(c["titulo"])}</a></li>' for i, c in enumerate(caps)) + '</ol></nav>'
