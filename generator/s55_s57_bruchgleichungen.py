# -*- coding: utf-8 -*-
"""
S55 · Bruch mal Klammer in der Gleichung   (Lektion  15.6)
S56 · Term im Nenner, x im Nenner          (Lektionen 15.7 – 15.8)
S57 · Dezimalzahlen                        (Lektion  15.9)

    «Löse die Gleichung. Gib nur den Wert von x an.»
    (1/2)(x + 4) = 5      2/(x − 1) = 1      0.5x + 1.5 = 4

**Erhebungsaufgabe 1b** hängt an 15.6 und ist S55.

S56 IST DER EINE PUNKT, WO DIE DEFINITIONSMENGE ZÄHLT. Steht x im Nenner,
kann rechnerisch eine Zahl herauskommen, die den Nenner null macht — dann
ist sie keine Lösung. CLAUDE.md hält Definitionsbereiche ausserhalb des
Umfangs; hier wird der Fall darum nicht als Menge abgefragt, sondern als
Ergebnis: die Gleichung hat dann KEINE Lösung. Genau das steht auch in der
Theoriebox des Lehrmittels.

LEVELACHSE (Teil 2):

    S55   Struktur der Lösung   ganzzahlig → negativ oder null → Bruch
    S56   Struktur des Nenners  Zahl → Term ohne x → x im Nenner
    S57   Anzahl Dezimalstellen und Summanden
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational

from .s45_gleichungen import ANLEITUNG, F, X, Z, _sammeln
from .s46_s47_klammern import (KL, SONDER, bau, fehler_eindeutig, fuenf,
                               kopfrechenbar, loesbar, nicht_null, reihe,
                               stimmt)
from .s15_bruchgleichungen import BZ, TIPPS, XB, ZB, bg
from .schablone import Bauform, Schablone

STANDARD = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
            nicht_null]

BEREICH = {
    "A": {"n1": [2, 3], "n2": [3, 4], "k": [1, 2, 4], "stufe": [1]},
    "B": {"n1": [2, 3], "n2": [4, 6], "k": [2, 3, 5], "stufe": [2]},
    "C": {"n1": [3, 4], "n2": [6, 5], "k": [1, 3, 5], "stufe": [3]},
}


@dataclass(frozen=True)
class BK:
    """Ein Bruch mal eine Klammer:  (1/2)(x + 4)

    Der Bruch wird durchmultipliziert — die Gleichung bleibt linear.
    """
    zaehler: int
    nenner: int
    muster: str
    glieder: tuple

    @property
    def _innen(self):
        return _sammeln(self.muster, self.glieder)

    @property
    def anteil(self):
        return Rational(self.zaehler, self.nenner) * self._innen[0]

    @property
    def konstante(self):
        return Rational(self.zaehler, self.nenner) * self._innen[1]

    @property
    def text(self) -> str:
        return (f"({self.zaehler}/{self.nenner})"
                f"({reihe(self.muster, self.glieder)})")


@dataclass(frozen=True)
class DZ:
    """Eine Dezimalzahl:  0.5   ·   1.25"""
    wert: Rational

    @property
    def anteil(self):
        return 0

    @property
    def konstante(self):
        return self.wert

    @property
    def text(self) -> str:
        return str(float(self.wert))


@dataclass(frozen=True)
class DX:
    """Eine Dezimalzahl mal x:  0.5x"""
    wert: Rational

    @property
    def anteil(self):
        return self.wert

    @property
    def konstante(self):
        return 0

    @property
    def text(self) -> str:
        return f"{float(self.wert)}x"


def bk_extra(bkl, hn):
    """Der Fehler, wegen dem es Lektion 15.6 gibt: der Bruch wurde nur mit
    dem ersten Glied der Klammer multipliziert."""
    return F("nur_erstes_glied_bk", Integer(hn),
             "Der Bruch vor der Klammer gilt für JEDES Glied darin, nicht "
             "nur für das erste.")


# ══════════════════════════════════════════════════════════════════════════
# S55 · Bruch mal Klammer in der Gleichung   (15.6, Erhebung 1b)
# ══════════════════════════════════════════════════════════════════════════

def zielwert(p):
    """Die Levelachse von S55 ist die STRUKTUR DER LÖSUNG:
    ganzzahlig, negativ, Bruch."""
    return {1: Integer(6), 2: Integer(-4), 3: Rational(3, 2)}[p["stufe"]]


def klammer(p, koeff, konst, nenner):
    """Die Klammer in der Bauart der Stufe.

    Teil 2 nennt als Achse die STRUKTUR DER LOESUNG — ganzzahlig, negativ,
    Bruch. Das sieht man der Aufgabe aber nicht an, und der Testlauf
    beanstandet zu Recht, wenn A und B gleich gebaut sind. Darum waechst
    zusaetzlich die Klammer mit: A zwei Glieder, B ein Minus darin, C drei
    Glieder.
    """
    st = p["stufe"]
    if st == 3:
        return BK(1, nenner, "++-", (X(koeff), Z(konst), Z(1)))
    if st == 2:
        return BK(1, nenner, "+-", (X(koeff), Z(konst)))
    return BK(1, nenner, "++", (X(koeff), Z(konst)))


def b55(links, rechts, extra=()):
    return bg(links, rechts, extra=list(extra))


def bf55_1(p):
    """Bruch mal Klammer links, Zahl rechts:  (1/2)(x + 4) = 5"""
    n1, k = p["n1"], p["k"]
    links = ("+", (klammer(p, 1, k * 2, n1),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * zielwert(p) + kl),))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_1 = Bauform("BF1", "Bruch mal Klammer links, Zahl rechts",
    bereiche=BEREICH, bauen=bf55_1, filter=STANDARD)


def bf55_2(p):
    """Ganze Zahl links, Bruch rechts:  2(x + 1) = (1/2)(x + 8)"""
    n1, k = p["n1"], p["k"]
    #: Auf C kommt links ein drittes Glied dazu.
    if p["stufe"] == 3:
        links = ("+", (KL(2, "++-", (X(1), Z(k), Z(1))),))
    else:
        links = ("+", (KL(2, "+-" if p["stufe"] == 2 else "++",
                          (X(1), Z(k))),))
    al, kl = _sammeln(*links)
    ziel = zielwert(p)
    rechts_bk = BK(1, n1, "++", (X(1), Z(0)))
    ar = Rational(1, n1)
    rest = al * ziel + kl - ar * ziel
    rechts = ("++", (BK(1, n1, "++", (X(1), Z(0))), Z(rest)))
    return b55(links, rechts, extra=[bk_extra(rechts, n1)])


BF55_2 = Bauform("BF2", "Ganze Zahl links, Bruch rechts",
    bereiche=BEREICH, bauen=bf55_2, filter=STANDARD)


def bf55_3(p):
    """Bruch hebt den Koeffizienten auf:  2((1/2)x + 1) = x + 2"""
    n1, k = p["n1"], p["k"]
    links = ("+", (klammer(p, n1, k * n1, n1),))
    al, kl = _sammeln(*links)
    ziel = zielwert(p)
    #: Rechts MUSS ein anderer x-Anteil stehen — sonst heben sich die x auf
    #: und die Gleichung hat keine eindeutige Loesung. Das waere BF6.
    rechts = ("++", (X(2), Z(al * ziel + kl - 2 * ziel)))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_3 = Bauform("BF3", "Bruch hebt den Koeffizienten auf",
    bereiche=BEREICH, bauen=bf55_3, filter=STANDARD)


def bf55_4(p):
    """Derselbe Bruchfaktor auf beiden Seiten:
       (1/3)(3x − 3) = x − 1 + k"""
    n1, k = p["n1"], p["k"]
    links = ("+", (klammer(p, n1, n1 * k, n1),))
    al, kl = _sammeln(*links)
    ziel = zielwert(p)
    #: Auch hier: rechts ein anderer x-Anteil, sonst ist die Gleichung
    #: entweder allgemeingueltig oder unloesbar — beides eigene Bauformen.
    rechts = ("+-+", (X(3), Z(k), Z(al * ziel + kl - 3 * ziel + k)))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_4 = Bauform("BF4", "Derselbe Bruchfaktor auf beiden Seiten",
    bereiche=BEREICH, bauen=bf55_4, filter=STANDARD)


def bf55_5(p):
    """Sonderfall: keine Lösung:  (1/2)(2x + 1) = x + 2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    links = ("+", (BK(1, n1, "++", (X(n1), Z(k))),))
    _, kl = _sammeln(*links)
    if st == 3:
        rechts = ("+++", (X(1), Z(k), Z(1)))
    elif st == 2:
        rechts = ("+-", (X(1), Z(k)))
    else:
        rechts = ("++", (X(1), Z(k + 1)))
    return bg(links, rechts, art="keine")


