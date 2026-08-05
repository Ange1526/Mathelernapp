# -*- coding: utf-8 -*-
"""
S22 · Potenzen verstehen                     (Lektionen 7.1 – 7.2)
S23 · Potenz vor Punkt vor Strich, negative Basis   (Lektionen 7.3 – 7.4)

    «Rechne aus.»
    2³      x · x · x      (2x)²      2 · 4² − (−3) + 2³      −7²

Zusammen mit S24 und S25 ersetzen sie `s7_potenzen.py`. S23 bringt
Erhebungsaufgabe 3c (`2 · 4² − (−3) + 2³`, BF2 auf Level C) und die Form von
3d (`(5 − 7)² · (3² − 2) : 2²`, BF6 auf Level C).

LEVELACHSE (Teil 2 der Schablonen, wörtlich):

    S22   Grösse des Exponenten   zwei bis drei → drei bis vier → fünf und mehr
    S23   Anzahl Glieder          zwei         → zwei bis drei → drei bis vier
    S23   Vorzeichen              ein Minus    → zwei Minus    → doppeltes Minus
                                                                 oder negative Basis

S22 ist die eine dokumentierte Ausnahme von der Regel, dass die Levelachse
strukturell sein muss. Teil 2 sagt dazu wörtlich: der Exponent ist «der
einzige Regler, der hier ohne Vorgriff funktioniert» — Punkt vor Strich ist
7.3, die negative Basis 7.4, die Potenzgesetze 7.5. Ein grösserer Exponent
ist aber ohnehin kein blosses Grösserwerden der Zahlen: 2⁵ hat fünf Faktoren
und 2² deren zwei. Der Aufbau ändert sich also mit.

Eine Bauform bleibt auch damit ohne Regler: BF4 «Sonderfall: Exponent eins»
sperrt den Exponenten selbst. Dort trägt die Zahlengrösse das Level, so wie
es in Teil 1 der Schablone steht (3¹ → 7¹ → 12¹). Das ist die zweite und
letzte Ausnahme in dieser Datei und im Kopf von BF4 nochmals vermerkt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sympy import Expr, Integer, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS, zeige
from .qualitaet import (exponent_hoechstens, fehler_eindeutig,
                        kopfrechenbar, loesung_nicht_null)
from .schablone import Bauform, Schablone

a, b, c, d, m, n, p_, q, u, v, w, x, y, z = symbole("a b c d m n p q u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "p", "q", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

VARIABLEN = [x, y, z, a, u]

#: Hochgestellte Ziffern — `anzeige.HOCH` beginnt bei zwei, hier braucht es
#: auch die Eins und die Zehn.
HOCH_ALLE = {1: "¹", 10: "¹⁰", 11: "¹¹", 12: "¹²", **HOCH}


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def hoch(e: int) -> str:
    return HOCH_ALLE.get(e, f"^{e}")


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════
#
# Eine Aufgabe besteht aus GLIEDERN, die mit + und − verbunden sind. Das
# Vorzeichen steht im Muster, nicht im Glied — wie in `s6_punktrechnung`.
#
# Ein Glied ist eine KETTE aus Teilen, verbunden mit · oder :
#
#     Kette([Pz(4, 2)])                      ->  4²
#     Kette([2, Pz(4, 2)])                   ->  2 · 4²
#     Kette([Pz(2, 3), Pz(2, 2)], [":"])     ->  2³ : 2²
#
# Ein Teil ist eine Potenz `Pz`, eine Klammer `Kl` oder eine blosse Zahl.


@dataclass(frozen=True)
class Pz:
    """Eine Potenz. `basis_text` ist für Klammerbasen wie (5 − 7)² da."""
    basis: Expr
    exp: int
    basis_text: str = ""
    klammer: bool = False

    @property
    def wert(self) -> Expr:
        return sympify(self.basis) ** self.exp

    @property
    def text(self) -> str:
        kern = self.basis_text or zeige(self.basis)
        return f"({kern}){hoch(self.exp)}" if self.klammer else \
               f"{kern}{hoch(self.exp)}"


@dataclass(frozen=True)
class Kl:
    """Eine Klammer als Faktor:  (3² − 2)"""
    inhalt: str
    wert: Expr

    @property
    def text(self) -> str:
        return f"({self.inhalt})"


def teil_wert(t, ersatz=None) -> Expr:
    if isinstance(t, Pz):
        return ersatz(t) if ersatz else t.wert
    if isinstance(t, Kl):
        return t.wert
    return sympify(t)


def teil_text(t) -> str:
    if isinstance(t, (Pz, Kl)):
        return t.text
    return zeige(t)


@dataclass(frozen=True)
class Kette:
    teile: tuple
    ops: tuple = ()          # ("·",) oder (":",) zwischen den Teilen

    def wert(self, ersatz=None) -> Expr:
        gesamt = teil_wert(self.teile[0], ersatz)
        for i, op in enumerate(self.ops):
            rechts = teil_wert(self.teile[i + 1], ersatz)
            gesamt = gesamt / rechts if op == ":" else gesamt * rechts
        return gesamt

    @property
    def text(self) -> str:
        raus = teil_text(self.teile[0])
        for i, op in enumerate(self.ops):
            raus += f" {op} {teil_text(self.teile[i + 1])}"
        return raus

    @property
    def potenzen(self) -> list:
        return [t for t in self.teile if isinstance(t, Pz)]


def K(*teile, ops=None) -> Kette:
    """Kurzschreibweise. Ohne `ops` sind alle Verbindungen Malpunkte."""
    return Kette(tuple(teile), tuple(ops or ["·"] * (len(teile) - 1)))


# ── Zusammenbau ───────────────────────────────────────────────────────────

def frage_text(muster, glieder) -> str:
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def summe(muster, glieder, ersatz=None) -> Expr:
    gesamt = Integer(0)
    for zeichen, g in zip(muster, glieder):
        w = g.wert(ersatz)
        gesamt += w if zeichen == "+" else -w
    return gesamt


def alle_potenzen(glieder) -> list:
    return [t for g in glieder for t in g.potenzen]


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 5 von S22 und S23 nennt zusammen zehn Fehler. Sie stehen hier einmal
# und gelten für jede Bauform, in der sie überhaupt auftreten können.


def _grundzahl(pz: Pz):
    """Zahl und Rest der Basis:  2x -> (2, x)   ·   4 -> (4, 1)"""
    return sympify(pz.basis).as_coeff_Mul()


def kandidaten(muster, glieder, loesung):
    raus = []
    pot = alle_potenzen(glieder)
    if not pot:
        return raus

    # 1 · Basis mit dem Exponenten multipliziert:  2³ -> 6
    mal = [p for p in pot if p.exp > 1]
    if mal:
        raus.append(F("basis_mal_exponent",
            summe(muster, glieder, lambda p: p.basis * p.exp),
            f"{mal[0].text} heisst "
            f"{' · '.join([zeige(mal[0].basis)] * min(mal[0].exp, 4))}"
            f"{' · …' if mal[0].exp > 4 else ''} = {zeige(mal[0].wert)}, "
            f"nicht {zeige(mal[0].basis)} · {mal[0].exp}."))

    # 2 · Klammer nur teilweise potenziert:  (2x)² -> 2x²
    teil = [p for p in pot if p.klammer and _grundzahl(p)[0] not in (1, -1)
            and _grundzahl(p)[1] != 1]
    if teil:
        def nur_variable(p):
            k, rest = _grundzahl(p)
            return k * rest ** p.exp if p in teil else p.wert
        raus.append(F("klammer_teilweise",
            summe(muster, glieder, nur_variable),
            f"Die Klammer gilt für alles darin: {teil[0].text} ist "
            f"{zeige(teil[0].wert)}."))

    # 3 · Exponent eins falsch gelesen:  3¹ -> 1
    eins = [p for p in pot if p.exp == 1]
    if eins:
        raus.append(F("exponent_eins",
            summe(muster, glieder, lambda p: Integer(1) if p.exp == 1 else p.wert),
            f"Der Exponent 1 heisst: die Basis kommt einmal vor. "
            f"{eins[0].text} ist {zeige(eins[0].basis)}."))

    # 4 · Basis und Exponent vertauscht:  2⁴ statt 4²
    tausch = [p for p in pot if p.basis.is_Integer and p.basis > 1
              and p.exp != p.basis and 1 < p.exp <= 10]
    if tausch:
        raus.append(F("basis_exponent_vertauscht",
            summe(muster, glieder,
                  lambda p: Integer(p.exp) ** int(p.basis)
                  if p in tausch else p.wert),
            f"Basis und Exponent sind nicht vertauschbar: {tausch[0].text} "
            f"ist {zeige(tausch[0].wert)}, "
            f"{zeige(tausch[0].exp)}{hoch(int(tausch[0].basis))} wäre "
            f"{zeige(Integer(tausch[0].exp) ** int(tausch[0].basis))}."))

    # 5 · Negative Basis mit geradem Exponenten negativ gelassen: (−2)² -> −4
    negativ = [p for p in pot if p.basis.is_number and p.basis < 0
               and p.exp % 2 == 0]
    if negativ:
        raus.append(F("negative_basis_gerade",
            summe(muster, glieder,
                  lambda p: -abs(p.wert) if p in negativ else p.wert),
            f"Eine gerade Hochzahl macht das Ergebnis positiv: "
            f"{negativ[0].text} ist {zeige(negativ[0].wert)}."))

    return raus


def siebe(fehler, loesung):
    """Doppelte und die Lösung selbst aus dem Katalog entfernen."""
    raus, gesehen = [], set()
    for f in fehler:
        e = f.ergebnis.expr
        if e is None or e == sympify(loesung) or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Der gemeinsame Bauplan
# ══════════════════════════════════════════════════════════════════════════

def bau(muster, glieder, extra=(), schritte=None, tipps=None,
        loesung=None, loesung_text=None):
    l = summe(muster, glieder) if loesung is None else sympify(loesung)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l), l)
    frage = frage_text(muster, glieder)
    return {"frage": frage,
            "loesung_text": loesung_text or zeige(l),
            "glieder": glieder,
            "muster": muster,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=fehler),
            "schritte": schritte or schritte_standard(muster, glieder, l),
            "tipps": tipps or tipps_fuer(glieder)}


def schritte_standard(muster, glieder, l):
    pot = alle_potenzen(glieder)
    schritte = [("Die Aufgabe hinschreiben", frage_text(muster, glieder))]
    if pot:
        p0 = pot[0]
        anzahl = min(p0.exp, 5)
        ausgeschrieben = " · ".join([zeige(p0.basis)] * anzahl)
        if p0.exp > 5:
            ausgeschrieben += " · …"
        schritte.append((f"{p0.text} als Produkt ausschreiben", ausgeschrieben))
        schritte.append(("Die Potenz ausrechnen",
                         f"{p0.text} = {zeige(p0.wert)}"))
    schritte.append(("Ergebnis", zeige(l)))
    return schritte


TIPPS = [
    "Eine Potenz ist eine Abkürzung für ein Produkt: 2³ heisst 2 · 2 · 2.",
    "Schreib die Potenz als Produkt aus, dann siehst du, was zu rechnen ist.",
    "",
]

TIPPS23 = [
    "Die Reihenfolge lautet: Klammer vor Potenz vor Punkt vor Strich.",
    "Rechne zuerst die Klammern aus, danach die Potenzen.",
    "",
]


def tipps_fuer(glieder, basis=None):
    basis = basis or TIPPS
    pot = alle_potenzen(glieder)
    if pot:
        p0 = pot[0]
        konkret = (f"{p0.text} heisst "
                   f"{' · '.join([zeige(p0.basis)] * min(p0.exp, 5))}"
                   f"{' · …' if p0.exp > 5 else ''} und ergibt "
                   f"{zeige(p0.wert)}.")
    else:
        konkret = "Geh Schritt für Schritt vor."
    return [basis[0], basis[1], konkret]


def hat_fehler(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 1


def ganzzahlig(p, g) -> bool:
    """Kein Bruch als Ergebnis. Bei 2³ : 2² geht die Division auf, bei
    2² : 2³ nicht — solche Aufgaben gehören nicht in Kapitel 7."""
    l = g["aufgabe"].loesung.expr
    return bool(getattr(l, "is_Integer", False)) or not l.is_number


STANDARD = [kopfrechenbar, fehler_eindeutig, hat_fehler,
            exponent_hoechstens(10)]

#: Wo null nicht die Aufgabe ist, ist null ein Zufallsunfall — `18 − 2 · 3²`
#: sieht aus wie der Sonderfall BF9, ist aber keiner.
STANDARD_N = STANDARD + [loesung_nicht_null]


# ══════════════════════════════════════════════════════════════════════════
# S22 · Potenzen verstehen        (Lektionen 7.1 – 7.2)
# ══════════════════════════════════════════════════════════════════════════

#: Teil 2: zwei bis drei → drei bis vier → fünf und mehr.
EXP = {"A": [2, 3], "B": [3, 4], "C": [5, 6, 7]}

#: Basen so gewählt, dass das Ergebnis im Kopf bleibt. Was zu gross wird,
#: verwirft `kopfrechenbar`.
BASIS = {"A": [2, 3, 4, 5, 6, 7], "B": [2, 3, 4, 5], "C": [2, 3]}


def bf22_1(p):
    """Potenz mit Zahlenbasis ausrechnen:  2³"""
    return bau("+", [K(Pz(Integer(p["basis"]), p["exp"]))])


BEREICH22 = {lv: {"basis": BASIS[lv], "exp": EXP[lv], "var": VARIABLEN}
             for lv in ("A", "B", "C")}

BF22_1 = Bauform("BF1", "Potenz mit Zahlenbasis ausrechnen",
    bereiche=BEREICH22, bauen=bf22_1, filter=STANDARD)


def bf22_2(p):
    """Produkt gleicher Variablen als Potenz schreiben:  x · x · x"""
    v, e = p["var"], p["exp"]
    kette = K(*([v] * e))
    return bau("+", [kette], extra=[
        F("faktoren_gezaehlt", Integer(e) * v,
          f"{e} gleiche Faktoren ergeben die Hochzahl {e}, nicht den Vorfaktor "
          f"{e}: {zeige(v ** e)}."),
        F("einer_zu_wenig", v ** (e - 1),
          f"Zähl nochmals: {zeige(v)} kommt {e}-mal vor."),
    ], schritte=[("Gleiche Faktoren zählen", f"{e} Stück {zeige(v)}"),
                 ("Als Potenz schreiben", zeige(v ** e))],
       loesung=v ** e)


BF22_2 = Bauform("BF2", "Produkt gleicher Variablen als Potenz schreiben",
    bereiche=BEREICH22, bauen=bf22_2, filter=[fehler_eindeutig, hat_fehler])


def bf22_3(p):
    """Quadrat- und Kubikzahlen:  5²  ·  10³  ·  2¹⁰

    Hier ist `kopfrechenbar` bewusst nicht gesetzt: 10³ und 2¹⁰ SIND die
    Aufgabe. Sie sollen im Kopf sitzen, auch wenn sie über tausend gehen.
    """
    return bau("+", [K(Pz(Integer(p["basis"]), p["exp"]))])


BF22_3 = Bauform("BF3", "Quadrat- und Kubikzahlen",
    bereiche={"A": {"basis": [4, 5, 6, 7, 8, 9, 11, 12], "exp": [2],
                    "var": VARIABLEN},
              "B": {"basis": [4, 5, 6, 7, 8, 10], "exp": [3], "var": VARIABLEN},
              "C": {"basis": [2], "exp": [5, 6, 7, 8, 9, 10], "var": VARIABLEN}},
    bauen=bf22_3, filter=[fehler_eindeutig, hat_fehler])


def bf22_4(p):
    """Sonderfall: Exponent eins.

    DIE AUSNAHME. Der Exponent ist hier die Bauform selbst und kann das
    Level nicht tragen. Es bleibt die Zahlengrösse — so steht es auch in
    Teil 1: 3¹ → 7¹ → 12¹.
    """
    return bau("+", [K(Pz(Integer(p["basis"]), 1))])


BF22_4 = Bauform("BF4", "Sonderfall: Exponent eins",
    bereiche={"A": {"basis": [2, 3, 4, 5], "exp": [1], "var": VARIABLEN},
              "B": {"basis": [6, 7, 8, 9], "exp": [1], "var": VARIABLEN},
              "C": {"basis": [11, 12, 15, 20], "exp": [1], "var": VARIABLEN}},
    bauen=bf22_4, filter=[fehler_eindeutig, hat_fehler])


def bf22_5(p):
    """Klammer mit Koeffizient wird potenziert:  (2x)²"""
    v, e, k = p["var"], p["exp"], p["koeff"]
    return bau("+", [K(Pz(k * v, e, klammer=True))])


BF22_5 = Bauform("BF5", "Klammer mit Koeffizient wird potenziert",
    bereiche={"A": {"var": VARIABLEN, "exp": [2, 3], "koeff": [2, 3, 4]},
              "B": {"var": VARIABLEN, "exp": [3, 4], "koeff": [2, 3]},
              "C": {"var": VARIABLEN, "exp": [5, 6], "koeff": [2]}},
    bauen=bf22_5, filter=[fehler_eindeutig, hat_fehler,
                          exponent_hoechstens(10)])


def bf22_6(p):
    """Sonderfall: Basis eins.  1⁵ → 1,  auf C zusammen mit einer echten
    Potenz: 1³ · 2³."""
    e = p["exp"]
    if p["zweite"]:
        return bau("+", [K(Pz(Integer(1), e), Pz(Integer(p["basis"]), e))])
    return bau("+", [K(Pz(Integer(1), e))])


BF22_6 = Bauform("BF6", "Sonderfall: Basis eins",
    bereiche={"A": {"exp": [2, 3], "zweite": [False], "basis": [2],
                    "var": VARIABLEN},
              "B": {"exp": [4, 5, 6], "zweite": [False], "basis": [2],
                    "var": VARIABLEN},
              "C": {"exp": [3, 4, 5], "zweite": [True], "basis": [2, 3],
                    "var": VARIABLEN}},
    bauen=bf22_6, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf22_7(p):
    """Zwei Potenzen addieren oder subtrahieren:  2² + 3²"""
    muster, e, bs = p["muster"], p["exp"], p["basis"]
    #: Nur die erste Potenz traegt den Exponenten des Levels. Bekaeme ihn
    #: auch die zweite, stuenden auf C Zahlen wie 3⁵ = 243 nebeneinander —
    #: das ist nicht mehr Kopfrechnen, und der Exponent soll die Aufgabe
    #: laenger machen, nicht unrechenbar.
    glieder = [K(Pz(Integer(bs), e)), K(Pz(Integer(bs + 1), max(e - 2, 2)))]
    if len(muster) == 3:
        glieder.append(K(Pz(Integer(bs + 3), 1)))
    return bau(muster, glieder)


BF22_7 = Bauform("BF7", "Zwei Potenzen addieren oder subtrahieren",
    bereiche={"A": {"muster": ["++"], "exp": [2, 3], "basis": [2, 3, 4],
                    "var": VARIABLEN},
              "B": {"muster": ["+-"], "exp": [3, 4], "basis": [2, 3],
                    "var": VARIABLEN},
              "C": {"muster": ["++-", "+-+"], "exp": [5, 6], "basis": [2],
                    "var": VARIABLEN}},
    bauen=bf22_7, filter=STANDARD)


def bf22_8(p):
    """Sonderfall: Basis null.  0³ → 0,  auf C als Faktor: 0 · 4²"""
    e = p["exp"]
    bs = Integer(p["basis"])
    if p["als_faktor"]:
        return bau("+", [K(Integer(0), Pz(bs, e))], loesung=0, extra=[
            F("null_uebersehen", bs ** e,
              f"Ein Faktor ist null, also ist das ganze Produkt null — auch "
              f"wenn {zeige(bs)}{hoch(e)} = {zeige(bs ** e)} ist."),
        ])
    return bau("+", [K(Pz(Integer(0), e))], loesung=0, extra=[
        F("null_ist_eins", Integer(1),
          f"0{hoch(e)} heisst {' · '.join(['0'] * min(e, 4))}"
          f"{' · …' if e > 4 else ''} und ergibt 0, nicht 1."),
        F("exponent_geblieben", Integer(e),
          "Der Exponent sagt nur, wie oft die Basis vorkommt. Die Basis ist "
          "null, also ist das Ergebnis null."),
    ])


BF22_8 = Bauform("BF8", "Sonderfall: Basis null",
    bereiche={"A": {"exp": [2, 3], "als_faktor": [False], "basis": [2],
                    "var": VARIABLEN},
              "B": {"exp": [4, 5], "als_faktor": [False], "basis": [2],
                    "var": VARIABLEN},
              "C": {"exp": [2, 3], "als_faktor": [True], "basis": [4, 5],
                    "var": VARIABLEN}},
    bauen=bf22_8,
    filter=[fehler_eindeutig, hat_fehler])


def bf22_9(p):
    """Potenz mal ihre eigene Basis:  2³ · 2

    Ausgerechnet, nicht mit dem Potenzgesetz — das ist 7.5 und damit S24.
    """
    bs, e = Integer(p["basis"]), p["exp"]
    zweite = Pz(bs, p["exp2"]) if p["exp2"] > 1 else bs
    return bau("+", [K(Pz(bs, e), zweite)], extra=[
        F("hochzahlen_multipliziert", bs ** (e * max(p["exp2"], 1)),
          f"Die Hochzahlen werden hier addiert, nicht multipliziert: "
          f"{e} + {max(p['exp2'], 1)} = {e + max(p['exp2'], 1)}."),
    ])


BF22_9 = Bauform("BF9", "Potenz mal ihre eigene Basis",
    bereiche={"A": {"basis": [2, 3], "exp": [2, 3], "exp2": [1],
                    "var": VARIABLEN},
              "B": {"basis": [2, 3], "exp": [3, 4], "exp2": [1],
                    "var": VARIABLEN},
              "C": {"basis": [2], "exp": [3, 4], "exp2": [2, 3],
                    "var": VARIABLEN}},
    bauen=bf22_9, filter=STANDARD)


def bf22_10(p):
    """Basis und Exponent vertauscht — verschiedene Ergebnisse.

    Auf A steht 4², auf B 2⁴. Beide ergeben 16, und genau das ist die Falle.
    Auf C stehen zwei Potenzen derselben Basis nebeneinander, wo der Zufall
    nicht mehr mitspielt: 3³ − 3² ist 18.
    """
    bs, e = Integer(p["basis"]), p["exp"]
    if p["zwei"]:
        return bau("+-", [K(Pz(bs, e)), K(Pz(bs, e - 1))])
    return bau("+", [K(Pz(bs, e))])


BF22_10 = Bauform("BF10", "Basis und Exponent vertauscht",
    bereiche={"A": {"basis": [4, 5, 6], "exp": [2], "zwei": [False],
                    "var": VARIABLEN},
              "B": {"basis": [2, 3], "exp": [4], "zwei": [False],
                    "var": VARIABLEN},
              "C": {"basis": [2, 3], "exp": [3, 4, 5], "zwei": [True],
                    "var": VARIABLEN}},
    bauen=bf22_10, filter=STANDARD)


def bf22_11(p):
    """Variablenpotenz mal Variable:  x² · x"""
    v, e1, e2 = p["var"], p["exp"], p["exp2"]
    links = Pz(v, e1) if e1 > 1 else v
    rechts = Pz(v, e2) if e2 > 1 else v
    return bau("+", [K(links, rechts)], extra=[
        F("hochzahlen_multipliziert", v ** (e1 * e2),
          f"Beim Multiplizieren werden die Hochzahlen addiert: "
          f"{e1} + {e2} = {e1 + e2}."),
        F("hochzahl_gleich", v ** max(e1, e2),
          f"Beide Faktoren zählen: {zeige(v)} kommt {e1 + e2}-mal vor."),
    ], loesung=v ** (e1 + e2))


BF22_11 = Bauform("BF11", "Variablenpotenz mal Variable",
    bereiche={"A": {"var": VARIABLEN, "exp": [2], "exp2": [1]},
              "B": {"var": VARIABLEN, "exp": [1, 3], "exp2": [3, 1]},
              "C": {"var": VARIABLEN, "exp": [2, 3], "exp2": [2, 3, 4]}},
    bauen=bf22_11, filter=[fehler_eindeutig, hat_fehler,
                           exponent_hoechstens(10)])


def bf22_12(p):
    """Potenz mal Zahl:  2³ · 5"""
    bs, e, k = Integer(p["basis"]), p["exp"], Integer(p["koeff"])
    kette = K(Pz(bs, e), k) if p["potenz_vorne"] else K(k, Pz(bs, e))
    glieder = [kette]
    muster = "+"
    if p["dritt"]:
        glieder.append(K(Integer(p["dritt"])))
        muster = "+-"
    return bau(muster, glieder)


BF22_12 = Bauform("BF12", "Potenz mal Zahl",
    bereiche={"A": {"basis": [2, 3], "exp": [2, 3], "koeff": [5, 4],
                    "potenz_vorne": [True], "dritt": [0], "var": VARIABLEN},
              "B": {"basis": [4, 5], "exp": [3], "koeff": [3, 2],
                    "potenz_vorne": [False], "dritt": [0], "var": VARIABLEN},
              "C": {"basis": [3], "exp": [5], "koeff": [2],
                    "potenz_vorne": [False], "dritt": [4, 6],
                    "var": VARIABLEN}},
    bauen=bf22_12, filter=STANDARD)


S22 = Schablone(
    nr="S22", titel="Potenzen verstehen",
    lektionen="7.1 – 7.2", erhebung="Vorstufe zu 3c",
    anleitung=ANLEITUNG,
    levelachse="Grösse des Exponenten",
    bauformen=[BF22_1, BF22_2, BF22_3, BF22_4, BF22_5, BF22_6,
               BF22_7, BF22_8, BF22_9, BF22_10, BF22_11, BF22_12],
    kernidee=("Eine Potenz ist eine Abkürzung für ein Produkt gleicher "
              "Faktoren. Der Exponent sagt, wie oft die Basis vorkommt — er "
              "wird nicht mit ihr multipliziert."),
)


# ══════════════════════════════════════════════════════════════════════════
# S23 · Potenz vor Punkt vor Strich, negative Basis   (Lektionen 7.3 – 7.4)
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 2: zwei → zwei bis drei → drei bis vier Glieder, und beim Vorzeichen
# ein Minus → zwei Minus → doppeltes Minus oder negative Basis.

MUSTER23 = {
    "A": ["+-"],
    "B": ["+--", "+-+"],
    "C": ["+-+-", "+--+", "+-++"],
}

#: Für Bauformen, die ihr Minus schon in der Klammer oder vor der Potenz
#: tragen (BF3 bis BF5, BF10). Dort ist das Vorzeichen die Bauform selbst,
#: das Level trägt die Gliederzahl.
MUSTER23_P = {
    "A": ["+"],
    "B": ["++", "+-"],
    "C": ["++-", "+-+", "+--"],
}

ZAHL23 = [2, 3, 4, 5]


def bau23(muster, glieder, extra=(), loesung=None):
    g = bau(muster, glieder, extra=extra, loesung=loesung,
            tipps=tipps_fuer(glieder, TIPPS23))
    return g


def bf23_1(p):
    """Zahl mal Potenz:  2 · 4²"""
    k, bs, e = Integer(p["koeff"]), Integer(p["basis"]), p["exp"]
    glieder = [K(k, Pz(bs, e))]
    muster = p["muster"]
    for i in range(1, len(muster)):
        glieder.append(K(Pz(Integer(p["basis2"]), 2 + i)))
    return bau23(muster, glieder, extra=[
        F("faktor_mitpotenziert", (k * bs) ** e + summe(
            muster[1:], glieder[1:]) if len(muster) > 1 else (k * bs) ** e,
          f"Die Potenz gilt nur für die {zeige(bs)}: {zeige(bs)}{hoch(e)} = "
          f"{zeige(bs ** e)}, danach {zeige(k)} · {zeige(bs ** e)}. "
          f"({zeige(k)} · {zeige(bs)}){hoch(e)} wäre etwas anderes."),
    ])


BEREICH23 = {lv: {"muster": MUSTER23[lv], "koeff": [2, 3], "basis": [3, 4, 5],
                  "basis2": [2, 3], "exp": [2, 3]} for lv in ("A", "B", "C")}

BF23_1 = Bauform("BF1", "Zahl mal Potenz",
    bereiche={lv: dict(BEREICH23[lv], muster=MUSTER23_P[lv])
              for lv in ("A", "B", "C")},
    bauen=bf23_1, filter=STANDARD_N)


def bf23_2(p):
    """Doppeltes Minus zwischen Potenzen:  2 · 4² − (−3)

    Auf Level C ist das Erhebungsaufgabe 3c:  2 · 4² − (−3) + 2³
    """
    k, bs, e = Integer(p["koeff"]), Integer(p["basis"]), p["exp"]
    minus = Integer(p["minuszahl"])
    glieder = [K(k, Pz(bs, e)), K(Kl(f"{MINUS}{zeige(minus)}", -minus))]
    muster = "+-"
    if p["drittes"] == "minus":
        #: Level B: drei Glieder, zwei Minus
        glieder.append(K(Pz(Integer(2), 3)))
        muster = "+--"
    elif p["drittes"] == "plus":
        #: Level C: das ist Erhebungsaufgabe 2 · 4² − (−3) + 2³
        glieder.append(K(Pz(Integer(2), 3)))
        muster = "+-+"
    return bau23(muster, glieder, extra=[
        F("doppelminus_nicht_aufgeloest",
          summe(muster.replace("-", "+", 1) if False else "++" + muster[2:],
                glieder),
          f"{MINUS}({MINUS}{zeige(minus)}) wird +{zeige(minus)}. Minus mal "
          f"Minus gibt Plus."),
    ])


BF23_2 = Bauform("BF2", "Doppeltes Minus zwischen Potenzen",
    bereiche={"A": {"koeff": [2], "basis": [4, 3], "exp": [2],
                    "minuszahl": [3, 4], "drittes": [""]},
              "B": {"koeff": [5, 3], "basis": [2, 3], "exp": [3],
                    "minuszahl": [4, 5], "drittes": ["minus"]},
              "C": {"koeff": [2, 3], "basis": [4, 3], "exp": [2],
                    "minuszahl": [3, 5], "drittes": ["plus"]}},
    bauen=bf23_2, filter=STANDARD_N)


def bf23_3(p):
    """Klammer wird potenziert, Ergebnis der Klammer negativ:  (5 − 7)²"""
    o, u = Integer(p["oben"]), Integer(p["unten"])
    e = p["exp"]
    kl = Pz(o - u, e, basis_text=f"{zeige(o)} {MINUS} {zeige(u)}", klammer=True)
    glieder = [K(kl)]
    muster = p["muster"]
    for i in range(1, len(muster)):
        glieder.append(K(Pz(Integer(2 + i), 2)))
    return bau23(muster, glieder, extra=[
        F("klammer_nicht_zuerst", (o ** e - u ** e) + summe(
            muster[1:], glieder[1:]) if len(muster) > 1 else o ** e - u ** e,
          f"Zuerst die Klammer: {zeige(o)} {MINUS} {zeige(u)} = "
          f"{zeige(o - u)}. Erst danach wird potenziert."),
    ])


BF23_3 = Bauform("BF3", "Klammer wird potenziert, Klammerergebnis negativ",
    bereiche={"A": {"oben": [5, 4, 3], "unten": [7, 6, 8], "exp": [2],
                    "muster": MUSTER23_P["A"]},
              "B": {"oben": [3, 2], "unten": [8, 7], "exp": [2],
                    "muster": MUSTER23_P["B"]},
              "C": {"oben": [2, 3], "unten": [6, 5], "exp": [2, 3],
                    "muster": MUSTER23_P["C"]}},
    bauen=bf23_3,
    filter=STANDARD_N + [lambda p, g: abs(p["oben"] - p["unten"]) >= 2])


def bf23_4(p):
    """Minus VOR der Potenz — die Basis ist positiv:  −7² = −49"""
    bs, e = Integer(p["basis"]), p["exp"]
    glieder = [K(Pz(bs, e))]
    muster = "-" + p["muster"][1:]
    for i in range(1, len(muster)):
        glieder.append(K(Pz(Integer(p["basis2"] + i - 1), 2)))
    return bau23(muster, glieder, extra=[
        F("minus_als_basis",
          summe("+" + muster[1:], glieder),
          f"Ohne Klammer gilt die Potenz zuerst: {MINUS}{zeige(bs)}{hoch(e)} "
          f"ist {MINUS}({zeige(bs)}{hoch(e)}) = {zeige(-bs ** e)}. Nur "
          f"({MINUS}{zeige(bs)}){hoch(e)} wäre {zeige((-bs) ** e)}."),
    ])


BF23_4 = Bauform("BF4", "Minus vor der Potenz — die Basis ist positiv",
    bereiche={"A": {"basis": [7, 5, 6], "exp": [2], "basis2": [2],
                    "muster": ["+"]},
              "B": {"basis": [3, 2], "exp": [4, 3], "basis2": [2],
                    "muster": ["++", "+-"]},
              "C": {"basis": [2, 3], "exp": [3], "basis2": [3, 2],
                    "muster": ["++-", "+-+"]}},
    bauen=bf23_4, filter=STANDARD_N)


def bf23_5(p):
    """Negative Basis in Klammern:  (−2)²"""
    bs, e = Integer(p["basis"]), p["exp"]
    glieder = [K(Pz(-bs, e, klammer=True))]
    muster = p["muster"]
    if len(muster) > 1:
        glieder.append(K(Pz(-bs, e - 1, klammer=True)))
    for i in range(2, len(muster)):
        glieder.append(K(Pz(Integer(2), 2)))
    return bau23(muster, glieder, extra=[
        F("vorzeichen_ignoriert",
          summe(muster, [K(Pz(bs, gg.teile[0].exp))
                         if isinstance(gg.teile[0], Pz) else gg
                         for gg in glieder]),
          f"Das Minus steht in der Klammer und gehört zur Basis: "
          f"({MINUS}{zeige(bs)}){hoch(e)} = {zeige((-bs) ** e)}."),
    ])


BF23_5 = Bauform("BF5", "Negative Basis in Klammern",
    bereiche={"A": {"basis": [2, 3], "exp": [2], "muster": ["+"]},
              "B": {"basis": [2, 3], "exp": [3], "muster": ["+-"]},
              "C": {"basis": [2], "exp": [4], "muster": ["+-+", "+--"]}},
    bauen=bf23_5, filter=STANDARD_N)


def bf23_6(p):
    """Zwei Klammern mit Potenzen, dazu Division.

    Auf Level C ist das Erhebungsaufgabe 3d:  (5 − 7)² · (3² − 2) : 2²
    """
    o, u = Integer(p["oben"]), Integer(p["unten"])
    bs2, ab = Integer(p["basis2"]), Integer(p["abzug"])
    links = Pz(o - u, 2, basis_text=f"{zeige(o)} {MINUS} {zeige(u)}",
               klammer=True)
    rechts = Kl(f"{zeige(bs2)}{hoch(2)} {MINUS} {zeige(ab)}", bs2 ** 2 - ab)
    if p["stufe"] == 1:
        #: Level A ist die blosse Klammer, ohne Klammerzeichen:  3² − 2
        return bau23("+-", [K(Pz(bs2, 2)), K(ab)], extra=[
            F("links_nach_rechts", (bs2 - ab) ** 2,
              f"Zuerst die Potenz: {zeige(bs2)}{hoch(2)} = "
              f"{zeige(bs2 ** 2)}, danach minus {zeige(ab)}."),
        ])
    if p["stufe"] == 2:
        kette = K(links, rechts)
    else:
        kette = Kette((links, rechts, Pz(Integer(p["teiler"]), 2)),
                      ("·", ":"))
    return bau23("+", [kette], extra=[
        F("klammer_nicht_zuerst", (o ** 2 - u ** 2) * (bs2 ** 2 - ab),
          f"Die Klammer kommt zuerst: {zeige(o)} {MINUS} {zeige(u)} = "
          f"{zeige(o - u)}, und ({zeige(o - u)}){hoch(2)} = "
          f"{zeige((o - u) ** 2)}."),
    ])


BF23_6 = Bauform("BF6", "Zwei Klammern mit Potenzen, dazu Division",
    bereiche={"A": {"oben": [5], "unten": [7], "basis2": [3, 4],
                    "abzug": [2, 3], "teiler": [2], "stufe": [1]},
              "B": {"oben": [5, 4], "unten": [7, 6], "basis2": [3],
                    "abzug": [2], "teiler": [2], "stufe": [2]},
              "C": {"oben": [5], "unten": [7], "basis2": [3], "abzug": [2],
                    "teiler": [2], "stufe": [3]}},
    bauen=bf23_6, filter=[fehler_eindeutig, hat_fehler, ganzzahlig])


def bf23_7(p):
    """Zwei Potenzen addieren oder subtrahieren:  3² + 4²"""
    muster = p["muster"]
    bs, e = Integer(p["basis"]), p["exp"]
    glieder = [K(Pz(bs, e)), K(Pz(bs + 1, e))]
    for i in range(2, len(muster)):
        glieder.append(K(Pz(bs + i, max(e - 1, 1))))
    return bau23(muster, glieder)


BF23_7 = Bauform("BF7", "Zwei Potenzen addieren oder subtrahieren",
    bereiche={"A": {"muster": ["+-"], "basis": [3, 4, 5], "exp": [2]},
              "B": {"muster": ["+--"], "basis": [5, 4], "exp": [2, 3]},
              "C": {"muster": ["+-+-", "+--+"], "basis": [2, 3], "exp": [3]}},
    bauen=bf23_7, filter=STANDARD_N)


def bf23_8(p):
    """Potenz geteilt durch Potenz:  2³ : 2²  —  ausgerechnet, nicht mit
    dem Potenzgesetz. Das Gesetz ist 7.6 und damit S24."""
    bs, e1, e2 = Integer(p["basis"]), p["exp"], p["exp2"]
    if p["art"] == "klammer":
        #: Level C:  (4² − 2²) : 2²  — so steht es in Teil 1.
        oben = Integer(p["basis2"]) ** 2 - bs ** 2
        kl = Kl(f"{zeige(p['basis2'])}{hoch(2)} {MINUS} {zeige(bs)}{hoch(2)}",
                oben)
        return bau23("+", [Kette((kl, Pz(bs, 2)), (":",))], extra=[
            F("klammer_nicht_zuerst", Integer(p["basis2"]) ** 2 - Integer(1),
              f"Zuerst die Klammer ausrechnen: "
              f"{zeige(p['basis2'])}{hoch(2)} {MINUS} {zeige(bs)}{hoch(2)} = "
              f"{zeige(oben)}."),
        ])
    if p["art"] == "zwei_basen":
        #: Level B: zwei Glieder, zwei verschiedene Basen
        kette = Kette((Pz(Integer(p["basis2"]), e1), Pz(bs, e1)), (":",))
        return bau23("+-", [kette, K(Pz(bs, e2))])
    kette = Kette((Pz(bs, e1), Pz(bs, e2)), (":",))
    return bau23("+", [kette])


BF23_8 = Bauform("BF8", "Potenz geteilt durch Potenz",
    bereiche={"A": {"basis": [2, 3], "exp": [3], "exp2": [2],
                    "art": ["einfach"], "basis2": [6]},
              "B": {"basis": [3, 2], "exp": [2], "exp2": [1],
                    "art": ["zwei_basen"], "basis2": [6, 4]},
              "C": {"basis": [2], "exp": [2], "exp2": [2],
                    "art": ["klammer"], "basis2": [4, 6]}},
    bauen=bf23_8, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler,
                          ganzzahlig, loesung_nicht_null])


def bf23_9(p):
    """Sonderfall: das Ergebnis ist null:  (3 − 3)²  ·  2³ − 2³"""
    bs, e = Integer(p["basis"]), p["exp"]
    if p["art"] == "klammer":
        glieder = [K(Pz(Integer(0), e,
                        basis_text=f"{zeige(bs)} {MINUS} {zeige(bs)}",
                        klammer=True))]
        muster = "+"
    elif p["art"] == "gleich":
        glieder = [K(Pz(bs, e)), K(Pz(bs, e))]
        muster = "+-"
    else:
        glieder = [K(Integer(p["koeff"]),
                     Kl(f"{zeige(bs)}{hoch(2)} {MINUS} {zeige(bs ** 2)}",
                        Integer(0)))]
        muster = "+"
    return bau23(muster, glieder, loesung=0, extra=[
        F("nicht_null", bs ** e,
          "Beide Teile heben sich genau auf — das Ergebnis ist null."),
    ])


BF23_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"basis": [3, 4, 5], "exp": [2], "art": ["klammer"],
                    "koeff": [5]},
              "B": {"basis": [2, 3], "exp": [3, 4], "art": ["gleich"],
                    "koeff": [5]},
              "C": {"basis": [2, 3], "exp": [2], "art": ["faktor"],
                    "koeff": [5, 4]}},
    bauen=bf23_9, filter=[fehler_eindeutig, hat_fehler])


def bf23_10(p):
    """Sonderfall: Basis minus eins:  (−1)⁴ = 1,  (−1)⁵ = −1"""
    e = p["exp"]
    glieder = [K(Pz(Integer(-1), e, klammer=True))]
    muster = "+"
    if p["mal"]:
        glieder = [K(Pz(Integer(-1), e, klammer=True),
                     Pz(Integer(p["basis"]), 2))]
    elif p["zweites"]:
        #: Level B: zwei Glieder, damit sich A und B im Aufbau unterscheiden
        glieder.append(K(Pz(Integer(p["basis"]), 2)))
        muster = "+-"
    return bau23(muster, glieder, extra=[
        F("immer_eins", Integer(1) if e % 2 else Integer(-1),
          "Bei ungerader Hochzahl bleibt das Minus stehen, bei gerader "
          "nicht. Zähl die Faktoren."),
    ])


BF23_10 = Bauform("BF10", "Sonderfall: Basis minus eins",
    bereiche={"A": {"exp": [4, 6], "mal": [False], "zweites": [False],
                    "basis": [3]},
              "B": {"exp": [5, 7], "mal": [False], "zweites": [True],
                    "basis": [3, 2]},
              "C": {"exp": [4, 5], "mal": [True], "zweites": [False],
                    "basis": [3, 2]}},
    bauen=bf23_10, filter=[fehler_eindeutig, hat_fehler])


def bf23_11(p):
    """Potenz mitten in einem Strichterm:  2 + 3 · 2²"""
    muster = p["muster"]
    z, k, bs = Integer(p["zahl"]), Integer(p["koeff"]), Integer(p["basis"])
    glieder = [K(z), K(k, Pz(bs, p["exp"]))]
    for i in range(2, len(muster)):
        glieder.append(K(Pz(Integer(4), 2)))
    return bau23(muster, glieder, extra=[
        F("links_nach_rechts", _lnr(muster, glieder),
          f"Punkt vor Strich: zuerst {zeige(bs)}{hoch(p['exp'])} = "
          f"{zeige(bs ** p['exp'])}, dann mal {zeige(k)}, erst danach "
          f"plus und minus."),
    ])


def _lnr(muster, glieder):
    """Stur von links nach rechts, ohne Punkt vor Strich."""
    acc = None
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        erst = teil_wert(g.teile[0])
        if i == 0:
            acc = erst if zeichen == "+" else -erst
        else:
            acc = acc + erst if zeichen == "+" else acc - erst
        for j, op in enumerate(g.ops):
            rechts = teil_wert(g.teile[j + 1])
            acc = acc / rechts if op == ":" else acc * rechts
    return acc


BF23_11 = Bauform("BF11", "Potenz mitten in einem Strichterm",
    bereiche={"A": {"muster": ["+-"], "zahl": [20, 18], "koeff": [2, 3],
                    "basis": [3, 2], "exp": [2]},
              "B": {"muster": ["+-", "++"], "zahl": [20, 25], "koeff": [2],
                    "basis": [3], "exp": [2, 3]},
              "C": {"muster": ["++-", "+-+"], "zahl": [5, 8], "koeff": [2],
                    "basis": [3], "exp": [2]}},
    bauen=bf23_11, filter=STANDARD_N)


def bf23_12(p):
    """Klammer potenziert gegen Faktor potenziert:  (2 · 3)² − 2 · 3²"""
    k, bs, e = Integer(p["koeff"]), Integer(p["basis"]), p["exp"]
    klammer = K(Pz(k * bs, e, basis_text=f"{zeige(k)} · {zeige(bs)}",
                   klammer=True))
    faktor = K(k, Pz(bs, e))
    if p["art"] == "klammer":
        glieder, muster = [klammer], "+"
    elif p["art"] == "faktor":
        glieder, muster = [faktor], "+"
    else:
        glieder, muster = [klammer, faktor], "+-"
    return bau23(muster, glieder, extra=[
        F("verwechselt", (k * bs) ** e if p["art"] == "faktor" else k * bs ** e,
          f"({zeige(k)} · {zeige(bs)}){hoch(e)} ist "
          f"{zeige((k * bs) ** e)}, aber {zeige(k)} · {zeige(bs)}{hoch(e)} "
          f"ist {zeige(k * bs ** e)}. Die Klammer entscheidet."),
    ])


BF23_12 = Bauform("BF12", "Klammer potenziert gegen Faktor potenziert",
    bereiche={"A": {"koeff": [2], "basis": [3, 4], "exp": [2],
                    "art": ["klammer"]},
              "B": {"koeff": [2], "basis": [3, 4], "exp": [2],
                    "art": ["faktor"]},
              "C": {"koeff": [2], "basis": [3], "exp": [2],
                    "art": ["beide"]}},
    bauen=bf23_12, filter=STANDARD_N)


S23 = Schablone(
    nr="S23", titel="Potenz vor Punkt vor Strich, negative Basis",
    lektionen="7.3 – 7.4", erhebung="3c",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF23_1, BF23_2, BF23_3, BF23_4, BF23_5, BF23_6,
               BF23_7, BF23_8, BF23_9, BF23_10, BF23_11, BF23_12],
    kernidee=("Klammer vor Potenz vor Punkt vor Strich. Ein Minus ohne "
              "Klammer gehört nicht zur Basis: −7² ist −49, aber (−7)² "
              "ist +49."),
)
