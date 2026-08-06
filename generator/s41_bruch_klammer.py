# -*- coding: utf-8 -*-
"""
S41 · Bruch mal Klammer                          (Lektion 11.9)

    «Rechne aus.»
    (3/4)(x + 4)      (2/7)(3 + x)      9x((1/2)x² − 5x + 3)

Die letzte fehlende Zutat für Erhebungsaufgabe 1b. Der Abdeckungsnachweis
führt 1b auf 11.9, 2.9, 15.2, 15.6 und 13.9 zurück — 11.9 ist diese
Schablone, 15.6 ist S55.

BF4 ist die wichtigste für Kapitel 15: `(3/4)((4/3)x − 1)` ergibt `x − 3/4`,
weil (3/4) · (4/3) genau 1 ist. Dort fällt das x weg und die Gleichung wird
entweder unlösbar oder allgemeingültig. Wer das hier nicht sieht, versteht
in Kapitel 15 nicht, was passiert ist.

WARUM DIE GLIEDER SELBST GESCHRIEBEN WERDEN: SymPy zeigt `Rational(3,4)*x`
als `3x/4`. Im Lehrmittel steht `(3/4)x` — und `3x/4` liest sich wie «drei x
geteilt durch vier», was beim Ausmultiplizieren gerade die Verwechslung ist,
um die es geht. Der Text kommt darum aus den Gliedern, nie aus `str()`.

LEVELACHSE (Teil 2): Struktur des Faktors und Gliederzahl.

    A   Bruch mal ganze Zahl, Bruch mal Variable, zwei Glieder
    B   Bruch mal Bruch · der Koeffizient kürzt sich zu 1
    C   Variable im Faktor · Faktor rechts · drei Glieder

Die Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar, nenner_freundlich
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(expand(ergebnis)), text)


# ══════════════════════════════════════════════════════════════════════════
# Ein Glied — der Koeffizient darf ein Bruch sein
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class G:
    """Ein Glied. Der Koeffizient ist IMMER positiv — das Vorzeichen sitzt
    im Muster, nie im Glied (wie in `s6_punktrechnung`)."""
    koeff: object = Integer(1)
    basen: tuple = ()

    @property
    def wert(self):
        raus = sympify(self.koeff)
        for s, e in self.basen:
            raus *= s ** e
        return raus

    @property
    def text(self) -> str:
        k = sympify(self.koeff)
        if not self.basen:
            return f"{k.p}/{k.q}" if k.q != 1 else zeige(k)
        if k == 1:
            vorne = ""
        elif k.q != 1:
            vorne = f"({k.p}/{k.q})"
        else:
            vorne = zeige(k)
        return vorne + "".join(zeige(s) + (HOCH[e] if e > 1 else "")
                               for s, e in self.basen)


def mal(g1: G, g2: G) -> G:
    """Zwei Glieder multiplizieren — die Reihenfolge der Basen bleibt."""
    basen = list(g1.basen)
    for s, e in g2.basen:
        for i, (s2, e2) in enumerate(basen):
            if s2 == s:
                basen[i] = (s, e2 + e)
                break
        else:
            basen.append((s, e))
    basen = [(s, e) for s, e in basen if e != 0]
    return G(sympify(g1.koeff) * sympify(g2.koeff), tuple(basen))


def reihe(muster, glieder) -> str:
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def summe(muster, glieder):
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += g.wert if zeichen == "+" else -g.wert
    return expand(raus)


# ══════════════════════════════════════════════════════════════════════════
# Der Fehlerkatalog, aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def kandidaten(faktor: G, muster, glieder, loesung):
    """Die fünf Fehler aus Teil 5."""
    raus = []
    fk = sympify(faktor.koeff)

    def mit(wandeln):
        wert = Integer(0)
        for i, (zeichen, g) in enumerate(zip(muster, glieder)):
            teil = wandeln(i, g)
            wert += teil if zeichen == "+" else -teil
        return expand(wert)

    #: 1 · Nur das erste Glied wurde multipliziert.
    raus.append(F("nur_erstes",
        mit(lambda i, g: mal(faktor, g).wert if i == 0 else g.wert),
        f"Der Faktor {faktor.text} gilt für JEDES Glied in der Klammer, "
        f"nicht nur für das erste."))

    #: 2 · Nur das letzte Glied wurde multipliziert. Das ist der Fehler,
    #:     der bei einem Faktor RECHTS von der Klammer passiert.
    letztes = len(glieder) - 1
    raus.append(F("nur_letztes",
        mit(lambda i, g: mal(faktor, g).wert if i == letztes else g.wert),
        f"Der Faktor {faktor.text} gilt für die ganze Klammer — auch für "
        f"das erste Glied."))

    #: 3 · Bruch mal ganze Zahl: auch der Nenner wurde multipliziert.
    #:     (2/7) · 3 wird dann wieder 6/21 = 2/7.
    if fk.q != 1 and any(not g.basen for g in glieder):
        def nenner_auch(i, g):
            if not g.basen:
                return fk
            return mal(faktor, g).wert
        raus.append(F("nenner_auch_multipliziert", mit(nenner_auch),
            f"Bei {faktor.text} · einer ganzen Zahl wird nur der ZÄHLER "
            f"multipliziert. Der Nenner bleibt stehen."))

    #: 4 · Das Vorzeichen des letzten Glieds übersehen.
    if any(zn == "-" for zn in muster):
        gedreht = "".join("+" if zn == "-" else "-" for zn in muster)
        gedreht = "+" + gedreht[1:] if muster[0] == "+" else gedreht
        raus.append(F("vorzeichen_glied",
            summe(gedreht, [mal(faktor, g) for g in glieder]),
            "Ein Minus in der Klammer bleibt beim Ausmultiplizieren "
            "erhalten."))

    #: 5 · Mit dem Kehrwert multipliziert — hier wird mal gerechnet, nicht
    #:     geteilt.
    if fk.q != 1:
        kehr = G(Rational(fk.q, fk.p), faktor.basen)
        raus.append(F("kehrwert",
            summe(muster, [mal(kehr, g) for g in glieder]),
            f"Hier wird multipliziert, nicht dividiert. Der Faktor bleibt "
            f"{faktor.text} und wird nicht umgekehrt."))

    #: 6 · Der Faktor wurde ganz vergessen.
    raus.append(F("faktor_vergessen", summe(muster, glieder),
        f"Der Faktor {faktor.text} vor der Klammer gehört zur Aufgabe — "
        f"er fällt nicht weg."))

    #: 7 · Das Vorzeichen des ganzen Ergebnisses gedreht.
    raus.append(F("vorzeichen_gesamt", -sympify(loesung),
        "Zähl die Minuszeichen noch einmal."))

    #: 8 · Statt multipliziert wurde addiert.
    raus.append(F("addiert",
        mit(lambda i, g: fk + g.wert),
        f"{faktor.text} steht vor der Klammer — das heisst mal, nicht plus."))

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    ziel = expand(sympify(loesung))
    for fe in fehler:
        e = fe.ergebnis.expr
        if e is None:
            continue
        e = expand(sympify(e))
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(fe)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Bauen
# ══════════════════════════════════════════════════════════════════════════

def bau(faktor: G, muster, glieder, hinten=False, minus=False):
    """`hinten` stellt den Faktor rechts von die Klammer — das ist BF6."""
    ergebnis = [mal(faktor, g) for g in glieder]
    vz = -1 if minus else 1
    l = vz * summe(muster, ergebnis)

    kl = f"({reihe(muster, glieder)})"
    ft = faktor.text
    #: Ein blosser Bruch als Faktor braucht eine Klammer: `2/9(u + 9)` liest
    #: sich wie «2 geteilt durch 9(u+9)». Im Lehrmittel steht `(2/9)(u + 9)`.
    ft_frage = f"({ft})" if ("/" in ft and not ft.startswith("(")) else ft
    if hinten:
        frage = f"{kl} · {ft_frage}"
    else:
        frage = f"{ft_frage}{kl}"
    if minus:
        frage = MINUS + frage

    mus = muster if not minus else "".join(
        "-" if zn == "+" else "+" for zn in muster)
    loesung_text = reihe(mus, ergebnis)

    fehler = siebe(kandidaten(faktor, muster, glieder, summe(muster, ergebnis)),
                   summe(muster, ergebnis))
    if minus:
        fehler = [Fehler(fe.schluessel, Loesung.zahl(-sympify(fe.ergebnis.expr)),
                         fe.text) for fe in fehler]
        fehler = siebe(fehler, l)

    return {
        "frage": frage,
        "loesung_text": loesung_text,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                           zielform=Zielform.AUSMULTIPLIZIERT,
                           fehlerkatalog=fehler),
        "schritte": [
            ("Den Faktor notieren und die Glieder durchnummerieren",
             f"Faktor {ft}, {len(glieder)} Glieder"),
            ("Faktor mal jedes Glied — Zähler mal Zähler, Nenner mal Nenner",
             loesung_text),
            ("Jedes Teilergebnis kürzen", loesung_text),
            ("Gegenprobe: den Faktor wieder ausklammern", frage)],
        "tipps": [
            "Ein Bruch vor einer Klammer wird mit jedem einzelnen Glied "
            "darin multipliziert.",
            "Nimm die Glieder einzeln: erst Faktor mal erstes Glied, dann "
            "Faktor mal zweites Glied.",
            f"{ft} · {glieder[0].text} ergibt {ergebnis[0].text}. Jetzt "
            f"noch {ft} · {glieder[1].text}."],
    }


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr != 0


STANDARD = [kopfrechenbar, nenner_freundlich, fehler_eindeutig, fuenf,
            nicht_null]


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"v1": SORTE1, "v2": SORTE2,
            "p1": [2, 3, 4, 5], "q1": [3, 4, 5, 7],
            "p2": [2, 3, 5, 7], "q2": [2, 3, 4, 5],
            "z1": [2, 3, 4, 6], "z2": [3, 5, 7, 9],
            "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


def _bruch(p, welcher=1) -> G:
    """Ein echter Bruch als Faktor — nie eine ganze Zahl."""
    if welcher == 1:
        return G(Rational(p["p1"], p["q1"] + p["p1"]))
    return G(Rational(p["p2"], p["q2"] + p["p2"] + 1))


# ══════════════════════════════════════════════════════════════════════════
# Die zwölf Bauformen
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    """Bruch mal zweigliedrige Klammer, ein Glied wird ganzzahlig:
    (3/4)(x + 4)"""
    st, v1 = p["stufe"], p["v1"]
    f = _bruch(p)
    ganz = G(Integer(f.koeff.q))          # damit ein Glied aufgeht
    if st == 1:
        return bau(f, "++", [G(Integer(1), ((v1, 1),)), ganz])
    if st == 2:
        return bau(f, "+-", [G(Integer(1), ((v1, 1),)), ganz])
    return bau(f, "+-+", [G(Integer(1), ((v1, 1),)), ganz,
                          G(Integer(2 * f.koeff.q), ((v1, 2),))])


BF1 = Bauform("BF1", "Bruch mal Klammer, ein Glied wird ganzzahlig",
    bereiche=BEREICH, bauen=bf1, filter=STANDARD)


def bf2(p):
    """Die Zahl steht vorne — der Anteil aus Erhebungsaufgabe 1b:
    (2/7)(3 + x)"""
    st, v1 = p["stufe"], p["v1"]
    f = _bruch(p)
    if st == 1:
        return bau(f, "++", [G(Integer(p["z1"])), G(Integer(1), ((v1, 1),))])
    if st == 2:
        return bau(f, "+-", [G(Integer(p["z1"])), G(Integer(1), ((v1, 1),))])
    #: Auf C ein drittes Glied MIT Variable — zwei blosse Zahlen in der
    #: Klammer liessen sich vorher zusammenfassen.
    return bau(f, "+-+", [G(Integer(p["z1"])), G(Integer(1), ((v1, 1),)),
                          G(Integer(p["z2"]), ((v1, 2),))])


BF2 = Bauform("BF2", "Die Zahl steht vorne (Erhebungsaufgabe 1b)",
    bereiche=BEREICH, bauen=bf2, filter=STANDARD)


def bf3(p):
    """In der Klammer stehen selbst Brüche:  (9/5)((3/2)k + 15/7)"""
    st, v1 = p["stufe"], p["v1"]
    f = _bruch(p)
    b2 = _bruch(p, 2)
    if st == 1:
        return bau(f, "++", [G(b2.koeff, ((v1, 1),)), G(Integer(p["z1"]))])
    if st == 2:
        return bau(f, "+-", [G(b2.koeff, ((v1, 1),)), G(b2.koeff)])
    return bau(f, "+-+", [G(b2.koeff, ((v1, 1),)), G(b2.koeff),
                          G(Integer(p["z1"]), ((v1, 2),))])


BF3 = Bauform("BF3", "In der Klammer stehen selbst Brüche",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD)


def bf4(p):
    """Der Faktor hebt den Koeffizienten auf — das x wird «nackt»:
    (3/4)((4/3)x − 1)

    Die wichtigste Bauform für Kapitel 15.
    """
    st, v1 = p["stufe"], p["v1"]
    f = _bruch(p)
    kehr = Rational(f.koeff.q, f.koeff.p)
    if st == 1:
        return bau(f, "++", [G(kehr, ((v1, 1),)), G(Integer(1))])
    if st == 2:
        return bau(f, "+-", [G(kehr, ((v1, 1),)), G(Integer(1))])
    return bau(f, "+-+", [G(kehr, ((v1, 1),)), G(Integer(1)),
                          G(kehr, ((v1, 2),))])


BF4 = Bauform("BF4", "Der Faktor hebt den Koeffizienten auf",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """Variable im Faktor, Klammer mit Bruch:  9x((1/2)x² − 5x + 3)"""
    st, v1 = p["stufe"], p["v1"]
    f = G(Integer(p["z2"]), ((v1, 1),))
    b = _bruch(p)
    if st == 1:
        return bau(f, "++", [G(b.koeff, ((v1, 2),)), G(Integer(p["z1"]))])
    if st == 2:
        return bau(f, "++-", [G(b.koeff, ((v1, 2),)),
                              G(Integer(p["z1"]), ((v1, 1),)),
                              G(Integer(p["z2"]))])
    return bau(f, "+--", [G(b.koeff, ((v1, 2),)),
                          G(Integer(p["z1"]), ((v1, 1),)),
                          G(Integer(p["z2"]))])


BF5 = Bauform("BF5", "Variable im Faktor, dreigliedrige Klammer",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD)


def bf6(p):
    """Der Faktor steht rechts:  (8x² + (2/3)x) · (7/6)x"""
    st, v1 = p["stufe"], p["v1"]
    b = _bruch(p)
    f = G(b.koeff, ((v1, 1),))
    if st == 1:
        return bau(f, "++", [G(Integer(p["z2"]), ((v1, 2),)),
                             G(_bruch(p, 2).koeff, ((v1, 1),))],
                   hinten=True)
    if st == 2:
        return bau(f, "+-", [G(Integer(p["z2"]), ((v1, 2),)),
                             G(_bruch(p, 2).koeff, ((v1, 1),))],
                   hinten=True)
    return bau(f, "+-+", [G(Integer(p["z2"]), ((v1, 2),)),
                          G(_bruch(p, 2).koeff, ((v1, 1),)),
                          G(Integer(p["z1"]))], hinten=True)


BF6 = Bauform("BF6", "Der Faktor steht rechts von der Klammer",
    bereiche=BEREICH, bauen=bf6, filter=STANDARD)


# ── Varianten zu BF1 bis BF6 ───────────────────────────────────────────────
# Die Schablone nennt sechs Bauformen. Sechs Varianten kommen dazu, damit
# die Ziehung nicht immer dieselben sechs Formen liefert. Jede ist eine
# echte Abwandlung, keine blosse Zahlenvariante.

def bf7(p):
    """Zwei verschiedene Variablen in der Klammer"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    f = _bruch(p)
    if st == 1:
        return bau(f, "++", [G(Integer(1), ((v1, 1),)),
                             G(Integer(f.koeff.q), ((v2, 1),))])
    if st == 2:
        return bau(f, "+-", [G(Integer(1), ((v1, 1),)),
                             G(Integer(f.koeff.q), ((v2, 1),))])
    return bau(f, "+-+", [G(Integer(1), ((v1, 1),)),
                          G(Integer(f.koeff.q), ((v2, 1),)),
                          G(Integer(f.koeff.q), ((v1, 1), (v2, 1)))])


