# -*- coding: utf-8 -*-
"""
S50 · Bruchterme addieren bei gleichem Nenner  (Lektionen 14.6 – 14.7)
S51 · Multiplizieren, dividieren, Doppelbruch  (Lektionen 14.9 – 14.11)

    «Rechne aus und kürze so weit wie möglich.»
    2x/(3y) + x/(3y)        (a+b)/n − (a−b)/n
    (8a/(3b)) · (9bc/(4a))  ·  (8b/(9a)) : (4a/(3b))     ← Erhebung 5c

S51/BF2 auf Level B ist Erhebungsaufgabe 5c im Wortlaut:
`(8b/(9a)) : (4a/(3b))` mit dem Ergebnis `2b²/(3a²)`.

Die Bausteine kommen aus `s14_bruchterme` — Bruchterm, Fehlerkatalog und die
Prüfung auf «fertig gekürzt» stehen dort schon.
"""
from __future__ import annotations

from sympy import Integer, cancel, sympify

from korrektur import Aufgabe, Loesung, Zielform
from .s14_bruchterme import (ANLEITUNG, B, F, kette, SORTE1, SORTE2, SORTE3,
                             STANDARD, TIPPS50, TIPPS51, VARS, ZWEI, DREI,
                             _als_text, bau, fehler_eindeutig, fuenf,
                             kandidaten, klein, kopfrechenbar, reihe_b,
                             siebe, summe, verschieden)
from .s9_division import M, Su
from .schablone import Bauform, Schablone

BEREICH = {
    "A": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [2, 3],
          "k": [2, 3, 4], "stufe": [1]},
    "B": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [3, 4],
          "k": [3, 4, 5], "stufe": [2]},
    "C": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [4, 5],
          "k": [2, 3, 5], "stufe": [3]},
}


# ══════════════════════════════════════════════════════════════════════════
# S50 · Bruchterme addieren bei gleichem Nenner   (14.6 – 14.7)
# ══════════════════════════════════════════════════════════════════════════

def b50(muster, brueche, extra=()):
    """Mehrere Brüche mit demselben Nenner, verbunden mit + und −."""
    frage = reihe_b(muster, brueche)
    wert = cancel(summe(muster, brueche))
    nenner = brueche[0].nenner
    zaehler_summe = Integer(0)
    for zeichen, br in zip(muster, brueche):
        w = sympify(br.zaehler.wert)
        zaehler_summe += w if zeichen == "+" else -w
    if wert == 0:
        #: Die Zaehler heben sich auf. Fast jeder gerechnete Kandidat waere
        #: dann auch null — darum hier ein fester Katalog.
        katalog = list(extra) + [
            F("nicht_null_50", cancel(sympify(brueche[0].wert)),
              "Die Zähler heben sich genau auf — der ganze Term wird null."),
            F("eins_50", Integer(1),
              "Wenn oben null steht, ist der ganze Bruch null, nicht eins."),
            F("nenner_50", cancel(sympify(nenner.wert)),
              "Der Nenner spielt keine Rolle, sobald der Zähler null ist."),
            F("minus_eins_50", Integer(-1),
              "Null bleibt null."),
            F("zwei_50", Integer(2),
              "Rechne die Zähler zusammen: sie ergeben null."),
        ]
        return bau(frage, wert, katalog, TIPPS50)
    katalog = list(extra) + [
        F("nenner_addiert", cancel(zaehler_summe / (nenner.wert * len(brueche))),
          "Bei gleichem Nenner werden nur die Zähler verrechnet — der Nenner "
          "bleibt stehen, er wird nicht mitaddiert."),
        F("vorzeichen_zaehler", cancel(-wert),
          "Ein Minus vor einem Bruch gilt für den GANZEN Zähler, nicht nur "
          "für dessen erstes Glied."),
        F("nur_erster", cancel(sympify(brueche[0].wert)),
          "Alle Brüche zählen mit, nicht nur der erste."),
        F("zaehler_nenner_getauscht",
          cancel(nenner.wert * len(brueche) / zaehler_summe)
          if zaehler_summe != 0 else Integer(0),
          "Zähler und Nenner stehen verkehrt herum."),
        F("summe_der_nenner", cancel(zaehler_summe + nenner.wert),
          "Der Bruchstrich heisst geteilt — die Nenner werden nicht zum "
          "Zähler addiert."),
        F("alles_addiert", cancel(zaehler_summe * 2 / nenner.wert)
          if nenner.wert != 0 else Integer(0),
          "Jeder Zähler wird genau einmal gezählt."),
    ]
    return bau(frage, wert, katalog, TIPPS50, schritte=[
        ("Prüfen: haben alle Brüche denselben Nenner?", frage),
        ("Nur die Zähler verrechnen, der Nenner bleibt",
         f"({_als_text(zaehler_summe)})/({nenner.text})"),
        ("Kürzen, wenn möglich", _als_text(wert)),
    ])


