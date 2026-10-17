#!/usr/bin/env python3
"""Genera il sito statico di Riccardo Benotti in public/.

Uso: python3 src/build.py
Le puntate del filo stanno in data/filo.json (testo così come esce su LinkedIn,
con i grassetti Unicode). Le pagine fisse stanno in src/body_it.html e src/body_en.html.
"""
import json, html, re, os, unicodedata, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, PUB = ROOT / 'src', ROOT / 'public'
CFG = json.loads((ROOT / 'data' / 'config.json').read_text())
SITE = CFG['site'].rstrip('/')
LINKEDIN = 'https://www.linkedin.com/in/riccardo-benotti-0a0534362'

exec((SRC / 'filo_lib.py').read_text())  # unb, isbold, tohtml, EMO

MESI = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio',
        'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']


def data_it(iso):
    y, m, d = map(int, iso.split('-'))
    return f'{d} {MESI[m-1]} {y}'


def data_en(iso):
    y, m, d = map(int, iso.split('-'))
    return f'{d} {MONTHS[m-1]} {y}'


def typo(s):
    s = s.replace("'", '’').replace('"', '§')
    out, o = '', True
    for ch in s:
        if ch == '§':
            out += '“' if o else '”'
            o = not o
        else:
            out += ch
    return out


def puntata(p):
    titolo = html.escape(typo(unicodedata.normalize('NFC', unb(p['titolo']))), quote=False)
    paras = [EMO.sub('', typo(x)).strip() for x in p['testo'].split('\n') if x.strip()]
    paras_html = [f'<p>{tohtml(x)}</p>' for x in paras]
    plain = re.sub(r'<[^>]+>', '', paras_html[0]) if paras_html else ''
    return {**p, 'titolo_html': titolo, 'paras': paras_html, 'sommario': plain,
            'url': f'/filo/{p["data"]}/',
            'linkedin': f'https://www.linkedin.com/feed/update/urn:li:activity:{p["urn"]}/'}


def fonti_html(p):
    if not p.get('fonti'):
        return ''
    li = ''.join(f'<li><a href="{html.escape(u)}">{html.escape(t)}</a></li>' for t, u in p['fonti'])
    return f'<div class="fonti"><span class="label">Fonti</span><ul>{li}</ul></div>'


def meta_html(p):
    foto = f'<span>Foto {html.escape(p["credito"])}</span>' if p.get('credito') else ''
    return f'<div class="meta">{foto}<a href="{p["linkedin"]}">Leggi su LinkedIn</a></div>'


def figura(p, cls='foto', lazy=True):
    if not p.get('foto'):
        return ''
    from PIL import Image
    w, h = Image.open(PUB / 'img' / p['foto']).size
    alt = html.escape(p.get('alt') or p['sommario'][:120])
    return (f'<figure class="{cls}"><img src="/img/{p["foto"]}" width="{w}" height="{h}" alt="{alt}"'
            + (' loading="lazy"' if lazy else '') + '></figure>')


def home_items(puntate):
    out = []
    for k, p in enumerate(puntate[:3]):
        testa = (f'<time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time>'
                 f'<h3><a class="tit" href="{p["url"]}">{p["titolo_html"]}</a></h3>')
        if k == 0:
            corpo = (f'<div class="testo">{p["paras"][0]}</div>'
                     f'<details><summary>Continua a leggere</summary><div class="testo">{"".join(p["paras"][1:])}</div>'
                     f'{fonti_html(p)}{meta_html(p)}</details>')
        else:
            corpo = (f'<details><summary>Leggi la puntata</summary><div class="testo">{"".join(p["paras"])}</div>'
                     f'{fonti_html(p)}{meta_html(p)}</details>')
        cls = 'puntata ultima' if k == 0 else 'puntata'
        out.append(f'\n      <li class="{cls}">\n        <div class="corpo">{testa}{corpo}</div>\n        {figura(p, lazy=k > 0)}\n      </li>')
    return ''.join(out) + '\n    '


CSS_VER = None


