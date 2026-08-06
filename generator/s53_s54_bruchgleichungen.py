# -*- coding: utf-8 -*-
"""
S53 · Jeden Summanden mit dem Hauptnenner mal   (Lektion  15.3)
S54 · Term im Zähler, zwei Brüche gleich null   (Lektionen 15.4 – 15.5)

    «Löse die Gleichung. Gib nur den Wert von x an.»
    x/2 − 1 = x/4        x − 1 − x/3 = 1        (x+1)/2 = 3
    (x+1)/2 + (x−1)/2 = 1

**Erhebungsaufgabe 6b** hängt an 15.3 und ist S53/BF1: der bruchfreie
Summand sieht nicht nach einem Bruch aus und wird beim Multiplizieren
vergessen. **Erhebungsaufgabe 6a** hängt an 15.5 und ist S54.

LEVELACHSE (Teil 2):

    S53   Anzahl bruchfreier Summanden   keiner → einer → zwei
    S54   Struktur der Zähler            Zahl → Term → Term mit Koeffizient

Bausteine aus `s15_bruchgleichungen` und `s45_gleichungen`.
"""
from __future__ import annotations

from sympy import Integer, Rational

from .s45_gleichungen import ANLEITUNG, F, X, Z, _sammeln
from .s46_s47_klammern import (KL, SONDER, bau, fehler_eindeutig, fuenf,
                               kopfrechenbar, loesbar, nicht_null, stimmt)
from .s15_bruchgleichungen import BZ, TIPPS, XB, ZB, bg
from .qualitaet import brueche_gekuerzt
from .schablone import Bauform, Schablone

STANDARD = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
            nicht_null,
            # Verhindert «x/2 = 3/6» und «2/2 − (1/4 − x) + 1»: die Ziehung
            # würfelt Zähler und Nenner unabhängig, und ungekürzte Brüche in
            # der FRAGE stehen in keinem Lehrmittel.
            brueche_gekuerzt]

BEREICH = {
    "A": {"n1": [2, 3], "n2": [4, 6], "k": [1, 2, 3], "stufe": [1]},
    "B": {"n1": [2, 3], "n2": [4, 6], "k": [2, 3, 4], "stufe": [2]},
    "C": {"n1": [3, 2], "n2": [6, 4], "k": [1, 2, 5], "stufe": [3]},
}


def vergessen(links, rechts, hn):
    """Der Fehler, an dem Lektion 15.3 hängt.

    Wer `x/2 − 1 = x/4` mit 4 malnimmt und die −1 stehen lässt, rechnet
    `2x − 1 = x` statt `2x − 4 = x`. Der Eintrag wird aus genau dieser
    unterlassenen Multiplikation gerechnet.
    """
    al, kl = _sammeln(*links)
    ar, kr = _sammeln(*rechts)
    if al == ar:
        return None
    #: Die bruchfreien Summanden wurden NICHT mit hn malgenommen.
    ganz_l = sum((g.konstante if zn == "+" else -g.konstante)
                 for zn, g in zip(*links) if isinstance(g, Z))
    ganz_r = sum((g.konstante if zn == "+" else -g.konstante)
                 for zn, g in zip(*rechts) if isinstance(g, Z))
    if ganz_l == 0 and ganz_r == 0:
        return None
    neu_kl = kl - ganz_l + Rational(ganz_l, hn)
    neu_kr = kr - ganz_r + Rational(ganz_r, hn)
    return Rational(neu_kr - neu_kl, al - ar)


def b53(links, rechts, hn, extra=()):
    """Bruchgleichung mit Hauptnenner `hn`.

    Drei Eintraege gelten bei JEDER Bruchgleichung und stehen darum hier:
    der Hauptnenner als Loesung verwechselt, am Schluss nicht
    zurueckgeteilt, und den Hauptnenner zur Loesung addiert.
    """
    from .s45_gleichungen import loesen
    zusatz = list(extra)
    w = vergessen(links, rechts, hn)
    if w is not None:
        zusatz.append(F("summand_vergessen", w,
            f"Beim Multiplizieren mit {hn} muss JEDER Summand mit — auch "
            f"der, der gar kein Bruch ist."))
    l = loesen(links, rechts)
    if l is not None:
        zusatz += [
            F("hauptnenner_als_loesung", Integer(hn),
              f"{hn} ist der Hauptnenner, mit dem multipliziert wird — nicht "
              f"der Wert von x."),
            F("nicht_zurueckgeteilt", l * hn,
              f"Nach dem Multiplizieren mit {hn} muss am Schluss noch durch "
              f"den Koeffizienten vor dem x geteilt werden."),
            F("hauptnenner_addiert", l + hn,
              "Der Hauptnenner wird zum Multiplizieren gebraucht, nicht zum "
              "Addieren."),
        ]
    return bg(links, rechts, extra=zusatz)


