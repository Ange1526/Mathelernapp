# Maturaarbeit · Adaptive Algebra-Lernplattform

Diese Datei ist das Gedächtnis des Projekts. Lies sie zu Beginn jeder Sitzung.

## Worum es geht

Donatella schreibt ihre Maturaarbeit über eine adaptive Lernplattform für
Algebra. Ziel: Erstklässler des Gymnasiums sollen die Erhebung
«Vorkenntnisse Algebra 1m» der Kantonsschule Frauenfeld fehlerfrei lösen —
und zwar unabhängig davon, wo sie starten.

**Studiendesign:** quasi-experimentell, zwei Klassen. Eine übt mit der App,
die andere mit einem Matheplan aus dem Lehrmittel. Beide Gruppen bekommen
**ausschliesslich Rechenaufgaben** («rechne aus»). Das ist eine feste
Vorgabe: die Studie soll Adaptivität messen, nicht Aufgabenvielfalt.

Donatella hat wenig Programmiererfahrung. Erkläre in kleinen, konkreten
Schritten ohne Fachjargon, wenn ein Begriff neu ist. Sie kommuniziert kurz
und direkt und schickt oft nur eine Fehlermeldung.

## Technik

Flask · SQLAlchemy · SymPy · Python · Windows mit PowerShell.

```
app.py                  Flask-App, alle Routen und Modelle
migration_streak.py     Beispiel für eine Schema-Änderung
generator/
  schablone.py          Bauform, Schablone, erzeugen()
  ziehung.py            Round-Robin-Ziehung
  qualitaet.py          Filter (kopfrechenbar, fehler_eindeutig, ...)
  anzeige.py            zeige(), zeige_summe(), als_eingabe(), HOCH, MINUS
  netz_daten.py         alle 170 Lektionen mit Voraussetzungen
  netz.py               Netz, SCHABLONE_FUER, ZIEL, RUECKSPRUNG
  anbindung.py          KAPITEL: Kapitelnummer -> Schablone
  lernstand.py          Level, Mastery, Ziehung je Bauform
  einstufung.py         Adaptiver Einstufungstest, drei Phasen (Stand 08/26)
  vertiefung.py         Probe-Erhebung, Schwachstellen, Level C
  theorie.py            Theorie-Animationen
  s60_mischen.py        Mischaufgaben, Kapitel 16.1 (kombiniert Schablonen)
  s*.py                 die Generatoren
korrektur/
  eingabe_parser.py     SymPy-Parser mit Sicherheitsprüfung
  pruefung.py           Fünf-Status-Prüfung, Fehlerkataloge
tests/
  test_alle.py          Testlauf über alle Schablonen (dauert ~8 Minuten)
  test_einstufung.py    12 künstliche Schüler durch den Einstufungstest
  test_s60.py           1440 Mischaufgaben durch Parser und SymPy
Schablonen/             die 43 Schablonen als .docx
```

## Wie eine Schablone gebaut wird

Jede der 43 Schablonen liegt als `.docx` im Ordner `Schablonen/`. Aufbau:

1. **Teil 1 · Matrix** — 11 oder 12 Bauformen mal Level A, B, C, mit einem
   Beispiel je Zelle
2. **Teil 2 · Regler** — welche Stellschraube das Level trägt, und welche
   gesperrt ist
3. **Teil 3 · Lösungsweg** — die Schritte, die in `schritte` gehören
4. **Teil 4 · Tipps** — drei Stufen, von allgemein bis konkret
5. **Teil 5 · Fehlerkatalog** — fünf typische Fehler mit Ergebnis und
   Rückmeldung
6. **Teil 6 · Theorie-Kernidee** — ein bis zwei Sätze

Lies alle sechs Teile, bevor du Code schreibst.

### Die Levelachse ist strukturell, nicht numerisch

**Das ist die wichtigste Regel des Projekts.** A, B und C unterscheiden sich
im AUFBAU der Aufgabe — Anzahl Glieder, Anzahl Vorzeichen, Anzahl Variablen,
Anzahl Faktoren. Sie unterscheiden sich NICHT in der Grösse der Zahlen.

