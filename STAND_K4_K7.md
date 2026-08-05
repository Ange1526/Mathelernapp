# K4 und K7 · Stand nach dieser Runde

Zwei neue Schablonen, beide aus einem Grund gebaut: **sie sind Rücksprungziele.**
4.8 und 7.10 gehören mit 10.6 zu den drei Lektionen, auf die die meisten
Fehlerdiagnosen zeigen. Ohne sie sagte die App «schau dir das an» und hatte
nichts zu zeigen.

| | |
|---|---|
| `s4k_gleichartig.py` | 4.1 – 4.10 · acht Bauformen · 920 Aufgaben getestet |
| `s7_potenzen.py` | 7.1 – 7.11 · acht Bauformen · 920 Aufgaben getestet |

**Lektionen mit Generator: 39 von 170** (vorher 18).

Ein Schüler ohne Vorwissen rechnet jetzt **228 Aufgaben** über fünf Schablonen,
bevor er in die Vertiefung kommt.

---

## Drei Funde aus den Testläufen

### 1 · Der Parser lässt keine Exponenten über 10 zu

Das ist eine Sicherung in deinem `eingabe_parser`, und sie ist richtig. Mein
Generator hat sie zunächst missachtet und Aufgaben wie `u⁵ · u⁴` gebaut — mit
der Musterlösung `u⁹`, aber dem Fehlerergebnis `u²⁰`. Die richtige Antwort wäre
angenommen worden, aber die App hätte den typischen Fehler nie erkennen können.

Schlimmer: bei `u⁶ · u⁵` wäre die **richtige** Lösung `u¹¹` gewesen — und der
Parser hätte die korrekte Eingabe des Schülers als Eingabefehler abgewiesen.

**225 unlösbare Aufgaben.** Neuer Filter `exponent_hoechstens(10)` prüft die
Lösung UND jeden Fehlerkatalogeintrag.

### 2 · Bei ungeraden Hochzahlen gibt es den Unterschied gar nicht

`−7²` gegen `(−7)²` ist der Kern von 7.4. Bei einer ungeraden Hochzahl ist
`(−7)³ = −7³` — kein Unterschied, und der Fehlerkatalog hätte denselben Wert
wie die Lösung gehabt. BF7 ist deshalb auf gerade Exponenten beschränkt.

### 3 · Der Koeffizient wird nur eins, wenn die Differenz eins ist

BF8 in K4 baute `6u + 5c − 8u` und behauptete, das Ergebnis sei `u + 5c`. Es ist
`−2u + 5c`. Die Zahlen waren frei gewürfelt; jetzt wird k1 aus k2 abgeleitet.

---

## Neu: `als_eingabe()`

`3a² − 2`  →  `3a^2 - 2`. Der Rückweg vom Anzeigetext zum Eingabetext. Wird
gebraucht, wenn die Musterlösung geprüft oder ins Eingabefeld gestellt wird.
Hochgestellte Zeichen gibt es nur noch bis `⁹`, darüber `^10` — sonst liest
niemand mehr, ob da `¹¹` oder `¹¹` steht.

---

## Restaufwand mit fünf Schablonen

Vier Wochen, eine Schullektion pro Woche = 3 Stunden in der Schule.

| Einstieg | Lektionen offen | Aufgaben | Gesamt | zu Hause pro Woche |
|---:|---:|---:|---:|---:|
| 0 % | 170 | 884 | 11.1 h | 122 min |
| 40 % | 102 | 530 | 6.6 h | 54 min |
| 50 % | 85 | 442 | 5.5 h | 38 min |
| 60 % | 68 | 353 | 4.4 h | 21 min |
| 70 % | 51 | 265 | 3.3 h | 4 min |

---

## Was als Nächstes

**Fünf Rücksprungziele haben noch keinen Generator:** 1.9, 1.19, 9.3, 11.4, 11.6.
Solange sie fehlen, läuft die Lückensuche in diesen Fällen ins Leere.

Meine Reihenfolge bleibt:

1. **K1** (1.9, 1.19) — zwei Rücksprungziele auf einmal, und das Fundament für
   schwache Schüler. Fünf Schablonen.
2. **K2 Brüche** — Rücksprungziel für K14 und K15. Sechs Schablonen.
3. **K11** (11.4, 11.6) — die letzten beiden Rücksprungziele, dazu Erhebung 2b.
4. **K9** (9.3) — dazu Erhebung 2c.

Nach Schritt 3 hat **jede** Fehlerdiagnose im System ein Ziel, das auch
existiert. Das ist der Punkt, an dem die Lückensuche vollständig ist.
