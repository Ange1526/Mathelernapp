# Dashboard und gemischte Aufgaben

## Was neu ist

Alle **170 Lektionen** stehen auf dem Dashboard, nach Kapiteln gruppiert.
Vier Zustände, alle mit deinen bestehenden CSS-Klassen:

| Zustand | Aussehen | anklickbar |
|---|---|---|
| sitzt | grün, Häkchen, Balken voll (`num-green`) | ja, zum Wiederholen |
| jetzt dran | blau, blauer Rand (`num-blue`) | ja |
| freigeschaltet | blau (`num-blue`) | ja |
| noch keine Aufgaben | grau, Hinweis (`num-grey`) | nein |
| gesperrt | grau, Schloss (`lock-icon`) | nein |

**Am Design habe ich nichts geändert.** Die Karten benutzen dieselben Klassen
wie vorher. Dazu kamen nur zwei Ergänzungen im `<style>`-Block:
`.kapitel-titel` für die Überschriften und `.chapters-grid.fein` — kleinere
Karten, weil es 170 statt fünf sind. Farben, Schatten, Radien: unverändert.

Freigeschaltet ist eine Lektion, wenn **alle ihre Voraussetzungen sitzen**. Das
kommt direkt aus der Landkarte. Wer nichts gemacht hat, sieht fast nur Schlösser
— das ist ehrlich, aber du kannst mir sagen, wenn dir das zu entmutigend ist.

## Gemischte Aufgaben

Der Knopf steht im violetten Banner neben «Jetzt weitermachen», und er
erscheint erst, wenn mindestens eine Lektion sitzt. Er zieht **reihum** durch
die Kapitel, die der Schüler schon hatte — nicht zufällig, sonst käme dasselbe
Thema mehrfach hintereinander.

Er greift ausschliesslich auf `Lernweg.sichere_menge()` zu. Kein Vorgriff auf
Themen, die noch nicht dran waren.

## Seitenleiste

Zwei Kacheln ausgetauscht, im gleichen Stil wie die anderen:

- **Lektionen sicher** — 62 von 170, mit Prozentzahl
- **Noch vor dir** — Stunden, Lektionen und Aufgabenzahl

Damit hat die Schülerin die Zahl, um die du gebeten hattest: sie sieht
jederzeit, wie viel noch kommt, und kann selbst entscheiden, ob sie zu Hause
etwas macht.

## Nachgeprüft

```
Dashboard HTTP 200
  Karten 170 | Schlösser 66 | Häkchen 62
  Knopf gemischt: True      aktuelle Lektion markiert: True
  Design erhalten: True
  /gemischt -> 200, Aufgabe wird gestellt
```

---

# Wie viele Generatoren noch fehlen

**131 von 170 Lektionen** haben keinen. Das sind rund **43 Schablonen**:

| Kapitel | Lektionen offen | Schablonen |
|---|---:|---:|
| K1 Zahlen und Vorzeichen | 20 | 7 |
| K2 Brüche | 13 | 4 |
| K3 Variablen | 12 | 4 |
| K5 Multiplikation | 9 | 3 |
| K6 gemischte Operationen | 5 | 2 |
| K8 Wurzeln | 10 | 3 |
| K9 Division | 7 | 2 |
| K10 Klammern (Rest) | 6 | 2 |
| K11 Distributivgesetz | 10 | 3 |
| K12 Faktorisieren (Rest) | 5 | 2 |
| K13 Gleichungen | 10 | 3 |
| K14 Bruchterme | 12 | 4 |
| K15 Bruchgleichungen | 9 | 3 |
| K16 Vermischtes | 3 | 1 |
| **Gesamt** | **131** | **43** |

Bei zwei bis drei Schablonen pro Runde sind das **etwa 16 bis 20 Runden**.

Meine Reihenfolge bleibt: **K1** (zwei Rücksprungziele plus Fundament),
dann **K2**, dann **K11** — danach hat jede Fehlerdiagnose im System ein Ziel,
das auch existiert. Erst wenn das steht, lohnt es sich, den Einstufungstest zu
verlängern.
