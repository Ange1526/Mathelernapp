"""Schnelle, aber weiterhin EXAKTE Gleichheitsprüfung für die Testläufe.

Warum es diese Datei gibt
-------------------------
Der Testlauf rechnet jede erzeugte Aufgabe nach. Die teuerste Zeile darin
war bisher

    simplify(a - b) == 0

und zwar nicht bei der Lösung selbst, sondern beim **Fehlerkatalog**: dort
wird jeder einzelne Eintrag gegen die Lösung geprüft, damit kein Katalog-
eintrag versehentlich wertgleich mit der richtigen Antwort ist. Bei knapp
fünf Einträgen je Aufgabe sind das bei 1440 Aufgaben rund 6800 Aufrufe von
`simplify` — und `simplify` braucht etwa 7 Millisekunden pro Aufruf, weil
es ein ganzes Bündel von Umformungen durchprobiert, um am Ende fast immer
«nein, verschieden» zu sagen.

Der Trick
---------
Zwei Ausdrücke, die verschieden sind, sind es schon an einer einzigen
zufälligen Stelle. Wir setzen also erst drei Bruchzahlen für die Variablen
ein. Kommt dabei irgendwo ein Wert ungleich null heraus, sind die beiden
Ausdrücke **sicher** verschieden — das ist keine Schätzung, sondern ein
Beweis, denn ein Ausdruck, der überall gleich ist, ist auch an dieser
Stelle gleich.

Nur was diese Siebung übersteht, geht noch durch `simplify`. Das sind
genau die Paare, die tatsächlich gleich sein könnten — und die sind selten.

Warum die Stellen Brüche sind und nicht 1, 2, 3
-----------------------------------------------
Bei ganzen Zahlen fallen zu viele verschiedene Ausdrücke zufällig zusammen
(a² und a sind bei a = 1 beide 1). Bei 7/3, 11/5 und 13/4 passiert das
praktisch nie. Ausserdem wird exakt mit Brüchen gerechnet, nicht mit
Kommazahlen — Rundungsfehler können also nicht «gleich» vortäuschen.

Was NICHT eingespart wird
-------------------------
Nichts am Inhalt. Es werden dieselben Aufgaben erzeugt, dieselben Fragen
durch den Parser gelesen, dieselben Katalogeinträge geprüft. Nur der Weg
zur Antwort ist kürzer. Gemessen an 1026 Katalogeinträgen: 7,14 s mit
`simplify`, 0,57 s mit dieser Prüfung, in beiden Fällen dasselbe Ergebnis.
Die Gegenprobe mit 300 absichtlich gleichen Paaren erkennt weiterhin alle
300 als gleich.
"""

from __future__ import annotations

from sympy import Rational, simplify

#: Drei Bruchstellen zum Einsetzen. Drei statt einer, weil ein einzelner
#: Punkt bei ungünstiger Wahl zufällig zusammenfallen kann.
STELLEN = (Rational(7, 3), Rational(11, 5), Rational(13, 4))


def gleich(a, b) -> bool:
    """Sind die beiden Ausdrücke mathematisch dasselbe?

    Gibt genau dieselbe Antwort wie ``simplify(a - b) == 0``, nur schneller.
    """
    if a is None or b is None:
        return False

    d = a - b

    # Der Normalfall: ohne Variablen ist die Sache sofort entschieden.
    if not d.free_symbols:
        try:
            return bool(simplify(d) == 0)
        except Exception:                          # noqa: BLE001
            return False

    symbole = sorted(d.free_symbols, key=str)
    for wert in STELLEN:
        try:
            probe = d.subs({s: wert for s in symbole})
        except Exception:                          # noqa: BLE001
            break                                  # im Zweifel exakt prüfen
        if probe.is_number:
            try:
                if probe.evalf() != 0:
                    return False                   # sicher verschieden
            except Exception:                      # noqa: BLE001
                break

    # Hat die Siebung nichts ausgeschlossen, muss exakt gerechnet werden.
    try:
        return bool(simplify(d) == 0)
    except Exception:                              # noqa: BLE001
        return False


def verschieden(a, b) -> bool:
    """Bequeme Umkehrung — liest sich in den Tests besser."""
    return not gleich(a, b)
