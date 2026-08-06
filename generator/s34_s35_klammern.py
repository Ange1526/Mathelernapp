# -*- coding: utf-8 -*-
"""
S34 · Strichoperation vor der Klammer  (Lektionen 10.2 – 10.6)
S35 · Punktoperation und Klammer       (Lektionen 10.7 – 10.11)

    «Rechne aus.»
    20 − (7 + 5)      −(7 + 5) + 20      3 · (4 − 2)      12 : (2 · 3)

**In S34 liegt Lektion 10.6 — das häufigste Rücksprungziel im ganzen Netz.**
Wer irgendwo an einem Minus vor der Klammer scheitert, landet hier. Der
Fehler dazu wird in jeder Bauform aus der Aufgabe gerechnet: ein Minus vor
der Klammer dreht JEDES Vorzeichen darin um, nicht nur das erste.

Der Unterschied zwischen den beiden: bei S34 steht vor der Klammer ein Plus
oder Minus, bei S35 immer eine Punktoperation — und dort geht es um die
Reihenfolge, vor allem wenn der Faktor ausserhalb steht oder wenn durch eine
Klammer geteilt wird.

LEVELACHSE (Teil 2 beider Schablonen): die Gliederzahl.

Die Bausteine kommen aus `s10_klammern_neu`.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational

from .anzeige import MINUS, zeige
from .s10_klammern_neu import (ANLEITUNG, BEREICH, F, K, KL, STANDARD, Z,
                               _zahlen, bau, fehler_eindeutig, fuenf, ganz,
                               kopfrechenbar, nicht_null, siebe)
from .schablone import Bauform, Schablone


@dataclass(frozen=True)
class ROH:
    """Ein Glied mit eigenem Text — für verschachtelte Klammern."""
    text: str
    wert_: object

    @property
    def wert(self):
        return self.wert_

    @property
    def zahlen(self):
        return ()


SONDER = [kopfrechenbar, fehler_eindeutig, fuenf]


# ══════════════════════════════════════════════════════════════════════════
# S34 · Strichoperation vor der Klammer     (10.2 – 10.6)
# ══════════════════════════════════════════════════════════════════════════

def bf34_1(p):
    """Plus vor der Klammer — alle Vorzeichen bleiben stehen"""
    st = p["stufe"]
    n = st + 1
    mus = "+" + ("+-" * n)[:n - 1]
    return bau("++", [Z(p["a"]), KL(mus, tuple(_zahlen(p, n)))])


BF34_1 = Bauform("BF1", "Plus vor der Klammer — alle Vorzeichen bleiben",
    bereiche=BEREICH, bauen=bf34_1, filter=STANDARD)


def bf34_2(p):
    """Minus vor der Klammer, drinnen nur Plus:  20 − (7 + 5)

    Das ist Lektion 10.6 in ihrer reinsten Form.
    """
    st = p["stufe"]
    n = st + 1
    return bau("+-", [Z(p["a"] * 3),
                      KL("+" + "+" * (n - 1), tuple(_zahlen(p, n)))])


BF34_2 = Bauform("BF2", "Minus vor der Klammer, drinnen nur Plus",
    bereiche=BEREICH, bauen=bf34_2, filter=STANDARD)


def bf34_3(p):
    """Minus vor der Klammer, drinnen ein Minus — doppeltes Minus"""
    st = p["stufe"]
    n = st + 1
    return bau("+-", [Z(p["a"] * 3),
                      KL("+" + "-" * (n - 1), tuple(_zahlen(p, n)))])


BF34_3 = Bauform("BF3", "Minus vor der Klammer, doppeltes Minus",
    bereiche=BEREICH, bauen=bf34_3, filter=STANDARD)


def bf34_4(p):
    """Minus vor der Klammer, gemischte Vorzeichen drinnen"""
    st = p["stufe"]
    n = st + 2
    mus = "+" + ("-+" * n)[:n - 1]
    return bau("+-", [Z(p["a"] * 3), KL(mus, tuple(_zahlen(p, n)))])


BF34_4 = Bauform("BF4", "Minus vor der Klammer, gemischte Vorzeichen",
    bereiche=BEREICH, bauen=bf34_4, filter=STANDARD)


def bf34_5(p):
    """Ein Summand vor UND nach der Klammer:  20 − (7 + 5) + 3"""
    st = p["stufe"]
    n = st + 1
    if st == 3:
        return bau("+-+-", [Z(p["a"] * 3), KL("++", (p["b"], p["c"])),
                            Z(p["b"]), Z(1)])
    return bau("+-+", [Z(p["a"] * 3),
                       KL("+" + "+" * (n - 1), tuple(_zahlen(p, n))),
                       Z(p["b"])])


BF34_5 = Bauform("BF5", "Summand vor UND nach der Klammer",
    bereiche=BEREICH, bauen=bf34_5, filter=STANDARD)


def bf34_6(p):
    """Die Klammer steht ganz vorne, mit Minus davor:  −(7 + 5) + 20"""
    st = p["stufe"]
    n = st + 1
    return bau("-+", [KL("+" + "+" * (n - 1), tuple(_zahlen(p, n))),
                      Z(p["a"] * 3)])


BF34_6 = Bauform("BF6", "Klammer ganz vorne, mit Minus davor",
    bereiche=BEREICH, bauen=bf34_6, filter=STANDARD)


def bf34_7(p):
    """Zwei Klammern hintereinander:  (8 + 3) − (4 + 2)"""
    st = p["stufe"]
    n = st + 1
    k1 = KL("+" + "+" * (n - 1), tuple(_zahlen(p, n)))
    k2 = KL("+" + "-" * (n - 1), tuple(_zahlen(p, n)[::-1]))
    if st == 3:
        return bau("+-+", [k1, k2, Z(p["b"])])
    return bau("+-", [k1, k2])


BF34_7 = Bauform("BF7", "Zwei Klammern hintereinander",
    bereiche=BEREICH, bauen=bf34_7, filter=STANDARD)


def bf34_8(p):
    """Verschachtelte Klammern:  20 − (8 − (3 + 2))"""
    a, b, c, st = p["a"], p["b"], p["c"], p["stufe"]
    innen = KL("++", (b, c)) if st == 1 else KL("++-", (b, c, 1))
    aussen_wert = Integer(a) - innen.wert
    if st == 3:
        aussen = ROH(f"({zeige(Integer(a))} {MINUS} {innen.text} + "
                     f"{zeige(Integer(c))})", aussen_wert + c)
    else:
        aussen = ROH(f"({zeige(Integer(a))} {MINUS} {innen.text})",
                     aussen_wert)
    l = Integer(a * 3) - aussen.wert
    frage = f"{zeige(Integer(a * 3))} {MINUS} {aussen.text}"
    from korrektur import Aufgabe, Loesung, Zielform
    return {"frage": frage, "loesung_text": zeige(l),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=set(),
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=siebe([
                F("innere_klammer_zuerst",
                  Integer(a * 3) - Integer(a) - innen.wert,
                  "Die INNERE Klammer wird zuerst gerechnet — und das "
                  "Minus davor gilt für ihr ganzes Ergebnis."),
                F("beide_minus_vergessen",
                  Integer(a * 3) - Integer(a) + innen.wert,
                  "Zwei Minuszeichen hintereinander ergeben ein Plus. "
                  "Zähl sie einzeln."),
                F("nur_aussen", Integer(a * 3) - Integer(a),
                  "Auch die innere Klammer gehört zur Rechnung."),
                F("vorzeichen_34", -l,
                  "Zähl die Minuszeichen noch einmal."),
                F("alles_addiert_34",
                  Integer(a * 3) + Integer(a) + innen.wert,
                  "Nicht alle Zeichen sind Plus."),
                F("nur_innere", Integer(a * 3) - innen.wert,
                  "Zwischen den beiden Klammern steht noch eine Zahl — "
                  "sie gehoert mit dazu."),
                F("innere_ignoriert", Integer(a * 3) - Integer(a) * 2,
                  "Die innere Klammer wird zuerst gerechnet, nicht "
                  "weggelassen."),
            ], l)),
            "schritte": [("Die innerste Klammer zuerst",
                          f"{innen.text} = {zeige(innen.wert)}"),
                         ("Dann die äussere", zeige(aussen.wert)),
                         ("Zum Schluss der Rest", zeige(l))],
            "tipps": ["Bei verschachtelten Klammern beginnt man innen.",
                      "Rechne die innerste Klammer aus und schreib den Term "
                      "neu hin.",
                      f"{innen.text} ergibt {zeige(innen.wert)}."]}


BF34_8 = Bauform("BF8", "Verschachtelte Klammern",
    bereiche=BEREICH, bauen=bf34_8,
    filter=[kopfrechenbar, fehler_eindeutig, fuenf, nicht_null, ganz])


def bf34_9(p):
    """Sonderfall: die Klammer ergibt null:  20 − (7 − 7)"""
    a, b, st = p["a"], p["b"], p["stufe"]
    if st == 1:
        kl = KL("+-", (b, b))
    elif st == 2:
        kl = KL("+-+-", (b, b, a, a))
    else:
        kl = KL("+-+-+-", (b, b, a, a, p["c"], p["c"]))
    return bau("+-", [Z(a * 3), kl], extra=[
        F("klammer_ignoriert_34", Integer(a * 3) - Integer(b),
          "Die Klammer ergibt null — es wird nichts abgezogen."),
    ])


BF34_9 = Bauform("BF9", "Sonderfall: die Klammer ergibt null",
    bereiche=BEREICH, bauen=bf34_9, filter=STANDARD)


def bf34_10(p):
    """Sonderfall: das Ergebnis ist null:  12 − (7 + 5)"""
    a, b, st = p["a"], p["b"], p["stufe"]
    if st == 1:
        kl = KL("++", (b, a))
    elif st == 2:
        kl = KL("++-", (b, a, 1))
    else:
        kl = KL("++-+", (b, a, 1, p["c"]))
    g = bau("+-", [Z(int(kl.wert)), kl])
    g["aufgabe"].fehlerkatalog = siebe([
        F("nicht_null_34", kl.wert,
          "Vor und in der Klammer steht derselbe Wert — es bleibt null."),
        F("doppelt_34", kl.wert * 2,
          "Die Klammer wird abgezogen, nicht dazugezählt."),
        F("eins_34", Integer(1), "Es bleibt genau null übrig."),
        F("minus_34", Integer(-1), "Es bleibt genau null übrig."),
        F("erste_zahl_34", Integer(kl.zahlen[0]),
          "Alle Zahlen der Klammer zählen mit."),
    ], Integer(0))
    return g


BF34_10 = Bauform("BF10", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH, bauen=bf34_10, filter=SONDER)


def bf34_11(p):
    """Drei Glieder, Klammer in der Mitte:  20 − (7 + 5) − 3"""
    st = p["stufe"]
    n = st + 1
    return bau("+--", [Z(p["a"] * 3),
                       KL("+" + "+" * (n - 1), tuple(_zahlen(p, n))),
                       Z(p["b"])])


BF34_11 = Bauform("BF11", "Drei Glieder, Klammer in der Mitte",
    bereiche=BEREICH, bauen=bf34_11, filter=STANDARD)


def bf34_12(p):
    """Zwei Klammern, beide mit Minus davor"""
    st = p["stufe"]
    n = st + 1
    k1 = KL("+" + "+" * (n - 1), tuple(_zahlen(p, n)))
    k2 = KL("+" + "-" * (n - 1), tuple(_zahlen(p, n)[::-1]))
    return bau("+--", [Z(p["a"] * 4), k1, k2])


BF34_12 = Bauform("BF12", "Zwei Klammern, beide mit Minus davor",
    bereiche=BEREICH, bauen=bf34_12, filter=STANDARD)


S34 = Schablone(
    nr="S34", titel="Strichoperation vor der Klammer",
    lektionen="10.2 – 10.6", erhebung="Vorstufe zu 2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl",
    bauformen=[BF34_1, BF34_2, BF34_3, BF34_4, BF34_5, BF34_6,
               BF34_7, BF34_8, BF34_9, BF34_10, BF34_11, BF34_12],
    kernidee=("Ein Minus vor der Klammer dreht jedes Vorzeichen darin um — "
              "auch das zweite und dritte."),
)


# ══════════════════════════════════════════════════════════════════════════
# S35 · Punktoperation und Klammer     (10.7 – 10.11)
# ══════════════════════════════════════════════════════════════════════════

def bf35_1(p):
    """Nur Punktoperationen:  3 · (4 · 2)"""
    st = p["stufe"]
    n = st + 1
    klein = (2, 3, 2, 2)[:n]
    return bau("+", [K(Z(2), KL("+" + "·" * (n - 1), klein))])


BF35_1 = Bauform("BF1", "Nur Punktoperationen",
    bereiche=BEREICH, bauen=bf35_1, filter=STANDARD)


def bf35_2(p):
    """Strich vor der Klammer, Punkt darin:  20 − (3 · 4)"""
    st = p["stufe"]
    n = st + 1
    klein = (3, 4, 2, 2)[:n]
    return bau("+-", [Z(p["a"] * 4), KL("+" + "·" * (n - 1), klein)])


BF35_2 = Bauform("BF2", "Strich vor der Klammer, Punkt darin",
    bereiche=BEREICH, bauen=bf35_2, filter=STANDARD)


def bf35_3(p):
    """Punkt vor der Klammer, Strich darin:  3 · (4 − 2)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-", (p["a"], p["b"]))
    elif st == 2:
        kl = KL("+-+", (p["a"], p["b"], p["c"]))
    else:
        kl = KL("+-+-", (p["a"], p["b"], p["c"], 1))
    return bau("+", [K(Z(p["b"]), kl)])