Fünf frühe Generatoren verletzten das: `s2_grundoperationen.py`,
`s4_faktorisieren.py`, `s7_potenzen.py`, `s10_klammern.py` und das
inzwischen ersetzte `s4k_gleichartig.py` hatten auf allen drei Level
denselben Aufbau und nur andere Zahlen. Donatella hat das beim Üben gemerkt.
S2, S4, S7 und S10 sind noch nicht ersetzt.

Massgebend ist immer **Teil 2 der Schablone**, nicht das, was plausibel
wirkt. Einzige Ausnahme: wo Teil 2 ausdrücklich sagt, dass die Zahlengrösse
der einzige verfügbare Regler ist — etwa bei S26.

So prüfst du es:

```python
import re, random
def muster(t):
    t = re.sub(r'\d+', '#', t); t = re.sub(r'[a-z]', '~', t)
    return re.sub(r'\s+', '', t)
# Für jede Bauform: erzeuge je Level 12 Aufgaben, vergleiche die Mustermengen.
# Sind sie gleich, trägt das Level nur Zahlen. Das ist ein Fehler.
```

### Aufbau eines Generators

Vorbild: `generator/s8_wurzeln.py` und `generator/s16_gleichartig.py`.

```python
BF1 = Bauform("BF1", "Kurzer Titel",
    bereiche={lv: {...} for lv in ("A", "B", "C")},
    bauen=bf1, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])

S99 = Schablone(nr="S99", titel="...", lektionen="9.1 – 9.4",
                erhebung="2c", anleitung="Rechne aus.",
                levelachse="Gliederzahl und Vorzeichen",
                bauformen=[BF1, ...], kernidee="...")
```

`bauen` bekommt die gezogenen Parameter und gibt ein dict zurück mit
`frage`, `loesung_text`, `aufgabe` (ein `korrektur.Aufgabe`), `schritte`
und `tipps`.

### Fehlerkataloge aus der Aufgabe berechnen

Schreib die fünf Fehler aus Teil 5 nicht einzeln pro Bauform hin, sondern
berechne sie aus der Aufgabe. Dann tragen sie überall. Vorbild:
`kandidaten13`, `kandidaten14` und `kandidaten17`.

Danach immer sieben: Einträge, die gleich der Lösung sind, und Doppelte
müssen weg. Sonst wird eine richtige Antwort als Fehler gemeldet, oder die
Diagnose ist mehrdeutig und `fehler_eindeutig` verwirft jede Aufgabe.

Richtwert: **mindestens 1,6 Einträge je Aufgabe**, keine Aufgabe ohne
Eintrag. Prüfen:

```python
sum(len(e.aufgabe.fehlerkatalog) for e in aufgaben) / len(aufgaben)
```

## Fallen, die schon einmal Zeit gekostet haben

**SymPy**

- `Symbol('a')` und `Symbol('a', positive=True)` sind verschiedene Objekte —
  Referenzlösung und geparste Antwort müssen dasselbe benutzen
- `solve()` liefert bei `positive=True` keine negativen Lösungen
- Formprüfung braucht `.form` (unausgewertet), nicht `.expr`
- `together()` kürzt vor der Prüfung — untauglich für Kürzungsprüfungen
- `factor(b) == b` ist auf unausgewerteten Ausdrücken unzuverlässig
- SymPy sortiert Summen und Produkte alphabetisch um. Wo die Reihenfolge
  zählt, `zeige_summe()` benutzen oder `loesung_text` von Hand setzen
- `Rational(48, 75)` kürzt beim Erzeugen zu `16/25`. Brüche, die sich erst
  kürzen lassen sollen, als Text bauen
- `√25` wertet sofort zu `5` aus — «Wurzel stehen gelassen» lässt sich
  darum nicht in den Fehlerkatalog aufnehmen
- SIGALRM-Timeouts feuern im Flask-Entwicklungsserver nicht

**Zahlen ziehen**

