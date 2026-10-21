"""Convierte el HTML original de Blogger en bloques limpios (sin estilos viejos).

Bloques: h2, h3, p, list, quote, button, image, video.
Los enlaces dentro de los párrafos se conservan con su dirección original.
"""
import re, html
from html.parser import HTMLParser

BLOCK = {'div', 'section', 'article', 'header', 'footer', 'main', 'aside', 'nav', 'p', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5',
         'blockquote', 'table', 'tr', 'td', 'th', 'figure', 'figcaption', 'details', 'summary', 'form', 'center', 'dl', 'dt', 'dd'}
SKIP = {'script', 'style', 'noscript', 'svg', 'button', 'input', 'select', 'textarea', 'head', 'title'}
VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'source', 'iframe', 'wbr'}

def yt_id(src):
    m = re.search(r'(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})', src or '')
    return m.group(1) if m else None

def yt_list(src):
    m = re.search(r'[?&]list=([\w-]+)', src or '')
    return m.group(1) if m else None

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.blocks, self.buf, self.skip = [], [], [], 0
        self.link = None; self.link_text = []; self.buf_links = 0; self.buf_plain = []
        self.title = None

    # --- utilidades ---
    def ctx(self):
        for t in reversed(self.stack):
            if t in ('h1', 'h2', 'h3', 'h4', 'h5', 'li', 'blockquote', 'dt', 'summary', 'th'): return t
        return 'p'

    def flush(self):
        raw = ''.join(self.buf); plain = re.sub(r'\s+', ' ', ''.join(self.buf_plain)).strip()
        self.buf, self.buf_plain = [], []
        links = self.buf_links; self.buf_links = 0
        if not plain: return
        text = re.sub(r'\s+', ' ', raw).strip()
        kind = self.ctx()
        if kind == 'h1':
            if not self.title: self.title = plain
            return
        if kind in ('h2',): self.blocks.append({'t': 'h2', 'text': plain}); return
        if kind in ('h3', 'h4', 'h5', 'dt', 'summary', 'th'): self.blocks.append({'t': 'h3', 'text': plain}); return
        if kind == 'li': self.blocks.append({'t': 'li', 'html': text}); return
        if kind == 'blockquote': self.blocks.append({'t': 'quote', 'html': text}); return
        # párrafo que es solo un enlace -> botón
        m = re.fullmatch(r'<a href="([^"]+)">(.+?)</a>', text)
        if m and links == 1 and len(plain) < 70:
            self.blocks.append({'t': 'button', 'href': html.unescape(m.group(1)), 'text': plain}); return
        self.blocks.append({'t': 'p', 'html': text})

    # --- parser ---
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.skip or tag in SKIP:
            if tag not in VOID: self.skip += 1
            return
        if tag in BLOCK: self.flush()
        if tag == 'br':
            self.buf.append(' '); self.buf_plain.append(' '); return
        if tag == 'img':
            src = a.get('src', '')
            w = a.get('width', '')
            if src and not src.startswith('data:') and not (w.isdigit() and int(w) < 60):
                self.flush(); self.blocks.append({'t': 'image', 'src': src, 'alt': a.get('alt', '')})
            return
        if tag == 'iframe':
            src = a.get('src', '') or a.get('data-src', '')
            vid, lst = yt_id(src), yt_list(src)
            if vid or lst:
                self.flush(); self.blocks.append({'t': 'video', 'id': vid, 'list': lst})
            return
        if tag == 'a':
            href = a.get('href', '')
            self.link = href if href and not href.startswith('javascript') else None
            self.link_text = []
            # enlace a video de YouTube suelto
            return
        if tag not in VOID: self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.skip:
            if tag in SKIP or True:
                if tag not in VOID: self.skip -= 1
            return
        if tag == 'a':
            t = ''.join(self.link_text)
            if self.link and t.strip():
                h = self.link if self.link.startswith(('http', '/', '#', 'mailto:', 'tel:')) else self.link
                self.buf.append(f'<a href="{html.escape(h, quote=True)}">{html.escape(t.strip())}</a>' if not h.startswith('#') else html.escape(t))
                if not h.startswith('#'): self.buf_links += 1
            else:
                self.buf.append(html.escape(t))
            self.buf_plain.append(t)
            self.link = None; self.link_text = []
            return
        if tag in BLOCK: self.flush()
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag: pass
        if tag in ('strong', 'b'): pass

    def handle_data(self, d):
        if self.skip: return
        if self.link is not None:
            self.link_text.append(d); return
        self.buf.append(html.escape(d)); self.buf_plain.append(d)

def convert(raw):
    raw = re.sub(r'<!--[\s\S]*?-->', '', raw)
    p = P(); p.feed(raw); p.flush()
    out, seen_img = [], set()
    for b in p.blocks:
        # agrupar viñetas en listas
        if b['t'] == 'li':
            if out and out[-1]['t'] == 'list': out[-1]['items'].append(b['html'])
            else: out.append({'t': 'list', 'items': [b['html']]})
            continue
        if b['t'] == 'button':
            if out and out[-1]['t'] == 'buttons': out[-1]['items'].append(b)
            else: out.append({'t': 'buttons', 'items': [b]})
            continue
        if b['t'] == 'image':
            key = re.sub(r'/s\d+[^/]*/', '/', b['src'])
            if key in seen_img: continue
            seen_img.add(key)
        if b['t'] == 'video':
            if any(x['t'] == 'video' and x.get('id') == b.get('id') and x.get('list') == b.get('list') for x in out): continue
        out.append(b)
    return p.title, out
