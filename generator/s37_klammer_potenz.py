# -*- coding: utf-8 -*-
"""
S37 · Klammer mit negativem Ergebnis quadrieren   (Lektion 10.16)

    «Rechne aus.»
    (3 − 5)²      −(3 − 5)²      (5 − 7)² · (3² − 2) : 2²

**Erhebungsaufgabe 3d** hängt an 10.16 und steht als BF3 auf Level C im
Wortlaut: `(5 − 7)² · (3² − 2) : 2²` mit dem Ergebnis 7.

Diese Lektion existiert, weil zwei Dinge zusammenkommen, die einzeln schon
schwer sind: eine Klammer, die ein negatives Ergebnis liefert, und ein
Exponent darüber. Der Unterschied zwischen `(3 − 5)²` und `−(3 − 5)²` ist
der ganze Inhalt — beim ersten wird das Ergebnis positiv, beim zweiten
nicht.

LEVELACHSE (Teil 2): Gliederzahl und Exponent.

Die Bausteine kommen aus `s22_s23_potenzen`: Potenz, Klammer und Kette
stehen dort schon, samt Fehlerkatalog für negative Basen.
"""
from __future__ import annotations

from sympy import Integer

from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar, loesung_nicht_null
from .s22_s23_potenzen import (ANLEITUNG, F, K, Kette, Kl, Pz, TIPPS23, bau,
                               ganzzahlig, hat_fehler, hoch, tipps_fuer)
from .schablone import Bauform, Schablone

STANDARD = [kopfrechenbar, fehler_eindeutig, hat_fehler]
NICHT_NULL = STANDARD + [loesung_nicht_null]


def b37(muster, glieder, extra=()):
    return bau(muster, glieder, extra=extra,
               tipps=tipps_fuer(glieder, TIPPS23))


def kl(o, u, e, minus=False):
    """Eine Klammer, die ein negatives Ergebnis liefert:  (3 − 5)²"""
    return Pz(Integer(o - u), e,
              basis_text=f"{zeige(Integer(o))} {MINUS} {zeige(Integer(u))}",
              klammer=True)


BEREICH = {
    "A": {"o": [3, 4, 5], "u": [5, 6, 7], "e": [2], "k": [2, 3],
          "stufe": [1]},
    "B": {"o": [2, 3, 5], "u": [5, 8, 7], "e": [2, 3], "k": [3, 5],
          "stufe": [2]},
    "C": {"o": [2, 1, 3], "u": [9, 4, 8], "e": [2, 4], "k": [2, 3],
          "stufe": [3]},
}


def bf1(p):
    """Klammer ergibt negativ, gerader Exponent:  (3 − 5)²"""
    o, u, st = p["o"], p["u"], p["stufe"]
    glieder = [K(kl(o, u, 2))]
    muster = "+"
    if st == 2:
        glieder.append(K(Pz(Integer(p["k"]), 2)))
        muster = "+-"
    elif st == 3:
        glieder.append(K(Pz(Integer(p["k"]), 2)))
        glieder.append(K(Pz(Integer(2), 3)))
        muster = "+-+"
    return b37(muster, glieder)


BF1 = Bauform("BF1", "Klammer ergibt negativ, gerader Exponent",
    bereiche=BEREICH, bauen=bf1, filter=NICHT_NULL)


def bf2(p):
    """Klammer ergibt negativ, ungerader Exponent:  (3 − 5)³"""
    o, u, st = p["o"], p["u"], p["stufe"]
    e = 3 if st < 3 else 4
    glieder = [K(kl(o, u, e))]
    muster = "+"
    if st == 2:
        glieder.append(K(Pz(Integer(p["k"]), 2)))
        muster = "++"
    elif st == 3:
        glieder.append(K(Pz(Integer(p["k"]), 2)))
        glieder.append(K(Pz(Integer(2), 2)))
        muster = "+-+"
    return b37(muster, glieder)


BF2 = Bauform("BF2", "Klammer ergibt negativ, ungerader Exponent",
    bereiche=BEREICH, bauen=bf2, filter=NICHT_NULL)


def bf3(p):
    """Zwei Klammern, dazu Division.

    Auf Level C ist das Erhebungsaufgabe 3d im Wortlaut:
    (5 − 7)² · (3² − 2) : 2²  =  7
    """
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    rechts = Kl(f"{zeige(Integer(3))}{hoch(2)} {MINUS} {zeige(Integer(2))}",
                Integer(7))
    if st == 1:
        #: Nur die Klammer mit der Potenz darin
        return b37("+-", [K(Pz(Integer(3), 2)), K(Integer(2))])
    if st == 2:
        return b37("+", [K(kl(5, 7, 2), rechts)])
    return b37("+", [Kette((kl(5, 7, 2), rechts, Pz(Integer(2), 2)),
                           ("·", ":"))])


