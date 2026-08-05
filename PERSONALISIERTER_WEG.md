# Der personalisierte Weg

**Der Schüler wählt kein Kapitel mehr.** Er macht einmal den Einstufungstest,
und ab dann sagt die App bei jedem Öffnen: das hier ist jetzt dran. Vorwärts,
wenn eine Lektion sitzt. Rückwärts zu genau der Voraussetzung, auf die ein
Fehler deutet. Ziel ist immer dasselbe: die Erhebungsprüfung fehlerfrei.

Neue Dateien: `generator/netz.py`, `generator/einstufung.py`,
`templates/einstufung.html`, `einstufung_fertig.html`, `ziel_erreicht.html`.

---

## Das Ziel steht jetzt im Code

`netz.py` enthält die 19 Teilaufgaben und die Lektion, die jede prüft:

```python
ZIEL = {"1a": "13.9", "2a": "6.7", "3e": "8.9", "4d": "12.8", "6a": "15.5", ...}
```

Daraus rechnet die App die **Zielmenge**: die 19 geprüften Lektionen plus alles,
was sie voraussetzen. Ergebnis: **41 Lektionen**. Wer die beherrscht, löst den
Test fehlerfrei — das ist die Messlatte, und sie ist jetzt eine Zahl.

Der vollständige Weg für jemanden ohne Vorwissen:

```
1.9 → 1.19 → 2.2 → 2.5 → 2.6 → 2.9 → 3.11 → 4.8 → 4.9 → 5.7 → 6.4 → 6.7 →
7.4 → 7.8 → 7.10 → 8.2 → 8.8 → 8.9 → 9.3 → 9.6 → 10.6 → 10.16 → 11.4 →
11.6 → 11.8 → 11.9 → 12.4 → 12.6 → 12.8 → 13.4 → 13.6 → 13.9 → 14.2 →
14.4 → 14.6 → 14.8 → 14.11 → 15.2 → 15.3 → 15.5 → 15.6
```

Wer schon etwas kann, startet weiter hinten — und lässt weg, was er nicht
braucht.

---

## Der Rücksprung geht dorthin, wo der Fehler herkommt

Das war deine Vorgabe, und sie ist der Kern. Bei einer Bruchgleichung kann
derselbe falsche Wert drei Ursachen haben. Der Fehlerkatalog weiss, welche es
war; `RUECKSPRUNG` sagt, wohin sie zeigt:

```python
"S2/BF2/nur_erster":     "10.6",   # Minusklammer nur beim ersten Glied
"S2/BF3/hochzahl":       "7.10",   # Hochzahlen beim Dividieren
"S2/BF1/punkt_vor_strich": "1.19", # Punkt vor Strich
"S4/BF6/zweite_variable": "12.4",  # Faktor steckt nicht in allen Gliedern
```

Kein Eintrag heisst: der Fehler gehört zur Lektion selbst. Dann wird nicht
zurückgesprungen, sondern weitergeübt — nicht jeder Fehler ist eine Lücke.

Nach dem Rücksprung merkt sich die App in `Lernweg.zurueck_zu`, wo er herkam.
Sobald die Lücke geschlossen ist, geht es **dort** weiter, nicht irgendwo.

---

## Der Einstufungstest

Binäre Suche durch das Netz, keine feste Aufgabenliste. Wer eine Leitaufgabe
löst, bekommt **alle Vorstufen gutgeschrieben** — sonst bräuchte der Test 41
Aufgaben statt zwölf.

Drei simulierte Schüler, gleicher Test, drei Startpunkte:

```
schwacher Schüler   5 Aufgaben   →  2/41 sicher   Start: 1.9  Vorzeichen
mittlerer Schüler   7 Aufgaben   →  9/41 sicher   Start: 2.2  Brüche kürzen
starker Schüler     9 Aufgaben   → 29/41 sicher   Start: 4.9  Produkte als Terme
```

Tippfehler zählen im Test nicht. Ein Vertipper würde sonst jemanden zu tief
einstufen, und er müsste wochenlang Bekanntes wiederholen.

---

## Wo es jetzt hakt — und das ist der Punkt

**Von 41 Zielektionen haben vier einen Generator.** Alle anderen kann die App
nicht üben.

Ich habe das **nicht** versteckt. Erster Entwurf hat solche Lektionen
stillschweigend als «sitzt» verbucht — damit hätte die App Lückenfreiheit
behauptet, wo keine ist. Jetzt stehen sie in einer eigenen Spalte
`Lernweg.uebersprungen`, zählen **nicht** als sicher, und die Statusseite nennt
sie beim Namen:

> **Noch nicht übbar** — Für 11 Lektionen gibt es noch keine Aufgaben.
> Sie zählen nicht als sicher: 1.9 Addieren und Subtrahieren mit Vorzeichen, …

Sobald ein Generator dazukommt, trägst du ihn in `SCHABLONE_FUER` ein und die
Lektion fällt von selbst in den Weg zurück.

**Solange das so ist, ist die Messlatte nicht erreichbar.** Der Einstufungstest
kann niemanden sinnvoll einordnen, wenn er nur zwei von zwölf Leitaufgaben
stellen kann. Das ist keine Schwäche der Mechanik — die läuft — sondern schlicht
fehlende Generatoren.

---

## Reihenfolge, die ich vorschlagen würde

Nicht nach Erhebungsaufgabe, sondern nach Hebelwirkung im Netz. Diese vier
Lektionen sind Voraussetzung für die meisten anderen:

| Lektion | was sie freischaltet |
|---|---|
| **10.6** Minus vor der Klammer | 11.4, 11.6, 13.6, 14.8, 10.16 |
| **4.8** gleichartige Terme | 4.9, 6.7, 10.15, 11.6 |
| **7.10** Potenzen mehrere Variablen | 8.9, 9.6, 12.6 |
| **13.4** einfache Gleichungen | 13.6, 13.9, 15.2 |

Mit diesen vier plus den zwei vorhandenen wären 20 der 41 Lektionen übbar —
knapp die Hälfte, und der Einstufungstest würde funktionieren.

---

## Datenbank

Drei neue Tabellen insgesamt, keine geänderte Spalte:
`BauformStand`, `KapitelStand`, `Lernweg`. `db.create_all()` legt sie an.

## Start

```powershell
python app.py
```

Nach dem Login geht es automatisch auf `/start` → Einstufungstest → `/lernen`.
Die alten Kapitel 1.3 bis 1.7 sind über `/lektion/1.3` weiterhin erreichbar.
