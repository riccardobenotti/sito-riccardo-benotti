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


# Paesi dei viaggi: sigla -> (nome italiano, nome inglese, Q-id Wikidata). Le bandiere sono in public/img/bandiere/<sigla>.svg.
PAESI = {'uy': ('Uruguay', 'Uruguay', 'Q77'), 'ar': ('Argentina', 'Argentina', 'Q414'), 'pe': ('Perù', 'Peru', 'Q419'),
         'fr': ('Francia', 'France', 'Q142'), 'es': ('Spagna', 'Spain', 'Q29'), 'mc': ('Principato di Monaco', 'Monaco', 'Q235'),
         'dz': ('Algeria', 'Algeria', 'Q262'), 'cm': ('Camerun', 'Cameroon', 'Q1009'), 'ao': ('Angola', 'Angola', 'Q916'),
         'gq': ('Guinea Equatoriale', 'Equatorial Guinea', 'Q983'), 'it': ('Italia', 'Italy', 'Q38')}


def bandiera(p, lingua='it'):
    """Bandierina accanto alla data quando il Papa è in viaggio all'estero. Campo "paese" (sigla) in filo.json:
    il paese in cui il Papa si trova nella giornata della puntata (non per annunci e puntate dopo il rientro)."""
    c = p.get('paese')
    if not c:
        return ''
    nome = html.escape(PAESI[c][0 if lingua == 'it' else 1])
    return f'<img class="bandiera" src="/img/bandiere/{c}.svg" width="18" height="12" alt="{nome}" title="{nome}">'


# Colori del paese: bande della bandiera ('v' = bande affiancate, 'h' = bande sovrapposte) e colori di accento per la cornice.
FASCE = {'uy': ('h', [('#FFFFFF', 1), ('#0038A8', 1)] * 4 + [('#FFFFFF', 1)]),
         'ar': ('h', [('#74ACDF', 1), ('#FFFFFF', 1), ('#74ACDF', 1)]),
         'pe': ('v', [('#D91023', 1), ('#FFFFFF', 1), ('#D91023', 1)]),
         'fr': ('v', [('#002654', 1), ('#FFFFFF', 1), ('#CE1126', 1)]),
         'es': ('h', [('#AA151B', 1), ('#F1BF00', 2), ('#AA151B', 1)]),
         'mc': ('h', [('#CE1126', 1), ('#FFFFFF', 1)]),
         'dz': ('v', [('#006233', 1), ('#FFFFFF', 1)]),
         'cm': ('v', [('#007A5E', 1), ('#CE1126', 1), ('#FCD116', 1)]),
         'ao': ('h', [('#CC092F', 1), ('#000000', 1)]),
         'gq': ('h', [('#3E9A00', 1), ('#FFFFFF', 1), ('#E32118', 1)]),
         'it': ('v', [('#009246', 1), ('#FFFFFF', 1), ('#CE2B37', 1)])}
ACCENTI = {'uy': ['#0038A8', '#FCD116'], 'ar': ['#74ACDF', '#F6B40E'], 'pe': ['#D91023', '#D91023'], 'fr': ['#002654', '#CE1126'],
           'es': ['#AA151B', '#F1BF00'], 'mc': ['#CE1126', '#CE1126'], 'dz': ['#006233', '#D21034'],
           'cm': ['#007A5E', '#CE1126', '#FCD116'], 'ao': ['#CC092F', '#000000'], 'gq': ['#3E9A00', '#E32118'], 'it': ['#009246', '#CE2B37']}


def fascia(c):
    """Gradiente a bande nette con l'orientamento vero della bandiera."""
    verso, segs = FASCE[c]
    tot = sum(w for _, w in segs)
    a, st = 0.0, []
    for col, w in segs:
        b = a + w / tot * 100
        st.append(f'{col} {a:.2f}% {b:.2f}%')
        a = b
    return f'linear-gradient({90 if verso == "v" else 180}deg, ' + ', '.join(st) + ')'


# Paesi la cui cornice riprende le bande della bandiera, senza stacchi: dall'interno verso l'esterno.
CORNICE_BANDE = {'ar': ['#74ACDF', '#FFFFFF', '#74ACDF']}


