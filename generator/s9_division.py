# -*- coding: utf-8 -*-
"""
S30 · Terme dividieren, einfache Fälle          (Lektionen 9.1 – 9.3)
S31 · Monome mit Potenzen dividieren            (Lektionen 9.4 – 9.5)
S32 · Division in längeren Termen einordnen     (Lektion  9.6)

    «Rechne aus.»
    6x : 3      12ab : (4a)      21a²b² : (7ab)      12ab + 21ab : (7a)

Damit ist Kapitel 9 vollständig und Erhebungsaufgabe 2c abgedeckt: dort steht
`21a²b² : (7ab)` mitten in einem längeren Term. Das Dividieren selbst ist
S31, die Einordnung in den Term ist S32.

Die drei bauen aufeinander auf:

    S30   nackte Division, jede Variable kommt höchstens einfach vor.
          Potenzen gibt es hier noch nicht — die Kette 9.3 ← 9.2 ← 9.1 ← 5.1
          führt nicht über Kapitel 7.
    S31   mit Potenzen und mit Summen im Zähler. Das ist 9.4, wo K7 dazukommt.
    S32   die Division steht in einem Term mit Plus und Minus ringsherum.

LEVELACHSE (Teil 2 der drei Schablonen, wörtlich):

    S30   Vorzeichen         alles positiv →  ein Minus      →  zwei Minus
    S31   Anzahl Variablen   eine          →  eine bis zwei  →  zwei bis drei
    S31   Vorzeichen         positiv       →  ein Minus      →  zwei Minus
    S32   Anzahl Glieder     zwei          →  zwei           →  drei
    S32   Vorzeichen         alles positiv →  ein Minus      →  mehrere Minus

Bei S30 ist das Vorzeichen der einzige Regler, den Teil 2 nennt — «der
wichtigste Regler hier», steht dort. Das ist strukturell und nicht numerisch:
ein Minus mehr ist ein Zeichen mehr, keine grössere Zahl. Was die Bauformen
trennt, bleibt gesperrt: wodurch geteilt wird und wie viele Variablen
vorkommen.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Expr, Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import fehler_eindeutig, kopfrechenbar, loesung_nicht_null
from .s22_s23_potenzen import hoch
from .schablone import Bauform, Schablone

a, b, c, d, k, m, n, p_, q, u, v, w, x, y, z = symbole(
    "a b c d k m n p q u v w x y z")
VARS = {"a", "b", "c", "d", "k", "m", "n", "p", "q",
        "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

SORTE1 = [x, a, u, m, p_]
SORTE2 = [y, b, v, n, q]
#: Ohne d: aus den Plaetzen a, n und d entsteht sonst das Monom «and», und
#: das ist ein Schluesselwort — der Parser weist die richtige Antwort dann
#: als Eingabefehler ab. Beim Testlauf mit «5and» aufgetreten.
SORTE3 = [z, c, w, k]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════
#
#   M(6, ((x, 1),))          ->  6x
#   M(-42, ((k, 2),))        ->  −42k²
#   M(3)                     ->  3
#   Div(M(6,(x,1)), M(3))    ->  6x : 3
#   Div(Sum, M(3))           ->  (6x + 9) : 3
#
# Das Vorzeichen eines GLIEDS steht im Muster, nicht im Glied — wie in
# `s6_punktrechnung`. Das Vorzeichen eines DIVISORS gehört dagegen zum
# Divisor: bei `20y : (−5)` ist das Minus Teil der Aufgabe, nicht des Terms.


@dataclass(frozen=True)
class M:
    """Ein Monom."""
    koeff: Expr = Integer(1)
    basen: tuple = ()

    @property
    def monom(self) -> Expr:
        raus = Integer(1)
        for s, e in self.basen:
            raus *= s ** e
        return raus

    @property
    def wert(self) -> Expr:
        return sympify(self.koeff) * self.monom

    @property
    def text(self) -> str:
        kk = sympify(self.koeff)
        if not self.basen:
            return zeige(kk)
        vorne = "" if kk == 1 else (MINUS if kk == -1 else zeige(kk))
        return vorne + "".join(zeige(s) + (hoch(e) if e > 1 else "")
                               for s, e in self.basen)


@dataclass(frozen=True)
class Su:
    """Eine Summe in Klammern als Zähler:  (18u⁴ − 12u³ + 2u²)"""
    muster: str
    glieder: tuple

    @property
    def wert(self) -> Expr:
        raus = Integer(0)
        for zeichen, g in zip(self.muster, self.glieder):
            raus += g.wert if zeichen == "+" else -g.wert
        return raus

    @property
    def text(self) -> str:
        return "(" + _reihe(self.muster, self.glieder) + ")"


def als_divisor(t) -> str:
    """Klammern um den Divisor — aber nur, wo sie nötig sind.

    So steht es in den Schablonen: `6x : 3` und `x⁵ : x²` ohne, aber
    `12ab : (4a)` und `20y : (−5)` mit. Die Klammer trennt den Divisor
    dort, wo er aus mehr als einem Stück besteht oder ein Vorzeichen trägt.
    """
    kk = sympify(t.koeff)
    braucht = (kk < 0                              # (−5), (−7k)
               or len(t.basen) > 1                 # (u²v³w⁴)
               or (t.basen and kk != 1))           # (4a), (7ab)
    return f"({t.text})" if braucht else t.text


@dataclass(frozen=True)
class Div:
    zaehler: object
    nenner: M

    @property
    def wert(self) -> Expr:
        """`expand` ist hier Pflicht, nicht Kosmetik.

        SymPy laesst `(18u⁴ − 12u³ + 2u²)/(2u²)` unausgewertet stehen. Ohne
        `expand` waere die Musterloesung dieser Bruch, und der Test meldete
        «unfertig: du kannst noch zusammenfassen» — zu Recht.
        """
        from sympy import expand
        return expand(sympify(self.zaehler.wert) / self.nenner.wert)

    @property
    def text(self) -> str:
        return f"{self.zaehler.text} : {als_divisor(self.nenner)}"


@dataclass(frozen=True)
class Pr:
    """Ein Produkt als Glied:  4a · 2"""
    faktoren: tuple

    @property
    def wert(self) -> Expr:
        raus = Integer(1)
        for f in self.faktoren:
            raus *= f.wert
        return raus

    @property
    def text(self) -> str:
        return " · ".join(f.text for f in self.faktoren)


def _reihe(muster, glieder) -> str:
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def summe(muster, glieder) -> Expr:
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += g.wert if zeichen == "+" else -g.wert
    return raus


def reihenfolge(glieder) -> list:
    """Die Variablen in der Reihenfolge, in der sie in der Aufgabe stehen."""
    raus = []
    stapel = list(glieder)
    while stapel:
        g = stapel.pop(0)
        if isinstance(g, M):
            for s, _ in g.basen:
                if s not in raus:
                    raus.append(s)
        elif isinstance(g, Div):
            stapel = [g.zaehler, g.nenner] + stapel
        elif isinstance(g, (Pr,)):
            stapel = list(g.faktoren) + stapel
        elif isinstance(g, Su):
            stapel = list(g.glieder) + stapel
    return raus


def als_text(wert, folge) -> str:
    """Das Ergebnis in der Reihenfolge der Aufgabe hinschreiben.

    SymPy sortiert Produkte alphabetisch um — aus `2u` mal `v` wird beim
    Ausgeben `uv`, aber aus `x` mal `q` wird `qx`. Wo die Reihenfolge zählt,
    wird sie hier selbst gesetzt (CLAUDE.md, «SymPy sortiert um»).
    """
    wert = sympify(wert)
    if wert.is_Add:
        return zeige_summe(*_summanden(wert, folge))
    return _monom_text(wert, folge)


def _summanden(wert, folge):
    """Die Summanden nach der Reihenfolge der Variablen sortiert."""
    def schluessel(t):
        symbole_ = [s for s in folge if s in t.free_symbols]
        return (folge.index(symbole_[0]) if symbole_ else len(folge), str(t))
    return sorted(wert.args, key=schluessel)


def _monom_text(wert, folge) -> str:
    kk, rest = wert.as_coeff_Mul()
    potenzen = rest.as_powers_dict()
    if any(not s.is_Symbol for s in potenzen) or not potenzen:
        return zeige(wert)
    txt = "" if kk == 1 else (MINUS if kk == -1 else zeige(kk))
    for s in folge:
        e = potenzen.get(s)
        if e is None:
            continue
        txt += zeige(s) + (hoch(int(e)) if e > 1 else "")
    return txt or zeige(wert)


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 5 der drei Schablonen nennt zusammen zwölf Fehler, acht davon
# doppelt. Sie stehen hier einmal und gelten für jede Bauform, in der sie
# überhaupt entstehen können.


def _divisionen(glieder) -> list:
    return [g for g in glieder if isinstance(g, Div)]


def _ersetzt(muster, glieder, div, neuer_wert) -> Expr:
    """Die ganze Summe, aber mit einem anderen Wert für EINE Division."""
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        w = neuer_wert if g is div else g.wert
        raus += w if zeichen == "+" else -w
    return raus


def kandidaten(muster, glieder, loesung):
    raus = []
    divs = _divisionen(glieder)
    if not divs:
        return raus
    d = divs[0]
    n = d.nenner
    zaehler_ist_summe = isinstance(d.zaehler, Su)

    #  1 · Die Variablen wurden nicht gekürzt.
    #      12ab : (4a) -> 3ab   ·   21a²b² : (7ab) -> 3a²b²
    if n.basen and not zaehler_ist_summe:
        falsch = (sympify(d.zaehler.koeff) / n.koeff) * d.zaehler.monom
        raus.append(F("nicht_gekuerzt", _ersetzt(muster, glieder, d, falsch),
            f"Beim Dividieren fällt jede Variable weg, die oben UND unten "
            f"steht: {d.text} ist {zeige(d.wert)}."))

    #  2 · Nur die Zahl geteilt, die Variable weggelassen.
    #      6x : 3 -> 2
    if not n.basen and not zaehler_ist_summe and d.zaehler.basen:
        falsch = sympify(d.zaehler.koeff) / n.koeff
        raus.append(F("variable_weggelassen",
            _ersetzt(muster, glieder, d, falsch),
            f"Geteilt wird nur die Zahl. {zeige(d.zaehler.monom)} steht nur "
            f"oben und bleibt stehen: {zeige(d.wert)}."))

    #  3 · Vorzeichen falsch gezählt.  −42k² : (−7k) -> −6k
    if loesung != 0 and (sympify(n.koeff) < 0
                         or (not zaehler_ist_summe
                             and sympify(d.zaehler.koeff) < 0)):
        raus.append(F("vorzeichen", -loesung,
            "Minus durch minus gibt plus. Zähl die Minuszeichen: eine "
            "gerade Anzahl ergibt ein positives Ergebnis."))

    #  4 · Nur das erste Glied der Summe geteilt.
    #      (−16mx + 40my) : (−8m) -> 2x + 40my
    if zaehler_ist_summe:
        s = d.zaehler
        erstes = s.glieder[0].wert / n.wert
        rest = Integer(0)
        for zeichen, g in list(zip(s.muster, s.glieder))[1:]:
            rest += g.wert if zeichen == "+" else -g.wert
        raus.append(F("nur_erstes_glied",
            _ersetzt(muster, glieder, d, erstes + rest),
            "Jedes Glied der Summe wird einzeln geteilt, nicht nur das "
            "erste."))

        #  5 · Das Glied, das ganz aufgeht, wurde weggelassen.
        #      (18u⁴ − 12u³ + 2u²) : (−2u²) -> −9u² + 6u
        for i, g in enumerate(s.glieder):
            if abs(sympify(g.wert / n.wert)) == 1:
                ohne = Integer(0)
                for j, (zeichen, gg) in enumerate(zip(s.muster, s.glieder)):
                    if j == i:
                        continue
                    ohne += (gg.wert if zeichen == "+" else -gg.wert) / n.wert
                raus.append(F("glied_weggelassen",
                    _ersetzt(muster, glieder, d, ohne),
                    f"Ein Glied geht ganz auf — dann bleibt eine 1 oder −1 "
                    f"stehen, nicht nichts."))
                break

    #  6 · Die ganze Summe davor mitgeteilt.
    #      12ab + 21ab : (7a) -> (12ab + 21ab) : (7a)
    i = next((j for j, g in enumerate(glieder) if g is d), 0)
    if i > 0:
        davor = Integer(0)
        for zeichen, g in list(zip(muster, glieder))[:i]:
            davor += g.wert if zeichen == "+" else -g.wert
        alles = (davor + d.zaehler.wert) / n.wert
        for zeichen, g in list(zip(muster, glieder))[i + 1:]:
            alles += g.wert if zeichen == "+" else -g.wert
        raus.append(F("ganze_summe_geteilt", alles,
            f"Ohne Klammer gilt die Division nur für das Glied direkt davor "
            f"— hier nur für {d.zaehler.text}."))

    #  7 · Die Division auf das Glied DAHINTER bezogen.
    #      6x : 3 + 4x -> 6x : (3 + 4x)
    if i + 1 < len(glieder) and not zaehler_ist_summe:
        dahinter = glieder[i + 1].wert
        if muster[i + 1] == "-":
            dahinter = -dahinter
        nenner_falsch = n.wert + dahinter
        if nenner_falsch != 0:
            falsch = sympify(d.zaehler.wert) / nenner_falsch
            for zeichen, g in list(zip(muster, glieder))[:i]:
                falsch += g.wert if zeichen == "+" else -g.wert
            raus.append(F("nach_hinten_bezogen", falsch,
                f"Geteilt wird durch {n.text}, nicht durch alles, was "
                f"dahinter steht."))

    return raus


def siebe(fehler, loesung):
    """Doppelte und die Lösung selbst aus dem Katalog entfernen."""
    raus, gesehen = [], set()
    ziel = sympify(loesung)
    for f in fehler:
        e = f.ergebnis.expr
        if e is None or sympify(e) == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Der gemeinsame Bauplan
# ══════════════════════════════════════════════════════════════════════════

TIPPS30 = [
    "Beim Dividieren werden die Zahlen geteilt, und eine Variable fällt weg, "
    "wenn sie oben und unten steht.",
    "Geh die Zahl und jede Variable einzeln durch.",
    "",
]

TIPPS31 = [
    "Beim Dividieren werden die Zahlen geteilt und die Hochzahlen "
    "subtrahiert.",
    "Steht im Zähler eine Summe, wird jedes Glied einzeln geteilt.",
    "",
]

TIPPS32 = [
    "Eine Division ist eine Punktoperation und wird vor dem Plus und Minus "
    "ringsherum ausgeführt.",
    "Schau genau, was geteilt wird: nur das Glied direkt vor dem "
    "Doppelpunkt, nicht die ganze Summe.",
    "",
]


def bau(muster, glieder, extra=(), tipps=None, loesung=None,
        loesung_text=None, sorten=None, zielform=Zielform.ZUSAMMENGEFASST):
    l = summe(muster, glieder) if loesung is None else sympify(loesung)
    folge = reihenfolge(glieder)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l), l)
    frage = _reihe(muster, glieder)
    text = loesung_text or als_text(l, folge)
    divs = _divisionen(glieder)
    schritte = [("Term durchgehen und die Division suchen", frage)]
    if divs:
        d = divs[0]
        schritte += [
            ("Prüfen, was genau geteilt wird",
             f"nur {d.zaehler.text}, nicht der ganze Term"),
            ("Vorzeichen bestimmen und die Zahlen teilen",
             f"{d.text} = {als_text(d.wert, folge)}"),
        ]
    schritte.append(("Ergebnis", text))
    grund = tipps or TIPPS30
    konkret = (f"{divs[0].text} ergibt {als_text(divs[0].wert, folge)}."
               if divs else f"Das Ergebnis ist {text}.")
    return {"frage": frage, "loesung_text": text, "glieder": glieder,
            "muster": muster, "sorten": sorten or [],
            "teile": _teile(l, folge),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=zielform, fehlerkatalog=fehler),
            "schritte": schritte,
            "tipps": [grund[0], grund[1], konkret]}


def _teile(l, folge):
    l = sympify(l)
    return [t.as_coeff_Mul()[1] for t in (l.args if l.is_Add else (l,))]


# ── Filter ────────────────────────────────────────────────────────────────

def hat_fehler(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 1


def ganzzahlig(p, g) -> bool:
    """Kein Bruch, wo keiner sein soll.

    Teil 1 von S31 lässt bei BF4 auf Level C ausdrücklich einen Bruch zu
    (`−3uv³ : (−6uv)` ergibt `v²/2`), aber die Schablone sagt dazu: solche
    Fälle zulassen, nicht häufen. Überall sonst muss die Division aufgehen.
    """
    l = g["aufgabe"].loesung.expr
    for t in (l.args if l.is_Add else (l,)):
        koeff, _ = sympify(t).as_coeff_Mul()
        if koeff.is_Rational and koeff.q != 1:
            return False
    return True


def sorten_bleiben(p, g) -> bool:
    erwartet = g.get("sorten") or []
    if not erwartet:
        return True
    vorhanden = {str(t) for t in g["teile"]}
    return all(str(s) in vorhanden for s in erwartet)


STANDARD = [kopfrechenbar, fehler_eindeutig, hat_fehler, ganzzahlig,
            sorten_bleiben]


def verschieden(*namen):
    def f(p, g):
        werte = [str(p[nn]) for nn in namen if nn in p]
        return len(set(werte)) == len(werte)
    return f


ZWEI = STANDARD + [verschieden("var", "var2")]
DREI = STANDARD + [verschieden("var", "var2", "var3")]


# ══════════════════════════════════════════════════════════════════════════
# S30 · Terme dividieren, einfache Fälle        (Lektionen 9.1 – 9.3)
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 2: das Vorzeichen ist der Regler — alles positiv, ein Minus, zwei
# Minus. Potenzen gibt es hier nicht, jede Variable kommt höchstens einfach
# vor: die Kette 9.3 ← 9.2 ← 9.1 ← 5.1 führt nicht über Kapitel 7.

#: (Vorzeichen oben, Vorzeichen unten) je Level.
VZ = {"A": [(1, 1)], "B": [(-1, 1), (1, -1)], "C": [(-1, -1)]}

ZAHL30 = [2, 3, 4, 5, 6, 7]


def bau30(muster, glieder, extra=(), **kw):
    kw.setdefault("tipps", TIPPS30)
    return bau(muster, glieder, extra=extra, **kw)


def _vz(p):
    return p["vz"]


def bf30_1(p):
    """Term durch Zahl:  6x : 3"""
    v1, t, n = p["var"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t * n), ((v1, 1),)),
                           M(Integer(un * t)))])


BEREICH30 = {lv: {"var": SORTE1, "var2": SORTE2, "teiler": ZAHL30,
                  "faktor": [2, 3, 4, 5, 6], "vz": VZ[lv]}
             for lv in ("A", "B", "C")}

BF30_1 = Bauform("BF1", "Term durch Zahl",
    bereiche=BEREICH30, bauen=bf30_1, filter=STANDARD)


def bf30_2(p):
    """Term durch die eigene Variable — sie fällt weg:  6x : x"""
    v1, t = p["var"], p["teiler"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t), ((v1, 1),)),
                           M(Integer(un), ((v1, 1),)))], extra=[
        F("variable_geblieben", Integer(o * t * un) * v1,
          f"Das {zeige(v1)} steht oben und unten und fällt weg. Übrig bleibt "
          f"die blosse Zahl."),
    ])


BF30_2 = Bauform("BF2", "Term durch die eigene Variable",
    bereiche={lv: dict(BEREICH30[lv], teiler=[6, 7, 12, 17, 24]) for lv in "ABC"},
    bauen=bf30_2, filter=STANDARD)


def bf30_3(p):
    """Monom durch Monom, die erste Variable bleibt oben:  −52qd : (4d)"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t * f2), ((v1, 1), (v2, 1))),
                           M(Integer(un * t), ((v2, 1),)))],
                 sorten=[v1])