BF35_3 = Bauform("BF3", "Punkt vor der Klammer, Strich darin",
    bereiche=BEREICH, bauen=bf35_3, filter=STANDARD)


def bf35_4(p):
    """Mehrere Operationen in der Klammer:  3 · (4 − 2 · 5)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-·", (p["a"] * 3, p["b"], 2))
    elif st == 2:
        kl = KL("+-·+", (p["a"], p["b"], 2, p["c"]))
    else:
        kl = KL("+-·+-", (p["a"], p["b"], 2, p["c"], 1))
    return bau("+", [K(Z(2), kl)])


BF35_4 = Bauform("BF4", "Mehrere Operationen in der Klammer",
    bereiche=BEREICH, bauen=bf35_4, filter=STANDARD)


def bf35_5(p):
    """Zwei Faktoren vor der Klammer:  3 · 2 · (5 − 4)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-", (p["a"], p["b"]))
        return bau("+", [K(Z(2), Z(2), kl)])
    if st == 2:
        kl = KL("+-+", (p["a"], p["b"], p["c"]))
        return bau("+", [K(Z(2), Z(2), kl)])
    kl = KL("+-+-", (p["a"], p["b"], p["c"], 1))
    return bau("+", [K(Z(2), Z(2), kl)])


BF35_5 = Bauform("BF5", "Zwei Faktoren vor der Klammer",
    bereiche=BEREICH, bauen=bf35_5, filter=STANDARD)