Die Schrittweite beim Durchlaufen eines Zahlenvorrats muss zu jeder
Vorratsgrösse teilerfremd sein. Bei Schrittweite 3 und sechs Zahlen
wiederholt sich jede Zahl; bei 5 und fünf Zahlen werden alle gleich.
**7 benutzen** — die Vorräte haben vier, fünf oder sechs Einträge.

**Datenbank**

`db.create_all()` legt nur fehlende TABELLEN an, keine neuen SPALTEN. Für
Schemaänderungen ein Migrationsskript mit `ALTER TABLE` schreiben, nach dem
Vorbild von `migration_streak.py`.

**Bekannter Fehler, nicht angerührt:** `_irreduzibel` in `pruefung.py`
verwirft `−v²` als Faktor. Dadurch gelten gültige Faktorisierungen als
unvollständig.

## Arbeitsweise

Eine Runde ist ein Kapitel. Ablauf:

1. Die `.docx` der Schablonen lesen, alle sechs Teile
2. Generator schreiben, Vorbild `s8_wurzeln.py`
3. Sichtprüfung: je Bauform und Level eine Aufgabe ausgeben und ansehen
4. Levelachse messen (siehe oben) — A, B, C müssen sich im Aufbau
   unterscheiden
5. Fehlerdichte messen — mindestens 1,6
6. Testdatei schreiben, Vorbild `tests/test_s8.py`
7. In `anbindung.py` (KAPITEL) und `netz.py` (SCHABLONE_FUER) eintragen.
   **Nur die Lektionen eintragen, die die Schablone wirklich abdeckt.**
   Frühere Einträge behaupteten mehr, als die Generatoren konnten
8. Eine Theorie-Animation in `theorie.py` ergänzen
9. Die neue Schablone in `LAEUFE` in `tests/test_alle.py` eintragen.
   **Ohne diesen Eintrag wird sie nie geprüft**, und der Testlauf meldet
   trotzdem ALLES BESTANDEN
10. Beim Bauen `python test_alle.py K6 --wenig` — rund zehn Sekunden.
    Erst wenn das sauber ist, `python test_alle.py` ohne Schalter
11. App starten und die neuen Lektionen im Browser ansehen

### Der Testlauf

```
python test_alle.py --liste        zeigt alle Schablonen
python test_alle.py K6 --wenig     ein Kapitel, kleine Stichprobe, ~10 s
python test_alle.py --geaendert    nur was sich seit dem letzten Lauf änderte
python test_alle.py                voller Lauf, alle Stichproben
python test_alle.py --einzeln      ohne Parallelbetrieb, für die Fehlersuche
```

`--wenig` nimmt zehn statt vierzig Aufgaben je Bauform und Level. Danach
wird der Stand bewusst NICHT gemerkt — eine Stichprobe von zehn ist keine
Freigabe. Vor dem Abschluss einer Runde immer den vollen Lauf.

Änderungen minimal und chirurgisch halten. Bestehende Bauteile nicht
umbauen, wenn nur eine Ergänzung verlangt ist.

## Stand

Fertig: 46 Schablonen. 134 der 170 Lektionen haben Aufgaben.
**Alle 19 Erhebungsteilaufgaben sind übbar.**
Vollständige Kapitel: 3 bis 15 — jede Lektion hat Aufgaben.
Offen sind nur noch Kapitel 1 und 2 (33 Lektionen) und Kapitel 16.

Kein Generator hat mehr eine numerische Levelachse. `s2_grundoperationen.py`,
`s7_potenzen.py`, `s10_klammern.py` und `s4_faktorisieren.py` hängen an keiner
Lektion mehr; sie stehen im Testlauf unter «abgeloest» und können weg, sobald
niemand sie mehr vermisst.