BF30_3 = Bauform("BF3", "Monom durch Monom, eine Variable bleibt",
    bereiche=BEREICH30, bauen=bf30_3, filter=ZWEI)


def bf30_4(p):
    """Monom durch Monom, die zweite Variable bleibt:  8xy : (2y)"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t * f2), ((v1, 1), (v2, 1))),
                           M(Integer(un * t), ((v1, 1),)))],
                 sorten=[v2])


BF30_4 = Bauform("BF4", "Monom durch Monom, die andere Variable bleibt",
    bereiche=BEREICH30, bauen=bf30_4, filter=ZWEI)


def bf30_5(p):
    """Zahl geht auf, Variable bleibt:  10a : 5"""
    v1, t = p["var"], p["teiler"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t * p["faktor"]), ((v1, 1),)),
                           M(Integer(un * t)))], extra=[
        F("zahl_addiert", Integer(o * un) * (t + p["faktor"]) * v1,
          "Die Zahlen werden geteilt, nicht verrechnet."),
    ])


BF30_5 = Bauform("BF5", "Zahl geht auf, Variable bleibt",
    bereiche=BEREICH30, bauen=bf30_5, filter=STANDARD)


def bf30_6(p):
    """Sonderfall: der Koeffizient wird eins:  4x : 4"""
    v1, t = p["var"], p["teiler"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t), ((v1, 1),)), M(Integer(un * t)))],
                 extra=[
        F("zahl_geblieben", Integer(o * un) * t,
          f"{t} : {t} ergibt 1, und 1{zeige(v1)} schreibt man als "
          f"{zeige(v1)}."),
        F("eins_geschrieben", Integer(o * un),
          f"Die Eins wird nicht hingeschrieben, aber {zeige(v1)} bleibt."),
    ])


BF30_6 = Bauform("BF6", "Sonderfall: der Koeffizient wird eins",
    bereiche={lv: dict(BEREICH30[lv], teiler=[4, 7, 11, 5]) for lv in "ABC"},
    bauen=bf30_6, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf30_7(p):
    """Sonderfall: nur die Variable bleibt übrig:  3bc : (3c)"""
    v1, v2, t = p["var"], p["var2"], p["teiler"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(o * t), ((v1, 1), (v2, 1))),
                           M(Integer(un * t), ((v2, 1),)))], extra=[
        F("zahl_geblieben", Integer(o * un) * t * v1,
          f"{t} : {t} ergibt 1 — die Zahl verschwindet, {zeige(v1)} bleibt."),
    ])


BF30_7 = Bauform("BF7", "Sonderfall: nur die Variable bleibt übrig",
    bereiche=BEREICH30, bauen=bf30_7, filter=ZWEI)


def bf30_8(p):
    """Sonderfall: der Zähler ist null:  0 : (5x)"""
    v1, t = p["var"], p["teiler"]
    o, un = _vz(p)
    return bau30("+", [Div(M(Integer(0)), M(Integer(un * t), ((v1, 1),)))],
                 loesung=0, extra=[
        F("nenner_geblieben", Integer(un * t) * v1,
          "Null geteilt durch irgendetwas bleibt null."),
        F("eins_geschrieben", Integer(1),
          "Null geteilt durch etwas ist null, nicht eins."),
    ])


BF30_8 = Bauform("BF8", "Sonderfall: der Zähler ist null",
    bereiche=BEREICH30, bauen=bf30_8,
    filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf30_9(p):
    """Sonderfall: das Ergebnis ist eins:  6x : (6x)"""
    v1, v2, t = p["var"], p["var2"], p["teiler"]
    o, un = _vz(p)
    basen = ((v1, 1),) if p["eine"] else ((v1, 1), (v2, 1))
    return bau30("+", [Div(M(Integer(o * t), basen), M(Integer(un * t), basen))],
                 loesung=o * un, extra=[
        F("null_geschrieben", Integer(0),
          "Etwas geteilt durch sich selbst ergibt eins, nicht null."),
        F("term_geblieben", Integer(o * un) * M(Integer(t), basen).monom,
          "Oben und unten steht dasselbe — es fällt vollständig weg."),
    ])


BF30_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist eins",
    bereiche={lv: dict(BEREICH30[lv], eine=[True, False]) for lv in "ABC"},
    bauen=bf30_9, filter=[fehler_eindeutig, hat_fehler,
                          verschieden("var", "var2")])


def bf30_10(p):
    """Alle Variablen fallen weg, eine Zahl bleibt:  24ab : (6ab)"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    basen = ((v1, 1), (v2, 1))
    return bau30("+", [Div(M(Integer(o * t * f2), basen),
                           M(Integer(un * t), basen))], extra=[
        F("variablen_geblieben", Integer(o * un) * f2 * v1 * v2,
          f"{zeige(v1 * v2)} steht oben und unten und fällt ganz weg. Übrig "
          f"bleibt nur die Zahl."),
    ])