def _n(p):
    """Der gemeinsame Nenner."""
    return M(Integer(p["f"]), ((p["v2"], 1),))


def bf50_1(p):
    """Addition, danach kürzbar:  2x/(3y) + x/(3y)"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    nen = _n(p)
    if st == 3:
        muster = "++-"
        br = [B(M(Integer(5), ((v1, 1),)), nen),
              B(M(Integer(3), ((v1, 1),)), nen),
              B(M(Integer(2), ((v1, 1),)), nen)]
    else:
        muster = "++"
        br = [B(M(Integer(2 if st == 1 else 2 * k), ((v1, 1),)), nen),
              B(M(Integer(1 if st == 1 else 4 * k), ((v1, 1),)), nen)]
    return b50(muster, br)


BF50_1 = Bauform("BF1", "Addition, danach kürzbar",
    bereiche=BEREICH, bauen=bf50_1, filter=ZWEI)


def bf50_2(p):
    """Subtraktion, danach kürzbar:  5/(8a) − 1/(8a)"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    nen = M(Integer(8 if st < 3 else 6), ((v1, 1),))
    if st == 3:
        muster = "+--"
        br = [B(M(Integer(11)), nen), B(M(Integer(3)), nen),
              B(M(Integer(2)), nen)]
    elif st == 2:
        #: Auf B steht im Zaehler eine Summe statt einer blossen Zahl.
        muster = "+-"
        br = [B(Su("++", (M(Integer(5)), M(Integer(2)))), nen),
              B(M(Integer(1)), nen)]
    else:
        muster = "+-"
        br = [B(M(Integer(5)), nen), B(M(Integer(1)), nen)]
    return b50(muster, br)


BF50_2 = Bauform("BF2", "Subtraktion, danach kürzbar",
    bereiche=BEREICH, bauen=bf50_2, filter=STANDARD)


def bf50_3(p):
    """Doppeltes Minus:  5/(3n) − (−1)/(3n)"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    nen = M(Integer(f), ((v1, 1),))
    if st == 3:
        muster = "+--"
        br = [B(M(Integer(7)), nen), B(M(Integer(-3)), nen),
              B(M(Integer(2)), nen)]
    elif st == 2:
        muster = "++-"
        br = [B(M(Integer(5)), nen), B(M(Integer(2)), nen),
              B(M(Integer(-5)), nen)]
    else:
        muster = "+-"
        br = [B(M(Integer(5)), nen), B(M(Integer(-1)), nen)]
    return b50(muster, br)


BF50_3 = Bauform("BF3", "Doppeltes Minus",
    bereiche=BEREICH, bauen=bf50_3, filter=STANDARD)


def bf50_4(p):
    """Summen im Zähler — der Bruch verschwindet:
       (a+b)/a + (a−b)/a  →  2"""
    v1, v2, st = p["v1"], p["v2"], p["stufe"]
    nen = M(Integer(1), ((v1, 1),))
    f1 = 1 if st == 1 else st
    br = [B(Su("++", (M(Integer(f1), ((v1, 1),)),
                      M(Integer(1), ((v2, 1),)))), nen),
          B(Su("+-", (M(Integer(1), ((v1, 1),)),
                      M(Integer(1), ((v2, 1),)))), nen)]
    if st == 3:
        #: Auf C kommt ein dritter Bruch dazu.
        br.append(B(M(Integer(1), ((v1, 1),)), nen))
        return b50("+++", br)
    return b50("++", br)


BF50_4 = Bauform("BF4", "Summen im Zähler — der Bruch verschwindet",
    bereiche=BEREICH, bauen=bf50_4, filter=ZWEI)


def bf50_5(p):
    """Minus vor einem ganzen Zähler — das ist Lektion 14.7:
       (a+b)/(n+1) − (a−b)/(n+1)  →  2b/(n+1)"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    nen = Su("++", (M(Integer(1), ((v3, 1),)), M(Integer(1))))
    f1 = 1 if st == 1 else st
    br = [B(Su("++", (M(Integer(1), ((v1, 1),)),
                      M(Integer(f1), ((v2, 1),)))), nen),
          B(Su("+-", (M(Integer(1), ((v1, 1),)),
                      M(Integer(f1), ((v2, 1),)))), nen)]
    if st == 3:
        br.append(B(M(Integer(1), ((v2, 1),)), nen))
        return b50("+-+", br)
    return b50("+-", br)