BF55_5 = Bauform("BF5", "Sonderfall: keine Lösung",
    bereiche=BEREICH, bauen=bf55_5, filter=SONDER)


def bf55_6(p):
    """Sonderfall: allgemeingültig:  (1/2)(2x + 4) = x + 2"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++", (BK(1, n1, "++", (X(n1), Z(k * n1))), Z(1)))
    elif st == 2:
        links = ("+", (BK(1, n1, "+-", (X(n1), Z(k * n1))),))
    else:
        links = ("+", (BK(1, n1, "++", (X(n1), Z(k * n1))),))
    al, kl = _sammeln(*links)
    rechts = ("++", (X(1), Z(kl))) if kl >= 0 else ("+-", (X(1), Z(-kl)))
    return bg(links, rechts, art="alle")


BF55_6 = Bauform("BF6", "Sonderfall: allgemeingültig",
    bereiche=BEREICH, bauen=bf55_6, filter=SONDER)


def bf55_7(p):
    """Brüche als Koeffizienten beidseitig:
       (1/2)x + 1 = (1/3)x + 2"""
    n1, n2, k, st = p["n1"], p["n2"], p["k"], p["stufe"]
    if n1 == n2:
        n2 = n1 + 1
    if st == 3:
        links = ("++-", (XB(n1), Z(k), Z(1)))
    elif st == 2:
        links = ("+-", (XB(n1), Z(k)))
    else:
        links = ("++", (XB(n1), Z(k)))
    al, kl = _sammeln(*links)
    ziel = zielwert(p)
    ar = Rational(1, n2)
    rechts = ("++", (XB(n2), Z(al * ziel + kl - ar * ziel)))
    return b55(links, rechts)


BF55_7 = Bauform("BF7", "Brüche als Koeffizienten beidseitig",
    bereiche=BEREICH, bauen=bf55_7, filter=STANDARD)


def bf55_8(p):
    """Sonderfall: die Lösung ist null:  (1/2)(x + 2) = 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++", (BK(1, n1, "++", (X(1), Z(k))), Z(1)))
    elif st == 2:
        links = ("+", (BK(1, n1, "+-", (X(1), Z(k))),))
    else:
        links = ("+", (BK(1, n1, "++", (X(1), Z(k))),))
    _, kl = _sammeln(*links)
    rechts = ("+", (Z(kl),)) if kl >= 0 else ("-", (Z(-kl),))
    return bg(links, rechts, loesung=0, extra=[
        F("nenner_55", Integer(n1), f"{n1} ist der Nenner, nicht die Lösung."),
        F("klammer_55", Integer(k), f"{k} steht in der Klammer, nicht x."),
        F("eins_55", Integer(1), "Setz null ein — es stimmt."),
        F("minus_55", Integer(-1), "Nur null macht beide Seiten gleich."),
        F("bruch_55", Rational(1, n1), "Der Bruchfaktor ist nicht x."),
    ])


