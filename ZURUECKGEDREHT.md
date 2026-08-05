# Was ich zurückgedreht habe

Ich habe vier Dinge verändert, die du nie angefragt hast. Sie sind raus.

| | vorher (kaputt) | jetzt (wie ursprünglich) |
|---|---|---|
| Nach dem Login | Zwangsweiterleitung in den Einstufungstest | zurück aufs Dashboard |
| Startseite `/` | leitete Eingeloggte weiter | zeigt wieder `index.html` |
| Falsche Antwort | nach drei Fehlversuchen kam automatisch eine andere Aufgabe | Aufgabe bleibt stehen, Hinweisbox erscheint, Lösung nach `MAX_TRIES` |
| Dashboard-Kapitel | ich hatte 4.1, 7.1, 10.1, 12.1 hineingeschrieben | wieder nur 1.3 bis 1.7 |

Nachgeprüft im Testclient: bei einer falschen Antwort bleibt dieselbe Aufgabe
stehen, die Hinweisbox kommt, und nach drei Versuchen die Lösung — in den alten
Kapiteln (1.3) **und** in den neuen (10.1) identisch.

An `login.html`, `register.html`, `dashboard.html` und `base.html` habe ich
**nie** etwas geändert; die waren nie in einem meiner ZIPs. Was du beim Login
anders erlebt hast, war die Zwangsweiterleitung — die ist jetzt weg.

---

## Was ich ohne deine Dateien nicht bauen kann

### Dashboard mit allen Lektionen

Du willst alle 170 Lektionen sehen, gesperrte nicht anklickbar — **im
bestehenden Design**. Dafür brauche ich `dashboard.html`. Ohne sie müsste ich
das Aussehen erfinden, und genau das soll ich nicht.

Schick mir die Datei, dann baue ich hinein:

- alle Lektionen nach Kapiteln gruppiert
- freigeschaltet = anklickbar, gesperrt = ausgegraut, aktuelle hervorgehoben
- den Knopf für gemischte Aufgaben

Ich benutze dabei nur die CSS-Klassen, die schon in deiner Datei stehen.

### Gemischte Aufgaben über bisherige Themen

Braucht dasselbe Dashboard. Die Logik selbst ist klein: aus
`Lernweg.sichere_menge()` alle Lektionen mit Generator nehmen, daraus reihum
ziehen. Das kann ich vorbereiten, sobald ich weiss, wo der Knopf hinsoll.

---

## Der Einstufungstest ist kurz, weil es zu wenig Generatoren gibt

Das ist kein Konstruktionsfehler, sondern eine Folge: **von 170 Lektionen haben
39 einen Generator.** Der Test kann nur fragen, wozu es Aufgaben gibt — bei fünf
Schablonen sind das vier bis fünf Fragen.

«Alle Themen kurz drin» heisst rund zwölf Fragen quer durch alle Kapitel. Dafür
braucht es mindestens je einen Generator für K1, K2, K5, K8, K9, K11, K13, K14,
K15. Das sind die noch fehlenden rund 40 Schablonen.

Solange die fehlen, gilt: wer alles kann, wird trotzdem weit unten eingestuft —
weil die App es nicht prüfen kann. Ich kann den Test nicht länger machen, ohne
Aufgaben zu erfinden, die es nicht gibt.
