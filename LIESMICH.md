# C1 bis C3 · Aufgabengenerator

Baut auf **deinem** Korrektur-Paket auf. Der Generator erzeugt fertige
`korrektur.Aufgabe`-Objekte — du gibst sie direkt an `auswerten()`.
An deinem B4-Code ändert sich nichts.

## Dateien

```
generator/schablone.py         Bauform, Schablone, ErzeugteAufgabe
generator/qualitaet.py         Qualitätsfilter gegen hässliche Zufallsaufgaben
generator/ziehung.py           Reihum-Ziehung und Mastery pro Bauform
generator/anzeige.py           SymPy-Ausdruck -> Schülerschreibweise
generator/s4_faktorisieren.py  Erhebungsaufgabe 4, acht Bauformen
generator/s2_grundoperationen.py  Erhebungsaufgabe 2, acht Bauformen
tests/test_s4.py               880 Aufgaben
tests/test_s2.py               920 Aufgaben
tests/test_alle.py             beide zusammen
demo_lauf.py                   Ein Durchlauf, wie ihn ein Schüler erlebt
```

Starten unter Windows:

```powershell
cd tests
python test_alle.py
cd ..
python demo_lauf.py
```

Der Ordner `korrektur\` muss daneben liegen (ist im Paket dabei).

---

## Deine fünf Fragen

### 1 · Wie beschreibe ich eine Aufgabenfamilie?

Eine **Bauform** besteht aus drei Dingen:

```python
BF3 = Bauform("BF3", "Zahl und Variable gemeinsam ausklammern",
    bereiche={"A": {"g": [2,3,4], "var": [x,a,y], "u": [2,3], "v": [1,2,3]},
              "B": {...}, "C": {...}},
    bauen=bf3,                                   # Parameter -> Aufgabe
    filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])