BF30_10 = Bauform("BF10", "Alle Variablen fallen weg, eine Zahl bleibt",
    bereiche=BEREICH30, bauen=bf30_10, filter=ZWEI)


def bf30_11(p):
    """Minuszeichen an verschiedenen Stellen:  −24z : 3"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    #: Diese Bauform trägt IMMER ein Minus — das macht sie aus. Das Level
    #: entscheidet, ob es eines oder zwei sind.
    if (o, un) == (1, 1):
        o = -1
    return bau30("+", [Div(M(Integer(o * t * f2), ((v1, 1),)),
                           M(Integer(un * t)))])


BF30_11 = Bauform("BF11", "Minuszeichen an verschiedenen Stellen",
    bereiche=BEREICH30, bauen=bf30_11, filter=STANDARD)


S30 = Schablone(
    nr="S30", titel="Terme dividieren, einfache Fälle",
    lektionen="9.1 – 9.3", erhebung="Vorstufe zu 2c",
    anleitung=ANLEITUNG,
    levelachse="Vorzeichen",
    bauformen=[BF30_1, BF30_2, BF30_3, BF30_4, BF30_5, BF30_6,
               BF30_7, BF30_8, BF30_9, BF30_10, BF30_11],
    kernidee=("Beim Dividieren werden die Zahlen geteilt, und jede Variable, "
              "die oben und unten steht, fällt weg."),
)


# ══════════════════════════════════════════════════════════════════════════
# S31 · Monome mit Potenzen dividieren        (Lektionen 9.4 – 9.5)
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 2: Anzahl Variablen eine → eine bis zwei → zwei bis drei, dazu das
# Vorzeichen positiv → ein Minus → zwei Minus.

ANZ31 = {"A": [1], "B": [2], "C": [3]}

BEREICH31 = {lv: {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                  "teiler": [2, 3, 4, 5, 6, 7], "faktor": [2, 3, 4, 5],
                  "vz": VZ[lv], "anzahl": ANZ31[lv]}
             for lv in ("A", "B", "C")}


def bau31(muster, glieder, extra=(), **kw):
    kw.setdefault("tipps", TIPPS31)
    return bau(muster, glieder, extra=extra, **kw)


def _basen31(p, exp_oben, exp_unten):
    """Ein bis drei Variablen — das ist die Levelachse von S31."""
    vs = [p["var"], p["var2"], p["var3"]][:p["anzahl"]]
    oben = tuple((s, exp_oben[i % len(exp_oben)]) for i, s in enumerate(vs))
    unten = tuple((s, exp_unten[i % len(exp_unten)]) for i, s in enumerate(vs))
    return oben, unten


def bf31_1(p):
    """Eine Potenz bleibt übrig:  6x² : (2x)"""
    t, f2 = p["teiler"], p["faktor"]
    o, un = _vz(p)
    oben, unten = _basen31(p, [2, 3, 2], [1, 2, 1])
    return bau31("+", [Div(M(Integer(o * t * f2), oben), M(Integer(un * t), unten))])


BF31_1 = Bauform("BF1", "Eine Variable, eine Potenz bleibt übrig",
    bereiche=BEREICH31, bauen=bf31_1, filter=DREI)


def bf31_2(p):
    """Die Variable fällt ganz weg:  −27y⁴ : (−3y⁴)"""
    t, f2 = p["teiler"], p["faktor"]
    o, un = _vz(p)
    oben, unten = _basen31(p, [2, 3, 4], [2, 3, 4])
    return bau31("+", [Div(M(Integer(o * t * f2), oben),
                           M(Integer(un * t), unten))], extra=[
        F("variablen_geblieben", Integer(o * un) * f2 * M(1, oben).monom,
          "Oben und unten stehen dieselben Variablen mit denselben "
          "Hochzahlen — sie fallen ganz weg."),
    ])


BF31_2 = Bauform("BF2", "Die Variable fällt ganz weg",
    bereiche=BEREICH31, bauen=bf31_2, filter=DREI)


def bf31_3(p):
    """Zwei Variablen, eine bleibt:  52x⁴y : (−13x²)"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    e = 2 if p["anzahl"] == 1 else p["anzahl"] + 1
    return bau31("+", [Div(M(Integer(o * t * f2), ((v1, e), (v2, 1))),
                           M(Integer(un * t), ((v1, e - 1),)))],
                 sorten=[v1 * v2])