| Kapitel | Schablonen | Datei |
|---|---|---|
| 3 | S12, S13, S14 | `s3_terme.py` |
| 4 | S15, S16, S17 | `s15_s17_sorten.py`, `s16_gleichartig.py` |
| 5 | S18, S19 | `s5_produkte.py` |
| 6 | S20, S21 | `s6_punktrechnung.py` |
| 7 | S22–S25 | `s22_s23_potenzen.py`, `s24_s25_potenzgesetze.py` |
| 8 | S26–S29 | `s8_wurzeln.py` |
| 9 | S30, S31, S32 | `s9_division.py` |
| 10 | S33–S37 | `s10_klammern_neu.py`, `s34_s35_klammern.py`, `s36_klammern_variablen.py`, `s37_klammer_potenz.py` |
| 11 | S38–S41 | `s11_ausmultiplizieren.py`, `s39_s40_ausmultiplizieren.py`, `s41_bruch_klammer.py` |
| 12 | S42, S43, S44 | `s42_s44_faktorisieren.py` |
| 13 | S45, S46, S47 | `s45_gleichungen.py`, `s46_s47_klammern.py`, `s47_brueche.py` |
| 14 | S48–S51, S49B | `s48_erweitern.py`, `s14_bruchterme.py`, `s49b_ausklammern_kuerzen.py`, `s50_s51_bruchterme.py` |
| 15 | S52–S56 | `s15_bruchgleichungen.py`, `s53_s54_bruchgleichungen.py`, `s55_s57_bruchgleichungen.py`, `s56_x_im_nenner.py` |
| 16 | S60, M16 | `s60_mischen.py`, `mischung.py` |

### Die Gemischt-Lektionen (`generator/mischung.py`)

Die letzte Lektion jedes Kapitels heisst «Gemischt: alles aus Kapitel N
kombiniert». Sie erfindet keinen neuen Stoff: `mischung()` nimmt die
Bauformen der Kapitelschablonen im Round Robin, nummeriert sie neu durch und
setzt sie in eine eigene Schablone M3 … M16. Es sind DIESELBEN Objekte —
ein Fehler kann sich dort nicht anders verhalten als in der Quelle.

Zwei Dinge sind daran wichtig:

- Die **Anleitung** steht an der Schablone, nicht an der Bauform. Es kommen
  darum nur die Quellen mit der HÄUFIGSTEN Anleitung des Kapitels hinein —
  lieber eine Bauform weniger als eine falsch angeschriebene Aufgabe.
- Die **Mastery** hängt an (Schablone, Bauform). Eine Gemischt-Lektion hat
  eigene Häkchen, und das ist gewollt: eine Aufgabe zu können, wenn sie
  angekündigt ist, ist nicht dasselbe, wie sie zwischen zwölf anderen Formen
  zu erkennen.

### Was bewusst fehlt

- **S56/BF6** — «jede Zahl ausser 2 und −2». Definitionsbereiche sind
  ausserhalb des Umfangs, und die App kennt nur eine Zahl, «keine Lösung»
  und «jede Zahl». Der Fall «keine Lösung» IST gebaut (S56/BF4); er braucht
  keine Mengenschreibweise. Wer BF6 will, muss zuerst entscheiden, wie eine
  Antwort mit Ausnahmen aussieht — das ist eine Entscheidung über die
  Eingabe, nicht über den Generator.
- **Kapitel 1 und 2** — S1 bis S11, im alten Format, mit Lift-Animation.
- **Lektion 12.9, 16.1, 16.2, 16.3** stehen nicht in `SCHABLONE_FUER`:
  Kapitel 16 ist die Stufe ÜBER dem Weg, nicht auf ihm.

## Reihenfolge der nächsten Runden

1. **Datenexport als CSV** für die Auswertung der Maturaarbeit — fehlt ganz
2. **Gruppenfeld** am Konto: App-Gruppe gegen Matheplan-Gruppe
3. **Ansicht für die Lehrperson** mit den markierten Fragen aller Schülerinnen
4. K1 und K2 — S1 bis S11, im alten Format, mit Lift-Animation

Die drei ersten Punkte brauchen `app.py`. Solange daran parallel gearbeitet
wird, ist das der Grund, warum sie liegen bleiben — nicht der Aufwand.

