# -*- coding: utf-8 -*-
"""
S52 · Gleichung mit einem Bruch, Hauptnenner    (Lektionen 15.1 – 15.2)
S53 · Jeden Summanden mit dem Hauptnenner mal   (Lektion  15.3)
S54 · Term im Zähler, zwei Brüche gleich null   (Lektionen 15.4 – 15.5)

    «Löse die Gleichung. Gib nur den Wert von x an.»
    x/2 = 4        x/4 + x/6 = 5        x/2 − 1 = x/4        (x+1)/2 = 3

Erhebungsaufgabe **6b** hängt an 15.3 (S53/BF1), **6a** an 15.5 (S54).

DAS WORT «JEDEN» STEHT NICHT OHNE GRUND IM LEKTIONSTITEL von 15.3. Wer
`x/2 − 1 = x/4` mit 4 multipliziert, muss auch die −1 mitnehmen: aus −1 wird
−4, nicht −1. Genau dieser Fehler steht als eigener Katalogeintrag in jeder
Bauform dieser drei Schablonen.

LEVELACHSE (Teil 2):

    S52   Struktur der Nenner    ein Bruch → zwei Brüche, teilerfremd →
                                 zwei Brüche mit gemeinsamem Teiler
    S53   Anzahl bruchfreier Summanden   keiner → einer → zwei
    S54   Struktur der Zähler    Zahl → Term → Term mit Koeffizient

Die Bausteine kommen aus `s45_gleichungen` und `s46_s47_klammern`: Glieder,
Seiten, das Lösen ohne `solve` und die drei Antwortarten (Zahl, «keine
Lösung», «jede Zahl») stehen dort schon.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational

from .s45_gleichungen import ANLEITUNG, F, X, Z, _sammeln
from .s46_s47_klammern import (KL, SONDER, bau, fehler_eindeutig, fuenf,
                               ganz, kopfrechenbar, loesbar, nicht_null,
                               reihe, stimmt)
from .qualitaet import brueche_gekuerzt
from .schablone import Bauform, Schablone


# ══════════════════════════════════════════════════════════════════════════
# Zwei Bausteine kommen dazu
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class XB:
    """x über einem Nenner:  x/2   ·   3x/4"""
    nenner: int
    koeff: int = 1

    @property
    def anteil(self):
        return Rational(self.koeff, self.nenner)

    @property
    def konstante(self):
        return 0

    @property
    def text(self) -> str:
        oben = "x" if self.koeff == 1 else f"{self.koeff}x"
        return f"{oben}/{self.nenner}"


@dataclass(frozen=True)
class BZ:
    """Ein Bruch als blosse Zahl:  1/3"""
    zaehler: int
    nenner: int

    @property
    def anteil(self):
        return 0

    @property
    def konstante(self):
        return Rational(self.zaehler, self.nenner)

    @property
    def text(self) -> str:
        return f"{self.zaehler}/{self.nenner}"


@dataclass(frozen=True)
class ZB:
    """Ein ganzer Term über einem Nenner:  (x + 1)/2

    Genau die Form, an der Lektion 15.4 hängt: der Bruchstrich wirkt wie
    eine Klammer, und beim Multiplizieren muss der GANZE Zähler mit.
    """
    muster: str
    glieder: tuple
    nenner: int

    @property
    def _innen(self):
        return _sammeln(self.muster, self.glieder)

    @property
    def anteil(self):
        return Rational(self._innen[0], self.nenner)

    @property
    def konstante(self):
        return Rational(self._innen[1], self.nenner)

    @property
    def text(self) -> str:
        return f"({reihe(self.muster, self.glieder)})/{self.nenner}"


TIPPS = [
    "Multiplizier beide Seiten mit dem Hauptnenner — dann verschwinden alle "
    "Brüche.",
    "JEDER Summand wird mit dem Hauptnenner malgenommen, auch der, der gar "
    "kein Bruch ist.",
    "",
]


def bg(links, rechts, extra=(), **kw):
    kw.setdefault("tipps", TIPPS)
    return bau(links, rechts, extra=extra, **kw)


def hauptnenner_fehler(links, rechts, hn):
    """Der Fehler, an dem Lektion 15.3 hängt: beim Multiplizieren mit dem
    Hauptnenner wurde der bruchfreie Summand vergessen."""
    al, kl = _sammeln(*links)
    ar, kr = _sammeln(*rechts)
    #: Die bruchfreien Glieder blieben stehen, statt mit hn malgenommen zu
    #: werden — dadurch verschiebt sich die Lösung.
    ganz_links = sum(g.konstante for zn, g in zip(*links)
                     if isinstance(g, Z) and zn == "+")
    ganz_links -= sum(g.konstante for zn, g in zip(*links)
                      if isinstance(g, Z) and zn == "-")
    if al == ar:
        return None
    falsch_kl = kl - ganz_links * (hn - 1) / hn
    return Rational(kr - falsch_kl, al - ar)


STANDARD = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
            nicht_null,
            # kein «3/6» und kein «2/2» in der Frage
            brueche_gekuerzt]
GANZ = STANDARD + [ganz]


BEREICH = {
    "A": {"n1": [2, 3], "n2": [3, 4], "k": [1, 3, 4], "stufe": [1]},
    "B": {"n1": [2, 3], "n2": [3, 5], "k": [2, 4, 5], "stufe": [2]},
    "C": {"n1": [4, 6], "n2": [6, 4], "k": [2, 3, 5], "stufe": [3]},
}


# ══════════════════════════════════════════════════════════════════════════
# S52 · Gleichung mit einem Bruch, Hauptnenner    (15.1 – 15.2)
# ══════════════════════════════════════════════════════════════════════════

def bf52_1(p):
    """Ein Bruch, ganze Zahl auf der anderen Seite:  x/2 = 4"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++", (XB(n1), Z(k)))
        rechts = ("+", (Z(k + n1 * 2),))
    elif st == 2:
        links = ("+", (XB(n1, 3),))
        rechts = ("+", (Z(k + 2),))
    else:
        links = ("+", (XB(n1),))
        rechts = ("+", (Z(k + 3),))
    return bg(links, rechts)


