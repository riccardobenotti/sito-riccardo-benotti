#!/usr/bin/env python3
"""Ricava src/body_en.html e src/footer_en.html dalla versione italiana.
Ogni coppia (italiano, inglese) deve comparire nel testo: se una frase italiana
cambia, lo script si ferma e segnala la coppia da aggiornare."""
import pathlib, re, sys
SRC = pathlib.Path(__file__).resolve().parent
it = (SRC / 'body_it.html').read_text()
foot = (SRC / 'footer_it.html').read_text()

# 1. tolgo la sezione del filo (in inglese va in fondo, in forma breve)
a = it.index('  <section id="filo"'); b = it.index('</section>', a) + len('</section>\n')
en = it[:a] + it[b:]

FILO_EN = '''
  <section id="filo">
    <div class="sec">
      <h2 class="label">Daily column</h2>
      <div class="prose">
        <h2 class="big">Leone, <em>il filo del giorno</em></h2>
        {{SEGNO}}
        <p>Every day Riccardo writes a daily account of Pope Leo XIV’s news and engagements, held together by a single thread: the <i>filo del giorno</i>. The column is published in Italian on this site and on <a href="https://www.linkedin.com/in/riccardo-benotti-0a0534362">LinkedIn</a>. Latest instalments:</p>
        <ol class="filo-en">{{FILO_EN}}</ol>
        <p><a href="/filo/" hreflang="it">Full archive</a> (in Italian)</p>
      </div>
    </div>
  </section>
'''
k = en.index('  <section id="contatti">')
en = en[:k] + FILO_EN + '\n' + en[k:]