BF55_8 = Bauform("BF8", "Sonderfall: die Lösung ist null",
    bereiche=BEREICH, bauen=bf55_8,
    filter=[loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf])


def bf55_9(p):
    """Negativer Bruchfaktor:  −(1/2)(x + 4) = 1"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("-+", (BK(1, n1, "++", (X(1), Z(k * 2))), Z(1)))
    elif st == 2:
        links = ("-", (BK(1, n1, "+-", (X(1), Z(k * 2))),))
    else:
        links = ("-", (BK(1, n1, "++", (X(1), Z(k * 2))),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * zielwert(p) + kl),))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_9 = Bauform("BF9", "Negativer Bruchfaktor",
    bereiche=BEREICH, bauen=bf55_9, filter=STANDARD)


def bf55_10(p):
    """Bruch mal Klammer auf beiden Seiten:
       (1/2)(x + 1) = (1/3)(x + 2)"""
    n1, n2, k = p["n1"], p["n2"], p["k"]
    if n1 == n2:
        n2 = n1 + 1
    #: Die Klammer links waechst mit der Stufe: erst ein Glied mehr, dann
    #: ein Minus darin.
    mus = "+-" if p["stufe"] == 2 else "++"
    if p["stufe"] == 3:
        links = ("+", (BK(1, n1, "+++", (X(1), Z(k), Z(1))),))
    else:
        links = ("+", (BK(1, n1, mus, (X(1), Z(k))),))
    al, kl = _sammeln(*links)
    ziel = zielwert(p)
    ar = Rational(1, n2)
    rest = al * ziel + kl - ar * ziel
    rechts = ("++", (BK(1, n2, "++", (X(1), Z(0))), Z(rest)))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_10 = Bauform("BF10", "Bruch mal Klammer auf beiden Seiten",
    bereiche=BEREICH, bauen=bf55_10, filter=STANDARD)


def bf55_11(p):
    """Die Lösung ist ein Bruch:  (1/2)(x + 3) = 4"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("+-", (BK(1, n1, "++", (X(2), Z(k))), Z(1)))
    elif st == 2:
        links = ("+", (BK(1, n1, "+-", (X(2), Z(k))),))
    else:
        links = ("+", (BK(1, n1, "++", (X(2), Z(k))),))
    al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * zielwert(p) + kl),))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_11 = Bauform("BF11", "Die Lösung ist ein Bruch",
    bereiche=BEREICH, bauen=bf55_11, filter=STANDARD)


