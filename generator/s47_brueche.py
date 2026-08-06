# -*- coding: utf-8 -*-
"""
S47 · Klammern beidseitig, Lösung als Bruch   (Lektionen 13.7 – 13.9)

    «Löse die Gleichung.»
    2x + 1 = 4          →  x = 3/2
    14x = 21            →  x = 3/2   (der Bruch muss gekürzt werden)
    5x + 10(2 − 6x) = 22 − 6(x − 2)   →  x = −2/7      ERHEBUNGSAUFGABE 1a

Damit ist Kapitel 13 bis auf die Gemischt-Lektion 13.10 vollständig und
**Erhebungsaufgabe 1a übbar** — sie steht als BF1 auf Level C im Wortlaut.

Der Unterschied zu S46: hier DARF die Lösung ein Bruch sein, weil 13.9 die
Lektion 2.2 voraussetzt. Der letzte Schritt ist deshalb immer derselbe:
kürzen.

LEVELACHSE (Teil 2): Struktur der Lösung — ganzzahlig, Bruch, gekürzter
Bruch; dazu wie bei S46 die Gliederzahl und die Vorzeichen.

Die Bausteine kommen aus `s45_gleichungen` und `s46_s47_klammern`; hier
kommen nur die Brüche dazu.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational

from korrektur import Zielform
from .s45_gleichungen import ANLEITUNG, F, X, Z, _sammeln
from .s46_s47_klammern import (KL, SONDER, TIPPS47, bau, echter_bruch,
                               fehler_eindeutig, fuenf, ganz, kopfrechenbar,
                               loesbar, stimmt)
from .schablone import Bauform, Schablone


@dataclass(frozen=True)
class BR:
    """Ein Bruch als Koeffizient vor dem x:  (1/2)x"""
    zaehler: int
    nenner: int

    @property
    def anteil(self):
        return Rational(self.zaehler, self.nenner)

    @property
    def konstante(self):
        return 0

    @property
    def text(self) -> str:
        return f"({self.zaehler}/{self.nenner})x"


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
class PROD:
    """Zwei Klammern mal einander:  (x + 1)(x + 2)

    Der x²-Anteil ist immer 1. Die Bauform baut beide Seiten so, dass er
    sich aufhebt — sonst wäre die Gleichung quadratisch und gehörte nicht
    in Kapitel 13.
    """
    a: int
    b: int

    @property
    def anteil(self):
        return self.a + self.b

    @property
    def konstante(self):
        return self.a * self.b

    @property
    def text(self) -> str:
        def klammer(w):
            vz = "+" if w >= 0 else "−"
            return f"(x {vz} {abs(w)})"
        return klammer(self.a) + klammer(self.b)


TIPPS = TIPPS47
BRUCH = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
         echter_bruch]
FREI = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf]

BEREICH = {
    "A": {"f": [2, 3], "k": [1, 3, 5], "z": [2, 3], "mus": ["++"],
          "lang": [False]},
    "B": {"f": [3, 4], "k": [2, 5, 7], "z": [2, 3], "mus": ["+-"],
          "lang": [False]},
    "C": {"f": [5, 6], "k": [3, 5, 7], "z": [2, 4], "mus": ["+-"],
          "lang": [True]},
}


def b47(links, rechts, **kw):
    kw.setdefault("tipps", TIPPS47)
    return bau(links, rechts, **kw)


def bf1(p):
    """Lösung ist ein Bruch, Grundform:  2x + 1 = 4

    Auf Level C steht Erhebungsaufgabe 1a im Wortlaut:
    5x + 10(2 − 6x) = 22 − 6(x − 2)  →  x = −2/7
    """
    f, k, mus = p["f"], p["k"], p["mus"]
    if p["lang"]:
        links = ("++", (X(5), KL(10, "+-", (Z(2), X(6)))))
        rechts = ("+-", (Z(22), KL(6, "+-", (X(1), Z(2)))))
        return b47(links, rechts)
    if mus == "+-":
        links = ("+-", (X(f + 2), Z(k)))
        rechts = ("+", (Z(k + 1),))
    else:
        links = ("++", (X(f + 2), Z(k)))
        rechts = ("+", (Z(k + f + 1),))
    return b47(links, rechts)


BF1 = Bauform("BF1", "Lösung ist ein Bruch, Grundform",
    bereiche=BEREICH, bauen=bf1, filter=BRUCH)


def bf2(p):
    """Der Bruch muss gekürzt werden:  14x = 21  →  x = 3/2"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    g = z + 1
    if p["lang"]:
        links = ("+-", (X(2 * g), Z(k)))
        rechts = ("+-", (Z(3 * g + k), Z(k)))
    elif mus == "+-":
        links = ("+-", (X(2 * g), Z(k)))
        rechts = ("+", (Z(3 * g - k),))
    else:
        links = ("+", (X(2 * g),))
        rechts = ("+", (Z(3 * g),))
    return b47(links, rechts, extra=[
        F("nicht_gekuerzt", Rational(3 * g, 2 * g) + Rational(1, 2),
          f"Der Bruch lässt sich kürzen: {3 * g} und {2 * g} haben beide "
          f"den Teiler {g}."),
    ])


