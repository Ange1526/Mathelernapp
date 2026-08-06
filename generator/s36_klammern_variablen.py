# -*- coding: utf-8 -*-
"""
S36 · Klammern mit Variablen und gemischt      (Lektionen 10.12 – 10.15)

    «Rechne aus.»
    5a − (2a − 3)      4x − (2y − 3z) − y      15y − [5y − (2y − z)]

Das Gegenstück zu S34: dort standen reine Zahlen in der Klammer, hier
kommen die Variablen dazu. Die Kette lautet 10.12 ← 10.3, 4.8 — gleichartige
Terme sind also verfügbar, x² als Term auch (über 4.8), Potenzgesetze nicht.

DER FEHLER, UM DEN SICH ALLES DREHT: ein Minus vor der Klammer dreht JEDES
Vorzeichen darin um, nicht nur das erste. Er wird in jeder Bauform aus der
Aufgabe gerechnet und steht darum überall im Katalog.

Zwei Sonderfälle, die die alte Fassung nicht hatte:

    BF9    das Ergebnis ist null
    BF10   die Variablen heben sich auf, übrig bleibt eine blosse Zahl

Wer erwartet, dass in einer Variablenaufgabe am Schluss eine Variable steht,
hält das für einen Rechenfehler. Genau darum stehen sie hier.

LEVELACHSE (Teil 2): Gliederzahl (zwei bis drei → drei bis vier → vier bis
fünf) und Vorzeichen (ein Minus → zwei Minus → doppeltes Minus in der
Klammer). Verschachtelung ist gesperrt — sie ist eine eigene Bauform (BF8).
Die Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s9_division import M, Su, _reihe, als_text, reihenfolge
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]
SORTE3 = [z, c, w, d]


def F(schluessel, ergebnis, text):
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


@dataclass(frozen=True)
class EK:
    """Eine eckige Klammer — sie steht immer aussen um eine runde.

    Zwei runde Klammern ineinander liest niemand gern; das Lehrmittel
    schreibt darum `15y − [5y − (2y − z)]`.
    """
    muster: str
    glieder: tuple

    @property
    def wert(self):
        raus = Integer(0)
        for zeichen, g in zip(self.muster, self.glieder):
            raus += g.wert if zeichen == "+" else -g.wert
        return raus

    @property
    def text(self) -> str:
        return "[" + _reihe(self.muster, self.glieder) + "]"


KLAMMER = (Su, EK)


# ══════════════════════════════════════════════════════════════════════════
# Rechnen und Anzeigen
# ══════════════════════════════════════════════════════════════════════════

def _std(zeichen, g):
    return g.wert if zeichen == "+" else -g.wert


def _summe(muster, glieder, wie=_std):
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += wie(zeichen, g)
    return expand(raus)


def _flach(muster, glieder, vz=1):
    """Alle Klammern auflösen und die Glieder mit ihrem Zeichen ausgeben."""
    raus = []
    for zeichen, g in zip(muster, glieder):
        s = vz * (1 if zeichen == "+" else -1)
        if isinstance(g, KLAMMER):
            raus += _flach(g.muster, g.glieder, s)
        else:
            raus.append((s, g))
    return raus


def _ohne_klammern(muster, glieder) -> str:
    paare = _flach(muster, glieder)
    return _reihe("".join("+" if s > 0 else "-" for s, _ in paare),
                  [g for _, g in paare])


def _folge(muster, glieder) -> list:
    """Die Variablen in der Reihenfolge, in der sie in der Aufgabe stehen."""
    raus = []
    for _, g in _flach(muster, glieder):
        for s in reihenfolge([g]):
            if s not in raus:
                raus.append(s)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Der Fehlerkatalog, aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def kandidaten(muster, glieder, loesung, folge):
    """Die fünf Fehler aus Teil 5, für jede Bauform aus der Aufgabe."""
    raus = []
    hat_minus_klammer = any(zn == "-" and isinstance(g, KLAMMER)
                            for zn, g in zip(muster, glieder))

    #: 1 · Das Minus vor der Klammer galt nur für das erste Glied darin.
    #:     5a − (2a − 3)  →  3a − 3   statt   3a + 3
    def nur_erstes(zeichen, g):
        if zeichen == "-" and isinstance(g, KLAMMER):
            teil = Integer(0)
            for i, (izn, ig) in enumerate(zip(g.muster, g.glieder)):
                wert = ig.wert if izn == "+" else -ig.wert
                teil += -wert if i == 0 else wert
            return teil
        return _std(zeichen, g)

    if hat_minus_klammer:
        raus.append(F("nur_erstes_glied", _summe(muster, glieder, nur_erstes),
            "Das Minus vor der Klammer gilt für ALLES darin, nicht nur für "
            "das erste Glied."))

    #: 2 · Die Klammer wurde einfach weggelassen, die Zeichen blieben stehen.
    #:     4x − (x − 2x)  →  3x — das ist der Fall «doppeltes Minus».
    def klammer_weg(zeichen, g):
        return g.wert if isinstance(g, KLAMMER) else _std(zeichen, g)

    if hat_minus_klammer:
        raus.append(F("minus_vergessen", _summe(muster, glieder, klammer_weg),
            "Vor der Klammer steht ein Minus. Es dreht jedes Vorzeichen "
            "darin um."))

    #: 3 · Vor einer Plus-Klammer wurde trotzdem alles gedreht.
    def zuviel_gedreht(zeichen, g):
        if zeichen == "+" and isinstance(g, KLAMMER):
            return -g.wert
        return _std(zeichen, g)

    if any(zn == "+" and isinstance(g, KLAMMER)
           for zn, g in zip(muster, glieder)):
        raus.append(F("zuviel_gedreht", _summe(muster, glieder, zuviel_gedreht),
            "Vor dieser Klammer steht ein Plus — darin bleibt jedes "
            "Vorzeichen, wie es ist."))

    #: 4 · Alles addiert, kein einziges Zeichen beachtet.
    def alles_plus(g):
        if isinstance(g, KLAMMER):
            return sum((alles_plus(t) for t in g.glieder), Integer(0))
        return g.wert

    raus.append(F("alles_addiert",
        expand(sum((alles_plus(g) for g in glieder), Integer(0))),
        "Nicht jedes Zeichen in dieser Aufgabe ist ein Plus."))

    #: 5 · Verschiedene Variablen zusammengezogen:  5u − (2v + 3w) → 0
    if len(folge) > 1:
        ersatz = {s: folge[0] for s in folge[1:]}
        raus.append(F("variablen_gemischt", expand(sympify(loesung).subs(ersatz)),
            "Die Variablen sind verschieden — sie lassen sich nicht "
            "zusammenfassen."))

    #: 6 · Eine weggefallene Variable trotzdem hingeschrieben:
    #:     7a − (3a + 4a) + 2  →  7a + 2   statt   2
    erstes = glieder[0]
    if isinstance(erstes, M) and erstes.basen:
        fehlt = any(s not in sympify(loesung).free_symbols
                    for s, _ in erstes.basen)
        if fehlt:
            raus.append(F("variable_bleibt",
                expand(sympify(loesung) + erstes.wert),
                "Die gleichartigen Glieder heben sich vollständig auf. "
                "Dann steht dort auch keine Variable mehr."))

    #: 7 · Das Vorzeichen des ganzen Ergebnisses gedreht.
    raus.append(F("vorzeichen_gesamt", expand(-sympify(loesung)),
        "Zähl die Minuszeichen noch einmal."))

    #: 8 · Nur die Klammer gerechnet, das Glied davor vergessen.
    for zn, g in zip(muster, glieder):
        if isinstance(g, KLAMMER):
            raus.append(F("nur_klammer", expand(_std(zn, g)),
                "Was vor der Klammer steht, gehört zur Aufgabe."))
            break

    #: 9 · Die Klammer ganz weggelassen.
    ohne = [(zn, g) for zn, g in zip(muster, glieder)
            if not isinstance(g, KLAMMER)]
    if ohne:
        raus.append(F("klammer_ignoriert",
            _summe("".join(zn for zn, _ in ohne), [g for _, g in ohne]),
            "Die Klammer verschwindet nicht, sie wird aufgelöst."))

    #: 10 · Ungleichartiges zusammengefasst:  5x + 4  →  9x
    l = sympify(loesung)
    if len(l.free_symbols) == 1:
        s = list(l.free_symbols)[0]
        koeff, konst = l.coeff(s, 1), l.coeff(s, 0)
        if koeff != 0 and konst != 0 and l == koeff * s + konst:
            raus.append(F("ungleichartig", expand((koeff + konst) * s),
                "Eine Zahl und ein Glied mit Variable sind nicht "
                "gleichartig — sie bleiben nebeneinander stehen."))

    #: 11 · Die blosse Zahl am Schluss vergessen.
    if l.is_Add:
        konst = l.as_coeff_Add()[0]
        if konst != 0:
            raus.append(F("zahl_vergessen", expand(l - konst),
                "Die Zahl ohne Variable gehört auch ins Ergebnis."))

    #: 12 · In der Klammer nur bis zum ersten Glied gerechnet, der Rest
    #:      blieb liegen.
    for i, (zn, g) in enumerate(zip(muster, glieder)):
        if zn == "-" and isinstance(g, KLAMMER) and len(g.glieder) > 1:
            rest = list(glieder)
            rest[i] = g.glieder[0]
            raus.append(F("klammer_abgebrochen", _summe(muster, rest),
                "In der Klammer stehen mehrere Glieder. Jedes davon zählt."))
            break

    return raus


def siebe(fehler, loesung):
    """Doppelte weg und alles, was gleich der Lösung ist."""
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
    "Ein Minus vor der Klammer dreht jedes Vorzeichen darin um — auch bei "
    "Variablen.",
    "Arbeite von innen nach aussen und löse eine Klammer nach der anderen "
    "auf.",
    "",
]


def bau(muster, glieder, extra=()):
    l = _summe(muster, glieder)
    frage = _reihe(muster, glieder)
    folge = _folge(muster, glieder)
    text = als_text(l, folge)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l, folge), l)
    return {"frage": frage, "loesung_text": text,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.ZUSAMMENGEFASST,
                               fehlerkatalog=fehler),
            "schritte": [
                ("Klammern auflösen — ein Minus davor dreht jedes Zeichen",
                 _ohne_klammern(muster, glieder)),
                ("Gleichartige Glieder zusammenfassen", text)],
            "tipps": [TIPPS[0], TIPPS[1], f"Am Schluss steht {text}."]}


# ══════════════════════════════════════════════════════════════════════════
# Filter
# ══════════════════════════════════════════════════════════════════════════

def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr != 0


def drei(p, g) -> bool:
    """Für BF9 · Ergebnis null.

    Wo die Lösung null ist, fallen die meisten gerechneten Fehler auf
    denselben Wert — mehr als drei unterscheidbare Einträge gibt es dort
    nicht. Lieber drei echte als fünf ausgedachte.
    """
    return len(g["aufgabe"].fehlerkatalog) >= 3


def hat_variable(p, g) -> bool:
    return bool(sympify(g["aufgabe"].loesung.expr).free_symbols)


STANDARD = [kopfrechenbar, fehler_eindeutig, fuenf, nicht_null]
SONDER = [kopfrechenbar, fehler_eindeutig, fuenf]


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════
#
# Die Levelachse ist der Aufbau, nicht die Zahl. `stufe` ist der einzige
# Eintrag, der sich zwischen A, B und C unterscheidet.

def _vorrat(stufe):
    return {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3,
            "k1": [2, 3, 4, 5], "k2": [2, 3, 5, 7], "k3": [1, 2, 3, 4],
            "z1": [2, 3, 4, 5, 7], "z2": [1, 2, 3, 4, 6],
            "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


def T(koeff, var, exp=1):
    """Ein Glied mit Variable. Der Koeffizient bleibt immer positiv —
    das Vorzeichen sitzt im Muster, nie im Glied."""
    return M(Integer(koeff), ((var, exp),))


def Z(wert):
    return M(Integer(wert), ())


# ══════════════════════════════════════════════════════════════════════════
# Die zwölf Bauformen
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    """Plus vor der Klammer, nur Variablen:  3x + (2x − x)"""
    st, vr = p["stufe"], p["v1"]
    innen = [T(p["k1"], vr), T(p["k2"], vr), T(p["k3"], vr),
             T(p["k2"] + 1, vr)][:st + 1]
    mus = ("+-+-")[:st + 1]
    return bau("++", [T(p["k1"] + 5, vr), Su(mus, tuple(innen))])


BF1 = Bauform("BF1", "Plus vor der Klammer, nur Variablen",
    bereiche=BEREICH, bauen=bf1, filter=STANDARD)


def bf2(p):
    """Minus vor der Klammer, Variable und Zahl darin:  5a − (2a − 3)"""
    st, vr = p["stufe"], p["v1"]
    if st == 3:
        innen = (T(p["k1"], vr), Z(p["z1"]), T(p["k3"], vr))
        mus = "+-+"
    else:
        innen = (T(p["k1"], vr), Z(p["z1"]))
        mus = "++" if st == 1 else "+-"
    return bau("+-", [T(p["k1"] + p["k2"] + 3, vr), Su(mus, innen)])


BF2 = Bauform("BF2", "Minus vor der Klammer, Variable und Zahl darin",
    bereiche=BEREICH, bauen=bf2, filter=STANDARD)


def bf3(p):
    """Zahl vorne, Klammer mit Variable:  4 − (2x − 3)"""
    st, vr = p["stufe"], p["v1"]
    kl = Su("+-", (T(p["k1"], vr), Z(p["z1"])))
    if st == 1:
        return bau("+-", [Z(p["z1"] + p["z2"] + 4), kl])
    if st == 2:
        return bau("+-+", [Z(p["z1"] + p["z2"] + 4), kl, T(p["k3"], vr)])
    return bau("+-+-", [Z(p["z1"] + p["z2"] + 4), kl, T(p["k3"], vr),
                        Z(p["z2"])])


BF3 = Bauform("BF3", "Zahl vorne, Klammer mit Variable",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD)


def bf4(p):
    """Zwei Klammern hintereinander:  (3a + 2) − (a − 4)"""
    st, vr = p["stufe"], p["v1"]
    k1 = Su("++", (T(p["k1"] + 2, vr), Z(p["z1"])))
    k2 = Su("++" if st == 1 else "+-", (T(p["k3"], vr), Z(p["z2"])))
    if st == 3:
        k3 = Su("++", (T(p["k2"], vr), Z(p["z2"] + 1)))
        return bau("+--", [k1, k2, k3])
    return bau("+-", [k1, k2])


BF4 = Bauform("BF4", "Zwei Klammern hintereinander",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """Verschiedene Variablen in der Klammer:  5u − (2v + 3w)"""
    st = p["stufe"]
    v1, v2, v3 = p["v1"], p["v2"], p["v3"]
    if st == 1:
        return bau("+-", [T(p["k1"], v1),
                          Su("++", (T(p["k2"], v2), T(p["k3"], v3)))])
    if st == 2:
        return bau("+-", [T(p["k1"], v1),
                          Su("++-", (T(p["k2"], v2), T(p["k3"], v3),
                                     T(1, v2)))])
    return bau("+--", [T(p["k1"] + 2, v1),
                       Su("+-", (T(p["k2"], v2), T(p["k3"] + 2, v3))),
                       T(1, v2)])


BF5 = Bauform("BF5", "Verschiedene Variablen in der Klammer",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD)


def bf6(p):
    """Plus vor der Klammer, gemischter Inhalt:  2x + (3x + 4)"""
    st, vr = p["stufe"], p["v1"]
    kl = Su("++" if st == 1 else "+-", (T(p["k2"], vr), Z(p["z1"])))
    if st == 1:
        return bau("++", [T(p["k1"], vr), kl])
    if st == 2:
        return bau("+++", [T(p["k1"], vr), kl, Z(p["z2"])])
    return bau("++-", [T(p["k1"] + 3, vr), kl,
                       Su("++", (T(p["k3"], vr), Z(p["z2"] + 2)))])


BF6 = Bauform("BF6", "Plus vor der Klammer, gemischter Inhalt",
    bereiche=BEREICH, bauen=bf6, filter=STANDARD)


def bf7(p):
    """Mit Potenzen:  8x² − (4x + 3x²)

    x² darf hier als Term stehen (über 4.8) — die Potenzgesetze liegen
    NICHT in der Kette, es wird also nie x² · x³ gerechnet.
    """
    st, vr = p["stufe"], p["v1"]
    if st == 1:
        return bau("+-", [T(p["k1"] + 4, vr, 2),
                          Su("++", (T(p["k2"], vr), T(p["k3"], vr, 2)))])
    if st == 2:
        return bau("+-", [T(p["k1"] + 4, vr, 2),
                          Su("+-+", (T(p["k2"], vr, 2), T(p["k3"], vr),
                                     T(1, vr, 2)))])
    innen = Su("+-", (T(p["k3"] + 2, vr, 2), T(p["k2"] + 2, vr)))
    aussen = EK("+-", (T(p["k1"], vr), innen))
    return bau("+-", [T(p["k1"] + 4, vr, 2), aussen],
               extra=[_von_aussen("+-", [T(p["k1"] + 4, vr, 2), aussen],
                                  innen)])


BF7 = Bauform("BF7", "Mit Potenzen",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def _von_aussen(muster, glieder, innen):
    """Verschachtelt von aussen nach innen gerechnet.

    Die innerste Klammer bekommt dann das falsche Vorzeichen — genau der
    Fehler aus Teil 5:  15y − [5y − (2y − z)]  →  8y + z  statt  12y − z.
    """
    l = _summe(muster, glieder)
    return F("von_aussen", expand(l - 2 * innen.wert),
             "Verschachtelte Klammern werden von innen nach aussen "
             "aufgelöst, nicht umgekehrt.")


def bf8(p):
    """Verschachtelte Klammern:  15y − [5y − (2y − z)]"""
    st = p["stufe"]
    v1, v2 = p["v1"], p["v2"]
    if st == 1:
        return bau("+-", [T(1, v1), Su("+-", (T(1, v2), T(1, p["v3"])))])
    innen = Su("+-", (T(p["k3"], v1), T(1, v2)))
    if st == 2:
        aussen = EK("+-", (T(p["k1"], v1), innen))
        mus, gl = "+-", [T(p["k1"] + p["k2"] + 5, v1), aussen]
    else:
        aussen = EK("+-+", (T(p["k3"], v1), innen, T(1, v2)))
        mus, gl = "+--", [T(p["k1"] + 2, v1), Z(p["z1"]), aussen]
    return bau(mus, gl, extra=[_von_aussen(mus, gl, innen)])


BF8 = Bauform("BF8", "Verschachtelte Klammern",
    bereiche=BEREICH, bauen=bf8, filter=STANDARD)


def bf9(p):
    """Sonderfall: das Ergebnis ist null:  3x − (3x)"""
    st, vr = p["stufe"], p["v1"]
    if st == 1:
        return bau("+-", [T(p["k1"], vr), Su("+", (T(p["k1"], vr),))])
    if st == 2:
        kl = Su("++", (T(p["k1"], vr), Z(p["z1"])))
        return bau("+-", [kl, kl])
    return bau("+--", [T(p["k1"] * 2, vr),
                       Su("++", (T(p["k1"], vr), Z(p["z1"]))),
                       Su("+-", (T(p["k1"], vr), Z(p["z1"])))])


BF9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH, bauen=bf9,
    filter=[kopfrechenbar, fehler_eindeutig, drei])


def bf10(p):
    """Sonderfall: die Variablen fallen weg:  7a − (3a + 4a) + 2"""
    st, vr = p["stufe"], p["v1"]
    k1, k2 = p["k1"], p["k2"]
    kl = Su("++", (T(k1, vr), T(k2, vr)))
    if st == 1:
        return bau("+-", [T(k1 + k2, vr), kl])
    if st == 2:
        return bau("+-+", [T(k1 + k2, vr), kl, Z(p["z1"])])
    return bau("+-+-", [T(k1 + k2, vr), kl, T(p["k3"], vr), Z(p["z1"])])


BF10 = Bauform("BF10", "Sonderfall: die Variablen fallen weg",
    bereiche=BEREICH, bauen=bf10, filter=SONDER)


def bf11(p):
    """Klammer ganz vorne, mit Minus davor:  −(2x − 5)"""
    st, vr = p["stufe"], p["v1"]
    kl = Su("+-", (T(p["k1"], vr), Z(p["z1"])))
    if st == 1:
        return bau("-", [kl])
    if st == 2:
        return bau("-+", [Su("++", (T(p["k1"], vr), Z(p["z1"]))),
                          T(p["k3"], vr)])
    return bau("--+", [kl, Su("++", (T(p["k2"], vr), Z(p["z2"]))),
                       T(1, vr)])


BF11 = Bauform("BF11", "Klammer ganz vorne, mit Minus davor",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD)


def bf12(p):
    """Doppeltes Minus in der Klammer:  4x − (x − 2x)"""
    st, vr = p["stufe"], p["v1"]
    kl = Su("+-", (T(p["k3"], vr), T(p["k3"] + p["k1"], vr)))
    if st == 1:
        return bau("+-", [T(p["k1"] + 3, vr), kl])
    if st == 2:
        return bau("+--", [T(p["k1"] + 5, vr), kl, T(1, vr)])
    return bau("+--", [T(p["k1"] + 6, vr), kl,
                       Su("+-", (T(p["k2"], vr), T(1, vr)))])


BF12 = Bauform("BF12", "Doppeltes Minus in der Klammer",
    bereiche=BEREICH, bauen=bf12, filter=STANDARD)


S36 = Schablone(
    nr="S36", titel="Klammern mit Variablen und gemischt",
    lektionen="10.12 – 10.15", erhebung="2b", anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee="Ein Minus vor der Klammer dreht jedes Vorzeichen darin um. "
             "Danach werden nur Glieder mit derselben Variablen "
             "zusammengefasst — manchmal bleibt gar keine übrig.")
