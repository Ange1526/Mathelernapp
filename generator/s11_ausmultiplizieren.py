# -*- coding: utf-8 -*-
"""
S38 · Zahl bzw. Variable mal Klammer          (Lektionen 11.1 – 11.4)
S39 · Ausmultiplizieren und zusammenfassen    (Lektionen 11.5 – 11.6)
S40 · Negative Zahl, Minus vor Variable       (Lektionen 11.7 – 11.8)

    «Rechne aus.»
    3(x + 2)      x(3 + y)      2(x + 1) + 3(x + 2)      −a(b − c)

**Erhebungsaufgabe 2b** hängt an 11.8 und liegt damit in S40.

DER FEHLER, UM DEN SICH DAS GANZE KAPITEL DREHT: der Faktor vor der Klammer
gilt für JEDES Glied darin. `3(x + 2)` ist `3x + 6`, nicht `3x + 2`. Er wird
in jeder Bauform aus der Aufgabe gerechnet und steht darum überall im
Katalog.

Die Zielform ist AUSMULTIPLIZIERT: eine Antwort, die die Klammer noch
enthält, ist nicht falsch, sondern unfertig — die App sagt das von sich aus.

LEVELACHSE (Teil 2 der drei Schablonen):

    S38   Gliederzahl und Art des Faktors   Zahl → Variable → Monom
    S39   Gliederzahl und Vorzeichen
    S40   Gliederzahl und Anzahl Minuszeichen
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s9_division import M, Su, _reihe, als_text, reihenfolge
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]
SORTE3 = [z, c, w, d]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


@dataclass(frozen=True)
class KM:
    """Ein Faktor mal eine Klammer:  3(x + 2)   ·   (x + 2) · 3

    `hinten` stellt den Faktor hinter die Klammer — das ist BF6 von S38.
    """
    faktor: M
    muster: str
    glieder: tuple
    hinten: bool = False

    @property
    def wert(self):
        innen = Integer(0)
        for zeichen, g in zip(self.muster, self.glieder):
            innen += g.wert if zeichen == "+" else -g.wert
        return expand(sympify(self.faktor.wert) * innen)

    @property
    def _klammer(self) -> str:
        return f"({_reihe(self.muster, self.glieder)})"

    @property
    def text(self) -> str:
        f = self.faktor.text
        if self.hinten:
            return f"{self._klammer} · {f}"
        if f == "1":
            return f"1 · {self._klammer}"
        if f == MINUS + "1":
            #: «−(x + 2)» statt «−1(x + 2)» — so steht es im Lehrmittel.
            return f"{MINUS}{self._klammer}"
        return f"{f}{self._klammer}"


def summe(muster, glieder):
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += g.wert if zeichen == "+" else -g.wert
    return expand(raus)


def kandidaten(muster, glieder, loesung):
    """Die fünf Fehler aus Teil 5, aus der Aufgabe gerechnet."""
    raus = []
    klammern = [g for g in glieder if isinstance(g, KM)]
    if not klammern:
        return raus
    k0 = klammern[0]
    fw = sympify(k0.faktor.wert)

    #: 1 · Der Faktor wurde nur mit dem ERSTEN Glied malgenommen.
    def nur_erstes(km):
        innen = Integer(0)
        for i, (zeichen, g) in enumerate(zip(km.muster, km.glieder)):
            w = sympify(g.wert) * (sympify(km.faktor.wert) if i == 0 else 1)
            innen += w if zeichen == "+" else -w
        return expand(innen)

    raus.append(F("nur_erstes_glied",
        expand(summe(muster, [nur_erstes(g) if isinstance(g, KM) else g.wert
                              for g in glieder]) if False else
               sum((nur_erstes(g) if isinstance(g, KM) else sympify(g.wert))
                   * (1 if zn == "+" else -1)
                   for zn, g in zip(muster, glieder))),
        f"Der Faktor {k0.faktor.text} gilt für JEDES Glied in der Klammer, "
        f"nicht nur für das erste."))

    #: 2 · Das Vorzeichen in der Klammer wurde nicht mitgenommen.
    def ohne_vorzeichen(km):
        innen = Integer(0)
        for zeichen, g in zip(km.muster, km.glieder):
            innen += sympify(g.wert)
        return expand(sympify(km.faktor.wert) * innen)

    raus.append(F("vorzeichen_klammer",
        expand(sum((ohne_vorzeichen(g) if isinstance(g, KM)
                    else sympify(g.wert)) * (1 if zn == "+" else -1)
                   for zn, g in zip(muster, glieder))),
        "Ein Minus in der Klammer bleibt beim Ausmultiplizieren erhalten."))

    #: 3 · Der Faktor wurde addiert statt multipliziert.
    def addiert(km):
        innen = Integer(0)
        for zeichen, g in zip(km.muster, km.glieder):
            w = sympify(km.faktor.wert) + sympify(g.wert)
            innen += w if zeichen == "+" else -w
        return expand(innen)

    raus.append(F("faktor_addiert",
        expand(sum((addiert(g) if isinstance(g, KM) else sympify(g.wert))
                   * (1 if zn == "+" else -1)
                   for zn, g in zip(muster, glieder))),
        f"{k0.faktor.text} steht vor der Klammer — das heisst mal, nicht "
        f"plus."))

    #: 4 · Nur das letzte Glied wurde malgenommen.
    def nur_letztes(km):
        innen = Integer(0)
        letzte = len(km.glieder) - 1
        for i, (zeichen, g) in enumerate(zip(km.muster, km.glieder)):
            w = sympify(g.wert) * (sympify(km.faktor.wert)
                                   if i == letzte else 1)
            innen += w if zeichen == "+" else -w
        return expand(innen)

    raus.append(F("nur_letztes_glied",
        expand(sum((nur_letztes(g) if isinstance(g, KM) else sympify(g.wert))
                   * (1 if zn == "+" else -1)
                   for zn, g in zip(muster, glieder))),
        "Jedes Glied der Klammer wird mit dem Faktor malgenommen."))

    #: 5 · Das ganze Vorzeichen der Aufgabe gedreht.
    raus.append(F("vorzeichen_gesamt", expand(-sympify(loesung)),
        "Zähl die Minuszeichen noch einmal."))

    #: 6 · Der Faktor wurde zweimal angewandt.
    if fw not in (0, 1):
        raus.append(F("faktor_zweimal", expand(sympify(loesung) * fw),
            f"{k0.faktor.text} wird genau einmal mit jedem Glied "
            f"malgenommen."))

    #: 7 · Die Klammer wurde einfach weggelassen.
    innen = Integer(0)
    for zeichen, g in zip(k0.muster, k0.glieder):
        innen += sympify(g.wert) if zeichen == "+" else -sympify(g.wert)
    raus.append(F("faktor_vergessen", expand(innen),
        f"Der Faktor {k0.faktor.text} vor der Klammer gehoert zur Aufgabe — "
        f"er faellt nicht weg."))

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    ziel = expand(sympify(loesung))
    for f in fehler:
        e = f.ergebnis.expr
        if e is None:
            continue
        e = expand(sympify(e))
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


TIPPS = [
    "Der Faktor vor der Klammer gilt für JEDES Glied darin.",
    "Geh die Glieder der Klammer der Reihe nach durch und multiplizier "
    "jedes einzeln.",
    "",
]


def bau(muster, glieder, extra=()):
    l = summe(muster, glieder)
    frage = _reihe(muster, glieder)
    folge = reihenfolge([g for g in glieder if not isinstance(g, KM)]) or []
    for g in glieder:
        if isinstance(g, KM):
            for s in reihenfolge(list(g.glieder) + [g.faktor]):
                if s not in folge:
                    folge.append(s)
    text = als_text(l, folge)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l), l)
    klammern = [g for g in glieder if isinstance(g, KM)]
    schritte = [("Die Klammer anschauen", frage)]
    if klammern:
        k0 = klammern[0]
        schritte.append((f"Jedes Glied mit {k0.faktor.text} malnehmen",
                         als_text(k0.wert, folge)))
    schritte.append(("Gleichartige Glieder zusammenfassen", text))
    return {"frage": frage, "loesung_text": text,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.AUSMULTIPLIZIERT,
                               fehlerkatalog=fehler),
            "schritte": schritte,
            "tipps": [TIPPS[0], TIPPS[1], f"Am Schluss steht {text}."]}


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr != 0


def verschieden(*namen):
    def f(p, g):
        werte = [str(p[nn]) for nn in namen if nn in p]
        return len(set(werte)) == len(werte)
    return f


STANDARD = [kopfrechenbar, fehler_eindeutig, fuenf, nicht_null]
ZWEI = STANDARD + [verschieden("v1", "v2")]
DREI = STANDARD + [verschieden("v1", "v2", "v3")]

BEREICH = {
    "A": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [2, 3],
          "k": [2, 3, 4], "stufe": [1]},
    "B": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [3, 4],
          "k": [3, 4, 5], "stufe": [2]},
    "C": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [4, 5],
          "k": [2, 3, 5], "stufe": [3]},
}


def _zahl(w):
    return M(Integer(w))


def _var(s, e=1, k=1):
    return M(Integer(k), ((s, e),))


# ══════════════════════════════════════════════════════════════════════════
# S38 · Zahl bzw. Variable mal Klammer     (11.1 – 11.4)
# ══════════════════════════════════════════════════════════════════════════

def bf38_1(p):
    """Zahl mal Klammer, Plus darin:  3(x + 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(f), "+++", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(f), "++", (_var(v1, k=2), _zahl(k)))
    else:
        km = KM(_zahl(f), "++", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF38_1 = Bauform("BF1", "Zahl mal Klammer, Plus darin",
    bereiche=BEREICH, bauen=bf38_1, filter=ZWEI)


def bf38_2(p):
    """Zahl mal Klammer, Minus darin:  3(x − 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(f), "+--", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(f), "+-", (_var(v1, k=2), _zahl(k)))
    else:
        km = KM(_zahl(f), "+-", (_var(v1), _zahl(k)))
    return bau("+", [km])


BF38_2 = Bauform("BF2", "Zahl mal Klammer, Minus darin",
    bereiche=BEREICH, bauen=bf38_2, filter=ZWEI)


def bf38_3(p):
    """Drei und mehr Glieder in der Klammer:  3(x + 2 − y)"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        km = KM(_zahl(f), "++-+", (_var(v1), _zahl(k), _var(v2), _var(v3)))
    elif st == 2:
        km = KM(_zahl(f), "+-+", (_var(v1), _zahl(k), _var(v2)))
    else:
        km = KM(_zahl(f), "++-", (_var(v1), _zahl(k), _var(v2)))
    return bau("+", [km])


BF38_3 = Bauform("BF3", "Drei und mehr Glieder in der Klammer",
    bereiche=BEREICH, bauen=bf38_3, filter=DREI)


def bf38_4(p):
    """Variable mal Klammer:  x(3 + y)"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    if st == 3:
        km = KM(_var(v1), "++-", (_zahl(f), _var(v2), _var(v3)))
    elif st == 2:
        km = KM(_var(v1), "+-", (_zahl(f), _var(v2)))
    else:
        km = KM(_var(v1), "++", (_zahl(f), _var(v2)))
    return bau("+", [km])


BF38_4 = Bauform("BF4", "Variable mal Klammer",
    bereiche=BEREICH, bauen=bf38_4, filter=DREI)


def bf38_5(p):
    """Monom mal Klammer — Potenzen entstehen:  a(2a + b)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_var(v1, k=f), "+-", (_var(v1, k=2), _var(v2, k=k)))
    elif st == 2:
        km = KM(_var(v1), "+-", (_var(v1, k=2), _var(v2)))
    else:
        km = KM(_var(v1), "++", (_var(v1, k=2), _var(v2)))
    return bau("+", [km])


