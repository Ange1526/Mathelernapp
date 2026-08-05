# Anbindung an deine App — was zu tun ist

Drei Schritte, alle unter Windows in PowerShell.

## 1 · Dateien kopieren

In deinen Projektordner (dort, wo `app.py` und der Ordner `korrektur\` liegen):

```
dein-projekt\
├── app.py              ← ERSETZEN durch die neue Datei
├── korrektur\          ← bleibt unverändert
├── generator\          ← NEU, ganzer Ordner
│   ├── __init__.py
│   ├── anzeige.py
│   ├── anbindung.py
│   ├── qualitaet.py
│   ├── schablone.py
│   ├── ziehung.py
│   ├── s2_grundoperationen.py
│   └── s4_faktorisieren.py
├── templates\          ← bleibt unverändert
└── tests\              ← NEU, optional
```

## 2 · Starten

```powershell
python app.py
```

Im Browser sind zwei neue Kapitel da: **6.1 Grundoperationen** und
**12.1 Faktorisieren**. Die alten Kapitel 1.3 bis 1.7 laufen unverändert weiter.

## 3 · Prüfen, ob alles läuft

```powershell
cd tests
python test_alle.py
cd ..
```

1800 Aufgaben, beide Schablonen. Erwartete Ausgabe am Schluss: `ALLES BESTANDEN`.

---

## Was ich in app.py geändert habe

Neun Stellen, sonst nichts. Deine Datenmodelle, Login, Levellogik und Templates
sind unangetastet.

| Stelle | Änderung |
|---|---|
| Import | `from generator.anbindung import ...` dazu |
| `CHAPTER_NAMES` | Kapitel aus dem Generator ergänzt |
| `get_hint()` | bei Generatorkapiteln kommt der Tipp aus der Schablone statt aus `HINTS` |
| neu: `neue_aufgabe_fuer()` | erzeugt eine Aufgabe, egal ob aus dem Generator oder aus `generate_math_task()` |
| `lektion()` | legt die **ganze** Aufgabe in `session["aufgabe"]` |
| `check()` | baut die Aufgabe mit `aufgabe_aus_session()` statt mit `aufgabe_aus_generator()` |
| `markieren()` | Lösung ist neu ein Text; `_als_float()` schreibt nur echte Zahlen in die Float-Spalte |
| `close_task()`, `reset_progress()` | verwerfen `session["aufgabe"]` mit |
| `dashboard()` | zeigt die neuen Kapitel an |

### Warum das nötig war

Bisher stand in der Session nur die Lösung als Float, und `check()` baute die
Aufgabe daraus neu:

```python
aufgabe = aufgabe_aus_generator(korrekte_loesung)     # alt
```

Damit gingen **Zielform und Fehlerkatalog verloren**. Bei einer
Faktorisieraufgabe hätte die App `2az + 3a` als richtig durchgewinkt, obwohl
`a(2z + 3)` verlangt ist. Jetzt liegt die ganze Aufgabe in der Session:

```python
aufgabe = aufgabe_aus_session(daten)                  # neu
```

Nachgeprüft im laufenden Testclient:

```
Aufgabe: 3a + 2az   korrekt: a(2z + 3)
  Eingabe «a(2z + 3)»   -> success   Richtig.
  Eingabe «2*a*z + 3*a» -> warning   Stimmt — aber das ist noch kein fertiges Produkt.
```

---

## Was der Testclient sonst noch bestätigt hat

```
12.1 A «u + 3cu»              -> «u(3c + 1)»        richtig
12.1 A «4x + 7y + 11»         -> «4x + 28y + 44»    falsch / etwas_ausgeklammert
6.1  A «3b − 3b · 2u + 3bu»   -> «3b - 3bu»         richtig
6.1  A «11m − 2 · (2m + 4n)»  -> «7m + 4n»          falsch / nur_erster
1.3  A «6 + (-7)»             -> «-1»               richtig
```

Die alten Zahlenkapitel funktionieren unverändert, die neuen liefern den
Fehlerschlüssel ins `TaskAttempt` — das ist dein Studienmaterial.

---

## Eine Sache, die dir auffallen wird

Tippfehler (`EINGABEFEHLER`) landen **nicht** in `TaskAttempt`. Deine `check()`
kehrt vorher um. Für die Quote ist das richtig, für die Auswertung schade: du
siehst später nicht, wie oft die Eingabe das Problem war und nicht die Mathematik.

Falls du das ändern willst, gehört in `check()` vor dem frühen `return` ein
`TaskAttempt`-Eintrag mit `correct=False` und `status="eingabefehler"`. Ich habe
es **nicht** geändert, weil es deine Zählweise betrifft.

---

## Kapitelnummern

`generator/anbindung.py`, ganz oben:

```python
KAPITEL = {
    "6.1":  S2,     # Grundoperationen — Erhebung 2a, 2b, 2c
    "12.1": S4,     # Faktorisieren    — Erhebung 4a bis 4d
}
```

Dort trägst du die weiteren Schablonen ein, sobald sie fertig sind.
