# -*- coding: utf-8 -*-
"""
S49 · Bruchterme kürzen                        (Lektionen 14.3 – 14.4)
S50 · Bruchterme addieren bei gleichem Nenner  (Lektion  14.6)
S51 · Multiplizieren, dividieren, Doppelbruch  (Lektionen 14.9 – 14.11)

    «Rechne aus.»
    6d/(3d)      (2a + 4)/2      2x/(3y) + x/(3y)      (8b/(9a)) : (4a/(3b))

Drei Erhebungsaufgaben auf einmal: **5b** liegt bei 14.4 (S49), **5a** bei
14.8 und **5c** bei 14.11 (S51, BF2 auf Level B im Wortlaut).

DIE PRÜFREGEL «IST ES FERTIG» GILT HIER BESONDERS. Die Zielform ist
GEKUERZT: eine Antwort, die richtig gerechnet, aber nicht fertiggekürzt ist,
kommt als «Stimmt — aber das lässt sich noch kürzen» zurück, nicht als
falsch. Laut Schablone ist das fast die Hälfte aller Fehler in dieser
Lektion.

Aus demselben Grund steht der ungekürzte Bruch NICHT im Fehlerkatalog: er
ist kein Fehler, sondern eine unfertige Antwort, und die App sagt das schon
von sich aus.

LEVELACHSE (Teil 2 der drei Schablonen):

    S49   Struktur des Zählers   Monom → Monom mit mehreren Variablen →
                                 Summe oder Binom
    S50   Struktur des Zählers   zwei Brüche → zwei mit Vorzeichenwechsel →
                                 drei Brüche
    S51   Struktur der Verknüpfung   mal → geteilt → Doppelbruch

Die Bausteine für Monome und Summen kommen aus `s9_division` — dort stehen
sie schon, und dreimal dieselbe Mechanik zu schreiben wäre dreimal dieselbe
Fehlerquelle.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational, cancel, expand, factor, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s9_division import M, Su, _reihe
from .schablone import Bauform, Schablone

a, b, c, d, k, m, n, p_, q, r, u, v, w, x, y, z = symbole(
    "a b c d k m n p q r u v w x y z")
VARS = {"a", "b", "c", "d", "k", "m", "n", "p", "q", "r",
        "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus und kürze so weit wie möglich."

SORTE1 = [x, a, u, p_]
SORTE2 = [y, b, v, q]
SORTE3 = [z, c, w, r]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ══════════════════════════════════════════════════════════════════════════
# Der Bruchterm
# ══════════════════════════════════════════════════════════════════════════

def _klammer(teil) -> str:
    """Ein Nenner bekommt Klammern, sobald er aus mehr als einem Stück
    besteht — `6d/(3d)`, aber `x³/x`."""
    t = teil.text
    if isinstance(teil, Su):
        return t                      # Su bringt seine Klammern selbst mit
    if len(t) > 1 and not t.lstrip(MINUS).isalnum():
        return f"({t})"
    kk = sympify(getattr(teil, "koeff", 1))
    if kk != 1 and getattr(teil, "basen", ()):
        return f"({t})"
    if kk < 0:
        return f"({t})"
    return t


@dataclass(frozen=True)
class B:
    """Ein Bruchterm:  6d/(3d)   ·   (2a + 4)/2"""
    zaehler: object
    nenner: object

    @property
    def wert(self):
        return sympify(self.zaehler.wert) / self.nenner.wert

    @property
    def text(self) -> str:
        oben = self.zaehler.text
        if isinstance(self.zaehler, M) and sympify(self.zaehler.koeff) < 0:
            pass                       # ein negativer Zaehler darf so stehen
        return f"{oben}/{_klammer(self.nenner)}"


@dataclass(frozen=True)
class G:
    """Ein ganzer Term ohne Bruchstrich als Faktor:  (x + 1)"""
    inhalt: object

    @property
    def wert(self):
        return self.inhalt.wert

    @property
    def text(self) -> str:
        return self.inhalt.text


def reihe_b(muster, glieder) -> str:
    """Brüche mit + und − verbinden."""
    return _reihe(muster, glieder)


def kette(teile, ops) -> str:
    """Brüche mit · und : verbinden — jeder Bruch in eigenen Klammern,
    so wie es in der Schablone steht."""
    raus = f"({teile[0].text})"
    for i, op in enumerate(ops):
        raus += f" {op} ({teile[i + 1].text})"
    return raus


def summe(muster, glieder):
    raus = Integer(0)
    for zeichen, g in zip(muster, glieder):
        raus += g.wert if zeichen == "+" else -g.wert
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════
#
# Fünf Einträge je Aufgabe. Der ungekürzte Bruch gehört NICHT dazu: er ist
# wertgleich mit der Lösung, und die Zielform GEKUERZT meldet ihn schon als
# «noch nicht fertig».


def kandidaten(zaehler, nenner, loesung, extra_zahl=None):
    raus = []
    l = cancel(sympify(loesung))
    zw = sympify(zaehler.wert)
    nw = sympify(nenner.wert)

    raus.append(F("vorzeichen", -l,
        "Zähl die Minuszeichen noch einmal: minus durch minus ergibt plus."))

    if l != 0:
        raus.append(F("kehrwert", 1 / l,
            "Zähler und Nenner stehen verkehrt herum."))

    raus.append(F("subtrahiert", expand(zw - nw),
        "Ein Bruchstrich heisst geteilt, nicht minus."))

    raus.append(F("addiert", expand(zw + nw),
        "Ein Bruchstrich heisst geteilt, nicht plus."))

    #: Der Kernfehler von Lektion 14.3: gekuerzt wird nur, was FAKTOR ist.
    #: Wer in (2a + 4)/2 nur den ersten Summanden teilt, bekommt a + 4.
    if getattr(zaehler, "glieder", None):
        erstes = zaehler.glieder[0]
        rest = Integer(0)
        for zeichen, g in list(zip(zaehler.muster, zaehler.glieder))[1:]:
            rest += g.wert if zeichen == "+" else -g.wert
        raus.append(F("summand_gekuerzt",
            expand(sympify(erstes.wert) / nw + rest),
            "Kürzen darf man nur Faktoren, nie einzelne Summanden. Wenn oben "
            "eine Summe steht, muss JEDES Glied geteilt werden."))

    #: Die Variable ist mitgekuerzt worden, obwohl sie oben blieb — oder
    #: umgekehrt stehen geblieben, obwohl sie wegfaellt.
    gemeinsam = Integer(1)
    for s in sorted(nw.free_symbols, key=str):
        if s in zw.free_symbols:
            gemeinsam *= s
    if gemeinsam != 1:
        raus.append(F("variable_geblieben", expand(l * gemeinsam),
            f"{zeige(gemeinsam)} steht oben UND unten und fällt beim Kürzen "
            f"ganz weg."))

    if extra_zahl is not None and extra_zahl != l:
        raus.append(extra_zahl)
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


TIPPS49 = [
    "Kürzen darf man nur Faktoren, nie einzelne Summanden.",
    "Zerleg Zähler und Nenner zuerst in Faktoren, dann siehst du, was sich "
    "wegkürzt.",
    "",
]

TIPPS50 = [
    "Bei gleichem Nenner werden nur die Zähler verrechnet — der Nenner "
    "bleibt stehen.",
    "Ein Minus vor einem Bruch gilt für den GANZEN Zähler.",
    "",
]

TIPPS51 = [
    "Beim Multiplizieren mal man Zähler mit Zähler und Nenner mit Nenner.",
    "Geteilt durch einen Bruch heisst mal den Kehrwert.",
    "",
]


def bau(frage, loesung, katalog, tipps, schritte=None):
    #: `cancel` ist Pflicht: SymPy laesst (a − b)/(b − a) stehen, und dann
    #: waere die Musterloesung selbst nicht fertig gekuerzt — die Zielform
    #: GEKUERZT haette sie als «geht noch» zurueckgewiesen.
    l = cancel(sympify(loesung))
    fehler = siebe(katalog, l)
    text = _als_text(l)
    return {
        "frage": frage, "loesung_text": text,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                           zielform=Zielform.GEKUERZT, fehlerkatalog=fehler),
        "schritte": schritte or [
            ("Zähler und Nenner in Faktoren zerlegen", frage),
            ("Gemeinsame Faktoren streichen", "was oben und unten steht, "
                                              "fällt weg"),
            ("Ergebnis", text),
        ],
        "tipps": [tipps[0], tipps[1], f"Am Schluss steht {text}."],
    }


def _als_text(l) -> str:
    """Die Lösung hinschreiben. Bei einem Bruch mit Zähler und Nenner."""
    from sympy import fraction
    p, q = fraction(sympify(l))
    if q == 1:
        return zeige(p)
    oben = zeige(p)
    #: Ohne Klammer heisst «20u − 25v/(15u)» nach Punktrechnung etwas ganz
    #: anderes als der Bruch, den wir meinen. Beim Testlauf hat der Parser
    #: die eigene Musterloesung darum als falsch abgewiesen.
    if p.is_Add:
        oben = f"({oben})"
    unten = zeige(q)
    if len(unten) > 1 or q.is_Add:
        unten = f"({unten})"
    return f"{oben}/{unten}"


# ── Filter ────────────────────────────────────────────────────────────────

def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def klein(p, g) -> bool:
    l = g["aufgabe"].loesung.expr
    for t in sympify(l).atoms(Rational):
        if abs(t.p) > 200 or t.q > 200:
            return False
    return True


def verschieden(*namen):
    def f(p, g):
        werte = [str(p[nn]) for nn in namen if nn in p]
        return len(set(werte)) == len(werte)
    return f


STANDARD = [kopfrechenbar, fehler_eindeutig, fuenf, klein]
ZWEI = STANDARD + [verschieden("v1", "v2")]
DREI = STANDARD + [verschieden("v1", "v2", "v3")]


# ══════════════════════════════════════════════════════════════════════════
# S49 · Bruchterme kürzen        (Lektionen 14.3 – 14.4)
# ══════════════════════════════════════════════════════════════════════════

BEREICH49 = {
    "A": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [2, 3],
          "k": [2, 3, 4], "e": [1], "vz": [1], "stufe": [1]},
    "B": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [3, 4],
          "k": [3, 4, 5], "e": [2], "vz": [-1], "stufe": [2]},
    "C": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [4, 5],
          "k": [2, 3, 5], "e": [2, 3], "vz": [-1], "stufe": [3]},
}


def b49(frage, loesung, katalog):
    return bau(frage, loesung, katalog, TIPPS49)


def bf49_1(p):
    """Die Variable fällt ganz weg:  6d/(3d)"""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    e = 1 if st == 1 else st - 1
    oben = M(Integer(p["vz"] * f * k), ((v1, e),))
    unten = M(Integer(k), ((v1, e),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_1 = Bauform("BF1", "Die Variable fällt ganz weg",
    bereiche=BEREICH49, bauen=bf49_1, filter=STANDARD)


def bf49_2(p):
    """Mehrere Variablen, eine bleibt oben:  4xy/(2x)"""
    v1, v2, f, k = p["v1"], p["v2"], p["f"], p["k"]
    st = p["stufe"]
    if st == 3:
        oben = M(Integer(p["vz"] * f * k), ((v1, 2), (v2, 1), (p["v3"], 2)))
        unten = M(Integer(k), ((v1, 1), (v2, 1), (p["v3"], 1)))
    elif st == 2:
        oben = M(Integer(p["vz"] * f * k), ((v1, 1), (v2, 1), (p["v3"], 1)))
        unten = M(Integer(k), ((v1, 1), (p["v3"], 1)))
    else:
        oben = M(Integer(f * k), ((v1, 1), (v2, 1)))
        unten = M(Integer(k), ((v1, 1),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_2 = Bauform("BF2", "Mehrere Variablen, eine bleibt oben",
    bereiche=BEREICH49, bauen=bf49_2, filter=DREI)


def bf49_3(p):
    """Nur Potenzen derselben Variablen:  x³/x  ·  x⁵y³/(x²y⁵)"""
    v1, v2, st = p["v1"], p["v2"], p["stufe"]
    if st == 3:
        oben = M(Integer(1), ((v1, 5), (v2, 3)))
        unten = M(Integer(1), ((v1, 2), (v2, 5)))
    elif st == 2:
        oben = M(Integer(1), ((v1, 4), (v2, 1)))
        unten = M(Integer(1), ((v1, 2), (v2, 1)))
    else:
        oben = M(Integer(1), ((v1, 3),))
        unten = M(Integer(1), ((v1, 1),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_3 = Bauform("BF3", "Nur Potenzen derselben Variablen",
    bereiche=BEREICH49, bauen=bf49_3, filter=ZWEI)


def bf49_4(p):
    """Summe im Zähler — nur der Zahlfaktor darf weg:  (2a + 4)/2

    Das ist die Bauform, auf die Lektion 14.3 zielt: «Nur Faktoren kürzen,
    nie Summanden.»
    """
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        oben = Su("+-", (M(Integer(4 * k), ((v1, 1),)),
                         M(Integer(5 * k), ((v2, 1),))))
        unten = M(Integer(3 * k), ((v1, 1),))
    elif st == 2:
        oben = Su("++", (M(Integer(2 * k), ((v1, 1),)), M(Integer(10 * k))))
        unten = M(Integer(2 * k), ((v1, 1),))
    else:
        oben = Su("++", (M(Integer(k), ((v1, 1),)), M(Integer(2 * k))))
        unten = M(Integer(k))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_4 = Bauform("BF4", "Summe im Zähler — nur der Zahlfaktor darf weg",
    bereiche=BEREICH49, bauen=bf49_4, filter=ZWEI)


def bf49_5(p):
    """Zähler und Nenner unterscheiden sich nur im Vorzeichen:
       (a − b)/(b − a)  →  −1"""
    v1, v2, f, st = p["v1"], p["v2"], p["f"], p["stufe"]
    #: A: (a − b)/(b − a).  B: der Nenner bekommt einen Zahlfaktor.
    #: C: der Zaehler bekommt einen — so unterscheidet sich der Aufbau.
    g = f if st == 3 else 1
    h = f if st == 2 else 1
    oben = Su("+-", (M(Integer(g), ((v1, 1),)), M(Integer(g), ((v2, 1),))))
    unten = Su("+-", (M(Integer(h), ((v2, 1),)), M(Integer(h), ((v1, 1),))))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert, extra_zahl=F(
        "vorzeichen_uebersehen", Integer(g),
        "Oben und unten steht dasselbe, nur mit umgekehrtem Vorzeichen. Das "
        "ergibt ein Minus.")))


BF49_5 = Bauform("BF5", "Zähler und Nenner unterscheiden sich nur im Vorzeichen",
    bereiche=BEREICH49, bauen=bf49_5, filter=ZWEI)


def bf49_6(p):
    """Dritte binomische Formel im Zähler:  (x² − 1)/(x − 1)  →  x + 1"""
    v1, k, st = p["v1"], p["k"], p["stufe"]
    oben = Su("+-", (M(Integer(1), ((v1, 2),)), M(Integer(k * k))))
    if st == 3:
        #: (y² − 9)/(y² + 6y + 9)  —  unten steht ein zweites Binom
        unten = Su("+++", (M(Integer(1), ((v1, 2),)),
                           M(Integer(2 * k), ((v1, 1),)),
                           M(Integer(k * k))))
    else:
        unten = Su("+-" if st == 1 else "++",
                   (M(Integer(1), ((v1, 1),)), M(Integer(k))))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_6 = Bauform("BF6", "Dritte binomische Formel im Zähler",
    bereiche=BEREICH49, bauen=bf49_6, filter=STANDARD)


def bf49_7(p):
    """Nach dem Ausklammern kürzt sich die Klammer weg:
       (2x + 2)/(x + 1)  →  2"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        oben = Su("++", (M(Integer(f), ((v1, 1),)),
                         M(Integer(2 * f), ((v2, 1),))))
        unten = Su("++", (M(Integer(1), ((v1, 1),)),
                          M(Integer(2), ((v2, 1),))))
    elif st == 2:
        oben = Su("+-", (M(Integer(f), ((v1, 1),)), M(Integer(2 * f))))
        unten = Su("+-", (M(Integer(1), ((v1, 1),)), M(Integer(2))))
    else:
        oben = Su("++", (M(Integer(f), ((v1, 1),)), M(Integer(f))))
        unten = Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(1))))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_7 = Bauform("BF7", "Nach dem Ausklammern kürzt sich die Klammer weg",
    bereiche=BEREICH49, bauen=bf49_7, filter=ZWEI)