BF3 = Bauform("BF3", "Zwei Klammern, dazu Division",
    bereiche=BEREICH, bauen=bf3,
    filter=[fehler_eindeutig, hat_fehler, ganzzahlig])


def bf4(p):
    """Minus VOR der Klammer statt darin:  −(3 − 5)²  →  −4

    Der Kern der Lektion: die Potenz gilt für die Klammer, das Minus
    davor bleibt stehen.
    """
    o, u, st = p["o"], p["u"], p["stufe"]
    glieder = [K(kl(o, u, 2))]
    muster = "-"
    if st == 2:
        glieder.append(K(Pz(Integer(p["k"]), 2)))
        muster = "-+"
    elif st == 3:
        glieder.append(K(kl(2, 4, 2)))
        muster = "--"
    return b37(muster, glieder, extra=[
        F("minus_in_die_klammer", -Integer((o - u) ** 2)
          if False else Integer((o - u) ** 2),
          f"Das Minus steht VOR der Klammer, nicht darin. Erst wird "
          f"({zeige(Integer(o))} {MINUS} {zeige(Integer(u))}){hoch(2)} "
          f"gerechnet, dann kommt das Minus dazu."),
    ])


BF4 = Bauform("BF4", "Minus vor der Klammer statt darin",
    bereiche=BEREICH, bauen=bf4, filter=NICHT_NULL)


def bf5(p):
    """Potenzierte Klammer plus oder minus eine Zahl:  (4 − 6)² + 3"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    if st == 3:
        glieder = [K(kl(o, u, 2)), K(kl(1, 4, 2))]
        muster = "+-"
    elif st == 2:
        glieder = [K(kl(o, u, 2)), K(Integer(k))]
        muster = "+-"
    else:
        glieder = [K(kl(o, u, 2)), K(Integer(k))]
        muster = "++"
    return b37(muster, glieder)


BF5 = Bauform("BF5", "Potenzierte Klammer plus oder minus eine Zahl",
    bereiche=BEREICH, bauen=bf5, filter=NICHT_NULL)


def bf6(p):
    """Faktor vor der potenzierten Klammer:  2 · (3 − 5)²"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    glieder = [K(Integer(k), kl(o, u, 2))]
    muster = "+"
    if st == 2:
        glieder.append(K(Pz(Integer(2), 3)))
        muster = "+-"
    elif st == 3:
        glieder.append(K(Integer(2), kl(1, 3, 2)))
        muster = "+-"
    return b37(muster, glieder)


BF6 = Bauform("BF6", "Faktor vor der potenzierten Klammer",
    bereiche=BEREICH, bauen=bf6, filter=NICHT_NULL)