BF52_1 = Bauform("BF1", "Ein Bruch, ganze Zahl auf der anderen Seite",
    bereiche=BEREICH, bauen=bf52_1, filter=STANDARD)


def bf52_2(p):
    """Auf beiden Seiten ein Bruch:  x/2 = 1/3"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if st == 3:
        links = ("+", (XB(n1),))
        rechts = ("+-", (BZ(k, n2), BZ(1, n2)))
    elif st == 2:
        #: Auf B steht ein Koeffizient vor dem x — ein Stueck mehr.
        links = ("+", (XB(n1, 3),))
        rechts = ("+", (BZ(k, n2),))
    else:
        links = ("+", (XB(n1),))
        rechts = ("+", (BZ(1, n2),))
    return bg(links, rechts)


BF52_2 = Bauform("BF2", "Auf beiden Seiten ein Bruch",
    bereiche=BEREICH, bauen=bf52_2, filter=STANDARD)


def bf52_3(p):
    """Brüche als Konstanten:  1/2 − x = 1/3"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-+", (BZ(1, n1), X(1), BZ(1, n2)))
        rechts = ("+", (BZ(1, n2),))
    elif st == 2:
        #: Auf B kommt rechts ein zweites Glied dazu.
        links = ("+-", (BZ(k, n1), X(1)))
        rechts = ("++", (BZ(1, n2), Z(1)))
    else:
        links = ("+-", (BZ(1, n1), X(1)))
        rechts = ("+", (BZ(1, n2),))
    return bg(links, rechts)


BF52_3 = Bauform("BF3", "Brüche als Konstanten",
    bereiche=BEREICH, bauen=bf52_3, filter=STANDARD)


def bf52_4(p):
    """Zwei Brüche mit x, teilerfremde Nenner:  x/2 + x/3 = 5"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    if st == 2:
        #: Auf B traegt einer der beiden Brueche einen Koeffizienten.
        links = ("++", (XB(n1, 2), XB(n2)))
    else:
        links = ("++", (XB(n1), XB(n2)))
    al, kl = _sammeln(*links)
    ziel = n1 * n2
    if st == 3:
        links = ("++-", (XB(n1), XB(n2), Z(1)))
        al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * ziel + kl),))
    return bg(links, rechts)


BF52_4 = Bauform("BF4", "Zwei Brüche mit x, teilerfremde Nenner",
    bereiche=BEREICH, bauen=bf52_4, filter=STANDARD)


def bf52_5(p):
    """Ein Bruch und eine ganze Zahl:  x/2 + 1 = 4"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++-", (XB(n1), Z(k), Z(1)))
    elif st == 2:
        links = ("+-", (XB(n1), Z(k)))
    else:
        links = ("++", (XB(n1), Z(k)))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * (n1 * 2) + kl),))
    return bg(links, rechts)


BF52_5 = Bauform("BF5", "Ein Bruch und eine ganze Zahl",
    bereiche=BEREICH, bauen=bf52_5, filter=STANDARD)


def bf52_6(p):
    """Nenner mit gemeinsamem Teiler — das kgV ist kleiner als das Produkt:
       x/4 + x/6 = 5  →  x = 12"""
    st = p["stufe"]
    paare = {1: (4, 6), 2: (6, 9), 3: (4, 10)}
    n1, n2 = paare[st]
    if st == 2:
        #: Auf B ein Minus zwischen den Bruechen.
        links = ("+-", (XB(n1), XB(n2)))
    elif st == 3:
        #: Auf C ein dritter Summand.
        links = ("++-", (XB(n1), XB(n2), Z(2)))
    else:
        links = ("++", (XB(n1), XB(n2)))
    al, kl = _sammeln(*links)
    from sympy import ilcm
    kgv = ilcm(n1, n2)
    if al == 0:
        return bg(("+", (XB(n1),)), ("+", (Z(n1),)))
    rechts = ("+", (Z(al * kgv + kl),))
    return bg(links, rechts, extra=[
        F("kgv_statt_produkt", Integer(n1 * n2),
          f"Der Hauptnenner ist das kgV von {n1} und {n2}, also {kgv} — "
          f"nicht ihr Produkt {n1 * n2}."),
        F("nenner_addiert_15", Integer(n1 + n2),
          "Die Nenner werden nicht addiert. Gesucht ist ihr kleinstes "
          "gemeinsames Vielfaches."),
        F("kgv_als_loesung", Integer(kgv),
          f"{kgv} ist der Hauptnenner, mit dem multipliziert wird — nicht "
          f"die Lösung."),
    ])