# ══════════════════════════════════════════════════════════════════════════
# S53 · Jeden Summanden mit dem Hauptnenner malnehmen   (15.3)
# ══════════════════════════════════════════════════════════════════════════

def bf53_1(p):
    """Bruchfreier Summand muss mitgenommen werden:  x/2 − 1 = x/4

    Das ist Erhebungsaufgabe 6b und die Bauform, an der die Lektion hängt.
    """
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    #: DIE ACHSE VON S53: wie viele bruchfreie Summanden links stehen.
    #: A keiner (die Zahl steht rechts), B einer, C zwei.
    if st == 3:
        links = ("+--", (XB(n1), Z(k), Z(1)))
        rechts = ("+", (XB(n2),))
    elif st == 2:
        links = ("+-", (XB(n1), Z(k)))
        rechts = ("+", (XB(n2),))
    else:
        links = ("+", (XB(n1),))
        rechts = ("++", (XB(n2), Z(k)))
    return b53(links, rechts, n1 * n2)


BF53_1 = Bauform("BF1", "Bruchfreier Summand muss mitgenommen werden",
    bereiche=BEREICH, bauen=bf53_1, filter=STANDARD)


def bf53_2(p):
    """Rechts ein bruchfreier Term mit Variable:  x/2 + 1 = x"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++-", (XB(n1), Z(k), Z(1)))
    elif st == 2:
        links = ("+-", (XB(n1), Z(k)))
    else:
        links = ("++", (XB(n1), Z(k)))
    rechts = ("+", (X(1),))
    return b53(links, rechts, n1)


BF53_2 = Bauform("BF2", "Rechts ein bruchfreier Term mit Variable",
    bereiche=BEREICH, bauen=bf53_2, filter=STANDARD)


def bf53_3(p):
    """Zwei bruchfreie Summanden:  x − 1 − x/3 = 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("+--+", (X(1), Z(k), XB(n1), Z(1)))
    elif st == 2:
        links = ("+--", (X(1), Z(k), XB(n1)))
    else:
        links = ("+-", (X(1), XB(n1)))
    rechts = ("+", (Z(k),))
    return b53(links, rechts, n1)


BF53_3 = Bauform("BF3", "Zwei bruchfreie Summanden",
    bereiche=BEREICH, bauen=bf53_3, filter=STANDARD)


def bf53_4(p):
    """Zusätzlich eine Klammer:  1/2 − (1/3 − x) = 1/4"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-+-", (BZ(1, n1), KL(1, "+-", (BZ(1, n2), X(1))),
                          Z(1), Z(2)))
    elif st == 2:
        links = ("+-+", (BZ(k, n1), KL(1, "+-", (BZ(1, n2), X(1))), Z(1)))
    else:
        links = ("+-", (BZ(1, n1), KL(1, "+-", (BZ(1, n2), X(1)))))
    rechts = ("+", (BZ(1, n2 + 1),))
    return b53(links, rechts, n1 * n2)


BF53_4 = Bauform("BF4", "Zusätzlich eine Klammer",
    bereiche=BEREICH, bauen=bf53_4, filter=STANDARD)


def bf53_5(p):
    """Drei Brüche, rechts eine Zahl:  x/3 − x/6 = 1"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-+--", (XB(n1), XB(n2), XB(n2 * 2), Z(1), Z(2)))
    elif st == 2:
        links = ("+--", (XB(n1), XB(n2), Z(1)))
    else:
        links = ("+-", (XB(n1), XB(n2)))
    al, kl = _sammeln(*links)
    if al == 0:
        links = ("+-", (XB(n1), XB(n1 * 2)))
        al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * n2 * 2 + kl),))
    return b53(links, rechts, n2 * 2)


BF53_5 = Bauform("BF5", "Drei Brüche, rechts eine Zahl",
    bereiche=BEREICH, bauen=bf53_5, filter=STANDARD)