BF50_5 = Bauform("BF5", "Minus vor einem ganzen Zähler",
    bereiche=BEREICH, bauen=bf50_5, filter=DREI)


def bf50_6(p):
    """Zusammengesetzter Nenner:
       (2r+1)/(r−1)² + (r+3)/(r−1)²"""
    v1, v3, k, st = p["v1"], p["v3"], p["k"], p["stufe"]
    nen = Su("+-", (M(Integer(1), ((v3, 2),)), M(Integer(k * k))))
    if st == 3:
        muster = "++-"
        br = [B(Su("+-", (M(Integer(4), ((v1, 1),)), M(Integer(1)))), nen),
              B(Su("++", (M(Integer(2), ((v1, 1),)), M(Integer(7)))), nen),
              B(M(Integer(3), ((v1, 1),)), nen)]
    elif st == 2:
        #: Auf B steht im ersten Zaehler ein Minus.
        muster = "++"
        br = [B(Su("+-", (M(Integer(5), ((v1, 1),)), M(Integer(4)))), nen),
              B(Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(7)))), nen)]
    else:
        muster = "++"
        br = [B(Su("++", (M(Integer(2), ((v1, 1),)), M(Integer(1)))), nen),
              B(Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(3)))), nen)]
    return b50(muster, br)


BF50_6 = Bauform("BF6", "Zusammengesetzter Nenner",
    bereiche=BEREICH, bauen=bf50_6, filter=ZWEI)


def bf50_7(p):
    """Einfachster Fall, nichts zu kürzen:  3/x + 2/x"""
    v1, v2, st = p["v1"], p["v2"], p["stufe"]
    nen = M(Integer(1), ((v1, 1),))
    if st == 3:
        return b50("+-+", [B(M(Integer(5), ((v2, 1),)), nen),
                           B(M(Integer(3), ((v2, 1),)), nen),
                           B(M(Integer(1), ((v2, 1),)), nen)])
    if st == 2:
        return b50("++-", [B(M(Integer(1), ((v2, 1),)), nen),
                           B(M(Integer(2), ((v2, 1),)), nen),
                           B(M(Integer(1), ((v2, 1),)), nen)])
    return b50("++", [B(M(Integer(3)), nen), B(M(Integer(2)), nen)])


BF50_7 = Bauform("BF7", "Einfachster Fall, nichts zu kürzen",
    bereiche=BEREICH, bauen=bf50_7, filter=ZWEI)