def bf35_6(p):
    """Klammer vorne, Faktor dahinter:  (6 + 2) · 3"""
    st = p["stufe"]
    n = st + 1
    return bau("+", [K(KL("+" + "+" * (n - 1), tuple(_zahlen(p, n))), Z(2))])


BF35_6 = Bauform("BF6", "Klammer vorne, Faktor dahinter",
    bereiche=BEREICH, bauen=bf35_6, filter=STANDARD)


def bf35_7(p):
    """Zwei Produkte, eines in der Klammer:  20 − (3 · 4) + 2 · 5"""
    st = p["stufe"]
    kl = KL("+·", (3, 4)) if st == 1 else KL("+·+", (3, 4, p["c"]))
    if st == 3:
        return bau("+-+", [Z(p["a"] * 4), kl, K(Z(2), Z(p["b"]))])
    if st == 2:
        return bau("+-", [Z(p["a"] * 4), kl])
    return bau("+-", [Z(p["a"] * 4), kl])


BF35_7 = Bauform("BF7", "Zwei Produkte, eines in der Klammer",
    bereiche=BEREICH, bauen=bf35_7, filter=STANDARD)


def bf35_8(p):
    """Durch eine Klammer geteilt:  12 : (2 · 3)"""
    st = p["stufe"]
    if st == 1:
        kl, oben = KL("+·", (2, 3)), 12
    elif st == 2:
        kl, oben = KL("+·+", (2, 3, 2)), 24
    else:
        kl, oben = KL("+·+-", (2, 3, 4, 2)), 32
    return bau("+", [K(Z(oben), kl, ops=[":"])])