BF38_5 = Bauform("BF5", "Monom mal Klammer — Potenzen entstehen",
    bereiche=BEREICH, bauen=bf38_5, filter=ZWEI)


def bf38_6(p):
    """Der Faktor steht hinter der Klammer:  (x + 2) · 3"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(f), "++-", (_var(v1), _zahl(k), _var(v2)), hinten=True)
    elif st == 2:
        km = KM(_zahl(f), "+-", (_var(v1), _zahl(k)), hinten=True)
    else:
        km = KM(_zahl(f), "++", (_var(v1), _zahl(k)), hinten=True)
    return bau("+", [km])


BF38_6 = Bauform("BF6", "Der Faktor steht hinter der Klammer",
    bereiche=BEREICH, bauen=bf38_6, filter=ZWEI)


def bf38_7(p):
    """Beide Faktoren sind Monome mit Potenzen:  (a² + b²)ab"""
    v1, v2, st = p["v1"], p["v2"], p["stufe"]
    if st == 3:
        km = KM(M(Integer(1), ((v1, 1), (v2, 1))), "+-",
                (_var(v1, 2), _var(v2, 2)), hinten=True)
    elif st == 2:
        km = KM(M(Integer(1), ((v1, 1), (v2, 1))), "++",
                (_var(v1, 2), _var(v2, 1)), hinten=True)
    else:
        km = KM(M(Integer(1), ((v1, 1), (v2, 1))), "++",
                (_var(v1, 2), _var(v2, 2)), hinten=True)
    return bau("+", [km])


BF38_7 = Bauform("BF7", "Beide Faktoren sind Monome mit Potenzen",
    bereiche=BEREICH, bauen=bf38_7, filter=ZWEI)


def bf38_8(p):
    """Sonderfall: der Faktor ist eins:  1 · (x + 5)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(1), "++-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(1), "+-", (_var(v1), _zahl(k)))
    else:
        km = KM(_zahl(1), "++", (_var(v1), _zahl(k)))
    innen = Integer(0)
    for zeichen, g in zip(km.muster, km.glieder):
        innen += sympify(g.wert) if zeichen == "+" else -sympify(g.wert)
    l = expand(innen)
    return {"frage": km.text, "loesung_text": als_text(l, reihenfolge(
                list(km.glieder))),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.AUSMULTIPLIZIERT,
                               fehlerkatalog=[
                F("verdoppelt", expand(l * 2),
                  "Mal eins ändert nichts — die Klammer bleibt, wie sie ist."),
                F("eins_dazu", expand(l + 1),
                  "Der Faktor 1 wird nicht addiert, sondern multipliziert — "
                  "und mal eins ändert nichts."),
                F("nur_eins", Integer(1),
                  "Mal eins lässt den ganzen Term unverändert."),
                F("vorzeichen_eins", expand(-l),
                  "Mal eins dreht kein Vorzeichen um."),
                F("erstes_eins", sympify(km.glieder[0].wert),
                  "Alle Glieder der Klammer bleiben stehen."),
            ]),
            "schritte": [("Den Faktor anschauen", km.text),
                         ("Mal eins ändert nichts", als_text(l, reihenfolge(
                             list(km.glieder))))],
            "tipps": [TIPPS[0], TIPPS[1],
                      "Der Faktor ist eins — die Klammer kann einfach "
                      "weggelassen werden."]}


