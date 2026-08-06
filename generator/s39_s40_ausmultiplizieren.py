# -*- coding: utf-8 -*-
"""
S39 · Ausmultiplizieren und zusammenfassen  (Lektionen 11.5 – 11.6)
S40 · Negative Zahl, Minus vor der Variablen mal Klammer
                                            (Lektionen 11.7 – 11.8)

    «Rechne aus.»
    2(x + 1) + 3(x + 2)      −3(x + 2)      −a(b − c)      x − 2(x − 3)

**Erhebungsaufgabe 2b** hängt an 11.8 und ist S40.

Der gefährlichste Fall des ganzen Kapitels steht in S40: ein MINUS vor der
Klammer dreht jedes Vorzeichen darin um. `−2(x − 3)` ist `−2x + 6`, nicht
`−2x − 6`. Genau dieser Fehler steht in jeder Bauform im Katalog.

LEVELACHSE (Teil 2):

    S39   Gliederzahl und Vorzeichen
    S40   Gliederzahl und Anzahl Minuszeichen

Bausteine aus `s11_ausmultiplizieren`.
"""
from __future__ import annotations

from sympy import Integer, expand, sympify

from korrektur import Zielform
from .s11_ausmultiplizieren import (ANLEITUNG, BEREICH, DREI, F, KM, SORTE1,
                                    SORTE2, SORTE3, STANDARD, TIPPS, VARS,
                                    ZWEI, _var, _zahl, bau, fehler_eindeutig,
                                    fuenf, kopfrechenbar, nicht_null,
                                    verschieden)
from .s9_division import M
from .schablone import Bauform, Schablone


# ══════════════════════════════════════════════════════════════════════════
# S39 · Ausmultiplizieren und zusammenfassen   (11.5 – 11.6)
# ══════════════════════════════════════════════════════════════════════════

def bf39_1(p):
    """Zwei Klammern, gleichartige Glieder danach:
       2(x + 1) + 3(x + 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(f), "++", (_var(v1), _zahl(k)))
    if st == 3:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _var(v2)))
        return bau("+-", [k1, k2])
    if st == 2:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _zahl(k + 1)))
        return bau("++", [k1, k2])
    k2 = KM(_zahl(f + 1), "++", (_var(v1), _zahl(k + 1)))
    return bau("++", [k1, k2])


BF39_1 = Bauform("BF1", "Zwei Klammern, danach zusammenfassen",
    bereiche=BEREICH, bauen=bf39_1, filter=ZWEI)


def bf39_2(p):
    """Klammer und einzelnes Glied:  2(x + 3) − x"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "+-" if st == 2 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("+-+", [km, _var(v1, k=2), _var(v2)])
    return bau("+-", [km, _var(v1)])


BF39_2 = Bauform("BF2", "Klammer und einzelnes Glied",
    bereiche=BEREICH, bauen=bf39_2, filter=ZWEI)


def bf39_3(p):
    """Variable mal Klammer, danach zusammenfassen:  x(x + 2) − x²"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1), "++-", (_var(v1), _zahl(k), _var(v2)))
        return bau("+-", [km, _var(v1, 2)])
    if st == 2:
        km = KM(_var(v1), "+-", (_var(v1), _zahl(k)))
        return bau("++", [km, _var(v1, 2)])
    km = KM(_var(v1), "++", (_var(v1), _zahl(k)))
    return bau("+-", [km, _var(v1, 2)])


BF39_3 = Bauform("BF3", "Variable mal Klammer, danach zusammenfassen",
    bereiche=BEREICH, bauen=bf39_3, filter=ZWEI)


def bf39_4(p):
    """Zwei Klammern mit Variablenfaktor:  a(b + 1) + b(a + 1)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_var(v1), "++", (_var(v2), _zahl(k)))
    if st == 3:
        k2 = KM(_var(v2), "+-", (_var(v1), _zahl(k)))
        return bau("+-", [k1, k2])
    if st == 2:
        k2 = KM(_var(v2), "+-", (_var(v1), _zahl(k)))
        return bau("++", [k1, k2])
    k2 = KM(_var(v2), "++", (_var(v1), _zahl(k)))
    return bau("++", [k1, k2])


BF39_4 = Bauform("BF4", "Zwei Klammern mit Variablenfaktor",
    bereiche=BEREICH, bauen=bf39_4, filter=ZWEI)


