# Archivio di «Leone, il filo del giorno»: indice generale, pagine mensili,
# una pagina per puntata, feed RSS. Eseguito da build.py (usa le sue funzioni).
from email.utils import format_datetime

SERIE = 'Leone, il filo del giorno'
INTRO = ('Ogni giorno, da dicembre 2025, una lettura delle notizie e degli appuntamenti di papa Leone XIV, '
         'tenuti insieme da un solo filo: udienze, viaggi, documenti, nomine, parole del Papa e della Santa Sede. '
         'La rubrica di Riccardo Benotti esce anche su LinkedIn.')


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


def _serie_ld():
    return {"@type": "CreativeWorkSeries", "@id": SITE + "/filo/#serie", "name": SERIE, "url": SITE + "/filo/",
            "inLanguage": "it", "author": {"@id": SITE + "/#riccardo-benotti"}, "about": {"@type": "Person", "name": "Leone XIV"}}


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
      <ol class="archivio">{righe}
      </ol>
    </section>'''
    bric, bld = _briciole([('Home', '/'), (SERIE, None)])
    body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">Rubrica quotidiana · {len(puntate)} puntate</span>
    <h1>Leone, <em>il filo del giorno</em></h1>
    <p class="intro">{html.escape(INTRO)} <a href="{LINKEDIN}">Seguila su LinkedIn</a> o con il <a href="/filo/feed.xml">feed RSS</a>.</p>
    <nav class="mesi" aria-label="Archivio per mese"><span class="label">Archivio per mese</span><ul>{indice_mesi}</ul></nav>
    <p class="ultima-p"><span class="label">Ultima puntata</span> <a href="{puntate[0]["url"]}">{puntate[0]["titolo_html"]}</a> <time datetime="{puntate[0]["data"]}">({data_it(puntate[0]["data"])})</time></p>
    {blocchi}
  </main>
</div>
'''
    graph = [{"@type": "CollectionPage", "@id": SITE + "/filo/", "url": SITE + "/filo/", "name": SERIE + " – tutte le puntate",
              "description": INTRO, "inLanguage": "it", "isPartOf": {"@id": SITE + "/#sito"}, "mainEntity": {"@id": SITE + "/filo/#serie"},
              "author": {"@id": SITE + "/#riccardo-benotti"}}, _serie_ld(), bld]
    _pagina(f'{SERIE}: tutte le puntate | Riccardo Benotti',
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
    <p class="intro">Le puntate di {nome} della rubrica quotidiana di Riccardo Benotti su papa Leone XIV.</p>
    <ol class="lista-mese">{voci}
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
        _pagina(f'{SERIE} – {nome} | Riccardo Benotti',
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
        if p.get('foto'):
            from PIL import Image
            w, h = Image.open(PUB / 'img' / 'filo' / p['foto']).size
            alt = html.escape(('Foto della puntata del ' + data_it(p['data']) + ': ' + p['titolo_txt'])[:180])
            cap = f'<figcaption>Foto {html.escape(p["credito"])}</figcaption>' if p.get('credito') else ''
            fig = f'<figure class="foto-grande"><img src="/img/filo/{p["foto"]}" width="{w}" height="{h}" alt="{alt}" fetchpriority="high">{cap}</figure>'
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
      <div class="testo">{"".join(p["paras"])}</div>
      {fonti_html(p)}
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
               "isPartOf": {"@id": SITE + "/filo/#serie"}, "about": {"@type": "Person", "name": "Leone XIV"},
               "sameAs": p['linkedin']}
        if p.get('foto'):
            art["image"] = {"@type": "ImageObject", "url": SITE + '/img/filo/' + p['foto'],
                            **({"creditText": p['credito'], "copyrightNotice": "© " + p['credito'],
                                "creator": {"@type": "Organization", "name": p['credito']}} if p.get('credito') else {})}
        extra = (f'<meta property="article:published_time" content="{p["pubblicato"]}">\n'
                 f'<meta property="article:author" content="{SITE}/">\n<meta property="article:section" content="{SERIE}">\n')
        if prec:
            extra += f'<link rel="prev" href="{SITE}{prec["url"]}">\n'
        if succ:
            extra += f'<link rel="next" href="{SITE}{succ["url"]}">\n'
        _pagina(f'{p["titolo_txt"]} | {SERIE}', p['descrizione'], p['url'], body, [art, _serie_ld(), bld],
                og_type='article', img=('filo/' + p['foto']) if p.get('foto') else None, extra=extra)
        urls.append((p['url'], p['data'], ('filo/' + p['foto']) if p.get('foto') else None))

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
