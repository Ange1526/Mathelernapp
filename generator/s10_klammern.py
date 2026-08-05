# -*- coding: utf-8 -*-
"""
Klammern       (Lektionen 10.1 – 10.16, Erhebung 2b und 3d)

    «Rechne aus.»
    3 − (4 + 2)      −(2x − 5) + 7      (5 − 7)² · (3² − 2) : 2²

10.6 «Minus vor der Klammer» ist das häufigste Rücksprungziel im ganzen Netz:
sechs verschiedene Fehler aus zwei Schablonen zeigen dorthin. Ohne diesen
Generator läuft die Lückensuche ins Leere.

Levelachse: Anzahl Glieder in der Klammer (A zwei, B drei, C vier).
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

a, b, c, m, u, v, x, y, z = symbole("a b c m u v x y z")
VARS = {"a", "b", "c", "m", "u", "v", "x", "y", "z"}
ANLEITUNG = "Rechne aus."


def Zb(lo, hi):
    return [Integer(i) for i in range(lo, hi)]


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def bau(frage, loesung, fehler, schritte, tipps, zielform=Zielform.BELIEBIG):
    return {"frage": frage, "loesung_text": zeige(loesung),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=zielform, fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


TIPPS_MINUS = [
    "Ein Minus vor der Klammer dreht JEDES Vorzeichen darin um — nicht nur das erste.",
    "Du hast zwei Wege: entweder die Klammer zuerst ausrechnen, oder alle "
    "Vorzeichen drehen und die Klammer weglassen. Beide führen zum selben Ergebnis.",
    "Rechne zuerst aus, was in der Klammer steht, und zieh das Ergebnis dann ab.",
]
TIPPS_PLUS = [
    "Ein Plus vor der Klammer lässt alle Vorzeichen darin stehen.",
    "Du kannst die Klammer weglassen und der Reihe nach rechnen.",
    "Rechne zuerst aus, was in der Klammer steht.",
]


def glieder(p, muster):
    return [(muster[i], p[f"z{i}"]) for i in range(len(muster))]


def wert(g):
    s = Integer(0)
    for vz, zz in g:
        s += zz if vz == "+" else -zz
    return s


def txt(g):
    t = str(g[0][1]) if g[0][0] == "+" else f"{MINUS}{g[0][1]}"
    for vz, zz in g[1:]:
        t += f" {'+' if vz == '+' else MINUS} {zz}"
    return t


# ── BF1 bis BF4 · a  ±  ( Glieder ) ────────────────────────────────────────

def bau_klammer(vz_vor):
    def bauen(p):
        A_ = p["a"]
        g = glieder(p, p["muster"])
        innen = wert(g)
        loesung = A_ + innen if vz_vor == "+" else A_ - innen
        vz = "+" if vz_vor == "+" else MINUS
        fehler = []
        if vz_vor == "-":
            # F1 · Minus nur auf das erste Glied
            f1 = A_ - g[0][1] + wert(g[1:])
            fehler.append(F("nur_erstes", f1,
                            "Das Minus gilt für ALLES in der Klammer, nicht nur "
                            "für die erste Zahl."))
            if len(g) >= 3:
                f2 = A_ + sum((-zz if vz2 == "+" else zz) for vz2, zz in g[:-1]) \
                     + (g[-1][1] if g[-1][0] == "+" else -g[-1][1])
                fehler.append(F("letztes_nicht_gedreht", f2,
                                "Auch das letzte Vorzeichen in der Klammer dreht sich um."))
        return bau(f"{A_} {vz} ({txt(g)})", loesung, fehler,
                   schritte=[("Anschauen, was vor der Klammer steht",
                              f"ein {'Plus' if vz_vor == '+' else 'Minus'}"),
                             ("Klammer ausrechnen", f"{txt(g)} = {innen}"),
                             ("Strichoperation ausführen",
                              f"{A_} {vz} {innen} = {loesung}")],
                   tipps=TIPPS_MINUS if vz_vor == "-" else TIPPS_PLUS)
    return bauen


def ber(muster_je_level, a_je, z_je):
    out = {}
    for lvl, mu in muster_je_level.items():
        d = {"a": a_je[lvl], "muster": [mu]}
        for i in range(len(mu)):
            d[f"z{i}"] = z_je[lvl]
        out[lvl] = d
    return out


A_B = {"A": Zb(20, 60), "B": Zb(40, 120), "C": Zb(120, 300)}
Z_B = {"A": Zb(2, 20), "B": Zb(3, 30), "C": Zb(5, 45)}
STD = [kopfrechenbar, fehler_eindeutig]


BF1 = Bauform("BF1", "Plus vor der Klammer — alle Vorzeichen bleiben",
    bereiche=ber({"A": "+-", "B": "+-+", "C": "+-+-"}, A_B, Z_B),
    bauen=bau_klammer("+"), filter=STD)

BF2 = Bauform("BF2", "Minus vor der Klammer, drinnen nur Plus",
    bereiche=ber({"A": "++", "B": "+++", "C": "++++"}, A_B, Z_B),
    bauen=bau_klammer("-"), filter=STD)

BF3 = Bauform("BF3", "Minus vor der Klammer, drinnen ein Minus",
    bereiche=ber({"A": "+-", "B": "+-+", "C": "+-+-"}, A_B, Z_B),
    bauen=bau_klammer("-"), filter=STD)

BF4 = Bauform("BF4", "Minus vor der Klammer, gemischte Vorzeichen",
    bereiche=ber({"B": "++-", "C": "++-+"},
                 {"B": Zb(60, 150), "C": Zb(100, 250)},
                 {"B": Zb(4, 30), "C": Zb(8, 45)}),
    bauen=bau_klammer("-"), filter=STD, levels=("B", "C"))


# ── BF5 · Klammer vorne, Minus davor ───────────────────────────────────────

def bau_vorne(p):
    C_ = p["c"]
    g = glieder(p, p["muster"])
    innen = wert(g)
    loesung = -innen + C_
    return bau(f"{MINUS}({txt(g)}) + {C_}", loesung,
               [F("nur_erstes", -g[0][1] + wert(g[1:]) + C_,
                  "Das Minus gilt für die ganze Klammer."),
                F("minus_uebersehen", innen + C_,
                  "Vor der Klammer steht ein Minus — das ganze Klammerergebnis "
                  "wird abgezogen.")],
               schritte=[("Klammer ausrechnen", f"{txt(g)} = {innen}"),
                         ("Minus anwenden", f"{MINUS}{innen} + {C_} = {loesung}")],
               tipps=TIPPS_MINUS)


BF5 = Bauform("BF5", "Klammer steht vorne, Minus davor",
    bereiche={lvl: {**{f"z{i}": Z_B[lvl] for i in range(len(mu))},
                    "c": A_B[lvl], "muster": [mu]}
              for lvl, mu in {"A": "++", "B": "+-+", "C": "+-+-"}.items()},
    bauen=bau_vorne, filter=STD)


# ── BF6 · Verschachtelt ────────────────────────────────────────────────────

def bau_verschachtelt(p):
    A_, B_ = p["a"], p["b"]
    g = glieder(p, p["muster"])
    innen = wert(g)
    mitte = B_ - innen
    loesung = A_ - mitte
    return bau(f"{A_} {MINUS} [{B_} {MINUS} ({txt(g)})]", loesung,
               [F("von_aussen", A_ - B_ - innen,
                  "Immer von innen nach aussen: erst die runde Klammer, dann "
                  "die eckige."),
                F("aeusseres_minus", A_ + B_ - innen,
                  "Vor der eckigen Klammer steht ein Minus — sie wird ganz abgezogen.")],
               schritte=[("Innerste Klammer zuerst", f"{txt(g)} = {innen}"),
                         ("Eckige Klammer", f"{B_} {MINUS} {innen} = {mitte}"),
                         ("Zum Schluss aussen", f"{A_} {MINUS} ({mitte}) = {loesung}")],
               tipps=["Arbeite immer von innen nach aussen.",
                      "Rechne zuerst die runde Klammer aus, dann die eckige.",
                      f"Die runde Klammer ergibt {innen}."])


BF6 = Bauform("BF6", "Verschachtelte Klammern",
    bereiche={lvl: {**{f"z{i}": Z_B[lvl] for i in range(len(mu))},
                    "a": A_B[lvl], "b": Z_B[lvl], "muster": [mu]}
              for lvl, mu in {"B": "++", "C": "++-"}.items()},
    bauen=bau_verschachtelt, filter=STD, levels=("B", "C"))


# ── BF7 · Punkt vor der Klammer ────────────────────────────────────────────

def bau_faktor(p):
    f_ = p["f"]
    g = glieder(p, p["muster"])
    innen = wert(g)
    loesung = f_ * innen
    return bau(f"{f_} · ({txt(g)})", loesung,
               [F("nur_erstes", f_ * g[0][1] + wert(g[1:]),
                  "Der Faktor gilt für jedes Glied der Klammer."),
                F("klammer_zuletzt", f_ + innen,
                  "Zwischen Faktor und Klammer steht ein Mal, kein Plus.")],
               schritte=[("Klammer ausrechnen", f"{txt(g)} = {innen}"),
                         ("Mit dem Faktor multiplizieren",
                          f"{f_} · {innen} = {loesung}")],
               tipps=["Klammer vor Punkt vor Strich.",
                      "Rechne zuerst die Klammer aus, dann multipliziere.",
                      f"In der Klammer steht {innen}."])


BF7 = Bauform("BF7", "Faktor vor der Klammer",
    bereiche={lvl: {**{f"z{i}": Z_B[lvl] for i in range(len(mu))},
                    "f": Zb(2, 9), "muster": [mu]}
              for lvl, mu in {"A": "+-", "B": "+-+", "C": "+-+-"}.items()},
    bauen=bau_faktor, filter=STD)


# ── BF8 · Sonderfall: die Klammer ergibt null ──────────────────────────────

def bau_null(p):
    A_ = p["a"]
    g = glieder(p, p["muster"])
    rest = wert(g[:-1])
    g[-1] = ("-", rest) if rest > 0 else ("+", -rest)
    innen = wert(g)
    loesung = A_ - innen
    return bau(f"{A_} {MINUS} ({txt(g)})", loesung,
               [F("klammer_ignoriert", A_ - g[0][1],
                  "Rechne die ganze Klammer aus — hier ergibt sie null.")],
               schritte=[("Klammer ausrechnen", f"{txt(g)} = 0"),
                         ("Strichoperation", f"{A_} {MINUS} 0 = {loesung}")],
               tipps=TIPPS_MINUS)


BF8 = Bauform("BF8", "Sonderfall: die Klammer ergibt null",
    bereiche={lvl: {**{f"z{i}": Z_B[lvl] for i in range(len(mu))},
                    "a": A_B[lvl], "muster": [mu]}
              for lvl, mu in {"A": "+-", "B": "++-", "C": "++--"}.items()},
    bauen=bau_null, filter=[kopfrechenbar, fehler_eindeutig])


S10 = Schablone(
    nr="S10", titel="Klammern",
    lektionen="10.1 – 10.16", erhebung="Vorstufe zu 2b und 3d",
    anleitung=ANLEITUNG,
    levelachse="Anzahl Glieder in der Klammer",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8],
    kernidee=("Klammer vor Punkt vor Strich. Ein Minus vor der Klammer dreht "
              "jedes Vorzeichen darin um — auch das zweite und dritte."),
)