def head(lang, title, desc, path, alt=None, og_type='website', jsonld=None, extra=''):
    url = SITE + path
    alts = ''
    if alt:
        for hl, hp in alt:
            alts += f'<link rel="alternate" hreflang="{hl}" href="{SITE + hp}">\n'
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, indent=1)}</script>\n' if jsonld else ''
    loc = 'it_IT' if lang == 'it' else 'en_GB'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
{alts}<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{loc}">
<meta property="og:site_name" content="Riccardo Benotti">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1B2336">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/newsreader-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={CSS_VER}">
{ld}{extra}</head>
<body>
'''


def nav(lang, home, switch):
    pre = '' if home else '/'
    if lang == 'it':
        voci = [('filo', 'Il filo del giorno'), ('profilo', 'Profilo'), ('libri', 'Libri'),
                ('scritti', 'Scritti e interventi'), ('ricerca', 'Ricerca'), ('contatti', 'Contatti')]
        base, aria, sw_lab, sw_title = '/', 'Sezioni', 'EN', 'English version'
    else:
        voci = [('profile', 'Profile'), ('books', 'Books'), ('writing', 'Writing and talks'),
                ('research', 'Research'), ('filo', 'Daily column'), ('contact', 'Contact')]
        base, aria, sw_lab, sw_title = '/en/', 'Sections', 'IT', 'Versione italiana'
        pre = '' if home else '/en/'
    li = ''.join(f'\n      <li><a class="link" href="{pre}#{a}">{t}</a></li>' for a, t in voci)
    hl = 'en' if lang == 'it' else 'it'
    li += f'\n      <li><a class="lang" href="{switch}" hreflang="{hl}" lang="{hl}" title="{sw_title}">{sw_lab}</a></li>'
    return f'''<nav class="nav" aria-label="{aria}">
  <div class="wrap">
    <a class="brand" href="{base}">Riccardo Benotti</a>
    <ul>{li}
    </ul>
  </div>