BF35_8 = Bauform("BF8", "Durch eine Klammer geteilt",
    bereiche=BEREICH, bauen=bf35_8,
    filter=[kopfrechenbar, fehler_eindeutig, fuenf, nicht_null, ganz])


def bf35_9(p):
    """Sonderfall: die Klammer ergibt null:  3 · (4 − 4)"""
    a, b, st = p["a"], p["b"], p["stufe"]
    if st == 1:
        kl = KL("+-", (a, a))
    elif st == 2:
        kl = KL("+-+-", (a, a, b, b))
    else:
        kl = KL("+-+-+-", (a, a, b, b, p["c"], p["c"]))
    g = bau("+", [K(Z(b), kl)])
    g["aufgabe"].fehlerkatalog = siebe([
        F("nicht_null_35", Integer(b) * Integer(a),
          "In der Klammer steht null — mal null ergibt null."),
        F("summe_35", Integer(b) + Integer(a),
          "Zuerst die Klammer: sie ergibt null."),
        F("eins_35", Integer(1), "Mal null ergibt null, nicht eins."),
        F("faktor_35", Integer(b),
          "Der Faktor vor der Klammer ändert nichts: null bleibt null."),
        F("minus_35", Integer(-1), "Null bleibt null."),
    ], Integer(0))
    return g