BF38_8 = Bauform("BF8", "Sonderfall: der Faktor ist eins",
    bereiche=BEREICH, bauen=bf38_8, filter=ZWEI)


def bf38_9(p):
    """Sonderfall: der Faktor ist null:  0 · (x + 5)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(0), "++-", (_var(v1), _zahl(k), _var(v2)))
    elif st == 2:
        km = KM(_zahl(0), "+-", (_var(v1), _zahl(k)))
    else:
        km = KM(_zahl(0), "++", (_var(v1), _zahl(k)))
    innen = Integer(0)
    for zeichen, g in zip(km.muster, km.glieder):
        innen += g.wert if zeichen == "+" else -g.wert
    return {"frage": km.text, "loesung_text": "0",
            "aufgabe": Aufgabe(loesung=Loesung.zahl(0), variablen=VARS,
                               zielform=Zielform.AUSMULTIPLIZIERT,
                               fehlerkatalog=[
                F("klammer_geblieben", expand(innen),
                  "Mal null ist alles null — die Klammer verschwindet ganz."),
                F("eins_38", Integer(1),
                  "Mal null ergibt null, nicht eins."),
                F("nur_erstes_38", sympify(km.glieder[0].wert),
                  "Der Faktor null gilt für die ganze Klammer."),
                F("minus_38", Integer(-1),
                  "Null mal irgendetwas bleibt null."),
                F("zwei_38", Integer(2),
                  "Null mal irgendetwas bleibt null."),
            ]),
            "schritte": [("Den Faktor anschauen", km.text),
                         ("Mal null ist alles null", "0")],
            "tipps": [TIPPS[0], TIPPS[1], "Der Faktor ist null — damit ist "
                                          "der ganze Term null."]}


BF38_9 = Bauform("BF9", "Sonderfall: der Faktor ist null",
    bereiche=BEREICH, bauen=bf38_9,
    filter=[kopfrechenbar, fehler_eindeutig, fuenf, verschieden("v1", "v2")])


def bf38_10(p):
    """In der Klammer lässt sich zuerst zusammenfassen:  2(3x + 4x)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        km = KM(_zahl(f), "++-", (_var(v1, k=3), _var(v1, k=4), _var(v2)))
    elif st == 2:
        km = KM(_zahl(f), "+-", (_var(v1, k=5), _var(v1, k=2)))
    else:
        km = KM(_zahl(f), "++", (_var(v1, k=3), _var(v1, k=4)))
    return bau("+", [km])


