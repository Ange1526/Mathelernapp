# -*- coding: utf-8 -*-
"""
ABGELOEST. Diese Schablone haengt seit Runde K7 an keiner Lektion mehr —
S22 bis S25 in `s22_s23_potenzen.py` und `s24_s25_potenzgesetze.py` haben
Kapitel 7 uebernommen. Grund: die Levelachse war hier numerisch, A, B und C
hatten denselben Aufbau und nur groessere Zahlen.

Die Datei bleibt vorerst liegen, damit sich die alten Aufgaben mit den neuen
vergleichen lassen. Sie ist in `anbindung.py` und `netz.py` nicht mehr
eingetragen und wird von der App nicht mehr aufgerufen.

Potenzen       (Lektionen 7.1 – 7.11, Erhebung 3c und Vorstufe zu 3e, 2c)

    «Rechne aus.»  /  «Fasse zusammen.»
    2 · 4² − (−3) + 2³      x² · x³      −7²  gegen  (−7)²

7.10 ist eines der drei häufigen Rücksprungziele: vier Fehler aus zwei
Schablonen zeigen hierher, immer wenn jemand beim Dividieren oder Ausklammern
die Hochzahlen falsch behandelt.

Levelachse: Grösse der Exponenten und Anzahl Glieder.
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (exponent_hoechstens, fehler_eindeutig, kopfrechenbar,
                        loesung_nicht_null, parameter_verschieden,
                        symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, m, u, v, x, y, z = symbole("a b m u v x y z")
VARS = {"a", "b", "m", "u", "v", "x", "y", "z"}
VARIABLEN = [x, a, u, y, m]


def Zb(*w):
    return [Integer(i) if isinstance(i, int) else i for i in w]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def bau(frage, loesung, fehler, schritte, tipps, anleitung=None,
        zielform=Zielform.ZUSAMMENGEFASST, loesung_text=None):
    return {"frage": frage, "loesung_text": loesung_text or zeige(loesung),
            "anleitung": anleitung,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=zielform, fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


# Der Parser weist Exponenten ueber 10 ab. Ohne diesen Filter baut der
# Generator Aufgaben, die der Schueler gar nicht beantworten KANN.
STD = [kopfrechenbar, fehler_eindeutig, exponent_hoechstens(10)]

TIPPS_GESETZE = [
    "Beim Multiplizieren werden die Hochzahlen addiert, beim Dividieren "
    "subtrahiert, bei einer Potenz einer Potenz multipliziert.",
    "Schau zuerst, welche Rechenart da steht — die drei Gesetze sehen ähnlich "
    "aus und werden oft verwechselt.",
    "Beim Addieren passiert mit der Hochzahl gar nichts: x⁵ + x⁵ ist 2x⁵.",
]


# ── BF1 · Potenzen multiplizieren ──────────────────────────────────────────

def bf1(p):
    v, e1, e2 = p["var"], p["e1"], p["e2"]
    loesung = v ** (e1 + e2)
    frage = f"{zeige(v**e1)} · {zeige(v**e2)}"
    return bau(frage, loesung, [
        F("multipliziert", v ** (e1 * e2),
          f"Beim Multiplizieren werden die Hochzahlen ADDIERT: {e1} + {e2} = {e1+e2}."),
        F("gezaehlt", 2 * v ** e1,
          "Gezählt wird beim Addieren, nicht beim Multiplizieren."),
    ], schritte=[
        ("Rechenart bestimmen", "es wird multipliziert"),
        ("Hochzahlen addieren", f"{e1} + {e2} = {e1+e2}"),
        ("Ergebnis", zeige(loesung)),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.")


BF1 = Bauform("BF1", "Potenzen multiplizieren — Hochzahlen addieren",
    bereiche={"A": {"var": VARIABLEN, "e1": Zb(2,3), "e2": Zb(2,3)},
              "B": {"var": VARIABLEN, "e1": Zb(3,4), "e2": Zb(2,3)},
              "C": {"var": VARIABLEN, "e1": Zb(2,3,4), "e2": Zb(2,3)}},
    bauen=bf1, filter=STD)


# ── BF2 · Potenzen dividieren ──────────────────────────────────────────────

def bf2(p):
    v, e1, e2 = p["var"], p["e1"], p["e2"]
    loesung = v ** (e1 - e2)
    frage = f"{zeige(v**e1)} : {zeige(v**e2)}"
    return bau(frage, loesung, [
        F("addiert", v ** (e1 + e2),
          f"Beim Dividieren werden die Hochzahlen SUBTRAHIERT: {e1} {MINUS} {e2} = {e1-e2}."),
        F("geteilt", v ** max(1, e1 // e2),
          "Die Hochzahlen werden subtrahiert, nicht geteilt."),
    ], schritte=[
        ("Rechenart bestimmen", "es wird dividiert"),
        ("Hochzahlen subtrahieren", f"{e1} {MINUS} {e2} = {e1-e2}"),
        ("Ergebnis", zeige(loesung)),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.")


BF2 = Bauform("BF2", "Potenzen dividieren — Hochzahlen subtrahieren",
    bereiche={"A": {"var": VARIABLEN, "e1": Zb(4,5), "e2": Zb(2,3)},
              "B": {"var": VARIABLEN, "e1": Zb(6,7), "e2": Zb(2,3)},
              "C": {"var": VARIABLEN, "e1": Zb(7,8), "e2": Zb(2,3)}},
    bauen=bf2, filter=STD + [loesung_nicht_null])


# ── BF3 · Potenz einer Potenz ──────────────────────────────────────────────

def bf3(p):
    v, e1, e2 = p["var"], p["e1"], p["e2"]
    loesung = v ** (e1 * e2)
    from .anzeige import HOCH
    frage = f"({zeige(v**e1)}){HOCH.get(int(e2), f'^{e2}')}"
    return bau(frage, loesung, [
        F("addiert", v ** (e1 + e2),
          f"Bei einer Potenz einer Potenz werden die Hochzahlen MULTIPLIZIERT: "
          f"{e1} · {e2} = {e1*e2}."),
    ], schritte=[
        ("Rechenart bestimmen", "eine Potenz wird potenziert"),
        ("Hochzahlen multiplizieren", f"{e1} · {e2} = {e1*e2}"),
        ("Ergebnis", zeige(loesung)),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.")


BF3 = Bauform("BF3", "Potenz einer Potenz — Hochzahlen multiplizieren",
    bereiche={"A": {"var": VARIABLEN, "e1": Zb(2), "e2": Zb(2,3)},
              "B": {"var": VARIABLEN, "e1": Zb(2,3), "e2": Zb(2,3)},
              "C": {"var": VARIABLEN, "e1": Zb(3,4), "e2": Zb(2,3)}},
    bauen=bf3, filter=STD)


# ── BF4 · Potenzen addieren — die Hochzahl bleibt ──────────────────────────

def bf4(p):
    v, e1, k = p["var"], p["e1"], p["k"]
    loesung = (k + 1) * v ** e1
    frage = " + ".join([zeige(v**e1)] + [zeige(v**e1)] * k)
    return bau(frage, loesung, [
        F("hochzahlen_addiert", v ** (e1 * (k + 1)),
          f"Beim Addieren wird GEZÄHLT, nicht gerechnet: {k+1} Stück "
          f"{zeige(v**e1)} ergeben {zeige(loesung)}."),
        F("falsch_gezaehlt", k * v ** e1,
          f"Es sind {k+1} Glieder, nicht {k}."),
    ], schritte=[
        ("Rechenart bestimmen", "es wird addiert"),
        ("Zählen, wie viele gleiche Glieder da sind", f"{k+1} Stück"),
        ("Die Hochzahl bleibt unverändert", zeige(loesung)),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.")


BF4 = Bauform("BF4", "Potenzen addieren — die Hochzahl bleibt",
    bereiche={"A": {"var": VARIABLEN, "e1": Zb(2,3), "k": Zb(1,2)},
              "B": {"var": VARIABLEN, "e1": Zb(3,4,5), "k": Zb(2,3)},
              "C": {"var": VARIABLEN, "e1": Zb(2,3), "k": Zb(3,4)}},
    bauen=bf4, filter=STD)


# ── BF5 · Nichts lässt sich zusammenfassen ─────────────────────────────────

def bf5(p):
    v, e1, e2 = p["var"], p["e1"], p["e2"]
    loesung = v ** e1 + v ** e2
    frage = zeige_summe(v**e1, v**e2)
    return bau(frage, loesung, [
        F("zusammengezogen", v ** (e1 + e2),
          f"{zeige(v**e1)} und {zeige(v**e2)} sind verschiedene Sorten. "
          f"{frage} ist bereits die Antwort."),
        F("gezaehlt", 2 * v ** e1,
          "Gezählt wird nur bei GLEICHEN Potenzen."),
    ], schritte=[
        ("Sorten bestimmen",
         f"{zeige(v**e1)} und {zeige(v**e2)} — verschiedene Hochzahlen"),
        ("Zusammenfassen nur bei gleicher Hochzahl", "geht hier nicht"),
        ("Antwort", frage),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.", loesung_text=frage)


BF5 = Bauform("BF5", "Sonderfall: verschiedene Hochzahlen, nichts zu tun",
    bereiche={"A": {"var": VARIABLEN, "e1": Zb(2), "e2": Zb(3)},
              "B": {"var": VARIABLEN, "e1": Zb(2,3), "e2": Zb(4,5)},
              "C": {"var": VARIABLEN, "e1": Zb(3,4), "e2": Zb(5,6)}},
    bauen=bf5, filter=STD + [parameter_verschieden("e1", "e2")])


# ── BF6 · Zwei Variablen ───────────────────────────────────────────────────

def bf6(p):
    v1, v2, e1, e2, e3 = p["var"], p["var2"], p["e1"], p["e2"], p["e3"]
    loesung = v1 ** (e1 + e3) * v2 ** e2
    frage = f"{zeige(v1**e1 * v2**e2)} · {zeige(v1**e3)}"
    return bau(frage, loesung, [
        F("beide_addiert", v1 ** (e1 + e3) * v2 ** (e2 + e3),
          f"Nur beim {zeige(v1)} wird die Hochzahl erhöht — {zeige(v2)} kommt "
          f"im zweiten Faktor gar nicht vor."),
        F("multipliziert", v1 ** (e1 * e3) * v2 ** e2,
          f"Beim Multiplizieren werden die Hochzahlen addiert: {e1} + {e3} = {e1+e3}."),
    ], schritte=[
        ("Für jede Variable getrennt schauen",
         f"{zeige(v1)}: {e1} und {e3}   |   {zeige(v2)}: nur {e2}"),
        (f"Hochzahlen von {zeige(v1)} addieren", f"{e1} + {e3} = {e1+e3}"),
        ("Ergebnis", zeige(loesung)),
    ], tipps=TIPPS_GESETZE, anleitung="Fasse zusammen.")


BF6 = Bauform("BF6", "Zwei Variablen — jede für sich",
    bereiche={"A": {"var": VARIABLEN, "var2": VARIABLEN, "e1": Zb(2,3), "e2": Zb(2), "e3": Zb(2,3)},
              "B": {"var": VARIABLEN, "var2": VARIABLEN, "e1": Zb(2,3,4), "e2": Zb(2,3), "e3": Zb(2,3)},
              "C": {"var": VARIABLEN, "var2": VARIABLEN, "e1": Zb(3,4), "e2": Zb(2,4), "e3": Zb(2,3)}},
    bauen=bf6, filter=STD + [symbole_verschieden("var", "var2")])


# ── BF7 · Minus vor der Potenz gegen negative Basis  (Erhebung 3c) ─────────

def bf7(p):
    z1, e1, z2 = p["z1"], p["e1"], p["z2"]
    loesung = -(z1 ** e1) + z2
    from .anzeige import HOCH
    frage = f"{MINUS}{zeige(z1)}{HOCH[int(e1)]} + {z2}"
    return bau(frage, loesung, [
        F("basis_negativ", (-z1) ** e1 + z2,
          f"Ohne Klammer gilt die Potenz zuerst: {MINUS}{z1}² ist "
          f"{MINUS}({z1}²) = {-(z1**e1)}. Nur ({MINUS}{z1})² wäre positiv."),
    ], schritte=[
        ("Anschauen, wo das Minus steht", "vor der Potenz, nicht in einer Klammer"),
        ("Potenz zuerst", f"{z1}^{e1} = {z1**e1}"),
        ("Dann das Minus", f"{MINUS}{z1**e1} + {z2} = {loesung}"),
    ], tipps=[
        "Klammer vor Potenz vor Punkt vor Strich.",
        "Ein Minus ohne Klammer gehört NICHT zur Basis.",
        f"{MINUS}{z1}² bedeutet {MINUS}({z1}²), also {-(z1**e1)}.",
    ], anleitung="Rechne aus.", zielform=Zielform.BELIEBIG)


# Der Exponent muss GERADE sein. Bei einer ungeraden Hochzahl ist
# (−7)³ = −7³ — dann gibt es gar keinen Unterschied, und der Fehlerkatalog
# haette denselben Wert wie die Loesung. Der Testlauf hat das gefunden.
BF7 = Bauform("BF7", "Minus vor der Potenz — nicht in der Basis",
    bereiche={"A": {"z1": Zb(3,4,5), "e1": Zb(2), "z2": Zb(20,30,50)},
              "B": {"z1": Zb(5,6,7), "e1": Zb(2), "z2": Zb(50,60,80)},
              "C": {"z1": Zb(3,4,5), "e1": Zb(4), "z2": Zb(100,150,200)}},
    bauen=bf7, filter=STD)


# ── BF8 · Punkt vor Strich mit Potenzen  (Erhebung 3c) ────────────────────

def bf8(p):
    k, z1, e1, z2, e2 = p["k"], p["z1"], p["e1"], p["z2"], p["e2"]
    loesung = k * z1 ** e1 + z2 ** e2
    from .anzeige import HOCH as H
    frage = f"{k} · {z1}{H[int(e1)]} + {z2}{H[int(e2)]}"
    return bau(frage, loesung, [
        F("faktor_potenziert", (k * z1) ** e1 + z2 ** e2,
          f"Die Potenz gilt nur für die {z1}: {z1}^{e1} = {z1**e1}, dann "
          f"{k} · {z1**e1}."),
        F("von_links", (k * z1 ** e1 + z2) ** e2 if e2 == 2 and k * z1**e1 + z2 < 40
          else k * z1 ** e1 * z2 ** e2,
          "Potenz vor Punkt vor Strich — erst die Potenzen, dann das Mal, "
          "dann das Plus."),
    ], schritte=[
        ("Potenzen zuerst", f"{z1}^{e1} = {z1**e1}   und   {z2}^{e2} = {z2**e2}"),
        ("Dann Punkt", f"{k} · {z1**e1} = {k * z1**e1}"),
        ("Dann Strich", f"{k * z1**e1} + {z2**e2} = {loesung}"),
    ], tipps=[
        "Potenz vor Punkt vor Strich.",
        "Rechne zuerst alle Potenzen aus und schreib den Term neu hin.",
        f"{z1}^{e1} = {z1**e1} und {z2}^{e2} = {z2**e2}.",
    ], anleitung="Rechne aus.", zielform=Zielform.BELIEBIG)


BF8 = Bauform("BF8", "Potenz vor Punkt vor Strich",
    bereiche={"A": {"k": Zb(2,3), "z1": Zb(3,4), "e1": Zb(2), "z2": Zb(2,3), "e2": Zb(2)},
              "B": {"k": Zb(2,3,4), "z1": Zb(4,5), "e1": Zb(2), "z2": Zb(2,3), "e2": Zb(3)},
              "C": {"k": Zb(3,4,5), "z1": Zb(5,6), "e1": Zb(2), "z2": Zb(3,4), "e2": Zb(3)}},
    bauen=bf8, filter=STD)


S7 = Schablone(
    nr="S7", titel="Potenzen",
    lektionen="7.1 – 7.11", erhebung="3c · Vorstufe zu 3e und 2c",
    anleitung="Rechne aus.",
    levelachse="Grösse der Exponenten und Anzahl Glieder",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8],
    kernidee=("Beim Multiplizieren werden die Hochzahlen addiert, beim "
              "Dividieren subtrahiert, bei einer Potenz einer Potenz "
              "multipliziert — und beim Addieren bleibt die Hochzahl gleich."),
)