def bf39_5(p):
    """Drei Glieder in der Klammer, danach zusammenfassen"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        km = KM(_zahl(f), "++--", (_var(v1), _zahl(k), _var(v2), _var(v3)))
    elif st == 2:
        km = KM(_zahl(f), "+-+", (_var(v1), _zahl(k), _var(v2)))
    else:
        km = KM(_zahl(f), "+++", (_var(v1), _zahl(k), _var(v2)))
    return bau("++", [km, _var(v1)])


BF39_5 = Bauform("BF5", "Drei Glieder in der Klammer",
    bereiche=BEREICH, bauen=bf39_5, filter=DREI)


def bf39_6(p):
    """Sonderfall: alles hebt sich auf:  2(x + 1) − 2x − 2"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "++", (_var(v1), _zahl(k)))
    if st == 3:
        glieder = [km, _var(v1, k=f), _zahl(f * k - 1), _zahl(1)]
        muster = "+---"
    elif st == 2:
        #: Auf B steht die Zahl vor dem x-Glied — ein anderer Aufbau.
        glieder = [km, _zahl(f * k), _var(v1, k=f)]
        muster = "+--"
    else:
        glieder = [km, _var(v1, k=f), _zahl(f * k)]
        muster = "+--"
    return _null_aufgabe(muster, glieder, f, k, v1)


def _null_aufgabe(muster, glieder, f, k, v1):
    from korrektur import Aufgabe, Loesung
    from .s9_division import _reihe as _r
    _reihe = _r
    frage = _reihe(muster, glieder)
    return {"frage": frage, "loesung_text": "0",
            "aufgabe": Aufgabe(loesung=Loesung.zahl(0), variablen=VARS,
                               zielform=Zielform.AUSMULTIPLIZIERT,
                               fehlerkatalog=[
                F("nicht_null_39", expand(sympify(glieder[0].wert)),
                  "Nach dem Ausmultiplizieren heben sich alle Glieder auf."),
                F("nur_zahl_39", Integer(f * k),
                  "Auch die Zahlen heben sich auf."),
                F("nur_variable_39", expand(_var(v1, k=f).wert),
                  "Auch die x-Glieder heben sich auf."),
                F("eins_39", Integer(1),
                  "Es bleibt nichts übrig — das Ergebnis ist null."),
                F("doppelt_39", expand(sympify(glieder[0].wert) * 2),
                  "Jedes Glied kommt genau einmal vor."),
            ]),
            "schritte": [("Klammer ausmultiplizieren", frage),
                         ("Alles zusammenfassen", "0")],
            "tipps": [TIPPS[0], TIPPS[1],
                      "Nach dem Ausmultiplizieren heben sich alle Glieder "
                      "gegenseitig auf."]}


BF39_6 = Bauform("BF6", "Sonderfall: alles hebt sich auf",
    bereiche=BEREICH, bauen=bf39_6,
    filter=[kopfrechenbar, fehler_eindeutig, fuenf])


def bf39_7(p):
    """Klammer vorne, Klammer hinten, verschiedene Faktoren"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(f), "++", (_var(v1), _var(v2)))
    if st == 3:
        k2 = KM(_zahl(f + 2), "+-", (_var(v1), _var(v2)))
        return bau("+-", [k1, k2])
    if st == 2:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _var(v2)))
        return bau("++", [k1, k2])
    k2 = KM(_zahl(f + 1), "++", (_var(v1), _var(v2)))
    return bau("++", [k1, k2])


BF39_7 = Bauform("BF7", "Zwei Klammern mit zwei Variablen",
    bereiche=BEREICH, bauen=bf39_7, filter=ZWEI)


def bf39_8(p):
    """Monom mal Klammer, danach zusammenfassen"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1, k=f), "+-+", (_var(v1), _var(v2), _zahl(k)))
    elif st == 2:
        km = KM(_var(v1, k=f), "+-", (_var(v1), _var(v2)))
    else:
        km = KM(_var(v1, k=f), "++", (_var(v1), _var(v2)))
    return bau("++", [km, _var(v1, 2)])


BF39_8 = Bauform("BF8", "Monom mal Klammer, danach zusammenfassen",
    bereiche=BEREICH, bauen=bf39_8, filter=ZWEI)


def bf39_9(p):
    """Klammer mal Zahl, dann noch eine Zahl:  3(x + 2) + 5"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "+-" if st == 2 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("++-", [km, _zahl(k + 3), _zahl(1)])
    return bau("++", [km, _zahl(k + 3)])


BF39_9 = Bauform("BF9", "Klammer mal Zahl, dann noch eine Zahl",
    bereiche=BEREICH, bauen=bf39_9, filter=ZWEI)


def bf39_10(p):
    """Drei Klammern"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(f), "++", (_var(v1), _zahl(1)))
    k2 = KM(_zahl(f + 1), "++", (_var(v1), _zahl(k)))
    if st == 3:
        k3 = KM(_zahl(2), "+-", (_var(v1), _var(v2)))
        return bau("++-", [k1, k2, k3])
    if st == 2:
        return bau("+-", [k1, k2])
    return bau("++", [k1, k2])


