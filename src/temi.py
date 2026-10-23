# Pagine per tema, persona e luogo: /filo/temi/ e /filo/temi/<slug>/.
# Eseguito da build.py dopo archivio.py (ne usa le funzioni). Elenco e regole in data/temi.json.
SOGLIA_TEMA = 5  # un tema ha la sua pagina solo se compare in almeno 5 puntate
TIPI = [('persona', 'Persone', 'Person'), ('luogo', 'Luoghi', 'Place'),
        ('evento', 'Liturgia e appuntamenti', 'Thing'), ('tema', 'Temi', 'Thing')]


def _plain(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h))


def calcola_temi(puntate):
    """Abbina i temi alle puntate. Ogni puntata riceve p['temi'] (nell'ordine di data/temi.json)."""
    cfg = json.loads((ROOT / 'data' / 'temi.json').read_text())
    out = []
    for t in cfg:
        rx = re.compile(t['rx'])
        hit = []
        for p in puntate:
            paragrafi = [_plain(x) for x in p['paras']]
            snip = next((x for x in paragrafi if rx.search(x)), None)
            if snip is None and rx.search(p['titolo_txt']):
                snip = p['sommario']
            if snip is not None:
                hit.append((p, snip))
        if len(hit) >= SOGLIA_TEMA:
            out.append({**t, 'hit': hit})
    for p in puntate:
        p['temi'] = []
    for t in out:
        for p, _ in t['hit']:
            p['temi'].append(t)
    return out


def temi_html(p):
    if not p.get('temi'):
        return ''
    li = ''.join(f'<li><a href="/filo/temi/{t["slug"]}/">{html.escape(t["nome"])}</a></li>' for t in p['temi'][:6])
    return f'<div class="temi-puntata"><span class="label">Temi</span><ul>{li}</ul></div>'


def _chip(temi, escludi=None):
    return ''.join(f'<li><a href="/filo/temi/{t["slug"]}/">{html.escape(t["nome"])}</a> <span class="n">{len(t["hit"])}</span></li>'
                   for t in temi if t['slug'] != escludi)


def temi(puntate, TEMI):
    urls = []
    # --- pagine dei singoli temi
    for t in TEMI:
        n = len(t['hit'])
        tipo_ld = {x[0]: x[2] for x in TIPI}[t['tipo']]
        etichetta = {x[0]: x[1] for x in TIPI}[t['tipo']].rstrip('i').rstrip('e') if False else {'persona': 'Persona', 'luogo': 'Luogo', 'evento': 'Liturgia e appuntamenti', 'tema': 'Tema'}[t['tipo']]
        voci = ''
        for p, snip in t['hit']:
            th = ''
            if p.get('foto'):
                th = f'<a class="th" href="{p["url"]}" tabindex="-1" aria-hidden="true"><img src="/img/filo/{p["foto"]}" alt="" loading="lazy" width="160" height="107"{fuoco(p)}></a>'
            voci += f'''
      <li class="voce-mese">
        {th}<div><time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time>
        <h2><a href="{p["url"]}">{p["titolo_html"]}</a></h2>
        <p>{html.escape(taglia(snip, 260))}</p></div>
      </li>'''
        bric, bld = _briciole([('Home', '/'), (SERIE, '/filo/'), ('Temi', '/filo/temi/'), (t['nome'], None)])
        body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">{etichetta} · {n} puntate</span>
    <h1>{html.escape(t["nome"])}</h1>
    {SEGNO}
    <p class="intro">Le puntate di «{SERIE}», la rubrica quotidiana di Riccardo Benotti su papa Leone XIV, che parlano di {html.escape(t["nome"])}, dalla più recente. Per ciascuna, il passaggio in cui compare. <a href="https://www.wikidata.org/wiki/{t["qid"]}" rel="noopener">Scheda su Wikidata</a>.</p>
    <ol class="lista-mese filo-linea">{voci}
    </ol>
    <nav class="temi-altri" aria-label="Altri temi"><span class="label">Altri temi</span><ul>{_chip(TEMI, t["slug"])}</ul></nav>
    <p class="ultima-p"><a href="/filo/temi/">Tutti i temi</a> · <a href="/filo/">Tutte le puntate</a></p>
  </main>
</div>
'''
        path = f'/filo/temi/{t["slug"]}/'
        graph = [{"@type": "CollectionPage", "@id": SITE + path, "url": SITE + path, "name": f'{t["nome"]} e papa Leone XIV: le puntate di {SERIE}',
                  "inLanguage": "it", "isPartOf": {"@id": SITE + "/filo/temi/"},
                  "about": {"@type": tipo_ld, "name": t['nome'], "sameAs": f'https://www.wikidata.org/wiki/{t["qid"]}'},
                  "author": {"@id": SITE + "/#riccardo-benotti"},
                  "hasPart": [{"@type": "NewsArticle", "headline": p['titolo_txt'][:110], "url": SITE + p['url'], "datePublished": p['pubblicato']}
                              for p, _ in t['hit'][:60]]}, bld]
        cosa = 'in cui compare' if t['tipo'] == 'persona' else 'che parlano di'
        _pagina(f'{t["nome"]} e papa Leone XIV: tutte le puntate | Il filo del giorno',
                taglia(f'Le {n} puntate di «{SERIE}» di Riccardo Benotti {cosa} {t["nome"]}, dalla più recente: '
                       + '; '.join(p['titolo_txt'] for p, _ in t['hit'][:3]), 158), path, body, graph)
        urls.append((path, t['hit'][0][0]['data']))

    # --- indice dei temi
    gruppi = ''
    for tipo, nome_g, _ in TIPI:
        li = _chip([t for t in TEMI if t['tipo'] == tipo])
        if li:
            gruppi += f'\n    <section class="temi-gruppo"><h2>{nome_g}</h2><ul>{li}</ul></section>'
    bric, bld = _briciole([('Home', '/'), (SERIE, '/filo/'), ('Temi', None)])
    body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">{SERIE} · {len(TEMI)} temi</span>
    <h1>Temi, <em>persone e luoghi</em></h1>
    {SEGNO}
    <p class="intro">Le puntate di «{SERIE}» raccolte per argomento: i Papi e i santi che Leone XIV cita, i Paesi e i viaggi, i tempi liturgici, i grandi temi del pontificato. Accanto a ogni voce, il numero di puntate.</p>{gruppi}
    <p class="ultima-p"><a href="/filo/">Tutte le puntate, mese per mese</a></p>
  </main>
</div>
'''
    graph = [{"@type": "CollectionPage", "@id": SITE + "/filo/temi/", "url": SITE + "/filo/temi/", "name": f"{SERIE}: temi, persone e luoghi",
              "inLanguage": "it", "isPartOf": {"@id": SITE + "/filo/"}, "author": {"@id": SITE + "/#riccardo-benotti"},
              "hasPart": [{"@type": "CollectionPage", "name": t['nome'], "url": SITE + f'/filo/temi/{t["slug"]}/'} for t in TEMI]}, bld]
    _pagina('Temi, persone e luoghi del pontificato di Leone XIV | Il filo del giorno',
            f'Le puntate di «{SERIE}» di Riccardo Benotti raccolte per tema: Papa Francesco, Giovanni Paolo II, Agostino, Medio Oriente, '
            'Ucraina, intelligenza artificiale, Natale, Pasqua e altri argomenti.', '/filo/temi/', body, graph)
    urls.append(('/filo/temi/', puntate[0]['data']))
    return urls