BF52_6 = Bauform("BF6", "Nenner mit gemeinsamem Teiler",
    bereiche=BEREICH, bauen=bf52_6, filter=STANDARD)


def bf52_7(p):
    """x-Brüche auf beiden Seiten:  x/2 = x/3 + 1"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    links = ("+", (XB(n1),))
    if st == 3:
        rechts = ("++-", (XB(n2), Z(k), Z(1)))
    elif st == 2:
        #: Auf B traegt der rechte Bruch einen Koeffizienten.
        rechts = ("++", (XB(n2, 2), Z(k)))
    else:
        rechts = ("++", (XB(n2), Z(k)))
    return bg(links, rechts)


BF52_7 = Bauform("BF7", "x-Brüche auf beiden Seiten",
    bereiche=BEREICH, bauen=bf52_7, filter=STANDARD)


def bf52_8(p):
    """Sonderfall: keine Lösung:  x/2 = x/2 + 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    links = ("+", (XB(n1),))
    if st == 3:
        rechts = ("++-", (XB(n1), Z(k + 1), Z(1)))
    elif st == 2:
        rechts = ("+-", (XB(n1), Z(k)))
    else:
        rechts = ("++", (XB(n1), Z(k)))
    return bg(links, rechts, art="keine")


BF52_8 = Bauform("BF8", "Sonderfall: keine Lösung",
    bereiche=BEREICH, bauen=bf52_8, filter=SONDER)


def bf52_9(p):
    """Sonderfall: allgemeingültig:  x/2 = x/2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++", (XB(n1), Z(k)))
        rechts = ("++", (XB(n1), Z(k)))
    elif st == 2:
        links = ("+", (XB(n1, 2),))
        rechts = ("+", (XB(n1, 2),))
    else:
        links = ("+", (XB(n1),))
        rechts = ("+", (XB(n1),))
    return bg(links, rechts, art="alle")


BF52_9 = Bauform("BF9", "Sonderfall: allgemeingültig",
    bereiche=BEREICH, bauen=bf52_9, filter=SONDER)


def bf52_10(p):
    """Sonderfall: die Lösung ist null:  x/3 = 0"""
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
        F("nenner_als_loesung", Integer(n1),
          f"{n1} ist der Nenner, nicht die Lösung."),
        F("eins_15", Integer(1),
          "Setz null ein: beide Seiten stimmen überein."),
        F("konstante_15", Integer(k),
          "Die Zahlen der Gleichung sind nicht die Lösung."),
        F("minus_eins_15", Integer(-1),
          "Nur null macht beide Seiten gleich."),
        F("bruch_15", Rational(1, n1),
          "Der Nenner unter dem x ist nicht die Lösung."),
    ])


BF52_10 = Bauform("BF10", "Sonderfall: die Lösung ist null",
    bereiche=BEREICH, bauen=bf52_10,
    filter=[loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf])


def bf52_11(p):
    """Negativer Koeffizient:  −x/2 = 3"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("-+", (XB(n1), Z(k)))
    elif st == 2:
        links = ("-", (XB(n1, 3),))
    else:
        links = ("-", (XB(n1),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * (n1 * 2) + kl),))
    return bg(links, rechts)


BF52_11 = Bauform("BF11", "Negativer Koeffizient",
    bereiche=BEREICH, bauen=bf52_11, filter=STANDARD)


def bf52_12(p):
    """Viele Summanden mit zwei Nennern"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    if st == 3:
        links = ("++-", (XB(n1), XB(n2), Z(k)))
    elif st == 2:
        links = ("+-", (XB(n1), XB(n2)))
    else:
        links = ("+", (XB(n1),))
    al, kl = _sammeln(*links)
    if al == 0:
        al = Rational(1, n1)
        links = ("+", (XB(n1),))
        kl = 0
    rechts = ("+", (Z(al * (n1 * n2) + kl),))
    return bg(links, rechts)


BF52_12 = Bauform("BF12", "Viele Summanden mit zwei Nennern",
    bereiche=BEREICH, bauen=bf52_12, filter=STANDARD)


S52 = Schablone(
    nr="S52", titel="Gleichung mit einem Bruch, Hauptnenner",
    lektionen="15.1 – 15.2", erhebung="6b",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Nenner",
    bauformen=[BF52_1, BF52_2, BF52_3, BF52_4, BF52_5, BF52_6,
               BF52_7, BF52_8, BF52_9, BF52_10, BF52_11, BF52_12],
    kernidee=("Multipliziere beide Seiten mit dem Hauptnenner — dem kgV "
              "aller Nenner. Dann verschwinden die Brüche, und es bleibt "
              "eine gewöhnliche Gleichung."),
)