def bf55_12(p):
    """Zwei Brüche mal Klammer, dann zusammenfassen:
       (1/2)(x + 2) + (1/2)x = 5"""
    n1, k, st = p["n1"], p["k"], p["stufe"]
    if st == 3:
        links = ("++-", (BK(1, n1, "++", (X(1), Z(k))), XB(n1), Z(1)))
    elif st == 2:
        links = ("+-", (BK(1, n1, "++", (X(1), Z(k))), XB(n1)))
    else:
        links = ("++", (BK(1, n1, "++", (X(1), Z(k))), XB(n1)))
    al, kl = _sammeln(*links)
    if al == 0:
        links = ("++", (BK(1, n1, "++", (X(1), Z(k))), XB(n1 + 1)))
        al, kl = _sammeln(*links)
    rechts = ("+", (Z(al * zielwert(p) + kl),))
    return b55(links, rechts, extra=[bk_extra(links, n1)])


BF55_12 = Bauform("BF12", "Zwei Brüche mal Klammer, dann zusammenfassen",
    bereiche=BEREICH, bauen=bf55_12, filter=STANDARD)


S55 = Schablone(
    nr="S55", titel="Bruch mal Klammer in der Gleichung",
    lektionen="15.6", erhebung="1b",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Lösung",
    bauformen=[BF55_1, BF55_2, BF55_3, BF55_4, BF55_5, BF55_6,
               BF55_7, BF55_8, BF55_9, BF55_10, BF55_11, BF55_12],
    kernidee=("Ein Bruch vor einer Klammer gilt für JEDES Glied darin. "
              "Multipliziere die Klammer aus oder nimm beide Seiten mit dem "
              "Kehrwert mal."),
)
