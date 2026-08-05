# -*- coding: utf-8 -*-
"""
Kapitel 3 · Variablen und Terme      (Lektionen 3.1 – 3.11)

    S12  Zahlen in Terme einsetzen        3.1 – 3.3
    S13  Variablen addieren, subtrahieren, multiplizieren    3.4 – 3.9
    S14  Terme mit Zahlen und einer Variablen vereinfachen   3.10 – 3.11

Das Fundament fuer alles Weitere: 4.1 setzt 3.11 voraus, und ueber 3.1 haengt
das ganze Kapitel an 1.19.

LEVELACHSEN, woertlich aus Teil 2 der drei Schablonen:

    S12  Anzahl Variablen  eine → zwei → drei
         Vorzeichen der Werte  positiv → auch negativ → in mehreren Feldern
    S13  Anzahl Glieder  zwei → drei bis vier → fuenf bis sieben
    S14  Anzahl Glieder  zwei bis drei → vier → fuenf und mehr
         Vorzeichen  alles positiv → ein Minus → mehrere Minus

Was hier NICHT vorkommt, und zwar mit Absicht: Potenzen als Bestandteil der
Aufgabe (kommen erst ab 7.2), Brueche (K2 liegt nicht in der Kette) und bei
S13 Koeffizienten (3a gibt es erst ab 3.10). In S13 entsteht die Potenz nur
als ERGEBNIS, wenn a · a zu a² wird — das ist Lektion 3.6.
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS, zeige, zeige_summe
from .qualitaet import (fehler_eindeutig, kopfrechenbar, loesung_nicht_null,
                        symbole_verschieden)
from .s16_gleichartig import beide_sorten_bleiben, wert, zeige_glieder
from .schablone import Bauform, Schablone

a, b, c, d, e, m, n, u, v, w, x, y, z = symbole("a b c d e m n u v w x y z")
VARS = {"a", "b", "c", "d", "e", "m", "n", "u", "v", "w", "x", "y", "z"}

SORTE1 = [a, x, u, m, b]
SORTE2 = [b, y, v, n, c]
SORTE3 = [c, z, w, d, e]


def F(s, err, t):
    return Fehler(s, Loesung.zahl(err), t)


def siebe(fehler, loesung):
    """Was gleich der Loesung ist oder doppelt vorkommt, faellt weg.

    Der Fehlerkatalog darf nicht mehrdeutig sein: zwei Eintraege mit
    demselben Wert koennten nicht unterschieden werden, und ein Eintrag, der
    die Loesung trifft, wuerde eine richtige Antwort als Fehler melden.
    """
    raus, gesehen = [], set()
    for f in fehler:
        w = f.ergebnis.expr
        if w is None or w == loesung or str(w) in gesehen:
            continue
        gesehen.add(str(w))
        raus.append(f)
    return raus


def bau(frage, loesung, fehler, schritte, tipps, loesung_text=None,
        zielform=Zielform.BELIEBIG, sorten=None):
    fehler = siebe(fehler, loesung)
    return {"frage": frage, "loesung_text": loesung_text or zeige(loesung),
            "sorten": sorten or [],
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=zielform, fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


# ══════════════════════════════════════════════════════════════════════════
# S12 · Zahlen in Terme einsetzen        Lektionen 3.1 – 3.3
# ══════════════════════════════════════════════════════════════════════════

TIPPS12 = [
    "Setze jeden Wert in einer eigenen Klammer ein, dann kann kein Vorzeichen "
    "verlorengehen.",
    "Schreib die Werte zuerst auf und rechne erst danach.",
    "Rechne aus, was in der innersten Klammer steht, bevor du weitergehst.",
]


def wertliste(paare) -> str:
    """«für a = −5, b = 3»"""
    return ", ".join(f"{zeige(sym)} = {zeige(Integer(w))}" for sym, w in paare)


def frage12(term: str, paare) -> str:
    return f"{term}   für {wertliste(paare)}"


def schritte12(paare, term, loesung):
    return [("Werte notieren", wertliste(paare)),
            ("Jeden Wert in einer Klammer einsetzen",
             "so bleibt jedes Vorzeichen erhalten"),
            ("Ausrechnen", f"{term} = {zeige(loesung)}")]


#: Die Levelachse von S12: wie viele Variablen, und wie viele davon negativ.
#: Level A hat eine Variable und einen positiven Wert, C hat drei Variablen
#: und mehrere negative Werte.
WERTE = {
    "A": {"anzahl": 1, "werte": [4, 5, 7, 11], "neg": 0},
    "B": {"anzahl": 2, "werte": [3, 4, 6, 8, 9], "neg": 1},
    "C": {"anzahl": 3, "werte": [2, 3, 4, 5, 6, 7], "neg": 2},
}


def zieh_werte(p):
    """Werte gemaess Level: Anzahl und wie viele davon negativ."""
    stufe = WERTE[p["lvl"]]
    vorrat = stufe["werte"]
    roh = [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(stufe["anzahl"])]
    return [-w if i < stufe["neg"] else w for i, w in enumerate(roh)]


def syms(p, anzahl):
    return [p["var"], p["var2"], p["var3"]][:anzahl]


def fehler12_allgemein(paare, formel, loesung):
    """Die drei Fehler aus Teil 5, die in jeder S12-Bauform vorkommen.

    Sie werden aus derselben Formel berechnet wie die Loesung, nur mit
    verfaelschten Werten. Dadurch stimmen sie fuer jede Bauform, statt fuer
    jede einzeln von Hand geschrieben werden zu muessen.
    """
    werte = [w for _, w in paare]
    raus = []

    # «Vorzeichen des Wertes weggelassen» — alle Werte positiv gerechnet
    if any(w < 0 for w in werte):
        ohne = formel([abs(w) for w in werte])
        raus.append(F("vorzeichen_weggelassen", Integer(ohne),
                      "Ein Wert ist negativ. Das Vorzeichen gehört zum Wert "
                      "und muss mit eingesetzt werden."))

    # «Negativen Wert ohne Klammer eingesetzt» — beim letzten negativen Wert
    # kippt das Vorzeichen, weil das Doppelminus verlorengeht
    for i in range(len(werte) - 1, -1, -1):
        if werte[i] < 0:
            gekippt = list(werte)
            gekippt[i] = -gekippt[i]
            raus.append(F("ohne_klammer", Integer(formel(gekippt)),
                          "Ohne Klammer geht bei einem negativen Wert das "
                          "Doppelminus verloren. Setz jeden Wert in einer "
                          "eigenen Klammer ein."))
            break

    # «Werte vertauscht» — nur sinnvoll bei mindestens zwei Variablen
    if len(werte) >= 2 and werte[0] != werte[1]:
        getauscht = list(werte)
        getauscht[0], getauscht[1] = getauscht[1], getauscht[0]
        raus.append(F("werte_vertauscht", Integer(formel(getauscht)),
                      "Die Werte sind vertauscht. Schreib zuerst auf, welcher "
                      "Buchstabe welche Zahl ist."))
    return raus


def s12_bau(p, formel, anzeige, fehlerbau, schrittname, benutzt=None):
    """Gemeinsames Geruest aller S12-Bauformen.

    `benutzt` sagt, wie viele der Variablen im Term wirklich vorkommen.
    Ohne das stand in der Werteliste eine Variable, die es im Term gar nicht
    gab — beim Testlauf aufgetreten: «2m − m · y   für m = −2, y = −3, c = 4».
    """
    stufe = WERTE[p["lvl"]]
    vs = syms(p, stufe["anzahl"])
    ws = zieh_werte(p)
    if benutzt is not None:
        vs, ws = vs[:benutzt(stufe["anzahl"])], ws[:benutzt(stufe["anzahl"])]
    paare = list(zip(vs, ws))
    loesung = Integer(formel(ws))
    term = anzeige(vs)
    fehler = list(fehlerbau(ws, loesung)) + fehler12_allgemein(paare, formel,
                                                              loesung)
    # Doppelte und solche, die die Loesung treffen, aussortieren
    gesiebt, gesehen = [], set()
    for f in fehler:
        w = f.ergebnis.expr
        if w == loesung or str(w) in gesehen:
            continue
        gesehen.add(str(w))
        gesiebt.append(f)
    return bau(frage12(term, paare), loesung, gesiebt,
               schritte12(paare, term, loesung), TIPPS12)


def _bereiche12(**extra):
    return {lv: dict({"lvl": [lv], "var": SORTE1, "var2": SORTE2,
                      "var3": SORTE3, "dreh": [0, 1, 2]}, **extra)
            for lv in ("A", "B", "C")}


FILTER12 = [kopfrechenbar, fehler_eindeutig,
            symbole_verschieden("var", "var2", "var3")]


def bf12_1(p):
    zusatz = p["zusatz"]
    return s12_bau(p,
        lambda w: sum(w) + (zusatz if len(w) == 1 else 0),
        lambda vs: (zeige_summe(*vs) if len(vs) > 1
                    else f"{zeige(vs[0])} + {zusatz}"),
        lambda w, l: [
            F("vorzeichen_verloren", l + 2 * abs(min(w)) if min(w) < 0 else l + 2,
              "Ein Wert ist negativ — das Vorzeichen gehört mit in die Klammer."),
        ], "Summe")


BF12_1 = Bauform("BF1", "Summe",
    bereiche=_bereiche12(zusatz=[4, 7, 9]), bauen=bf12_1, filter=FILTER12 + [loesung_nicht_null])


def bf12_2(p):
    zusatz = p["zusatz"]

    def formel(w):
        if len(w) == 1:
            return w[0] - zusatz
        r = w[0]
        for t in w[1:]:
            r -= t
        return r

    def anzeige(vs):
        if len(vs) == 1:
            return f"{zeige(vs[0])} {MINUS} {zusatz}"
        return f" {MINUS} ".join(zeige(s) for s in vs)

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("doppelminus_verloren", l - 2 * abs(w[-1]) if w[-1] < 0 else l - 2,
              "Ohne Klammer geht bei einem negativen Wert das Doppelminus "
              "verloren."),
        ], "Differenz")


BF12_2 = Bauform("BF2", "Differenz",
    bereiche=_bereiche12(zusatz=[4, 6, 8]), bauen=bf12_2, filter=FILTER12 + [loesung_nicht_null])


def bf12_3(p):
    faktor = p["faktor"]

    def formel(w):
        r = faktor if len(w) == 1 else 1
        for t in w:
            r *= t
        return r

    def anzeige(vs):
        if len(vs) == 1:
            return f"{faktor}{zeige(vs[0])}"
        return " · ".join(zeige(s) for s in vs)

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("vorzeichen_produkt", -l,
              "Zähl die Minuszeichen: eine gerade Anzahl ergibt plus, eine "
              "ungerade minus."),
        ], "Produkt")


BF12_3 = Bauform("BF3", "Produkt",
    bereiche=_bereiche12(faktor=[3, 5, 6]), bauen=bf12_3, filter=FILTER12 + [loesung_nicht_null])


def bf12_5(p):
    k1, k2, k3 = p["k1"], p["k2"], p["k3"]

    def formel(w):
        if len(w) == 1:
            return k1 * w[0] + k2
        ks = [k1, k2, k3][:len(w)]
        vorz = [1, 1, -1][:len(w)]
        return sum(k * v * s for k, v, s in zip(ks, w, vorz))

    def anzeige(vs):
        ks = [k1, k2, k3][:len(vs)]
        if len(vs) == 1:
            return f"{ks[0]}{zeige(vs[0])} + {k2}"
        teile = [f"{ks[0]}{zeige(vs[0])}"]
        if len(vs) > 1:
            teile.append(f"+ {ks[1]}{zeige(vs[1])}")
        if len(vs) > 2:
            teile.append(f"{MINUS} {ks[2]}{zeige(vs[2])}")
        return " ".join(teile)

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("vorzeichen_weggelassen", l + 2 * k1 * abs(w[0]) if w[0] < 0 else l + 2 * k1,
              "Der Wert ist negativ — das Vorzeichen gehört zum Produkt dazu."),
        ], "Punkt vor Strich")


BF12_5 = Bauform("BF5", "Punkt vor Strich",
    bereiche=_bereiche12(k1=[3, 5], k2=[2, 3], k3=[2, 4]),
    bauen=bf12_5, filter=FILTER12 + [loesung_nicht_null])


def bf12_7(p):
    zusatz = p["zusatz"]

    def formel(w):
        if len(w) == 1:
            return -w[0] + zusatz
        r = -w[0]
        for i, t in enumerate(w[1:]):
            r += -t if i == 0 else t
        return r

    def anzeige(vs):
        if len(vs) == 1:
            return f"{MINUS}{zeige(vs[0])} + {zusatz}"
        teile = [f"{MINUS}{zeige(vs[0])}", f"{MINUS} {zeige(vs[1])}"]
        if len(vs) > 2:
            teile.append(f"+ {zeige(vs[2])}")
        return " ".join(teile)

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("als_klammer_gelesen", -(w[0] - (w[1] if len(w) > 1 else 0)),
              f"{MINUS}a {MINUS} b heisst nicht {MINUS}(a {MINUS} b). Jedes "
              f"Glied bekommt sein eigenes Vorzeichen."),
        ], "Minus vor der Variablen")


BF12_7 = Bauform("BF7", "Minuszeichen direkt vor der Variablen",
    bereiche=_bereiche12(zusatz=[8, 10, 12]), bauen=bf12_7, filter=FILTER12 + [loesung_nicht_null])


def bf12_8(p):
    k = p["k"]

    def formel(w):
        return w[0] - k * w[0] if len(w) == 1 else 2 * w[0] - w[0] * w[1]

    def anzeige(vs):
        if len(vs) == 1:
            return f"{zeige(vs[0])} {MINUS} {k}{zeige(vs[0])}"
        return f"2{zeige(vs[0])} {MINUS} {zeige(vs[0])} · {zeige(vs[1])}"

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("zweites_uebersehen", w[0] - k if len(w) == 1 else 2 * w[0] - w[1],
              "Auch im zweiten Glied steckt dieselbe Variable — dort muss "
              "derselbe Wert eingesetzt werden."),
        ], "Dieselbe Variable mehrfach", benutzt=lambda n: min(n, 2))


BF12_8 = Bauform("BF8", "Dieselbe Variable kommt mehrfach vor",
    bereiche=_bereiche12(k=[3, 4]), bauen=bf12_8,
    filter=FILTER12 + [loesung_nicht_null])


def bf12_9(p):
    kopf = p["kopf"]

    def formel(w):
        if len(w) == 1:
            return kopf - (w[0] + 3)
        if len(w) == 2:
            return kopf - (w[0] + w[1])
        return w[0] - (w[1] - w[2] + 2)

    def anzeige(vs):
        if len(vs) == 1:
            return f"{kopf} {MINUS} ({zeige(vs[0])} + 3)"
        if len(vs) == 2:
            return f"{kopf} {MINUS} ({zeige(vs[0])} + {zeige(vs[1])})"
        return (f"{zeige(vs[0])} {MINUS} ({zeige(vs[1])} {MINUS} "
                f"{zeige(vs[2])} + 2)")

    return s12_bau(p, formel, anzeige,
        lambda w, l: [
            F("nur_erstes_glied",
              kopf - w[0] + 3 if len(w) == 1
              else (kopf - w[0] + w[1] if len(w) == 2 else w[0] - w[1] - w[2] - 2),
              "Das Minus gilt für die ganze Klammer, nicht nur für das erste "
              "Glied darin."),
        ], "Minus vor der Klammer")


BF12_9 = Bauform("BF9", "Minus vor der Klammer",
    bereiche=_bereiche12(kopf=[20, 24, 30]), bauen=bf12_9, filter=FILTER12 + [loesung_nicht_null])


def bf12_10(p):
    """Sonderfall: eingesetzt wird eine Null."""
    k, zusatz = p["k"], p["zusatz"]
    stufe = WERTE[p["lvl"]]
    vs = syms(p, stufe["anzahl"])
    if len(vs) == 1:
        paare = [(vs[0], 0)]
        term = f"{k}{zeige(vs[0])} + {zusatz}"
        loesung = Integer(zusatz)
        falsch = Integer(k + zusatz)
    else:
        andere = zieh_werte(p)[1]
        paare = [(vs[0], 0), (vs[1], andere)]
        term = f"{zeige(vs[0])} · {zeige(vs[1])} + {zeige(vs[0])}"
        loesung = Integer(0)
        falsch = Integer(andere)
    return bau(frage12(term, paare), loesung, [
        F("null_ignoriert", falsch,
          "Null mal irgendetwas ist null — die Null muss überall eingesetzt "
          "werden, wo die Variable steht."),
    ], schritte12(paare, term, loesung), TIPPS12)


BF12_10 = Bauform("BF10", "Sonderfall: eingesetzt wird eine Null",
    bereiche=_bereiche12(k=[5, 6], zusatz=[7, 9]),
    bauen=bf12_10, filter=[fehler_eindeutig,
                           symbole_verschieden("var", "var2", "var3")])


def bf12_11(p):
    """Sonderfall: das Ergebnis wird null."""
    stufe = WERTE[p["lvl"]]
    vs = syms(p, stufe["anzahl"])
    w = zieh_werte(p)
    if len(vs) == 1:
        paare = [(vs[0], w[0])]
        term = f"{zeige(vs[0])} {MINUS} {abs(w[0])}"
        paare = [(vs[0], abs(w[0]))]
    elif len(vs) == 2:
        paare = [(vs[0], -abs(w[0])), (vs[1], abs(w[0]))]
        term = zeige_summe(vs[0], vs[1])
    else:
        paare = [(vs[0], w[0]), (vs[1], abs(w[1])),
                 (vs[2], w[0] * abs(w[1]))]
        term = f"{zeige(vs[0])} · {zeige(vs[1])} {MINUS} {zeige(vs[2])}"
    return bau(frage12(term, paare), Integer(0), [
        F("nicht_null", Integer(sum(abs(v) for _, v in paare)),
          "Die Vorzeichen zählen mit — hier heben sich die Werte auf."),
    ], schritte12(paare, term, Integer(0)), TIPPS12)


BF12_11 = Bauform("BF11", "Sonderfall: das Ergebnis wird null",
    bereiche=_bereiche12(), bauen=bf12_11,
    filter=[fehler_eindeutig, symbole_verschieden("var", "var2", "var3")])


S12 = Schablone(
    nr="S12", titel="Zahlen in Terme einsetzen",
    lektionen="3.1 – 3.3", erhebung="Vorstufe",
    anleitung="Rechne aus.",
    levelachse="Anzahl Variablen und Vorzeichen der Werte",
    bauformen=[BF12_1, BF12_2, BF12_3, BF12_5, BF12_7,
               BF12_8, BF12_9, BF12_10, BF12_11],
    kernidee=("Eine Variable ist ein Platzhalter für eine Zahl. Setze den "
              "Wert immer in einer Klammer ein, dann bleiben die Vorzeichen "
              "erhalten."),
)


# ══════════════════════════════════════════════════════════════════════════
# S13 · Variablen addieren, subtrahieren, multiplizieren   3.4 – 3.9
# ══════════════════════════════════════════════════════════════════════════
#
# Hier gibt es noch KEINE Koeffizienten: 3a kommt erst in 3.10. Die Aufgaben
# bestehen aus blossen Variablen, und die Zahl entsteht erst im Ergebnis.

def kandidaten13(glieder, alle_vars, loesung):
    """Die fuenf Fehler aus Teil 5 von S13, soweit sie hier passen.

    - Addieren mit Multiplizieren verwechselt   a + a  ->  a²
    - Multiplizieren mit Addieren verwechselt   a · a  ->  2a
    - Verschiedene Variablen zusammengezogen    a + b  ->  ab
    - Alles zusammengezaehlt ohne zu sortieren  a+a+a+b+b  ->  5ab
    - Minuszeichen am Anfang uebersehen
    """
    anzahl = len(glieder)
    summe = sum(k for k, _, _ in glieder)
    produkt = Integer(1)
    for s in alle_vars:
        produkt *= s

    raus = []
    if len(alle_vars) > 1:
        raus.append(F("sorten_zusammengezogen", Integer(summe) * produkt,
            " und ".join(zeige(s) for s in alle_vars)
            + " sind verschieden und lassen sich nicht zusammenzählen."))
        raus.append(F("alles_ohne_sortieren", Integer(anzahl) * produkt,
            "Jede Sorte wird für sich gezählt, nicht alles zusammen."))
    raus.append(F("minus_uebersehen", Integer(anzahl) * alle_vars[0],
        "Die Minuszeichen zählen mit: abgezogene Glieder werden weggezählt."))
    raus.append(F("mal_statt_plus",
        alle_vars[0] ** anzahl if len(alle_vars) == 1 else produkt,
        "Beim Addieren wird gezählt, beim Multiplizieren entsteht eine "
        "Potenz. Schau auf das Rechenzeichen."))
    return raus


TIPPS13 = [
    "Beim Addieren wird gezählt: a + a sind zwei Stück a, also 2a.",
    "Beim Multiplizieren entsteht eine Potenz: a · a ist a².",
    "Sortiere zuerst nach Variablen und zähle dann jede Sorte für sich.",
]

#: Levelachse von S13: nur die Gliederzahl. Zwei, drei bis vier, fuenf bis
#: sieben — so steht es in Teil 2.
ANZAHL13 = {"A": [2], "B": [3, 4], "C": [5, 6, 7]}


def fehler13(glieder, loesung, vs):
    """Teil 5 von S13, so weit die Werte fuer die jeweilige Aufgabe passen."""
    raus = []
    anzahl = len(glieder)
    einzeln = [v for v in vs]

    # «Verschiedene Variablen zusammengezogen»: a + b -> ab
    if len(einzeln) >= 2:
        produkt = Integer(sum(abs(k) for k, _, _ in glieder))
        for v in einzeln:
            produkt *= v
        raus.append(F("variablen_multipliziert", produkt,
                      f"{zeige(einzeln[0])} und {zeige(einzeln[1])} sind "
                      f"verschieden und lassen sich nicht zusammenzählen."))

    # «Alles zusammengezählt, ohne zu sortieren»
    if len(einzeln) >= 2:
        alles = Integer(sum(k for k, _, _ in glieder))
        for v in einzeln:
            alles *= v
        raus.append(F("nicht_sortiert", alles,
                      "Jede Variable wird für sich gezählt, nicht alles "
                      "zusammen."))

    # «Minuszeichen übersehen»
    if any(k < 0 for k, _, _ in glieder):
        raus.append(F("minus_uebersehen",
                      sum(abs(k) * bs for k, bs, _ in glieder),
                      "Die Minuszeichen zählen mit: abgezogene Glieder werden "
                      "weggezählt, nicht dazu."))
    return raus


def s13_summe(vs_folge, minus_ab=None):
    """Glieder aus einer Variablenfolge; ab `minus_ab` werden sie abgezogen."""
    glieder = []
    for i, v in enumerate(vs_folge):
        k = -1 if (minus_ab is not None and i >= minus_ab) else 1
        glieder.append((k, v, "+" if k > 0 else "-"))
    return glieder


def bf13_1(p):
    v, anz = p["var"], p["anzahl"]
    glieder = s13_summe([v] * anz)
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("hochzahl_statt_zahl", v ** anz,
          f"Beim Addieren wird gezählt: {anz} Stück {zeige(v)} ergeben "
          f"{anz}{zeige(v)}. {zeige(v)}{'²' if anz == 2 else ''} entsteht nur "
          f"beim Multiplizieren."),
    ], [("Gleiche Variablen zählen", f"{anz} Stück {zeige(v)}"),
        ("Ergebnis", zeige(l))], TIPPS13)


BF13_1 = Bauform("BF1", "Gleiche Variable addieren",
    bereiche={lv: {"var": SORTE1, "anzahl": ANZAHL13[lv]}
              for lv in ("A", "B", "C")},
    bauen=bf13_1, filter=[kopfrechenbar, fehler_eindeutig])


def bf13_2(p):
    v, anz, minus = p["var"], p["anzahl"], p["minus"]
    glieder = s13_summe([v] * anz, minus_ab=anz - minus)
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("minus_uebersehen", Integer(anz) * v,
          "Die Minuszeichen zählen mit: abgezogene Glieder werden "
          "weggezählt, nicht dazu."),
    ] + kandidaten13(glieder, [v], l), [("Plus-Glieder zählen", f"{anz - minus} Stück"),
        ("Minus-Glieder abziehen", f"{minus} Stück"),
        ("Ergebnis", zeige(l))], TIPPS13)


BF13_2 = Bauform("BF2", "Gleiche Variable addieren und subtrahieren",
    bereiche={"A": {"var": SORTE1, "anzahl": [3], "minus": [1]},
              "B": {"var": SORTE1, "anzahl": [4], "minus": [1]},
              "C": {"var": SORTE1, "anzahl": [6, 7], "minus": [2]}},
    bauen=bf13_2, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf13_3(p):
    v, anz = p["var"], p["anzahl"]
    l = v ** anz
    return bau(" · ".join([zeige(v)] * anz), l, [
        F("addiert", Integer(anz) * v,
          f"Beim Multiplizieren entsteht eine Potenz: {zeige(v)} · {zeige(v)} "
          f"ist {zeige(v)}². {anz}{zeige(v)} wäre die Summe."),
        F("faktoren_gezaehlt", Integer(anz) * v ** 2,
          "Die Anzahl gleicher Faktoren wird zur Hochzahl, nicht zum "
          "Vorfaktor."),
        F("nur_zwei", v ** 2,
          f"Es sind {anz} Faktoren, nicht zwei."),
    ], [("Gleiche Faktoren zählen", f"{anz} Stück {zeige(v)}"),
        ("Als Potenz schreiben", zeige(l))], TIPPS13)


BF13_3 = Bauform("BF3", "Gleiche Variable multiplizieren",
    bereiche={lv: {"var": SORTE1, "anzahl": [k for k in ANZAHL13[lv] if k <= 7]}
              for lv in ("A", "B", "C")},
    bauen=bf13_3, filter=[fehler_eindeutig])


def bf13_4(p):
    v1, v2, anz = p["var"], p["var2"], p["anzahl"]
    erste = (anz + 1) // 2
    folge = [v1] * erste + [v2] * (anz - erste)
    glieder = s13_summe(folge)
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("alles_zusammen", Integer(anz) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} werden getrennt gezählt."),
        F("nicht_sortiert", Integer(anz) * v1,
          "Beide Sorten bleiben stehen — es fällt keine weg."),
    ], [("Sorten trennen", f"{zeige(v1)} und {zeige(v2)}"),
        ("Jede Sorte zählen", zeige(l))], TIPPS13,
        loesung_text=zeige_summe(erste * v1, (anz - erste) * v2))


BF13_4 = Bauform("BF4", "Verschiedene Variablen addieren",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "anzahl": [k for k in ANZAHL13[lv] if k >= 2]}
              for lv in ("A", "B", "C")},
    bauen=bf13_4, filter=[kopfrechenbar, fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf13_6(p):
    v1, v2, anz = p["var"], p["var2"], p["anzahl"]
    erste = (anz + 1) // 2
    folge = [v1] * erste + [v2] * (anz - erste)
    l = v1 ** erste * v2 ** (anz - erste)
    text = (f"{zeige(v1)}{'' if erste == 1 else HOCH.get(erste, '^%d' % erste)}"
            f"{zeige(v2)}{'' if anz - erste == 1 else HOCH.get(anz - erste, '^%d' % (anz - erste))}")
    return bau(" · ".join(zeige(f) for f in folge), l, [
        F("addiert", Integer(anz) * v1,
          "Beim Multiplizieren entstehen Potenzen, keine Vielfachen."),
        F("alles_eine_potenz", (v1 * v2) ** (anz // 2 or 1),
          "Jede Variable bekommt ihre eigene Hochzahl."),
        F("nur_gezaehlt", Integer(anz) * v1 * v2,
          "Beim Multiplizieren wird nicht gezählt."),
    ], [("Gleiche Faktoren zählen",
         f"{erste} Stück {zeige(v1)}, {anz - erste} Stück {zeige(v2)}"),
        ("Als Potenzen schreiben", text)], TIPPS13, loesung_text=text)


BF13_6 = Bauform("BF6", "Verschiedene Variablen multiplizieren",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "anzahl": ANZAHL13[lv]}
              for lv in ("A", "B", "C")},
    bauen=bf13_6, filter=[fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf13_8(p):
    """Sonderfall: eine Sorte hebt sich auf."""
    v1, v2, anz = p["var"], p["var2"], p["anzahl"]
    paare = anz // 2
    folge = [v1] * paare + [v2] + [v1] * paare
    glieder = ([(1, v1, "+")] * paare + [(1, v2, "+")]
               + [(-1, v1, "-")] * paare)
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("nicht_aufgehoben", Integer(2 * paare) * v1 + v2,
          f"Die {zeige(v1)}-Glieder heben sich auf. Übrig bleibt nur "
          f"{zeige(v2)}."),
    ] + kandidaten13(glieder, [v1, v2], l), [("Sorten trennen", f"{zeige(v1)} und {zeige(v2)}"),
        (f"{zeige(v1)} zusammenzählen", "ergibt null"),
        ("Ergebnis", zeige(l))], TIPPS13)


BF13_8 = Bauform("BF8", "Sonderfall: eine Sorte hebt sich auf",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [3]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [5]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [7]}},
    bauen=bf13_8, filter=[fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf13_9(p):
    """Sonderfall: das Ergebnis ist null."""
    v1, v2, anz = p["var"], p["var2"], p["anzahl"]
    if anz == 2:
        glieder = [(1, v1, "+"), (-1, v1, "-")]
    elif anz == 4:
        glieder = [(1, v1, "+"), (1, v1, "+"), (-1, v1, "-"), (-1, v1, "-")]
    else:
        glieder = [(1, v1, "+"), (1, v2, "+"), (-1, v1, "-"), (-1, v2, "-")]
    return bau(zeige_glieder(glieder), Integer(0), [
        F("nicht_null", Integer(len(glieder)) * v1,
          "Die Minuszeichen zählen mit — hier hebt sich alles auf."),
        F("sorten_zusammengezogen", Integer(len(glieder)) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschiedene Sorten."),
    ], [("Sortieren", "gleiche Variablen zusammen"),
        ("Zusammenzählen", "alles ergibt null")], TIPPS13)


BF13_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [2]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [4]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [4, 5]}},
    bauen=bf13_9, filter=[fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf13_10(p):
    """Minuszeichen am Anfang."""
    v, plus, minus = p["var"], p["plus"], p["minus"]
    glieder = [(-1, v, "-")] * minus + [(1, v, "+")] * plus
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("minus_uebersehen", Integer(plus + minus) * v,
          f"{minus} Minus und {plus} Plus — die Minuszeichen werden "
          f"abgezogen."),
    ] + kandidaten13(glieder, [v], l), [("Minus-Glieder zählen", f"{minus} Stück"),
        ("Plus-Glieder zählen", f"{plus} Stück"),
        ("Ergebnis", zeige(l))], TIPPS13)


BF13_10 = Bauform("BF10", "Minuszeichen am Anfang",
    bereiche={"A": {"var": SORTE1, "plus": [2], "minus": [1]},
              "B": {"var": SORTE1, "plus": [3], "minus": [2]},
              "C": {"var": SORTE1, "plus": [2, 4], "minus": [3]}},
    bauen=bf13_10, filter=[kopfrechenbar, fehler_eindeutig,
                           loesung_nicht_null])


def bf13_11(p):
    """Produkt und Summe im selben Term."""
    v1, v2, art = p["var"], p["var2"], p["art"]
    if art == 1:
        frage = f"{zeige(v1)} · {zeige(v1)} + {zeige(v1)}"
        l = v1 ** 2 + v1
        schritte = [("Produkt zuerst", f"{zeige(v1)} · {zeige(v1)} = {zeige(v1)}²"),
                    ("Rest anhängen", zeige(l))]
    elif art == 2:
        frage = f"{zeige(v1)} · {zeige(v2)} + {zeige(v1)} · {zeige(v2)}"
        l = 2 * v1 * v2
        schritte = [("Beide Produkte sind gleich", zeige(v1 * v2)),
                    ("Zwei Stück davon", zeige(l))]
    else:
        frage = (f"{zeige(v1)} · {zeige(v1)} + {zeige(v1)} · {zeige(v2)} + "
                 f"{zeige(v1)} · {zeige(v1)}")
        l = 2 * v1 ** 2 + v1 * v2
        schritte = [("Produkte ausrechnen",
                     f"{zeige(v1)}², {zeige(v1*v2)}, {zeige(v1)}²"),
                    ("Gleichartige zählen", zeige_summe(2 * v1 ** 2, v1 * v2))]
    return bau(frage, l, [
        F("alles_addiert", 2 * v1 + v2 if art != 1 else 2 * v1,
          "Ein Produkt wird nicht gezählt, sondern zu einer Potenz "
          "zusammengefasst."),
    ], schritte, TIPPS13, zielform=Zielform.ZUSAMMENGEFASST,
        loesung_text=(zeige_summe(2 * v1 ** 2, v1 * v2) if art == 3
                      else zeige(l)))


BF13_11 = Bauform("BF11", "Produkt und Summe im selben Term",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "art": [1]},
              "B": {"var": SORTE1, "var2": SORTE2, "art": [2]},
              "C": {"var": SORTE1, "var2": SORTE2, "art": [3]}},
    bauen=bf13_11, filter=[fehler_eindeutig,
                           symbole_verschieden("var", "var2")])


S13 = Schablone(
    nr="S13", titel="Variablen addieren, subtrahieren, multiplizieren",
    lektionen="3.4 – 3.9", erhebung="Vorstufe",
    anleitung="Fasse so weit wie möglich zusammen.",
    levelachse="Anzahl Glieder",
    bauformen=[BF13_1, BF13_2, BF13_3, BF13_4, BF13_6,
               BF13_8, BF13_9, BF13_10, BF13_11],
    kernidee=("Beim Addieren wird gezählt: a + a sind zwei Stück a, also 2a. "
              "Beim Multiplizieren entsteht eine Potenz: a · a ist a²."),
)


# ══════════════════════════════════════════════════════════════════════════
# S14 · Terme mit Zahlen und EINER Variablen        3.10 – 3.11
# ══════════════════════════════════════════════════════════════════════════

TIPPS14 = [
    "Die Variable und die reinen Zahlen sind zwei verschiedene Sorten.",
    "Zähle zuerst alle Glieder mit der Variablen zusammen, dann die Zahlen.",
    "Bleibt von beiden Sorten etwas übrig, stehen sie nebeneinander — das "
    "ist bereits die Antwort.",
]

def kandidaten14(glieder, v, loesung):
    """Die fuenf Fehler aus Teil 5 von S14, aus den Gliedern berechnet.

    - Zahl und Variablenterm zusammengezogen   3a + 4  ->  7a
    - Unsichtbare Eins uebersehen              a + 5a  ->  5a
    - Koeffizient eins weggelassen             4a − 3a ->  0
    - Vorzeichen beim Sortieren verloren       aus −9 wird +9
    - Punkt vor Strich missachtet              (nur wo ein Mal vorkommt)
    """
    summe = sum(k for k, _, _ in glieder)
    var_summe = sum(k for k, bs, _ in glieder if bs == v)
    zahl_summe = sum(k for k, bs, _ in glieder if bs != v)
    hat_zahlen = any(bs != v for _, bs, _ in glieder)

    raus = [F("alles_zusammengezogen", Integer(summe) * v,
              f"Ein Vielfaches von {zeige(v)} und eine reine Zahl sind "
              f"verschiedene Sorten.")]

    if hat_zahlen:
        # Vorzeichen beim Sortieren verloren: alle Zahlen positiv gerechnet
        falsch = var_summe * v + sum(abs(k) for k, bs, _ in glieder if bs != v)
        raus.append(F("vorzeichen_beim_sortieren", falsch,
                      "Abgezogene Zahlen bleiben negativ, auch wenn sie "
                      "weiter hinten stehen."))

    if any(abs(k) == 1 and bs == v for k, bs, _ in glieder):
        raus.append(F("unsichtbare_eins", (var_summe - 1) * v + zahl_summe,
                      f"Ein einzelnes {zeige(v)} zählt als 1{zeige(v)}."))

    if var_summe == 1:
        raus.append(F("eins_als_null", Integer(zahl_summe),
                      f"Bleibt genau ein {zeige(v)} übrig, schreibt man "
                      f"{zeige(v)} — nicht null."))

    raus.append(F("nur_zahlen", Integer(summe),
                  f"Die Variable {zeige(v)} bleibt stehen."))
    return raus


MUSTER14 = {
    "A": ["++", "+++"],
    "B": ["++-+", "+-++"],
    "C": ["+-+-+", "+--++", "+-+-+-"],
}
ZAHLEN14 = {"A": [2, 3, 4, 5], "B": [2, 3, 4, 5, 6], "C": [2, 3, 4, 5, 6, 7]}


def koeff14(p, anzahl):
    vorrat = p["zahlen"]
    return [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]


EINS = symbole("q")[0] ** 0        # neutrale Basis für reine Zahlen


def s14_glieder(muster, koeff, basen):
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        glieder.append((k, basen[i % len(basen)], "+" if k > 0 else "-"))
    return glieder


def s14_text(glieder, v):
    zahl = sum(k for k, bs, _ in glieder if bs == EINS)
    varteil = sum(k for k, bs, _ in glieder if bs == v)
    stuecke = [t for t in (varteil * v, zahl * EINS) if t != 0]
    return zeige_summe(*stuecke) if stuecke else "0"


def bf14_1(p):
    """Nichts lässt sich zusammenfassen — die wichtigste Bauform.

    Viele Schueler machen aus 3a + 4 die Zahl 7a, weil sie gelernt haben,
    dass am Schluss immer etwas Kuerzeres steht. Wenn der Generator diese
    Form nicht gezielt bringt, trainiert die App genau diese Erwartung.
    """
    v, muster = p["var"], p["muster"]
    koeff = koeff14(p, len(muster))
    glieder = [(koeff[0], v, "+")]
    for i, zeichen in enumerate(muster[1:], start=1):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        glieder.append((k, EINS, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("zusammengezogen", sum(k for k, _, _ in glieder) * v,
          f"{zeige(koeff[0] * v)} und eine reine Zahl sind verschiedene "
          f"Sorten — sie lassen sich nicht zusammenzählen."),
    ] + kandidaten14(glieder, v, l), [
        ("Sorten bestimmen", f"{zeige(v)}-Glieder und reine Zahlen"),
        ("Zahlen zusammenzählen", "die Variable bleibt stehen"),
        ("Ergebnis", s14_text(glieder, v))], TIPPS14,
        loesung_text=s14_text(glieder, v), zielform=Zielform.ZUSAMMENGEFASST)


BF14_1 = Bauform("BF1", "Zahl und Variablenterm nebeneinander",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER14[lv],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_1, filter=[kopfrechenbar, fehler_eindeutig])


def bf14_2(p):
    v, muster = p["var"], p["muster"]
    glieder = s14_glieder(muster, koeff14(p, len(muster)), [v])
    l = wert(glieder)
    negativ = sum(abs(k) for k, _, _ in glieder if k < 0)
    fehler = [F("variable_verloren", sum(k for k, _, _ in glieder),
                f"Die Variable {zeige(v)} bleibt stehen.")]
    if negativ:
        # Ohne ein einziges negatives Glied waere dieser Fehler gleich der
        # Loesung — auf Level A gibt es keine Minuszeichen.
        fehler.insert(0, F("vorzeichen_verloren", l + 2 * negativ,
                           "Abgezogene Glieder werden weggezählt, nicht "
                           "dazugezählt."))
    return bau(zeige_glieder(glieder), l, fehler + kandidaten14(glieder, v, l), [("Alle Glieder abschreiben", zeige_glieder(glieder)),
        ("Zahlen verrechnen", zeige(l))], TIPPS14,
        zielform=Zielform.ZUSAMMENGEFASST)


BF14_2 = Bauform("BF2", "Eine Sorte, mehrere Glieder",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER14[lv],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_2, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_3(p):
    v, muster = p["var"], p["muster"]
    glieder = s14_glieder(muster, koeff14(p, len(muster)), [v, EINS])
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("alles_zusammen", sum(k for k, _, _ in glieder) * v,
          "Die Variable und die reinen Zahlen sind zwei Sorten."),
    ] + kandidaten14(glieder, v, l), [("Sorten trennen", f"{zeige(v)}-Glieder und Zahlen"),
        ("Jede Sorte zählen", s14_text(glieder, v))], TIPPS14,
        loesung_text=s14_text(glieder, v), zielform=Zielform.ZUSAMMENGEFASST)


BF14_3 = Bauform("BF3", "Eine Sorte und Zahlen gemischt",
    bereiche={lv: {"var": SORTE1,
                   "muster": [mm for mm in MUSTER14[lv] if len(mm) >= 3],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_3, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_4(p):
    """Variable ohne sichtbaren Koeffizienten — die unsichtbare Eins."""
    v, muster = p["var"], p["muster"]
    koeff = koeff14(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = 1 if i == 0 else koeff[i]
        if zeichen == "-":
            k = -k
        glieder.append((k, v, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("eins_uebersehen", l - v,
          f"Das einzelne {zeige(v)} zählt als 1{zeige(v)}."),
    ] + kandidaten14(glieder, v, l), [("Unsichtbare Eins mitzählen", f"{zeige(v)} ist 1{zeige(v)}"),
        ("Zusammenzählen", zeige(l))], TIPPS14,
        zielform=Zielform.ZUSAMMENGEFASST)


BF14_4 = Bauform("BF4", "Variable ohne sichtbaren Koeffizienten",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER14[lv],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_4, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_5(p):
    """Punkt vor Strich vor dem Zusammenfassen."""
    v, f1, k1, k2, anzahl, minus = (p["var"], p["faktor"], p["k1"], p["k2"],
                                    p["anzahl"], p["minus"])
    teile = [f"{f1} · {k1}{zeige(v)}"]
    glieder = [(f1 * k1, v, "+")]
    teile.append(f"{MINUS if minus else '+'} {k2}{zeige(v)}")
    glieder.append((-k2 if minus else k2, v, "+"))
    if anzahl >= 3:
        teile.append(f"+ {zeige(v)}")
        glieder.append((1, v, "+"))
    l = wert(glieder)
    return bau(" ".join(teile), l, [
        F("mal_vergessen", l - (f1 - 1) * k1 * v,
          f"Zuerst das Mal: {f1} · {k1}{zeige(v)} = {f1*k1}{zeige(v)}."),
    ], [("Punkt vor Strich", f"{f1} · {k1}{zeige(v)} = {f1*k1}{zeige(v)}"),
        ("Zusammenfassen", zeige(l))], TIPPS14,
        zielform=Zielform.ZUSAMMENGEFASST)


BF14_5 = Bauform("BF5", "Punkt vor Strich vor dem Zusammenfassen",
    bereiche={"A": {"var": SORTE1, "faktor": [2], "k1": [3], "k2": [4],
                    "anzahl": [2], "minus": [False]},
              "B": {"var": SORTE1, "faktor": [3], "k1": [2], "k2": [4],
                    "anzahl": [3], "minus": [True]},
              "C": {"var": SORTE1, "faktor": [4, 5], "k1": [2, 3], "k2": [5],
                    "anzahl": [3], "minus": [True]}},
    bauen=bf14_5, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_6(p):
    """Sonderfall: nur eine Zahl bleibt übrig."""
    v, k, zahl, anzahl = p["var"], p["k1"], p["zahl"], p["anzahl"]
    if anzahl == 3:
        glieder = [(k, v, "+"), (-k, v, "-"), (zahl, EINS, "+")]
    elif anzahl == 4:
        glieder = [(k, v, "+"), (zahl + 2, EINS, "+"), (-k, v, "-"),
                   (-2, EINS, "-")]
    else:
        glieder = [(k, v, "+"), (zahl + 3, EINS, "+"), (-k, v, "-"),
                   (-2, EINS, "-"), (-1, EINS, "-")]
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("variable_geblieben", l + k * v,
          f"Die {zeige(v)}-Glieder heben sich auf — übrig bleibt nur die Zahl."),
    ], [("Sorten trennen", f"{zeige(v)}-Glieder und Zahlen"),
        (f"{zeige(v)} zusammenzählen", "ergibt null"),
        ("Ergebnis", zeige(l))], TIPPS14, zielform=Zielform.ZUSAMMENGEFASST)


BF14_6 = Bauform("BF6", "Sonderfall: nur eine Zahl bleibt übrig",
    bereiche={"A": {"var": SORTE1, "k1": [4, 5], "zahl": [9, 7], "anzahl": [3]},
              "B": {"var": SORTE1, "k1": [5, 6], "zahl": [5, 8], "anzahl": [4]},
              "C": {"var": SORTE1, "k1": [3, 7], "zahl": [5, 9], "anzahl": [5]}},
    bauen=bf14_6, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_7(p):
    """Sonderfall: nur ein Variablenterm bleibt übrig."""
    v, k, zahl, anzahl = p["var"], p["k1"], p["zahl"], p["anzahl"]
    if anzahl == 3:
        glieder = [(k, v, "+"), (zahl, EINS, "+"), (-zahl, EINS, "-")]
    elif anzahl == 4:
        glieder = [(k, v, "+"), (-zahl, EINS, "-"), (2, v, "+"),
                   (zahl, EINS, "+")]
    else:
        glieder = [(k, v, "+"), (zahl, EINS, "+"), (3, v, "+"),
                   (-3, EINS, "-"), (-(zahl - 3), EINS, "-")]
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("zahl_geblieben", l + zahl,
          "Die reinen Zahlen heben sich auf — übrig bleibt nur die Variable."),
    ], [("Sorten trennen", f"{zeige(v)}-Glieder und Zahlen"),
        ("Zahlen zusammenzählen", "ergibt null"),
        ("Ergebnis", zeige(l))], TIPPS14, zielform=Zielform.ZUSAMMENGEFASST)


BF14_7 = Bauform("BF7", "Sonderfall: nur ein Variablenterm bleibt übrig",
    bereiche={"A": {"var": SORTE1, "k1": [3, 4], "zahl": [5, 6], "anzahl": [3]},
              "B": {"var": SORTE1, "k1": [6, 7], "zahl": [4, 5], "anzahl": [4]},
              "C": {"var": SORTE1, "k1": [2, 4], "zahl": [7, 9], "anzahl": [5]}},
    bauen=bf14_7, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_8(p):
    """Minuszeichen am Anfang."""
    v, muster = p["var"], p["muster"]
    koeff = koeff14(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = koeff[i]
        if i == 0 or zeichen == "-":
            k = -k
        glieder.append((k, v, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("erstes_positiv", l + 2 * abs(glieder[0][0]) * v,
          "Das erste Glied ist negativ — das Minus gehört dazu."),
    ] + kandidaten14(glieder, v, l),
        [("Vorzeichen abschreiben", zeige_glieder(glieder)),
         ("Zusammenzählen", zeige(l))], TIPPS14,
        zielform=Zielform.ZUSAMMENGEFASST)


BF14_8 = Bauform("BF8", "Minuszeichen am Anfang",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER14[lv],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_8, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf14_9(p):
    """Sonderfall: das Ergebnis ist null."""
    v, k, zahl, anzahl = p["var"], p["k1"], p["zahl"], p["anzahl"]
    if anzahl == 2:
        glieder = [(k, v, "+"), (-k, v, "-")]
    elif anzahl == 4:
        glieder = [(k, v, "+"), (zahl, EINS, "+"), (-k, v, "-"),
                   (-zahl, EINS, "-")]
    else:
        glieder = [(k + 3, v, "+"), (-zahl, EINS, "-"), (-3, v, "-"),
                   (-k, v, "-"), (zahl, EINS, "+")]
    return bau(zeige_glieder(glieder), Integer(0), [
        F("nicht_null", Integer(k) * v,
          "Die Vorzeichen zählen mit — hier hebt sich alles auf."),
    ], [("Sorten trennen", "Variable und Zahlen"),
        ("Beide ergeben null", "das Ergebnis ist 0")], TIPPS14)


BF14_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"var": SORTE1, "k1": [5, 6], "zahl": [2], "anzahl": [2]},
              "B": {"var": SORTE1, "k1": [3, 4], "zahl": [4, 5], "anzahl": [4]},
              "C": {"var": SORTE1, "k1": [4, 7], "zahl": [2, 3], "anzahl": [5]}},
    bauen=bf14_9, filter=[fehler_eindeutig])


def bf14_10(p):
    """Sonderfall: der Koeffizient wird eins."""
    v, k, anzahl = p["var"], p["k1"], p["anzahl"]
    if anzahl == 2:
        glieder = [(k + 1, v, "+"), (-k, v, "-")]
    elif anzahl == 3:
        glieder = [(k + 2, v, "+"), (-k, v, "-"), (-1, v, "-")]
    else:
        glieder = [(k + 1, v, "+"), (3, EINS, "+"), (-k, v, "-"),
                   (-3, EINS, "-")]
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("null_geschrieben", Integer(0),
          f"Die Differenz ist eins, nicht null — geschrieben wird {zeige(v)}."),
    ], [("Zahlen verrechnen", "die Differenz ist 1"),
        ("Eins wird nicht geschrieben", zeige(l))], TIPPS14,
        zielform=Zielform.ZUSAMMENGEFASST)


BF14_10 = Bauform("BF10", "Sonderfall: der Koeffizient wird eins",
    bereiche={"A": {"var": SORTE1, "k1": [3, 4], "anzahl": [2]},
              "B": {"var": SORTE1, "k1": [5, 6], "anzahl": [3]},
              "C": {"var": SORTE1, "k1": [7, 8], "anzahl": [4]}},
    bauen=bf14_10, filter=[fehler_eindeutig])


def bf14_11(p):
    """Zahlen über den Term verstreut."""
    v, muster = p["var"], p["muster"]
    koeff = koeff14(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        # abwechselnd Variable und Zahl, damit die Zahlen verstreut liegen
        glieder.append((k, v if i % 2 == 0 else EINS, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(zeige_glieder(glieder), l, [
        F("alles_zusammen", sum(k for k, _, _ in glieder) * v,
          "Zahlen und Variablenglieder werden getrennt gezählt, auch wenn "
          "sie durcheinander stehen."),
    ] + kandidaten14(glieder, v, l), [("Sortieren", "erst alle Variablenglieder, dann alle Zahlen"),
        ("Jede Sorte zählen", s14_text(glieder, v))], TIPPS14,
        loesung_text=s14_text(glieder, v), zielform=Zielform.ZUSAMMENGEFASST)


BF14_11 = Bauform("BF11", "Zahlen über den Term verstreut",
    bereiche={lv: {"var": SORTE1,
                   "muster": [mm for mm in MUSTER14[lv] if len(mm) >= 3],
                   "zahlen": [ZAHLEN14[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf14_11, filter=[kopfrechenbar, fehler_eindeutig,
                           loesung_nicht_null])


S14 = Schablone(
    nr="S14", titel="Terme mit Zahlen und einer Variablen",
    lektionen="3.10 – 3.11", erhebung="Vorstufe zu 2a",
    anleitung="Fasse so weit wie möglich zusammen.",
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF14_1, BF14_2, BF14_3, BF14_4, BF14_5, BF14_6,
               BF14_7, BF14_8, BF14_9, BF14_10, BF14_11],
    kernidee=("Eine Variable und eine reine Zahl sind verschiedene Sorten. "
              "3a + 4 lässt sich nicht zusammenfassen — das ist bereits die "
              "Antwort."),
)