Theorie-Animationen gibt es für jedes Kapitel von 3 bis 15, auch für die
Gemischt-Lektionen. `RUECKSPRUNG` in `netz.py` kennt jetzt Sternschlüssel:
`"S42/*/eins_vergessen"` gilt für alle zwölf Bauformen — nötig, seit die
Fehlerkataloge aus der Aufgabe gerechnet werden statt je Bauform von Hand.

## Entscheidungen, die feststehen

- Mastery je Bauform, nicht je Lektion
- Round-Robin-Ziehung, nicht zufällig
- `MASTERY_SERIE = 2`, `HAEKCHEN_VERFAELLT = False`
- Ein Level ist erst fertig, wenn ALLE Bauformen ein Häkchen haben — keine
  80-Prozent-Schwelle
- Aufgaben werden erzeugt, nicht gespeichert
- Gerundete Dezimalzahlen mit zwei Stellen werden akzeptiert
- Definitionsbereiche sind ausserhalb des Umfangs
- Der Knopf «Ich verstehe die Aufgabe nicht» speichert den Wortlaut für die
  Lehrperson
- Lektionen ohne Generator zählen NICHT als sicher, sondern als übersprungen


## Einstufungstest (neu geschrieben, August 2026)

Der alte Test stellte 12 feste Leitaufgaben, ALLE auf Level B. Drei Fehler:
er passte die Schwierigkeit nie an, eine richtige Antwort schrieb über
`rueckwaerts_gutschreiben` bis zu 34 Lektionen gut, und ein Fehlschlag
führte zu keiner gezielten Rückfrage. Ersetzt durch drei Phasen:

1. **Anker** — 3 Sonden, binäre Suche über die Themenstränge, Level B.
2. **Strangdurchgang** — je Strang eine Sonde. Das Level hängt am laufenden
   Niveau 0–3: `{3:"C", 2:"B", 1:"A", 0:"A"}`. Bei Fehlschlag zuerst eine
   Stufe tiefer im SELBEN Strang (C→B→A), erst danach über `vorstrang()`
   eine Ebene tiefer. **Nach unten spezifischer, nach oben schwerer.**
3. **Feinschliff** — erst ab 70 % übbarer Lektionen; prüft bis zu 8 nie
   selbst gelöste, aber gutgeschriebene Stellen auf Level C.

**Kontrollrunde** (`bericht["kontrolle"]`): Ein Test mit 30 Aufgaben kann
eine einzelne Lücke unter 80 Lektionen nicht sicher orten — das ist
Rechnerei, keine Bauschwäche. Darum verschwindet mittelbar Gutgeschriebenes
nicht aus dem Weg, sondern kommt als kurze Runde auf Level C wieder. Das
ist die eigentliche Lösung gegen den Deckeneffekt bei Gymnasiasten.

Weitere feste Punkte:
- `Strang` entsteht automatisch aus `SCHABLONE_FUER`. Neue Generatoren
  werden ohne Pflegeaufwand mitgeprüft.
- Level-A-Antworten schreiben NUR strangintern gut, nicht netzweit.
- `_prozent_uebbar()` rechnet gegen die ~80 übbaren Lektionen, nicht gegen
  170. Ohne das feuert die Feinschliffphase nie.
- Budget `GRENZE = {0:16, 1:22, 2:30, 3:30}`, Frühabbruch nach 3 Fehlschlägen
  auf Niveau 0, davor 5 Streusonden gegen «Inselbegabung übersehen».
- `startpunkt()` liefert den ersten Eintrag des Plans, NICHT die kleinste
  offene Nummer im Netz — sonst liest ein Gymnasiast auf der Ergebnisseite
  «du beginnst bei 1.1» und misstraut der Einstufung zu Recht.
- Berichtsfelder: `plan`, `plan_kapitel`, `kontrolle`, `luecken`, `profil`,
  `prozent_uebbar`, `richtig`, `protokoll`, `geschaetzt_gesamt()`,
  `naechstes_level()`.

Gemessen mit `tests/test_einstufung.py` (12 künstliche Schüler):
24,2 Aufgaben im Schnitt, 0,2 Lektionen zu hoch, 0,4 zu tief, alle
eingebauten Lücken abgedeckt. Vorher: bis zu 11 Lektionen zu hoch.