BF38_10 = Bauform("BF10", "In der Klammer lässt sich zuerst zusammenfassen",
    bereiche=BEREICH, bauen=bf38_10, filter=ZWEI)


def bf38_11(p):
    """Nach dem Ausmultiplizieren kommt noch ein Glied dazu:
       2(x + 3) + 4"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    km = KM(_zahl(f), "+-" if st == 2 else "++", (_var(v1), _zahl(k)))
    if st == 3:
        return bau("++-", [km, _zahl(k * 2), _var(v2)])
    return bau("++", [km, _zahl(k * 2)])


BF38_11 = Bauform("BF11", "Nach dem Ausmultiplizieren kommt ein Glied dazu",
    bereiche=BEREICH, bauen=bf38_11, filter=ZWEI)


def bf38_12(p):
    """Zwei Klammern, beide ausmultiplizieren:  2(x + 1) + 3(x + 2)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    k1 = KM(_zahl(f), "++", (_var(v1), _zahl(1)))
    if st == 3:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _var(v2)))
        return bau("+-", [k1, k2])
    if st == 2:
        k2 = KM(_zahl(f + 1), "+-", (_var(v1), _zahl(k)))
        return bau("++", [k1, k2])
    k2 = KM(_zahl(f + 1), "++", (_var(v1), _zahl(k)))
    return bau("++", [k1, k2])


BF38_12 = Bauform("BF12", "Zwei Klammern, beide ausmultiplizieren",
    bereiche=BEREICH, bauen=bf38_12, filter=ZWEI)


S38 = Schablone(
    nr="S38", titel="Zahl bzw. Variable mal Klammer",
    lektionen="11.1 – 11.4", erhebung="2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Art des Faktors",
    bauformen=[BF38_1, BF38_2, BF38_3, BF38_4, BF38_5, BF38_6,
               BF38_7, BF38_8, BF38_9, BF38_10, BF38_11, BF38_12],
    kernidee=("Der Faktor vor der Klammer gilt für JEDES Glied darin. "
              "3(x + 2) ist 3x + 6, nicht 3x + 2."),
)
