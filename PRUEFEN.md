# Wenn beim Start ein SyntaxError kommt

```
File "app.py", line 559
    existing =
              ^
SyntaxError: invalid syntax
```

Das ist **kein Fehler im Code**, sondern eine abgeschnittene Datei. Meine
`app.py` hat 1329 Zeilen, und `existing = User.query...` steht dort vollständig
auf Zeile 1220. Wenn der Fehler bei 559 auftritt, ist beim Herunterladen oder
Kopieren rund die Hälfte verlorengegangen.

## So prüfst du, ob eine Datei vollständig ist

In PowerShell, im Projektordner:

```powershell
(Get-Content app.py).Count
```

Erwartet: **1330**. Steht dort weniger, ist die Datei unvollständig.

Und der Schnelltest, ob Python sie überhaupt lesen kann:

```powershell
python -m py_compile app.py
```

Keine Ausgabe heisst: alles in Ordnung. Kommt ein `SyntaxError`, ist die Datei
kaputt — dann nochmals herunterladen, nicht suchen gehen.

## Dasselbe für die anderen Dateien

```powershell
Get-ChildItem generator\*.py | ForEach-Object { "$($_.Name): $((Get-Content $_).Count) Zeilen" }
```

Erwartete Zeilenzahlen:

| Datei | Zeilen |
|---|---:|
| anbindung.py | 117 |
| anzeige.py | 69 |
| einstufung.py | 144 |
| lernstand.py | 134 |
| netz.py | 232 |
| netz_daten.py | 178 |
| qualitaet.py | 213 |
| s10_klammern.py | 252 |
| s2_grundoperationen.py | 381 |
| s4_faktorisieren.py | 323 |
| s4k_gleichartig.py | 316 |
| s7_potenzen.py | 289 |
| schablone.py | 109 |
| vertiefung.py | 135 |
| ziehung.py | 62 |

Die genauen Zahlen können um ein, zwei Zeilen abweichen — worauf es ankommt:
keine Datei sollte nur halb so lang sein wie hier angegeben.

## Wenn alles vollständig ist

```powershell
cd tests
python test_alle.py
cd ..
python app.py
```

`test_alle.py` muss mit **ALLES BESTANDEN** enden. Erst danach lohnt es sich,
die App im Browser zu öffnen.
