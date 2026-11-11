# Pagine dei libri: /libri/<slug>/, una per volume (Covid-19: preti in prima linea; Viaggio nella vita religiosa).
# Eseguito da build.py dopo viaggi.py. Dati in data/libri.json. I colori di ogni pagina vengono dalla copertina (vedi .lp-* in style.css).
def _libri_cfg():
    return json.loads((ROOT / 'data' / 'libri.json').read_text())


def url_libro(l):
    return f'/libri/{l["slug"]}/'


def libro_ld(l, altri):
    url = SITE + url_libro(l)
    autore = {"@id": SITE + "/#riccardo-benotti"}
    contributi = []
    for ruolo, chi in l.get('voci', []):
        nome = re.sub(r'^(card\.|fra)\s+', '', chi.split(',')[0]).strip()
        contributi.append({"@type": "Person", "name": nome, "roleName": ruolo})
    edizioni = [{"@type": "Book", "bookFormat": "https://schema.org/Paperback", "isbn": l['isbn'],
                 "numberOfPages": l['pagine'], "publisher": {"@type": "Organization", "name": l['editore']}, "datePublished": l['anno']}]
    if l.get('isbn_ebook'):
        edizioni.append({"@type": "Book", "bookFormat": "https://schema.org/EBook", "isbn": l['isbn_ebook'],
                         "publisher": {"@type": "Organization", "name": l['editore']}, "datePublished": l['anno']})
    libro = {"@type": "Book", "@id": url + "#libro", "name": l['titolo'] + '. ' + l['sottotitolo'],
             "alternativeHeadline": l['sottotitolo'], "author": autore, "inLanguage": "it",
             "publisher": {"@type": "Organization", "name": l['editore']}, "datePublished": l['anno'],
             "isbn": l['isbn'], "numberOfPages": l['pagine'], "bookFormat": "https://schema.org/Paperback",
             "image": SITE + '/img/' + l['cover'], "description": l['descrizione'], "url": url,
             "mainEntityOfPage": url, "workExample": edizioni, "keywords": ', '.join(l.get('parole', [])),
             "sameAs": "https://www.wikidata.org/wiki/" + l['wikidata'], "isPartOf": {"@id": SITE + "/#sito"}}
    if contributi:
        libro["contributor"] = contributi
    return libro