def bf50_8(p):
    """Sonderfall: das Ergebnis ist null:  2/x − 2/x"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    nen = M(Integer(1), ((v1, 1),))
    if st == 3:
        z1 = Su("++", (M(Integer(3), ((v2, 1),)), M(Integer(2))))
        z2 = Su("+-", (M(Integer(1), ((v2, 1),)), M(Integer(1))))
        z3 = Su("++", (M(Integer(4), ((v2, 1),)), M(Integer(1))))
        br = [B(z1, nen), B(z2, nen), B(z3, nen)]
        muster = "++-"
    elif st == 2:
        z = Su("++", (M(Integer(1), ((v2, 1),)), M(Integer(1))))
        br = [B(z, nen), B(z, nen)]
        muster = "+-"
    else:
        br = [B(M(Integer(k)), nen), B(M(Integer(k)), nen)]
        muster = "+-"
    return b50(muster, br, extra=[
        F("nicht_null", Integer(2),
          "Die Zähler heben sich genau auf — der ganze Bruch wird null."),
    ])


BF50_8 = Bauform("BF8", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH, bauen=bf50_8, filter=[kopfrechenbar, fuenf, klein])


def bf50_9(p):
    """Zähler lassen sich nicht zusammenfassen:  3/x + x/x"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    nen = M(Integer(1), ((v3, 1),))
    if st == 3:
        br = [B(Su("++", (M(Integer(1), ((v1, 1),)),
                          M(Integer(1), ((v2, 1),)))), nen),
              B(Su("+-", (M(Integer(1), ((v1, 1),)),
                          M(Integer(1), ((v2, 1),)))), nen)]
    elif st == 2:
        br = [B(M(Integer(2), ((v1, 1),)), nen),
              B(M(Integer(1), ((v2, 1),)), nen)]
    else:
        br = [B(M(Integer(3)), nen), B(M(Integer(1), ((v1, 1),)), nen)]
    return b50("++", br)


BF50_9 = Bauform("BF9", "Zähler lassen sich nicht zusammenfassen",
    bereiche=BEREICH, bauen=bf50_9, filter=DREI)


def bf50_10(p):
    """Das Ergebnis muss gekürzt werden:  4x/(2y) + 2x/(2y)"""
    v1, v2, f, st = p["v1"], p["v2"], p["f"], p["stufe"]
    nen = M(Integer(2 * f), ((v2, 1),))
    if st == 3:
        return b50("++-", [B(M(Integer(6 * f), ((v1, 1),)), nen),
                           B(M(Integer(4 * f), ((v1, 1),)), nen),
                           B(M(Integer(2 * f), ((v1, 1),)), nen)])
    if st == 2:
        #: Auf B steht ein Minus — das ist der Vorzeichenregler.
        return b50("+-", [B(M(Integer(6 * f), ((v1, 1),)), nen),
                          B(M(Integer(2 * f), ((v1, 1),)), nen)])
    return b50("++", [B(M(Integer(2 * f), ((v1, 1),)), nen),
                      B(M(Integer(2 * f), ((v1, 1),)), nen)])


BF50_10 = Bauform("BF10", "Das Ergebnis muss gekürzt werden",
    bereiche=BEREICH, bauen=bf50_10, filter=ZWEI)


def bf50_11(p):
    """Drei Brüche, gemischte Vorzeichen"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    nen = M(Integer(k + 2), ((v2, 1),))
    if st == 1:
        return b50("++", [B(M(Integer(2), ((v1, 1),)), nen),
                          B(M(Integer(3), ((v1, 1),)), nen)])
    if st == 2:
        return b50("+-", [B(M(Integer(7), ((v1, 1),)), nen),
                          B(M(Integer(2), ((v1, 1),)), nen)])
    return b50("+-+", [B(M(Integer(9), ((v1, 1),)), nen),
                       B(M(Integer(4), ((v1, 1),)), nen),
                       B(M(Integer(2), ((v1, 1),)), nen)])


BF50_11 = Bauform("BF11", "Drei Brüche, gemischte Vorzeichen",
    bereiche=BEREICH, bauen=bf50_11, filter=ZWEI)


def bf50_12(p):
    """Zahl und Variable im Zähler gemischt"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    nen = M(Integer(k), ((v2, 1),))
    z1 = Su("++", (M(Integer(2), ((v1, 1),)), M(Integer(k))))
    z2 = Su("+-", (M(Integer(1), ((v1, 1),)), M(Integer(k))))
    if st == 3:
        return b50("++-", [B(z1, nen), B(z2, nen),
                           B(M(Integer(1), ((v1, 1),)), nen)])
    if st == 2:
        return b50("+-", [B(z1, nen), B(z2, nen)])
    return b50("++", [B(z1, nen), B(z2, nen)])


BF50_12 = Bauform("BF12", "Zahl und Variable im Zähler gemischt",
    bereiche=BEREICH, bauen=bf50_12, filter=ZWEI)


