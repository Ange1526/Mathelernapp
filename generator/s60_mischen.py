# -*- coding: utf-8 -*-
"""
S60 · Mischaufgaben — zwei bis drei Kapitel in EINER Aufgabe

Die App übt heute Einzelteile: Wurzeln bei den Wurzeln, Potenzen bei den
Potenzen. Die Erhebung tut das nicht. Aufgabe 4 verlangt Faktorisieren und
Potenzen gleichzeitig, Aufgabe 2c eine Division mitten in einem längeren
Term. Wer nur Einzelteile geübt hat, scheitert nicht am Stoff, sondern an
der Kombination — und genau das misst die Erhebung.

Zielrichtung, wörtlich aus dem Auftrag:

    √(36a⁴) · 2a − 4a³

Diese Schablone ist eine Stufe ÜBER Level C der Einzelkapitel und etwas
schwerer als die Erhebung selbst. Kein neuer Stoff: jede einzelne Handlung
kommt aus einem Kapitel, das der Schüler schon hatte. Neu ist nur, dass er
sie in der richtigen Reihenfolge hintereinander ausführen muss.

WELCHE KAPITEL WERDEN KOMBINIERT

    BF1   Wurzel · Monom − Monom              K8 · K5 · K4
    BF2   Potenz ausrechnen, zusammenfassen   K7 · K4
    BF3   Klammer mal Zahl, zusammenfassen    K10 · K4
    BF4   Division, dann zusammenfassen       K9 · K4
    BF5   Wurzel und Potenzgesetz             K8 · K7
    BF6   Produkt zweier Monome minus Monom   K5 · K4
    BF7   Minus vor der Klammer               K10 · K4
    BF8   Division mit Wurzel                 K8 · K9
    BF9   Sonderfall · Ergebnis ist null      K8 · K4
    BF10  Sonderfall · Koeffizient ist eins   K8 · K5 · K4
    BF11  Sonderfall · nichts geht zusammen   K7 · K4
    BF12  Division, Wurzel und Subtraktion    K9 · K8 · K4

DIE LEVELACHSE IST STRUKTURELL

    A   zwei Teilschritte · eine Variable · zwei Glieder
    B   zwei Teilschritte · eine Variable · Vorzeichenwechsel, drei Glieder
        oder höhere Potenzstufe im Zwischenschritt
    C   drei Teilschritte · ZWEI Variablen · drei Glieder mit gemischten
        Vorzeichen

Gesperrt bleibt die Zahlengrösse: alle drei Level ziehen aus denselben
Zahlenvorräten. Was A von C trennt, ist die Anzahl Schritte und die zweite
Variable — nicht, ob dort 3 oder 9 steht.

DIE VIER SONDERFÄLLE sind eigene Bauformen, nicht Zufallstreffer. Ohne sie
lernt der Schüler, dass am Schluss immer etwas Kürzeres dasteht, und schreibt
in der Prüfung irgendetwas hin, statt «geht nicht weiter» zu erkennen.
"""
from __future__ import annotations

import re

from sympy import Integer, Rational, sqrt

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

a, b, u, v, x, y = symbole("a b u v x y")
VARS = {"a", "b", "u", "v", "x", "y"}

#: Erste und zweite Variable. Zwei getrennte Vorräte, damit in einer Aufgabe
#: nie zweimal dasselbe Zeichen steht.
EINS = ["a", "x", "u"]
ZWEI = ["b", "y", "v"]

SYM = {"a": a, "b": b, "u": u, "v": v, "x": x, "y": y}


# ══════════════════════════════════════════════════════════════════════════
# Anzeige — Terme so schreiben, wie sie im Lehrmittel stehen
# ══════════════════════════════════════════════════════════════════════════

def pot(zeichen: str, e: int) -> str:
    """a², a³ — ab zehn wieder a^10."""
    if e == 0:
        return ""
    if e == 1:
        return zeichen
    return f"{zeichen}{HOCH.get(e, f'^{e}')}"


def T(koeff, *paare) -> str:
    """Ein Monom als Text.  T(3, ('a', 2), ('b', 1))  ->  3a²b

    Koeffizient 1 verschwindet, −1 wird zum blossen Minus. Ohne das steht in
    der Aufgabe «1a²», und der Schüler denkt, das sei ein Tippfehler.
    """
    k = int(koeff)
    teil = "".join(pot(z, e) for z, e in paare if e)
    if not teil:
        return f"{MINUS}{abs(k)}" if k < 0 else str(k)
    if abs(k) == 1:
        vor = MINUS if k < 0 else ""
        return f"{vor}{teil}"
    vor = MINUS if k < 0 else ""
    return f"{vor}{abs(k)}{teil}"


def reihe(*teile: str) -> str:
    """Glieder aneinanderhängen und dabei die Vorzeichen richtig setzen.

    SymPy sortiert Summen alphabetisch um. Für die Aufgabe muss der Term aber
    so dastehen, wie er gemeint ist — darum wird der Text hier aus den
    Gliedern selbst gebaut und nie über `str()` eines Ausdrucks.
    """
    raus = teile[0]
    for t in teile[1:]:
        if t.startswith(MINUS):
            raus += f" {MINUS} {t[1:]}"
        else:
            raus += f" + {t}"
    return raus


def W(inhalt: str) -> str:
    """√(36a⁴) — immer mit Klammer, sonst ist die Eingabe mehrdeutig."""
    return f"√({inhalt})"


def M(koeff, *paare):
    """Dasselbe Monom als SymPy-Ausdruck."""
    e = Integer(koeff)
    for z, k in paare:
        if k:
            e = e * SYM[z] ** k
    return e


def F(schluessel: str, ergebnis, text: str) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def bau(frage, loesung, loesung_text, fehler, schritte, tipps):
    """Zusammensetzen und den Fehlerkatalog sieben.

    Einträge, die WERTGLEICH der Lösung sind, müssen weg: sonst bekommt ein
    Schüler für die richtige Antwort eine Fehlermeldung. Doppelte müssen
    ebenfalls weg, sonst ist die Diagnose mehrdeutig und `fehler_eindeutig`
    verwirft die ganze Aufgabe.
    """
    ziel = Loesung.zahl(loesung).expr
    gesehen, brauchbar = set(), []
    for f in fehler:
        w = f.ergebnis.expr
        if w is None or w == ziel or w in gesehen:
            continue
        gesehen.add(w)
        brauchbar.append(f)
    return {"frage": frage, "loesung_text": loesung_text,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=brauchbar),
            "schritte": schritte, "tipps": tipps}