BF31_3 = Bauform("BF3", "Zwei Variablen, eine bleibt",
    bereiche=BEREICH31, bauen=bf31_3, filter=ZWEI)


def bf31_4(p):
    """Beide Variablen bleiben:  12u²v² : (4uv)"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    e = p["anzahl"] + 1
    return bau31("+", [Div(M(Integer(o * t * f2), ((v1, e), (v2, e))),
                           M(Integer(un * t), ((v1, 1), (v2, 1))))],
                 sorten=[v1 ** (e - 1) * v2 ** (e - 1)])


BF31_4 = Bauform("BF4", "Beide Variablen bleiben",
    bereiche=BEREICH31, bauen=bf31_4, filter=ZWEI)


def bf31_5(p):
    """Drei Variablen:  −u³v⁴w⁵ : (u²v³w⁴)"""
    v1, v2, v3 = p["var"], p["var2"], p["var3"]
    o, un = _vz(p)
    t = p["teiler"]
    anz = max(p["anzahl"], 2)
    oben = ((v1, 3), (v2, 4), (v3, 5))[:anz]
    unten = ((v1, 2), (v2, 3), (v3, 4))[:anz]
    return bau31("+", [Div(M(Integer(o * t), oben), M(Integer(un * t), unten))])


BF31_5 = Bauform("BF5", "Drei Variablen",
    bereiche=BEREICH31, bauen=bf31_5, filter=DREI)


def bf31_6(p):
    """Summe durch Monom — jedes Glied einzeln:  (6x + 9) : 3"""
    v1, v2, v3, t = p["var"], p["var2"], p["var3"], p["teiler"]
    un = _vz(p)[1]
    #: Alle Glieder werden positiv hingeschrieben, das Vorzeichen steht im
    #: Muster der Summe. Der Divisor traegt sein eigenes Vorzeichen.
    if p["anzahl"] == 1:
        #: Level A: durch eine blosse Zahl,  (6x + 9) : 3
        nenner = M(Integer(un * t))
        glieder = (M(Integer(2 * t), ((v1, 1),)), M(Integer(3 * t)))
        muster = "++"
    elif p["anzahl"] == 2:
        #: Level B: durch ein Monom,  (−16mx + 40my) : (−8m)
        nenner = M(Integer(un * t), ((v1, 1),))
        glieder = (M(Integer(2 * t), ((v1, 1), (v2, 1))),
                   M(Integer(5 * t), ((v1, 1), (v3, 1))))
        muster = "+-"
    else:
        #: Level C: drei Glieder, das letzte ohne zweite Variable
        nenner = M(Integer(un * t), ((v1, 1),))
        glieder = (M(Integer(2 * t), ((v1, 1), (v2, 1))),
                   M(Integer(5 * t), ((v1, 1), (v3, 1))),
                   M(Integer(3 * t), ((v1, 1),)))
        muster = "+--"
    return bau31("+", [Div(Su(muster, glieder), nenner)])


BF31_6 = Bauform("BF6", "Summe durch Monom — jedes Glied einzeln",
    bereiche=BEREICH31, bauen=bf31_6, filter=DREI)


def bf31_7(p):
    """Summe mit Potenzen — ein Glied wird zur Eins:
       (18u⁴ − 12u³ + 2u²) : (−2u²)"""
    v1, t = p["var"], p["teiler"]
    un = _vz(p)[1]
    #: Jedes Glied positiv, das Vorzeichen steht im Muster. Der Divisor
    #: traegt sein eigenes.
    if p["stufe"] == 1:
        #: Level A: beide Glieder gleichartig, das Ergebnis ist eine Zahl
        nenner = M(Integer(t), ((v1, 2),))
        glieder = (M(Integer(2 * t), ((v1, 2),)), M(Integer(t), ((v1, 2),)))
        muster = "++"
    elif p["stufe"] == 2:
        #: Level B: zwei Glieder, der Divisor ist negativ
        nenner = M(Integer(-t), ((v1, 2),))
        glieder = (M(Integer(9 * t), ((v1, 4),)), M(Integer(6 * t), ((v1, 3),)))
        muster = "+-"
    else:
        #: Level C: das dritte Glied geht ganz auf — dort bleibt eine −1
        #: stehen, nicht nichts. Das ist der Kern dieser Bauform.
        nenner = M(Integer(-t), ((v1, 2),))
        glieder = (M(Integer(9 * t), ((v1, 4),)), M(Integer(6 * t), ((v1, 3),)),
                   M(Integer(t), ((v1, 2),)))
        muster = "+-+"
    return bau31("+", [Div(Su(muster, glieder), nenner)])


BF31_7 = Bauform("BF7", "Summe mit Potenzen — ein Glied wird zur Eins",
    bereiche={"A": dict(BEREICH31["A"], stufe=[1]),
              "B": dict(BEREICH31["B"], stufe=[2]),
              "C": dict(BEREICH31["C"], stufe=[3])},
    bauen=bf31_7, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf31_8(p):
    """Sonderfall: das Ergebnis ist eins:  5a² : (5a²)"""
    t = p["teiler"]
    o, un = _vz(p)
    oben, _ = _basen31(p, [2, 3, 1], [2, 3, 1])
    return bau31("+", [Div(M(Integer(o * t), oben), M(Integer(un * t), oben))],
                 loesung=o * un, extra=[
        F("null_geschrieben", Integer(0),
          "Etwas geteilt durch sich selbst ergibt eins, nicht null."),
        F("term_geblieben", Integer(o * un) * M(1, oben).monom,
          "Zähler und Nenner sind gleich — alles fällt weg."),
    ])


BF31_8 = Bauform("BF8", "Sonderfall: das Ergebnis ist eins",
    bereiche=BEREICH31, bauen=bf31_8,
    filter=[fehler_eindeutig, hat_fehler, verschieden("var", "var2", "var3")])


def bf31_9(p):
    """Sonderfall: nur durch eine Zahl geteilt:  4x² : 4"""
    t = p["teiler"]
    o, un = _vz(p)
    oben, _ = _basen31(p, [2, 3, 1], [1, 1, 1])
    return bau31("+", [Div(M(Integer(o * t), oben), M(Integer(un * t)))],
                 extra=[
        F("zahl_geblieben", Integer(o * un) * t,
          "Die Zahl geht auf, aber die Variablen bleiben stehen."),
    ])


BF31_9 = Bauform("BF9", "Sonderfall: nur durch eine Zahl geteilt",
    bereiche=BEREICH31, bauen=bf31_9, filter=DREI)


def bf31_10(p):
    """Sonderfall: der Zähler ist null:  0 : (5x²)"""
    t = p["teiler"]
    o, un = _vz(p)
    _, unten = _basen31(p, [2, 2, 2], [2, 3, 1])
    return bau31("+", [Div(M(Integer(0)), M(Integer(un * t), unten))],
                 loesung=0, extra=[
        F("nenner_geblieben", Integer(un * t) * M(1, unten).monom,
          "Null geteilt durch irgendetwas bleibt null."),
        F("eins_geschrieben", Integer(1),
          "Null geteilt durch etwas ist null, nicht eins."),
    ])


BF31_10 = Bauform("BF10", "Sonderfall: der Zähler ist null",
    bereiche=BEREICH31, bauen=bf31_10,
    filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf31_11(p):
    """Vorzeichen an verschiedenen Stellen:  −30u³v² : (−5uv)"""
    t, f2 = p["teiler"], p["faktor"]
    o, un = _vz(p)
    if (o, un) == (1, 1):
        o = -1
    oben, unten = _basen31(p, [3, 2, 2], [1, 1, 1])
    return bau31("+", [Div(M(Integer(o * t * f2), oben),
                           M(Integer(un * t), unten))])


BF31_11 = Bauform("BF11", "Vorzeichen an verschiedenen Stellen",
    bereiche=BEREICH31, bauen=bf31_11, filter=DREI)


def bf31_12(p):
    """Nur Hochzahlen, hohe Differenz:  x⁵ : x²  ·  −24z⁷ : (6z³)"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    o, un = _vz(p)
    e = 4 + p["anzahl"]
    return bau31("+", [Div(M(Integer(o * t * f2), ((v1, e),)),
                           M(Integer(un * t), ((v1, e - 3),)))], extra=[
        F("hochzahlen_geteilt", Integer(o * un) * f2 * v1 ** (e // (e - 3)),
          f"Beim Dividieren werden die Hochzahlen subtrahiert: "
          f"{e} − {e - 3} = 3."),
    ])


BF31_12 = Bauform("BF12", "Nur Hochzahlen, hohe Differenz",
    bereiche=BEREICH31, bauen=bf31_12, filter=STANDARD)


S31 = Schablone(
    nr="S31", titel="Monome mit Potenzen dividieren",
    lektionen="9.4 – 9.5", erhebung="2c",
    anleitung=ANLEITUNG,
    levelachse="Anzahl Variablen und Vorzeichen",
    bauformen=[BF31_1, BF31_2, BF31_3, BF31_4, BF31_5, BF31_6,
               BF31_7, BF31_8, BF31_9, BF31_10, BF31_11, BF31_12],
    kernidee=("Beim Dividieren werden die Zahlen geteilt und die Hochzahlen "
              "subtrahiert. Steht im Zähler eine Summe, wird jedes Glied "
              "einzeln geteilt — auch das, welches ganz aufgeht."),
)


# ══════════════════════════════════════════════════════════════════════════
# S32 · Division in längeren Termen einordnen        (Lektion 9.6)
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 2: Anzahl Glieder zwei → zwei → drei, Vorzeichen alles positiv → ein
# Minus → mehrere Minus. A und B haben gleich viele Glieder; den Unterschied
# trägt das Vorzeichen. So steht es in der Schablone.

MUSTER32 = {"A": ["++"], "B": ["+-"], "C": ["++-", "+-+", "+--"]}

BEREICH32 = {lv: {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                  "muster": MUSTER32[lv], "teiler": [2, 3, 4, 5, 6],
                  "faktor": [2, 3, 4, 5],
                  "vz": [(1, 1)] if lv == "A" else [(1, -1), (-1, 1)]}
             for lv in ("A", "B", "C")}


def bau32(muster, glieder, extra=(), **kw):
    kw.setdefault("tipps", TIPPS32)
    return bau(muster, glieder, extra=extra, **kw)


def bf32_1(p):
    """Division in der Mitte, gleichartiges Glied davor:
       12ab + 21ab : (7a)     — das ist die Erhebungsform."""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    muster = p["muster"]
    un = _vz(p)[1]
    #: Der Zaehler bleibt positiv. Steht das Divisionsglied an einer
    #: Minus-Stelle des Musters, staende sonst «− −25my» da — zwei Zeichen
    #: nebeneinander. Das Vorzeichen der Aufgabe traegt der Divisor.
    glieder = [M(Integer(f2 * 2), ((v1, 1), (v2, 1))),
               Div(M(Integer(t * (f2 + 1)), ((v1, 1), (v2, 1))),
                   M(Integer(un * t), ((v1, 1),)))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v2, 1),)))
    return bau32(muster, glieder, sorten=[v1 * v2, v2])