```

`bauen` bekommt die gewürfelten Parameter und liefert Frage, `korrektur.Aufgabe`
mit Musterlösung, Zielform und Fehlerkatalog, dazu Lösungsweg und drei Tipps.

### 2 · Wie verhindere ich hässliche Aufgaben?

Über Filter. Jeder bekommt `(parameter, gebaut)` und gibt `False` zurück, wenn
die Aufgabe verworfen und neu gewürfelt werden soll. Mitgeliefert:

| Filter | verhindert |
|---|---|
| `loesung_nicht_null` | Lösung 0 als Zufallsunfall |
| `nenner_freundlich` | Brüche mit Nenner 137 |
| `kopfrechenbar` | Zahlen über 1000 — kein Taschenrechner erlaubt |
| `parameter_verschieden("u","v")` | `6x + 6x` |
| `faktor_ist_groesster` | siehe unten, hat einen echten Fehler gefunden |
| `fehler_eindeutig` | siehe unten, ebenfalls |

`STANDARD` = die drei, die jede Schablone braucht.

### 3 · Wie hängen A/B/C an den Schablonen?

**Über Parameterbereiche derselben Bauform, nicht über eigene Schablonen.**
`bereiche` ist ein Dictionary mit einem Eintrag pro Level. Eine Bauform, die auf
einem Level nicht sinnvoll ist, bekommt `levels=("B","C")` — bei S4 betrifft das
BF6 und BF7, weil drei Glieder auf Level A zu früh sind.

Bei S4 trägt die Struktur den Sprung, nicht die Zahlengrösse:
A zwei Glieder · B Potenzen und zwei Variablen · C drei Glieder.

### 4 · Testfälle

`tests/test_s4.py` erzeugt 40 Aufgaben je Bauform und Level (880 insgesamt) und
prüft jede viermal: erzeugbar, Musterlösung wird als RICHTIG erkannt, und jeder
Eintrag im Fehlerkatalog wird als genau dieser Fehler erkannt. Aktuell: keine
Beanstandungen.

### 5 · Eine Schablone als Muster

`s4_faktorisieren.py` ist Erhebungsaufgabe 4 vollständig. Alle vier
Teilaufgaben stecken als Bauform drin: 4a = BF1, 4b = BF3, 4c = BF5, 4d = BF6.

---

## Drei Funde aus dem Testlauf

### A · Beim Faktorisieren sind die meisten Fehler FORMfehler, keine Wertfehler

`8(2x+4)` und `16(x+2)` haben denselben Wert. Ein wertbasierter Fehlerkatalog
kann sie nie unterscheiden. Dasselbe gilt für «nur zwei von drei Gliedern
ausgeklammert» und «Variable vergessen».

Diese Fälle fängt **deine Zielform `FAKTORISIERT` mit `content_streng=True`** ab
— sie kommen als `UNFERTIG` zurück, nicht als `FALSCH`. Das ist auch didaktisch
richtig: der Schüler hat richtig gerechnet.

In den Fehlerkatalog gehören nur Fehler, die den Wert ändern: Vorzeichen in der
Klammer, Hochzahl beim Teilen, weggelassene Eins.

Ich habe drei meiner ursprünglichen Katalogeinträge deshalb wieder entfernt.

### B · `fehler_eindeutig` — die App diagnostizierte richtige Antworten als Fehler

Bei manchen Zufallszahlen ergibt ein vorberechneter Fehler genau dieselbe Zahl
wie die Lösung. Dann meldet die App bei einer **richtigen** Antwort einen
Fehler. Der Filter verwirft solche Aufgaben. Er gehört in jede Schablone.

### C · `faktor_ist_groesster` — der Generator zeigte einen falschen Lösungsweg

Aus `g=12, u=4, v=2` entstand `48y² − 24y`, und der Generator behauptete, der
Faktor sei `12y`. In der Klammer bleibt aber `4y − 2`, darin steckt noch eine 2
— der grösste Faktor ist `24y`. Der Schüler hätte einen falschen Lösungsweg
gesehen und wäre bei der richtigen Antwort als «unfertig» abgewiesen worden.

---

## Ein Fund in deinem Korrektur-Modul

`_irreduzibel` in `pruefung.py` weist einen Faktor der Gestalt `−v²` ab.

```python
from korrektur import parse_answer
a = parse_answer("-v^2*x*(-v + x)", {"v", "x"})
# Mul.make_args(a.form) -> (-v**2, x, -v + x)
# -v**2 ist ein Mul(-1, v**2), kein Pow -> basis bleibt -v**2
# _irreduzibel(-v**2): factor() -> args (-1, v**2), v**2 ist Pow mit exp>1 -> False
```

Ergebnis: `−v²x(−v+x)` gilt als UNFERTIG, obwohl es eine gültige Faktorzerlegung
von `xy³ − x²y²` ist. Ein Schüler, der das Minus vorzieht statt in die Klammer
zu schreiben, wird abgewiesen.

Vorschlag: in `_ist_faktorisiert` das Vorzeichen vom Faktor trennen, bevor
`_irreduzibel` gerufen wird — also `basis = f.base if f.is_Pow else f` ersetzen
durch etwas, das `−v²` erst zu `v²` und dann zu `v` normalisiert.

Ich habe es **nicht** geändert, weil es dein Modul ist und du die Tests dazu
hast. Mein Generator umgeht es, indem er die Musterlösung als
`Faktor(Klammer)` in Schülerschreibweise baut statt über `factor()`.

---

## Erhebungsaufgabe 2 · Grundoperationen

Acht Bauformen, 920 Aufgaben im Test, keine Beanstandungen. Zwei davon treffen
die Originalaufgaben genau:

```
BF1 B:  5b − 5b · 2c + 3bc        →  5b − 7bc      (Erhebung 2a)
BF2 B:  11w − 2 · (5w + 4u)       →  w − 8u        (Erhebung 2b)
BF6 B:  12uv + 21u²v² : (7uv) + 56u²/(7u) − u · (2 − 3v)   (Erhebung 2c)
```

Zielform ist hier `ZUSAMMENGEFASST`. Anders als beim Faktorisieren ändern die
typischen Fehler den Wert — der Fehlerkatalog trägt also, und alle 1000
Katalogfehler werden erkannt.

Zwei neue Filter waren nötig:

- `symbole_verschieden("var","var2")` — es entstand `20u − 5 · (5u + 7u)`,
  beide Variablenplätze hatten dieselbe Variable gezogen.
- `alle_sorten_bleiben` — es entstand `15w − 3(5w + 4b)` mit dem Ergebnis
  `−12b`: die w hoben sich zufällig auf. Das ist ein legitimer Sonderfall, aber
  er gehört in eine eigene Bauform (hier BF7), nicht als Zufallstreffer in eine
  gewöhnliche.

## Was als Nächstes drankommt

Noch vier Erhebungsaufgaben, nach Aufwand sortiert: **3 Potenzen und Wurzeln**,
**5 Brüche**, **1 Gleichungen I**, **6 Gleichungen II**.

Bei 6 gilt deine Einschränkung: keine Bruchgleichungen erzeugen, die auf der
Definitionsmenge allgemeingültig sind. Polstellen sind unproblematisch,
`solve()` liefert dort `[]`.