BF2 = Bauform("BF2", "Der Bruch muss gekürzt werden",
    bereiche=BEREICH, bauen=bf2, filter=BRUCH)


def bf3(p):
    """Klammer, Lösung als Bruch:  2(x + 1) = 5"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("++", (KL(f, mus, (X(1), Z(k))), KL(z, "+-", (X(1), Z(k)))))
    else:
        links = ("+", (KL(f, mus, (X(1), Z(k))),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(kl + al + 1),))
    return b47(links, rechts)


BF3 = Bauform("BF3", "Klammer, Lösung als Bruch",
    bereiche=BEREICH, bauen=bf3, filter=BRUCH)


def bf4(p):
    """Zwei Produkte — das x² hebt sich auf:
       (x + 1)(x + 5) = (x + 3)(x + 7)"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("+", (PROD(-k, -z),))
        rechts = ("+", (PROD(-(k + 1), -(z + 2)),))
    elif mus == "+-":
        links = ("+", (PROD(1, -k),))
        rechts = ("+", (PROD(z, -(k + z + 1)),))
    else:
        links = ("+", (PROD(1, z),))
        rechts = ("+", (PROD(k, z + 2),))
    return b47(links, rechts)


BF4 = Bauform("BF4", "Zwei Produkte — das x² hebt sich auf",
    bereiche=BEREICH, bauen=bf4, filter=FREI)


def bf5(p):
    """Sonderfall: allgemeingültig:  2(x + 3) = 2x + 6"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    links = ("+", (KL(f, mus, (X(1), Z(k))),))
    _, kl = _sammeln(*links)
    if p["lang"]:
        links = ("+-", (KL(f, mus, (X(1), Z(k))), Z(z)))
        _, kl = _sammeln(*links)
    rechts = ("++", (X(f), Z(kl))) if kl >= 0 else ("+-", (X(f), Z(-kl)))
    return b47(links, rechts, art="alle")


BF5 = Bauform("BF5", "Sonderfall: allgemeingültig",
    bereiche=BEREICH, bauen=bf5, filter=SONDER)


def bf6(p):
    """Bruch als Faktor vor dem x:  (1/2)x = 3"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("+--", (BR(1, f), BZ(1, z), Z(1)))
    elif mus == "+-":
        links = ("+-", (BR(1, f), BZ(1, z)))
    else:
        links = ("+", (BR(1, f),))
    rechts = ("+", (BZ(1, z + 1),))
    return b47(links, rechts)


BF6 = Bauform("BF6", "Bruch als Faktor vor dem x",
    bereiche=BEREICH, bauen=bf6, filter=FREI)


def bf7(p):
    """Brüche als Koeffizienten beidseitig:
       (3/4)x − 1/2 = (1/4)x + 1/3"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("+-", (BR(3, 4), BZ(1, 2)))
        rechts = ("++", (BR(1, 4), BZ(1, 3)))
    elif mus == "+-":
        links = ("++", (BR(2, 3), BZ(1, 2)))
        rechts = ("+", (BR(1, 2),))
    else:
        links = ("+", (BR(1, 2),))
        rechts = ("+", (BZ(1, 3),))
    return b47(links, rechts)


BF7 = Bauform("BF7", "Brüche als Koeffizienten beidseitig",
    bereiche=BEREICH, bauen=bf7, filter=FREI)


def bf8(p):
    """Sonderfall: unlösbar:  3x + 5 = 3x + 9"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("+", (KL(f, "+-", (X(1), Z(k))),))
        _, kl = _sammeln(*links)
        rechts = ("++", (X(f), Z(kl + z)))
    elif mus == "+-":
        links = ("+", (KL(f, "++", (X(1), Z(k))),))
        rechts = ("+-", (X(f), Z(k)))
    else:
        links = ("++", (X(f), Z(k)))
        rechts = ("++", (X(f), Z(k + z + 1)))
    return b47(links, rechts, art="keine")