BF32_1 = Bauform("BF1", "Division in der Mitte, gleichartiges Glied davor",
    bereiche=BEREICH32, bauen=bf32_1, filter=ZWEI)


def bf32_2(p):
    """Division vorne:  6x : 3 + 4x"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t * f2), ((v1, 1),)), M(Integer(un * t))),
               M(Integer(f2 + 1), ((v1, 1),))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v1, 1),)))
    return bau32(muster, glieder)


BF32_2 = Bauform("BF2", "Division vorne",
    bereiche=BEREICH32, bauen=bf32_2, filter=STANDARD + [loesung_nicht_null])


def bf32_3(p):
    """Division hinten, eine Variable:  6a + 12a : 4"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    un = _vz(p)[1]
    #: Zaehler positiv — siehe BF1.
    glieder = [M(Integer(f2 + 1), ((v1, 1),)),
               Div(M(Integer(t * f2), ((v1, 1),)), M(Integer(un * t)))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v1, 1),)))
    return bau32(muster, glieder)


BF32_3 = Bauform("BF3", "Division hinten, eine Variable",
    bereiche=BEREICH32, bauen=bf32_3, filter=STANDARD + [loesung_nicht_null])


def bf32_4(p):
    """Division vorne, Monom durch Monom:  12ab : (4a) + 5b"""
    v1, v2, t, f2 = p["var"], p["var2"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t * f2), ((v1, 1), (v2, 1))),
                   M(Integer(un * t), ((v1, 1),))),
               M(Integer(f2 + 1), ((v2, 1),))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v2, 1),)))
    return bau32(muster, glieder)