## Mischaufgaben S60 (neu, August 2026)

`generator/s60_mischen.py`, Kapitel **16.1**, 12 Bauformen. Kombiniert
zwei bis drei Kapitel je Aufgabe (K8·K5·K4, K7·K4, K9·K8·K4 …). Kein neuer
Stoff — nur Kombination. Vier Sonderfall-Bauformen: Ergebnis null (BF9),
Koeffizient eins (BF10), nichts lässt sich zusammenfassen (BF11).

Levelachse strukturell: A = zwei Teilschritte, eine Variable, zwei Glieder ·
B = Vorzeichenwechsel, drei Glieder oder höhere Potenzstufe · C = drei
Teilschritte, ZWEI Variablen, drei Glieder gemischt. Zahlenvorräte auf
allen drei Level identisch.

**Bewusst NICHT in `netz.SCHABLONE_FUER` eingetragen.** Mischaufgaben sind
keine Lektion auf dem Weg, sondern die Stufe darüber. Stattdessen in
`anbindung.py`: `MISCHEN = "16.1"`, `MISCH_VORAUSSETZUNG`,
`mischen_moeglich()` (vier von sechs Grundlagen genügen, damit es innerhalb
der Studienzeit erreichbar bleibt).

`Probelauf.neu()` hängt drei Mischaufgaben (M1–M3) an die 19
Erhebungsteilaufgaben — die Probe ist damit etwas schwerer als das Original.

**Die Probe-Erhebung hat jetzt Folgen.** Vorher meldete sie nur eine Quote.
Jetzt streicht sie falsch gelöste Teilaufgaben aus `sicher`, setzt das
Kapitel auf Level C zurück und `durchgelaufen = False`.

Neuer Filter `kein_null_glied`: verwirft Ergebnisse mit Koeffizient 0 vor
einer Variablen («0x − 20»), die der Parser als Eingabefehler zurückweist.
Der echte Nullfall bleibt BF9 vorbehalten, dort steht sauber «0».


## Tempo der Testlaeufe (August 2026)

Der Testlauf hing nicht am Erzeugen der Aufgaben (1,4 ms je Aufgabe),
sondern an `simplify`. Gemessen: 7 ms je Aufruf, und aufgerufen wird es vor
allem beim **Fehlerkatalog** — jeder Eintrag wird gegen die Loesung geprueft,
im Schnitt 4,7 Eintraege je Aufgabe.

Geaendert an zwei Stellen, beide mit derselben Idee:

- `korrektur/pruefung.py`, `_ist_null()`: vor der letzten Stufe wird eine
  Bruchzahl fuer die Variablen eingesetzt. Kommt ein Wert **deutlich**
  ungleich null heraus (Schwelle 1e-9), sind die Ausdruecke sicher
  verschieden — bewiesen, nicht geschaetzt. Nur der Rest geht an `simplify`.
- `tests/schnellpruefung.py`, `gleich()`: dasselbe fuer die Testlaeufe.

**Die Schwelle 1e-9 ist wichtig.** Ohne sie liefert `evalf()` bei Wurzeln
statt null manchmal 1e-17, und eine RICHTIGE Schuelerantwort wuerde als
falsch abgestempelt. Alles unterhalb der Schwelle muss weiter an `simplify`.

Gemessen, jeweils mit identischem Ergebnis:
- 1640 echte Paare: alt 11,4 s → neu 2,5 s, **0 Abweichungen**
- `test_alle.py K16 --wenig`: 52 s → 14 s
- `test_s60.py` (1440 Aufgaben): 49 s → 7 s
- `test_alle.py --wenig` (8200 Aufgaben, EIN Kern): 118 s

`test_alle.py` verteilt ueber `ProcessPoolExecutor` bereits auf alle Kerne.
Auf einem Rechner mit vier bis acht Kernen liegt der volle Lauf damit unter
zwei Minuten.

Nebenwirkung, erwuenscht: auch die App selbst antwortet schneller, denn
`_ist_null` laeuft bei JEDER falschen Schuelerantwort.
