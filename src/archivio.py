# Archivio di «Leone, il filo del giorno»: indice generale, pagine mensili,
# una pagina per puntata, feed RSS. Eseguito da build.py (usa le sue funzioni).
import re
from email.utils import format_datetime

SERIE = 'Leone, il filo del giorno'
INTRO = ('Ogni giorno, da dicembre 2025, una lettura delle notizie e degli appuntamenti di papa Leone XIV, '
         'tenuti insieme da un solo filo: udienze, viaggi, documenti, nomine, parole del Papa e della Santa Sede. '
         'La rubrica di Riccardo Benotti esce anche su LinkedIn.')


SEGNO = '<svg class="filo-segno" viewBox="0 0 320 44" width="320" height="44" aria-hidden="true" focusable="false"><path class="gom" d="M12.0 33.9 A16 16 0 1 1 28.0 6.1 A16 16 0 1 1 12.0 33.9 M21.4 35.6 Q8.6 29.5 4.9 16.0 M27.1 33.9 Q12.3 26.5 7.6 10.6 M31.4 30.5 Q16.4 23.0 11.6 6.9 M34.6 25.7 Q21.1 19.0 16.9 4.7 M35.8 20.2 Q25.0 15.8 22.6 4.4 M5.1 24.7 Q19.6 19.5 27.2 6.2 M8.1 30.0 Q23.9 24.6 31.9 10.0" pathLength="1"/><path class="coda" d="M25.5 35.0 C26.5 35.5 28.4 37.2 31.5 37.5 C34.6 37.9 38.2 37.8 44.0 37.0 C49.8 36.2 57.3 35.2 66.0 33.0 C74.7 30.8 85.7 25.8 96.0 24.0 C106.3 22.2 117.3 21.0 128.0 22.0 C138.7 23.0 148.7 28.2 160.0 30.0 C171.3 31.8 184.0 33.8 196.0 33.0 C208.0 32.2 220.3 27.2 232.0 25.0 C243.7 22.8 254.7 20.2 266.0 19.5 C277.3 18.8 291.3 20.1 300.0 21.0 C308.7 21.9 315.0 24.3 318.0 25.0" pathLength="1"/></svg>'
CHIUSA = '<svg class="filo-segno" viewBox="0 0 165 34" width="165" height="34" aria-hidden="true" focusable="false"><path d="M2.0 24.0 C6.7 23.4 20.0 20.3 30.0 20.5 C40.0 20.7 51.0 24.1 62.0 25.0 C73.0 25.9 86.0 26.0 96.0 26.0 C106.0 26.0 115.8 25.4 122.0 25.0 C128.2 24.6 130.5 24.7 133.4 23.8 C136.3 23.0 138.4 20.5 139.4 19.8"/><path d="M144.5 26.5 A11 11 0 1 1 155.5 7.5 A11 11 0 1 1 144.5 26.5 M151.2 27.7 Q142.2 23.5 139.7 14.0 M155.2 26.3 Q144.8 21.3 141.7 10.2 M158.3 23.8 Q147.9 18.8 144.8 7.7 M160.3 20.0 Q151.4 15.8 148.8 6.3 M140.2 21.3 Q150.4 17.5 155.9 8.1"/></svg>'

def _mese(iso):
    y, m = iso[:4], int(iso[5:7])
    return f'{MESI[m - 1]} {y}'


def _mese_url(iso):
    return f'/filo/{iso[:4]}/{iso[5:7]}/'


def _briciole(voci):
    vis = ' <span aria-hidden="true">›</span> '.join(
        f'<a href="{u}">{html.escape(t)}</a>' if u else f'<span aria-current="page">{html.escape(t)}</span>' for t, u in voci)
    ld = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, **({"item": SITE + u} if u else {})} for i, (t, u) in enumerate(voci)]}
    return f'<nav class="briciole" aria-label="Percorso">{vis}</nav>', ld