BF32_4 = Bauform("BF4", "Division vorne, Monom durch Monom",
    bereiche=BEREICH32, bauen=bf32_4, filter=ZWEI + [loesung_nicht_null])


def bf32_5(p):
    """Division und blosse Zahl:  8x : 2 + 3"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t * f2), ((v1, 1),)), M(Integer(un * t))),
               M(Integer(f2 + 2))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2)))
    return bau32(muster, glieder, sorten=[v1, Integer(1)])


BF32_5 = Bauform("BF5", "Division und blosse Zahl",
    bereiche=BEREICH32, bauen=bf32_5, filter=STANDARD)


def bf32_6(p):
    """Nach der Division bleiben zwei Sorten:  6ab : (2b) + 4ac"""
    v1, v2, v3 = p["var"], p["var2"], p["var3"]
    t, f2 = p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t * f2), ((v1, 1), (v2, 1))),
                   M(Integer(un * t), ((v2, 1),))),
               M(Integer(f2 + 1), ((v1, 1), (v3, 1)))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v1, 1),)))
    return bau32(muster, glieder, sorten=[v1, v1 * v3])


BF32_6 = Bauform("BF6", "Nach der Division bleiben zwei Sorten",
    bereiche=BEREICH32, bauen=bf32_6, filter=DREI)


def bf32_7(p):
    """Produkt und Division im selben Term:  4a · 2 + 16a : 8"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Pr((M(Integer(f2), ((v1, 1),)), M(Integer(2)))),
               Div(M(Integer(o * t * f2), ((v1, 1),)), M(Integer(un * t)))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v1, 1),)))
    return bau32(muster, glieder, extra=[
        F("nur_division", Integer(o * un) * f2 * v1,
          "Auch das Produkt vorne zählt mit."),
    ])


