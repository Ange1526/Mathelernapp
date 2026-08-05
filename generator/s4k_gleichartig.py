# -*- coding: utf-8 -*-
"""
Gleichartige Terme     (Lektionen 4.1 – 4.10, Erhebung 2a)

    «Fasse so weit wie möglich zusammen.»
    5a + 3b + 2a + 4b      3x + 4y      2ab + 3ba

4.8 ist eines der drei häufigen Rücksprungziele im Netz: fünf Fehler aus zwei
Schablonen zeigen hierher. Der Kern ist nicht das Rechnen, sondern das
Erkennen — welche Glieder gehören überhaupt zusammen.

Levelachse: Anzahl Glieder (A drei, B vier, C fünf bis sechs).
"""
from __future__ import annotations

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (STANDARD, alle_sorten_bleiben, fehler_eindeutig,
                        kopfrechenbar, loesung_nicht_null,
                        parameter_verschieden, symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Fasse so weit wie möglich zusammen."

S1 = [a, x, u, b, m]          # erste Variablensorte
S2 = [b, y, v, c, n]          # zweite


def Zb(*w_):
    return list(w_)


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def bau(frage, loesung, fehler, schritte, tipps, loesung_text=None, sorten=None):
    return {"frage": frage, "loesung_text": loesung_text or zeige(loesung),
            "sorten": sorten or [],
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=Zielform.ZUSAMMENGEFASST,
                               fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


TIPPS = [
    "Zusammenfassen darf man nur Glieder mit genau derselben Variablen. "
    "Reine Zahlen sind eine eigene Sorte.",
    "Schreib jedes Glied mit seinem Vorzeichen ab und sortiere danach.",
    "Rechne jede Sorte für sich zusammen — verschiedene Sorten bleiben "
    "nebeneinander stehen.",
]


# ── BF1 · Zwei Sorten, beide mehrfach ──────────────────────────────────────

def bf1(p):
    k1, k2, k3, k4, v1, v2 = p["k1"], p["k2"], p["k3"], p["k4"], p["var"], p["var2"]
    loesung = (k1 + k3) * v1 + (k2 + k4) * v2
    frage = zeige_summe(k1 * v1, k2 * v2, k3 * v1, k4 * v2)
    return bau(frage, loesung, [
        F("sorten_gemischt", (k1 + k2 + k3 + k4) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden und lassen sich nicht "
          f"zusammenzählen."),
        F("nur_erste_sorte", (k1 + k3) * v1 + k2 * v2,
          f"Auch die {zeige(v2)}-Glieder werden zusammengefasst."),
        F("vorzeichen", (k1 + k3) * v1 + (k2 - k4) * v2,
          "Beide Glieder dieser Sorte werden addiert."),
    ], schritte=[
        ("Alle Glieder mit ihrem Vorzeichen abschreiben", frage),
        ("Sorten bestimmen", f"{zeige(v1)}-Glieder und {zeige(v2)}-Glieder"),
        ("Jede Sorte für sich rechnen",
         f"{k1} + {k3} = {k1+k3}   und   {k2} + {k4} = {k2+k4}"),
        ("Zusammenschreiben", zeige_summe((k1+k3) * v1, (k2+k4) * v2)),
    ], tipps=TIPPS, loesung_text=zeige_summe((k1+k3) * v1, (k2+k4) * v2),
       sorten=[v1, v2])


BF1 = Bauform("BF1", "Zwei Sorten, beide kommen mehrfach vor",
    bereiche={"A": {"k1": Zb(2,3,5), "k2": Zb(2,3,4), "k3": Zb(1,2,3), "k4": Zb(2,4),
                    "var": S1, "var2": S2},
              "B": {"k1": Zb(4,5,7), "k2": Zb(3,4,6), "k3": Zb(2,3,5), "k4": Zb(3,5,7),
                    "var": S1, "var2": S2},
              "C": {"k1": Zb(6,8,11), "k2": Zb(5,7,9), "k3": Zb(4,6,7), "k4": Zb(4,6,8),
                    "var": S1, "var2": S2}},
    bauen=bf1, filter=STANDARD + [symbole_verschieden("var", "var2"),
                                  alle_sorten_bleiben])


# ── BF2 · Nichts lässt sich zusammenfassen ─────────────────────────────────

def bf2(p):
    k1, k2, v1, v2 = p["k1"], p["k2"], p["var"], p["var2"]
    loesung = k1 * v1 + k2 * v2
    frage = zeige_summe(k1 * v1, k2 * v2)
    return bau(frage, loesung, [
        F("zusammengezogen", (k1 + k2) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden. {frage} ist bereits "
          f"die Antwort."),
        F("nur_zahlen", (k1 + k2) * v1,
          "Verschiedene Variablen bleiben nebeneinander stehen."),
    ], schritte=[
        ("Sorten bestimmen", f"{zeige(v1)} und {zeige(v2)}"),
        ("Prüfen: gibt es von einer Sorte mehr als eines?", "nein"),
        ("Antwort", f"{frage} — hier ist nichts zusammenzufassen"),
    ], tipps=TIPPS, loesung_text=frage, sorten=[v1, v2])


BF2 = Bauform("BF2", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche={"A": {"k1": Zb(2,3,5), "k2": Zb(4,7), "var": S1, "var2": S2},
              "B": {"k1": Zb(4,6,9), "k2": Zb(5,8,11), "var": S1, "var2": S2},
              "C": {"k1": Zb(7,11,13), "k2": Zb(9,12,17), "var": S1, "var2": S2}},
    bauen=bf2, filter=STANDARD + [symbole_verschieden("var", "var2"),
                                  parameter_verschieden("k1", "k2")])


# ── BF3 · Zwei Sorten und Zahlen ───────────────────────────────────────────

def bf3(p):
    k1, k2, k3, zahl1, zahl2, v1, v2 = (p["k1"], p["k2"], p["k3"], p["zahl1"],
                                        p["zahl2"], p["var"], p["var2"])
    loesung = (k1 + k3) * v1 + k2 * v2 + (zahl1 - zahl2)
    frage = zeige_summe(k1 * v1, k2 * v2, zahl1, k3 * v1, -zahl2)
    return bau(frage, loesung, [
        F("zahl_zur_variablen", (k1 + k3 + zahl1 - zahl2) * v1 + k2 * v2,
          "Reine Zahlen sind eine eigene Sorte und gehören nicht zu den "
          f"{zeige(v1)}-Gliedern."),
        F("vorzeichen", (k1 + k3) * v1 + k2 * v2 + (zahl1 + zahl2),
          f"Die {zahl2} wird abgezogen, nicht addiert."),
    ], schritte=[
        ("Drei Sorten bestimmen",
         f"{zeige(v1)}, {zeige(v2)} und reine Zahlen"),
        ("Jede Sorte rechnen",
         f"{k1} + {k3} = {k1+k3}   |   {k2}   |   {zahl1} {MINUS} {zahl2} = {zahl1-zahl2}"),
        ("Zusammenschreiben",
         zeige_summe((k1+k3) * v1, k2 * v2, zahl1 - zahl2)),
    ], tipps=TIPPS,
       loesung_text=zeige_summe((k1+k3) * v1, k2 * v2, zahl1 - zahl2),
       sorten=[v1, v2])


BF3 = Bauform("BF3", "Zwei Sorten und reine Zahlen",
    bereiche={"A": {"k1": Zb(2,3), "k2": Zb(2,3), "k3": Zb(1,2), "zahl1": Zb(5,7,9),
                    "zahl2": Zb(2,3), "var": S1, "var2": S2},
              "B": {"k1": Zb(3,5), "k2": Zb(3,4), "k3": Zb(2,4), "zahl1": Zb(8,11,14),
                    "zahl2": Zb(3,5,6), "var": S1, "var2": S2},
              "C": {"k1": Zb(5,7), "k2": Zb(4,6), "k3": Zb(3,5), "zahl1": Zb(12,15,18),
                    "zahl2": Zb(4,7,9), "var": S1, "var2": S2}},
    bauen=bf3, filter=STANDARD + [symbole_verschieden("var", "var2"),
                                  alle_sorten_bleiben,
                                  parameter_verschieden("zahl1", "zahl2")])


# ── BF4 · Eine Sorte fällt ganz weg ────────────────────────────────────────

def bf4(p):
    k1, k2, v1, v2 = p["k1"], p["k2"], p["var"], p["var2"]
    loesung = k2 * v2
    frage = zeige_summe(k1 * v1, k2 * v2, -k1 * v1)
    return bau(frage, loesung, [
        F("sorte_geblieben", k1 * v1 + k2 * v2,
          f"Die {zeige(v1)}-Glieder heben sich auf: {k1} {MINUS} {k1} = 0."),
        F("alles_weg", k2 * 0,
          f"Nur die {zeige(v1)}-Glieder heben sich auf. Die "
          f"{zeige(k2 * v2)} bleiben stehen."),
    ], schritte=[
        ("Sorten bestimmen", f"{zeige(v1)} und {zeige(v2)}"),
        (f"Die {zeige(v1)}-Glieder rechnen", f"{k1} {MINUS} {k1} = 0"),
        ("Übrig bleibt nur eine Sorte", zeige(loesung)),
    ], tipps=TIPPS, sorten=[v2])


BF4 = Bauform("BF4", "Sonderfall: eine Sorte fällt ganz weg",
    bereiche={"A": {"k1": Zb(2,3,5), "k2": Zb(3,4,6), "var": S1, "var2": S2},
              "B": {"k1": Zb(4,6,7), "k2": Zb(5,7,9), "var": S1, "var2": S2},
              "C": {"k1": Zb(8,9,12), "k2": Zb(6,8,11), "var": S1, "var2": S2}},
    bauen=bf4, filter=[kopfrechenbar, fehler_eindeutig,
                       symbole_verschieden("var", "var2"),
                       parameter_verschieden("k1", "k2")])


# ── BF5 · Produkte als Sorte, Reihenfolge egal ─────────────────────────────

def bf5(p):
    k1, k2, k3, v1, v2 = p["k1"], p["k2"], p["k3"], p["var"], p["var2"]
    loesung = (k1 + k2 - k3) * v1 * v2
    frage = f"{zeige(k1*v1*v2)} + {k2}{zeige(v2)}{zeige(v1)} {MINUS} {zeige(k3*v1*v2)}"
    return bau(frage, loesung, [
        F("reihenfolge", (k1 - k3) * v1 * v2,
          f"{zeige(v1)}{zeige(v2)} und {zeige(v2)}{zeige(v1)} sind dasselbe — "
          f"die Reihenfolge der Faktoren spielt keine Rolle."),
        F("vorzeichen", (k1 + k2 + k3) * v1 * v2,
          f"Das letzte Glied wird abgezogen."),
    ], schritte=[
        ("Prüfen: sind es wirklich dieselben Faktoren?",
         f"{zeige(v1)}{zeige(v2)} und {zeige(v2)}{zeige(v1)} — ja"),
        ("Alle drei Glieder gehören zur selben Sorte",
         f"{k1} + {k2} {MINUS} {k3} = {k1+k2-k3}"),
        ("Ergebnis", zeige(loesung)),
    ], tipps=[
        "Zwei Produkte sind gleichartig, wenn sie dieselben Variablen haben — "
        "die Reihenfolge der Faktoren spielt keine Rolle.",
        "Schreib bei jedem Glied auf, welche Variablen vorkommen.",
        f"{zeige(v1)}{zeige(v2)} und {zeige(v2)}{zeige(v1)} sind dasselbe.",
    ], sorten=[v1, v2])


BF5 = Bauform("BF5", "Produkte — die Reihenfolge der Faktoren ist egal",
    bereiche={"A": {"k1": Zb(2,3), "k2": Zb(3,4), "k3": Zb(1,2), "var": S1, "var2": S2},
              "B": {"k1": Zb(4,5), "k2": Zb(5,6), "k3": Zb(2,3), "var": S1, "var2": S2},
              "C": {"k1": Zb(7,9), "k2": Zb(6,8), "k3": Zb(4,5), "var": S1, "var2": S2}},
    bauen=bf5, filter=STANDARD + [symbole_verschieden("var", "var2"),
                                  loesung_nicht_null])


# ── BF6 · Drei Sorten ──────────────────────────────────────────────────────

def bf6(p):
    k1, k2, k3, k4, v1, v2, v3 = (p["k1"], p["k2"], p["k3"], p["k4"],
                                  p["var"], p["var2"], p["var3"])
    loesung = (k1 + k4) * v1 + k2 * v2 + k3 * v3
    frage = zeige_summe(k1 * v1, k2 * v2, k3 * v3, k4 * v1)
    return bau(frage, loesung, [
        F("alles_zusammen", (k1 + k2 + k3 + k4) * v1,
          "Drei verschiedene Variablen — sie bleiben nebeneinander stehen."),
        F("nur_zwei_sorten", (k1 + k4) * v1 + (k2 + k3) * v2,
          f"{zeige(v2)} und {zeige(v3)} sind ebenfalls verschieden."),
    ], schritte=[
        ("Sorten bestimmen", f"{zeige(v1)}, {zeige(v2)}, {zeige(v3)}"),
        (f"Nur die {zeige(v1)}-Glieder kommen zweimal vor",
         f"{k1} + {k4} = {k1+k4}"),
        ("Zusammenschreiben",
         zeige_summe((k1+k4) * v1, k2 * v2, k3 * v3)),
    ], tipps=TIPPS,
       loesung_text=zeige_summe((k1+k4) * v1, k2 * v2, k3 * v3),
       sorten=[v1, v2, v3])


BF6 = Bauform("BF6", "Drei Sorten",
    bereiche={"B": {"k1": Zb(2,3,4), "k2": Zb(3,5), "k3": Zb(2,4), "k4": Zb(1,3),
                    "var": [a, x], "var2": [b, y], "var3": [c, z]},
              "C": {"k1": Zb(5,6,8), "k2": Zb(4,7), "k3": Zb(3,6), "k4": Zb(2,5),
                    "var": [a, x, u], "var2": [b, y, v], "var3": [c, z, w]}},
    bauen=bf6, filter=STANDARD + [symbole_verschieden("var", "var2", "var3"),
                                  alle_sorten_bleiben],
    levels=("B", "C"))


# ── BF7 · Ergebnis ist null ────────────────────────────────────────────────

def bf7(p):
    k1, k2, v1, v2 = p["k1"], p["k2"], p["var"], p["var2"]
    frage = zeige_summe(k1 * v1, k2 * v2, -k1 * v1, -k2 * v2)
    return bau(frage, k1 * 0, [
        F("nur_eine_sorte", k2 * v2,
          f"Auch die {zeige(v2)}-Glieder heben sich auf."),
        F("nicht_null", k1 * v1 + k2 * v2,
          "Beide Sorten heben sich vollständig auf — das Ergebnis ist 0."),
    ], schritte=[
        (f"Die {zeige(v1)}-Glieder", f"{k1} {MINUS} {k1} = 0"),
        (f"Die {zeige(v2)}-Glieder", f"{k2} {MINUS} {k2} = 0"),
        ("Ergebnis", "0"),
    ], tipps=TIPPS, loesung_text="0")


BF7 = Bauform("BF7", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"k1": Zb(2,3,5), "k2": Zb(3,4,6), "var": S1, "var2": S2},
              "B": {"k1": Zb(4,6,8), "k2": Zb(5,7,9), "var": S1, "var2": S2},
              "C": {"k1": Zb(9,11,13), "k2": Zb(8,12,14), "var": S1, "var2": S2}},
    bauen=bf7, filter=[kopfrechenbar, fehler_eindeutig,
                       symbole_verschieden("var", "var2"),
                       parameter_verschieden("k1", "k2")])