def cornice(c):
    """Righe sottili concentriche (ombre) attorno alla foto: un colore del paese per riga. Restituisce (box-shadow, ingombro in px).
    Per i paesi in CORNICE_BANDE le bande sono contigue, come nella bandiera."""
    if c in CORNICE_BANDE:
        sh, r = ['0 0 0 3px var(--passe)'], 3
        for col in CORNICE_BANDE[c]:
            r += 3
            sh.append(f'0 0 0 {r}px {col}')
        return ', '.join(sh), r
    sh, r = ['0 0 0 4px var(--passe)'], 4
    for col in ACCENTI[c]:
        sh.append(f'0 0 0 {r + 2}px {col}')
        sh.append(f'0 0 0 {r + 5}px var(--passe)')
        r += 5
    return ', '.join(sh[:-1]), r - 3


def attr_paese(p):
    c = p.get('paese')
    if not c:
        return ''
    ombra, ing = cornice(c)
    return f' data-paese="{c}" style="--bn:{fascia(c)};--cornice:{ombra};--cp:{ing}px"'


def nome_paese(p):
    c = p.get('paese')
    return f'<span class="paese-nome">{html.escape(PAESI[c][0])}</span>' if c else ''


SEGNO_HOME = re.search(r"^SEGNO = '(.*)'$", (pathlib.Path(__file__).parent / 'archivio.py').read_text(), re.M).group(1)
ROME = __import__('zoneinfo').ZoneInfo('Europe/Rome')


def taglia(t, n):
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) <= n:
        return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:.–—') + '…'


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
    plain = html.unescape(re.sub(r'<[^>]+>', '', paras_html[0])) if paras_html else ''
    # descrizione per i motori di ricerca: l'attacco della puntata, completato con il primo tema se è troppo breve
    desc = plain
    for altro in paras_html[1:]:
        if len(desc) >= 140:
            break
        desc += ' ' + html.unescape(re.sub(r'<[^>]+>', '', altro))
    titolo_txt = html.unescape(titolo)
    pub = datetime.datetime.fromtimestamp((int(p['urn']) >> 22) / 1000, ROME) if p.get('urn') else None
    return {**p, 'titolo_html': titolo, 'titolo_txt': titolo_txt, 'paras': paras_html, 'sommario': plain,
            'descrizione': taglia(desc, 158),
            'pubblicato': pub.isoformat(timespec='seconds') if pub else (p.get('pubblicato') or datetime.datetime.fromisoformat(p['data'] + 'T19:00:00').replace(tzinfo=ROME).isoformat()),
            'parole': len(re.sub(r'<[^>]+>', ' ', ' '.join(paras_html)).split()),
            'url': f'/filo/{p.get("slug") or p["data"]}/',
            'linkedin': f'https://www.linkedin.com/feed/update/urn:li:activity:{p["urn"]}/' if p.get('urn') else LINKEDIN + '/recent-activity/all/'}


def fonti_html(p):
    if not p.get('fonti'):
        return ''
    li = ''.join(f'<li><a href="{html.escape(u)}">{html.escape(t)}</a></li>' for t, u in p['fonti'])
    return f'<div class="fonti"><span class="label">Fonti</span><ul>{li}</ul></div>'


def meta_html(p):
    foto = f'<span>Foto {html.escape(p["credito"])}</span>' if p.get('credito') else ''
    return f'<div class="meta">{foto}<a href="{p["linkedin"]}">Leggi su LinkedIn</a></div>'


def fuoco(p):
    """Punto di ritaglio per le anteprime 3:2. Campo "fuoco" in filo.json (es. "50% 20%");
    per le foto verticali, se manca, si tiene la parte alta, dove di solito c'è il volto."""
    if not p.get('foto'):
        return ''
    if p.get('fuoco'):
        return f' style="object-position:{p["fuoco"]}"'
    from PIL import Image
    w, h = Image.open(PUB / 'img' / 'filo' / p['foto']).size
    return ' style="object-position:50% 22%"' if h > w * 0.8 else ''


def figura(p, cls='foto', lazy=True):
    if not p.get('foto'):
        return ''
    from PIL import Image
    w, h = Image.open(PUB / 'img' / 'filo' / p['foto']).size
    alt = html.escape(p.get('alt') or ('Foto della puntata del ' + data_it(p['data']) + ': ' + p['titolo_txt'])[:180])
    return (f'<figure class="{cls}"><img src="/img/filo/{p["foto"]}" width="{w}" height="{h}" alt="{alt}"'
            + fuoco(p) + (' loading="lazy"' if lazy else '') + '></figure>')


