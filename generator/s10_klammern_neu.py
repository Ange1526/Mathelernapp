# -*- coding: utf-8 -*-
"""
S33 · Klammertypen erkennen          (Lektion  10.1)
S34 · Strichoperation vor der Klammer (Lektionen 10.2 – 10.6)
S35 · Punktoperation und Klammer      (Lektionen 10.7 – 10.11)

    «Rechne aus.»
    3 + (4 + 2)      20 − (7 + 5)      3 · (4 − 2)      12 : (2 · 3)

Diese drei ersetzen `s10_klammern.py`. Der alte Generator hatte eine
numerische Levelachse und eine Fehlerdichte von 1,50 — unter dem Richtwert
von 1,6. Und **10.6 ist das häufigste Rücksprungziel im ganzen Netz**: wer
irgendwo an einem Minus vor der Klammer scheitert, landet hier. Diese
Lektion muss darum besonders gut abgedeckt sein.

DER FEHLER, UM DEN SICH ALLES DREHT: ein Minus vor der Klammer dreht JEDES
Vorzeichen darin um. `20 − (7 + 5)` ist `20 − 7 − 5`, nicht `20 − 7 + 5`.
Er wird in jeder Bauform aus der Aufgabe gerechnet.

LEVELACHSE (Teil 2 der drei Schablonen): die Gliederzahl. Reine
Zahlenlektionen — Variablen kommen in Kapitel 10 erst ab 10.12 und gehören
zu S36.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

ANLEITUNG = "Rechne aus."


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════
#
#   Z(3)                       ->  3
#   KL("++", (4, 2))           ->  (4 + 2)        Wert 6
#   KL("+·", (4, 2))           ->  (4 · 2)        Wert 8
#
# Innerhalb einer Klammer verbindet «·» oder «:» statt eines Vorzeichens.
# Das Vorzeichen eines GLIEDS steht im Muster der Aufgabe, wie überall im
# Projekt.


@dataclass(frozen=True)
class Z:
    wert_: int

    @property
    def wert(self):
        return Integer(self.wert_)

    @property
    def text(self) -> str:
        return zeige(Integer(self.wert_))


@dataclass(frozen=True)
class KL:
    """Eine Klammer.  `muster` beschreibt, was zwischen den Zahlen steht:
    «+», «-», «·» oder «:» — das erste Zeichen gilt für das erste Glied."""
    muster: str
    zahlen: tuple

    @property
    def wert(self):
        w = Integer(self.zahlen[0]) * (1 if self.muster[0] != "-" else -1)
        for i, zeichen in enumerate(self.muster[1:]):
            z = Integer(self.zahlen[i + 1])
            if zeichen == "+":
                w += z
            elif zeichen == "-":
                w -= z
            elif zeichen == "·":
                w *= z
            else:
                w = Rational(w, z)
        return w

    @property
    def inhalt(self) -> str:
        raus = (zeige(Integer(self.zahlen[0])) if self.muster[0] != "-"
                else f"{MINUS}{zeige(Integer(self.zahlen[0]))}")
        for i, zeichen in enumerate(self.muster[1:]):
            raus += f" {zeichen if zeichen != '-' else MINUS} " \
                    f"{zeige(Integer(self.zahlen[i + 1]))}"
        return raus

    @property
    def text(self) -> str:
        return f"({self.inhalt})"


@dataclass(frozen=True)
class Kette:
    """Glieder, verbunden mit · oder : — 3 · (4 − 2)"""
    teile: tuple
    ops: tuple = ()

    @property
    def wert(self):
        w = self.teile[0].wert
        for i, op in enumerate(self.ops):
            r = self.teile[i + 1].wert
            w = Rational(w, r) if op == ":" else w * r
        return w

    @property
    def text(self) -> str:
        raus = self.teile[0].text
        for i, op in enumerate(self.ops):
            raus += f" {op} {self.teile[i + 1].text}"
        return raus


def K(*teile, ops=None) -> Kette:
    return Kette(tuple(teile), tuple(ops or ["·"] * (len(teile) - 1)))


def reihe(muster, glieder) -> str:
    raus = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            raus.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            raus.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(raus)


def summe(muster, glieder):
    w = Integer(0)
    for zeichen, g in zip(muster, glieder):
        w += g.wert if zeichen == "+" else -g.wert
    return w


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def _klammern(glieder):
    raus = []
    for g in glieder:
        if isinstance(g, KL):
            raus.append(g)
        elif isinstance(g, Kette):
            raus += [t for t in g.teile if isinstance(t, KL)]
    return raus


def kandidaten(muster, glieder, loesung):
    """Die fünf Fehler aus Teil 5, aus der Aufgabe gerechnet."""
    raus = []
    kl = _klammern(glieder)
    if not kl:
        return raus
    k0 = kl[0]

    #: 1 · DER Fehler von Lektion 10.6: das Minus vor der Klammer gilt nur
    #:     für das erste Glied darin.
    i = next((j for j, g in enumerate(glieder)
              if g is k0 or (isinstance(g, Kette) and k0 in g.teile)), 0)
    if muster[i] == "-" and len(k0.zahlen) > 1:
        ohne = Integer(k0.zahlen[0])
        rest = Integer(0)
        for j, zeichen in enumerate(k0.muster[1:]):
            z = Integer(k0.zahlen[j + 1])
            rest += z if zeichen == "+" else (-z if zeichen == "-" else 0)
        raus.append(F("minus_nur_erstes",
            loesung + 2 * rest if k0.muster[1] in "+-" else loesung,
            "Ein Minus vor der Klammer dreht JEDES Vorzeichen darin um — "
            "auch das zweite und dritte."))

    #: 2 · Die Klammer wurde ignoriert, von links nach rechts gerechnet.
    flach = Integer(0)
    for zeichen, g in zip(muster, glieder):
        if isinstance(g, KL):
            w = Integer(g.zahlen[0])
            for j, zn in enumerate(g.muster[1:]):
                z = Integer(g.zahlen[j + 1])
                w = w + z if zn == "+" else (w - z if zn == "-" else
                                             (w * z if zn == "·"
                                              else Rational(w, z)))
            flach += w if zeichen == "+" else -w
        else:
            flach += g.wert if zeichen == "+" else -g.wert
    raus.append(F("klammer_ignoriert", flach + 1,
        "Was in der Klammer steht, wird zuerst gerechnet."))

    #: 3 · Nur die erste Zahl der Klammer verrechnet.
    nur_erste = Integer(0)
    for zeichen, g in zip(muster, glieder):
        w = Integer(g.zahlen[0]) if isinstance(g, KL) else g.wert
        nur_erste += w if zeichen == "+" else -w
    raus.append(F("nur_erste_zahl", nur_erste,
        "Alle Zahlen der Klammer zählen mit, nicht nur die erste."))

    #: 4 · Das Vorzeichen des Ergebnisses gedreht.
    raus.append(F("vorzeichen", -sympify(loesung),
        "Zähl die Minuszeichen noch einmal."))

    #: 5 · Der Klammerinhalt allein als Antwort.
    raus.append(F("nur_klammer", k0.wert,
        "Das ist der Wert der Klammer. Der Rest der Aufgabe gehört dazu."))

    #: 6 · Alle Zahlen einfach addiert.
    alles = Integer(0)
    for g in glieder:
        if isinstance(g, KL):
            alles += sum(Integer(z) for z in g.zahlen)
        elif isinstance(g, Kette):
            for t in g.teile:
                alles += (sum(Integer(z) for z in t.zahlen)
                          if isinstance(t, KL) else t.wert)
        else:
            alles += g.wert
    raus.append(F("alles_addiert", alles,
        "Nicht alle Zeichen sind Plus — schau genau hin."))

    #: 7 · Die Rechenart vor der Klammer vertauscht — mal statt plus.
    for j, g in enumerate(glieder):
        if isinstance(g, Kette) and len(g.teile) > 1:
            vertauscht = Integer(0)
            for zn, gg in zip(muster, glieder):
                if gg is g:
                    w = sum(t.wert for t in g.teile)
                else:
                    w = gg.wert
                vertauscht += w if zn == "+" else -w
            raus.append(F("mal_statt_plus", vertauscht,
                "Zwischen dem Faktor und der Klammer steht ein Malpunkt, "
                "kein Plus."))
            break

    #: 8 · Nur das erste Glied der Aufgabe gerechnet.
    erstes = glieder[0].wert * (1 if muster[0] == "+" else -1)
    raus.append(F("nur_erstes_glied", erstes,
        "Der ganze Term zählt, nicht nur sein Anfang."))

    #: 9 · Die letzte Zahl der Klammer vergessen.
    if len(k0.zahlen) > 1:
        gekuerzt = KL(k0.muster[:-1], k0.zahlen[:-1])
        ersatz = Integer(0)
        for zeichen, g in zip(muster, glieder):
            if g is k0:
                w = gekuerzt.wert
            elif isinstance(g, Kette) and k0 in g.teile:
                w = Integer(1)
                for j, teil in enumerate(g.teile):
                    x = gekuerzt.wert if teil is k0 else teil.wert
                    if j == 0:
                        w = x
                    else:
                        w = (Rational(w, x) if g.ops[j - 1] == ":"
                             else w * x)
            else:
                w = g.wert
            ersatz += w if zeichen == "+" else -w
        raus.append(F("letzte_zahl_vergessen", ersatz,
            "Zähl die Zahlen in der Klammer nach — eine fehlt."))

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    ziel = sympify(loesung)
    for f in fehler:
        e = f.ergebnis.expr
        if e is None or sympify(e) == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


TIPPS = [
    "Was in der Klammer steht, wird zuerst gerechnet.",
    "Ein Minus vor der Klammer dreht jedes Vorzeichen darin um.",
    "",
]


def bau(muster, glieder, extra=()):
    l = summe(muster, glieder)
    frage = reihe(muster, glieder)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l), l)
    kl = _klammern(glieder)
    schritte = [("Die Klammer suchen", frage)]
    if kl:
        schritte.append(("Zuerst die Klammer ausrechnen",
                         f"{kl[0].text} = {zeige(kl[0].wert)}"))
    schritte.append(("Dann den Rest", zeige(l)))
    return {"frage": frage, "loesung_text": zeige(l),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=set(),
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=fehler),
            "schritte": schritte,
            "tipps": [TIPPS[0], TIPPS[1],
                      f"{kl[0].text} ergibt {zeige(kl[0].wert)}."
                      if kl else f"Das Ergebnis ist {zeige(l)}."]}


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr != 0


def ganz(p, g) -> bool:
    return bool(getattr(g["aufgabe"].loesung.expr, "is_Integer", False))


STANDARD = [kopfrechenbar, fehler_eindeutig, fuenf, nicht_null, ganz]

#: Die Levelachse aller drei Schablonen: die Gliederzahl.
BEREICH = {
    "A": {"a": [3, 4, 5], "b": [2, 3, 4], "c": [2, 5, 7], "stufe": [1]},
    "B": {"a": [8, 12, 15], "b": [3, 5, 7], "c": [2, 3, 6], "stufe": [2]},
    "C": {"a": [20, 25, 18], "b": [4, 8, 11], "c": [2, 3, 4], "stufe": [3]},
}


def _zahlen(p, n):
    """n Zahlen aus dem Vorrat der Stufe."""
    vorrat = [p["a"], p["b"], p["c"], p["b"] + 2, p["c"] + 1, p["b"] + 4]
    return vorrat[:n]


# ══════════════════════════════════════════════════════════════════════════
# S33 · Klammertypen erkennen        (Lektion 10.1)
# ══════════════════════════════════════════════════════════════════════════
#
# Lektion 10.1 heisst «Klammertypen erkennen» und ist im Buch eine
# Sortieraufgabe. Weil die App nur «rechne aus» kennt, steckt das Erkennen
# in der Rechenaufgabe: je nachdem, was vor der Klammer steht und was darin,
# muss man anders vorgehen.

def _kl_zahlen(p, n, muster):
    """Eine Klammer mit n Zahlen, passend zur Stufe."""
    return KL(muster, tuple(_zahlen(p, n)))


def bf33_1(p):
    """Plus vor der Klammer, Plus darin:  3 + (4 + 2)"""
    st = p["stufe"]
    n = st + 1
    return bau("++", [Z(p["a"]), _kl_zahlen(p, n, "+" + "+" * (n - 1))])


BF33_1 = Bauform("BF1", "Plus vor der Klammer, Plus darin",
    bereiche=BEREICH, bauen=bf33_1, filter=STANDARD)


def bf33_2(p):
    """Minus vor der Klammer, Plus darin:  20 − (7 + 5)

    Das ist Lektion 10.6 im Kleinen — der Fehler, der im ganzen Netz am
    häufigsten hierher zurückführt.
    """
    st = p["stufe"]
    n = st + 1
    return bau("+-", [Z(p["a"] * 3), _kl_zahlen(p, n, "+" + "+" * (n - 1))])


BF33_2 = Bauform("BF2", "Minus vor der Klammer, Plus darin",
    bereiche=BEREICH, bauen=bf33_2, filter=STANDARD)


def bf33_3(p):
    """Punkt vor der Klammer, Punkt darin:  3 · (4 · 2)

    Reine Produkte wachsen schnell — mit den grossen Zahlen der Stufe C
    waere `4 · (20 · 4 · 2 · 6)` nicht mehr im Kopf zu rechnen. Darum
    kleine Faktoren, und die Stufe traegt allein die Faktorenzahl.
    """
    st = p["stufe"]
    n = st + 1
    klein = (2, 3, 2, 2)[:n]
    return bau("+", [K(Z(p["b"] if st == 1 else 2),
                       KL("+" + "·" * (n - 1), klein))])


BF33_3 = Bauform("BF3", "Punkt vor der Klammer, Punkt darin",
    bereiche=BEREICH, bauen=bf33_3, filter=STANDARD)


def bf33_4(p):
    """Strich vor der Klammer, Punkt darin:  30 − (4 · 2)"""
    st = p["stufe"]
    n = st + 1
    return bau("+-", [Z(p["a"] * 4), _kl_zahlen(p, n, "+" + "·" * (n - 1))])


BF33_4 = Bauform("BF4", "Strich vor der Klammer, Punkt darin",
    bereiche=BEREICH, bauen=bf33_4, filter=STANDARD)


def bf33_5(p):
    """Punkt vor der Klammer, Strich darin:  3 · (4 − 2)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-", (p["a"], p["b"]))
    elif st == 2:
        kl = KL("+-+", (p["a"], p["b"], p["c"]))
    else:
        kl = KL("+-+-", (p["a"], p["b"], p["c"], 1))
    return bau("+", [K(Z(p["b"]), kl)])


