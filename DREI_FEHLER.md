# Die drei Fehler und wie sie behoben sind

Messlatte: **egal wo einer startet, am Schluss löst er einen vergleichbaren
Erhebungstest fehlerfrei — ohne Unter- und ohne Überforderung.**

Alles unten ist im laufenden Testclient nachgeprüft, nicht nur behauptet.

---

## Fehler 1 · Die Quotenlogik liess Lücken bestehen

**Vorher:** 10 Aufgaben, 80 % richtig, Aufstieg. Niemand schaute nach, *welche*
Aufgabe falsch war. Wer ausgerechnet die Minusklammer nie konnte, stieg auf und
scheiterte später an Erhebungsaufgabe 2b.

**Neu:** Jede Bauform hat ihr eigenes Häkchen (`BauformStand`). Zwei richtige
Antworten, dann sitzt sie. Ein Fehler nimmt eines wieder weg. Das Level gilt
erst als fertig, wenn **alle** Bauformen sitzen.

Nachgeprüft — ein Schüler, der BF3 nie kann:

```
Reihenfolge:  BF1 BF5 BF8 BF3 BF3 BF3 BF4 BF2 BF1 BF3 BF3 BF3 BF8 BF4 BF2 ...

Level:            A          (bleibt A — richtig, denn BF3 sitzt nicht)
gemeistert:       BF1 BF2 BF4 BF5 BF8
nicht gemeistert: BF3
```

Er steigt **nicht** auf. Die Lücke bleibt sichtbar, statt sich zu verstecken.

Und wer alles kann, ist zügig durch: **44 Aufgaben für alle drei Level** von
Kapitel 12.1, dabei jede der 22 Bauformen zweimal.

---

## Fehler 2 · Das Level hing am Schüler, nicht an der Lektion

**Vorher:** ein `current_user.current_level` für alles. Wer bei Brüchen schwach
und beim Faktorisieren stark ist, bekam für beides dasselbe Niveau — einmal
Überforderung, einmal Langeweile.

**Neu:** `KapitelStand` speichert ein Level **pro Kapitel**.

Nachgeprüft:

```
Kapitel 12.1: Level A        (dort hängt er an BF3)
Kapitel 6.1:  Level B        (dort ist er schon weiter)
```

`User.current_level` bleibt bestehen — die alten Zahlenkapitel 1.3 bis 1.7
benutzen es unverändert weiter.

---

## Fehler 3 · Keine Lückensuche

**Vorher:** Wer scheitert, bekommt dieselbe Aufgabe nochmals. Die App wusste
nicht, ob das Problem die Aufgabe selbst ist oder etwas darunter.

**Neu:** Nach drei Fehlversuchen an derselben Bauform erscheint ein Hinweis auf
das Kapitel, das diese Lektion **voraussetzt** — aus der Spalte «setzt voraus»
deiner Lektionslandkarte:

```python
VORAUSSETZUNGEN = {
    "6.1":  ["5.7", "4.8"],     # Punkt vor Strich mit Variablen
    "12.1": ["11.6"],           # Faktorisieren
}
```

Der Schüler sieht:

> **Vielleicht fehlt etwas davor**
> Diese Aufgabenart macht dir mehrfach Mühe. Das liegt oft nicht an der Aufgabe
> selbst, sondern an dem, was sie voraussetzt: «Ausmultiplizieren und
> zusammenfassen». Willst du das zuerst nochmals anschauen?
>
> [ Zuerst Ausmultiplizieren und zusammenfassen üben ]

Ein Klick wechselt ins Voraussetzungskapitel. **Er wird nicht gezwungen** — der
Vorschlag kann auch ignoriert werden.

---

## Ein vierter Fund unterwegs

Beim ersten Test hing der simulierte Schüler **36 Mal an derselben Aufgabe** und
sah die übrigen Bauformen nie. Grund: bei einer falschen Antwort bleibt die
Aufgabe offen, damit man es nochmals versuchen kann — und die Reihum-Ziehung kam
gar nie zum Zug.

Genau die Überforderung, die vermieden werden soll. Behoben: nach `MAX_TRIES`
Fehlversuchen wird die Lösung gezeigt und die **nächste Aufgabe ist eine andere
Bauform**. Die missglückte kehrt später zurück — sie gilt ja nicht als
gemeistert.

---

## Was sich in deiner Datenbank ändert

Zwei **neue** Tabellen, keine geänderte Spalte:

| Tabelle | wofür |
|---|---|
| `BauformStand` | Treffer, Fehler und Häkchen je Bauform und Level |
| `KapitelStand` | Level pro Kapitel plus die laufende Ziehungsreihenfolge |

`db.create_all()` legt sie beim ersten Start an. Deine bestehenden Daten bleiben
unangetastet.

---

## Anleitung

```powershell
# app.py ersetzen, Ordner generator\ daneben legen, templates\lektion.html ersetzen
python app.py
```

Prüfen:

```powershell
cd tests
python test_alle.py      # 1800 Aufgaben -> ALLES BESTANDEN
cd ..
```

---

## Was noch fehlt, um die Messlatte ganz zu erreichen

**Der Einstufungstest (E2).** Ohne ihn startet jeder bei Level A von Kapitel 1 —
auch der Gute. Das ist Unterforderung. Der Test braucht rund zwölf Leitaufgaben
quer durch die Landkarte; wer sie löst, überspringt die zugehörigen Kapitel.

**Die Rückwärts-Propagation (E3).** Wer eine schwere Bauform löst, kann die
Vorstufen. Aktuell muss er sie trotzdem durchlaufen.

**Die übrigen vier Erhebungsaufgaben.** 1, 3, 5 und 6 haben noch keinen
Generator — ohne sie ist der Test nicht abgedeckt und die Messlatte
grundsätzlich nicht erreichbar.

Das ist die wichtigste der drei Baustellen.