S50 = Schablone(
    nr="S50", titel="Bruchterme addieren bei gleichem Nenner",
    lektionen="14.6 – 14.7", erhebung="5a",
    anleitung=ANLEITUNG,
    levelachse="Struktur des Zählers",
    bauformen=[BF50_1, BF50_2, BF50_3, BF50_4, BF50_5, BF50_6,
               BF50_7, BF50_8, BF50_9, BF50_10, BF50_11, BF50_12],
    kernidee=("Bei gleichem Nenner werden nur die Zähler verrechnet — der "
              "Nenner bleibt stehen. Ein Minus vor einem Bruch gilt für den "
              "ganzen Zähler."),
)


# ══════════════════════════════════════════════════════════════════════════
# S51 · Multiplizieren, dividieren, Doppelbruch   (14.9 – 14.11)
# ══════════════════════════════════════════════════════════════════════════

def b51(teile, ops, extra=()):
    """Brüche, verbunden mit · oder :"""
    frage = kette(teile, ops)
    wert = sympify(teile[0].wert)
    for i, op in enumerate(ops):
        rechts = sympify(teile[i + 1].wert)
        wert = wert / rechts if op == ":" else wert * rechts
    wert = cancel(wert)
    z1 = sympify(teile[0].zaehler.wert)
    z2 = sympify(teile[1].zaehler.wert)
    n1 = sympify(teile[0].nenner.wert)
    n2 = sympify(teile[1].nenner.wert)
    if wert == 0:
        #: Ein Faktor ist null. Fast jeder gerechnete Kandidat waere dann
        #: auch null und fiele beim Sieben weg — darum hier ein eigener,
        #: fester Katalog.
        katalog = list(extra) + [
            F("eins_statt_null", Integer(1),
              "Sobald ein Faktor null ist, ist das ganze Produkt null."),
            F("zweiter_bruch", cancel(z2 / n2),
              "Der zweite Bruch spielt keine Rolle mehr — null mal "
              "irgendetwas bleibt null."),
            F("minus_eins_null", Integer(-1),
              "Null bleibt null, unabhaengig vom Vorzeichen."),
            F("nenner_null", cancel(n1 * n2),
              "Nur der Zaehler entscheidet: steht dort null, ist alles "
              "null — der Nenner spielt keine Rolle."),
            F("zwei_null", Integer(2),
              "Null mal irgendetwas ergibt null."),
        ]
        return bau(frage, wert, katalog, TIPPS51)
    katalog = list(extra) + [
        F("vorzeichen_51", cancel(-wert),
          "Zähl die Minuszeichen noch einmal."),
        F("kehrwert_51", cancel(1 / wert) if wert != 0 else Integer(1),
          "Geteilt durch einen Bruch heisst mal den KEHRWERT — Zähler und "
          "Nenner des zweiten Bruchs werden getauscht."),
        F("nicht_getauscht",
          cancel(sympify(teile[0].wert) * sympify(teile[1].wert))
          if ops and ops[0] == ":" else cancel(
              sympify(teile[0].wert) / sympify(teile[1].wert)),
          "Beim Dividieren wird der zweite Bruch umgedreht, beim "
          "Multiplizieren nicht."),
        F("nur_erster_51", cancel(sympify(teile[0].wert)),
          "Beide Brüche zählen mit."),
        F("nur_zweiter_51", cancel(sympify(teile[1].wert)),
          "Beide Brüche zählen mit."),
        F("quadriert", cancel(wert * wert),
          "Jeder Faktor kommt genau einmal vor."),
        F("nur_zaehler", cancel(z1 * z2),
          "Auch die Nenner werden multipliziert, nicht nur die Zaehler."),
        F("nenner_vertauscht", cancel(z1 * n2 / (n1 * z2))
          if z2 != 0 else Integer(2),
          "Beim Multiplizieren wird NICHT umgedreht — das gilt nur beim "
          "Dividieren."),
        F("nenner_produkt", cancel(n1 * n2),
          "Der Nenner steht unter dem Bruchstrich, nicht davor."),
    ]
    return bau(frage, wert, katalog, TIPPS51, schritte=[
        ("Prüfen: wird multipliziert oder dividiert?", frage),
        ("Beim Dividieren den zweiten Bruch umdrehen",
         "aus : wird · mit dem Kehrwert"),
        ("Zähler mal Zähler, Nenner mal Nenner, dann kürzen",
         _als_text(wert)),
    ])


