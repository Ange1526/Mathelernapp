# Umfang und Zeit — die echten Zahlen

## Korrektur: es sind 170 Lektionen, nicht 41

Mein erstes `netz.py` war ein von Hand gebauter, verkürzter Graph — pro
Lektionsgruppe nur eine Vertreterin. Das war ein Fehler mit Folgen: die App
hätte einen Schüler von 6.7 auf 4.8 zurückgeschickt, obwohl die Lücke bei 4.3
liegt — eine Lektion, die es in meinem Graphen gar nicht gab.

`netz.py` wird jetzt aus `Lektionslandkarte_Algebra_v5.docx` **erzeugt**, nicht
abgetippt. Beim Erzeugen wird geprüft:

```
Zyklus im Netz:                        keiner — der Graph ist sauber
Voraussetzungen ohne eigene Zeile:     keine
Lektionen:                             170
```

**Alle 170 gehören zum Weg**, auch die 39, die für die Erhebung nicht nötig
wären — das Ziel ist die solide Basis, nicht nur der Test. Die Erhebung bleibt
der Massstab: `pruefungsmenge()` gibt die 131 Lektionen zurück, an denen
gemessen wird.

---

## Der Levelsprung

Wer die Leitaufgabe auf Level B löst, steigt in den folgenden Lektionen bei B
ein statt bei A. Das spart rund zwei Drittel der Übungszeit — und A wäre für ihn
Unterforderung.

**Die Theorie sieht er trotzdem.** Teil 6 der Schablone, die Kernidee, wird beim
Einstieg in jede Lektion einmal gezeigt, unabhängig vom Level:

> Ausklammern ist das Umgekehrte des Ausmultiplizierens: der grösste Faktor,
> der in JEDEM Glied steckt, kommt vor die Klammer.

---

## Wie lange dauert es?

Vier Wochen, eine Schullektion pro Woche à 45 Minuten = **3 Stunden in der
Schule**. Was darüber hinausgeht, ist Heimarbeit.

| Einstieg | Lektionen offen | Aufgaben | Gesamt | zu Hause pro Woche |
|---:|---:|---:|---:|---:|
| 0 % | 170 | 884 | 11.1 h | 122 min |
| 20 % | 136 | 707 | 8.8 h | 87 min |
| 30 % | 119 | 618 | 7.7 h | 70 min |
| **40 %** | 102 | 530 | 6.6 h | 54 min |
| **50 %** | 85 | 442 | 5.5 h | 38 min |
| **60 %** | 68 | 353 | 4.4 h | 21 min |
| 70 % | 51 | 265 | 3.3 h | 4 min |
| 80 % | 34 | 176 | 2.2 h | fertig vor Schluss |

Die Kennzahlen kommen aus dem Testlauf, nicht aus dem Bauch: eine Schablone mit
zwölf Bauformen braucht mit Levelsprung rund 15 Aufgaben, eine Schablone deckt
im Schnitt 2.9 Lektionen ab, 45 Sekunden pro Aufgabe.

`netz.restaufwand(sicher)` rechnet das live — die Zahl kann der Schülerin also
jederzeit angezeigt werden, damit sie sich einteilen kann.

---

## Wo steigen Erstklässler ein?

Aus dem Stoff geschlossen, nicht gemessen: K1 und K2 sitzen aus der Sek (Zahlen,
Vorzeichen, Brüche), K3 bis K6 grösstenteils (Variablen, Terme), ab K7 wird es
dünn (Potenzen, Wurzeln), K13 bis K15 meist gar nicht (Gleichungen, Bruchterme,
Bruchgleichungen).

Das entspricht **40 bis 60 Prozent** — also 4.4 bis 6.6 Stunden, oder 21 bis 54
Minuten Heimarbeit pro Woche. **Das füllt die vier Wochen, ohne zu überfordern.**

Drei simulierte Schüler durch den Einstufungstest:

```
schwach   7 Aufgaben  ->  25/170 sicher   noch 145 Lektionen,  9.4 h
mittel    7 Aufgaben  ->  41/170 sicher   noch 129 Lektionen,  8.4 h
stark    10 Aufgaben  ->  79/170 sicher   noch  91 Lektionen,  5.9 h
```

Selbst der starke Schüler ist nicht nach einer Woche durch. Das war deine Sorge,
und mit allen 170 Lektionen erledigt sie sich.

---

## Zwei Dinge, die noch offen sind

**Der Fall «fertig vor Schluss».** Wer bei über 70 Prozent einsteigt, ist vor
Ablauf der vier Wochen durch. Dann braucht es etwas: durchgängig Level C, eine
Wiederholungsrunde über die wackligsten Bauformen, oder eine Probe-Erhebung.
Sag mir, was dir lieber ist — ich baue es.

**Die Generatoren.** Von 170 Lektionen haben **sieben** einen. Die Tabelle oben
beschreibt, was möglich wäre, nicht was heute läuft. Ohne die übrigen
Generatoren bleibt jede Zeitangabe eine Rechnung auf dem Papier.
