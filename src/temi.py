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


def _sintesi(t, TEMI):
    """Testo introduttivo ricavato dai dati: quante puntate, prima e ultima, temi che ricorrono insieme."""
    hit = [p for p, _ in t['hit']]
    n = len(hit)
    prima, ultima = hit[-1], hit[0]
    if t['tipo'] == 'persona':
        frase = f'{html.escape(t["nome"])} compare in {n} puntate'
    else:
        frase = f'«{html.escape(t["nome"])}» ricorre in {n} puntate'
    frase += (f', dalla prima del <a href="{prima["url"]}">{data_it(prima["data"])}</a> '
              f'alla più recente del <a href="{ultima["url"]}">{data_it(ultima["data"])}</a>.')
    conta = {}
    for p in hit:
        for altro in p.get('temi', []):
            if altro['slug'] != t['slug']:
                conta[altro['slug']] = conta.get(altro['slug'], 0) + 1
    vicini = [x for x in sorted(TEMI, key=lambda x: -conta.get(x['slug'], 0)) if conta.get(x['slug'], 0) >= 2][:4]
    if vicini:
        nomi = [f'<a href="/filo/temi/{x["slug"]}/">{html.escape(x["nome"])}</a>' for x in vicini]
        elenco = nomi[0] if len(nomi) == 1 else ', '.join(nomi[:-1]) + ' e ' + nomi[-1]
        frase += f' Gli argomenti che tornano più spesso nelle stesse puntate: {elenco}.'
    return frase


def linka(p, massimo=6):
    """Collega alle pagine dei temi la prima occorrenza di ciascun tema nel testo della puntata (solo testo, mai dentro un link)."""
    usati, fatti, out = set(), 0, []
    for par in p['paras']:
        pezzi = re.split(r'(<[^>]+>)', par)
        dentro_a = False
        for i, x in enumerate(pezzi):
            if x.startswith('<'):
                if re.match(r'<a\b', x):
                    dentro_a = True
                elif x.startswith('</a'):
                    dentro_a = False
                continue
            if dentro_a or fatti >= massimo:
                continue
            fatto_qui, resto = '', x
            while fatti < massimo:
                migliore = None
                for t in p.get('temi', []):
                    if t['slug'] in usati:
                        continue
                    m = re.search(t['rx'], resto)
                    if m and m.group(0).strip() and (migliore is None or m.start() < migliore[1].start()):
                        migliore = (t, m)
                if not migliore:
                    break
                t, m = migliore
                a, b = m.span()
                b += len(re.match(r'\w*', resto[b:]).group(0))  # il link copre la parola intera
                fatto_qui += resto[:a] + f'<a class="link-tema" href="/filo/temi/{t["slug"]}/">{resto[a:b]}</a>'
                resto = resto[b:]
                usati.add(t['slug'])
                fatti += 1
            x = fatto_qui + resto
            pezzi[i] = x
        out.append(''.join(pezzi))
    return ''.join(out)


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
        wd = f' <a href="https://www.wikidata.org/wiki/{t["qid"]}" rel="noopener">Scheda su Wikidata</a>.' if t.get('qid') else ''
        body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">{etichetta} · {n} puntate</span>
    <h1>{html.escape(t["nome"])}</h1>
    {SEGNO}
    <p class="intro">Le puntate di «{SERIE}», la rubrica quotidiana di Riccardo Benotti su papa Leone XIV, {"in cui compare " + html.escape(t["nome"]) if t["tipo"] == "persona" else "raccolte sotto la voce «" + html.escape(t["nome"]) + "»"}, dalla più recente. Per ciascuna, il passaggio in cui compare.{wd}</p>
    <p class="intro">{_sintesi(t, TEMI)}</p>
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
                  "about": {"@type": tipo_ld, "name": t['nome'], **({"sameAs": f'https://www.wikidata.org/wiki/{t["qid"]}'} if t.get('qid') else {})},
                  "author": {"@id": SITE + "/#riccardo-benotti"},
                  "hasPart": [{"@type": "NewsArticle", "headline": p['titolo_txt'][:110], "url": SITE + p['url'], "datePublished": p['pubblicato']}
                              for p, _ in t['hit'][:60]]}, bld]
        cosa = 'in cui compare' if t['tipo'] == 'persona' else 'sul tema'
        _pagina(f'{t["nome"]} e papa Leone XIV: tutte le puntate | Il filo del giorno',
                taglia(f'Le {n} puntate di «{SERIE}» di Riccardo Benotti {cosa} {t["nome"] if t["tipo"] == "persona" else "«" + t["nome"] + "»"}, dalla più recente: '
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