def bf51_1(p):
    """Produkt zweier Bruchterme:  (8a/(3b)) · (9bc/(4a))"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        t1 = B(M(Integer(6), ((v1, 1), (v2, 1))), M(Integer(5), ((v3, 1),)))
        t2 = B(M(Integer(10), ((v3, 2),)), M(Integer(3), ((v1, 1),)))
    elif st == 2:
        t1 = B(M(Integer(8), ((v1, 1),)), M(Integer(3), ((v2, 1),)))
        t2 = B(M(Integer(9), ((v2, 1), (v3, 1))), M(Integer(4), ((v1, 1),)))
    else:
        t1 = B(M(Integer(2), ((v1, 1),)), M(Integer(3), ((v2, 1),)))
        t2 = B(M(Integer(3), ((v2, 1),)), M(Integer(2), ((v1, 1),)))
    return b51([t1, t2], ["·"])


BF51_1 = Bauform("BF1", "Produkt zweier Bruchterme",
    bereiche=BEREICH, bauen=bf51_1, filter=DREI)


def bf51_2(p):
    """Division über den Kehrwert:  (8b/(9a)) : (4a/(3b))

    Auf Level B steht Erhebungsaufgabe 5c im Wortlaut, Ergebnis 2b²/(3a²).
    """
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    if st == 3:
        t1 = B(M(Integer(12), ((v1, 1), (v2, 1))), M(Integer(5), ((v3, 1),)))
        t2 = B(M(Integer(4), ((v1, 1),)), M(Integer(15), ((v3, 1),)))
    elif st == 2:
        t1 = B(M(Integer(8), ((v2, 1),)), M(Integer(9), ((v1, 1),)))
        t2 = B(M(Integer(4), ((v1, 1),)), M(Integer(3), ((v2, 1),)))
    else:
        t1 = B(M(Integer(1), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v3, 1),)), M(Integer(2)))
    return b51([t1, t2], [":"])


BF51_2 = Bauform("BF2", "Division über den Kehrwert",
    bereiche=BEREICH, bauen=bf51_2, filter=DREI)


def bf51_3(p):
    """Bruch mal ganzer Term:  (2/(x+1)) · (x+1)"""
    v1, k, st = p["v1"], p["k"], p["stufe"]
    if st == 3:
        t1 = B(M(Integer(3), ((v1, 1),)),
               Su("+-", (M(Integer(1), ((v1, 2),)), M(Integer(k * k)))))
        t2 = B(Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(k)))),
               M(Integer(1)))
    elif st == 2:
        t1 = B(M(Integer(5)),
               Su("+-", (M(Integer(1), ((v1, 2),)), M(Integer(1)))))
        t2 = B(Su("+-", (M(Integer(1), ((v1, 1),)), M(Integer(1)))),
               M(Integer(1)))
    else:
        t1 = B(M(Integer(2)),
               Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(1)))))
        t2 = B(Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(1)))),
               M(Integer(1)))
    return b51([t1, t2], ["·"])


BF51_3 = Bauform("BF3", "Bruch mal ganzer Term",
    bereiche=BEREICH, bauen=bf51_3, filter=STANDARD)


def bf51_4(p):
    """Vorzeichenfall beim Kürzen:  ((a−1)/a) · (a/(1−a))  →  −1"""
    v1, v2, f, st = p["v1"], p["v2"], p["f"], p["stufe"]
    if st == 3:
        t1 = B(Su("+-", (M(Integer(2), ((v1, 1),)), M(Integer(6)))),
               M(Integer(5), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)),
               Su("+-", (M(Integer(3)), M(Integer(1), ((v1, 1),)))))
    elif st == 2:
        t1 = B(Su("+-", (M(Integer(1), ((v1, 1),)), M(Integer(1)))),
               M(Integer(18), ((v1, 1),)))
        t2 = B(M(Integer(12), ((v1, 2),)),
               Su("+-", (M(Integer(1)), M(Integer(1), ((v1, 1),)))))
    else:
        t1 = B(Su("+-", (M(Integer(1), ((v1, 1),)), M(Integer(1)))),
               M(Integer(1), ((v1, 1),)))
        t2 = B(M(Integer(1), ((v1, 1),)),
               Su("+-", (M(Integer(1)), M(Integer(1), ((v1, 1),)))))
    return b51([t1, t2], ["·"])


BF51_4 = Bauform("BF4", "Vorzeichenfall beim Kürzen",
    bereiche=BEREICH, bauen=bf51_4, filter=ZWEI)


def bf51_5(p):
    """Division durch einen ganzen Term:  ((x−2)/3) : (2−x)  →  −1/3"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    g = 1 if st == 1 else (2 if st == 2 else 3)
    t1 = B(Su("+-", (M(Integer(g), ((v1, 1),)), M(Integer(g * k)))),
           M(Integer(3 * f)))
    if st == 3:
        #: Auf C hat der Divisor selbst einen Zahlfaktor — ein Stueck mehr
        #: im Aufbau, nicht bloss andere Zahlen.
        t2 = B(Su("+-", (M(Integer(2 * k)), M(Integer(2), ((v1, 1),)))),
               M(Integer(2)))
    else:
        t2 = B(Su("+-", (M(Integer(k)), M(Integer(1), ((v1, 1),)))),
               M(Integer(1)))
    return b51([t1, t2], [":"])


