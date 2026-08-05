# -*- coding: utf-8 -*-
"""
Kapitel 5 · Variablen multiplizieren      (Lektionen 5.1 – 5.8)

    S18  Variablen multiplizieren          5.1 – 5.4   Vorstufe zu 2a und 2c
    S19  Produkte vereinfachen, mit Vorzeichen   5.5 – 5.8   Erhebung 2b

WICHTIG, und beide Schablonen sagen es ausdruecklich: hier gibt es KEINE
SUMMEN. Die Kette 5.1 ← 3.9 fuehrt nicht ueber 3.10 und 3.11, Terme wie
3a + 4 sind also noch nicht verfuegbar. Alle Aufgaben sind reine Produkte.

Potenzen kommen ebenfalls nur als ERGEBNIS vor. a² entsteht hier durch das
Multiplizieren; als Bestandteil der Aufgabe waere es 7.2 und damit zu frueh.

LEVELACHSE (Teil 2 beider Schablonen) — hier ist es ausnahmsweise nicht die
Gliederzahl, sondern das Vorzeichen:

    S18   Minuszeichen   keines → eines → zwei bis drei
    S19   Minuszeichen   eines  → zwei  → drei bis vier
    beide Anzahl Faktoren   Minimum → Minimum bzw. eines mehr → zwei mehr

Erst bei mehreren Minuszeichen muss man zaehlen, ob das Ergebnis positiv
oder negativ wird. Das ist der eigentliche Lernschritt von 5.8.
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar, symbole_verschieden
from .schablone import Bauform, Schablone

a, b, c, d, m, n, p_, q, u, v, w, x, y, z = symbole(
    "a b c d m n p q u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "p", "q", "u", "v", "w", "x", "y", "z"}

SORTE1 = [a, x, u, p_]
SORTE2 = [b, y, v, q]
SORTE3 = [c, z, w, d]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ── Ein Produkt aus Faktoren ──────────────────────────────────────────────
#
# Ein Faktor ist (Zahl, [Variablen]). Daraus entstehen Anzeige und Wert.
# Negative Faktoren stehen in Klammern — genau so steht es in den Beispielen
# der Schablone: (−3) · b, (−4b) · 6b, 3a · (−b) · (−c).

def faktor_text(zahl, vs) -> str:
    kern = ""
    if not vs:
        kern = str(abs(zahl))
    else:
        kern = ("" if abs(zahl) == 1 else str(abs(zahl))) + \
               "".join(zeige(s) for s in vs)
    return f"({MINUS}{kern})" if zahl < 0 else kern


def produkt_text(faktoren) -> str:
    teile = []
    for i, (zahl, vs) in enumerate(faktoren):
        txt = faktor_text(zahl, vs)
        # Der erste Faktor braucht keine Klammer, wenn er positiv ist.
        teile.append(txt)
    return " · ".join(teile)


def produkt_wert(faktoren):
    r = Integer(1)
    for zahl, vs in faktoren:
        r *= Integer(zahl)
        for s in vs:
            r *= s
    return r


def ohne_potenzen(faktoren):
    """Was herauskommt, wenn jemand a · a als a stehen laesst."""
    zahl = Integer(1)
    gesehen = []
    for k, vs in faktoren:
        zahl *= Integer(k)
        for s in vs:
            if s not in gesehen:
                gesehen.append(s)
    r = zahl
    for s in gesehen:
        r *= s
    return r


def zahlen_addiert(faktoren):
    """Was herauskommt, wenn jemand die Zahlen zusammenzaehlt."""
    summe = sum(Integer(k) for k, _ in faktoren)
    r = Integer(summe)
    zaehler = {}
    for _, vs in faktoren:
        for s in vs:
            zaehler[s] = zaehler.get(s, 0) + 1
    for s, e in zaehler.items():
        r *= s ** e
    return r


def eine_nicht_potenziert(faktoren):
    """Was herauskommt, wenn nur eine Variable die Hochzahl bekommt."""
    zahl = Integer(1)
    zaehler = {}
    for k, vs in faktoren:
        zahl *= Integer(k)
        for s in vs:
            zaehler[s] = zaehler.get(s, 0) + 1
    mehrfach = [s for s, e in zaehler.items() if e > 1]
    if not mehrfach:
        return None
    letzte = mehrfach[-1]
    r = zahl
    for s, e in zaehler.items():
        r *= s ** (1 if s is letzte else e)
    return r


TIPPS = [
    "Zähl zuerst die Minuszeichen: eine gerade Anzahl ergibt plus, eine "
    "ungerade minus.",
    "Multipliziere dann alle Zahlen miteinander — nicht addieren.",
    "Zähl für jede Variable, wie oft sie vorkommt. Das ist ihre Hochzahl.",
]


def schritte(faktoren, loesung):
    minus = sum(1 for k, _ in faktoren if k < 0)
    zahlen = [abs(k) for k, _ in faktoren]
    produkt = 1
    for k in zahlen:
        produkt *= k
    zaehler = {}
    for _, vs in faktoren:
        for s in vs:
            zaehler[s] = zaehler.get(s, 0) + 1
    return [
        ("Minuszeichen zählen",
         f"{minus} Stück — Ergebnis {'positiv' if minus % 2 == 0 else 'negativ'}"),
        ("Alle Zahlen multiplizieren",
         " · ".join(str(k) for k in zahlen) + f" = {produkt}"),
        ("Jede Variable zählen",
         "   ".join(f"{zeige(s)}: {e}mal" for s, e in zaehler.items())),
        ("Zusammensetzen", zeige(loesung)),
    ]


def bau(faktoren, extra_fehler=None):
    """Aufgabe aus Faktoren bauen.

    Die Fehlerkandidaten werden am Schluss zweifach gesiebt: was gleich der
    Loesung ist, faellt weg, und was zweimal denselben Wert ergibt, ebenfalls.
    Ohne dieses Sieb liessen sich sechs Bauformen gar nicht erzeugen — bei
    `2a · 2a · 2a` ergeben «Zahlen addiert» und «Zahlen addiert statt
    potenziert» beide 6a³, und `fehler_eindeutig` verwarf danach jede
    Aufgabe.
    """
    loesung = produkt_wert(faktoren)
    fehler = []
    ohne = ohne_potenzen(faktoren)
    if ohne != loesung:
        fehler.append(F("keine_potenz", ohne,
                        "Beim Multiplizieren wachsen die Hochzahlen: a · a "
                        "ergibt a², nicht a."))
    add = zahlen_addiert(faktoren)
    if add != loesung:
        fehler.append(F("zahlen_addiert", add,
                        "Die Zahlen werden multipliziert, nicht addiert."))
    if any(k < 0 for k, _ in faktoren):
        fehler.append(F("vorzeichen", -loesung,
                        "Zähl die Minuszeichen: eine gerade Anzahl ergibt "
                        "plus, eine ungerade minus."))
    eine = eine_nicht_potenziert(faktoren)
    if eine is not None and eine != loesung and all(
            eine != f.ergebnis.expr for f in fehler):
        fehler.append(F("nur_eine_potenziert", eine,
                        "Jede Variable bekommt ihre eigene Hochzahl — auch "
                        "die zweite."))
    if extra_fehler:
        fehler += list(extra_fehler)

    gesiebt, gesehen = [], set()
    for f in fehler:
        wert_ = f.ergebnis.expr
        if wert_ == loesung or str(wert_) in gesehen:
            continue
        gesehen.add(str(wert_))
        gesiebt.append(f)
    fehler = gesiebt

    return {"frage": produkt_text(faktoren), "loesung_text": zeige(loesung),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=fehler),
            "schritte": schritte(faktoren, loesung), "tipps": TIPPS}


def vorzeichen_setzen(zahlen, wie_viele_negativ):
    """Die ersten `wie_viele_negativ` Zahlen werden negativ."""
    return [-k if i < wie_viele_negativ else k for i, k in enumerate(zahlen)]


STD = [kopfrechenbar, fehler_eindeutig]


# ══════════════════════════════════════════════════════════════════════════
# S18 · Variablen multiplizieren        5.1 – 5.4
# ══════════════════════════════════════════════════════════════════════════
#
# Levelachse: A ohne Minus, B ein Minus, C zwei bis drei.

NEG18 = {"A": 0, "B": 1, "C": 2}
ZAHL18 = {"A": [2, 3, 4, 5], "B": [2, 3, 4, 5, 6], "C": [2, 3, 4, 5]}
EXTRA18 = {"A": 0, "B": 0, "C": 1}      # zusätzliche Faktoren auf Level C


def zahlen18(p, anzahl):
    vorrat = p["zahlen"]
    roh = [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]
    return vorzeichen_setzen(roh, min(p["neg"], anzahl))


def _b18(**extra):
    return {lv: dict({"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                      "zahlen": [ZAHL18[lv]], "neg": [NEG18[lv]],
                      "extra": [EXTRA18[lv]], "dreh": [0, 1, 2]}, **extra)
            for lv in ("A", "B", "C")}


def bf18_1(p):
    k = zahlen18(p, 1)[0]
    return bau([(k, []), (1, [p["var"]])])


BF18_1 = Bauform("BF1", "Zahl mal Variable",
    bereiche=_b18(), bauen=bf18_1, filter=STD)


def bf18_2(p):
    ks = zahlen18(p, 2 + p["extra"])
    return bau([(k, []) for k in ks] + [(1, [p["var"]])])


BF18_2 = Bauform("BF2", "Zwei Zahlen und eine Variable",
    bereiche=_b18(), bauen=bf18_2, filter=STD)


def bf18_3(p):
    ks = zahlen18(p, 2)
    v = p["var"]
    return bau([(ks[0], [v]), (ks[1], [v])])


BF18_3 = Bauform("BF3", "Zwei gleiche Variablen mit Koeffizienten",
    bereiche=_b18(), bauen=bf18_3, filter=STD)


def bf18_4(p):
    ks = zahlen18(p, 2)
    return bau([(ks[0], [p["var"]]), (ks[1], [p["var2"]])])


BF18_4 = Bauform("BF4", "Zwei verschiedene Variablen mit Koeffizienten",
    bereiche=_b18(), bauen=bf18_4,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf18_5(p):
    ks = zahlen18(p, 3)
    return bau([(ks[0], [p["var"]]), (ks[1], [p["var2"]]),
                (ks[2], [p["var3"]])])


BF18_5 = Bauform("BF5", "Drei Faktoren, drei verschiedene Variablen",
    bereiche=_b18(), bauen=bf18_5,
    filter=STD + [symbole_verschieden("var", "var2", "var3")])


def bf18_6(p):
    anzahl = 3 + p["extra"]
    ks = zahlen18(p, anzahl)
    v = p["var"]
    return bau([(k, [v]) for k in ks], extra_fehler=[
        F("zahlen_addiert_potenz", Integer(sum(abs(k) for k in ks)) * v ** anzahl,
          "Die Zahlen werden multipliziert. Nur die Hochzahl entsteht durchs "
          "Zählen."),
    ])


BF18_6 = Bauform("BF6", "Dieselbe Variable dreimal oder öfter",
    bereiche=_b18(zahlen=[[2, 3]]), bauen=bf18_6, filter=STD)


def bf18_7(p):
    ks = zahlen18(p, 2)
    v1, v2 = p["var"], p["var2"]
    return bau([(ks[0], [v1]), (ks[1], [v1, v2])])


BF18_7 = Bauform("BF7", "Variable einzeln und im Produkt",
    bereiche=_b18(), bauen=bf18_7,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf18_8(p):
    ks = zahlen18(p, 3)
    v1, v2 = p["var"], p["var2"]
    return bau([(ks[0], [v1]), (ks[1], [v2]), (ks[2], [v1])])


BF18_8 = Bauform("BF8", "Zwei Variablen, eine davon doppelt",
    bereiche=_b18(), bauen=bf18_8,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf18_9(p):
    """Sonderfall: ein Faktor ist eins."""
    k = zahlen18(p, 1)[0]
    v1, v2 = p["var"], p["var2"]
    if p["neg"] == 0:
        faktoren = [(1, []), (abs(k), [v1])]
    elif p["neg"] == 1:
        faktoren = [(1, [v1]), (1, [v2]), (-1, [])]
    else:
        faktoren = [(-1, []), (abs(k), [v1]), (-1, []), (1, [v2])]
    return bau(faktoren, extra_fehler=[
        F("eins_falsch", produkt_wert(faktoren) * 2,
          "Ein Faktor eins ändert nichts am Ergebnis."),
    ])


BF18_9 = Bauform("BF9", "Sonderfall: ein Faktor ist eins",
    bereiche=_b18(), bauen=bf18_9,
    filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf18_10(p):
    """Sonderfall: ein Faktor ist null.

    Muss der Generator gezielt bauen — bei zufaelligen Zahlen kommt die Null
    fast nie vor, und sie ist der einzige Fall, bei dem alle Variablen
    verschwinden.
    """
    k = abs(zahlen18(p, 1)[0])
    v1, v2 = p["var"], p["var2"]
    if p["neg"] == 0:
        faktoren = [(0, []), (k, [v1])]
    elif p["neg"] == 1:
        faktoren = [(k, [v1]), (0, []), (1, [v2])]
    else:
        faktoren = [(-k, [v1]), (0, []), (1, [v2]), (7, [])]
    return bau(faktoren, extra_fehler=[
        F("null_ignoriert", Integer(k) * v1,
          "Alles mal null ist null — auch die Variablen verschwinden."),
    ])


BF18_10 = Bauform("BF10", "Sonderfall: ein Faktor ist null",
    bereiche=_b18(), bauen=bf18_10,
    filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf18_11(p):
    """Nur Variablen, gar keine Zahl."""
    v1, v2 = p["var"], p["var2"]
    anzahl = 3 + p["extra"]
    folge = [v1, v2, v1, v2, v1][:anzahl + 1]
    return bau([(1, [s]) for s in folge])


BF18_11 = Bauform("BF11", "Nur Variablen, gar keine Zahl",
    bereiche=_b18(), bauen=bf18_11,
    filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


S18 = Schablone(
    nr="S18", titel="Variablen multiplizieren",
    lektionen="5.1 – 5.4", erhebung="Vorstufe zu 2a und 2c",
    anleitung="Fasse zu einem Produkt zusammen.",
    levelachse="Vorzeichen und Anzahl Faktoren",
    bauformen=[BF18_1, BF18_2, BF18_3, BF18_4, BF18_5, BF18_6,
               BF18_7, BF18_8, BF18_9, BF18_10, BF18_11],
    kernidee=("Beim Multiplizieren werden die Zahlen malgenommen und für "
              "jede Variable gezählt, wie oft sie vorkommt. Eine gerade "
              "Anzahl Minuszeichen ergibt plus, eine ungerade minus."),
)


# ══════════════════════════════════════════════════════════════════════════
# S19 · Produkte vereinfachen, mit Vorzeichen      5.5 – 5.8
# ══════════════════════════════════════════════════════════════════════════
#
# Levelachse: A ein Minus, B zwei, C drei bis vier. Und ein Faktor mehr
# pro Stufe.

NEG19 = {"A": 1, "B": 2, "C": 3}
ZAHL19 = {"A": [2, 3, 4], "B": [2, 3, 4, 5], "C": [2, 3, 4, 5]}
EXTRA19 = {"A": 0, "B": 1, "C": 2}


def zahlen19(p, anzahl):
    vorrat = p["zahlen"]
    roh = [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]
    return vorzeichen_setzen(roh, min(p["neg"], anzahl))


def _b19(**extra):
    return {lv: dict({"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                      "zahlen": [ZAHL19[lv]], "neg": [NEG19[lv]],
                      "extra": [EXTRA19[lv]], "dreh": [0, 1, 2]}, **extra)
            for lv in ("A", "B", "C")}


def bf19_1(p):
    ks = zahlen19(p, 2)
    return bau([(ks[0], []), (ks[1], [p["var"]])])


BF19_1 = Bauform("BF1", "Zahl mal Monom",
    bereiche=_b19(), bauen=bf19_1, filter=STD)


def bf19_2(p):
    ks = zahlen19(p, 2)
    return bau([(ks[0], [p["var"]]), (ks[1], [p["var2"]])])


BF19_2 = Bauform("BF2", "Zwei Monome, verschiedene Variablen",
    bereiche=_b19(), bauen=bf19_2,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf19_3(p):
    ks = zahlen19(p, 2)
    v = p["var"]
    return bau([(ks[0], [v]), (ks[1], [v])])


BF19_3 = Bauform("BF3", "Gleiche Variable — eine Potenz entsteht",
    bereiche=_b19(), bauen=bf19_3, filter=STD)


def bf19_4(p):
    ks = zahlen19(p, 2)
    v1, v2 = p["var"], p["var2"]
    return bau([(ks[0], [v1, v2]), (ks[1], [v1, v2])])


BF19_4 = Bauform("BF4", "Zwei Variablen, beide quadriert",
    bereiche=_b19(), bauen=bf19_4,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf19_5(p):
    """Drei bis vier Faktoren, Minus verteilt."""
    anzahl = 3 + p["extra"]
    ks = zahlen19(p, anzahl)
    vorrat = [p["var"], p["var2"], p["var3"]]
    sorten = [vorrat[i % 3] for i in range(anzahl)]
    # Variablen ohne Koeffizient, ausser beim ersten Faktor
    faktoren = [(ks[0], [sorten[0]])]
    for i in range(1, anzahl):
        k = ks[i]
        faktoren.append((-1 if k < 0 else 1, [sorten[i]]))
    return bau(faktoren)


BF19_5 = Bauform("BF5", "Drei bis vier Faktoren, Minus verteilt",
    bereiche=_b19(), bauen=bf19_5,
    filter=STD + [symbole_verschieden("var", "var2", "var3")])


def bf19_6(p):
    """Mehrere Faktoren, hohe Potenzen."""
    anzahl = 2 + p["extra"]
    ks = zahlen19(p, anzahl)
    v1, v2 = p["var"], p["var2"]
    muster = [[v1, v2], [v1, v2], [v1], [v2]][:anzahl]
    return bau([(k, vs) for k, vs in zip(ks, muster)])


BF19_6 = Bauform("BF6", "Mehrere Faktoren, hohe Potenzen",
    bereiche=_b19(zahlen=[[2, 3, 4]]), bauen=bf19_6,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf19_7(p):
    """Variable ohne Koeffizient als Faktor."""
    anzahl = 2 + p["extra"]
    ks = zahlen19(p, anzahl)
    v = p["var"]
    faktoren = [(ks[0], [v]), (abs(ks[1]) if len(ks) > 1 else 4, [v])]
    if anzahl >= 3:
        faktoren.append((-1 if ks[2] < 0 else 1, [v]))
    return bau(faktoren[:max(2, anzahl)])


BF19_7 = Bauform("BF7", "Variable ohne Koeffizient als Faktor",
    bereiche=_b19(), bauen=bf19_7, filter=STD)


def bf19_8(p):
    """Sonderfall: ein Faktor ist eins oder minus eins."""
    ks = zahlen19(p, 2)
    v1, v2 = p["var"], p["var2"]
    if p["neg"] == 1:
        faktoren = [(-1, []), (abs(ks[0]), [v1])]
    elif p["neg"] == 2:
        faktoren = [(-abs(ks[0]), [v1, v2]), (-abs(ks[1]), [v1, v2]),
                    (1, [])]
    else:
        faktoren = [(-abs(ks[0]), [v1, v2]), (-abs(ks[1]), [v1, v2]),
                    (-1, [])]
    return bau(faktoren)


BF19_8 = Bauform("BF8", "Sonderfall: ein Faktor ist eins oder minus eins",
    bereiche=_b19(), bauen=bf19_8,
    filter=[fehler_eindeutig, kopfrechenbar,
            symbole_verschieden("var", "var2")])


def bf19_9(p):
    """Sonderfall: ein Faktor ist null."""
    k = abs(zahlen19(p, 1)[0])
    v1, v2 = p["var"], p["var2"]
    if p["neg"] == 1:
        faktoren = [(-k, [v1]), (0, [])]
    elif p["neg"] == 2:
        faktoren = [(-k, [v1]), (0, []), (-3, [v2])]
    else:
        faktoren = [(-k, [v1]), (0, []), (-3, [v2]), (-2, [])]
    return bau(faktoren, extra_fehler=[
        F("null_ignoriert", Integer(k) * v1,
          "Alles mal null ist null — auch die Variablen verschwinden."),
    ])


BF19_9 = Bauform("BF9", "Sonderfall: ein Faktor ist null",
    bereiche=_b19(), bauen=bf19_9,
    filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf19_10(p):
    """Nur Variablen, dann eine Zahl."""
    anzahl = 3 + p["extra"]
    ks = zahlen19(p, anzahl)
    v1, v2 = p["var"], p["var2"]
    faktoren = [(1, [v1]), (1, [v2]), (-abs(ks[0]), [v1])]
    if anzahl >= 4:
        faktoren.append((abs(ks[1]), [v2]))
    if anzahl >= 5:
        faktoren.append((-abs(ks[2]), []))
    return bau(faktoren)


BF19_10 = Bauform("BF10", "Nur Variablen, dann eine Zahl",
    bereiche=_b19(), bauen=bf19_10,
    filter=STD + [symbole_verschieden("var", "var2")])


def bf19_11(p):
    """Anzahl Minuszeichen wächst — die Levelachse als eigene Bauform.

    Bei zwei Minuszeichen wird das Ergebnis positiv, bei drei negativ, bei
    vier wieder positiv. Wer das nicht zaehlt, sondern raet, liegt bei jeder
    zweiten Aufgabe falsch.
    """
    anzahl = 2 + p["extra"]
    ks = zahlen19(p, anzahl)
    vorrat = [p["var"], p["var2"], p["var3"]]
    sorten = [vorrat[i % 3] for i in range(anzahl)]
    faktoren = [(-abs(k) if i < p["neg"] else abs(k), [s])
                for i, (k, s) in enumerate(zip(ks, sorten))]
    return bau(faktoren)


BF19_11 = Bauform("BF11", "Anzahl Minuszeichen wächst",
    bereiche=_b19(), bauen=bf19_11,
    filter=STD + [symbole_verschieden("var", "var2", "var3")])


def bf19_12(p):
    """Derselbe Faktor mehrfach."""
    anzahl = 2 + p["extra"]
    k = abs(zahlen19(p, 1)[0])
    v = p["var"]
    faktoren = [(k, [v])] * anzahl
    return bau(faktoren, extra_fehler=[
        F("zahlen_addiert_potenz", Integer(k * anzahl) * v ** anzahl,
          f"Die Zahlen werden multipliziert: {' · '.join([str(k)] * anzahl)}. "
          f"Nur die Hochzahl entsteht durchs Zählen."),
    ])


BF19_12 = Bauform("BF12", "Derselbe Faktor mehrfach",
    bereiche=_b19(zahlen=[[2, 3, 4]]), bauen=bf19_12, filter=STD)


S19 = Schablone(
    nr="S19", titel="Produkte vereinfachen, mit Vorzeichen",
    lektionen="5.5 – 5.8", erhebung="2b",
    anleitung="Fasse zu einem Produkt zusammen.",
    levelachse="Vorzeichen und Anzahl Faktoren",
    bauformen=[BF19_1, BF19_2, BF19_3, BF19_4, BF19_5, BF19_6,
               BF19_7, BF19_8, BF19_9, BF19_10, BF19_11, BF19_12],
    kernidee=("Eine gerade Anzahl Minuszeichen ergibt plus, eine ungerade "
              "minus. Die Zahlen werden multipliziert, und jede Variable "
              "bekommt als Hochzahl, wie oft sie vorkommt."),
)
