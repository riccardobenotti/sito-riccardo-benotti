# riccardobenotti.it

Sito personale di Riccardo Benotti. Statico, pubblicato con GitHub Pages dalla cartella `public/` (workflow `.github/workflows/pages.yml`).

- `data/filo.json`: le puntate di «Leone, il filo del giorno» (testo come su LinkedIn, grassetti Unicode compresi), con foto, credito e fonti.
- `data/config.json`: indirizzo del sito ed email pubblica.
- `src/body_it.html`, `src/footer_it.html`: testi della home italiana.
- `src/make_en.py`: ricava la versione inglese dall'italiana (coppie frase per frase).
- `src/build.py`: genera home, /en/, archivio /filo/, una pagina per puntata, sitemap e robots.

Per aggiornare: modificare i dati, poi `python3 src/make_en.py && python3 src/build.py` e fare commit.

## Aggiungere una puntata del filo

1. Aggiungere in cima a `data/filo.json` una voce con `data`, `slug` (di norma uguale alla data), `urn` (numero dell'attività LinkedIn), `titolo` e `testo` così come su LinkedIn, `credito`, `foto` (file in `public/img/filo/`, webp ~640 px) e `fonti` (lista di [titolo, url]).
2. `python3 src/build.py` rigenera home, archivio, pagina mensile, pagina della puntata, feed RSS e sitemap.
3. Commit e push: GitHub Pages pubblica in automatico.