LEONE_LD = {"@type": "Person", "name": "Leone XIV", "alternateName": ["Papa Leone XIV", "Robert Francis Prevost"],
            "sameAs": ["https://www.wikidata.org/wiki/Q6109517", "https://it.wikipedia.org/wiki/Papa_Leone_XIV"]}


def _editore(url):
    h = url.split('/')[2]
    return {'press.vatican.va': 'Sala Stampa della Santa Sede', 'www.vatican.va': 'Santa Sede'}.get(h, h)


def titolo_seo(p):
    """Titolo per i motori di ricerca, entro ~70 caratteri: nome e data in testa, poi l'inizio del titolo (tagliato a un confine naturale). Il titolo intero resta nell'H1."""
    t = p['titolo_txt']
    pre = f'Papa Leone XIV, {data_it(p["data"])}: '
    cap = max(82 - len(pre), 30)
    frasi = re.split(r'(?<=[.!?”"])\s+(?=[A-ZÀ-Ý“"])', t)
    prima = frasi[0].rstrip('.')
    for f in frasi[1:]:
        if len(prima) >= 30:
            break
        if len(prima) + 2 + len(f) <= cap + 12:
            prima = prima + ': ' + f.rstrip('.') if not prima.endswith((':', '?', '!')) else prima + ' ' + f.rstrip('.')
    if len(prima) >= 20:
        t = prima
    if len(t) > cap:
        taglio = max((i for i in (t.rfind(sep, 0, cap + 1) for sep in (': ', '. ', ', ', ' – ', ' e ', ' ma ', ' per ', ' con ')) if i >= 16), default=None)
        t = t[:taglio] if taglio else t[:cap + 1].rsplit(' ', 1)[0]
        parole = t.split(' ')
        while len(parole) > 3 and re.fullmatch(r'(?i)(e|è|non|come|sono|sia|di|a|da|in|con|su|per|tra|fra|il|lo|la|le|i|gli|un|una|del|della|dei|delle|al|alla|ai|alle|nel|nella|che|ma|o)', parole[-1].strip(',;:')):
            parole.pop()
        t = ' '.join(parole).rstrip(',;:.–—-')
        if t.count('“') > t.count('”'):
            t = t.rstrip(' ,;:.–—-') + '…”'
        elif t.count('"') % 2:
            t = t.rstrip(' ,;:.–—-') + '…"'
    return pre + t


def _serie_ld():
    return {"@type": "CreativeWorkSeries", "@id": SITE + "/filo/#serie", "name": SERIE, "url": SITE + "/filo/",
            "inLanguage": "it", "author": {"@id": SITE + "/#riccardo-benotti"}, "about": LEONE_LD}