# ── BF8 · Koeffizient wird eins ────────────────────────────────────────────

def bf8(p):
    # k1 wird aus k2 abgeleitet, damit die Differenz WIRKLICH eins ist.
    # Frei gewuerfelt entstand sonst 6u + 5c − 8u = −2u + 5c — eine Aufgabe,
    # die nichts mit dem Sonderfall zu tun hat.
    k2, k3, v1, v2 = p["k2"], p["k3"], p["var"], p["var2"]
    k1 = k2 + 1
    loesung = v1 + k3 * v2
    frage = zeige_summe(k1 * v1, k3 * v2, -k2 * v1)
    return bau(frage, loesung, [
        F("null_statt_eins", k3 * v2,
          f"{k1} {MINUS} {k2} = 1, nicht 0. Es bleibt ein {zeige(v1)} übrig."),
        F("eins_geschrieben", 2 * v1 + k3 * v2,
          f"{k1} {MINUS} {k2} = 1. Geschrieben wird das als {zeige(v1)}."),
    ], schritte=[
        (f"Die {zeige(v1)}-Glieder", f"{k1} {MINUS} {k2} = 1"),
        ("Koeffizient 1 wird nicht geschrieben", f"1{zeige(v1)} = {zeige(v1)}"),
        ("Zusammenschreiben", zeige_summe(v1, k3 * v2)),
    ], tipps=TIPPS, loesung_text=zeige_summe(v1, k3 * v2), sorten=[v1, v2])


BF8 = Bauform("BF8", "Sonderfall: der Koeffizient wird eins",
    bereiche={"A": {"k2": Zb(2,3,4), "k3": Zb(2,3), "var": S1, "var2": S2},
              "B": {"k2": Zb(5,7,8), "k3": Zb(3,5), "var": S1, "var2": S2},
              "C": {"k2": Zb(9,11,14), "k3": Zb(4,6,7), "var": S1, "var2": S2}},
    bauen=bf8, filter=[kopfrechenbar, fehler_eindeutig,
                       symbole_verschieden("var", "var2")])


S4K = Schablone(
    nr="S4K", titel="Gleichartige Terme",
    lektionen="4.1 – 4.10", erhebung="Vorstufe zu 2a",
    anleitung=ANLEITUNG,
    levelachse="Anzahl Glieder und Anzahl Sorten",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8],
    kernidee=("Gleichartig sind nur Terme mit genau denselben Variablen. Reine "
              "Zahlen sind eine eigene Sorte, und die Reihenfolge der Faktoren "
              "spielt keine Rolle — ab und ba sind dasselbe."),
)
