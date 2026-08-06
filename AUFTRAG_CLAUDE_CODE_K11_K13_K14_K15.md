# Auftrag für Claude Code — Generatoren für K11, K13, K14, K15

## Warum diese vier Kapitel zuerst

Von den 19 Teilaufgaben der Erhebung «Vorkenntnisse Algebra 1m» haben
**acht noch keinen Generator**. Alle acht liegen in genau diesen vier
Kapiteln:

| Teilaufgabe | Ziel-Lektion | Kapitel |
|---|---|---|
| 1a | 13.9  | K13 |
| 1b | 15.6  | K15 |
| 2b | 11.8  | K11 |
| 5a | 14.8  | K14 |
| 5b | 14.4  | K14 |
| 5c | 14.11 | K14 |
| 6a | 15.5  | K15 |
| 6b | 15.3  | K15 |

Solange die fehlen, kann ein Schüler die Erhebung in der App nicht
vollständig üben — und genau das ist das Ziel der Maturaarbeit. Alles
andere (K1, K2) ist wichtig, aber nicht auf dem kritischen Pfad.

**Die Schablonen sind schon geschrieben.** Sie liegen als .docx im Ordner
`Schablonen/` (S45–S57, siehe `Runde13`, `Runde15`, `Runde16`, `Runde17`,
`Schablonen_S45-S47`, `Schablonen_S48-S51`, `Schablonen_S52-S56`). Es fehlt
nur die Umsetzung in Python. Lies die Schablone, bevor du eine Zeile Code
schreibst — die Bauformen, die Levelachse und der Fehlerkatalog stehen
dort bereits fest und dürfen nicht neu erfunden werden.

## Reihenfolge und Portionsgrösse

**Wichtig: arbeite in Portionen von drei Bauformen, nicht in ganzen
Kapiteln.** Donatella kann nicht vierzig Minuten am Stück warten. Eine
Portion dauert etwa fünf Minuten, und danach ist der Stand jedes Mal
lauffähig und geprüft. Halte an, melde dich, warte auf «weiter».

Vier Portionen ergeben eine fertige Schablone:

| Portion | Inhalt |
|---|---|
| 1 | Gerüst der Datei + BF1, BF2, BF3 + Eintrag in `anbindung.py`, `netz.py`, `LAEUFE` |
| 2 | BF4, BF5, BF6 |
| 3 | BF7, BF8, BF9 |
| 4 | BF10, BF11, BF12 — davon mindestens zwei Sonderfälle |

Nach JEDER Portion:

```
python tests/test_alle.py K13 --wenig
```

Das dauert wenige Sekunden. Läuft es nicht durch, repariere es SOFORT in
derselben Portion — ein Fehler, der drei Portionen mitwandert, kostet mehr
Zeit als er gespart hat. Läuft es durch, melde in zwei Sätzen: welche
Bauformen jetzt stehen, und was in der nächsten Portion drankommt.

Fang niemals eine neue Portion an, ohne dass die vorige grün ist.

Reihenfolge der Kapitel:

1. **K13** (10 Lektionen, 13.1–13.10) — Erhebung 1a
2. **K14** (12 Lektionen, 14.1–14.12) — Erhebung 5a, 5b, 5c
3. **K15** (9 Lektionen, 15.1–15.9) — Erhebung 1b, 6a, 6b
4. **K11** (10 Lektionen, 11.1–11.10) — Erhebung 2b

## Was du NICHT tun sollst, um Zeit zu sparen

Die Portionen sind kleiner, der Inhalt bleibt gleich. Nicht gekürzt werden
darf:

- die fünf Einträge im Fehlerkatalog je Bauform
- die Sonderfall-Bauformen
- die strukturelle Levelachse
- der Testlauf nach jeder Portion

Wenn eine Portion zu lang wird, mach sie kleiner — zwei Bauformen statt
drei. Nicht dünner.

## Die Vorlage

`generator/s60_mischen.py` ist der jüngste und sauberste Generator. Bau
die neuen genauso auf. Verbindlich sind:

- **Zwölf Bauformen** je Schablone, darunter mindestens **zwei
  Sonderfälle** (Ergebnis null, Koeffizient eins, nichts lässt sich
  zusammenfassen, kein gemeinsamer Faktor — je nach Thema).
- **Fünf Einträge im Fehlerkatalog** je Bauform. Nicht drei, nicht vier.
- **Strukturelle Levelachse.** A, B und C dürfen sich NICHT nur in der
  Grösse der Zahlen unterscheiden, sondern im Aufbau: Anzahl Glieder,
  Anzahl Teilschritte, Anzahl Variablen, Vorzeichenwechsel. Der Testlauf
  prüft das und beanstandet eine reine Zahlenachse.
- **Anzeigetexte aus den Gliedern selbst bauen** (`T()`, `reihe()`,
  `zeige_summe()`), NIE über `str()` eines SymPy-Ausdrucks. SymPy sortiert
  Summen alphabetisch um, und dann zeigt die App eine andere Aufgabe an,
  als sie gerechnet hat. Genau dieser Fehler war schon einmal da und hat
  100 % einer Bauform unbrauchbar gemacht.

## Was nach dem Bauen zu tun ist

1. Eintrag in `generator/anbindung.py` → `KAPITEL` für jede Lektion des
   Kapitels.
2. Eintrag in `generator/netz.py` → `SCHABLONE_FUER`.
3. Eintrag in `tests/test_alle.py` → `LAEUFE`, zum Beispiel
   `Lauf("K13", "generator.s45_...", "S45")`. **Ohne diesen Eintrag wird
   der Generator nie geprüft, und der Lauf meldet trotzdem ALLES
   BESTANDEN.**
4. Testen:
   ```
   python tests/test_alle.py K13 --wenig
   ```
   Das dauert jetzt wenige Sekunden. Erst wenn das durchläuft, das
   Kapitel als fertig melden.

## Fallen, die schon einmal Zeit gekostet haben

- `Symbol('a')` und `Symbol('a', positive=True)` sind verschiedene Objekte.
  Musterlösung und geparste Antwort müssen dieselbe Annahme benutzen.
- `solve()` liefert bei `positive=True` keine negativen Lösungen.
- Formprüfung braucht `.form`, nicht `.expr`.
- `factor(b) == b` ist bei unausgewerteten Ausdrücken unzuverlässig.
- `Bauform.erzeugen` würfelt bis zu 300-mal. Zu enge Filter führen zu
  `RuntimeError` statt zu einer Aufgabe.
- **Kein `simplify` in Schleifen.** Es kostet 7 ms pro Aufruf. Benutze
  `tests/schnellpruefung.gleich()` beziehungsweise `_ist_null` aus
  `korrektur/pruefung.py` — beide sieben vorher numerisch aus und sind
  fünfmal schneller bei identischem Ergebnis.

## Nicht anfassen

`app.py`, `generator/einstufung.py`, `generator/vertiefung.py`,
`korrektur/pruefung.py`, `static/style.css` und die Templates. Daran wird
parallel gearbeitet. Wenn eine Änderung dort nötig scheint, melden statt
ändern.