def bf49_8(p):
    """Sonderfall: nur die Variable bleibt übrig:  5x/5  ·  7ab/(7b)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 1:
        oben = M(Integer(k), ((v1, 1),))
        unten = M(Integer(k))
    elif st == 2:
        oben = M(Integer(k), ((v1, 1), (v2, 1)))
        unten = M(Integer(k), ((v2, 1),))
    else:
        oben = M(Integer(-k), ((v1, 1), (v2, 1)))
        unten = M(Integer(k), ((v2, 1),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert, extra_zahl=F(
        "eins_geschrieben", Integer(1),
        "Die Zahl kürzt sich zu 1 weg — übrig bleibt die Variable, nicht "
        "die Eins.")))


BF49_8 = Bauform("BF8", "Sonderfall: nur die Variable bleibt übrig",
    bereiche=BEREICH49, bauen=bf49_8, filter=ZWEI)


def bf49_9(p):
    """Sonderfall: der Zähler ist null:  0/(3x)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    oben = M(Integer(0))
    if st == 1:
        unten = M(Integer(k), ((v1, 1),))
    elif st == 2:
        unten = Su("++", (M(Integer(1), ((v1, 1),)),
                          M(Integer(1), ((v2, 1),))))
    else:
        unten = Su("+-", (M(Integer(1), ((v1, 2),)), M(Integer(k * k))))
    br = B(oben, unten)
    return b49(br.text, Integer(0), [
        F("nenner_geblieben", unten.wert,
          "Null geteilt durch irgendetwas bleibt null."),
        F("eins", Integer(1),
          "Null geteilt durch etwas ist null, nicht eins."),
        F("zaehler_ignoriert", Integer(k),
          "Sobald oben null steht, ist der ganze Bruch null."),
        F("minus_eins", Integer(-1),
          "Null bleibt null, egal was unten steht."),
        F("nenner_zahl", Integer(k * k),
          "Der Nenner spielt keine Rolle, wenn oben null steht."),
    ])