BF7 = Bauform("BF7", "Zwei verschiedene Variablen in der Klammer",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def bf8(p):
    """Ein Minus steht vor dem Bruch:  −(3/4)(x + 4)"""
    st, v1 = p["stufe"], p["v1"]
    f = _bruch(p)
    ganz = G(Integer(f.koeff.q))
    if st == 1:
        return bau(f, "++", [G(Integer(1), ((v1, 1),)), ganz], minus=True)
    if st == 2:
        return bau(f, "+-", [G(Integer(1), ((v1, 1),)), ganz], minus=True)
    return bau(f, "+-+", [G(Integer(1), ((v1, 1),)), ganz,
                          G(Integer(2 * f.koeff.q), ((v1, 2),))], minus=True)


BF8 = Bauform("BF8", "Ein Minus steht vor dem Bruch",
    bereiche=BEREICH, bauen=bf8, filter=STANDARD)


def bf9(p):
    """Stammbruch als Faktor:  (1/3)(6x + 9)"""
    st, v1 = p["stufe"], p["v1"]
    q = p["q1"] + 1
    f = G(Rational(1, q))
    if st == 1:
        return bau(f, "++", [G(Integer(q * p["z1"]), ((v1, 1),)),
                             G(Integer(q * p["z2"]))])
    if st == 2:
        return bau(f, "+-", [G(Integer(q * p["z1"]), ((v1, 1),)),
                             G(Integer(q * p["z2"]))])
    return bau(f, "+-+", [G(Integer(q * p["z1"]), ((v1, 1),)),
                          G(Integer(q * p["z2"])),
                          G(Integer(q * p["z1"]), ((v1, 2),))])


BF9 = Bauform("BF9", "Stammbruch als Faktor",
    bereiche=BEREICH, bauen=bf9, filter=STANDARD)


def bf10(p):
    """Ganze Zahl mal Klammer mit Brüchen:  6((1/2)x + 2/3)"""
    st, v1 = p["stufe"], p["v1"]
    f = G(Integer(p["z2"] + 3))
    b1, b2 = _bruch(p), _bruch(p, 2)
    if st == 1:
        return bau(f, "++", [G(b1.koeff, ((v1, 1),)), G(b2.koeff)])
    if st == 2:
        return bau(f, "+-", [G(b1.koeff, ((v1, 1),)), G(b2.koeff)])
    return bau(f, "+-+", [G(b1.koeff, ((v1, 1),)), G(b2.koeff),
                          G(b1.koeff, ((v1, 2),))])


BF10 = Bauform("BF10", "Ganze Zahl mal Klammer mit Brüchen",
    bereiche=BEREICH, bauen=bf10, filter=STANDARD)


def bf11(p):
    """Faktor rechts, Variable im Faktor:  (x + 3) · (2/5)x"""
    st, v1 = p["stufe"], p["v1"]
    f = G(_bruch(p).koeff, ((v1, 1),))
    if st == 1:
        return bau(f, "++", [G(Integer(1), ((v1, 1),)),
                             G(Integer(p["z1"]))], hinten=True)
    if st == 2:
        return bau(f, "+-", [G(Integer(1), ((v1, 1),)),
                             G(Integer(p["z1"]))], hinten=True)
    return bau(f, "+-+", [G(Integer(1), ((v1, 1),)), G(Integer(p["z1"])),
                          G(Integer(p["z2"]), ((v1, 2),))], hinten=True)


BF11 = Bauform("BF11", "Faktor rechts, Variable im Faktor",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD)


def bf12(p):
    """Zwei Variablen im Faktor:  (2/3)xy(3x + 6y)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    b = _bruch(p)
    f = G(b.koeff, ((v1, 1), (v2, 1)))
    if st == 1:
        return bau(f, "++", [G(Integer(b.koeff.q), ((v1, 1),)),
                             G(Integer(p["z1"] * b.koeff.q), ((v2, 1),))])
    if st == 2:
        return bau(f, "+-", [G(Integer(b.koeff.q), ((v1, 1),)),
                             G(Integer(p["z1"] * b.koeff.q), ((v2, 1),))])
    return bau(f, "+-+", [G(Integer(b.koeff.q), ((v1, 1),)),
                          G(Integer(p["z1"] * b.koeff.q), ((v2, 1),)),
                          G(Integer(b.koeff.q), ((v1, 1), (v2, 1)))])


BF12 = Bauform("BF12", "Zwei Variablen im Faktor",
    bereiche=BEREICH, bauen=bf12, filter=STANDARD)


S41 = Schablone(
    nr="S41", titel="Bruch mal Klammer",
    lektionen="11.9", erhebung="1b", anleitung=ANLEITUNG,
    levelachse="Struktur des Faktors und Gliederzahl",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee="Das Distributivgesetz gilt auch für Brüche: der Faktor vor "
             "der Klammer wird mit jedem einzelnen Glied darin "
             "multipliziert, und jedes Teilergebnis wird gekürzt.")