BF32_7 = Bauform("BF7", "Produkt und Division im selben Term",
    bereiche=BEREICH32, bauen=bf32_7, filter=STANDARD + [loesung_nicht_null])


def bf32_8(p):
    """Sonderfall: das Ergebnis ist null:  12a : 4 − 3a"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    #: Null geht nur mit einem Minus — das gehoert zur Bauform. Das Level
    #: traegt darum das ZWEITE Vorzeichen und ab C die Gliederzahl.
    if len(p["muster"]) == 3:
        glieder = [Div(M(Integer(t * f2), ((v1, 1),)), M(Integer(t))),
                   M(Integer(f2 + 1), ((v1, 1),)),
                   M(Integer(2 * f2 + 1), ((v1, 1),))]
        muster = "++-"
    elif p["vz"][1] < 0:
        #: Level B: der Divisor ist negativ, also steht oben auch ein Minus
        glieder = [Div(M(Integer(-t * f2), ((v1, 1),)), M(Integer(-t))),
                   M(Integer(f2), ((v1, 1),))]
        muster = "+-"
    else:
        glieder = [Div(M(Integer(t * f2), ((v1, 1),)), M(Integer(t))),
                   M(Integer(f2), ((v1, 1),))]
        muster = "+-"
    return bau32(muster, glieder, loesung=0, extra=[
        F("nicht_null", Integer(2 * f2) * v1,
          "Die beiden Teile heben sich genau auf — das Ergebnis ist null."),
    ])


BF32_8 = Bauform("BF8", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICH32, bauen=bf32_8,
    filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf32_9(p):
    """Sonderfall: der Quotient wird eine reine Variable:  6x : 6 + 2x"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t), ((v1, 1),)), M(Integer(un * t))),
               M(Integer(f2), ((v1, 1),))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(1), ((v1, 1),)))
    return bau32(muster, glieder, extra=[
        F("eins_verloren", Integer(f2) * v1,
          f"{t} : {t} ergibt 1 — das Glied wird zu {zeige(v1)} und "
          f"verschwindet nicht."),
    ])