def bf53_6(p):
    """Sonderfall: keine Lösung:  x/2 − x/4 = x/4 + 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    n = n1 * 2
    if st == 3:
        links = ("+--", (XB(n1), XB(n), Z(k)))
        rechts = ("++-", (XB(n), Z(1), Z(k + 1)))
    elif st == 2:
        links = ("+-", (XB(n1), XB(n)))
        rechts = ("+-", (XB(n), Z(k)))
    else:
        links = ("+-", (XB(n1), XB(n)))
        rechts = ("++", (XB(n), Z(k)))
    return bg(links, rechts, art="keine")


BF53_6 = Bauform("BF6", "Sonderfall: keine Lösung",
    bereiche=BEREICH, bauen=bf53_6, filter=SONDER)


def bf53_7(p):
    """Term im Zähler eines Bruchs:  (x+1)/2 = 3"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-", (ZB("++", (X(1), Z(k)), n1), Z(1)))
    elif st == 2:
        links = ("+", (ZB("+-", (X(1), Z(k)), n1),))
    else:
        links = ("+", (ZB("++", (X(1), Z(k)), n1),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * (n1 * 2) + kl),))
    return b53(links, rechts, n1)


BF53_7 = Bauform("BF7", "Term im Zähler eines Bruchs",
    bereiche=BEREICH, bauen=bf53_7, filter=STANDARD)


def bf53_8(p):
    """Drei Brüche mit x, einer rechts:  x/2 + x/3 = x/6 + 2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    a1, a2, a3 = 2, 3, 6
    if st == 3:
        links = ("++--", (XB(a1), XB(a2), Z(k), Z(1)))
    elif st == 2:
        links = ("++-", (XB(a1), XB(a2), Z(k)))
    else:
        links = ("++", (XB(a1), XB(a2)))
    al, kl = _sammeln(*links)
    ar = Rational(1, a3)
    rechts = ("++", (XB(a3), Z((al - ar) * 6 + kl)))
    return b53(links, rechts, 6)


BF53_8 = Bauform("BF8", "Drei Brüche mit x, einer rechts",
    bereiche=BEREICH, bauen=bf53_8, filter=STANDARD)


def bf53_9(p):
    """Sonderfall: die Lösung ist null:  x/5 = 0"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++-", (XB(n1), Z(k), Z(k)))
        rechts = ("+", (Z(0),))
    elif st == 2:
        links = ("++", (XB(n1), Z(k)))
        rechts = ("+", (Z(k),))
    else:
        links = ("+", (XB(n1),))
        rechts = ("+", (Z(0),))
    return bg(links, rechts, loesung=0, extra=[
        F("nenner_53", Integer(n1), f"{n1} ist der Nenner, nicht die Lösung."),
        F("eins_53", Integer(1), "Setz null ein — beide Seiten stimmen."),
        F("k_53", Integer(k), "Die Zahlen der Gleichung sind nicht x."),
        F("minus_53", Integer(-1), "Nur null passt."),
        F("bruch_53", Rational(1, n1), "Der Nenner ist nicht die Lösung."),
    ])


BF53_9 = Bauform("BF9", "Sonderfall: die Lösung ist null",
    bereiche=BEREICH, bauen=bf53_9,
    filter=[loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf])


def bf53_10(p):
    """Negativer Bruch:  −x/3 + 1 = 2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("-++", (XB(n1), Z(k), Z(1)))
    elif st == 2:
        links = ("-+", (XB(n1), Z(k)))
    else:
        links = ("-", (XB(n1),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * n1 * 3 + kl),))
    return b53(links, rechts, n1)


BF53_10 = Bauform("BF10", "Negativer Bruch",
    bereiche=BEREICH, bauen=bf53_10, filter=STANDARD)


def bf53_11(p):
    """Drei Brüche desselben x:  x/2 + x/3 + x/6 = 6"""
    k, st = p["k"], p["stufe"]
    if st == 3:
        links = ("++--", (XB(2), XB(3), XB(6), Z(k)))
    elif st == 2:
        links = ("++-", (XB(2), XB(3), XB(6)))
    else:
        links = ("+++", (XB(2), XB(3), XB(6)))
    al, kl = _sammeln(*links)
    #: mal 12 statt mal 6 — sonst faellt die Loesung mit dem Hauptnenner
    #: zusammen, und zwei Katalogeintraege heben sich gegenseitig auf.
    rechts = ("+", (Z(al * 12 + kl),))
    return b53(links, rechts, 6)


BF53_11 = Bauform("BF11", "Drei Brüche desselben x",
    bereiche=BEREICH, bauen=bf53_11, filter=STANDARD)


def bf53_12(p):
    """Die Lösung ist ein Bruch:  x/2 = 3/4"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-", (XB(n1), Z(1)))
        rechts = ("+", (BZ(3, n2),))
    elif st == 2:
        links = ("+", (XB(n1),))
        rechts = ("+-", (BZ(3, n2), BZ(1, n2)))
    else:
        links = ("+", (XB(n1),))
        rechts = ("+", (BZ(3, n2),))
    return b53(links, rechts, n1 * n2)