def bf7(p):
    """Zwei potenzierte Klammern nebeneinander"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    if st == 3:
        glieder = [K(kl(o, u, 2)), K(kl(2, 5, 2)), K(Pz(Integer(2), 2))]
        muster = "+--"
    elif st == 2:
        glieder = [K(kl(o, u, 2)), K(kl(2, 5, 2))]
        muster = "+-"
    else:
        glieder = [K(kl(o, u, 2)), K(kl(1, 3, 2))]
        muster = "++"
    return b37(muster, glieder)


BF7 = Bauform("BF7", "Zwei potenzierte Klammern nebeneinander",
    bereiche=BEREICH, bauen=bf7, filter=NICHT_NULL)


def bf8(p):
    """Sonderfall: das Ergebnis ist null:  (3 − 3)²"""
    o, k, st = p["o"], p["k"], p["stufe"]
    if st == 3:
        glieder = [K(kl(o, o, 2), Pz(Integer(k), 2))]
        muster = "+"
    elif st == 2:
        #: Auf B ein zweites Glied — sonst haetten A und B denselben Aufbau.
        glieder = [K(kl(o, o, 3)), K(Pz(Integer(k), 2))]
        muster = "+-"
        return b37(muster, glieder, extra=[
            F("nur_klammer_37", Integer(0),
              "Die Klammer ergibt null, aber das zweite Glied bleibt."),
            F("eins_37b", Integer(1), "Null hoch drei ist null."),
            F("plus_37b", Integer(k ** 2),
              "Das zweite Glied wird abgezogen, nicht addiert."),
            F("zahl_37b", Integer(o), "Zuerst die Klammer ausrechnen."),
            F("zwei_37b", Integer(2), "Der Exponent ist nicht das Ergebnis."),
        ])
    else:
        glieder = [K(kl(o, o, 2))]
        muster = "+"
    return b37(muster, glieder, extra=[
        F("nicht_null_37", Integer(o ** 2),
          f"In der Klammer steht {zeige(Integer(o))} {MINUS} "
          f"{zeige(Integer(o))} = 0, und null hoch irgendetwas bleibt null."),
        F("eins_37", Integer(1),
          "Null hoch zwei ist null, nicht eins."),
        F("zahl_37", Integer(o),
          "Zuerst die Klammer ausrechnen — sie ergibt null."),
        F("minus_37", Integer(-1),
          "Null bleibt null."),
        F("zwei_37", Integer(2),
          "Der Exponent ist nicht das Ergebnis."),
    ])


BF8 = Bauform("BF8", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH, bauen=bf8, filter=[fehler_eindeutig, hat_fehler])


def bf9(p):
    """Sonderfall: die Klammer ergibt minus eins:  (3 − 4)⁴"""
    o, k, st = p["o"], p["k"], p["stufe"]
    e = 4 if st == 1 else (5 if st == 2 else 4)
    glieder = [K(kl(o, o + 1, e))]
    muster = "+"
    if st == 2:
        #: Auf B ein Faktor davor, auf C ein zweites Glied.
        glieder = [K(Integer(k), kl(o, o + 1, e))]
    elif st == 3:
        glieder.append(K(Pz(Integer(k), 2)))
        muster = "+-"
    return b37(muster, glieder, extra=[
        F("vorzeichen_37", Integer((-1) ** (e + 1)),
          f"Die Klammer ergibt {MINUS}1. Bei einer geraden Hochzahl wird "
          f"das Ergebnis positiv, bei einer ungeraden negativ."),
    ])


BF9 = Bauform("BF9", "Sonderfall: die Klammer ergibt minus eins",
    bereiche=BEREICH, bauen=bf9, filter=[fehler_eindeutig, hat_fehler])


def bf10(p):
    """Klammer im Nenner einer Division:  (2 − 6)² : 2²"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    if st == 3:
        kette = Kette((kl(2, 6, 2), Pz(Integer(2), 2), Pz(Integer(2), 1)),
                      (":", ":"))
    elif st == 2:
        #: Auf B kommt ein zweites Glied dazu.
        #: 36 : 9 = 4, minus 2² waere null — darum minus 3.
        return b37("+-", [Kette((kl(2, 8, 2), Pz(Integer(3), 2)), (":",)),
                          K(Integer(3))])
    else:
        kette = Kette((kl(2, 6, 2), Pz(Integer(2), 2)), (":",))
    return b37("+", [kette])


BF10 = Bauform("BF10", "Klammer geteilt durch eine Potenz",
    bereiche=BEREICH, bauen=bf10,
    filter=[fehler_eindeutig, hat_fehler, ganzzahlig, loesung_nicht_null])


def bf11(p):
    """Drei Glieder mit potenzierten Klammern"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    if st == 3:
        glieder = [K(kl(o, u, 2)), K(Integer(k), kl(1, 3, 2)),
                   K(Pz(Integer(2), 3))]
        muster = "+-+"
    elif st == 2:
        glieder = [K(kl(o, u, 2)), K(Integer(k), kl(1, 3, 2))]
        muster = "+-"
    else:
        glieder = [K(kl(o, u, 2)), K(Integer(k))]
        muster = "+-"
    return b37(muster, glieder)


BF11 = Bauform("BF11", "Drei Glieder mit potenzierten Klammern",
    bereiche=BEREICH, bauen=bf11, filter=NICHT_NULL)


def bf12(p):
    """Klammer mit drei Gliedern darin:  (2 − 6 + 1)²"""
    o, u, k, st = p["o"], p["u"], p["k"], p["stufe"]
    innen = o - u + 1
    p3 = Pz(Integer(innen), 2,
            basis_text=f"{zeige(Integer(o))} {MINUS} {zeige(Integer(u))} + 1",
            klammer=True)
    glieder = [K(p3)]
    muster = "+"
    if st == 2:
        glieder.append(K(Pz(Integer(k), 2)))
        muster = "+-"
    elif st == 3:
        glieder.append(K(Pz(Integer(k), 2)))
        glieder.append(K(Integer(2)))
        muster = "+-+"
    return b37(muster, glieder)


BF12 = Bauform("BF12", "Klammer mit drei Gliedern darin",
    bereiche=BEREICH, bauen=bf12, filter=NICHT_NULL)


S37 = Schablone(
    nr="S37", titel="Klammer mit negativem Ergebnis quadrieren",
    lektionen="10.16", erhebung="3d",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Exponent",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Zuerst die Klammer ausrechnen, dann potenzieren. Ein Minus "
              "VOR der Klammer gehört nicht zur Basis: (3 − 5)² ist +4, "
              "−(3 − 5)² ist −4."),
)