BF32_9 = Bauform("BF9", "Sonderfall: der Quotient wird eine reine Variable",
    bereiche=BEREICH32, bauen=bf32_9, filter=STANDARD + [loesung_nicht_null])


def bf32_10(p):
    """Sonderfall: nichts lässt sich zusammenfassen:  10a : 5 + 3b"""
    v1, v2, v3 = p["var"], p["var2"], p["var3"]
    t, f2 = p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(o * t * f2), ((v1, 1),)), M(Integer(un * t))),
               M(Integer(f2 + 1), ((v2, 1),))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(1), ((v2, 1),)))
    return bau32(muster, glieder, sorten=[v1, v2])


BF32_10 = Bauform("BF10", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche=BEREICH32, bauen=bf32_10, filter=ZWEI)


def bf32_11(p):
    """Minuszeichen am Anfang:  −12a : 3 + 5a"""
    v1, t, f2 = p["var"], p["teiler"], p["faktor"]
    muster = p["muster"]
    o, un = _vz(p)
    glieder = [Div(M(Integer(-abs(o) * t * f2), ((v1, 1),)),
                   M(Integer(un * t))),
               M(Integer(f2 + 2), ((v1, 1),))]
    for i in range(2, len(muster)):
        glieder.append(M(Integer(2), ((v1, 1),)))
    return bau32(muster, glieder)


BF32_11 = Bauform("BF11", "Minuszeichen am Anfang",
    bereiche=BEREICH32, bauen=bf32_11, filter=STANDARD + [loesung_nicht_null])


S32 = Schablone(
    nr="S32", titel="Division in längeren Termen einordnen",
    lektionen="9.6", erhebung="2c",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF32_1, BF32_2, BF32_3, BF32_4, BF32_5, BF32_6,
               BF32_7, BF32_8, BF32_9, BF32_10, BF32_11],
    kernidee=("Eine Division ist eine Punktoperation und bindet stärker als "
              "Plus und Minus. Ohne Klammer wird nur das Glied direkt davor "
              "geteilt."),
)
