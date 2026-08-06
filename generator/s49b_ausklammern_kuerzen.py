# -*- coding: utf-8 -*-
"""
S49B · Kürzen nach dem Ausklammern             (Lektion 14.5)

    «Rechne aus und kürze so weit wie möglich.»
    (3x + 6)/3      (3x + 6)/(x + 2)      (5a − 5b)/(a − b)

Die Lektion sitzt genau zwischen zwei Kapiteln: 14.5 hat 14.4 und 12.5 als
Voraussetzung. Gekürzt wird durch FAKTOREN, nie durch Summanden — und
solange oben eine Summe steht, ist noch gar kein Faktor da. Erst das
Ausklammern macht einen daraus.

DER FEHLER, UM DEN SICH ALLES DREHT: `(3x + 6)/3` wird zu `x + 6`. Die 3
unten wurde gegen die 3 im ersten Summanden gekürzt und der zweite blieb
stehen. Er wird in jeder Bauform aus der Aufgabe gerechnet und steht darum
überall im Katalog.

Die Zielform ist GEKUERZT: wer richtig rechnet, aber nicht fertigkürzt,
bekommt «stimmt — das lässt sich noch kürzen» statt «falsch». Der ungekürzte
Bruch steht darum NICHT im Fehlerkatalog.

LEVELACHSE: Struktur von Zähler und Nenner.

    A   Zähler zweigliedrig, Nenner eine Zahl oder ein Monom
    B   Nenner ist selbst eine Summe · ein Minus kommt dazu
    C   drei Glieder oder zwei Variablen

Die Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from sympy import Integer, cancel, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s9_division import M, _reihe
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus und kürze so weit wie möglich."

SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def T(koeff, *basen) -> M:
    """Ein Monom. Der Koeffizient bleibt positiv — das Vorzeichen sitzt im
    Muster, nie im Glied."""
    return M(Integer(koeff), tuple((s, 1) if not isinstance(s, tuple) else s
                                   for s in basen))


def _summe(muster, glieder):
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += g.wert if zeichen == "+" else -g.wert
    return expand(raus)


def _text(muster, glieder, klammer: bool) -> str:
    t = _reihe(muster, glieder)
    return f"({t})" if klammer and len(glieder) > 1 else t


# ══════════════════════════════════════════════════════════════════════════
# Der Fehlerkatalog, aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def kandidaten(zf, zmus, zq, nf, nmus, nq, loesung):
    """zf · (zq)  über  nf · (nq)."""
    raus = []
    oben = sympify(zf.wert) * _summe(zmus, zq)
    unten = sympify(nf.wert) * _summe(nmus, nq)
    nenner_teil = sympify(nf.wert) * (nq[0].wert if len(nq) == 1
                                      else _summe(nmus, nq))

    #: 1 · Durch einen SUMMANDEN gekürzt statt durch einen Faktor: nur das
    #:     erste Glied oben wurde geteilt, der Rest blieb stehen.
    erstes = sympify(zf.wert) * zq[0].wert
    rest = oben - erstes
    raus.append(F("summand_gekuerzt",
        cancel(erstes / nenner_teil) + rest,
        "Gekürzt wird durch FAKTOREN, nie durch einzelne Summanden. "
        "Solange oben eine Summe steht, muss zuerst ausgeklammert werden."))

    #: 2 · Dasselbe mit dem letzten Glied.
    letztes = sympify(zf.wert) * (zq[-1].wert if zmus[-1] == "+"
                                  else -zq[-1].wert)
    raus.append(F("letzter_summand_gekuerzt",
        cancel(letztes / nenner_teil) + (oben - letztes),
        "Auch das letzte Glied ist ein Summand, kein Faktor."))

    #: 3 · Der Nenner wurde einfach weggelassen.
    raus.append(F("nenner_vergessen", expand(oben),
        "Der Nenner gehört zur Aufgabe — er verschwindet nicht beim "
        "Ausklammern."))

    #: 4 · Zähler und Nenner vertauscht.
    if unten != 0:
        raus.append(F("vertauscht", cancel(unten / oben),
            "Oben steht der Zähler, unten der Nenner. Beim Kürzen bleibt "
            "das so."))

    #: 5 · Subtrahiert statt gekürzt.
    raus.append(F("subtrahiert", expand(oben - unten),
        "Ein Bruchstrich heisst geteilt, nicht minus."))

    #: 6 · Das Vorzeichen des Ergebnisses gedreht.
    raus.append(F("vorzeichen_gesamt", expand(-sympify(loesung)),
        "Zähl die Minuszeichen noch einmal."))

    #: 7 · Nur die Zahlen gekürzt, die Variable stehen gelassen.
    zahl_oben = sympify(zf.koeff)
    zahl_unten = sympify(nf.koeff)
    if zahl_unten not in (0, 1) and zahl_oben != zahl_unten:
        raus.append(F("nur_zahlen_gekuerzt",
            cancel(oben / zahl_unten),
            "Nicht nur die Zahl unten lässt sich kürzen — schau, was noch "
            "in JEDEM Glied oben steckt."))

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    ziel = cancel(sympify(loesung))
    for fe in fehler:
        e = fe.ergebnis.expr
        if e is None:
            continue
        e = cancel(sympify(e))
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(fe)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Bauen
# ══════════════════════════════════════════════════════════════════════════

def bau(zf: M, zmus, zq, nf: M, nmus, nq):
    """Zähler und Nenner entstehen als Faktor mal Klammer — nie umgekehrt.

    Wie bei S42: so kann der Generator gar nicht behaupten, es liesse sich
    etwas kürzen, was sich nicht kürzen lässt.
    """
    zglieder = [_mal(zf, q) for q in zq]
    nglieder = [_mal(nf, q) for q in nq]
    oben = _summe(zmus, zglieder)
    unten = _summe(nmus, nglieder)
    l = cancel(oben / unten)

    otext = _text(zmus, zglieder, klammer=True)
    utext = _text(nmus, nglieder, klammer=True)
    if len(nglieder) == 1 and (sympify(nglieder[0].koeff) != 1
                               and nglieder[0].basen):
        utext = f"({utext})"
    frage = f"{otext}/{utext}"

    fehler = siebe(kandidaten(zf, zmus, zq, nf, nmus, nq, l), l)
    faktor = _mal(zf, M(Integer(1), ()))
    return {
        "frage": frage,
        "loesung_text": zeige(l),
        "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                           zielform=Zielform.GEKUERZT,
                           fehlerkatalog=fehler),
        "schritte": [
            ("Oben und unten getrennt anschauen", frage),
            (f"Im Zähler {zf.text} ausklammern",
             f"{zf.text}·{_text(zmus, zq, klammer=True)}"),
            ("Jetzt steht oben und unten ein Faktor — jetzt darf gekürzt "
             "werden", zeige(l))],
        "tipps": [
            "Gekürzt wird durch Faktoren, nie durch Summanden. Solange oben "
            "eine Summe steht, geht noch nichts.",
            "Klammere zuerst aus, was in JEDEM Glied steckt. Erst dann steht "
            "dort ein Faktor.",
            f"Oben lässt sich {zf.text} ausklammern. Und was steht unten?"],
    }


def _mal(g1: M, g2: M) -> M:
    basen = list(g1.basen)
    for s, e in g2.basen:
        for i, (s2, e2) in enumerate(basen):
            if s2 == s:
                basen[i] = (s, e2 + e)
                break
        else:
            basen.append((s, e))
    return M(sympify(g1.koeff) * sympify(g2.koeff),
             tuple((s, e) for s, e in basen if e != 0))


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def echt_gekuerzt(p, g) -> bool:
    """Es muss wirklich etwas zu kürzen geben — sonst ist es keine Aufgabe
    für diese Lektion."""
    l = sympify(g["aufgabe"].loesung.expr)
    return str(l).replace(" ", "") != g["frage"].replace(" ", "")


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr not in (0, 1, -1)


STANDARD = [kopfrechenbar, fehler_eindeutig, fuenf, echt_gekuerzt,
            nicht_null]


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"v1": SORTE1, "v2": SORTE2,
            "f": [2, 3, 5, 7], "k1": [2, 3, 4, 5], "k2": [3, 5, 7, 9],
            "k3": [2, 3, 5, 7], "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}
EINS = M(Integer(1), ())


# ══════════════════════════════════════════════════════════════════════════
# Die zwölf Bauformen
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    """Zahl ausklammern, Nenner ist dieselbe Zahl:  (3x + 6)/3"""
    st, v1, f = p["stufe"], p["v1"], p["f"]
    zf = M(Integer(f), ())
    if st == 1:
        return bau(zf, "++", [T(1, v1), T(p["k1"])], EINS, "+", [T(f)])
    if st == 2:
        return bau(zf, "+-", [T(1, v1), T(p["k1"])], EINS, "+", [T(f)])
    return bau(zf, "+-+", [T(1, v1), T(p["k1"]), T(p["k2"], v1, v1)],
               EINS, "+", [T(f)])


BF1 = Bauform("BF1", "Zahl ausklammern, Nenner ist dieselbe Zahl",
    bereiche=BEREICH, bauen=bf1, filter=STANDARD)


def bf2(p):
    """Der Nenner ist die Klammer selbst:  (3x + 6)/(x + 2)"""
    st, v1, f = p["stufe"], p["v1"], p["f"]
    zf = M(Integer(f), ())
    if st == 1:
        q = [T(1, v1), T(p["k1"])]
        return bau(zf, "++", q, EINS, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k1"])]
        return bau(zf, "+-", q, EINS, "+-", q)
    q = [T(1, v1), T(p["k1"]), T(p["k2"], v1, v1)]
    return bau(zf, "+-+", q, EINS, "+-+", q)


BF2 = Bauform("BF2", "Der Nenner ist die Klammer selbst",
    bereiche=BEREICH, bauen=bf2, filter=STANDARD)


def bf3(p):
    """Eine Variable ausklammern:  (ax + a)/(x + 1)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(1), ((v2, 1),))
    if st == 1:
        q = [T(1, v1), T(1)]
        return bau(zf, "++", q, EINS, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k1"])]
        return bau(zf, "+-", q, EINS, "+-", q)
    q = [T(1, v1), T(p["k1"]), T(p["k2"], v1, v1)]
    return bau(zf, "+-+", q, EINS, "+-+", q)


BF3 = Bauform("BF3", "Eine Variable ausklammern",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD)


def bf4(p):
    """Oben und unten bleibt eine Zahl übrig:  (2x + 4)/(4x + 8)"""
    st, v1 = p["stufe"], p["v1"]
    zf, nf = M(Integer(p["k1"]), ()), M(Integer(p["k1"] * 2), ())
    if st == 1:
        q = [T(1, v1), T(p["k2"])]
        return bau(zf, "++", q, nf, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k2"])]
        return bau(zf, "+-", q, nf, "+-", q)
    q = [T(1, v1), T(p["k2"]), T(p["k3"], v1, v1)]
    return bau(zf, "+-+", q, nf, "+-+", q)


BF4 = Bauform("BF4", "Oben und unten bleibt eine Zahl übrig",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """Variable ausklammern, Differenz im Nenner:  (a² − ab)/(a − b)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(1), ((v1, 1),))
    if st == 1:
        q = [T(1, v1), T(1, v2)]
        return bau(zf, "++", q, EINS, "++", q)
    if st == 2:
        q = [T(1, v1), T(1, v2)]
        return bau(zf, "+-", q, EINS, "+-", q)
    q = [T(1, v1), T(p["k1"], v2), T(p["k2"])]
    return bau(zf, "+-+", q, EINS, "+-+", q)


BF5 = Bauform("BF5", "Variable ausklammern, Differenz im Nenner",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD)


def bf6(p):
    """Zahl und Variable ausklammern:  (6x² + 9x)/(4x + 6)"""
    st, v1 = p["stufe"], p["v1"]
    zf = M(Integer(p["k1"] * 3), ((v1, 1),))
    nf = M(Integer(p["k1"] * 2), ())
    if st == 1:
        q = [T(p["k2"], v1), T(p["k3"])]
        return bau(zf, "++", q, nf, "++", q)
    if st == 2:
        q = [T(p["k2"], v1), T(p["k3"])]
        return bau(zf, "+-", q, nf, "+-", q)
    q = [T(p["k2"], v1), T(p["k3"]), T(1, v1, v1)]
    return bau(zf, "+-+", q, nf, "+-+", q)


BF6 = Bauform("BF6", "Zahl und Variable ausklammern",
    bereiche=BEREICH, bauen=bf6, filter=STANDARD)


def bf7(p):
    """Der Nenner ist ein Monom:  (x² + xy)/x"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(1), ((v1, 1),))
    if st == 1:
        return bau(zf, "++", [T(1, v1), T(1, v2)], EINS, "+", [T(1, v1)])
    if st == 2:
        return bau(zf, "+-", [T(1, v1), T(p["k1"], v2)],
                   EINS, "+", [T(1, v1)])
    return bau(zf, "+-+", [T(1, v1), T(p["k1"], v2), T(p["k2"])],
               EINS, "+", [T(1, v1)])


BF7 = Bauform("BF7", "Der Nenner ist ein Monom",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def bf8(p):
    """Übrig bleibt eine blosse Zahl:  (5a − 5b)/(a − b)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(p["k2"]), ())
    if st == 1:
        q = [T(1, v1), T(1, v2)]
        return bau(zf, "++", q, EINS, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k1"], v2)]
        return bau(zf, "+-", q, EINS, "+-", q)
    q = [T(1, v1), T(p["k1"], v2), T(p["k3"], v1, v2)]
    return bau(zf, "+-+", q, EINS, "+-+", q)


BF8 = Bauform("BF8", "Übrig bleibt eine blosse Zahl",
    bereiche=BEREICH, bauen=bf8, filter=STANDARD)


def bf9(p):
    """Zwei Variablen, beide gemeinsam:  (2xy + 4y)/(x + 2)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(p["k1"]), ((v2, 1),))
    if st == 1:
        q = [T(1, v1), T(p["k2"])]
        return bau(zf, "++", q, EINS, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k2"])]
        return bau(zf, "+-", q, EINS, "+-", q)
    q = [T(1, v1), T(p["k2"]), T(p["k3"], v1, v1)]
    return bau(zf, "+-+", q, EINS, "+-+", q)


BF9 = Bauform("BF9", "Zwei Variablen, beide gemeinsam",
    bereiche=BEREICH, bauen=bf9, filter=STANDARD)


def bf10(p):
    """Der Nenner ist ein Vielfaches der Klammer:  (3x + 6)/(6x + 12)"""
    st, v1 = p["stufe"], p["v1"]
    zf = M(Integer(p["k2"]), ())
    nf = M(Integer(p["k2"] * p["k1"]), ())
    if st == 1:
        q = [T(1, v1), T(p["k3"])]
        return bau(zf, "++", q, nf, "++", q)
    if st == 2:
        q = [T(1, v1), T(p["k3"])]
        return bau(zf, "+-", q, nf, "+-", q)
    q = [T(1, v1), T(p["k3"]), T(p["k1"], v1, v1)]
    return bau(zf, "+-+", q, nf, "+-+", q)


BF10 = Bauform("BF10", "Der Nenner ist ein Vielfaches der Klammer",
    bereiche=BEREICH, bauen=bf10, filter=STANDARD)


def bf11(p):
    """Eine Potenz im ausgeklammerten Faktor:  (x³ + x²y)/x²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(1), ((v1, 2),))
    if st == 1:
        return bau(zf, "++", [T(1, v1), T(1, v2)],
                   EINS, "+", [M(Integer(1), ((v1, 2),))])
    if st == 2:
        return bau(zf, "+-", [T(1, v1), T(p["k1"], v2)],
                   EINS, "+", [M(Integer(1), ((v1, 2),))])
    return bau(zf, "+-+", [T(1, v1), T(p["k1"], v2), T(p["k2"])],
               EINS, "+", [M(Integer(1), ((v1, 2),))])


BF11 = Bauform("BF11", "Eine Potenz im ausgeklammerten Faktor",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD)


def bf12(p):
    """Zahl mal Variable oben, blosse Variable unten:  (4ax + 6a)/(2a)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    zf = M(Integer(p["k1"] * 2), ((v2, 1),))
    nf = M(Integer(p["k1"]), ((v2, 1),))
    if st == 1:
        return bau(zf, "++", [T(1, v1), T(p["k2"])], nf, "+", [T(1)])
    if st == 2:
        return bau(zf, "+-", [T(1, v1), T(p["k2"])], nf, "+", [T(1)])
    return bau(zf, "+-+", [T(1, v1), T(p["k2"]), T(p["k3"], v1, v1)],
               nf, "+", [T(1)])


BF12 = Bauform("BF12", "Zahl mal Variable oben, Monom unten",
    bereiche=BEREICH, bauen=bf12, filter=STANDARD)


S49B = Schablone(
    nr="S49B", titel="Kürzen nach dem Ausklammern",
    lektionen="14.5", erhebung="", anleitung=ANLEITUNG,
    levelachse="Struktur von Zähler und Nenner",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee="Gekürzt wird durch Faktoren, nie durch Summanden. Solange "
             "oben eine Summe steht, muss zuerst ausgeklammert werden.")
