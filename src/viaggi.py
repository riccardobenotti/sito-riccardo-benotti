# Pagina /filo/viaggi/: i viaggi apostolici e le visite in Italia di Leone XIV, con le puntate del Filo.
# Eseguito da build.py dopo archivio.py e temi.py. Dati in data/viaggi.json; si pubblica solo con "pubblica": true.
GRUPPI_VIAGGI = [('annunciato', 'In programma'), ('estero', 'Viaggi apostolici'), ('italia', 'Visite in Italia')]


def viaggi(puntate, forza=False, percorso='/filo/viaggi/'):
    cfg = json.loads((ROOT / 'data' / 'viaggi.json').read_text())
    if not (cfg.get('pubblica') or forza):
        return []
    per_data = {p['data']: p for p in puntate}
    sezioni, elenco_ld, n_tot = '', [], 0
    for tipo, nome_g in GRUPPI_VIAGGI:
        blocchi = ''
        for v in [v for v in cfg['viaggi'] if v['tipo'] == tipo]:
            lista = [per_data[d] for d in v['puntate'] if d in per_data]
            if not lista:
                continue
            n_tot += 1
            voci = ''.join(f'''
        <li><time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time> <a href="{p["url"]}">{p["titolo_html"]}</a></li>''' for p in lista)
            blocchi += f'''
    <section class="viaggio" id="{v["slug"]}">
      <h3>{html.escape(v["titolo"])}</h3>
      <span class="label">{html.escape(v["periodo"])} · {len(lista)} {"puntata" if len(lista) == 1 else "puntate"}</span>
      <ol class="viaggio-puntate">{voci}
      </ol>
    </section>'''
            elenco_ld.append({"@type": "ListItem", "position": len(elenco_ld) + 1, "name": v['titolo'],
                              "url": SITE + percorso + '#' + v['slug']})
        if blocchi:
            sezioni += f'\n    <h2 class="viaggi-gruppo">{nome_g}</h2>{blocchi}'
    bric, bld = _briciole([('Home', '/'), (SERIE, '/filo/'), ('Viaggi', None)])
    body = f'''<div class="wrap">
  <main class="pagina larga">
    {bric}
    <span class="label gold">{SERIE} · {n_tot} viaggi e visite</span>
    <h1>I viaggi di <em>papa Leone XIV</em></h1>
    {SEGNO}
    <p class="intro">{html.escape(cfg["intro"])}</p>{sezioni}
    <p class="ultima-p"><a href="/filo/temi/">Temi, persone e luoghi</a> · <a href="/filo/">Tutte le puntate</a></p>
  </main>
</div>
'''
    graph = [{"@type": "CollectionPage", "@id": SITE + percorso, "url": SITE + percorso, "name": "I viaggi di papa Leone XIV",
              "inLanguage": "it", "isPartOf": {"@id": SITE + "/filo/"}, "about": LEONE_LD, "author": {"@id": SITE + "/#riccardo-benotti"},
              "mainEntity": {"@type": "ItemList", "itemListElement": elenco_ld}}, bld]
    _pagina('Viaggi di papa Leone XIV: tutte le tappe, giorno per giorno | Il filo del giorno',
            taglia('I viaggi apostolici e le visite in Italia di papa Leone XIV raccontati da Riccardo Benotti in «' + SERIE + '»: '
                   + ', '.join(v['titolo'] for v in cfg['viaggi'][:5]) + '.', 158), percorso, body, graph)
    return [(percorso, puntate[0]['data'])]