BF53_12 = Bauform("BF12", "Die Lösung ist ein Bruch",
    bereiche=BEREICH, bauen=bf53_12, filter=STANDARD)


S53 = Schablone(
    nr="S53", titel="Jeden Summanden mit dem Hauptnenner malnehmen",
    lektionen="15.3", erhebung="6b",
    anleitung=ANLEITUNG,
    levelachse="Anzahl bruchfreier Summanden",
    bauformen=[BF53_1, BF53_2, BF53_3, BF53_4, BF53_5, BF53_6,
               BF53_7, BF53_8, BF53_9, BF53_10, BF53_11, BF53_12],
    kernidee=("Beim Multiplizieren mit dem Hauptnenner muss JEDER Summand "
              "mit — auch der, der gar kein Bruch ist."),
)


# ══════════════════════════════════════════════════════════════════════════
# S54 · Term im Zähler, zwei Brüche gleich null   (15.4 – 15.5)
# ══════════════════════════════════════════════════════════════════════════

def _zb(mus, koeff, konst, nenner):
    """(kx + c)/n  —  der Zähler als ganzer Term über dem Bruchstrich."""
    return ZB(mus, (X(koeff), Z(konst)), nenner)


def zst(p, konst, nenner, minus=False):
    """Der Zähler in der Bauart der Stufe — das IST die Levelachse von S54.

        A   (x + 3)/n        Zähler aus x und einer Zahl
        B   (x − 3)/n        ein Minus im Zähler
        C   (2x + 3)/n       ein Koeffizient vor dem x

    Ohne diesen Unterschied haetten A und B denselben Aufbau, und der
    Testlauf beanstandet das zu Recht.
    """
    st = p["stufe"]
    koeff = 2 if st == 3 else 1
    mus = "+-" if (st == 2) != minus else "++"
    return ZB(mus, (X(koeff), Z(konst)), nenner)


def bf54_1(p):
    """Zwei Brüche, rechts steht null:  (x+1)/2 + (x−1)/2 = 0"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    #: Die beiden Zaehler duerfen sich nicht gegenseitig aufheben —
    #: sonst ist die Loesung immer null, und das ist BF8.
    links = ("++", (zst(p, k, n1), zst(p, k + 2, n1, minus=True)))
    rechts = ("+", (Z(0),))
    return b53(links, rechts, n1)


BF54_1 = Bauform("BF1", "Zwei Brüche, rechts steht null",
    bereiche=BEREICH, bauen=bf54_1, filter=STANDARD)


def bf54_2(p):
    """Zwei Brüche, rechts eine Zahl:  (x+1)/2 + (x−1)/2 = 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    links = ("++", (zst(p, k, n1), zst(p, k + 1, n1, minus=True)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * 2 + kl),))
    return b53(links, rechts, n1)


BF54_2 = Bauform("BF2", "Zwei Brüche, rechts eine Zahl",
    bereiche=BEREICH, bauen=bf54_2, filter=STANDARD)


def bf54_3(p):
    """Derselbe Term in beiden Zählern, mit Plus:
       (y−1)/2 + (y−1)/3 = 5/6"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    links = ("++", (zst(p, k, n1), zst(p, k, n2)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * 2 + kl),))
    return b53(links, rechts, n1 * n2)


BF54_3 = Bauform("BF3", "Derselbe Term in beiden Zählern, mit Plus",
    bereiche=BEREICH, bauen=bf54_3, filter=STANDARD)


def bf54_4(p):
    """Derselbe Term mit Minus — ausklammerbar:
       (x−2)/2 − (x−2)/3 = 1/6"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    links = ("+-", (zst(p, k, n1), zst(p, k, n2)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * 3 + kl),))
    return b53(links, rechts, n1 * n2)


BF54_4 = Bauform("BF4", "Derselbe Term mit Minus — ausklammerbar",
    bereiche=BEREICH, bauen=bf54_4, filter=STANDARD)