BF8 = Bauform("BF8", "Sonderfall: unlösbar",
    bereiche=BEREICH, bauen=bf8, filter=SONDER)


def bf9(p):
    """Negativer Bruch als Lösung:  4x + 9 = 2"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    #: Die linke Konstante ist immer groesser als die rechte Seite — damit
    #: wird die Loesung negativ, und weil f + 1 kein Teiler ist, ein Bruch.
    kl = k + f + 2
    if p["lang"]:
        links = ("++-", (X(f + 1), Z(kl + z), Z(z)))
        rechts = ("+-", (Z(k + 1), Z(1)))
    elif mus == "+-":
        links = ("++-", (X(f + 1), Z(kl + z), Z(z)))
        rechts = ("+", (Z(k),))
    else:
        links = ("++", (X(f + 1), Z(kl)))
        rechts = ("+", (Z(k),))
    return b47(links, rechts)


BF9 = Bauform("BF9", "Negativer Bruch als Lösung",
    bereiche=BEREICH, bauen=bf9, filter=BRUCH)


def bf10(p):
    """Klammer auf beiden Seiten, Lösung als Bruch:
       3(x + 2) = 2(x + 5) + 1"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    links = ("+", (KL(f + 2, mus, (X(1), Z(k))),))
    if p["lang"]:
        rechts = ("++-", (KL(f, mus, (X(1), Z(k + z))), Z(1), Z(z)))
    else:
        rechts = ("++", (KL(f, mus, (X(1), Z(k + z))), Z(1)))
    return b47(links, rechts)


BF10 = Bauform("BF10", "Klammer auf beiden Seiten, Lösung als Bruch",
    bereiche=BEREICH, bauen=bf10, filter=BRUCH)


def bf11(p):
    """Sonderfall: die Lösung ist null, trotz Brüchen:
       (1/2)x + 3 = 3"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("++-", (BR(1, z), Z(k), Z(1)))
    elif mus == "+-":
        links = ("+-", (BR(1, z), Z(k)))
    else:
        links = ("++", (BR(1, z), Z(k)))
    _, kl = _sammeln(*links)
    rechts = ("+", (Z(kl),)) if kl >= 0 else ("-", (Z(-kl),))
    return b47(links, rechts, extra=[
        F("nenner_als_loesung", Integer(z),
          f"{z} ist der Nenner des Bruchs, nicht die Lösung."),
        F("konstante_als_loesung", Integer(k),
          f"{k} steht in der Gleichung, ist aber nicht x."),
        F("eins_47", Integer(1),
          "Setz null ein und rechne nach — beide Seiten stimmen überein."),
        F("minus_eins_47", Integer(-1),
          "Nur null macht beide Seiten gleich."),
        F("bruch_47", Rational(1, z),
          "Der Bruch vor dem x ist nicht die Lösung."),
    ])


BF11 = Bauform("BF11", "Sonderfall: die Lösung ist null, trotz Brüchen",
    bereiche=BEREICH, bauen=bf11, filter=FREI)


def bf12(p):
    """Gemischt: Klammer, Bruch und Zahl in einer Gleichung"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("++-", (KL(f, mus, (X(1), Z(k))), BZ(1, z), Z(1)))
    else:
        links = ("++", (KL(f, mus, (X(1), Z(k))), BZ(1, z)))
    rechts = ("+", (Z(k + 1),))
    return b47(links, rechts)


BF12 = Bauform("BF12", "Gemischt: Klammer, Bruch und Zahl",
    bereiche=BEREICH, bauen=bf12, filter=BRUCH)


S47 = Schablone(
    nr="S47", titel="Klammern beidseitig, Lösung als Bruch",
    lektionen="13.7 – 13.9", erhebung="1a",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Lösung",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Rechne wie bei jeder Gleichung — und lass am Schluss den "
              "Bruch stehen, statt zu runden. Kürzen ist der letzte "
              "Schritt."),
)