def home_items(puntate):
    out = []
    for k, p in enumerate(puntate[:3]):
        testa = (f'<time class="mono" datetime="{p["data"]}">{data_it(p["data"])}</time>{nome_paese(p)}'
                 f'<h3><a class="tit" href="{p["url"]}">{p["titolo_html"]}</a></h3>')
        if k == 0:
            corpo = (f'<div class="testo">{p["paras"][0]}</div>'
                     f'<details><summary>Continua a leggere</summary><div class="testo">{"".join(p["paras"][1:])}</div>'
                     f'{fonti_html(p)}{meta_html(p)}</details>')
        else:
            corpo = (f'<details><summary>Leggi la puntata</summary><div class="testo">{"".join(p["paras"])}</div>'
                     f'{fonti_html(p)}{meta_html(p)}</details>')
        cls = 'puntata ultima' if k == 0 else 'puntata'
        out.append(f'\n      <li class="{cls}"{attr_paese(p)}>\n        <div class="corpo">{testa}{corpo}</div>\n        {figura(p, lazy=k > 0)}\n      </li>')
    return ''.join(out) + '\n    '


CSS_VER = None


ROBOTS = '<meta name="robots" content="max-image-preview:large, max-snippet:-1, max-video-preview:-1">'


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
<meta name="msvalidate.01" content="30EC3B24ACA589BA91D97B8485001137">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{ROBOTS}
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
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/img/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/newsreader-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={CSS_VER}">
<link rel="alternate" type="application/rss+xml" title="Leone, il filo del giorno" href="{SITE}/filo/feed.xml">
{ld}{extra}<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "5dbe16ea38a5458b937287b9e55afe86"}}'></script>
</head>
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
    li = ''.join(f'\n      <li><a class="link" href="{"/filo/" if (a == "filo" and not home and lang == "it") else pre + "#" + a}">{t}</a></li>' for a, t in voci)
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
        "givenName": "Riccardo", "familyName": "Benotti",
        "url": SITE + "/", "mainEntityOfPage": SITE + "/",
        "image": {"@type": "ImageObject", "url": SITE + "/img/riccardo-benotti-foto.jpg", "caption": "Riccardo Benotti", "creditText": "Riccardo Benotti", "copyrightNotice": "© Riccardo Benotti", "creator": {"@id": SITE + "/#riccardo-benotti"}, "license": SITE + "/crediti/", "acquireLicensePage": SITE + "/crediti/"},
        "birthDate": "1982-12-28",
        "birthPlace": {"@type": "Place", "name": "Roma", "sameAs": "https://www.wikidata.org/wiki/Q220"},
        "hasOccupation": {"@type": "Occupation", "name": "Giornalista", "sameAs": "https://www.wikidata.org/wiki/Q1930187"},
        "jobTitle": "Caposervizio",
        "description": "Giornalista professionista e autore italiano, caposervizio dell'agenzia SIR – Servizio Informazione Religiosa, accreditato presso la Sala Stampa della Santa Sede.",
        "worksFor": {"@type": "NewsMediaOrganization", "name": "SIR – Servizio Informazione Religiosa", "url": "https://www.agensir.it",
                     "sameAs": "https://www.wikidata.org/wiki/Q12050678"},
        "memberOf": {"@type": "Organization", "name": "Commissione Film CEI", "url": "https://www.commissionefilmcei.it/"},
        "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "Dottorato di ricerca",
                          "educationalLevel": "Dottorato di ricerca in Scienze della comunicazione sociale", "dateCreated": "2025-12-17T00:00:00+01:00",
                          "recognizedBy": {"@id": SITE + "/#ups"}},
        "alumniOf": {"@type": "CollegeOrUniversity", "@id": SITE + "/#ups", "name": "Università Pontificia Salesiana",
                     "url": "https://www.unisal.it", "sameAs": "https://www.wikidata.org/wiki/Q543289"},
        "homeLocation": {"@type": "Place", "name": "Roma"},
        "nationality": {"@type": "Country", "name": "Italia"},
        "knowsLanguage": ["it", "en"],
        "knowsAbout": ["Santa Sede", "Chiesa cattolica", "Giornalismo", "Intelligenza artificiale", "Comunicazione ecclesiale", "Vita religiosa"],
        "identifier": [
            {"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0000-5747-2592", "url": "https://orcid.org/0009-0000-5747-2592"},
            {"@type": "PropertyValue", "propertyID": "VIAF", "value": "86365863", "url": "https://viaf.org/viaf/86365863"},
            {"@type": "PropertyValue", "propertyID": "ISNI", "value": "0000 0001 1494 8837", "url": "https://isni.org/isni/0000000114948837"},
            {"@type": "PropertyValue", "propertyID": "SBN", "value": "IT\\ICCU\\MILV\\332562", "url": "https://opac.sbn.it/risultati-autori/-/opac-autori/detail/MILV332562"},
            {"@type": "PropertyValue", "propertyID": "Library of Congress Name Authority", "value": "no2009058363", "url": "https://id.loc.gov/authorities/names/no2009058363.html"},
            {"@type": "PropertyValue", "propertyID": "BnF", "value": "16262240v", "url": "https://catalogue.bnf.fr/ark:/12148/cb16262240v"},
            {"@type": "PropertyValue", "propertyID": "Wikidata", "value": "Q141757006", "url": "https://www.wikidata.org/wiki/Q141757006"},
        ],
        "sameAs": ["https://orcid.org/0009-0000-5747-2592", "https://scholar.google.com/citations?user=HPVbAx0AAAAJ", LINKEDIN,
                   "https://www.edizionisanpaolo.it/autore/riccardo-benotti.aspx",
                   "https://www.agensir.it/author/r-benotti/", "https://www.avvenire.it/redazione/riccardo-benotti-3476"] + CFG.get('sameAs_extra', []),
    }