BF39_10 = Bauform("BF10", "Drei Klammern",
    bereiche=BEREICH, bauen=bf39_10, filter=ZWEI)


def bf39_11(p):
    """Potenzen entstehen und werden zusammengefasst"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1, k=f), "++-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_var(v1, k=f), "+-", (_var(v1), _zahl(k)))
    else:
        km = KM(_var(v1, k=f), "++", (_var(v1), _zahl(k)))
    return bau("++", [km, _var(v1, 2, k=2)])


BF39_11 = Bauform("BF11", "Potenzen entstehen und werden zusammengefasst",
    bereiche=BEREICH, bauen=bf39_11, filter=ZWEI)


def bf39_12(p):
    """Nichts lässt sich zusammenfassen"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        km = KM(_zahl(f), "++-", (_var(v1), _var(v2), _var(v3)))
    elif st == 2:
        km = KM(_zahl(f), "+-", (_var(v1), _var(v2)))
    else:
        km = KM(_zahl(f), "++", (_var(v1), _var(v2)))
    return bau("++", [km, _zahl(k)])


BF39_12 = Bauform("BF12", "Nichts lässt sich zusammenfassen",
    bereiche=BEREICH, bauen=bf39_12, filter=DREI)


S39 = Schablone(
    nr="S39", titel="Ausmultiplizieren und zusammenfassen",
    lektionen="11.5 – 11.6", erhebung="2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF39_1, BF39_2, BF39_3, BF39_4, BF39_5, BF39_6,
               BF39_7, BF39_8, BF39_9, BF39_10, BF39_11, BF39_12],
    kernidee=("Erst jede Klammer für sich ausmultiplizieren, dann alle "
              "gleichartigen Glieder zusammenfassen."),
)


# ══════════════════════════════════════════════════════════════════════════
# S40 · Negative Zahl, Minus vor der Variablen   (11.7 – 11.8, Erhebung 2b)
# ══════════════════════════════════════════════════════════════════════════

def bf40_1(p):
    """Negative Zahl mal Klammer:  −3(x + 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(-f), "++-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(-f), "+-", (_var(v1), _zahl(k)))
    else:
        km = KM(_zahl(-f), "++", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF40_1 = Bauform("BF1", "Negative Zahl mal Klammer",
    bereiche=BEREICH, bauen=bf40_1, filter=ZWEI)


def bf40_2(p):
    """Negative Zahl, Minus in der Klammer:  −3(x − 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(-f), "+--", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(-f), "+-", (_var(v1, k=2), _zahl(k)))
    else:
        km = KM(_zahl(-f), "+-", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF40_2 = Bauform("BF2", "Negative Zahl, Minus in der Klammer",
    bereiche=BEREICH, bauen=bf40_2, filter=ZWEI)


def bf40_3(p):
    """Minus vor der Variablen mal Klammer:  −a(b − c)

    Das ist Lektion 11.8 und damit Erhebungsaufgabe 2b.
    """
    v1, v2, v3, k, st = p["v1"], p["v2"], p["v3"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1, k=-1), "+--", (_var(v2), _var(v3), _zahl(k)))
    elif st == 2:
        km = KM(_var(v1, k=-1), "+-", (_var(v2), _var(v3)))
    else:
        km = KM(_var(v1, k=-1), "++", (_var(v2), _var(v3)))
    return bau("+", [km])


BF40_3 = Bauform("BF3", "Minus vor der Variablen mal Klammer",
    bereiche=BEREICH, bauen=bf40_3, filter=DREI)


def bf40_4(p):
    """Minus vor der Klammer, danach ein Glied:  x − 2(x − 3)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "+-" if st != 1 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("+-+", [_var(v1, k=3), km, _var(v2)])
    return bau("+-", [_var(v1, k=3), km])


BF40_4 = Bauform("BF4", "Minus vor der Klammer, danach ein Glied",
    bereiche=BEREICH, bauen=bf40_4, filter=ZWEI)


def bf40_5(p):
    """Zwei Klammern, beide mit Minus"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(-f), "++", (_var(v1), _zahl(k)))
    if st == 3:
        k2 = KM(_zahl(-(f + 1)), "+-", (_var(v1), _var(v2)))
    elif st == 2:
        k2 = KM(_zahl(-(f + 1)), "+-", (_var(v1), _zahl(k)))
    else:
        k2 = KM(_zahl(-(f + 1)), "++", (_var(v1), _zahl(k)))
    return bau("++", [k1, k2])


BF40_5 = Bauform("BF5", "Zwei Klammern, beide mit Minus",
    bereiche=BEREICH, bauen=bf40_5, filter=ZWEI)