def bf54_5(p):
    """Verschiedene Zähler, Minus dazwischen:
       (a−1)/3 − (a+1)/6 = 1/6"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    n2 = n1 * 2
    links = ("+-", (zst(p, k, n1), zst(p, k, n2, minus=True)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * 4 + kl),))
    return b53(links, rechts, n2)


BF54_5 = Bauform("BF5", "Verschiedene Zähler, Minus dazwischen",
    bereiche=BEREICH, bauen=bf54_5, filter=STANDARD)


def bf54_6(p):
    """Sonderfall: keine Lösung:  (x+1)/2 = (x+2)/2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    links = ("+", (zst(p, k, n1),))
    rechts = ("+", (zst(p, k + 1, n1),))
    if st == 3:
        links = ("++", (zst(p, k, n1), Z(1)))
        rechts = ("++", (zst(p, k + 1, n1), Z(1)))
    return bg(links, rechts, art="keine")


BF54_6 = Bauform("BF6", "Sonderfall: keine Lösung",
    bereiche=BEREICH, bauen=bf54_6, filter=SONDER)


def bf54_7(p):
    """Sonderfall: allgemeingültig:  (x+1)/2 = (2x+2)/4"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    z = zst(p, k, n1)
    kk, cc = z.glieder[0].koeff, z.glieder[1].konstante
    vz = 1 if z.muster[1] == "+" else -1
    if st == 3:
        rechts = ("+", (ZB("++" if vz > 0 else "+-",
                            (X(kk * 3), Z(cc * 3)), n1 * 3),))
    else:
        rechts = ("+", (ZB("++" if vz > 0 else "+-",
                            (X(kk * 2), Z(cc * 2)), n1 * 2),))
    links = ("+", (z,))
    return bg(links, rechts, art="alle")


BF54_7 = Bauform("BF7", "Sonderfall: allgemeingültig",
    bereiche=BEREICH, bauen=bf54_7, filter=SONDER)


def bf54_8(p):
    """Ein Bruch gleich null:  (x+3)/2 = 0"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    links = ("+", (zst(p, k, n1),))
    rechts = ("+", (Z(0),))
    return b53(links, rechts, n1)


BF54_8 = Bauform("BF8", "Ein Bruch gleich null",
    bereiche=BEREICH, bauen=bf54_8, filter=STANDARD)


def bf54_9(p):
    """Zwei Brüche gleichgesetzt:  (x+1)/3 = (x−1)/2"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    links = ("+", (zst(p, k, n1),))
    rechts = ("+", (zst(p, k, n2, minus=True),))
    return b53(links, rechts, n1 * n2)


BF54_9 = Bauform("BF9", "Zwei Brüche gleichgesetzt",
    bereiche=BEREICH, bauen=bf54_9, filter=STANDARD)


def bf54_10(p):
    """Minus im Zähler:  (−x+1)/2 = 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-", (ZB("-+", (X(1), Z(k)), n1), Z(1)))
    elif st == 2:
        links = ("+", (ZB("--", (X(1), Z(k)), n1),))
    else:
        links = ("+", (ZB("-+", (X(1), Z(k)), n1),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * 2 + kl),))
    return b53(links, rechts, n1)


BF54_10 = Bauform("BF10", "Minus im Zähler",
    bereiche=BEREICH, bauen=bf54_10, filter=STANDARD)


def bf54_11(p):
    """Zwei Brüche, kleines Ergebnis rechts:
       (x+1)/2 − (x−1)/3 = 1/6"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    n2 = n1 + 1
    links = ("+-", (zst(p, k, n1), zst(p, k, n2, minus=True)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * (-4) + kl),))
    return b53(links, rechts, n1 * n2)


BF54_11 = Bauform("BF11", "Zwei Brüche, kleines Ergebnis rechts",
    bereiche=BEREICH, bauen=bf54_11, filter=STANDARD)


def bf54_12(p):
    """Verschiedene Nenner, Zähler mit Koeffizient:
       (x+1)/2 = (x+3)/4"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    n2 = n1 * 2
    links = ("+", (zst(p, k, n1),))
    rechts = ("+", (zst(p, k + 2, n2),))
    return b53(links, rechts, n2)


BF54_12 = Bauform("BF12", "Verschiedene Nenner, Zähler mit Koeffizient",
    bereiche=BEREICH, bauen=bf54_12, filter=STANDARD)


S54 = Schablone(
    nr="S54", titel="Term im Zähler, zwei Brüche gleich null",
    lektionen="15.4 – 15.5", erhebung="6a",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Zähler",
    bauformen=[BF54_1, BF54_2, BF54_3, BF54_4, BF54_5, BF54_6,
               BF54_7, BF54_8, BF54_9, BF54_10, BF54_11, BF54_12],
    kernidee=("Der Bruchstrich wirkt wie eine Klammer: beim Multiplizieren "
              "mit dem Hauptnenner muss der GANZE Zähler mit, nicht nur sein "
              "erstes Glied."),
)