BF49_9 = Bauform("BF9", "Sonderfall: der Zähler ist null",
    bereiche=BEREICH49, bauen=bf49_9, filter=[kopfrechenbar, fuenf])


def bf49_10(p):
    """Sonderfall: das Ergebnis ist eins:  4x/(4x)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    if st == 3:
        teil = Su("++", (M(Integer(1), ((v1, 1),)), M(Integer(k))))
        oben = unten = teil
    elif st == 2:
        oben = unten = M(Integer(-k), ((v1, 1), (v2, 1)))
    else:
        oben = unten = M(Integer(k), ((v1, 1),))
    br = B(oben, unten)
    return b49(br.text, Integer(1), [
        F("null", Integer(0),
          "Etwas geteilt durch sich selbst ergibt eins, nicht null."),
        F("term_geblieben", oben.wert,
          "Oben und unten steht dasselbe — es kürzt sich vollständig weg."),
        F("minus_eins", Integer(-1),
          "Beide Seiten sind gleich, also ist das Ergebnis +1."),
        F("zahl", Integer(k),
          "Auch die Zahl kürzt sich weg."),
        F("zwei", Integer(2),
          "Etwas geteilt durch sich selbst ist immer eins."),
    ])


BF49_10 = Bauform("BF10", "Sonderfall: das Ergebnis ist eins",
    bereiche=BEREICH49, bauen=bf49_10, filter=[kopfrechenbar, fuenf, klein])


def bf49_11(p):
    """Vorzeichen an verschiedenen Stellen:  −6x/(3x)  ·  −24uv²/(−8uv)"""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    if st == 3:
        oben = M(Integer(-f * k), ((v1, 1), (v2, 2)))
        unten = M(Integer(-k), ((v1, 1), (v2, 1)))
    elif st == 2:
        oben = M(Integer(-f * k), ((v1, 2),))
        unten = M(Integer(k), ((v1, 1),))
    else:
        oben = M(Integer(-f * k), ((v1, 1),))
        unten = M(Integer(k), ((v1, 1),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_11 = Bauform("BF11", "Vorzeichen an verschiedenen Stellen",
    bereiche=BEREICH49, bauen=bf49_11, filter=ZWEI)


def bf49_12(p):
    """Gemeinsamer Faktor im Zähler ausklammern:  (ab + ac)/a  →  b + c"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    k = p["k"]
    if st == 3:
        oben = Su("++", (M(Integer(3 * k), ((v1, 2),)),
                         M(Integer(6 * k), ((v1, 1), (v2, 1)))))
        unten = M(Integer(3 * k), ((v1, 1),))
    elif st == 2:
        oben = Su("++", (M(Integer(1), ((v1, 1), (v2, 1))),
                         M(Integer(1), ((v1, 1), (v3, 1)))))
        unten = M(Integer(1), ((v1, 1),))
    else:
        oben = Su("++", (M(Integer(1), ((v1, 2),)),
                         M(Integer(1), ((v1, 1),))))
        unten = M(Integer(1), ((v1, 1),))
    br = B(oben, unten)
    return b49(br.text, br.wert, kandidaten(oben, unten, br.wert))


BF49_12 = Bauform("BF12", "Gemeinsamer Faktor im Zähler ausklammern",
    bereiche=BEREICH49, bauen=bf49_12, filter=DREI)


S49 = Schablone(
    nr="S49", titel="Bruchterme kürzen",
    lektionen="14.3 – 14.4", erhebung="5b",
    anleitung=ANLEITUNG,
    levelachse="Struktur des Zählers",
    bauformen=[BF49_1, BF49_2, BF49_3, BF49_4, BF49_5, BF49_6,
               BF49_7, BF49_8, BF49_9, BF49_10, BF49_11, BF49_12],
    kernidee=("Kürzen darf man nur Faktoren, nie einzelne Summanden. Steht "
              "oben eine Summe, muss zuerst ausgeklammert werden."),
)