def libri():
    cfg = _libri_cfg()
    urls = []
    for l in cfg['libri']:
        url = url_libro(l)
        e = html.escape
        bric, bld = _briciole([('Home', '/'), ('Libri', '/#libri'), (l['titolo'], None)])
        dati = f'<span>{l["pagine"]} pagine</span><span>ISBN {l["isbn_fmt"]}</span>'
        corpo = ''.join(f'\n      <p>{t}</p>' for t in l['corpo'])
        sez = ''
        if l.get('struttura'):
            voci = ''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in l['struttura'])
            sez += f'\n    <section class="lp-sez"><h2 class="label">{e(l["struttura_titolo"])}</h2><dl class="lp-dl">{voci}</dl></section>'
        if l.get('cifre'):
            celle = ''.join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in l['cifre'])
            sez += f'''
    <section class="lp-sez"><h2 class="label">{e(l["cifre_titolo"])}</h2>
      <ul class="lp-cifre">{celle}</ul>
      <p class="lp-nota">{e(l["cifre_nota"])}</p></section>'''
        if l.get('intervistati'):
            righe = ''.join(f'<li><strong>{e(n)}</strong><span>{e(i)} · {e(r)}</span></li>' for n, i, r in l['intervistati'])
            sez += f'''
    <section class="lp-sez"><h2 class="label">{e(l["intervistati_titolo"])}</h2>
      <ul class="lp-intervistati">{righe}</ul>
      <p class="lp-nota">{e(l["intervistati_nota"])}</p></section>'''
        if l.get('voci') and l['tema'] == 'covid':
            voci = ''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in l['voci'])
            sez += f'\n    <section class="lp-sez"><h2 class="label">{e(l["voci_titolo"])}</h2><dl class="lp-dl">{voci}</dl></section>'
        if l.get('stampa'):
            li = ''.join(f'<li><span class="label">{e(a)}</span> <a href="{u}">{e(t)}</a></li>' for a, t, u in l['stampa'])
            sez += f'\n    <section class="lp-sez"><h2 class="label">{e(l["stampa_titolo"])}</h2><ul class="lp-link">{li}</ul></section>'
        li = ''.join(f'<li><a href="{u}">{e(t)}</a></li>' for t, u in l['dove'])
        sez += f'\n    <section class="lp-sez"><h2 class="label">Dove trovarlo</h2><ul class="lp-link">{li}</ul></section>'
        isbn_ed = f'<div><dt>ISBN</dt><dd>{l["isbn_fmt"]} (cartaceo)' + (f'<br>{l["isbn_ebook_fmt"]} (ebook)' if l.get('isbn_ebook') else '') + '</dd></div>'
        pref = ''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in l['voci']) if l['tema'] != 'covid' else ''
        sez += f'''
    <section class="lp-sez"><h2 class="label">Dati del volume</h2>
      <dl class="lp-dl"><div><dt>Autore</dt><dd><a href="/">Riccardo Benotti</a></dd></div>{pref}<div><dt>Editore</dt><dd>{e(l["editore"])}</dd></div><div><dt>Anno</dt><dd>{l["anno"]}</dd></div><div><dt>Pagine</dt><dd>{l["pagine"]}</dd></div>{isbn_ed}</dl></section>'''
        altri = [x for x in cfg['libri'] if x['slug'] != l['slug']]
        al = ''.join(f'<li><a href="{url_libro(x)}">{e(x["titolo"])}</a> <span class="label">{e(x["editore"])}, {x["anno"]}</span></li>' for x in altri)
        al += '<li><a href="https://www.governareilpatrimonio.it/">Governare il patrimonio ecclesiale nell’era dell’IA</a> <span class="label">Marcianum Press, 2026</span></li>'
        sez += f'\n    <section class="lp-sez"><h2 class="label">Altri libri di Riccardo Benotti</h2><ul class="lp-link">{al}</ul>\n      <p class="ultima-p"><a href="/#libri">Tutti i libri</a> · <a href="/">Profilo</a></p></section>'
        body = f'''<main class="lp lp-{l["tema"]}">
  <div class="lp-fascia">
    <div class="wrap">
      {bric}
      <div class="lp-hero">
        <figure class="lp-cover"><img src="/img/{l["cover"]}" width="{l["cover_w"]}" height="{l["cover_h"]}" alt="Copertina di {e(l["titolo"])}" fetchpriority="high"></figure>
        <div class="lp-testa">
          <span class="label">{e(l["etichetta"])}</span>
          <h1>{e(l["titolo"])}<span class="sub">{e(l["sottotitolo"])}</span></h1>
          <p class="lp-lead">{e(l["lead"])}</p>
          <div class="dati lp-dati">{dati}</div>
        </div>
      </div>
    </div>
  </div>
  <div class="wrap">
    <div class="lp-corpo">
    <section class="lp-sez lp-testo">{corpo}
    </section>{sez}
    </div>
  </div>
</main>
'''
        pagina = {"@type": "WebPage", "@id": SITE + url, "url": SITE + url, "name": l['titolo'] + ' | Riccardo Benotti',
                  "inLanguage": "it", "isPartOf": {"@id": SITE + "/#sito"}, "mainEntity": {"@id": SITE + url + "#libro"},
                  "about": {"@id": SITE + url + "#libro"}, "author": {"@id": SITE + "/#riccardo-benotti"},
                  "dateModified": cfg['aggiornato'], "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + '/img/' + l['cover']}}
        _pagina(f'{l["titolo"]} | libro di Riccardo Benotti', taglia(l['descrizione'], 158), url, body,
                [pagina, libro_ld(l, cfg['libri']), person_ld(), bld], og_type='book', img=l['cover'])
        urls.append((url, cfg['aggiornato'], l['cover']))
    return urls