#: Mindestens vier Einträge je Aufgabe müssen übrig bleiben. Der Richtwert
#: des Projekts ist 1,6 — hier liegt er höher, weil eine Mischaufgabe mehr
#: Stellen hat, an denen etwas schiefgehen kann.
def genug_fehler(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 3


def kein_null_glied(p, g) -> bool:
    """Kein Glied mit dem Koeffizienten null im Ergebnis.

    Bei k = m ergibt «7a² − (4a² + 3a²)» die Anzeige «0a²». Das ist keine
    Sonderfall-Aufgabe, sondern ein Anzeigefehler — den Sonderfall «Ergebnis
    ist null» baut BF9, und dort steht sauber «0». Beim Nachrechnen über den
    Parser ist genau das aufgefallen: «0x − 20» wurde als Eingabefehler
    zurückgewiesen.
    """
    return not re.search(r"(^|[\s(])0[a-zA-Z]", g.get("loesung_text", ""))


STD = [kopfrechenbar, fehler_eindeutig, genug_fehler, kein_null_glied]

TIPPS = [
    "Diese Aufgabe besteht aus mehreren Schritten. Mach zuerst alles, was "
    "für sich allein steht — Wurzel, Potenz, Klammer, Division. Erst danach "
    "wird zusammengefasst.",
    "Punkt vor Strich gilt auch hier: Multiplizieren und Dividieren kommen "
    "vor dem Plus und Minus. Die Wurzel und die Potenz stehen noch davor.",
    "Zusammenfassen darfst du nur, was dieselbe Variable mit derselben "
    "Hochzahl hat. a² und a³ sind verschiedene Sorten und bleiben "
    "nebeneinander stehen.",
]


# ══════════════════════════════════════════════════════════════════════════
# BF1 · Wurzel · Monom − Monom            K8 · K5 · K4
# Die Zielaufgabe aus dem Auftrag:  √(36a⁴) · 2a − 4a³
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    k, m, n, z = p["k"], p["m"], p["n"], p["z"]
    e = p["e"]                 # Hochzahl unter der Wurzel: 2 oder 4
    h = e // 2                 # nach dem Ziehen
    zwei = p.get("z2")

    if zwei:                   # Level C: zweite Variable
        rad = T(k * k, (z, e), (zwei, 2))
        frage = reihe(f"{W(rad)} · {T(m, (z, 1))}",
                      T(-n, (z, h + 1), (zwei, 1)))
        loesung = M(k * m - n, (z, h + 1), (zwei, 1))
        text = T(k * m - n, (z, h + 1), (zwei, 1))
        wurzel_txt = T(k, (z, h), (zwei, 1))
        fehler = [
            F("wurzel_nicht_gezogen", M(k * k * m - n, (z, e + 1), (zwei, 1)),
              f"Unter der Wurzel muss zuerst gezogen werden: "
              f"{W(rad)} = {wurzel_txt}. Erst dann wird multipliziert."),
            F("hochzahl_nicht_halbiert", M(k * m - n, (z, e + 1), (zwei, 1)),
              f"Beim Wurzelziehen wird die Hochzahl HALBIERT, nicht "
              f"übernommen: aus {pot(z, e)} wird {pot(z, h)}."),
            F("zweite_variable_vergessen", M(k * m - n, (z, h + 1)),
              f"Unter der Wurzel steht auch {pot(zwei, 2)}. Daraus wird "
              f"{zwei}, und das gehört ins Ergebnis."),
            F("nicht_zusammengefasst", M(k * m, (z, h + 1), (zwei, 1)),
              "Der zweite Term wurde weggelassen. Beide Glieder haben "
              "dieselbe Sorte, sie müssen verrechnet werden."),
            F("koeffizient_addiert", M(k + m - n, (z, h + 1), (zwei, 1)),
              f"{k} und {m} werden MULTIPLIZIERT, nicht addiert: "
              f"{k} · {m} = {k*m}."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                    ("Multiplizieren", f"{wurzel_txt} · {T(m,(z,1))} = "
                                       f"{T(k*m,(z,h+1),(zwei,1))}"),
                    ("Zusammenfassen", f"{T(k*m,(z,h+1),(zwei,1))} {MINUS} "
                                       f"{T(n,(z,h+1),(zwei,1))} = {text}")]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = reihe(f"{W(rad)} · {T(m, (z, 1))}", T(-n, (z, h + 1)))
    loesung = M(k * m - n, (z, h + 1))
    text = T(k * m - n, (z, h + 1))
    wurzel_txt = T(k, (z, h))
    fehler = [
        F("wurzel_nicht_gezogen", M(k * k * m - n, (z, e + 1)),
          f"Unter der Wurzel muss zuerst gezogen werden: {W(rad)} = "
          f"{wurzel_txt}. Erst dann wird multipliziert."),
        F("hochzahl_nicht_halbiert", M(k * m - n, (z, e + 1)),
          f"Beim Wurzelziehen wird die Hochzahl HALBIERT, nicht übernommen: "
          f"aus {pot(z, e)} wird {pot(z, h)}."),
        F("nicht_zusammengefasst", M(k * m, (z, h + 1)),
          "Der zweite Term wurde weggelassen. Beide Glieder haben dieselbe "
          "Sorte, sie müssen verrechnet werden."),
        F("koeffizient_addiert", M(k + m - n, (z, h + 1)),
          f"{k} und {m} werden MULTIPLIZIERT, nicht addiert: {k} · {m} = {k*m}."),
        F("hochzahl_addiert_statt_mal", M(k * m - n, (z, h + 2)),
          f"Beim Multiplizieren werden die Hochzahlen addiert: "
          f"{pot(z, h)} · {z} = {pot(z, h+1)}, nicht {pot(z, h+2)}."),
        F("minus_uebersehen", M(k * m + n, (z, h + 1)),
          "Vor dem zweiten Glied steht ein Minus. Es wird abgezogen, "
          "nicht dazugezählt."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                ("Multiplizieren", f"{wurzel_txt} · {T(m,(z,1))} = {T(k*m,(z,h+1))}"),
                ("Zusammenfassen", f"{T(k*m,(z,h+1))} {MINUS} {T(n,(z,h+1))} = {text}")]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF1 = Bauform("BF1", "Wurzel mal Monom, dann abziehen",
              bereiche={
                  "A": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4], "n": [1, 2, 3, 5],
                        "z": EINS, "e": [2], "z2": [None]},
                  "B": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4], "n": [2, 3, 4, 5, 7],
                        "z": EINS, "e": [4], "z2": [None]},
                  "C": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4], "n": [2, 3, 4, 5, 7],
                        "z": EINS, "e": [4], "z2": ZWEI},
              }, bauen=bf1, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF2 · Potenz ausrechnen, dann zusammenfassen            K7 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf2(p):
    k, m, n, z, zwei = p["k"], p["m"], p["n"], p["z"], p.get("z2")
    g = p["g"]                       # Hochzahl in der Klammer

    if zwei:
        frage = reihe(f"({T(k,(z,g),(zwei,1))})²",
                      T(-m, (z, 2 * g), (zwei, 2)),
                      T(n, (z, 2 * g), (zwei, 2)))
        wert = k * k - m + n
        loesung = M(wert, (z, 2 * g), (zwei, 2))
        text = T(wert, (z, 2 * g), (zwei, 2))
        quad = T(k * k, (z, 2 * g), (zwei, 2))
        fehler = [
            F("koeffizient_nicht_quadriert", M(k - m + n, (z, 2 * g), (zwei, 2)),
              f"Beim Quadrieren wird AUCH die Zahl quadriert: "
              f"({k}…)² = {k*k}…, nicht {k}…"),
            F("hochzahl_nicht_verdoppelt", M(k * k - m + n, (z, g), (zwei, 1)),
              f"Beim Quadrieren werden die Hochzahlen verdoppelt: "
              f"({pot(z,g)})² = {pot(z,2*g)}."),
            F("zweite_variable_vergessen", M(wert, (z, 2 * g), (zwei, 1)),
              f"Auch {zwei} wird quadriert: ({zwei})² = {pot(zwei,2)}."),
            F("minus_uebersehen", M(k * k + m + n, (z, 2 * g), (zwei, 2)),
              "Das mittlere Glied wird ABGEZOGEN, nicht dazugezählt."),
            F("nur_quadriert", M(k * k, (z, 2 * g), (zwei, 2)),
              "Nach dem Quadrieren müssen die drei Glieder noch "
              "zusammengefasst werden."),
        ]
        schritte = [("Klammer quadrieren", f"({T(k,(z,g),(zwei,1))})² = {quad}"),
                    ("Zusammenfassen", f"{k*k} {MINUS} {m} + {n} = {wert}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    frage = reihe(f"({T(k,(z,g))})²", T(-m, (z, 2 * g)), T(n, (z, 2 * g))) \
        if p["glieder"] == 3 else reihe(f"({T(k,(z,g))})²", T(m, (z, 2 * g)))
    if p["glieder"] == 3:
        wert = k * k - m + n
    else:
        wert = k * k + m
    loesung = M(wert, (z, 2 * g))
    text = T(wert, (z, 2 * g))
    quad = T(k * k, (z, 2 * g))
    fehler = [
        F("koeffizient_nicht_quadriert",
          M(k - m + n if p["glieder"] == 3 else k + m, (z, 2 * g)),
          f"Beim Quadrieren wird AUCH die Zahl quadriert: "
          f"({k}…)² = {k*k}…, nicht {k}…"),
        F("hochzahl_nicht_verdoppelt", M(wert, (z, g)),
          f"Beim Quadrieren werden die Hochzahlen verdoppelt: "
          f"({pot(z,g)})² = {pot(z,2*g)}."),
        F("hochzahl_quadriert", M(wert, (z, g * g)) if g > 1 else
          M(wert, (z, 2 * g + 1)),
          f"Die Hochzahl wird VERDOPPELT, nicht quadriert: "
          f"({pot(z,g)})² = {pot(z,2*g)}."),
        F("nur_quadriert", M(k * k, (z, 2 * g)),
          "Nach dem Quadrieren müssen die Glieder noch zusammengefasst werden."),
        F("nur_zahl_quadriert", M(k * k, (z, g)),
          f"Quadriert wird die ganze Klammer, also Zahl UND Variable: "
          f"({T(k,(z,g))})² = {quad}."),
    ]
    schritte = [("Klammer quadrieren", f"({T(k,(z,g))})² = {quad}"),
                ("Zusammenfassen", f"alle Glieder haben {pot(z,2*g)}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF2 = Bauform("BF2", "Potenz ausrechnen und zusammenfassen",
              bereiche={
                  "A": {"k": [2, 3, 4, 5], "m": [2, 3, 4, 6], "n": [1],
                        "z": EINS, "g": [1], "glieder": [2], "z2": [None]},
                  "B": {"k": [2, 3, 4, 5], "m": [2, 3, 5, 7], "n": [2, 3, 4, 6],
                        "z": EINS, "g": [2], "glieder": [3], "z2": [None]},
                  "C": {"k": [2, 3, 4, 5], "m": [2, 3, 5, 7], "n": [2, 3, 4, 6],
                        "z": EINS, "g": [1, 2], "glieder": [3], "z2": ZWEI},
              }, bauen=bf2, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF3 · Klammer mal Zahl, dann zusammenfassen             K10 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf3(p):
    k, m, n, z, zwei = p["k"], p["m"], p["n"], p["z"], p.get("z2")
    vz = p["vz"]                    # +1 oder −1 vor der Klammer

    if zwei:
        # k a² − m a(a + n b)
        # NICHT ueber reihe(): die setzt selbst ein Pluszeichen zwischen die
        # Glieder, und das zweite Glied bringt hier schon eins mit. Ergebnis
        # war «3x + + 4 · (x + 2)» bzw. «6u −  4 · (u + 3)» mit doppeltem
        # Abstand. Rechnerisch harmlos, sieht aber nach Panne aus.
        zeichen = MINUS if vz < 0 else "+"
        frage = (f"{T(k, (z, 2))} {zeichen} {T(m,(z,1))} · "
                 f"({reihe(T(1,(z,1)), T(n,(zwei,1)))})")
        wert1 = k + vz * m
        loesung = M(wert1, (z, 2)) + M(vz * m * n, (z, 1), (zwei, 1))
        text = reihe(T(wert1, (z, 2)), T(vz * m * n, (z, 1), (zwei, 1)))
        fehler = [
            F("nur_erster_summand",
              M(k + vz * m, (z, 2)),
              f"Der Faktor {T(m,(z,1))} muss auf BEIDE Glieder der Klammer "
              f"verteilt werden, nicht nur auf das erste."),
            F("vorzeichen_nicht_verteilt",
              M(wert1, (z, 2)) + M(-vz * m * n, (z, 1), (zwei, 1)),
              "Das Vorzeichen vor der Klammer gilt für JEDES Glied darin."),
            F("sorten_vermischt",
              M(wert1 + vz * m * n, (z, 2)),
              f"{pot(z,2)} und {z}{zwei} sind verschiedene Sorten. Sie "
              f"können nicht zusammengezählt werden."),
            F("nicht_multipliziert",
              M(k, (z, 2)) + M(vz * m, (z, 1)) + M(vz * n, (zwei, 1)),
              "Die Klammer wurde weggelassen statt ausmultipliziert."),
            F("hochzahl_vergessen",
              M(wert1, (z, 1)) + M(vz * m * n, (z, 1), (zwei, 1)),
              f"{T(m,(z,1))} · {z} ergibt {pot(z,2)}, nicht {z}."),
        ]
        schritte = [("Ausmultiplizieren",
                     f"{T(m,(z,1))} · ({reihe(T(1,(z,1)), T(n,(zwei,1)))}) = "
                     f"{reihe(T(m,(z,2)), T(m*n,(z,1),(zwei,1)))}"),
                    ("Sorten ordnen", f"{pot(z,2)} zu {pot(z,2)}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    # k a  ±  m(a + n)
    zeichen = MINUS if vz < 0 else "+"
    frage = (f"{T(k, (z, 1))} {zeichen} {m} · "
             f"({reihe(T(1,(z,1)), T(n))})")
    wert1 = k + vz * m
    loesung = M(wert1, (z, 1)) + Integer(vz * m * n)
    text = reihe(T(wert1, (z, 1)), T(vz * m * n))
    fehler = [
        F("nur_erster_summand", M(wert1, (z, 1)),
          f"Die {m} muss auf BEIDE Glieder der Klammer verteilt werden: "
          f"auf {z} UND auf {n}."),
        F("vorzeichen_nicht_verteilt",
          M(wert1, (z, 1)) + Integer(-vz * m * n),
          "Das Vorzeichen vor der Klammer gilt für JEDES Glied darin."),
        F("sorten_vermischt", M(wert1 + vz * m * n, (z, 1)),
          f"{vz*m*n if vz*m*n>0 else -vz*m*n} ist eine blosse Zahl, "
          f"{z} eine Variable. Die beiden können nicht zusammengezählt werden."),
        F("nicht_multipliziert",
          M(k + vz, (z, 1)) + Integer(vz * n),
          "Die Klammer wurde weggelassen statt ausmultipliziert."),
        F("nur_zahl_multipliziert", M(k, (z, 1)) + Integer(vz * m * n),
          f"Auch das {z} in der Klammer wird mit {m} multipliziert."),
    ]
    schritte = [("Ausmultiplizieren",
                 f"{m} · ({reihe(T(1,(z,1)), T(n))}) = "
                 f"{reihe(T(m,(z,1)), T(m*n))}"),
                ("Gleichartiges zusammenfassen", f"{k} {'+' if vz>0 else MINUS} {m}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF3 = Bauform("BF3", "Klammer mal Zahl, dann zusammenfassen",
              bereiche={
                  "A": {"k": [2, 3, 5, 6, 7], "m": [2, 3, 4], "n": [2, 3, 4, 5],
                        "z": EINS, "vz": [1], "z2": [None]},
                  "B": {"k": [4, 5, 6, 7, 9], "m": [2, 3, 4], "n": [2, 3, 4, 5],
                        "z": EINS, "vz": [-1], "z2": [None]},
                  "C": {"k": [4, 5, 6, 7, 9], "m": [2, 3, 4], "n": [2, 3, 4, 5],
                        "z": EINS, "vz": [1, -1], "z2": ZWEI},
              }, bauen=bf3, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF4 · Division, dann zusammenfassen                     K9 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf4(p):
    m, q, n, z, zwei = p["m"], p["q"], p["n"], p["z"], p.get("z2")
    e = p["e"]                       # Hochzahl im Zähler
    k = m * q                        # damit die Division aufgeht

    if zwei:
        frage = reihe(f"{T(k,(z,e),(zwei,2))} : ({T(m,(z,1),(zwei,1))})",
                      T(-n, (z, e - 1), (zwei, 1)))
        loesung = M(q - n, (z, e - 1), (zwei, 1))
        text = T(q - n, (z, e - 1), (zwei, 1))
        teil = T(q, (z, e - 1), (zwei, 1))
        fehler = [
            F("nur_zahl_geteilt", M(k // m - n, (z, e), (zwei, 2)),
              f"Geteilt wird auch bei den Variablen: {pot(z,e)} : {z} = "
              f"{pot(z,e-1)}."),
            F("hochzahl_geteilt", M(q - n, (z, max(1, e // 2)), (zwei, 1)),
              f"Beim Dividieren werden die Hochzahlen SUBTRAHIERT, nicht "
              f"geteilt: {pot(z,e)} : {z} = {pot(z,e-1)}."),
            F("zweite_variable_vergessen", M(q - n, (z, e - 1), (zwei, 2)),
              f"Auch {zwei} wird geteilt: {pot(zwei,2)} : {zwei} = {zwei}."),
            F("nicht_zusammengefasst", M(q, (z, e - 1), (zwei, 1)),
              "Nach der Division steht noch ein zweites Glied da. Beide "
              "haben dieselbe Sorte und müssen verrechnet werden."),
            F("falsche_richtung", M(m - n, (z, e - 1), (zwei, 1)),
              f"Geteilt wird {k} durch {m}, also {k} : {m} = {q}."),
        ]
        schritte = [("Dividieren",
                     f"{T(k,(z,e),(zwei,2))} : ({T(m,(z,1),(zwei,1))}) = {teil}"),
                    ("Zusammenfassen", f"{teil} {MINUS} {T(n,(z,e-1),(zwei,1))}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    frage = reihe(f"{T(k,(z,e))} : ({T(m,(z,1))})", T(-n, (z, e - 1)))
    loesung = M(q - n, (z, e - 1))
    text = T(q - n, (z, e - 1))
    teil = T(q, (z, e - 1))
    fehler = [
        F("nur_zahl_geteilt", M(q - n, (z, e)),
          f"Geteilt wird auch bei den Variablen: {pot(z,e)} : {z} = "
          f"{pot(z,e-1)}."),
        F("hochzahl_geteilt", M(q - n, (z, max(1, e // 2))),
          f"Beim Dividieren werden die Hochzahlen SUBTRAHIERT, nicht "
          f"geteilt: {pot(z,e)} : {z} = {pot(z,e-1)}."),
        F("nicht_zusammengefasst", M(q, (z, e - 1)),
          "Nach der Division steht noch ein zweites Glied da. Beide haben "
          "dieselbe Sorte und müssen verrechnet werden."),
        F("falsche_richtung", M(m - n, (z, e - 1)),
          f"Geteilt wird {k} durch {m}, also {k} : {m} = {q}."),
        F("minus_uebersehen", M(q + n, (z, e - 1)),
          "Vor dem zweiten Glied steht ein Minus. Es wird abgezogen."),
    ]
    schritte = [("Dividieren", f"{T(k,(z,e))} : ({T(m,(z,1))}) = {teil}"),
                ("Zusammenfassen", f"{teil} {MINUS} {T(n,(z,e-1))}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF4 = Bauform("BF4", "Dividieren, dann zusammenfassen",
              bereiche={
                  "A": {"m": [2, 3, 4], "q": [3, 4, 5, 6], "n": [1, 2],
                        "z": EINS, "e": [2], "z2": [None]},
                  "B": {"m": [2, 3, 4, 5], "q": [3, 4, 5, 6, 7], "n": [2, 3, 4],
                        "z": EINS, "e": [3], "z2": [None]},
                  "C": {"m": [2, 3, 4, 5], "q": [3, 4, 5, 6, 7], "n": [2, 3, 4],
                        "z": EINS, "e": [3], "z2": ZWEI},
              }, bauen=bf4, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF5 · Wurzel und Potenzgesetz                           K8 · K7
# ══════════════════════════════════════════════════════════════════════════

def bf5(p):
    k, z, zwei, e, f = p["k"], p["z"], p.get("z2"), p["e"], p["f"]
    h = e // 2

    if zwei:
        rad = T(k * k, (z, e), (zwei, 2))
        frage = f"{W(rad)} · {T(1,(z,f),(zwei,2))}"
        loesung = M(k, (z, h + f), (zwei, 3))
        text = T(k, (z, h + f), (zwei, 3))
        wurzel_txt = T(k, (z, h), (zwei, 1))
        fehler = [
            F("hochzahl_nicht_halbiert", M(k, (z, e + f), (zwei, 3)),
              f"Beim Wurzelziehen wird die Hochzahl halbiert: "
              f"{pot(z,e)} wird zu {pot(z,h)}."),
            F("hochzahl_multipliziert", M(k, (z, h * f), (zwei, 2)),
              f"Beim Multiplizieren werden die Hochzahlen ADDIERT: "
              f"{pot(z,h)} · {pot(z,f)} = {pot(z,h+f)}."),
            F("wurzel_nicht_gezogen", M(k * k, (z, h + f), (zwei, 3)),
              f"Aus {k*k} unter der Wurzel wird {k}, nicht {k*k}."),
            F("zweite_variable_vergessen", M(k, (z, h + f), (zwei, 2)),
              f"Auch {pot(zwei,2)} steht unter der Wurzel: daraus wird {zwei}."),
            F("nur_wurzel", M(k, (z, h), (zwei, 1)),
              "Nach dem Wurzelziehen muss noch multipliziert werden."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                    ("Hochzahlen addieren",
                     f"{pot(z,h)} · {pot(z,f)} = {pot(z,h+f)}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = f"{W(rad)} · {T(1,(z,f))}"
    loesung = M(k, (z, h + f))
    text = T(k, (z, h + f))
    wurzel_txt = T(k, (z, h))
    fehler = [
        F("hochzahl_nicht_halbiert", M(k, (z, e + f)),
          f"Beim Wurzelziehen wird die Hochzahl halbiert: {pot(z,e)} wird "
          f"zu {pot(z,h)}."),
        F("hochzahl_multipliziert", M(k, (z, h * f)),
          f"Beim Multiplizieren werden die Hochzahlen ADDIERT: "
          f"{pot(z,h)} · {pot(z,f)} = {pot(z,h+f)}."),
        F("wurzel_nicht_gezogen", M(k * k, (z, h + f)),
          f"Aus {k*k} unter der Wurzel wird {k}, nicht {k*k}."),
        F("nur_wurzel", M(k, (z, h)),
          "Nach dem Wurzelziehen muss noch multipliziert werden."),
        F("koeffizient_halbiert", M(Rational(k * k, 2), (z, h + f)),
          f"Die Wurzel halbiert nicht: √{k*k} = {k}, weil {k} · {k} = {k*k}."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                ("Hochzahlen addieren", f"{pot(z,h)} · {pot(z,f)} = {pot(z,h+f)}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF5 = Bauform("BF5", "Wurzel ziehen und Potenzgesetz anwenden",
              bereiche={
                  "A": {"k": [2, 3, 4, 5, 6], "z": EINS, "e": [2], "f": [2],
                        "z2": [None]},
                  "B": {"k": [2, 3, 4, 5, 6], "z": EINS, "e": [4], "f": [2, 3],
                        "z2": [None]},
                  "C": {"k": [2, 3, 4, 5, 6], "z": EINS, "e": [4], "f": [1, 2],
                        "z2": ZWEI},
              }, bauen=bf5, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF6 · Produkt zweier Monome minus Monom                 K5 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf6(p):
    k, m, n, z, zwei = p["k"], p["m"], p["n"], p["z"], p.get("z2")
    e1, e2 = p["e1"], p["e2"]
    e = e1 + e2

    if zwei:
        frage = reihe(f"{T(k,(z,e1),(zwei,1))} · {T(m,(z,e2),(zwei,1))}",
                      T(-n, (z, e), (zwei, 2)))
        loesung = M(k * m - n, (z, e), (zwei, 2))
        text = T(k * m - n, (z, e), (zwei, 2))
        prod = T(k * m, (z, e), (zwei, 2))
        fehler = [
            F("hochzahlen_multipliziert", M(k * m - n, (z, e1 * e2), (zwei, 2))
              if e1 * e2 != e else M(k * m - n, (z, e + 1), (zwei, 2)),
              f"Beim Multiplizieren werden die Hochzahlen ADDIERT: "
              f"{pot(z,e1)} · {pot(z,e2)} = {pot(z,e)}."),
            F("koeffizient_addiert", M(k + m - n, (z, e), (zwei, 2)),
              f"{k} und {m} werden multipliziert: {k} · {m} = {k*m}."),
            F("zweite_variable_vergessen", M(k * m - n, (z, e), (zwei, 1)),
              f"{zwei} · {zwei} = {pot(zwei,2)} — die zweite Variable kommt "
              f"in beiden Faktoren vor."),
            F("nicht_zusammengefasst", M(k * m, (z, e), (zwei, 2)),
              "Das dritte Glied wurde weggelassen."),
            F("minus_uebersehen", M(k * m + n, (z, e), (zwei, 2)),
              "Vor dem letzten Glied steht ein Minus."),
        ]
        schritte = [("Multiplizieren",
                     f"{T(k,(z,e1),(zwei,1))} · {T(m,(z,e2),(zwei,1))} = {prod}"),
                    ("Zusammenfassen", f"{prod} {MINUS} {T(n,(z,e),(zwei,2))}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    frage = reihe(f"{T(k,(z,e1))} · {T(m,(z,e2))}", T(-n, (z, e)))
    loesung = M(k * m - n, (z, e))
    text = T(k * m - n, (z, e))
    prod = T(k * m, (z, e))
    fehler = [
        F("hochzahlen_multipliziert",
          M(k * m - n, (z, e1 * e2)) if e1 * e2 != e else M(k * m - n, (z, e + 1)),
          f"Beim Multiplizieren werden die Hochzahlen ADDIERT: "
          f"{pot(z,e1)} · {pot(z,e2)} = {pot(z,e)}."),
        F("koeffizient_addiert", M(k + m - n, (z, e)),
          f"{k} und {m} werden multipliziert: {k} · {m} = {k*m}."),
        F("nicht_zusammengefasst", M(k * m, (z, e)),
          "Das dritte Glied wurde weggelassen."),
        F("minus_uebersehen", M(k * m + n, (z, e)),
          "Vor dem letzten Glied steht ein Minus."),
        F("sorten_vermischt", M(k * m - n, (z, e1)),
          f"Das Produkt hat die Hochzahl {e}, nicht {e1}."),
    ]
    schritte = [("Multiplizieren", f"{T(k,(z,e1))} · {T(m,(z,e2))} = {prod}"),
                ("Zusammenfassen", f"{prod} {MINUS} {T(n,(z,e))}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF6 = Bauform("BF6", "Zwei Monome multiplizieren, dann abziehen",
              bereiche={
                  "A": {"k": [2, 3, 4, 5], "m": [2, 3, 4], "n": [1, 2, 3, 5],
                        "z": EINS, "e1": [1], "e2": [1], "z2": [None]},
                  "B": {"k": [2, 3, 4, 5], "m": [2, 3, 4], "n": [2, 3, 5, 7],
                        "z": EINS, "e1": [2], "e2": [1, 2], "z2": [None]},
                  "C": {"k": [2, 3, 4, 5], "m": [2, 3, 4], "n": [2, 3, 5, 7],
                        "z": EINS, "e1": [2], "e2": [1, 2], "z2": ZWEI},
              }, bauen=bf6, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF7 · Minus vor der Klammer                             K10 · K4
# 10.6 ist das häufigste Rücksprungziel im ganzen Netz.
# ══════════════════════════════════════════════════════════════════════════

def bf7(p):
    k, m, n, z, zwei = p["k"], p["m"], p["n"], p["z"], p.get("z2")
    vz = p["vz"]                     # Vorzeichen des zweiten Glieds IN der Klammer
    e = p["e"]

    if zwei:
        frage = (f"{T(k,(z,e),(zwei,1))} {MINUS} "
                 f"({reihe(T(m,(z,e),(zwei,1)), T(vz*n,(z,e),(zwei,1)))})")
        wert = k - m - vz * n
        loesung = M(wert, (z, e), (zwei, 1))
        text = T(wert, (z, e), (zwei, 1))
        fehler = [
            F("nur_erstes_umgedreht", M(k - m + vz * n, (z, e), (zwei, 1)),
              "Das Minus vor der Klammer dreht das Vorzeichen von JEDEM "
              "Glied in der Klammer um, nicht nur vom ersten."),
            F("klammer_ignoriert", M(k + m + vz * n, (z, e), (zwei, 1)),
              "Vor der Klammer steht ein Minus. Alles darin wird abgezogen."),
            F("nur_klammer", M(-m - vz * n, (z, e), (zwei, 1)),
              "Das erste Glied ausserhalb der Klammer gehört zum Ergebnis."),
            F("zweite_variable_verloren", M(wert, (z, e)),
              f"Alle Glieder haben {zwei}. Es bleibt im Ergebnis stehen."),
            F("hochzahl_addiert", M(wert, (z, e + 1), (zwei, 1)),
              "Beim Zusammenfassen ändert sich die Hochzahl nicht — es "
              "werden nur die Zahlen davor verrechnet."),
        ]
        schritte = [("Klammer auflösen",
                     f"{MINUS}({reihe(T(m,(z,e),(zwei,1)), T(vz*n,(z,e),(zwei,1)))}) = "
                     f"{reihe(T(-m,(z,e),(zwei,1)), T(-vz*n,(z,e),(zwei,1)))}"),
                    ("Zusammenfassen", f"{k} {MINUS} {m} "
                                       f"{MINUS if vz>0 else '+'} {n} = {wert}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    frage = (f"{T(k,(z,e))} {MINUS} "
             f"({reihe(T(m,(z,e)), T(vz*n,(z,e)))})")
    wert = k - m - vz * n
    loesung = M(wert, (z, e))
    text = T(wert, (z, e))
    fehler = [
        F("nur_erstes_umgedreht", M(k - m + vz * n, (z, e)),
          "Das Minus vor der Klammer dreht das Vorzeichen von JEDEM Glied "
          "in der Klammer um, nicht nur vom ersten."),
        F("klammer_ignoriert", M(k + m + vz * n, (z, e)),
          "Vor der Klammer steht ein Minus. Alles darin wird abgezogen."),
        F("nur_klammer", M(-m - vz * n, (z, e)),
          "Das erste Glied ausserhalb der Klammer gehört zum Ergebnis."),
        F("hochzahl_addiert", M(wert, (z, e + 1)),
          "Beim Zusammenfassen ändert sich die Hochzahl nicht — es werden "
          "nur die Zahlen davor verrechnet."),
        F("alles_addiert", M(k + m + vz * n, (z, e + 1)),
          "Zwei Fehler auf einmal: das Minus vor der Klammer und die "
          "Hochzahl. Die Hochzahl bleibt, die Vorzeichen drehen."),
    ]
    schritte = [("Klammer auflösen",
                 f"{MINUS}({reihe(T(m,(z,e)), T(vz*n,(z,e)))}) = "
                 f"{reihe(T(-m,(z,e)), T(-vz*n,(z,e)))}"),
                ("Zusammenfassen",
                 f"{k} {MINUS} {m} {MINUS if vz>0 else '+'} {n} = {wert}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF7 = Bauform("BF7", "Minus vor der Klammer, dann zusammenfassen",
              bereiche={
                  "A": {"k": [8, 9, 10, 12], "m": [2, 3, 4], "n": [1, 2, 3],
                        "z": EINS, "vz": [1], "e": [2], "z2": [None]},
                  "B": {"k": [7, 8, 9, 11, 12], "m": [2, 3, 4, 5], "n": [2, 3, 4],
                        "z": EINS, "vz": [-1], "e": [2, 3], "z2": [None]},
                  "C": {"k": [7, 8, 9, 11, 12], "m": [2, 3, 4, 5], "n": [2, 3, 4],
                        "z": EINS, "vz": [1, -1], "e": [2, 3], "z2": ZWEI},
              }, bauen=bf7, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF8 · Division mit Wurzel                               K8 · K9
# ══════════════════════════════════════════════════════════════════════════

def bf8(p):
    m, q, z, zwei, e = p["m"], p["q"], p["z"], p.get("z2"), p["e"]
    k = m * q                        # damit die Division aufgeht
    h = e // 2

    if zwei:
        rad = T(k * k, (z, e), (zwei, 2))
        frage = f"{W(rad)} : ({T(m,(z,1),(zwei,1))})"
        loesung = M(q, (z, h - 1), (zwei, 0))
        text = T(q, (z, h - 1))
        wurzel_txt = T(k, (z, h), (zwei, 1))
        fehler = [
            F("wurzel_nicht_gezogen", M(k * k // m, (z, e - 1), (zwei, 1)),
              f"Zuerst die Wurzel: {W(rad)} = {wurzel_txt}."),
            F("hochzahl_nicht_halbiert", M(q, (z, e - 1)),
              f"Beim Wurzelziehen wird die Hochzahl halbiert: {pot(z,e)} "
              f"wird zu {pot(z,h)}."),
            F("variable_geblieben", M(q, (z, h - 1), (zwei, 1)),
              f"{zwei} : {zwei} = 1 — die Variable kürzt sich ganz weg."),
            F("nur_zahl_geteilt", M(q, (z, h), (zwei, 1)),
              f"Geteilt wird auch bei den Variablen: {pot(z,h)} : {z} = "
              f"{pot(z,h-1)}."),
            F("falsche_richtung", M(m, (z, h - 1)),
              f"Geteilt wird {k} durch {m}: {k} : {m} = {q}."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                    ("Dividieren", f"{wurzel_txt} : ({T(m,(z,1),(zwei,1))}) = {text}"),
                    ("Ergebnis", text)]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = f"{W(rad)} : ({T(m,(z,1))})"
    loesung = M(q, (z, h - 1))
    text = T(q, (z, h - 1))
    wurzel_txt = T(k, (z, h))
    fehler = [
        F("wurzel_nicht_gezogen", M(k * k // m, (z, e - 1)),
          f"Zuerst die Wurzel: {W(rad)} = {wurzel_txt}."),
        F("hochzahl_nicht_halbiert", M(q, (z, e - 1)),
          f"Beim Wurzelziehen wird die Hochzahl halbiert: {pot(z,e)} wird "
          f"zu {pot(z,h)}."),
        F("nur_zahl_geteilt", M(q, (z, h)),
          f"Geteilt wird auch bei den Variablen: {pot(z,h)} : {z} = "
          f"{pot(z,h-1)}."),
        F("falsche_richtung", M(m, (z, h - 1)),
          f"Geteilt wird {k} durch {m}: {k} : {m} = {q}."),
        F("koeffizient_halbiert", M(Rational(k * k, 2 * m), (z, h - 1)),
          f"Die Wurzel halbiert nicht: √{k*k} = {k}."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                ("Dividieren", f"{wurzel_txt} : ({T(m,(z,1))}) = {text}"),
                ("Ergebnis", text)]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF8 = Bauform("BF8", "Wurzel ziehen und dividieren",
              bereiche={
                  "A": {"m": [2, 3, 4], "q": [2, 3, 4, 5], "z": EINS, "e": [2],
                        "z2": [None]},
                  "B": {"m": [2, 3, 4, 5], "q": [2, 3, 4, 6], "z": EINS, "e": [4],
                        "z2": [None]},
                  "C": {"m": [2, 3, 4, 5], "q": [2, 3, 4, 6], "z": EINS, "e": [4],
                        "z2": ZWEI},
              }, bauen=bf8, filter=STD)


# ══════════════════════════════════════════════════════════════════════════
# BF9 · Sonderfall · das Ergebnis ist null                K8 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf9(p):
    k, z, zwei, e = p["k"], p["z"], p.get("z2"), p["e"]
    h = e // 2

    if zwei:
        rad = T(k * k, (z, e), (zwei, 2))
        frage = reihe(W(rad), T(-k, (z, h), (zwei, 1)))
        wurzel_txt = T(k, (z, h), (zwei, 1))
        fehler = [
            F("wurzel_nicht_gezogen", M(k * k, (z, e), (zwei, 2)) -
              M(k, (z, h), (zwei, 1)),
              f"Zuerst die Wurzel ziehen: {W(rad)} = {wurzel_txt}. Danach "
              f"steht zweimal dasselbe da."),
            F("hochzahl_nicht_halbiert", M(k, (z, e), (zwei, 2)) -
              M(k, (z, h), (zwei, 1)),
              f"Die Hochzahl wird halbiert: {pot(z,e)} wird zu {pot(z,h)}."),
            F("zusammengezaehlt", M(2 * k, (z, h), (zwei, 1)),
              "Zwischen den beiden Gliedern steht ein Minus. Gleiches minus "
              "Gleiches ergibt null."),
            F("koeffizient_stehen", M(k, (z, h), (zwei, 1)),
              f"Beide Glieder sind gleich gross. {k} {MINUS} {k} = 0, "
              f"und damit ist das ganze Ergebnis 0."),
            F("nur_wurzel", M(k, (z, h), (zwei, 1)) * 1,
              "Das zweite Glied wurde weggelassen."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                    ("Vergleichen", f"{wurzel_txt} {MINUS} {wurzel_txt}"),
                    ("Ergebnis", "0")]
        return bau(frage, Integer(0), "0", fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = reihe(W(rad), T(-k, (z, h)))
    wurzel_txt = T(k, (z, h))
    fehler = [
        F("wurzel_nicht_gezogen", M(k * k, (z, e)) - M(k, (z, h)),
          f"Zuerst die Wurzel ziehen: {W(rad)} = {wurzel_txt}. Danach steht "
          f"zweimal dasselbe da."),
        F("hochzahl_nicht_halbiert", M(k, (z, e)) - M(k, (z, h)),
          f"Die Hochzahl wird halbiert: {pot(z,e)} wird zu {pot(z,h)}."),
        F("zusammengezaehlt", M(2 * k, (z, h)),
          "Zwischen den beiden Gliedern steht ein Minus. Gleiches minus "
          "Gleiches ergibt null."),
        F("koeffizient_stehen", M(k, (z, h)),
          f"Beide Glieder sind gleich gross: {k} {MINUS} {k} = 0."),
        F("nur_variable", SYM[z] ** h,
          "Auch die Variablen heben sich auf. Es bleibt nichts stehen, "
          "das Ergebnis ist 0."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {wurzel_txt}"),
                ("Vergleichen", f"{wurzel_txt} {MINUS} {wurzel_txt}"),
                ("Ergebnis", "0")]
    return bau(frage, Integer(0), "0", fehler, schritte, TIPPS)


BF9 = Bauform("BF9", "Sonderfall · das Ergebnis ist null",
              bereiche={
                  "A": {"k": [2, 3, 4, 5, 6, 7], "z": EINS, "e": [2], "z2": [None]},
                  "B": {"k": [2, 3, 4, 5, 6, 7], "z": EINS, "e": [4], "z2": [None]},
                  "C": {"k": [2, 3, 4, 5, 6, 7], "z": EINS, "e": [4], "z2": ZWEI},
              }, bauen=bf9, filter=[kopfrechenbar, fehler_eindeutig, genug_fehler,
                      kein_null_glied])


# ══════════════════════════════════════════════════════════════════════════
# BF10 · Sonderfall · vor dem Ergebnis steht keine Zahl   K8 · K5 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf10(p):
    k, z, zwei, e = p["k"], p["z"], p.get("z2"), p["e"]
    h = e // 2

    if zwei:
        rad = T(k * k, (z, e), (zwei, 2))
        frage = reihe(f"{W(rad)} · {T(1,(z,1))}",
                      T(-(k - 1), (z, h + 1), (zwei, 1)))
        loesung = M(1, (z, h + 1), (zwei, 1))
        text = T(1, (z, h + 1), (zwei, 1))
        fehler = [
            F("eins_geschrieben", M(1, (z, h + 1), (zwei, 1)) * 1 + Integer(0),
              ""),   # wird von bau() aussortiert (wertgleich) — Platzhalter
            F("koeffizient_falsch", M(k, (z, h + 1), (zwei, 1)),
              f"{k} {MINUS} {k-1} = 1. Vor der Variablen steht dann keine "
              f"Zahl mehr."),
            F("nicht_zusammengefasst", M(k, (z, h + 1), (zwei, 1)) -
              M(k - 1, (z, h + 1), (zwei, 1)) + M(1, (z, h)),
              "Beide Glieder haben dieselbe Sorte und müssen verrechnet "
              "werden."),
            F("hochzahl_nicht_halbiert", M(k * k - (k - 1), (z, e + 1), (zwei, 1)),
              f"Beim Wurzelziehen wird die Hochzahl halbiert: {pot(z,e)} "
              f"wird zu {pot(z,h)}."),
            F("wurzel_nicht_gezogen", M(k * k - (k - 1), (z, h + 1), (zwei, 1)),
              f"√{k*k} = {k}, nicht {k*k}."),
            F("null_geschrieben", Integer(0),
              f"{k} {MINUS} {k-1} ist 1, nicht 0. Es bleibt genau eine "
              f"Einheit übrig."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {T(k,(z,h),(zwei,1))}"),
                    ("Multiplizieren", f"= {T(k,(z,h+1),(zwei,1))}"),
                    ("Zusammenfassen", f"{k} {MINUS} {k-1} = 1, also {text}")]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = reihe(f"{W(rad)} · {T(1,(z,1))}", T(-(k - 1), (z, h + 1)))
    loesung = M(1, (z, h + 1))
    text = T(1, (z, h + 1))
    fehler = [
        F("koeffizient_falsch", M(k, (z, h + 1)),
          f"{k} {MINUS} {k-1} = 1. Vor der Variablen steht dann keine Zahl mehr."),
        F("null_geschrieben", Integer(0),
          f"{k} {MINUS} {k-1} ist 1, nicht 0. Es bleibt genau eine Einheit übrig."),
        F("hochzahl_nicht_halbiert", M(k * k - (k - 1), (z, e + 1)),
          f"Beim Wurzelziehen wird die Hochzahl halbiert: {pot(z,e)} wird "
          f"zu {pot(z,h)}."),
        F("wurzel_nicht_gezogen", M(k * k - (k - 1), (z, h + 1)),
          f"√{k*k} = {k}, nicht {k*k}."),
        F("nicht_multipliziert", M(k - (k - 1), (z, h)) if h != h + 1 else
          M(1, (z, h)),
          f"Nach der Wurzel steht noch «· {z}». Die Hochzahl steigt dadurch "
          f"um eins."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {T(k,(z,h))}"),
                ("Multiplizieren", f"= {T(k,(z,h+1))}"),
                ("Zusammenfassen", f"{k} {MINUS} {k-1} = 1, also {text}")]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF10 = Bauform("BF10", "Sonderfall · vor dem Ergebnis steht keine Zahl",
               bereiche={
                   "A": {"k": [3, 4, 5, 6, 7], "z": EINS, "e": [2], "z2": [None]},
                   "B": {"k": [3, 4, 5, 6, 7], "z": EINS, "e": [4], "z2": [None]},
                   "C": {"k": [3, 4, 5, 6, 7], "z": EINS, "e": [4], "z2": ZWEI},
               }, bauen=bf10, filter=[kopfrechenbar, fehler_eindeutig, genug_fehler,
                      kein_null_glied])


# ══════════════════════════════════════════════════════════════════════════
# BF11 · Sonderfall · es lässt sich nichts zusammenfassen  K7 · K4
# ══════════════════════════════════════════════════════════════════════════

def bf11(p):
    k, m, z, zwei, e = p["k"], p["m"], p["z"], p.get("z2"), p["e"]
    h = e // 2

    if zwei:
        rad = T(k * k, (z, e), (zwei, 2))
        frage = reihe(W(rad), T(m, (z, h), (zwei, 2)))
        loesung = M(k, (z, h), (zwei, 1)) + M(m, (z, h), (zwei, 2))
        text = reihe(T(k, (z, h), (zwei, 1)), T(m, (z, h), (zwei, 2)))
        fehler = [
            F("zusammengezaehlt", M(k + m, (z, h), (zwei, 1)),
              f"{T(k,(z,h),(zwei,1))} und {T(m,(z,h),(zwei,2))} sind "
              f"VERSCHIEDENE Sorten — einmal {zwei}, einmal {pot(zwei,2)}. "
              f"Sie bleiben nebeneinander stehen."),
            F("wurzel_nicht_gezogen", M(k * k, (z, e), (zwei, 2)) +
              M(m, (z, h), (zwei, 2)),
              f"Die Wurzel muss gezogen werden: {W(rad)} = "
              f"{T(k,(z,h),(zwei,1))}."),
            F("hochzahl_nicht_halbiert", M(k, (z, e), (zwei, 2)) +
              M(m, (z, h), (zwei, 2)),
              f"Beim Wurzelziehen wird die Hochzahl halbiert."),
            F("sorten_verschmolzen", M(k + m, (z, h), (zwei, 2)),
              "Zusammenfassen darf man nur, was dieselbe Variable mit "
              "derselben Hochzahl hat."),
            F("nur_erstes", M(k, (z, h), (zwei, 1)),
              "Das zweite Glied gehört zum Ergebnis, auch wenn es sich "
              "nicht zusammenfassen lässt."),
        ]
        schritte = [("Wurzel ziehen", f"{W(rad)} = {T(k,(z,h),(zwei,1))}"),
                    ("Sorten vergleichen",
                     f"{pot(z,h)}{zwei} und {pot(z,h)}{pot(zwei,2)} — "
                     f"verschieden"),
                    ("Ergebnis", f"{text} — es lässt sich nichts zusammenfassen")]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    rad = T(k * k, (z, e))
    frage = reihe(W(rad), T(m, (z, h + 1)))
    loesung = M(k, (z, h)) + M(m, (z, h + 1))
    text = reihe(T(k, (z, h)), T(m, (z, h + 1)))
    fehler = [
        F("zusammengezaehlt", M(k + m, (z, h)),
          f"{pot(z,h)} und {pot(z,h+1)} sind VERSCHIEDENE Sorten. Sie "
          f"bleiben nebeneinander stehen."),
        F("zusammengezaehlt_hoch", M(k + m, (z, h + 1)),
          f"{pot(z,h)} und {pot(z,h+1)} haben verschiedene Hochzahlen und "
          f"können nicht verrechnet werden."),
        F("wurzel_nicht_gezogen", M(k * k, (z, e)) + M(m, (z, h + 1)),
          f"Die Wurzel muss gezogen werden: {W(rad)} = {T(k,(z,h))}."),
        F("hochzahl_nicht_halbiert", M(k, (z, e)) + M(m, (z, h + 1)),
          "Beim Wurzelziehen wird die Hochzahl halbiert."),
        F("nur_erstes", M(k, (z, h)),
          "Das zweite Glied gehört zum Ergebnis, auch wenn es sich nicht "
          "zusammenfassen lässt."),
    ]
    schritte = [("Wurzel ziehen", f"{W(rad)} = {T(k,(z,h))}"),
                ("Sorten vergleichen", f"{pot(z,h)} und {pot(z,h+1)} — verschieden"),
                ("Ergebnis", f"{text} — es lässt sich nichts zusammenfassen")]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF11 = Bauform("BF11", "Sonderfall · es lässt sich nichts zusammenfassen",
               bereiche={
                   "A": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4, 5], "z": EINS,
                         "e": [2], "z2": [None]},
                   "B": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4, 5], "z": EINS,
                         "e": [4], "z2": [None]},
                   "C": {"k": [2, 3, 4, 5, 6], "m": [2, 3, 4, 5], "z": EINS,
                         "e": [4], "z2": ZWEI},
               }, bauen=bf11, filter=[kopfrechenbar, fehler_eindeutig, genug_fehler,
                      kein_null_glied])


# ══════════════════════════════════════════════════════════════════════════
# BF12 · Division, Wurzel und Subtraktion                 K9 · K8 · K4
# Die schwerste Form: drei Kapitel, drei Glieder.
# ══════════════════════════════════════════════════════════════════════════

def bf12(p):
    m, q, n, r, z, zwei = p["m"], p["q"], p["n"], p["r"], p["z"], p.get("z2")
    e = p["e"]
    k = m * q
    h = e // 2

    if zwei:
        zaehler = T(k, (z, e), (zwei, 2))
        teiler = T(m, (z, 1), (zwei, 1))
        rad = T(n * n, (z, 2 * (e - 1)), (zwei, 2))
        frage = reihe(f"{zaehler} : ({teiler})",
                      W(rad),
                      T(-r, (z, e - 1), (zwei, 1)))
        wert = q + n - r
        loesung = M(wert, (z, e - 1), (zwei, 1))
        text = T(wert, (z, e - 1), (zwei, 1))
        fehler = [
            F("division_falsch", M(m + n - r, (z, e - 1), (zwei, 1)),
              f"{k} : {m} = {q}, nicht {m}."),
            F("wurzel_nicht_gezogen", M(q - r, (z, e - 1), (zwei, 1)) +
              M(n * n, (z, 2 * (e - 1)), (zwei, 2)),
              f"Auch die Wurzel muss gezogen werden: {W(rad)} = "
              f"{T(n,(z,e-1),(zwei,1))}."),
            F("hochzahl_geteilt", M(wert, (z, e)),
              f"Beim Dividieren werden die Hochzahlen subtrahiert: "
              f"{pot(z,e)} : {z} = {pot(z,e-1)}."),
            F("minus_uebersehen", M(q + n + r, (z, e - 1), (zwei, 1)),
              "Vor dem letzten Glied steht ein Minus."),
            F("nur_zwei_glieder", M(q + n, (z, e - 1), (zwei, 1)),
              "Alle drei Glieder gehören ins Ergebnis."),
        ]
        schritte = [("Dividieren", f"{zaehler} : ({teiler}) = "
                                   f"{T(q,(z,e-1),(zwei,1))}"),
                    ("Wurzel ziehen", f"{W(rad)} = {T(n,(z,e-1),(zwei,1))}"),
                    ("Zusammenfassen",
                     f"{q} + {n} {MINUS} {r} = {wert}, also {text}")]
        return bau(frage, loesung, text, fehler, schritte, TIPPS)

    zaehler = T(k, (z, e))
    teiler = T(m, (z, 1))
    rad = T(n * n, (z, 2 * (e - 1)))
    frage = reihe(f"{zaehler} : ({teiler})", W(rad), T(-r, (z, e - 1)))
    wert = q + n - r
    loesung = M(wert, (z, e - 1))
    text = T(wert, (z, e - 1))
    fehler = [
        F("division_falsch", M(m + n - r, (z, e - 1)),
          f"{k} : {m} = {q}, nicht {m}."),
        F("wurzel_nicht_gezogen", M(q - r, (z, e - 1)) + M(n * n, (z, 2 * (e - 1))),
          f"Auch die Wurzel muss gezogen werden: {W(rad)} = {T(n,(z,e-1))}."),
        F("hochzahl_geteilt", M(wert, (z, e)),
          f"Beim Dividieren werden die Hochzahlen subtrahiert: {pot(z,e)} : "
          f"{z} = {pot(z,e-1)}."),
        F("minus_uebersehen", M(q + n + r, (z, e - 1)),
          "Vor dem letzten Glied steht ein Minus."),
        F("nur_zwei_glieder", M(q + n, (z, e - 1)),
          "Alle drei Glieder gehören ins Ergebnis."),
    ]
    schritte = [("Dividieren", f"{zaehler} : ({teiler}) = {T(q,(z,e-1))}"),
                ("Wurzel ziehen", f"{W(rad)} = {T(n,(z,e-1))}"),
                ("Zusammenfassen", f"{q} + {n} {MINUS} {r} = {wert}, also {text}")]
    return bau(frage, loesung, text, fehler, schritte, TIPPS)


BF12 = Bauform("BF12", "Dividieren, Wurzel ziehen und zusammenfassen",
               bereiche={
                   "A": {"m": [2, 3, 4], "q": [3, 4, 5], "n": [2, 3, 4],
                         "r": [1, 2, 3], "z": EINS, "e": [2], "z2": [None]},
                   "B": {"m": [2, 3, 4, 5], "q": [3, 4, 5, 6], "n": [2, 3, 4, 5],
                         "r": [2, 3, 4], "z": EINS, "e": [3], "z2": [None]},
                   "C": {"m": [2, 3, 4, 5], "q": [3, 4, 5, 6], "n": [2, 3, 4, 5],
                         "r": [2, 3, 4], "z": EINS, "e": [3], "z2": ZWEI},
               }, bauen=bf12, filter=STD)


# ══════════════════════════════════════════════════════════════════════════

S60 = Schablone(
    nr="S60", titel="Mischaufgaben — mehrere Kapitel in einer Aufgabe",
    lektionen="16.1", erhebung="alle",
    anleitung="Rechne aus und fasse so weit wie möglich zusammen.",
    levelachse="Anzahl Teilschritte, Anzahl Glieder und Anzahl Variablen",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=(
        "In einer Mischaufgabe steckt mehr als eine Regel. Arbeite von innen "
        "nach aussen: zuerst Wurzeln und Potenzen, dann Klammern, dann Mal "
        "und Geteilt, und ganz zum Schluss Plus und Minus. Zusammenfassen "
        "darfst du nur Glieder derselben Sorte."),
)