BOOKS = [
    ("Governare il patrimonio ecclesiale nell'era dell'IA. Discernimento, governance e asset management per enti religiosi", "Marcianum Press", "2026-12-04", "9791256272440", 320, None),
    ("Covid-19: preti in prima linea. Storie stra-ordinarie di chi ha dato la vita e di chi non si è arreso", "San Paolo", "2021", "9788892223813", 464, "Q141757041"),
    ("Viaggio nella vita religiosa. Interviste e incontri", "Libreria Editrice Vaticana", "2016", "9788820997304", 232, "Q141757042"),
    ("Viaggio nel New Journalism americano", "Aracne", "2009", "9788854822931", 143, "Q141757043"),
]


def ld_home():
    import datetime
    from zoneinfo import ZoneInfo
    oggi = datetime.datetime.now(ZoneInfo("Europe/Rome")).replace(microsecond=0).isoformat()
    g = [{"@type": "ProfilePage", "@id": SITE + "/#profilo", "url": SITE + "/", "name": "Riccardo Benotti",
          "mainEntity": {"@id": SITE + "/#riccardo-benotti"}, "isPartOf": {"@id": SITE + "/#sito"},
          "dateCreated": "2026-10-17T19:00:00+02:00", "dateModified": oggi, "inLanguage": "it"},
         person_ld(), {"@type": "WebSite", "@id": SITE + "/#sito", "url": SITE + "/", "name": "Riccardo Benotti",
                       "inLanguage": ["it", "en"], "publisher": {"@id": SITE + "/#riccardo-benotti"}}]
    for n, pub, y, isbn, pp, q in BOOKS:
        libro = {"@type": "Book", "name": n, "author": {"@id": SITE + "/#riccardo-benotti"},
                 "publisher": {"@type": "Organization", "name": pub}, "datePublished": y, "isbn": isbn,
                 "numberOfPages": pp, "inLanguage": "it"}
        if q:
            libro["sameAs"] = "https://www.wikidata.org/wiki/" + q
        if isbn == "9791256272440":
            libro["author"] = [{"@id": SITE + "/#riccardo-benotti"}, {"@type": "Person", "name": "Dario Sgrulletti"}]
            libro["contributor"] = {"@type": "Person", "name": "Giuseppe Baturi", "roleName": "Prefazione"}
            libro["image"] = SITE + "/img/cover-governare-patrimonio.webp"
            libro["bookFormat"] = "https://schema.org/Paperback"
            libro["url"] = "https://www.governareilpatrimonio.it/"
        g.append(libro)
    g.append({"@type": "Thesis", "name": "Intelligenza artificiale e giornalismo. Un'indagine sui pro e contro di una possibile implementazione di sistemi IA nelle redazioni cattoliche della CEI e della Santa Sede",
              "author": {"@id": SITE + "/#riccardo-benotti"}, "datePublished": "2025-12-17", "inLanguage": "it",
              "contributor": {"@type": "Person", "name": "Fabio Pasqualetti", "roleName": "Relatore"},
              "inSupportOf": "Dottorato di ricerca in Scienze della comunicazione sociale",
              "sourceOrganization": {"@id": SITE + "/#ups"}, "sameAs": "https://www.wikidata.org/wiki/Q141757044"})
    g.append({"@type": "ScholarlyArticle", "name": "A Tool, Not a Voice: Artificial Intelligence, Human Speech, and Christian Communicative Agency",
              "author": {"@id": SITE + "/#riccardo-benotti"}, "datePublished": "2026-11-03", "inLanguage": "en",
              "isPartOf": {"@type": "Periodical", "name": "Philosophia Reformata", "issn": ["0031-8035", "2352-8230"]},
              "identifier": {"@type": "PropertyValue", "propertyID": "DOI", "value": "10.1163/23528230-bja10144"},
              "url": "https://doi.org/10.1163/23528230-bja10144",
              "sameAs": ["https://doi.org/10.1163/23528230-bja10144", "https://www.wikidata.org/wiki/Q141985776"]})
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
    var ko = function () {
      var el = document.getElementById(b.getAttribute('data-copia'));
      try { var r = document.createRange(); r.selectNodeContents(el); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); } catch (e) {}
      var o = b.textContent; b.textContent = b.getAttribute('data-ko'); setTimeout(function () { b.textContent = o; }, 4000);
    };
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(t).then(done, ko); } else { ko(); }
  });
});
var menu = document.querySelector('.nav ul');
if (menu) { var f = function () { menu.closest('.nav').classList.toggle('fine', menu.scrollLeft + menu.clientWidth >= menu.scrollWidth - 4); }; menu.addEventListener('scroll', f, {passive: true}); f(); }
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
                                          key=lambda x: (x['data'], x.get('slug', '')), reverse=True)]
    oggi = datetime.date.today().isoformat()
    urls = []

    # Home IT
    body = (SRC / 'body_it.html').read_text().replace('{{FILO}}', home_items(puntate)).replace('{{SEGNO}}', SEGNO_HOME).replace('{{CONTATTO}}', contatto('it')).replace('{{N_PUNTATE}}', str(len(puntate)))
    page = head('it', 'Riccardo Benotti – Giornalista e autore',
                'Riccardo Benotti, giornalista professionista e autore, caposervizio del SIR – Servizio Informazione Religiosa. Chiesa, Santa Sede, comunicazione e intelligenza artificiale.',
                '/', alt=[('it', '/'), ('en', '/en/'), ('x-default', '/')], og_type='profile', jsonld=ld_home())
    page += nav('it', True, '/en/') + '<main id="contenuto">' + body + '</main>' + footer('it') + COPY_JS + '</body>\n</html>\n'
    write('/', page); urls.append(('/', oggi))

    # Home EN
    body = (SRC / 'body_en.html').read_text()
    ultime = ''.join(f'<li><time class="mono" datetime="{p["data"]}">{data_en(p["data"])}{bandiera(p, "en")}</time> <a href="{p["url"]}" hreflang="it" lang="it">{p["titolo_html"]}</a></li>' for p in puntate[:5])
    body = body.replace('{{FILO_EN}}', ultime).replace('{{SEGNO}}', SEGNO_HOME).replace('{{CONTATTO}}', contatto('en'))
    ld = {"@context": "https://schema.org", "@graph": [{**person_ld(), "jobTitle": "Senior editor",
          "description": "Italian journalist and author, senior editor at SIR – Servizio Informazione Religiosa, the news agency of the Italian Bishops' Conference, accredited to the Holy See Press Office."}]}
    page = head('en', 'Riccardo Benotti – Journalist and author',
                'Riccardo Benotti is an Italian journalist and author, senior editor at SIR, the news agency of the Italian Bishops’ Conference. The Pope, the Holy See, the Church, and AI in journalism.',
                '/en/', alt=[('it', '/'), ('en', '/en/'), ('x-default', '/')], og_type='profile', jsonld=ld)
    page += nav('en', True, '/') + '<main id="contenuto">' + body + '</main>' + footer('en') + COPY_JS + '</body>\n</html>\n'
    write('/en/', page); urls.append(('/en/', oggi))

    TEMI = calcola_temi(puntate)
    urls += archivio(puntate)
    urls += temi(puntate, TEMI)
    urls += viaggi(puntate)

    # crediti delle immagini (licenza e acquisizione per i metadati immagine)
    body = '''<div class="wrap"><main class="pagina"><span class="label gold">Note</span>
    <h1>Crediti delle immagini</h1>
    <p>Il ritratto di Riccardo Benotti pubblicato su questo sito è di sua proprietà. Per utilizzarlo, ad esempio nei materiali di presentazione di un incontro, scrivere a <a href="mailto:info@riccardobenotti.it">info@riccardobenotti.it</a>.</p>
    <p>Le fotografie delle puntate di «Leone, il filo del giorno» sono di Vatican Media, salvo diversa indicazione nella didascalia, e sono pubblicate a corredo dell’informazione con il credito dell’autore. I diritti restano ai titolari: per riutilizzarle occorre rivolgersi a Vatican Media.</p>
    <p>Le copertine dei libri sono riprodotte per illustrare i volumi e appartengono ai rispettivi editori.</p>
    <p lang="en">Image credits: the portrait belongs to Riccardo Benotti (contact info@riccardobenotti.it for use). Photos in “Leone, il filo del giorno” are by Vatican Media unless stated otherwise; rights remain with the copyright holders.</p></main></div>
'''
    page = head('it', 'Crediti delle immagini | Riccardo Benotti', 'Crediti e diritti delle immagini pubblicate su riccardobenotti.it.', '/crediti/')
    write('/crediti/', page + nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n')
    urls.append(('/crediti/', oggi))

    # 404
    body = '''<div class="wrap"><main class="pagina"><span class="label gold">Errore 404</span>
    <h1>Pagina non trovata</h1><p>L’indirizzo potrebbe essere cambiato. Torna alla <a href="/">home</a> o all’<a href="/filo/">archivio del filo del giorno</a>.</p>
    <p lang="en">Page not found. Go to the <a href="/en/">English home page</a>.</p></main></div>
'''
    page = head('it', 'Pagina non trovata | Riccardo Benotti', 'Pagina non trovata.', '/404.html')
    page = page.replace(ROBOTS, '<meta name="robots" content="noindex">')
    write('/404.html', page + nav('it', False, '/en/') + body + footer('it') + '</body>\n</html>\n')

    # sitemap e robots
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    for u, d, *img in urls:
        sm += f'  <url><loc>{SITE + u}</loc><lastmod>{d}</lastmod>'
        if img and img[0]:
            sm += f'<image:image><image:loc>{SITE}/img/{img[0]}</image:loc></image:image>'
        if u in ('/', '/en/'):
            sm += f'<xhtml:link rel="alternate" hreflang="it" href="{SITE}/"/><xhtml:link rel="alternate" hreflang="en" href="{SITE}/en/"/>'
        sm += '</url>\n'
    sm += '</urlset>\n'
    write('/sitemap.xml', sm)
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User',
            'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot', 'Applebot-Extended',
            'Bingbot', 'Googlebot', 'DuckAssistBot', 'MistralAI-User', 'CCBot']
    robots = ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)
    write('/robots.txt', robots + f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/sitemap-news.xml\n')
    # sitemap per Google News: solo le puntate delle ultime 48 ore
    adesso = datetime.datetime.now(datetime.timezone.utc)
    news = ''
    for p in puntate:
        try:
            dt = datetime.datetime.fromisoformat(p['pubblicato'])
        except ValueError:
            continue
        if dt.tzinfo and adesso - dt <= datetime.timedelta(hours=48):
            news += (f'  <url><loc>{SITE}{p["url"]}</loc><news:news><news:publication><news:name>Riccardo Benotti</news:name>'
                     f'<news:language>it</news:language></news:publication><news:publication_date>{p["pubblicato"]}</news:publication_date>'
                     f'<news:title>{html.escape(p["titolo_txt"])}</news:title></news:news></url>\n')
    write('/sitemap-news.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + news + '</urlset>\n')
    # scheda per assistenti IA (llms.txt)
    ultima = puntate[0]['data'] if puntate else ''
    write('/llms.txt', (SRC / 'llms.txt').read_text().replace('{{N_PUNTATE}}', str(len(puntate)))
          .replace('{{ULTIMA}}', data_it(ultima) if ultima else ''))
    # chiave IndexNow (Bing e altri motori)
    k = (ROOT / 'data' / 'indexnow.key').read_text().strip()
    write(f'/{k}.txt', k)
    print(f'OK: {len(puntate)} puntate, {len(urls)} pagine in sitemap')


exec((SRC / 'archivio.py').read_text())
exec((SRC / 'temi.py').read_text())
exec((SRC / 'viaggi.py').read_text())


if __name__ == '__main__':
    main()