def bf40_6(p):
    """Negatives Monom mal Klammer:  −2a(b + c)"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        km = KM(_var(v1, k=-f), "+--", (_var(v2), _var(v3), _zahl(k)))
    elif st == 2:
        km = KM(_var(v1, k=-f), "+-", (_var(v2), _var(v3)))
    else:
        km = KM(_var(v1, k=-f), "++", (_var(v2), _var(v3)))
    return bau("+", [km])


BF40_6 = Bauform("BF6", "Negatives Monom mal Klammer",
    bereiche=BEREICH, bauen=bf40_6, filter=DREI)


def bf40_7(p):
    """Minus vor der Klammer ohne Faktor:  −(x + 2)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(-1), "++-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        #: Zwei Glieder mit Variablen — sonst fallen bei −(x − k) die
        #: Kandidaten «nur erstes» und «nur letztes» zusammen.
        km = KM(_zahl(-1), "+-", (_var(v1, k=2), _var(v2)))
    else:
        km = KM(_zahl(-1), "++", (_var(v1), _zahl(k)))
    #: Beim Faktor −1 fallen mehrere gerechnete Kandidaten zusammen — hier
    #: braucht es zwei eigene.
    return bau("+", [km], extra=[
        F("klammer_geblieben_40", expand(-sympify(km.wert)),
          "Das Minus vor der Klammer dreht JEDES Vorzeichen darin um."),
        F("nur_erstes_40", expand(-sympify(km.glieder[0].wert)),
          "Auch das zweite Glied der Klammer wechselt das Vorzeichen."),
        F("letztes_40", expand(-sympify(km.glieder[-1].wert)),
          "Alle Glieder der Klammer wechseln das Vorzeichen, nicht nur "
          "eines."),
        F("summe_40", expand(sum(sympify(g.wert) for g in km.glieder)),
          "Das Minus vor der Klammer gehoert zur Aufgabe — es faellt nicht "
          "weg."),
    ])


BF40_7 = Bauform("BF7", "Minus vor der Klammer ohne Faktor",
    bereiche=BEREICH, bauen=bf40_7, filter=ZWEI)


def bf40_8(p):
    """Negative Klammer und positives Glied:  5 − 2(x + 1)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "+-" if st == 2 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("+-+", [_zahl(k * 4), km, _var(v2)])
    return bau("+-", [_zahl(k * 4), km])


BF40_8 = Bauform("BF8", "Negative Klammer und positives Glied",
    bereiche=BEREICH, bauen=bf40_8, filter=ZWEI)


def bf40_9(p):
    """Zwei Minuszeichen ergeben ein Plus:  −2(−x + 3)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(-f), "-+-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(-f), "--", (_var(v1), _zahl(k)))
    else:
        km = KM(_zahl(-f), "-+", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF40_9 = Bauform("BF9", "Zwei Minuszeichen ergeben ein Plus",
    bereiche=BEREICH, bauen=bf40_9, filter=ZWEI)


def bf40_10(p):
    """Negative Klammer, danach zusammenfassen"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(-f), "+-" if st != 1 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("++-", [km, _var(v1, k=f + 2), _var(v2)])
    return bau("++", [km, _var(v1, k=f + 2)])


BF40_10 = Bauform("BF10", "Negative Klammer, danach zusammenfassen",
    bereiche=BEREICH, bauen=bf40_10, filter=ZWEI)


def bf40_11(p):
    """Minus vor der Variablen, Potenz entsteht:  −x(x − 2)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1, k=-1), "+--", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_var(v1, k=-1), "+-", (_var(v1), _zahl(k)))
    else:
        km = KM(_var(v1, k=-1), "++", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF40_11 = Bauform("BF11", "Minus vor der Variablen, Potenz entsteht",
    bereiche=BEREICH, bauen=bf40_11, filter=ZWEI)


def bf40_12(p):
    """Zwei Klammern, eine positiv, eine negativ:
       2(x + 1) − 3(x − 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(f), "++", (_var(v1), _zahl(1)))
    if st == 3:
        k2 = KM(_zahl(f + 1), "+--", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _zahl(k)))
    else:
        k2 = KM(_zahl(f + 1), "++", (_var(v1), _zahl(k)))
    return bau("+-", [k1, k2])


BF40_12 = Bauform("BF12", "Zwei Klammern, eine positiv, eine negativ",
    bereiche=BEREICH, bauen=bf40_12, filter=ZWEI)


S40 = Schablone(
    nr="S40", titel="Negative Zahl, Minus vor der Variablen mal Klammer",
    lektionen="11.7 – 11.8", erhebung="2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Anzahl Minuszeichen",
    bauformen=[BF40_1, BF40_2, BF40_3, BF40_4, BF40_5, BF40_6,
               BF40_7, BF40_8, BF40_9, BF40_10, BF40_11, BF40_12],
    kernidee=("Ein Minus vor der Klammer dreht jedes Vorzeichen darin um — "
              "auch das zweite und dritte."),
)