BF33_5 = Bauform("BF5", "Punkt vor der Klammer, Strich darin",
    bereiche=BEREICH, bauen=bf33_5, filter=STANDARD)


def bf33_6(p):
    """Gemischt: Punkt und Strich in der Klammer:  3 · (4 − 2 · 5)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-·", (p["a"] * 3, p["b"], 2))
    elif st == 2:
        kl = KL("+-·+", (p["a"], p["b"], 2, p["c"]))
    else:
        kl = KL("+-·+-", (p["a"], p["b"], 2, p["c"], 1))
    return bau("+", [K(Z(2), kl)])


BF33_6 = Bauform("BF6", "Gemischt: Punkt und Strich in der Klammer",
    bereiche=BEREICH, bauen=bf33_6, filter=STANDARD)


def bf33_7(p):
    """Plus vor der Klammer, Minus darin:  3 + (4 − 2)"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-", (p["a"], p["b"]))
    elif st == 2:
        kl = KL("+-+", (p["a"], p["b"], p["c"]))
    else:
        kl = KL("+-+-", (p["a"], p["b"], p["c"], 1))
    return bau("++", [Z(p["b"]), kl])


BF33_7 = Bauform("BF7", "Plus vor der Klammer, Minus darin",
    bereiche=BEREICH, bauen=bf33_7, filter=STANDARD)