def _pagina(title, desc, path, body, graph, og_type='website', img=None, extra=''):
    page = head('it', title, desc, path, og_type=og_type,
                jsonld={"@context": "https://schema.org", "@graph": graph}, extra=extra)
    if img:
        page = page.replace(f'{SITE}/img/og.jpg', f'{SITE}/img/{img}').replace(
            '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n', '')
    write(path, page + nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n')


def archivio(puntate):
    urls = []
    mesi = {}
    for p in puntate:
        mesi.setdefault(p['data'][:7], []).append(p)
    chiavi = sorted(mesi, reverse=True)

    # --- indice generale /filo/
    indice_mesi = ''.join(f'<li><a href="{_mese_url(k)}">{_mese(k + "-01")}</a> <span class="n">{len(mesi[k])}</span></li>' for k in chiavi)
    blocchi = ''
    for k in chiavi:
        righe = ''.join(f'\n        <li><time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time><a href="{p["url"]}">{p["titolo_html"]}</a></li>' for p in mesi[k])
        blocchi += f'''
    <section class="mese" id="m{k}">
      <h2><a href="{_mese_url(k)}">{_mese(k + "-01").capitalize()}</a></h2>
      <ol class="archivio filo-linea">{righe}
      </ol>
    </section>'''
    bric, bld = _briciole([('Home', '/'), (SERIE, None)])
    body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">Rubrica quotidiana · {len(puntate)} puntate</span>
    <h1>Leone, <em>il filo del giorno</em></h1>
    {SEGNO}
    <p class="intro">{html.escape(INTRO)} <a href="{LINKEDIN}">Seguila su LinkedIn</a> o con il <a href="/filo/feed.xml">feed RSS</a>.</p>
    <nav class="mesi" aria-label="Archivio per mese"><span class="label">Archivio per mese</span><ul>{indice_mesi}</ul></nav>
    <p class="ultima-p"><span class="label">Per argomento</span> <a href="/filo/temi/">Persone, luoghi e temi delle puntate</a> · <a href="/filo/viaggi/">I viaggi del Papa</a></p>
    <p class="ultima-p"><span class="label">Ultima puntata</span> <a href="{puntate[0]["url"]}">{puntate[0]["titolo_html"]}</a> <time datetime="{puntate[0]["data"]}">({data_it(puntate[0]["data"])})</time></p>
    {blocchi}
  </main>
</div>
'''
    graph = [{"@type": "CollectionPage", "@id": SITE + "/filo/", "url": SITE + "/filo/", "name": SERIE + " – tutte le puntate",
              "description": INTRO, "inLanguage": "it", "isPartOf": {"@id": SITE + "/#sito"}, "mainEntity": {"@id": SITE + "/filo/#serie"},
              "author": {"@id": SITE + "/#riccardo-benotti"}}, _serie_ld(), bld]
    _pagina(f'{SERIE}: archivio completo su papa Leone XIV | Riccardo Benotti',
            'Archivio completo di «Leone, il filo del giorno», la rubrica quotidiana di Riccardo Benotti su papa Leone XIV: '
            f'{len(puntate)} puntate da dicembre 2025, ordinate per mese.', '/filo/', body, graph)
    urls.append(('/filo/', puntate[0]['data']))

    # --- pagine mensili
    for i, k in enumerate(chiavi):
        lista = mesi[k]
        nome = _mese(k + '-01')
        voci = ''
        for p in lista:
            th = ''
            if p.get('foto'):
                th = f'<a class="th" href="{p["url"]}" tabindex="-1" aria-hidden="true"><img src="/img/filo/{p["foto"]}" alt="" loading="lazy" width="160" height="107"{fuoco(p)}></a>'
            voci += f'''
      <li class="voce-mese">
        {th}<div><time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time>
        <h2><a href="{p["url"]}">{p["titolo_html"]}</a></h2>
        <p>{html.escape(taglia(p["sommario"], 260))}</p></div>
      </li>'''
        prec = chiavi[i + 1] if i + 1 < len(chiavi) else None
        succ = chiavi[i - 1] if i > 0 else None
        vic = '<nav class="vicine">'
        vic += f'<a href="{_mese_url(prec)}"><span class="label">← Mese precedente</span>{_mese(prec + "-01")}</a>' if prec else '<span></span>'
        vic += f'<a href="{_mese_url(succ)}" style="text-align:right"><span class="label">Mese successivo →</span>{_mese(succ + "-01")}</a>' if succ else '<span></span>'
        vic += '</nav>'
        bric, bld = _briciole([('Home', '/'), (SERIE, '/filo/'), (nome.capitalize(), None)])
        body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">{SERIE} · {len(lista)} puntate</span>
    <h1>Il filo del giorno, <em>{nome}</em></h1>
    {SEGNO}
    <p class="intro">Le puntate di {nome} della rubrica quotidiana di Riccardo Benotti su papa Leone XIV.</p>
    <ol class="lista-mese filo-linea">{voci}
    </ol>
    {vic}
  </main>
</div>
'''
        path = _mese_url(k)
        graph = [{"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": f'{SERIE} – {nome}',
                  "inLanguage": "it", "isPartOf": {"@id": SITE + "/filo/"},
                  "hasPart": [{"@type": "NewsArticle", "headline": p['titolo_txt'][:110], "url": SITE + p['url'], "datePublished": p['pubblicato']} for p in lista]},
                 bld]
        _pagina(f'Papa Leone XIV, {nome}: le puntate de «{SERIE}» | Riccardo Benotti',
                taglia(f'Le {len(lista)} puntate di {nome} di «{SERIE}», la rubrica quotidiana di Riccardo Benotti sul pontificato di Leone XIV: '
                       + '; '.join(p['titolo_txt'] for p in lista[:3]), 158), path, body, graph)
        urls.append((path, lista[0]['data']))

    # --- pagine delle puntate
    for i, p in enumerate(puntate):
        prec = puntate[i + 1] if i + 1 < len(puntate) else None
        succ = puntate[i - 1] if i > 0 else None
        vic = '<nav class="vicine">'
        vic += f'<a href="{prec["url"]}" rel="prev"><span class="label">← Puntata precedente</span>{prec["titolo_html"]}</a>' if prec else '<span></span>'
        vic += f'<a href="{succ["url"]}" rel="next" style="text-align:right"><span class="label">Puntata successiva →</span>{succ["titolo_html"]}</a>' if succ else '<span></span>'
        vic += '</nav>'
        fig = ''
        grande = gw = gh = None
        if p.get('foto'):
            from PIL import Image
            w, h = Image.open(PUB / 'img' / 'filo' / p['foto']).size
            alt = html.escape(('Foto della puntata del ' + data_it(p['data']) + ': ' + p['titolo_txt'])[:180])
            cap = f'<figcaption>Foto {html.escape(p["credito"])}</figcaption>' if p.get('credito') else ''
            # versione grande (1200 px) per Google Discover, anteprime social e schermi ad alta densità
            grande = p['foto'].rsplit('.', 1)[0] + '-1200.webp'
            gw = gh = None
            if (PUB / 'img' / 'filo' / grande).exists():
                gw, gh = Image.open(PUB / 'img' / 'filo' / grande).size
            else:
                grande = None
            srcset = f' srcset="/img/filo/{p["foto"]} {w}w, /img/filo/{grande} {gw}w" sizes="(max-width: 760px) 100vw, 720px"' if grande else ''
            fig = f'<figure class="foto-grande"><img src="/img/filo/{p["foto"]}"{srcset} width="{w}" height="{h}" alt="{alt}" fetchpriority="high">{cap}</figure>'
        nome_mese = _mese(p['data'])
        bric, bld = _briciole([('Home', '/'), (SERIE, '/filo/'), (nome_mese.capitalize(), _mese_url(p['data'])), (taglia(p['titolo_txt'], 60), None)])
        body = f'''<div class="wrap">
  <main class="pagina">
    {bric}
    <article>
      <header>
        <span class="label gold"><a href="/filo/">{SERIE}</a> · <time datetime="{p["pubblicato"]}">{data_it(p["data"])}</time></span>
        <h1>{p["titolo_html"]}</h1>
        <p class="firma-art">di <a href="/" rel="author">Riccardo Benotti</a></p>
      </header>
      {fig}
      <div class="testo">{linka(p)}</div>
      <div class="filo-chiusa">{CHIUSA}</div>
      {fonti_html(p)}
      {temi_html(p)}
      <div class="meta puntata-meta"><a href="{p["linkedin"]}">La puntata su LinkedIn</a><a href="{_mese_url(p["data"])}">Tutte le puntate di {nome_mese}</a></div>
    </article>
    {vic}
  </main>
</div>
'''
        art = {"@type": "NewsArticle", "@id": SITE + p['url'] + '#articolo', "headline": p['titolo_txt'][:110],
               "description": p['descrizione'], "datePublished": p['pubblicato'], "dateModified": p['pubblicato'],
               "inLanguage": "it", "url": SITE + p['url'], "mainEntityOfPage": SITE + p['url'],
               "wordCount": p['parole'], "articleSection": SERIE,
               "author": {"@type": "Person", "@id": SITE + "/#riccardo-benotti", "name": "Riccardo Benotti", "url": SITE + "/"},
               "publisher": {"@id": SITE + "/#riccardo-benotti"},
               "isPartOf": {"@id": SITE + "/filo/#serie"}, "about": LEONE_LD,
               "keywords": "Leone XIV, papa Leone XIV, Santa Sede, " + SERIE + ", " + data_it(p['data']),
               **({"sameAs": p['linkedin']} if p.get('urn') else {})}
        if p.get('fonti'):
            art["isBasedOn"] = [{"@type": "WebPage", "name": t, "url": u, "publisher": {"@type": "Organization", "name": _editore(u)}} for t, u in p['fonti']]
        if p.get('foto'):
            art["thumbnailUrl"] = SITE + '/img/filo/' + p['foto']
            art["image"] = {"@type": "ImageObject", "url": SITE + '/img/filo/' + (grande or p['foto']), "width": gw or w, "height": gh or h,
                            # licenza e dati di credito solo se l'autore è noto: senza credito non si dichiara nulla
                            **({"creditText": p['credito'], "copyrightNotice": "© " + p['credito'],
                                "creator": {"@type": "Organization", "name": p['credito']},
                                "license": SITE + "/crediti/", "acquireLicensePage": SITE + "/crediti/"} if p.get('credito') else {})}
        extra = (f'<meta property="article:published_time" content="{p["pubblicato"]}">\n'
                 f'<meta property="article:modified_time" content="{p["pubblicato"]}">\n'
                 f'<meta property="article:author" content="{SITE}/">\n<meta property="article:section" content="{SERIE}">\n')
        if p.get('foto'):
            extra += (f'<meta property="og:image:width" content="{gw or w}">\n<meta property="og:image:height" content="{gh or h}">\n'
                      f'<meta property="og:image:alt" content="{alt}">\n<meta name="twitter:image:alt" content="{alt}">\n')
        if prec:
            extra += f'<link rel="prev" href="{SITE}{prec["url"]}">\n'
        if succ:
            extra += f'<link rel="next" href="{SITE}{succ["url"]}">\n'
        _pagina(titolo_seo(p), p['descrizione'], p['url'], body, [art, _serie_ld(), bld],
                og_type='article', img=('filo/' + (grande or p['foto'])) if p.get('foto') else None, extra=extra)
        urls.append((p['url'], p['data'], ('filo/' + (grande or p['foto'])) if p.get('foto') else None))

    # --- feed RSS (ultime 40 puntate)
    items = ''
    for p in puntate[:40]:
        dt = datetime.datetime.fromisoformat(p['pubblicato']) if 'T' in p['pubblicato'] else datetime.datetime.fromisoformat(p['data'] + 'T20:00:00+01:00')
        enc = f'<enclosure url="{SITE}/img/filo/{p["foto"]}" type="image/webp" length="{(PUB / "img" / "filo" / p["foto"]).stat().st_size}"/>' if p.get('foto') else ''
        items += (f'<item><title>{html.escape(p["titolo_txt"])}</title><link>{SITE}{p["url"]}</link><guid isPermaLink="true">{SITE}{p["url"]}</guid>'
                  f'<pubDate>{format_datetime(dt)}</pubDate><dc:creator>Riccardo Benotti</dc:creator>'
                  f'<description>{html.escape("".join(p["paras"]))}</description>{enc}</item>\n')
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
<title>{SERIE}</title>
<link>{SITE}/filo/</link>
<atom:link href="{SITE}/filo/feed.xml" rel="self" type="application/rss+xml"/>
<description>{html.escape(INTRO)}</description>
<language>it</language>
<copyright>Riccardo Benotti</copyright>
{items}</channel>
</rss>
'''
    write('/filo/feed.xml', rss)
    return urls
