# Vertiefung und Generatorenstand

## 1 · Wer vor Schluss durch ist, hört nicht auf

`generator/vertiefung.py` plus drei Routen. Reihenfolge ist nicht willkürlich:
**zuerst messen, dann gezielt üben, erst zuletzt breit wiederholen.**

### Probe-Erhebung  `/probe`

Ein vollständiger Durchgang in Prüfungsform: eine Aufgabe pro Teilaufgabe der
Erhebung, Level C, **keine Tipps und keine zweite Chance**. Danach der Bericht:

> **2 von 2** richtig (100 %) — Fehlerfrei, genau das ist das Ziel.

Teilaufgaben ohne Generator werden übersprungen und im Bericht als **nicht
geprüft** ausgewiesen. Sie zählen nicht als bestanden — sonst würde die Probe
Fehlerfreiheit melden, wo nur nichts gefragt wurde.

### Wackelkandidaten  `/wiederholen/schwach`

Die Bauformen mit den meisten Fehlversuchen, aus den echten Zahlen in
`BauformStand` — nicht aus einer Annahme darüber, was schwer sein könnte. Das
Häkchen wird entfernt, die Bauform kommt wieder.

### Alles auf Level C  `/wiederholen/level_c`

Setzt jedes Kapitel auf C zurück, **auch die, bei denen der Schüler über den
Levelsprung eingestiegen ist und C nie gesehen hat.**

---

## 2 · Die Theorie beim Einstieg

Teil 6 der Schablone erscheint einmal pro Lektion, oberhalb der ersten Aufgabe —
unabhängig davon, ob der Schüler Level A überspringt:

> **Darum geht es**
> Klammer vor Punkt vor Strich. Ein Minus vor der Klammer dreht jedes
> Vorzeichen darin um — auch das zweite und dritte.

---

## 3 · Ein Generator dazu: die Klammern

`s10_klammern.py`, acht Bauformen, 880 Aufgaben im Test, keine Beanstandungen.

Ich habe diese Schablone vor allen anderen gebaut, weil **10.6 «Minus vor der
Klammer» das häufigste Rücksprungziel im ganzen Netz ist**: sechs Fehler aus
zwei Schablonen zeigen dorthin. Ohne sie lief die Lückensuche ins Leere — die
App hätte gesagt «schau dir das an» und hätte nichts zu zeigen gehabt.

Sie deckt 10.1 bis 10.11 ab, also elf Lektionen auf einmal.

**Stand: 18 von 170 Lektionen haben einen Generator** (vorher 7).

Ein simulierter Schüler ohne Vorwissen läuft jetzt **134 Aufgaben** durch alle
drei Schablonen, bevor er in die Vertiefung kommt.

---

## 4 · Was noch fehlt — ungeschönt

152 Lektionen ohne Generator. Nach Kapiteln, mit dem Aufwand pro Schablone
(je acht bis zwölf Bauformen, ein bis zwei Stunden Bauzeit plus Testlauf):

| Kapitel | Lektionen | Schablonen | wofür |
|---|---:|---:|---|
| K1 Zahlen und Vorzeichen | 20 | 5 | Fundament, Rücksprungziel 1.9 und 1.19 |
| K2 Brüche | 13 | 6 | Rücksprungziel für K14 und K15 |
| K3 Variablen | 12 | 3 | |
| K4 gleichartige Terme | 10 | 2 | Rücksprungziel 4.8 |
| K5 Multiplikation | 9 | 2 | |
| K6 gemischt | 8 | — | vorhanden |
| K7 Potenzen | 11 | 4 | Rücksprungziel 7.10 |
| K8 Wurzeln | 10 | 4 | Erhebung 3a, 3b, 3e |
| K9 Division | 7 | 3 | Erhebung 2c |
| K10 Klammern | 17 | 1 | 10.12–10.16 fehlen noch |
| K11 Distributivgesetz | 10 | 4 | Erhebung 2b |
| K12 Faktorisieren | 9 | 2 | 12.5–12.9 fehlen |
| K13 Gleichungen | 10 | 3 | Erhebung 1a |
| K14 Bruchterme | 12 | 5 | Erhebung 5a, 5b, 5c |
| K15 Bruchgleichungen | 9 | 5 | Erhebung 1b, 6a, 6b |
| K16 Vermischtes | 3 | 1 | |

**Rund 45 Schablonen.** Bei zwei bis drei pro Runde sind das etwa 18 Runden.

### Reihenfolge, die ich vorschlagen würde

Nicht nach Kapitelnummer, sondern nach Wirkung:

1. **K4 und K7** — die beiden übrigen häufigen Rücksprungziele (4.8, 7.10).
   Danach hat jede Lückensuche ein Ziel, das auch existiert.
2. **K1 und K2** — das Fundament. Ohne sie kann niemand ganz unten einsteigen,
   und genau dort landen die schwachen Schüler.
3. **K11, K13** — Erhebung 2b und 1a.
4. **K8, K9, K12** — Erhebung 3, 2c, 4 vollständig.
5. **K14, K15** — Erhebung 5 und 6, die schwersten.
6. **K3, K5, K16** — Rest.

Nach Schritt 2 wären rund 70 Lektionen übbar und der Einstufungstest würde für
schwache Schüler funktionieren. Nach Schritt 4 wären fünf der sechs
Erhebungsaufgaben abgedeckt.

---

## Testen

```powershell
cd tests
python test_alle.py       # 2680 Aufgaben über drei Schablonen
cd ..
python app.py
```