def bf33_8(p):
    """Klammer steht vorne, Punkt dahinter:  (3 + 4) · 2"""
    st = p["stufe"]
    n = st + 1
    return bau("+", [K(_kl_zahlen(p, n, "+" + "+" * (n - 1)), Z(p["b"]))])


BF33_8 = Bauform("BF8", "Klammer vorne, Punkt dahinter",
    bereiche=BEREICH, bauen=bf33_8, filter=STANDARD)


def bf33_9(p):
    """Sonderfall: das Ergebnis ist null:  3 · (4 − 4)"""
    st = p["stufe"]
    a = p["a"]
    if st == 1:
        kl = KL("+-", (a, a))
    elif st == 2:
        kl = KL("+-+-", (a, a, p["b"], p["b"]))
    else:
        #: Sechs Glieder — frueher stand hier versehentlich dieselbe
        #: Klammer wie auf B.
        kl = KL("+-+-+-", (a, a, p["b"], p["b"], p["c"], p["c"]))
    g = bau("+", [K(Z(p["b"]), kl)])
    g["aufgabe"].fehlerkatalog = siebe([
        F("nicht_null_33", Integer(p["b"] * a),
          "In der Klammer steht null — mal null ergibt null."),
        F("klammer_ignoriert_33", Integer(p["b"] + a),
          "Zuerst die Klammer: sie ergibt null."),
        F("eins_33", Integer(1), "Mal null ergibt null, nicht eins."),
        F("faktor_33", Integer(p["b"]),
          "Der Faktor vor der Klammer ändert nichts: null bleibt null."),
        F("minus_33", Integer(-1), "Null bleibt null."),
    ], Integer(0))
    return g