BF51_5 = Bauform("BF5", "Division durch einen ganzen Term",
    bereiche=BEREICH, bauen=bf51_5, filter=STANDARD)


def bf51_6(p):
    """Doppelbruch:  (1/2) / (1/3)  →  3/2"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        t1 = B(M(Integer(1)), M(Integer(1), ((v1, 1),)))
        t2 = B(M(Integer(1)), M(Integer(1), ((v2, 1),)))
    elif st == 2:
        t1 = B(M(Integer(1)), M(Integer(k), ((v1, 1),)))
        t2 = B(M(Integer(1)), M(Integer(k + 1)))
    else:
        t1 = B(M(Integer(1)), M(Integer(f)))
        t2 = B(M(Integer(1)), M(Integer(f + 1)))
    return b51([t1, t2], [":"])


BF51_6 = Bauform("BF6", "Doppelbruch",
    bereiche=BEREICH, bauen=bf51_6, filter=ZWEI)


def bf51_7(p):
    """Alles kürzt sich bis auf wenig weg:  (a/b) · (b/a)  →  1"""
    v1, v2, st = p["v1"], p["v2"], p["stufe"]
    if st == 3:
        t1 = B(M(Integer(1), ((v1, 3),)), M(Integer(1), ((v2, 2),)))
        t2 = B(M(Integer(1), ((v2, 3),)), M(Integer(1), ((v1, 2),)))
    elif st == 2:
        t1 = B(M(Integer(1), ((v1, 2),)), M(Integer(1), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(1), ((v1, 1),)))
    else:
        t1 = B(M(Integer(1), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(1), ((v1, 1),)))
    return b51([t1, t2], ["·"])


BF51_7 = Bauform("BF7", "Alles kürzt sich bis auf wenig weg",
    bereiche=BEREICH, bauen=bf51_7, filter=ZWEI)


def bf51_8(p):
    """Sonderfall: ein Faktor ist null:  0 · (a/b)"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    k = p["k"]
    if st == 1:
        #: (0/k) · (a/b)  —  der Faktor null steht vorne. Der Nenner ist
        #: bewusst nicht 1: sonst faellt ein Katalogeintrag mit einem
        #: anderen zusammen.
        t1 = B(M(Integer(0)), M(Integer(k)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(1), ((v3, 1),)))
    elif st == 2:
        #: (0/x) · (y/z)  —  null steht im Zaehler des ersten Bruchs
        t1 = B(M(Integer(0)), M(Integer(1), ((v1, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(1), ((v3, 1),)))
    else:
        #: (0 · x)/(k·y) · (z/x)  —  null als Faktor im Zaehler
        t1 = B(M(Integer(0)), M(Integer(k), ((v1, 1), (v2, 1))))
        t2 = B(M(Integer(1), ((v3, 2),)), M(Integer(1), ((v1, 1),)))
    return b51([t1, t2], ["·"], extra=[
        F("nicht_null_51", Integer(1),
          "Sobald ein Faktor null ist, ist das ganze Produkt null."),
        F("zweiter_geblieben", cancel(sympify(t2.wert)),
          "Der zweite Bruch spielt keine Rolle mehr — null mal irgendetwas "
          "ist null."),
    ])


BF51_8 = Bauform("BF8", "Sonderfall: ein Faktor ist null",
    bereiche=BEREICH, bauen=bf51_8, filter=[kopfrechenbar, fuenf, klein,
                                            verschieden("v1", "v2", "v3")])


def bf51_9(p):
    """Sonderfall: das Ergebnis ist eins"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        t1 = B(M(Integer(k), ((v1, 2), (v2, 1))), M(Integer(1), ((v2, 2),)))
        t2 = B(M(Integer(1), ((v2, 2),)), M(Integer(k), ((v1, 2), (v2, 1))))
    elif st == 2:
        t1 = B(M(Integer(k), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(k), ((v1, 1),)))
    else:
        t1 = B(M(Integer(1), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
        t2 = B(M(Integer(1), ((v2, 1),)), M(Integer(1), ((v1, 1),)))
    return b51([t1, t2], ["·"], extra=[
        F("null_51", Integer(0),
          "Ein Bruch mal seinem Kehrwert ergibt eins, nicht null."),
    ])


BF51_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist eins",
    bereiche=BEREICH, bauen=bf51_9, filter=[kopfrechenbar, fuenf, klein,
                                            verschieden("v1", "v2")])


def bf51_10(p):
    """Drei Faktoren"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    t1 = B(M(Integer(2), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
    t2 = B(M(Integer(3), ((v2, 1),)), M(Integer(1), ((v3, 1),)))
    t3 = B(M(Integer(1), ((v3, 1),)), M(Integer(1)))
    if st == 1:
        return b51([t1, t2], ["·"])
    if st == 2:
        return b51([t1, t2, t3], ["·", "·"])
    return b51([t1, t2, t3], ["·", ":"])


BF51_10 = Bauform("BF10", "Drei Faktoren",
    bereiche=BEREICH, bauen=bf51_10, filter=DREI)


def bf51_11(p):
    """Potenzen in Zähler und Nenner"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    e = st + 1
    t1 = B(M(Integer(k), ((v1, e),)), M(Integer(1), ((v2, 1),)))
    if st == 3:
        #: Auf C kommt eine dritte Variable dazu, auf B ein Koeffizient.
        t2 = B(M(Integer(1), ((v2, 2), (p["v3"], 1))),
               M(Integer(1), ((v1, 1),)))
    elif st == 2:
        t2 = B(M(Integer(k), ((v2, 2),)), M(Integer(1), ((v1, 1),)))
    else:
        t2 = B(M(Integer(1), ((v2, 2),)), M(Integer(1), ((v1, 1),)))
    return b51([t1, t2], ["·"])


BF51_11 = Bauform("BF11", "Potenzen in Zähler und Nenner",
    bereiche=BEREICH, bauen=bf51_11, filter=DREI)


def bf51_12(p):
    """Division mit Zahlen und Variablen gemischt"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    t1 = B(M(Integer(f * k), ((v1, 1),)), M(Integer(k), ((v2, 1),)))
    if st == 3:
        t2 = B(M(Integer(f), ((v1, 1),)), M(Integer(1), ((v2, 2),)))
    elif st == 2:
        t2 = B(M(Integer(f), ((v1, 1),)), M(Integer(1), ((v2, 1),)))
    else:
        t2 = B(M(Integer(f)), M(Integer(1), ((v2, 1),)))
    return b51([t1, t2], [":"])


BF51_12 = Bauform("BF12", "Division mit Zahlen und Variablen gemischt",
    bereiche=BEREICH, bauen=bf51_12, filter=ZWEI)


S51 = Schablone(
    nr="S51", titel="Multiplizieren, dividieren, Doppelbruch",
    lektionen="14.9 – 14.11", erhebung="5c",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Verknüpfung",
    bauformen=[BF51_1, BF51_2, BF51_3, BF51_4, BF51_5, BF51_6,
               BF51_7, BF51_8, BF51_9, BF51_10, BF51_11, BF51_12],
    kernidee=("Beim Multiplizieren mal man Zähler mit Zähler und Nenner mit "
              "Nenner. Geteilt durch einen Bruch heisst mal den Kehrwert."),
)