PAIRS = [
    # ids
    ('<section id="profilo">', '<section id="profile">'),
    ('<section id="libri">', '<section id="books">'),
    ('<section id="scritti">', '<section id="writing">'),
    ('<section id="ricerca">', '<section id="research">'),
    ('<section id="contatti">', '<section id="contact">'),
    ('href="#ricerca"', 'href="#research"'),
    # hero
    ('Giornalista professionista · Accreditato alla Sala Stampa della Santa Sede', 'Journalist · Accredited to the Holy See Press Office'),
    ('Racconta il Papa e la Chiesa per il SIR, l’agenzia della Conferenza episcopale italiana, e studia come l’intelligenza artificiale cambia il giornalismo.',
     'He reports on the Pope and the Church for SIR, the news agency of the Italian Bishops’ Conference, and studies how artificial intelligence is changing journalism.'),
    ('alt="Ritratto di Riccardo Benotti"', 'alt="Portrait of Riccardo Benotti"'),
    ('<dd>Caposervizio, in redazione dal 2006</dd>', '<dd>Senior editor, on staff since 2006</dd>'),
    ('<dt class="label">Libri</dt><dd>Quattro libri, due nuovi progetti editoriali</dd>', '<dt class="label">Books</dt><dd>Four books, two new projects</dd>'),
    ('<dt class="label">Commissione Film Cei</dt><dd>Membro dal 2020, mandato attuale 2024–2029</dd>', '<dt class="label">CEI Film Commission</dt><dd>Member since 2020, current term 2024–2029</dd>'),
    ('<dt class="label">Dottorato</dt><dd>Università Pontificia Salesiana, 2025</dd>', '<dt class="label">PhD</dt><dd>Pontifical Salesian University, 2025</dd>'),
    # profilo
    ('<p class="label">Profilo</p>', '<p class="label">Profile</p>'),
    ('Raccontare la Chiesa, capire come cambia il giornalismo', 'Reporting on the Church, understanding how journalism is changing'),
    ('<p>Riccardo Benotti è giornalista professionista e autore. Dal 2006 lavora al SIR, il Servizio Informazione Religiosa, dove oggi è caposervizio. Segue il Papa, la Santa Sede e la vita della Chiesa in Italia e nel mondo ed è accreditato presso la Sala Stampa della Santa Sede.</p>',
     '<p>Riccardo Benotti is an Italian professional journalist and author. He has worked since 2006 at SIR, the Servizio Informazione Religiosa, where he is now a senior editor. He covers the Pope, the Holy See and the life of the Church in Italy and around the world, and is accredited to the Holy See Press Office.</p>'),
    ('<p>Si è laureato in Scienze della comunicazione sociale, con specializzazione in giornalismo, all’Università Pontificia Salesiana, dove nel 2025 ha conseguito il dottorato di ricerca. Studia il rapporto tra comunicazione, cultura e società, con attenzione a come l’intelligenza artificiale trasforma il lavoro delle redazioni.</p>',
     '<p>He holds a degree in Social Communication, specialising in journalism, from the Pontifical Salesian University in Rome, where he also earned his doctorate in 2025. His research looks at communication, culture and society, with a focus on how artificial intelligence is reshaping the work of newsrooms.</p>'),
    ('<p>È membro della Commissione Film Cei dal 2020, oggi per il mandato 2024–2029, e collabora con il Gruppo interdisciplinare di osservazione e studio sulla disabilità del Servizio nazionale Cei per la pastorale delle persone con disabilità. Interviene in corsi e incontri sulla comunicazione digitale, sul piano editoriale e sull’intelligenza artificiale.</p>',
     '<p>He has sat on the Film Commission of the Italian Bishops’ Conference since 2020, now for the 2024–2029 term, and contributes to the Conference’s interdisciplinary study group on disability. He teaches courses and workshops on digital communication, editorial planning and artificial intelligence.</p>'),
    ('<h3>Il Papa e la Santa Sede</h3>', '<h3>The Pope and the Holy See</h3>'),
    ('Il pontificato di Leone XIV, la Curia romana, la diplomazia vaticana, le nomine e i documenti.', 'The pontificate of Leo XIV, the Roman Curia, Vatican diplomacy, appointments and documents.'),
    ('<h3>Chiesa e vita religiosa</h3>', '<h3>Church and religious life</h3>'),
    ('Diocesi, comunità, ordini e congregazioni: la vita ecclesiale raccontata dall’agenzia della Cei.', 'Dioceses, communities, orders and congregations: church life as reported by the Italian bishops’ news agency.'),
    ('<h3>Intelligenza artificiale e giornalismo</h3>', '<h3>Artificial intelligence and journalism</h3>'),
    ('Che cosa le redazioni affidano agli strumenti automatici e dove resta la responsabilità di chi firma.', 'What newsrooms hand over to automated tools, and where responsibility stays with the person who signs the piece.'),
    # libri
    ('<h2 class="label">Libri</h2>', '<h2 class="label">Books</h2>'),
    ('<span class="label gold">In pubblicazione</span>', '<span class="label gold">Forthcoming</span>'),
    ('Marcianum Press · collana Il Crogiolo', 'Marcianum Press · Il Crogiolo series'),
    ('alt="Copertina di Governare il patrimonio ecclesiale nell’era dell’IA"', 'alt="Cover of Governare il patrimonio ecclesiale nell’era dell’IA"'),
    ('2026 · Marcianum Press · con Dario Sgrulletti', '2026 · Marcianum Press · with Dario Sgrulletti'),
    ('<p>Come governare i beni di diocesi e congregazioni quando l’intelligenza artificiale entra nelle analisi e nelle decisioni finanziarie: un quadro di governo per economi, superiori e amministratori, con checklist, modelli e glossario. Il principio è uno: «L’esecuzione si delega, la coscienza no». Prefazione di mons. Giuseppe Baturi, note introduttive di padre Arturo Sosa e suor Oonah O’Shea.</p>',
     '<p>How to govern the assets of dioceses and religious congregations once artificial intelligence enters financial analysis and decision-making: a governance framework for bursars, superiors and administrators, with checklists, templates and a glossary. One principle runs through it: “Execution can be delegated, conscience cannot.” Preface by Archbishop Giuseppe Baturi, with introductory notes by Fr Arturo Sosa and Sr Oonah O’Shea.</p>'),
    ('<span class="label gold uscita">In libreria dal 4 dicembre 2026</span>', '<span class="label gold uscita">In bookshops from 4 December 2026</span>'),
    ('<div class="dati"><span>320 pagine</span>', '<div class="dati"><span>320 pages</span>'),
    ('">Il sito del libro</a>', '">The book’s website</a>'),
    ('LAS · in produzione', 'LAS · in production'),
    ('alt="Copertina di Covid-19: preti in prima linea"', 'alt="Cover of Covid-19: preti in prima linea"'),
    ('alt="Copertina di Viaggio nella vita religiosa"', 'alt="Cover of Viaggio nella vita religiosa"'),
    ('alt="Copertina di Viaggio nel New Journalism americano"', 'alt="Cover of Viaggio nel New Journalism americano"'),
    ('<p>Testimonianze di sacerdoti negli anni della pandemia e il ricordo dei preti diocesani italiani morti in quel periodo. Presentazione del cardinale Gualtiero Bassetti, prefazione del cardinale Angelo De Donatis.</p>',
     '<p>Accounts from priests during the pandemic years, and a memorial to the Italian diocesan priests who died in that period. Introduced by Cardinal Gualtiero Bassetti, with a preface by Cardinal Angelo De Donatis.</p>'),
    ('<span>464 pagine</span>', '<span>464 pages</span>'),
    ('Scheda dell’editore', 'Publisher’s page'),
    ('<p>Incontri con quattordici superiori generali, usciti per la chiusura dell’Anno della vita consacrata: i carismi della Chiesa raccontati da chi li guida.</p>',
     '<p>Conversations with fourteen superiors general, published for the close of the Year of Consecrated Life: the charisms of the Church described by those who lead them.</p>'),
    ('<span>232 pagine</span><span>Prefazione di Timothy Radcliffe</span>', '<span>232 pages</span><span>Preface by Timothy Radcliffe</span>'),
    ('Catalogo SBN</a><a href="https://viaggionellavitareligiosa.wordpress.com/">Il blog del libro</a>', 'Italian national library catalogue</a><a href="https://viaggionellavitareligiosa.wordpress.com/">The book’s blog</a>'),
    ('<p>Un percorso nella stagione del giornalismo narrativo statunitense, i suoi autori e le sue tecniche.</p>', '<p>A journey through the era of American narrative journalism, its authors and its techniques.</p>'),
    ('<span>143 pagine</span>', '<span>143 pages</span>'),
    ('">Catalogo SBN</a></div>', '">Italian national library catalogue</a></div>'),
    # scritti
    ('<h2 class="label">Scritti e interventi</h2>', '<h2 class="label">Writing and talks</h2>'),
    ('<h3 class="label gold sub-h">Articoli scelti</h3>', '<h3 class="label gold sub-h">Selected articles</h3>'),
    ('Sette testi per conoscere la scrittura: racconto, commento, critica dei media, intervista. Tutti gli articoli firmati per il SIR sono nella <a href="https://www.agensir.it/author/r-benotti/">pagina autore di agensir.it</a>.',
     'Seven pieces that show the range of his writing: personal narrative, commentary, media criticism and interviews. All are in Italian except the interview with Bishop Cantú, which SIR also published in English. His signed SIR articles are collected on his <a href="https://www.agensir.it/author/r-benotti/">agensir.it author page</a>.'),
    ('<h4><a href="https://www.agensir.it/chiesa/2026/09/22/intelligenza-artificiale-e-big-tech-mons-cantu-vescovi-usa-non-diamo-il-nostro-avallo-alle-aziende/">Intelligenza artificiale e big tech. Mons. Cantú (vescovi Usa): “Non diamo il nostro avallo alle aziende”</a></h4>',
     '<h4><a href="https://www.agensir.it/chiesa/2026/09/22/artificial-intelligence-and-big-tech-bishop-cantu-u-s-bishops-we-do-not-endorse-companies/" hreflang="en">Artificial intelligence and big tech. Bishop Cantú (U.S. bishops): “We do not endorse companies”</a></h4>'),
    ('<h3 class="label gold sub-h">In tv e in video</h3>', '<h3 class="label gold sub-h">On TV and video</h3>'),
    ('<p class="nota-sel">Partecipazioni televisive, presentazioni e incontri disponibili su YouTube.</p>', '<p class="nota-sel">Television appearances, book presentations and talks available on YouTube (in Italian).</p>'),
    ('<span class="label tipo">Telepace · «Fatti e prospettive»</span>', '<span class="label tipo">Telepace · “Fatti e prospettive”</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=D5MZ6gDz7L4">Ospite in studio sull’attualità</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=D5MZ6gDz7L4">Studio guest on current affairs</a></h4>'),
    ('<p>28 gennaio 2026.</p>', '<p>28 January 2026.</p>'),
    ('<span class="label tipo">Padre Pio TV · «Just Today»</span>', '<span class="label tipo">Padre Pio TV · “Just Today”</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=wzwT2HnoCoQ">Verso il Conclave per eleggere il nuovo Papa</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=wzwT2HnoCoQ">Towards the conclave to elect the new Pope</a></h4>'),
    ('<p>Intervista, 7 maggio 2025.</p>', '<p>Interview, 7 May 2025.</p>'),
    ('<h4><a href="https://www.youtube.com/watch?v=5K3EV6uI52A">Papa Francesco e l’informazione, nel Giubileo del mondo della comunicazione</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=5K3EV6uI52A">Pope Francis and the news media, at the Jubilee of the World of Communications</a></h4>'),
    ('<p>Intervista, 25 gennaio 2025.</p>', '<p>Interview, 25 January 2025.</p>'),
    ('<h4><a href="https://www.youtube.com/watch?v=54D1ZAGsOPs">Presentazione di «Covid-19: preti in prima linea»</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=54D1ZAGsOPs">Presenting “Covid-19: preti in prima linea”</a></h4>'),
    ('<p>In dialogo con don Roberto Cassano, settembre 2021.</p>', '<p>In conversation with Fr Roberto Cassano, September 2021.</p>'),
    ('<span class="label tipo">Caritas diocesana di Firenze</span>', '<span class="label tipo">Caritas of the Archdiocese of Florence</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=4TrUKsO0pcA">La persona con disabilità nella comunità cristiana. Occasione o tentazione?</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=4TrUKsO0pcA">People with disabilities in the Christian community: opportunity or temptation?</a></h4>'),
    ('<p>Moderatore dell’incontro, maggio 2021.</p>', '<p>Moderator, May 2021.</p>'),
    ('<span class="label tipo">Libreria San Paolo Laterano</span>', '<span class="label tipo">San Paolo Laterano bookshop</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=skWyayBaPyw">Presentazione di «Covid-19: preti in prima linea»</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=skWyayBaPyw">Presenting “Covid-19: preti in prima linea”</a></h4>'),
    ('<p>Diretta, 5 maggio 2021.</p>', '<p>Live stream, 5 May 2021.</p>'),
    ('<span class="label tipo">Tv2000 · «L’Ora Solare»</span>', '<span class="label tipo">Tv2000 · “L’Ora Solare”</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=JIzh9bfEVQI">I sacerdoti morti durante la pandemia</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=JIzh9bfEVQI">The priests who died during the pandemic</a></h4>'),
    ('<p>Ospite in studio, 18 marzo 2021.</p>', '<p>Studio guest, 18 March 2021.</p>'),
    ('<span class="label tipo">Tg2 · «Costume e società»</span>', '<span class="label tipo">Tg2 · “Costume e società”</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=27dl6HbfgT4">Servizio su «Viaggio nella vita religiosa»</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=27dl6HbfgT4">Report on “Viaggio nella vita religiosa”</a></h4>'),
    ('<p>4 aprile 2016.</p>', '<p>4 April 2016.</p>'),
    ('<span class="label tipo">Tv2000 · «Siamo noi»</span>', '<span class="label tipo">Tv2000 · “Siamo noi”</span>'),
    ('<h4><a href="https://www.youtube.com/watch?v=MFSCrccHc94">Vita consacrata: uomini e donne per «svegliare il mondo»</a></h4>', '<h4><a href="https://www.youtube.com/watch?v=MFSCrccHc94">Consecrated life: men and women to “wake up the world”</a></h4>'),
    ('<p>Ospite in studio, 2 febbraio 2016.</p>', '<p>Studio guest, 2 February 2016.</p>'),
    ('SIR · Intervista', 'SIR · Interview'), ('SIR · Commento', 'SIR · Commentary'), ('SIR · Critica dei media', 'SIR · Media criticism'),
    ('SIR · Approfondimento', 'SIR · Feature'), ('Avvenire · Racconto personale', 'Avvenire · Personal essay'), ('Vocazioni · Reportage', 'Vocazioni · Reportage'),
    ('<p>Il vescovo di San José, nella Silicon Valley, guida la task force dei vescovi statunitensi sull’intelligenza artificiale: dialogo con le aziende, tutele per gli utenti, le stesse regole dentro la Chiesa.</p>',
     '<p>The Bishop of San José, in Silicon Valley, leads the US bishops’ task force on artificial intelligence: dialogue with companies, safeguards for users, the same rules inside the Church.</p>'),
    ('<p>La morte di un sacerdote in diretta Facebook, in Ecuador, diventa in poche ore materia di scherno: una riflessione sulla dignità della persona davanti allo schermo e sugli algoritmi che premiano l’emozione rapida.</p>', '<p>A priest’s death during a Mass streamed on Facebook in Ecuador turns into online mockery within hours: a reflection on human dignity in front of the screen and on algorithms that reward instant emotion.</p>'),
    ('<p>Da una poesia scritta in carcere, una riflessione sulla dignità della persona e sul senso della pena.</p>', '<p>A poem written in prison prompts a reflection on human dignity and the meaning of punishment.</p>'),
    ('<p><i>Temptation Island</i> letto attraverso il montaggio e il giudizio che costruisce nello spettatore.</p>', '<p>An analysis of how the editing of Italy’s <i>Temptation Island</i> shapes the viewer’s judgement.</p>'),
    ('<p>Che cosa accade quando l’incontro digitale con la fede resta senza radici in una comunità.</p>', '<p>What happens when an encounter with faith that begins online never takes root in a community.</p>'),
    ('<p>Tor Vergata, 2000–2025: la Gmg vissuta da giovane e il ritorno venticinque anni dopo, da cronista.</p>', '<p>Tor Vergata, 2000–2025: World Youth Day as a young man, and the return twenty-five years later as a reporter.</p>'),
    ('<p>Una parrocchia raccontata dentro una celebrazione, con le voci di don Luigi D’Errico e di mons. Lojudice. <i>Vocazioni</i>, n. 3, maggio–giugno.</p>',
     '<p>A report from a parish Mass, with the voices of Fr Luigi D’Errico and Bishop Lojudice. <i>Vocazioni</i>, no. 3, May–June.</p>'),
    ('<h3 class="label gold sub-h">Saggi e contributi in rivista</h3>', '<h3 class="label gold sub-h">Essays and journal contributions</h3>'),
    ('Alcuni tra i contributi in volume e in rivista. Gli articoli scientifici sono nella sezione <a href="#research">Ricerca</a>.', 'A selection of book chapters and journal pieces. Peer-reviewed articles are listed under <a href="#research">Research</a>.'),
    ('<span class="label tipo">Saggio in volume</span>', '<span class="label tipo">Book chapter</span>'),
    ('<p>In Vincenzo Corrado e Alessandra Carenzio (a cura di), ', '<p>In Vincenzo Corrado and Alessandra Carenzio (eds.), '),
    ('Scholé, Brescia 2026, pp. 169 ss.', 'Scholé, Brescia 2026, pp. 169 ff.'),
    ('<span class="label tipo">Articolo in rivista</span>', '<span class="label tipo">Journal article</span>'),
    ('anno 7, n. 1, pp. 123–129.', 'vol. 7, no. 1, pp. 123–129.'),
    ('<p><i>Vocazioni</i>, n. 2, marzo–aprile 2017.</p>', '<p><i>Vocazioni</i>, no. 2, March–April 2017.</p>'),
    ('<h3 class="label gold sub-h">Relazioni e corsi</h3>', '<h3 class="label gold sub-h">Talks and courses</h3>'),
    ('Alcuni tra gli interventi a convegni, corsi e incontri di formazione.', 'A selection of conference papers, courses and training sessions.'),
    ('Relazione · video preregistrato', 'Paper · pre-recorded video'),
    ('AI4Peace 2026, Roma, sessione “AI and Democratic Institutions”. Presentazione in inglese.', 'AI4Peace 2026, Rome, “AI and Democratic Institutions” session. Presented in English.'),
    ('<span class="label tipo">Relazione</span>', '<span class="label tipo">Talk</span>'),
    ('Incontro nazionale dei direttori degli uffici catechistici diocesani e delle équipe, “Edificati dalla comunità”, Roma. Tavola rotonda con don Andrea Ciucci e Stefano Pasta.',
     'National meeting of Italian diocesan catechetical directors, “Edificati dalla comunità”, Rome. Round table with Fr Andrea Ciucci and Stefano Pasta.'),
    ('Docenza · corso online', 'Teaching · online course'),
    ('Modulo sul giornalismo del MOOC “(Post)Digitale: comunicazione, educazione ed etica”, Cei e Cremit, Università Cattolica.', 'Journalism module of the MOOC “(Post)Digitale: comunicazione, educazione ed etica”, Italian Bishops’ Conference and Cremit, Università Cattolica.'),
    ('<span class="label tipo">Intervento</span>', '<span class="label tipo">Talk</span>'),
    ('<h4>Corso “Evoluzione digitale”</h4>', '<h4>“Evoluzione digitale” course</h4>'),
    ('Fisc, con l’Ufficio nazionale per le comunicazioni sociali e il Servizio per la promozione del sostegno economico alla Chiesa della Cei, Roma.', 'Fisc, the federation of Italian Catholic weeklies, with two national offices of the Italian Bishops’ Conference, Rome.'),
    ('<span class="label tipo">Testimonianza</span>', '<span class="label tipo">Testimony</span>'),
    ('<h4>Giornata internazionale delle persone con disabilità</h4>', '<h4>International Day of Persons with Disabilities</h4>'),
    ('In collegamento con la diocesi di Mileto-Nicotera-Tropea: disabilità, vocazione, comunità e inclusione.', 'Online with the Diocese of Mileto-Nicotera-Tropea: disability, vocation, community and inclusion.'),
    ('<span class="label tipo">Docenza</span>', '<span class="label tipo">Teaching</span>'),
    ('Corso “Trasmettere, gestire, valorizzare”, modulo sulla valorizzazione del patrimonio archivistico. Pontificia Università Gregoriana, Associazione Archivistica Ecclesiastica e Cei.',
     '“Trasmettere, gestire, valorizzare” course, module on promoting archival heritage. Pontifical Gregorian University, Ecclesiastical Archival Association and Italian Bishops’ Conference.'),
    ('Laboratorio di formazione', 'Workshop'),
    ('XII laboratorio per animatori della cultura e della comunicazione “Ascoltate! Per una comunicazione di comunità”, diocesi di Molfetta-Ruvo-Giovinazzo-Terlizzi, Seminario vescovile di Molfetta.',
     'Twelfth workshop for culture and communication leaders, “Ascoltate! Per una comunicazione di comunità”, Diocese of Molfetta-Ruvo-Giovinazzo-Terlizzi, Molfetta.'),
    ('Formazione · online', 'Training · online'),
    ('Percorso “Trova la tua facoltà”, sessione “Talenti, limiti ed esperienze”, Sophia Impresa Sociale.', '“Trova la tua facoltà” programme, “Talents, limits and experiences” session, Sophia Impresa Sociale.'),
    ('Incontro con il Movimento dei Cursillos di Cristianità: disinformazione, big data, comunicazione social e media della Cei.', 'Meeting with the Cursillos in Christianity movement: disinformation, big data, social media and the Italian bishops’ media.'),
    ('<span class="label tipo">Workshop</span>', '<span class="label tipo">Workshop</span>'),
    ('Workshop “La comunicazione” nella giornata inaugurale di “Aperti al MAB”, Cei, Roma.', '“La comunicazione” workshop on the opening day of “Aperti al MAB”, Italian Bishops’ Conference, Rome.'),
    ('<h3 class="label gold sub-h">Interviste</h3>', '<h3 class="label gold sub-h">Interviews</h3>'),
    ('Alcune tra le interviste rilasciate.', 'A selection of interviews given.'),
    ('Intervista a cura di Simone Esposito.', 'Interview by Simone Esposito.'),
    ('Intervista di Benedetta Capelli su “Covid-19: preti in prima linea”.', 'Interview by Benedetta Capelli about “Covid-19: preti in prima linea”.'),
    # ricerca
    ('<h2 class="label">Ricerca</h2>', '<h2 class="label">Research</h2>'),
    ('<p>La tesi di dottorato, discussa nel 2025 all’Università Pontificia Salesiana, analizza l’arrivo dell’intelligenza artificiale nelle redazioni cattoliche italiane attraverso la tetrade di Marshall McLuhan. Il lavoro prosegue con articoli su riviste scientifiche dedicati al discernimento algoritmico e all’autorità giornalistica.</p>',
     '<p>His doctoral thesis, defended in 2025 at the Pontifical Salesian University, examines the arrival of artificial intelligence in Italian Catholic newsrooms through Marshall McLuhan’s tetrad. The work continues in peer-reviewed articles on algorithmic discernment and journalistic authority.</p>'),
    ('<dt class="label">Tesi</dt>', '<dt class="label">Thesis</dt>'),
    ('<dt class="label">Dottorato</dt>\n          <dd>Facoltà di Scienze della comunicazione sociale, Università Pontificia Salesiana, Roma, discussa il 17 dicembre 2025. Relatore prof. Fabio Pasqualetti. <a href="https://sas.unisal.it/?selTipoTesi=%25%25&amp;selCampi1=Autore&amp;txtSearch1=benotti&amp;selCampi2=Autore&amp;txtSearch2=&amp;btnSrch=Cerca&amp;id=archtesi">Archivio tesi UPS</a></dd>',
     '<dt class="label">Doctorate</dt>\n          <dd>Faculty of Social Communication Sciences, Pontifical Salesian University, Rome, defended on 17 December 2025. Supervisor: Prof. Fabio Pasqualetti. <a href="https://sas.unisal.it/?selTipoTesi=%25%25&amp;selCampi1=Autore&amp;txtSearch1=benotti&amp;selCampi2=Autore&amp;txtSearch2=&amp;btnSrch=Cerca&amp;id=archtesi">UPS thesis archive</a></dd>'),
    ('<dt class="label">In sintesi</dt>', '<dt class="label">Abstract</dt>'),
    ('<dd>Una ricerca qualitativa, condotta con interviste semi-strutturate a giornalisti, direttori ed esperti di Avvenire, Tv2000, SIR e Vatican News. La tetrade di McLuhan serve a leggere che cosa l’IA potenzia, rende obsoleto, recupera e rovescia nelle tre fasi del lavoro redazionale: raccolta, produzione e distribuzione delle notizie. Le conclusioni propongono un modello di integrazione che lascia al centro la responsabilità umana e la mediazione come atto di discernimento.</dd>',
     '<dd>A qualitative study based on semi-structured interviews with journalists, editors and experts at Avvenire, Tv2000, SIR and Vatican News. McLuhan’s tetrad is used to read what AI enhances, makes obsolete, retrieves and reverses across the three stages of newsroom work: gathering, producing and distributing the news. The conclusions propose a model of integration that keeps human responsibility, and mediation as an act of discernment, at the centre.</dd>'),
    ('Accettati e in corso di stampa', 'Accepted and in press'),
    ('<p>Accettato, in produzione.</p>', '<p>Accepted, in production.</p>'),
    ('<p>In produzione, n. 3/2026.</p>', '<p>In production, issue 3/2026.</p>'),
    ('<p>Accettato, in attesa di pubblicazione.</p>', '<p>Accepted, awaiting publication.</p>'),
    # contatti
    ('<h2 class="label">Contatti</h2>', '<h2 class="label">Contact</h2>'),
    ('<h3 class="label gold sub-h">Per chi organizza un incontro</h3>', '<h3 class="label gold sub-h">For event organisers</h3>'),
    ('Una biografia breve da usare per presentazioni e locandine, e una fotografia in alta risoluzione.', 'A short biography for introductions and programmes, and a high-resolution photograph.'),
    ('id="bio-breve"><p>Riccardo Benotti è giornalista professionista e caposervizio del SIR – Servizio Informazione Religiosa, l’agenzia della Conferenza episcopale italiana, dove lavora dal 2006. È accreditato presso la Sala Stampa della Santa Sede. Dottore di ricerca in Scienze della comunicazione sociale all’Università Pontificia Salesiana, studia come l’intelligenza artificiale trasforma il giornalismo. Ha pubblicato <i>Covid-19: preti in prima linea</i> (San Paolo, 2021) e <i>Viaggio nella vita religiosa</i> (Libreria Editrice Vaticana, 2016). È membro della Commissione Film Cei.</p>',
     'id="bio-breve"><p>Riccardo Benotti is an Italian journalist and senior editor at SIR – Servizio Informazione Religiosa, the news agency of the Italian Bishops’ Conference, where he has worked since 2006. He is accredited to the Holy See Press Office. He holds a PhD in Social Communication from the Pontifical Salesian University in Rome and studies how artificial intelligence is transforming journalism. His books include <i>Covid-19: preti in prima linea</i> (San Paolo, 2021) and <i>Viaggio nella vita religiosa</i> (Libreria Editrice Vaticana, 2016). He is a member of the Film Commission of the Italian Bishops’ Conference.</p>'),
    ('data-ok="Copiata" data-ko="Copia non riuscita: il testo è selezionato, copialo tu">Copia la biografia</button>', 'data-ok="Copied" data-ko="Copy failed: the text is selected, copy it manually">Copy the biography</button>'),
    ('Scarica la foto (JPG, 1254 × 1254)', 'Download the photo (JPG, 1254 × 1254)'),
]
FOOT = [
    ('<p>Giornalista professionista e autore. Caposervizio del SIR – Servizio Informazione Religiosa. Roma.</p>', '<p>Journalist and author. Senior editor at SIR – Servizio Informazione Religiosa. Rome.</p>'),
    ('<span class="label">Altrove</span>', '<span class="label">Elsewhere</span>'),
    ('<span>Gli articoli firmati</span>', '<span>Signed articles</span>'),
    ('<span>Il filo del giorno e altri post</span>', '<span>The daily column and other posts</span>'),
    ('<span>Archivio di tutte le puntate</span>', '<span>Archive of the daily column (in Italian)</span>'),
    ('<span>Pubblicazioni scientifiche</span>', '<span>Academic publications</span>'),
    ('<span>Profilo accademico</span>', '<span>Academic profile</span>'),
    ('<a href="/crediti/">Crediti delle immagini</a>', '<a href="/crediti/" hreflang="it">Image credits</a>'),
    ('<span>Pagina autore</span>', '<span>Author page</span>'),
    ('Commissione Film Cei</a><span>I membri</span>', 'CEI Film Commission</a><span>Members</span>'),
    ('Ufficio comunicazioni sociali Cei</a><span>La nomina nella Commissione, 2020</span>', 'CEI Office for Social Communications</a><span>Appointment to the Commission, 2020</span>'),
]
bad = []
for o, n in PAIRS:
    if o not in en:
        bad.append(o[:80])
    en = en.replace(o, n)
for o, n in FOOT:
    if o not in foot:
        bad.append(o[:80])
    foot = foot.replace(o, n)
if bad:
    print('Frasi italiane non trovate:\n - ' + '\n - '.join(bad)); sys.exit(1)
(SRC / 'body_en.html').write_text(en)
(SRC / 'footer_en.html').write_text(foot)
print('OK body_en.html')