BF33_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH, bauen=bf33_9,
    filter=[kopfrechenbar, fehler_eindeutig, fuenf])


def bf33_10(p):
    """Sonderfall: die Klammer ändert nichts:  2 + (3 · 1)

    Die lehrreichste Bauform der Schablone: die Klammer ist da, aber sie
    ändert am Ergebnis nichts. Eine Klammer bedeutet nicht automatisch
    etwas — man muss hinschauen, was drinsteht.
    """
    st = p["stufe"]
    if st == 1:
        kl = KL("+·", (p["b"], 1))
    elif st == 2:
        kl = KL("+·+", (p["b"], 1, p["c"]))
    else:
        kl = KL("+·+·", (p["b"], 1, p["c"], 1))
    return bau("++", [Z(p["a"]), kl], extra=[
        F("klammer_bedeutet_etwas", Integer(p["a"]) * kl.wert,
          "Vor der Klammer steht ein Plus — da ändert die Klammer nichts. "
          "Mal wäre etwas anderes."),
    ])


BF33_10 = Bauform("BF10", "Sonderfall: die Klammer ändert nichts",
    bereiche=BEREICH, bauen=bf33_10, filter=STANDARD)


def bf33_11(p):
    """Klammer vorne, Strich darin:  (6 − 2) · 3"""
    st = p["stufe"]
    if st == 1:
        kl = KL("+-", (p["a"], p["b"]))
    elif st == 2:
        kl = KL("+-+", (p["a"], p["b"], p["c"]))
    else:
        kl = KL("+-+-", (p["a"], p["b"], p["c"], 1))
    return bau("+", [K(kl, Z(p["b"]))])


BF33_11 = Bauform("BF11", "Klammer vorne, Strich darin",
    bereiche=BEREICH, bauen=bf33_11, filter=STANDARD)


def bf33_12(p):
    """Zwei Klammern nebeneinander:  (3 + 4) + (2 + 5)"""
    st = p["stufe"]
    n = st + 1
    k1 = KL("+" + "+" * (n - 1), tuple(_zahlen(p, n)))
    k2 = KL("+" + "-" * (n - 1), tuple(_zahlen(p, n)[::-1]))
    return bau("++", [k1, k2])


BF33_12 = Bauform("BF12", "Zwei Klammern nebeneinander",
    bereiche=BEREICH, bauen=bf33_12, filter=STANDARD)


S33 = Schablone(
    nr="S33", titel="Klammertypen erkennen",
    lektionen="10.1", erhebung="Vorstufe zu 2b",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl",
    bauformen=[BF33_1, BF33_2, BF33_3, BF33_4, BF33_5, BF33_6,
               BF33_7, BF33_8, BF33_9, BF33_10, BF33_11, BF33_12],
    kernidee=("Was in der Klammer steht, wird zuerst gerechnet. Was vor der "
              "Klammer steht, entscheidet, wie es danach weitergeht."),
)
