"""Segnala a IndexNow (Bing, Yandex, Seznam, Naver…) le pagine aggiornate di recente.
Gira nel workflow di GitHub Pages dopo la pubblicazione."""
import datetime, json, os, re, urllib.request, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
key = (ROOT / 'data' / 'indexnow.key').read_text().strip()
sm = (ROOT / 'public' / 'sitemap.xml').read_text()
limite = '0000' if os.environ.get('INDEXNOW_TUTTE') == 'true' else (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
urls = [u for u, d in re.findall(r'<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', sm) if d >= limite]
urls = sorted(set(urls + ['https://riccardobenotti.it/', 'https://riccardobenotti.it/en/',
                          'https://riccardobenotti.it/filo/', 'https://riccardobenotti.it/llms.txt']))[:500]
body = json.dumps({'host': 'riccardobenotti.it', 'key': key,
                   'keyLocation': f'https://riccardobenotti.it/{key}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                             headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow', r.status, len(urls), 'URL')
except Exception as e:  # non bloccare la pubblicazione
    print('IndexNow non riuscito:', e)
    sys.exit(0)
