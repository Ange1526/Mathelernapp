# -*- coding: utf-8 -*-
"""
S15 · Unterschiedliche Variablen erkennen   (Lektionen 4.1 · 4.7)
S17 · Produkte als gleichartige Terme       (Lektion 4.9)

Zusammen mit S16 ist Kapitel 4 damit vollstaendig — ausser 4.10, der
Gemischt-Lektion.

Der Lernschritt ist in beiden Faellen nicht das Rechnen, sondern das
ERKENNEN: welche Glieder gehoeren ueberhaupt zusammen? Weil die App nur
«rechne aus» kennt, steckt das Erkennen in der Rechenaufgabe — wer falsch
sortiert, bekommt ein falsches Ergebnis.

LEVELACHSE (Teil 2 beider Schablonen):

    S15   Glieder  zwei bis drei → vier → fuenf bis sieben
    S17   Glieder  zwei → zwei bis vier → drei bis vier
    beide Vorzeichen  alles positiv → ein Minus → mehrere Minus

Die Bausteine kommen aus `s16_gleichartig`: Glieder, Anzeige und der Filter
`beide_sorten_bleiben`. Dreimal dieselbe Mechanik zu schreiben waere dreimal
dieselbe Fehlerquelle.
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import zeige, zeige_summe
from .qualitaet import (fehler_eindeutig, kopfrechenbar, loesung_nicht_null,
                        symbole_verschieden)
from .s16_gleichartig import beide_sorten_bleiben, wert, zeige_glieder
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}

SORTE1 = [a, x, u, m]
SORTE2 = [b, y, v, n]
SORTE3 = [c, z, w, d]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def siebe(fehler, loesung):
    """Doppelte und die Loesung selbst aus dem Katalog entfernen."""
    raus, gesehen = [], set()
    for f in fehler:
        w = f.ergebnis.expr
        if w is None or w == loesung or str(w) in gesehen:
            continue
        gesehen.add(str(w))
        raus.append(f)
    return raus


def bau(glieder, fehler, schritte, tipps, loesung=None, loesung_text=None,
        sorten=None):
    l = loesung if loesung is not None else wert(glieder)
    fehler = siebe(fehler, l)
    return {"frage": zeige_glieder(glieder),
            "loesung_text": loesung_text or zeige(l),
            "sorten": sorten or [],
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.ZUSAMMENGEFASST,
                               fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


# ── Die Levelachse ────────────────────────────────────────────────────────
#
# Ein Zeichen pro Glied. A hat zwei bis drei Glieder und kein Minus, B vier
# Glieder und ein Minus, C fuenf bis sieben Glieder und mehrere Minus.
# Das ist der ganze Unterschied zwischen den Stufen — die Zahlen bleiben
# ueberall klein.

MUSTER15 = {
    "A": ["++", "+++"],
    "B": ["++-+", "+-++", "+++-"],
    "C": ["+-+-+", "+--++-", "+-+-+-+", "+-++--"],
}

#: S17 hat kuerzere Aufgaben, weil ein Produkt schon breiter ist als eine
#: einzelne Variable. Teil 2 sagt: zwei → zwei bis vier → drei bis vier.
MUSTER17 = {
    "A": ["++"],
    "B": ["+-", "++-", "+-++"],
    "C": ["+-+-", "+--+", "+-+"],
}

ZAHLEN = {"A": [2, 3, 4, 5], "B": [2, 3, 4, 5, 6], "C": [2, 3, 4, 5, 6, 7]}


def koeffizienten(p, anzahl):
    """Zahlen aus dem Vorrat, mit Schrittweite 5 durchlaufen.

    Die Schrittweite muss zu JEDER Vorratsgroesse teilerfremd sein, sonst
    wiederholen sich die Zahlen. Mit Schrittweite 3 und sechs Zahlen kam
    `3bu² − 6b²u + 3bu² − 6b²u` heraus; mit Schrittweite 5 und fuenf Zahlen
    waren sogar alle vier Koeffizienten gleich, und der Filter
    `beide_sorten_bleiben` verwarf danach jede Aufgabe.

    Die Vorraete haben vier, fuenf oder sechs Eintraege. 7 ist zu allen
    dreien teilerfremd.
    """
    vorrat = p["zahlen"]
    return [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]


def glieder_bauen(muster, koeff, basen):
    """Muster + Zahlen + Sortenfolge -> Glieder.

    `basen` wird zyklisch durchlaufen: bei zwei Sorten also abwechselnd.
    """
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        glieder.append((k, basen[i % len(basen)], "+" if k > 0 else "-"))
    return glieder


def summe_je_sorte(glieder, basis):
    return sum(k for k, bs, _ in glieder if bs == basis)


def text_sorten(glieder, basen):
    """Musterlösung in der Reihenfolge der Sorten, nicht in SymPys."""
    return zeige_summe(*[summe_je_sorte(glieder, bs) * bs for bs in basen
                         if summe_je_sorte(glieder, bs) != 0])


TIPPS15 = [
    "Nur Glieder mit genau derselben Variablen lassen sich zusammenfassen. "
    "a und b bleiben getrennt.",
    "Bestimme zuerst, wie viele Sorten es gibt, und behandle jede für sich.",
    "Rechne jede Sorte einzeln zusammen — die Sorten bleiben nebeneinander "
    "stehen.",
]

TIPPS17 = [
    "Zwei Produkte sind gleichartig, wenn sie dieselben Variablen mit "
    "denselben Hochzahlen haben. Die Reihenfolge der Faktoren spielt keine "
    "Rolle.",
    "Schreib bei jedem Term auf, welche Variable welche Hochzahl hat, und "
    "sortiere danach.",
    "x²y hat x zweimal und y einmal. xy² hat es umgekehrt — das sind zwei "
    "Sorten.",
]


def schritte_sorten(frage, basen, glieder, l):
    return [("Alle Glieder mit ihrem Vorzeichen abschreiben", frage),
            ("Sorten bestimmen",
             " und ".join(zeige(bs) for bs in basen)),
            ("Jede Sorte einzeln zusammenzählen",
             "   ".join(f"{zeige(bs)}: {summe_je_sorte(glieder, bs)}"
                        for bs in basen)),
            ("Zusammenschreiben", zeige(l))]


def fehler_sorten(glieder, basen, l):
    """Die drei Fehler, die in jeder Sortenaufgabe auftreten können."""
    alle = sum(k for k, _, _ in glieder)
    produkt = basen[0]
    for bs in basen[1:]:
        produkt = produkt * bs
    raus = [
        F("sorten_nicht_getrennt", alle * produkt,
          f"{' und '.join(zeige(bs) for bs in basen)} sind verschieden und "
          f"lassen sich nicht zusammenzählen."),
    ]
    # Vorzeichen beim Sortieren verloren: das erste negative Glied positiv
    for i, (k, bs, _) in enumerate(glieder):
        if k < 0:
            raus.append(F("vorzeichen_verloren", l + 2 * abs(k) * bs,
                          f"Das Glied {zeige(k * bs)} ist negativ — das "
                          f"Vorzeichen gehört dazu."))
            break

    # Alle Vorzeichen ignoriert
    ohne = sum(abs(k) * bs for k, bs, _ in glieder)
    raus.append(F("alle_vorzeichen_ignoriert", ohne,
                  "Die Minuszeichen zählen mit — abgezogene Glieder werden "
                  "weggezählt."))

    # Nur die Zahlen verrechnet, die Variablen weggelassen
    raus.append(F("variablen_weggelassen", Integer(alle),
                  "Die Variablen bleiben stehen. Nur die Zahlen davor werden "
                  "verrechnet."))
    return raus


# ══════════════════════════════════════════════════════════════════════════
# S15 · Unterschiedliche Variablen erkennen
# ══════════════════════════════════════════════════════════════════════════

def _bf15(p, basen, extra=None, sorten_pflicht=True):
    muster = p["muster"]
    glieder = glieder_bauen(muster, koeffizienten(p, len(muster)), basen)
    l = wert(glieder)
    fehler = fehler_sorten(glieder, basen, l) + (extra(glieder, basen, l)
                                                 if extra else [])
    return bau(glieder, fehler,
               schritte_sorten(zeige_glieder(glieder), basen, glieder, l),
               TIPPS15, loesung_text=text_sorten(glieder, basen),
               sorten=basen if sorten_pflicht else [])


def bf15_1(p):
    return _bf15(p, [p["var"], p["var2"]])


#: BF1 braucht mindestens vier Glieder — sonst kommt keine Sorte «mehrfach»
#: vor und die Bauform waere in Wahrheit BF3. Die Gliederzahl bleibt trotzdem
#: die Levelachse: vier, fuenf bis sechs, sechs bis sieben.
MUSTER15_BF1 = {"A": ["++++"], "B": ["++-+", "+-++", "+++-"],
                "C": ["+-+-+-", "+--++-", "+-+-+-+"]}


BF15_1 = Bauform("BF1", "Zwei Sorten, beide kommen mehrfach vor",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "muster": MUSTER15_BF1[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_1, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2"),
                          beide_sorten_bleiben])


def bf15_2(p):
    """Eine Sorte kommt nur einmal vor — sie steht am Schluss allein da."""
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        basis = v2 if i == 1 else v1          # nur ein einziges v2-Glied
        glieder.append((k, basis, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, fehler_sorten(glieder, [v1, v2], l),
               schritte_sorten(zeige_glieder(glieder), [v1, v2], glieder, l),
               TIPPS15, loesung_text=text_sorten(glieder, [v1, v2]),
               sorten=[v1, v2])


BF15_2 = Bauform("BF2", "Zwei Sorten, eine kommt nur einmal vor",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER15[lv] if len(mm) >= 3]
                             or MUSTER15[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_2, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2"),
                          beide_sorten_bleiben])


def bf15_3(p):
    """Nichts lässt sich zusammenfassen — jede Sorte kommt einmal vor.

    Das Gegenstück zu BF1: zwei Sorten, und trotzdem ist nichts zu tun.
    Genau das meint Lektion 4.7.
    """
    muster = p["muster"]
    basen = [p["var"], p["var2"], p["var3"]][:len(muster)]
    glieder = glieder_bauen(muster, koeffizienten(p, len(muster)), basen)
    l = wert(glieder)
    alle = sum(k for k, _, _ in glieder)
    return bau(glieder, [
        F("zusammengezogen", alle * basen[0],
          f"{' und '.join(zeige(bs) for bs in basen)} sind verschiedene "
          f"Sorten. Der Term ist bereits die Antwort."),
    ], [("Sorten vergleichen", "jede Variable kommt nur einmal vor"),
        ("Ergebnis", "der Term bleibt, wie er ist")], TIPPS15,
        loesung_text=zeige_glieder(glieder))


BF15_3 = Bauform("BF3", "Zwei Sorten, nichts lässt sich zusammenfassen",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "muster": ["++"], "zahlen": [ZAHLEN["A"]], "dreh": [0, 1]},
              "B": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "muster": ["+-"], "zahlen": [ZAHLEN["B"]], "dreh": [0, 1]},
              "C": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "muster": ["+-+", "-++"], "zahlen": [ZAHLEN["C"]],
                    "dreh": [0, 1, 2]}},
    bauen=bf15_3, filter=[kopfrechenbar, fehler_eindeutig,
                          symbole_verschieden("var", "var2", "var3")])


def bf15_4(p):
    """Zwei Sorten und reine Zahlen — Zahlen sind die dritte Sorte."""
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    eins = symbole("q")[0] ** 0          # neutrale Basis 1 für reine Zahlen
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        basis = [v1, v2, eins][i % 3]
        glieder.append((k, basis, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, fehler_sorten(glieder, [v1, v2], l),
               schritte_sorten(zeige_glieder(glieder), [v1, v2], glieder, l),
               TIPPS15, loesung_text=text_sorten(glieder, [v1, v2, eins]),
               sorten=[v1, v2])


BF15_4 = Bauform("BF4", "Zwei Sorten und Zahlen",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER15[lv] if len(mm) >= 3]
                             or MUSTER15[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_4, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2"),
                          beide_sorten_bleiben])


def bf15_5(p):
    return _bf15(p, [p["var"], p["var2"], p["var3"]])


BF15_5 = Bauform("BF5", "Drei Sorten",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                   "muster": [mm for mm in MUSTER15[lv] if len(mm) >= 3]
                             or MUSTER15[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_5, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2", "var3")])


def bf15_6(p):
    """Sonderfall: eine Sorte fällt ganz weg. Die Gliederzahl trägt das Level."""
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    k1, k2 = p["k1"], p["k2"]
    if anzahl == 3:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-k1, v1, "-")]
    elif anzahl == 4:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-k1, v1, "-"),
                   (k2 + 1, v2, "+")]
    else:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-(k1 - 1), v1, "-"),
                   (k2 + 1, v2, "+"), (-1, v1, "-")]
    l = wert(glieder)
    return bau(glieder, [
        F("weggefallene_sorte", l + k1 * v1,
          f"Die {zeige(v1)}-Glieder heben sich auf. Übrig bleibt nur "
          f"{zeige(l)}."),
        F("sorten_nicht_getrennt", sum(k for k, _, _ in glieder) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden."),
    ], [("Sorten bestimmen", f"{zeige(v1)} und {zeige(v2)}"),
        (f"{zeige(v1)}-Glieder rechnen", "sie ergeben null"),
        ("Ergebnis", zeige(l))], TIPPS15)


BF15_6 = Bauform("BF6", "Sonderfall: eine Sorte fällt ganz weg",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [3],
                    "k1": [3, 5, 7], "k2": [2, 3, 4]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [4],
                    "k1": [3, 5, 6], "k2": [2, 3, 4]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [5],
                    "k1": [4, 6, 7], "k2": [2, 3, 4]}},
    bauen=bf15_6, filter=[kopfrechenbar, fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf15_7(p):
    """Sonderfall: nur eine Zahl bleibt übrig."""
    v1, v2, zahl, anzahl = p["var"], p["var2"], p["zahl"], p["anzahl"]
    k1, k2 = p["k1"], p["k2"]
    eins = symbole("q")[0] ** 0
    if anzahl == 5:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-k1, v1, "-"),
                   (-k2, v2, "-"), (zahl, eins, "+")]
    else:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (zahl, eins, "+"),
                   (-k1, v1, "-"), (-k2, v2, "-"), (-1, eins, "-")]
    l = wert(glieder)
    return bau(glieder, [
        F("variablen_stehen_geblieben", l + k1 * v1,
          f"Auch die {zeige(v1)}-Glieder heben sich auf — übrig bleibt nur "
          f"die Zahl {zeige(l)}."),
    ], [("Sorten bestimmen", f"{zeige(v1)}, {zeige(v2)} und reine Zahlen"),
        ("Beide Variablensorten ergeben null", "sie heben sich auf"),
        ("Ergebnis", zeige(l))], TIPPS15)


BF15_7 = Bauform("BF7", "Sonderfall: nur eine Zahl bleibt übrig",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [5],
                    "k1": [2, 3], "k2": [2, 3], "zahl": [5, 8]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [5],
                    "k1": [4, 5], "k2": [2, 3], "zahl": [7, 9]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [6],
                    "k1": [4, 6], "k2": [3, 4], "zahl": [6, 9]}},
    bauen=bf15_7, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2")])


def bf15_8(p):
    """Sorten ohne sichtbaren Koeffizienten — die unsichtbare Eins."""
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = 1 if i < 2 else koeff[i]          # die ersten beiden ohne Zahl
        if zeichen == "-":
            k = -k
        glieder.append((k, [v1, v2][i % 2], "+" if k > 0 else "-"))
    l = wert(glieder)
    ohne_eins = sum(k * bs for k, bs, _ in glieder if abs(k) != 1)
    return bau(glieder, [
        F("unsichtbare_eins", ohne_eins,
          f"Das einzelne {zeige(v1)} zählt als 1{zeige(v1)}."),
        F("sorten_nicht_getrennt", sum(k for k, _, _ in glieder) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden."),
    ], schritte_sorten(zeige_glieder(glieder), [v1, v2], glieder, l),
        TIPPS15, loesung_text=text_sorten(glieder, [v1, v2]))


BF15_8 = Bauform("BF8", "Sorten ohne sichtbaren Koeffizienten",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER15[lv] if len(mm) >= 3]
                             or MUSTER15[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_8, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2")])


def bf15_9(p):
    """Minuszeichen am Anfang."""
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = koeff[i]
        if i == 0 or zeichen == "-":
            k = -k
        glieder.append((k, [v1, v2][i % 2], "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, [
        F("erstes_positiv", l + 2 * abs(glieder[0][0]) * v1,
          "Das erste Glied ist negativ — das Minus gehört dazu."),
        F("sorten_nicht_getrennt", sum(k for k, _, _ in glieder) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden."),
    ], schritte_sorten(zeige_glieder(glieder), [v1, v2], glieder, l),
        TIPPS15, loesung_text=text_sorten(glieder, [v1, v2]),
        sorten=[v1, v2])


BF15_9 = Bauform("BF9", "Minuszeichen am Anfang",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER15[lv] if len(mm) >= 3]
                             or MUSTER15[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf15_9, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2"),
                          beide_sorten_bleiben])


def bf15_10(p):
    """Punkt vor Strich vor dem Zusammenfassen."""
    v1, v2, f1, k1, k2, anzahl = (p["var"], p["var2"], p["faktor"],
                                  p["k1"], p["k2"], p["anzahl"])
    teile = [f"{f1} · {k1}{zeige(v1)}", f"+ {k2}{zeige(v2)}"]
    glieder = [(f1 * k1, v1, "+"), (k2, v2, "+")]
    if anzahl >= 3:
        teile.append(f"{'−' if p['minus'] else '+'} {k1}{zeige(v1)}")
        glieder.append((-k1 if p["minus"] else k1, v1, "+"))
    if anzahl >= 4:
        teile.append(f"+ {k2}{zeige(v2)}")
        glieder.append((k2, v2, "+"))
    frage = " ".join(teile)
    l = wert(glieder)
    g = bau(glieder, [
        F("mal_vergessen", l - (f1 - 1) * k1 * v1,
          f"Zuerst das Mal: {f1} · {k1}{zeige(v1)} = {f1*k1}{zeige(v1)}."),
        F("sorten_nicht_getrennt", sum(k for k, _, _ in glieder) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden."),
    ], [("Punkt vor Strich", f"{f1} · {k1}{zeige(v1)} = {f1*k1}{zeige(v1)}"),
        ("Sorten zusammenfassen", zeige(l))], TIPPS15,
        loesung_text=text_sorten(glieder, [v1, v2]),
        sorten=[v1, v2])
    # Die Frage wird von Hand gesetzt: sie enthaelt ein Malzeichen, das
    # `zeige_glieder` nicht kennt.
    g["frage"] = frage
    return g


BF15_10 = Bauform("BF10", "Punkt vor Strich vor dem Zusammenfassen",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "faktor": [2, 3],
                    "k1": [2, 3], "k2": [3, 4], "anzahl": [2],
                    "minus": [False]},
              "B": {"var": SORTE1, "var2": SORTE2, "faktor": [3, 4],
                    "k1": [2, 3], "k2": [4, 5], "anzahl": [3],
                    "minus": [True]},
              "C": {"var": SORTE1, "var2": SORTE2, "faktor": [4, 5],
                    "k1": [2, 3], "k2": [3, 4], "anzahl": [4],
                    "minus": [True]}},
    bauen=bf15_10, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                           symbole_verschieden("var", "var2"),
                           beide_sorten_bleiben])


def bf15_11(p):
    """Sonderfall: das Ergebnis ist null."""
    v1, v2, k1, k2, anzahl = p["var"], p["var2"], p["k1"], p["k2"], p["anzahl"]
    eins = symbole("q")[0] ** 0
    if anzahl == 4:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-k1, v1, "-"), (-k2, v2, "-")]
    else:
        glieder = [(k1, v1, "+"), (k2, v2, "+"), (-3, eins, "-"),
                   (-k1, v1, "-"), (-k2, v2, "-"), (3, eins, "+")]
    return bau(glieder, [
        F("nicht_null", sum(abs(k) for k, _, _ in glieder) * v1,
          "Die Vorzeichen zählen mit — hier heben sich alle Glieder auf."),
    ], [("Sorten sortieren", "gleiche Variablen zusammen"),
        ("Jede Sorte ergibt null", "alles hebt sich auf"),
        ("Ergebnis", "0")], TIPPS15, loesung=0)


BF15_11 = Bauform("BF11", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "k1": [3, 5],
                    "k2": [2, 3], "anzahl": [4]},
              "B": {"var": SORTE1, "var2": SORTE2, "k1": [4, 7],
                    "k2": [2, 3], "anzahl": [4]},
              "C": {"var": SORTE1, "var2": SORTE2, "k1": [5, 6],
                    "k2": [3, 4], "anzahl": [6]}},
    bauen=bf15_11, filter=[fehler_eindeutig,
                           symbole_verschieden("var", "var2")])


S15 = Schablone(
    nr="S15", titel="Unterschiedliche Variablen erkennen",
    lektionen="4.1 · 4.7", erhebung="Vorstufe zu 2a",
    anleitung="Fasse so weit wie möglich zusammen.",
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF15_1, BF15_2, BF15_3, BF15_4, BF15_5, BF15_6,
               BF15_7, BF15_8, BF15_9, BF15_10, BF15_11],
    kernidee=("Zwei Glieder sind nur dann gleichartig, wenn sie genau "
              "dieselbe Variable haben. Verschiedene Sorten bleiben "
              "nebeneinander stehen — auch wenn das Ergebnis dann länger "
              "aussieht als erwartet."),
)


# ══════════════════════════════════════════════════════════════════════════
# S17 · Produkte als gleichartige Terme
# ══════════════════════════════════════════════════════════════════════════

def kandidaten17(glieder, basen, loesung):
    """Die fuenf Fehler aus Teil 5 von S17.

    - Produkte mit vertauschten Hochzahlen zusammengefasst
    - Gleiches Produkt wegen anderer Reihenfolge getrennt
    - Minus vor der Klammer nicht aufgeloest
    - Weggefallene Sorte trotzdem hingeschrieben
    - Produkt und einfache Variable zusammengezogen
    """
    summe = sum(k for k, _, _ in glieder)
    raus = []

    if len(basen) > 1:
        produkt = basen[0]
        for bs in basen[1:]:
            produkt = produkt * bs
        raus.append(F("hochzahlen_addiert", Integer(summe) * produkt,
            f"{zeige(basen[0])} und {zeige(basen[-1])} sind verschiedene "
            f"Sorten. Beim Addieren ändern sich die Hochzahlen nicht."))
        raus.append(F("sorten_nicht_getrennt", Integer(summe) * basen[0],
            "Jede Sorte wird für sich gezählt."))

        # Weggefallene Sorte trotzdem hingeschrieben
        for bs in basen:
            if sum(k for k, b, _ in glieder if b == bs) == 0:
                rest = sum(k * b for k, b, _ in glieder if b != bs)
                erste = next(k for k, b, _ in glieder if b == bs)
                raus.append(F("weggefallene_sorte", rest + erste * bs,
                    f"Die {zeige(bs)}-Terme heben sich auf — sie werden nicht "
                    f"mehr hingeschrieben."))
                break

    # Vorzeichen eines negativen Glieds verloren
    for k, bs, _ in glieder:
        if k < 0:
            raus.append(F("vorzeichen_verloren", loesung + 2 * abs(k) * bs,
                f"Das Glied {zeige(k * bs)} ist negativ — das Vorzeichen "
                f"gehört dazu."))
            break

    raus.append(F("nur_koeffizienten", Integer(summe),
        "Der Term behält seine Variablen — nur die Zahlen davor werden "
        "verrechnet."))
    return raus


def _bf17(p, basen, extra=None, sorten_pflicht=True):
    muster = p["muster"]
    glieder = glieder_bauen(muster, koeffizienten(p, len(muster)), basen)
    l = wert(glieder)
    fehler = [F("sorten_nicht_getrennt",
                sum(k for k, _, _ in glieder) * basen[0] * basen[-1],
                f"{zeige(basen[0])} und {zeige(basen[-1])} sind "
                f"verschiedene Sorten.")] if len(basen) > 1 else []
    fehler += extra(glieder, basen, l) if extra else []
    fehler += kandidaten17(glieder, basen, l)
    return bau(glieder, fehler,
               schritte_sorten(zeige_glieder(glieder), basen, glieder, l),
               TIPPS17, loesung_text=text_sorten(glieder, basen),
               sorten=basen if sorten_pflicht and len(basen) > 1 else [])


def bf17_1(p):
    return _bf17(p, [p["var"] * p["var2"]])


BF17_1 = Bauform("BF1", "Gleiches Produkt, gleiche Reihenfolge",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "muster": MUSTER17[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_1, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2")])


def bf17_2(p):
    """Gleiches Produkt, andere Reihenfolge der Faktoren.

    Der Wert ist derselbe — nur die Anzeige dreht die Faktoren um. `zeige`
    wuerde sie sonst wieder alphabetisch sortieren, und dann waere die
    Bauform nicht mehr das, was sie sein soll.
    """
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    basis = v1 * v2
    teile = []
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        glieder.append((k, basis, "+" if k > 0 else "-"))
        gedreht = f"{zeige(v2)}{zeige(v1)}" if i % 2 else f"{zeige(v1)}{zeige(v2)}"
        stueck = f"{abs(k) if abs(k) != 1 else ''}{gedreht}"
        teile.append(stueck if i == 0 and k > 0 else
                     (f"− {stueck}" if k < 0 else f"+ {stueck}"))
    l = wert(glieder)
    g = bau(glieder, [
        F("reihenfolge_getrennt", sum(k for k, _, _ in glieder) * (v1 * v2) ** 2,
          f"{zeige(v1)}{zeige(v2)} und {zeige(v2)}{zeige(v1)} sind dasselbe: "
          f"die Reihenfolge der Faktoren spielt keine Rolle."),
    ], [("Faktoren ordnen", f"{zeige(v2)}{zeige(v1)} ist {zeige(v1)}{zeige(v2)}"),
        ("Zusammenzählen", zeige(l))], TIPPS17)
    g["frage"] = " ".join(teile)
    return g


BF17_2 = Bauform("BF2", "Gleiches Produkt, andere Reihenfolge der Faktoren",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_2, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2")])


def bf17_3(p):
    v1, v2 = p["var"], p["var2"]
    return _bf17(p, [v1 ** 2 * v2, v1 * v2 ** 2])


BF17_3 = Bauform("BF3", "Produkte mit Potenzen",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_3, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2"),
                          beide_sorten_bleiben])


def bf17_4(p):
    """Produkte, die sich nur in einem Faktor unterscheiden."""
    v1, v2, v3 = p["var"], p["var2"], p["var3"]
    return _bf17(p, [v1 * v2, v1 * v3])


BF17_4 = Bauform("BF4", "Produkte, die sich nur in einem Faktor unterscheiden",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_4, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2", "var3"),
                          beide_sorten_bleiben])


def bf17_5(p):
    """Eine Sorte hebt sich auf."""
    v1, v2, k1, k2, anzahl = p["var"], p["var2"], p["k1"], p["k2"], p["anzahl"]
    b1, b2 = v1 * v2 ** 2, v1 ** 2 * v2 ** 2
    if anzahl == 2:
        glieder = [(-k1, b1, "-"), (k1, b1, "+")]
        l = 0
    elif anzahl == 4:
        glieder = [(-k1, b1, "-"), (-k2, b2, "-"), (k1, b1, "+"), (-k2, b2, "-")]
        l = wert(glieder)
    else:
        glieder = [(-k1, b1, "-"), (k2, b2, "+"), (-k1, b1, "-"), (-k2, b2, "-")]
        l = wert(glieder)
    return bau(glieder, [
        F("weggefallene_sorte", l + (-k1 if anzahl != 2 else k1) * b1,
          f"Die {zeige(b1)}-Terme heben sich auf."),
    ], [("Sorten bestimmen", f"{zeige(b1)} und {zeige(b2)}"),
        ("Zusammenzählen", zeige(l))], TIPPS17, loesung=l)


BF17_5 = Bauform("BF5", "Eine Sorte hebt sich auf",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "k1": [4, 5],
                    "k2": [3, 7], "anzahl": [2]},
              "B": {"var": SORTE1, "var2": SORTE2, "k1": [5, 6],
                    "k2": [3, 7], "anzahl": [4]},
              "C": {"var": SORTE1, "var2": SORTE2, "k1": [3, 6],
                    "k2": [5, 11], "anzahl": [3]}},
    bauen=bf17_5, filter=[kopfrechenbar, fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf17_7(p):
    """Sonderfall: das Ergebnis ist null."""
    v1, v2, k1, k2, anzahl = p["var"], p["var2"], p["k1"], p["k2"], p["anzahl"]
    b1 = v1 * v2
    b2 = v1 ** 2 * v2
    if anzahl == 2:
        glieder = [(k1, b1, "+"), (-k1, b1, "-")]
    elif anzahl == 3:
        glieder = [(k1, b1, "+"), (k2, b1, "+"), (-(k1 + k2), b1, "-")]
    else:
        glieder = [(k1, b2, "+"), (-k2, b1, "-"), (-k1, b2, "-"), (k2, b1, "+")]
    return bau(glieder, [
        F("nicht_null", sum(abs(k) for k, _, _ in glieder) * b1,
          "Die Vorzeichen zählen mit — alle Glieder heben sich auf."),
    ], [("Sorten sortieren", "gleiche Produkte zusammen"),
        ("Zusammenzählen", "alles ergibt null")], TIPPS17, loesung=0)


BF17_7 = Bauform("BF7", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "k1": [3, 4],
                    "k2": [2, 3], "anzahl": [2]},
              "B": {"var": SORTE1, "var2": SORTE2, "k1": [3, 5],
                    "k2": [2, 4], "anzahl": [3]},
              "C": {"var": SORTE1, "var2": SORTE2, "k1": [6, 7],
                    "k2": [2, 4], "anzahl": [4]}},
    bauen=bf17_7, filter=[fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf17_8(p):
    """Sonderfall: der Koeffizient wird eins."""
    v1, v2, k, anzahl = p["var"], p["var2"], p["k1"], p["anzahl"]
    b1, b2 = v1 * v2, v1 ** 2 * v2
    if anzahl == 2:
        glieder = [(k + 1, b1, "+"), (-k, b1, "-")]
    elif anzahl == 3:
        glieder = [(k + 2, b1, "+"), (-k, b1, "-"), (-1, b1, "-")]
    else:
        glieder = [(k + 1, b2, "+"), (k, b1, "+"), (-k, b2, "-"), (-k, b1, "-")]
    l = wert(glieder)
    return bau(glieder, [
        F("null_geschrieben", 0,
          "Die Differenz ist eins, nicht null — geschrieben wird der Term "
          "ohne Zahl davor."),
    ], [("Zahlen verrechnen", "die Differenz ist 1"),
        ("Eins wird nicht geschrieben", zeige(l))], TIPPS17)


BF17_8 = Bauform("BF8", "Sonderfall: der Koeffizient wird eins",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "k1": [3, 4], "anzahl": [2]},
              "B": {"var": SORTE1, "var2": SORTE2, "k1": [3, 5], "anzahl": [3]},
              "C": {"var": SORTE1, "var2": SORTE2, "k1": [4, 6], "anzahl": [4]}},
    bauen=bf17_8, filter=[fehler_eindeutig,
                          symbole_verschieden("var", "var2")])


def bf17_9(p):
    """Drei Faktoren im Produkt."""
    v1, v2, v3 = p["var"], p["var2"], p["var3"]
    return _bf17(p, [v1 * v2 * v3])


BF17_9 = Bauform("BF9", "Drei Faktoren im Produkt",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                   "muster": MUSTER17[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_9, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2", "var3")])


def bf17_10(p):
    """Produkt und einfache Variable nebeneinander."""
    v1, v2 = p["var"], p["var2"]
    return _bf17(p, [v1 * v2, v1])


BF17_10 = Bauform("BF10", "Produkt und einfache Variable nebeneinander",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_10, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                           symbole_verschieden("var", "var2"),
                           beide_sorten_bleiben])


def bf17_11(p):
    """Minuszeichen am Anfang."""
    muster, v1, v2 = p["muster"], p["var"], p["var2"]
    koeff = koeffizienten(p, len(muster))
    basis = v1 * v2
    glieder = []
    for i, zeichen in enumerate(muster):
        k = koeff[i]
        if i == 0 or zeichen == "-":
            k = -k
        glieder.append((k, basis, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, [
        F("erstes_positiv", l + 2 * abs(glieder[0][0]) * basis,
          "Das erste Glied ist negativ — das Minus gehört dazu."),
    ], [("Vorzeichen abschreiben", zeige_glieder(glieder)),
        ("Zusammenzählen", zeige(l))], TIPPS17)


BF17_11 = Bauform("BF11", "Minuszeichen am Anfang",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_11, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                           symbole_verschieden("var", "var2")])


def bf17_12(p):
    """Zwei Produktsorten mit vertauschten Hochzahlen — a²b gegen ab²."""
    v1, v2 = p["var"], p["var2"]
    return _bf17(p, [v1 * v2 ** 2, v1 ** 2 * v2])


BF17_12 = Bauform("BF12", "Zwei Produktsorten mit vertauschten Hochzahlen",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER17[lv] if len(mm) >= 2],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf17_12, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                           symbole_verschieden("var", "var2"),
                           beide_sorten_bleiben])


def bf17_6(p):
    """Minus vor der Klammer bei Produkten: − (−4ab)."""
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    koeff = koeffizienten(p, anzahl)
    basis = v1 * v2
    stile = ["M", "+", "M", "-"][:anzahl]
    glieder = []
    for i, s in enumerate(stile):
        k = koeff[i]
        glieder.append((-k if s == "-" else k, basis, s))
    l = wert(glieder)
    doppelt_falsch = sum((-k if s == "M" else k) * basis
                         for k, _, s in glieder)
    return bau(glieder, [
        F("doppelminus", doppelt_falsch,
          f"−(−{zeige(basis)}) wird +{zeige(basis)}: Minus mal Minus gibt Plus."),
    ], [("Doppelzeichen auflösen", "−(−…) wird +…"),
        ("Zusammenzählen", zeige(l))], TIPPS17)


BF17_6 = Bauform("BF6", "Minus vor der Klammer bei Produkten",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [2],
                    "zahlen": [ZAHLEN["A"]], "dreh": [0, 1]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [3],
                    "zahlen": [ZAHLEN["B"]], "dreh": [0, 1, 2]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [4],
                    "zahlen": [ZAHLEN["C"]], "dreh": [0, 1, 2]}},
    bauen=bf17_6, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                          symbole_verschieden("var", "var2")])


S17 = Schablone(
    nr="S17", titel="Produkte als gleichartige Terme",
    lektionen="4.9", erhebung="2a",
    anleitung="Fasse so weit wie möglich zusammen.",
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF17_1, BF17_2, BF17_3, BF17_4, BF17_5, BF17_6,
               BF17_7, BF17_8, BF17_9, BF17_10, BF17_11, BF17_12],
    kernidee=("Zwei Produkte sind gleichartig, wenn sie dieselben Variablen "
              "mit denselben Hochzahlen haben. Die Reihenfolge der Faktoren "
              "spielt keine Rolle — ab und ba sind dasselbe."),
)