BF35_9 = Bauform("BF9", "Sonderfall: die Klammer ergibt null",
    bereiche=BEREICH, bauen=bf35_9, filter=SONDER)


def bf35_10(p):
    """Sonderfall: die Klammer ergibt eins:  5 · (4 − 3)"""
    a, b, st = p["a"], p["b"], p["stufe"]
    if st == 1:
        kl = KL("+-", (a, a - 1))
    elif st == 2:
        kl = KL("+-+", (a, a, 1))
    else:
        kl = KL("+-+-", (a, a, b + 1, b))
    return bau("+", [K(Z(b), kl)], extra=[
        F("mal_eins_vergessen", Integer(b) * Integer(a),
          "Die Klammer ergibt 1 — mal eins ändert nichts."),
    ])


BF35_10 = Bauform("BF10", "Sonderfall: die Klammer ergibt eins",
    bereiche=BEREICH, bauen=bf35_10, filter=STANDARD)


def bf35_11(p):
    """Klammer mal Klammer:  (3 + 2) · (4 − 2)"""
    st = p["stufe"]
    n = st + 1
    k1 = KL("+" + "+" * (n - 1), tuple(_zahlen(p, n)))
    k2 = KL("+-", (p["b"] + 2, p["b"]))
    return bau("+", [K(k1, k2)])


BF35_11 = Bauform("BF11", "Klammer mal Klammer",
    bereiche=BEREICH, bauen=bf35_11, filter=STANDARD)


def bf35_12(p):
    """Produkt und Klammer nebeneinander:  2 · 3 + (8 − 5)"""
    st = p["stufe"]
    n = st + 1
    kl = KL("+" + "-" * (n - 1), tuple(_zahlen(p, n)))
    if st == 3:
        return bau("++-", [K(Z(2), Z(p["b"])), kl, Z(1)])
    return bau("++", [K(Z(2), Z(p["b"])), kl])


BF35_12 = Bauform("BF12", "Produkt und Klammer nebeneinander",
    bereiche=BEREICH, bauen=bf35_12, filter=STANDARD)


S35 = Schablone(
    nr="S35", titel="Punktoperation und Klammer",
    lektionen="10.7 – 10.11", erhebung="Vorstufe zu 2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl",
    bauformen=[BF35_1, BF35_2, BF35_3, BF35_4, BF35_5, BF35_6,
               BF35_7, BF35_8, BF35_9, BF35_10, BF35_11, BF35_12],
    kernidee=("Was in der Klammer steht, wird zuerst gerechnet — auch wenn "
              "der Faktor davor oder dahinter steht."),
)
