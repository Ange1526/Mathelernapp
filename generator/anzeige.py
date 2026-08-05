# -*- coding: utf-8 -*-
"""
Anzeige — SymPy-Ausdruck zu Schülerschreibweise.

Zwei Dinge, die SymPy von sich aus falsch macht:

1. `str()` schreibt `3*a**2`, der Schüler liest `3a²`.
2. SymPy sortiert Summanden alphabetisch um. Aus `xy³ − x²y²` wird beim
   Ausgeben `−x²y² + xy³`. Für die Aufgabe muss der Term aber so dastehen,
   wie er im Lehrmittel steht. Darum bauen wir Summen mit `zeige_summe()`
   aus den Gliedern selbst, statt sie SymPy zu überlassen.
"""
from __future__ import annotations

from sympy import sympify

# Nur einstellige Hochzahlen als hochgestellte Zeichen. Ab zehn wird ^ge
# schrieben, sonst liest niemand mehr, ob da ¹¹ oder ¹¹ steht.
HOCH = {2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹"}

#: Rückweg: Anzeigetext -> etwas, das der Parser lesen kann.
#: Wird gebraucht, wenn die Musterlösung als Eingabe geprüft wird.
_ZURUECK = {v: f"^{k}" for k, v in HOCH.items()}
MINUS = "−"          # typografisches Minus, nicht der Bindestrich


def zeige(e) -> str:
    """3*a**2 -> 3a²   ·   x*y -> xy"""
    t = str(sympify(e))
    t = t.replace("**", "^").replace("*", "")
    for k, v in HOCH.items():
        t = t.replace(f"^{k}", v)
    t = t.replace(" - ", f" {MINUS} ")
    return (MINUS + t[1:]) if t.startswith("-") else t


def zeige_summe(*glieder) -> str:
    """Term in DER Reihenfolge anzeigen, in der er gemeint ist."""
    teile = []
    for i, roh in enumerate(glieder):
        g = sympify(roh)
        negativ = bool(g.could_extract_minus_sign())
        txt = zeige(-g if negativ else g)
        if i == 0:
            teile.append((MINUS + txt) if negativ else txt)
        else:
            teile.append(f"{MINUS if negativ else '+'} {txt}")
    return " ".join(teile)


def zeige_produkt(*faktoren) -> str:
    """5b · 2c — mit Malpunkt, wo der Schüler ihn sieht."""
    return " · ".join(zeige(f) for f in faktoren)


def als_eingabe(text: str) -> str:
    """Anzeigetext -> Eingabetext.  3a² − 2  ->  3a^2 - 2

    Der Schüler tippt `a^2`, angezeigt wird `a²`. Für Tests und für die
    Anzeige der Musterlösung im Eingabefeld braucht es den Rückweg.
    """
    for hoch, roh in _ZURUECK.items():
        text = text.replace(hoch, roh)
    return text.replace(MINUS, "-").replace(" · ", "*")


def klammer(e) -> str:
    """(3a − 2) — mit Klammern, Vorzeichenreihenfolge beibehalten."""
    return f"({zeige(e)})"