</nav>
'''


def person_ld():
    return {
        "@type": "Person", "@id": SITE + "/#riccardo-benotti", "name": "Riccardo Benotti",
        "url": SITE + "/", "image": SITE + "/img/riccardo-benotti-foto.jpg",
        "jobTitle": "Caposervizio",
        "description": "Giornalista professionista e autore italiano, caposervizio dell'agenzia SIR – Servizio Informazione Religiosa, accreditato presso la Sala Stampa della Santa Sede.",
        "worksFor": {"@type": "NewsMediaOrganization", "name": "SIR – Servizio Informazione Religiosa", "url": "https://www.agensir.it"},
        "memberOf": {"@type": "Organization", "name": "Commissione Film CEI", "url": "https://www.commissionefilmcei.it/"},
        "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "Dottorato di ricerca",
                          "educationalLevel": "Dottorato di ricerca in Scienze della comunicazione sociale", "dateCreated": "2025",
                          "recognizedBy": {"@type": "CollegeOrUniversity", "name": "Università Pontificia Salesiana"}},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Università Pontificia Salesiana"},
        "homeLocation": {"@type": "Place", "name": "Roma"},
        "nationality": {"@type": "Country", "name": "Italia"},
        "knowsAbout": ["Santa Sede", "Chiesa cattolica", "Giornalismo", "Intelligenza artificiale", "Comunicazione ecclesiale", "Vita religiosa"],
        "identifier": {"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0000-5747-2592"},
        "sameAs": ["https://orcid.org/0009-0000-5747-2592", LINKEDIN,
                   "https://www.edizionisanpaolo.it/autore/riccardo-benotti.aspx",
                   "https://www.agensir.it/author/r-benotti/"] + CFG.get('sameAs_extra', []),
    }


BOOKS = [
    ("Covid-19: preti in prima linea. Storie stra-ordinarie di chi ha dato la vita e di chi non si è arreso", "San Paolo", "2021", "9788892223813", 464),
    ("Viaggio nella vita religiosa. Interviste e incontri", "Libreria Editrice Vaticana", "2016", "9788820997304", 232),
    ("Viaggio nel New Journalism americano", "Aracne", "2009", "9788854822931", 143),
]


def ld_home():
    g = [person_ld(), {"@type": "WebSite", "@id": SITE + "/#sito", "url": SITE + "/", "name": "Riccardo Benotti",
                       "inLanguage": ["it", "en"], "publisher": {"@id": SITE + "/#riccardo-benotti"}}]
    for n, pub, y, isbn, pp in BOOKS:
        g.append({"@type": "Book", "name": n, "author": {"@id": SITE + "/#riccardo-benotti"},
                  "publisher": {"@type": "Organization", "name": pub}, "datePublished": y, "isbn": isbn,
                  "numberOfPages": pp, "inLanguage": "it"})
    g.append({"@type": "Thesis", "name": "Intelligenza artificiale e giornalismo. Un'indagine sui pro e contro di una possibile implementazione di sistemi IA nelle redazioni cattoliche della CEI e della Santa Sede",
              "author": {"@id": SITE + "/#riccardo-benotti"}, "datePublished": "2025", "inLanguage": "it",
              "inSupportOf": "Dottorato di ricerca in Scienze della comunicazione sociale",
              "sourceOrganization": {"@type": "CollegeOrUniversity", "name": "Università Pontificia Salesiana"}})
    return {"@context": "https://schema.org", "@graph": g}


def contatto(lang):
    email = CFG.get('email')
    if lang == 'it':
        if email:
            return f'Per presentazioni, incontri e collaborazioni: <a href="mailto:{email}">{email}</a>. Anche su <a href="{LINKEDIN}">LinkedIn</a>.'
        return f'Per presentazioni, incontri e collaborazioni è possibile scrivergli su <a href="{LINKEDIN}">LinkedIn</a>.'
    if email:
        return f'For talks, events and collaborations: <a href="mailto:{email}">{email}</a>. Also on <a href="{LINKEDIN}">LinkedIn</a>.'
    return f'For talks, events and collaborations, you can reach him on <a href="{LINKEDIN}">LinkedIn</a>.'


def footer(lang):
    f = (SRC / f'footer_{lang}.html').read_text()
    return f.replace('{{CONTATTO}}', contatto(lang))


COPY_JS = '''<script>
document.querySelectorAll('[data-copia]').forEach(function (b) {
  b.addEventListener('click', function () {
    var t = document.getElementById(b.getAttribute('data-copia')).innerText;
    var done = function () { var o = b.textContent; b.textContent = b.getAttribute('data-ok'); setTimeout(function () { b.textContent = o; }, 1800); };
    if (navigator.clipboard) { navigator.clipboard.writeText(t).then(done, function () {}); }
  });
});
</script>
'''


def write(path, content):
    p = PUB / path.lstrip('/')
    if path.endswith('/'):
        p = p / 'index.html'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def main():
    global CSS_VER
    css = (SRC / 'style.css').read_text()
    (PUB / 'style.css').write_text(css)
    import hashlib
    CSS_VER = hashlib.md5(css.encode()).hexdigest()[:8]

    puntate = [puntata(p) for p in sorted(json.loads((ROOT / 'data' / 'filo.json').read_text()),
                                          key=lambda x: x['data'], reverse=True)]
    oggi = datetime.date.today().isoformat()
    urls = []

    # Home IT
    body = (SRC / 'body_it.html').read_text().replace('{{FILO}}', home_items(puntate)).replace('{{CONTATTO}}', contatto('it'))
    page = head('it', 'Riccardo Benotti – Giornalista e autore',
                'Riccardo Benotti, giornalista professionista e autore, caposervizio del SIR – Servizio Informazione Religiosa. Chiesa, Santa Sede, comunicazione e intelligenza artificiale.',
                '/', alt=[('it', '/'), ('en', '/en/'), ('x-default', '/')], og_type='profile', jsonld=ld_home())
    page += nav('it', True, '/en/') + body + footer('it') + COPY_JS + '</body>\n</html>\n'
    write('/', page); urls.append(('/', oggi))

    # Home EN
    body = (SRC / 'body_en.html').read_text()
    ultime = ''.join(f'<li><time class="mono" datetime="{p["data"]}">{data_en(p["data"])}</time> <a href="{p["url"]}" hreflang="it" lang="it">{p["titolo_html"]}</a></li>' for p in puntate[:5])
    body = body.replace('{{FILO_EN}}', ultime).replace('{{CONTATTO}}', contatto('en'))
    ld = {"@context": "https://schema.org", "@graph": [{**person_ld(), "jobTitle": "Senior editor",
          "description": "Italian journalist and author, senior editor at SIR – Servizio Informazione Religiosa, the news agency of the Italian Bishops' Conference, accredited to the Holy See Press Office."}]}
    page = head('en', 'Riccardo Benotti – Journalist and author',
                'Riccardo Benotti is an Italian journalist and author, senior editor at SIR, the news agency of the Italian Bishops’ Conference. The Pope, the Holy See, the Church, and AI in journalism.',
                '/en/', alt=[('it', '/'), ('en', '/en/'), ('x-default', '/')], og_type='profile', jsonld=ld)
    page += nav('en', True, '/') + body + footer('en') + COPY_JS + '</body>\n</html>\n'
    write('/en/', page); urls.append(('/en/', oggi))

    # Archivio filo
    righe = ''.join(f'\n      <li><time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time><a href="{p["url"]}">{p["titolo_html"]}</a></li>' for p in puntate)
    body = f'''<div class="wrap">
  <main class="pagina">
    <a class="torna" href="/#filo">← Torna alla home</a>
    <span class="label gold">Rubrica quotidiana</span>
    <h1>Leone, <em>il filo del giorno</em>: tutte le puntate</h1>
    <p>Ogni giorno una lettura delle notizie e degli appuntamenti di Leone XIV, tenuti insieme da un solo filo. La rubrica esce anche su <a href="{LINKEDIN}">LinkedIn</a>.</p>
    <ol class="archivio">{righe}
    </ol>
  </main>
</div>
'''
    page = head('it', 'Leone, il filo del giorno – Archivio | Riccardo Benotti',
                'Tutte le puntate di «Leone, il filo del giorno», la rubrica quotidiana di Riccardo Benotti sulle notizie e gli appuntamenti di Leone XIV.',
                '/filo/', jsonld={"@context": "https://schema.org", "@type": "CollectionPage", "name": "Leone, il filo del giorno",
                                  "url": SITE + "/filo/", "author": {"@id": SITE + "/#riccardo-benotti"}, "inLanguage": "it"})
    page += nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n'
    write('/filo/', page); urls.append(('/filo/', puntate[0]['data']))

    # Pagine puntate
    for i, p in enumerate(puntate):
        prec = puntate[i + 1] if i + 1 < len(puntate) else None
        succ = puntate[i - 1] if i > 0 else None
        vic = '<nav class="vicine">'
        vic += f'<a href="{prec["url"]}"><span class="label">← Puntata precedente</span>{prec["titolo_html"]}</a>' if prec else '<span></span>'
        vic += f'<a href="{succ["url"]}" style="text-align:right"><span class="label">Puntata successiva →</span>{succ["titolo_html"]}</a>' if succ else '<span></span>'
        vic += '</nav>'
        fig = figura(p, cls='foto-grande', lazy=False)
        if fig and p.get('credito'):
            fig = fig.replace('</figure>', f'<figcaption>Foto {html.escape(p["credito"])}</figcaption></figure>')
        body = f'''<div class="wrap">
  <main class="pagina">
    <a class="torna" href="/filo/">← Tutte le puntate</a>
    <article>
      <span class="label gold">Leone, il filo del giorno · <time datetime="{p["data"]}">{data_it(p["data"])}</time></span>
      <h1>{p["titolo_html"]}</h1>
      {fig}
      <div class="testo">{"".join(p["paras"])}</div>
      {fonti_html(p)}
      <div class="meta puntata-meta"><a href="{p["linkedin"]}">La puntata su LinkedIn</a></div>
    </article>
    {vic}
  </main>
</div>
'''
        art = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": unicodedata.normalize('NFC', unb(p['titolo']))[:110],
               "datePublished": p['data'], "inLanguage": "it", "url": SITE + p['url'],
               "author": {"@type": "Person", "@id": SITE + "/#riccardo-benotti", "name": "Riccardo Benotti", "url": SITE + "/"},
               "isPartOf": {"@type": "CreativeWorkSeries", "name": "Leone, il filo del giorno", "url": SITE + "/filo/"}}
        if p.get('foto'):
            art["image"] = SITE + '/img/' + p['foto']
        titolo_pag = re.sub(r'<[^>]+>', '', html.unescape(p['titolo_html']))
        page = head('it', f'{titolo_pag} | Leone, il filo del giorno', p['sommario'][:300], p['url'],
                    og_type='article', jsonld=art)
        if p.get('foto'):
            page = page.replace(f'{SITE}/img/og.jpg', f'{SITE}/img/{p["foto"]}').replace(
                '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n', '')
        page += nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n'
        write(p['url'], page); urls.append((p['url'], p['data']))

    # 404
    body = '''<div class="wrap"><main class="pagina"><span class="label gold">Errore 404</span>
    <h1>Pagina non trovata</h1><p>L’indirizzo potrebbe essere cambiato. Torna alla <a href="/">home</a> o all’<a href="/filo/">archivio del filo del giorno</a>.</p>
    <p lang="en">Page not found. Go to the <a href="/en/">English home page</a>.</p></main></div>
'''
    page = head('it', 'Pagina non trovata | Riccardo Benotti', 'Pagina non trovata.', '/404.html')
    page = page.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    write('/404.html', page + nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n')

    # sitemap e robots
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for u, d in urls:
        sm += f'  <url><loc>{SITE + u}</loc><lastmod>{d}</lastmod>'
        if u in ('/', '/en/'):
            sm += f'<xhtml:link rel="alternate" hreflang="it" href="{SITE}/"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/"/>'
        sm += '</url>\n'
    sm += '</urlset>\n'
    write('/sitemap.xml', sm)
    write('/robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'OK: {len(puntate)} puntate, {len(urls)} pagine in sitemap')


if __name__ == '__main__':
    main()
