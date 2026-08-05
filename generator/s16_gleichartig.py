# -*- coding: utf-8 -*-
"""
S16 · Gleichartige Terme zusammenfassen   (Lektionen 4.2 – 4.6 · 4.8)

    «Fasse so weit wie möglich zusammen.»
    u² + u² + u²      4a² − a² + 2a²      5x² − 3x² − x² + 2x²

Ersetzt `s4k_gleichartig.py`. Der Grund ist nicht Geschmack, sondern ein
Konstruktionsfehler: dort stand im Kopf «Levelachse: Anzahl Glieder», gebaut
war aber etwas anderes. Jede Bauform hatte auf A, B und C denselben Aufbau,
nur mit anderen Zahlen — genau das, was die Schülerin beim Üben gemerkt hat.

LEVELACHSE (Teil 2 der Schablone, wörtlich):

    Anzahl Glieder   zwei bis drei  →  drei bis vier  →  vier bis fünf
    Vorzeichen       alles positiv  →  ein Minus      →  mehrere Minus,
                                                         auch in Klammern

Beide Regler sind hier umgesetzt. Die Zahlen bleiben auf allen drei Stufen
klein — sie sind ausdrücklich NICHT die Levelachse.

Gesperrt bleiben: Anzahl Sorten (trennt BF1–BF3 von BF4 und BF9) und die
Schreibweise der Vorzeichen (das ist BF5 und BF6).
"""
from __future__ import annotations

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (fehler_eindeutig, kopfrechenbar, loesung_nicht_null,
                        symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, c, m, n, u, v, w, x, y, z = symbole("a b c m n u v w x y z")
VARS = {"a", "b", "c", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Fasse so weit wie möglich zusammen."

SORTE1 = [a, x, u, m, b]
SORTE2 = [b, y, v, n, c]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ── Glieder und ihre Schreibweise ─────────────────────────────────────────
#
# Ein Glied ist (Koeffizient, Basis, Stil). Der Stil bestimmt NUR die
# Schreibweise, nicht den Wert:
#
#   "+"   3a²          gewöhnlich
#   "-"   − 3a²        gewöhnlich, negativ
#   "K"   + (−3a²)     Vorzeichen in Klammern      — Bauform BF3
#   "F"   + (−3)a²     Faktor in Klammern          — Bauform BF5
#   "M"   − (−3a²)     Minus vor der Klammer       — Bauform BF6
#
# Die drei letzten sind der Kern von 4.3 und 4.5: derselbe Wert, drei
# Schreibweisen. Sie dürfen deshalb nicht als Level-Regler dienen — sonst
# schöbe der Regler die Bauformen ineinander.

def _teil(k, basis, stil, erstes: bool) -> str:
    betrag = zeige(abs(k) * basis) if abs(k) != 1 else zeige(basis)
    if stil == "K":
        kern = f"({MINUS}{betrag})"
        return kern if erstes else f"+ {kern}"
    if stil == "F":
        zahl = f"({MINUS}{abs(k)})" if k < 0 else f"({abs(k)})"
        rest = zeige(basis)
        return f"{zahl}{rest}" if erstes else f"+ {zahl}{rest}"
    if stil == "M":
        kern = f"({MINUS}{betrag})"
        return f"{MINUS} {kern}" if not erstes else f"{MINUS}{kern}"
    if k < 0:
        return f"{MINUS}{betrag}" if erstes else f"{MINUS} {betrag}"
    return betrag if erstes else f"+ {betrag}"


def zeige_glieder(glieder) -> str:
    return " ".join(_teil(k, basis, stil, i == 0)
                    for i, (k, basis, stil) in enumerate(glieder))


def wert(glieder):
    """Der Wert eines Glieds hängt NICHT vom Stil ab — ausser bei «M».

    «M» heisst «− (−3a²)», also plus 3a². Der Koeffizient wird darum positiv
    gespeichert und das doppelte Minus nur beim Anzeigen erzeugt.
    """
    gesamt = 0
    for k, basis, _ in glieder:
        gesamt += k * basis
    return gesamt


def beide_sorten_bleiben(p, g) -> bool:
    """Keine Sorte darf sich zufaellig ganz aufheben.

    `2a² + 4a − 2a²` ergibt 4a — die a² sind weg. Das ist ein legitimer
    Sonderfall, aber er gehoert in BF7, nicht als Zufallstreffer in eine
    gewoehnliche Bauform. Sonst sieht die Schuelerin eine Aufgabe, deren
    Ergebnis nichts mit dem Aufbau zu tun hat.
    """
    erwartet = g.get("sorten") or []
    if not erwartet:
        return True
    l = g["aufgabe"].loesung.expr
    return all(l.coeff(bs) != 0 for bs in erwartet)


def bau(glieder, fehler, schritte, tipps, loesung=None, loesung_text=None,
        sorten=None):
    l = loesung if loesung is not None else wert(glieder)
    return {"frage": zeige_glieder(glieder),
            "loesung_text": loesung_text or zeige(l),
            "sorten": sorten or [],
            "glieder": glieder,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.ZUSAMMENGEFASST,
                               fehlerkatalog=fehler),
            "schritte": schritte, "tipps": tipps}


TIPPS = [
    "Gleichartig sind nur Terme mit genau denselben Variablen und denselben "
    "Hochzahlen.",
    "Löse zuerst alle Doppelzeichen auf und sortiere dann nach Sorten.",
    "Rechne jede Sorte für sich zusammen — verschiedene Sorten bleiben "
    "nebeneinander stehen.",
]


def schritte_standard(frage, loesung):
    return [("Alle Glieder mit ihrem Vorzeichen abschreiben", frage),
            ("Gleichartige suchen", "gleiche Variablen, gleiche Hochzahlen"),
            ("Zahlen zusammenrechnen", zeige(loesung))]


# ── Die Levelachse ────────────────────────────────────────────────────────
#
# Ein Muster ist eine Zeichenkette: ein Zeichen pro Glied. Daraus entsteht
# die Struktur der Aufgabe. Level A, B und C bekommen VERSCHIEDENE Muster —
# das ist der ganze Punkt.

MUSTER = {
    "A": ["++", "+++"],                       # zwei bis drei, alles positiv
    "B": ["+-+", "++-", "+-++"],              # drei bis vier, ein Minus
    "C": ["+--+", "+-+-", "+--++", "+-+--"],  # vier bis fünf, mehrere Minus
}

#: Dieselbe Achse, aber mit Klammerschreibweise auf C — «auch in Klammern»
#: aus Teil 2 der Schablone.
MUSTER_K = {
    "A": ["+K", "++"],
    "B": ["+K+", "+-K"],
    "C": ["+K+K", "+-K+", "+KK+"],
}

ZAHLEN = {"A": [2, 3, 4], "B": [2, 3, 4, 5], "C": [2, 3, 4, 5, 6]}


def glieder_aus(muster, zahlen, basis, rng_werte):
    """Muster + Zahlenvorrat -> Liste von Gliedern.

    `rng_werte` ist eine feste Liste, aus der die Koeffizienten der Reihe
    nach genommen werden. So bleibt die Erzeugung deterministisch prüfbar.
    """
    glieder = []
    for i, zeichen in enumerate(muster):
        k = zahlen[i % len(zahlen)]
        if zeichen in "-K":
            k = -k
        stil = zeichen if zeichen in "KFM" else ("+" if k > 0 else "-")
        glieder.append((k, basis, stil))
    return glieder


# ══════════════════════════════════════════════════════════════════════════
# Die zwölf Bauformen
# ══════════════════════════════════════════════════════════════════════════

def _koeffs(p, anzahl):
    """Koeffizienten aus dem Vorrat, rotiert — Zahlen sind nicht die Achse."""
    vorrat = p["zahlen"]
    return [vorrat[(i * 2 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]


def bf1(p):
    v1, muster = p["var"], p["muster"]
    basis = v1 ** 2
    glieder = glieder_aus(muster, _koeffs(p, len(muster)), basis, None)
    l = wert(glieder)
    anzahl = len(muster)
    return bau(glieder, [
        F("hochzahlen_addiert", v1 ** (2 * anzahl),
          f"Beim Addieren wird gezählt: {anzahl} Stück {zeige(basis)} ergeben "
          f"{anzahl}{zeige(basis)}. Die Hochzahl bleibt."),
        F("hochzahl_verloren", sum(k for k, _, _ in glieder) * v1,
          "Die Hochzahl bleibt beim Zusammenfassen stehen."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS)


BF1 = Bauform("BF1", "Gleiche Potenz mehrfach",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf1, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf2(p):
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    basis = v1 * v2
    glieder = glieder_aus(muster, _koeffs(p, len(muster)), basis, None)
    l = wert(glieder)
    return bau(glieder, [
        F("faktoren_multipliziert", sum(k for k, _, _ in glieder) * (v1 * v2) ** 2,
          f"{zeige(basis)} bleibt {zeige(basis)} — nur die Zahlen davor werden "
          f"verrechnet."),
        F("nur_erste_zwei",
          (glieder[0][0] + glieder[1][0]) * basis,
          "Alle Glieder gehören zusammengefasst, nicht nur die ersten beiden."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS)


BF2 = Bauform("BF2", "Produkt als Term",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf2, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                       symbole_verschieden("var", "var2")])


def bf3(p):
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    basis = v1 ** 2 * v2
    glieder = glieder_aus(muster, _koeffs(p, len(muster)), basis, None)
    l = wert(glieder)
    # Was herauskommt, wenn die Klammer-Vorzeichen übersehen werden
    falsch = sum(abs(k) * basis for k, _, s in glieder if s == "K") \
        + sum(k * basis for k, _, s in glieder if s != "K")
    return bau(glieder, [
        F("klammer_vorzeichen", falsch,
          f"+ ({MINUS}…) ist dasselbe wie {MINUS}… — das Vorzeichen in der "
          f"Klammer gilt."),
        F("hochzahlen_addiert", sum(k for k, _, _ in glieder) * v1 ** 2 * v2 ** 2,
          "Beim Zusammenfassen ändern sich die Hochzahlen nicht."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS)


BF3 = Bauform("BF3", "Negative Terme in Klammern",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "muster": MUSTER_K[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf3, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                       symbole_verschieden("var", "var2")])


def bf4(p):
    v1, muster = p["var"], p["muster"]
    koeff = _koeffs(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = koeff[i]
        if zeichen in "-K":
            k = -k
        basis = v1 ** 2 if i % 2 == 0 else v1
        stil = zeichen if zeichen in "KFM" else ("+" if k > 0 else "-")
        glieder.append((k, basis, stil))
    l = wert(glieder)
    quadrate = sum(k for k, bs, _ in glieder if bs == v1 ** 2)
    einfache = sum(k for k, bs, _ in glieder if bs == v1)
    return bau(glieder, [
        F("sorten_gemischt", (quadrate + einfache) * v1 ** 3,
          f"{zeige(v1**2)} und {zeige(v1)} sind verschiedene Sorten — sie "
          f"lassen sich nicht zusammenzählen."),
        F("nur_quadrate", quadrate * v1 ** 2,
          f"Auch die {zeige(v1)}-Glieder werden zusammengefasst."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS,
       loesung_text=zeige_summe(quadrate * v1 ** 2, einfache * v1),
       sorten=[v1 ** 2, v1])


BF4 = Bauform("BF4", "Zwei Sorten, gemischt",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf4, filter=[kopfrechenbar, fehler_eindeutig,
                       loesung_nicht_null, beide_sorten_bleiben])


def bf5(p):
    v1, anzahl = p["var"], p["anzahl"]
    k = p["zahl"]
    #: Drei Schreibweisen für dasselbe: −3m, (−3)m, −3m
    stile = ["-", "F", "-", "F", "-"][:anzahl]
    glieder = [(-k, v1, s) for s in stile]
    l = wert(glieder)
    return bau(glieder, [
        F("klammer_positiv", (-k * (anzahl - stile.count("F"))
                              + k * stile.count("F")) * v1,
          f"({MINUS}{k}){zeige(v1)} ist dasselbe wie {MINUS}{k}{zeige(v1)} — "
          f"die Klammer ändert nichts am Vorzeichen."),
        F("eines_vergessen", -k * (anzahl - 1) * v1,
          "Alle Glieder zählen, auch die in Klammerschreibweise."),
    ], [("Schreibweisen angleichen",
         f"({MINUS}{k}){zeige(v1)} ist {MINUS}{k}{zeige(v1)}"),
        ("Zusammenzählen", f"{anzahl} Stück {MINUS}{k}{zeige(v1)}"),
        ("Ergebnis", zeige(l))], TIPPS)


BF5 = Bauform("BF5", "Drei Schreibweisen für dasselbe",
    bereiche={"A": {"var": SORTE1, "anzahl": [2], "zahl": [2, 3]},
              "B": {"var": SORTE1, "anzahl": [3], "zahl": [2, 3, 4]},
              "C": {"var": SORTE1, "anzahl": [4, 5], "zahl": [2, 3, 4]}},
    bauen=bf5, filter=[kopfrechenbar, fehler_eindeutig])


def bf6(p):
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    koeff = _koeffs(p, anzahl)
    basis = v1 * v2
    #: Mindestens ein «M»: − (−8ab). Das ist der Kern der Bauform.
    stile = ["M", "+", "M", "-", "M"][:anzahl]
    glieder = []
    for i, s in enumerate(stile):
        k = koeff[i]
        glieder.append((-k if s == "-" else k, basis, s))
    l = wert(glieder)
    doppelminus_falsch = sum(
        (-k if s == "M" else k) * basis for k, _, s in glieder)
    return bau(glieder, [
        F("doppelminus", doppelminus_falsch,
          f"Minus mal Minus gibt Plus: {MINUS}({MINUS}{zeige(basis)}) wird "
          f"+{zeige(basis)}."),
        F("nur_erstes", glieder[0][0] * basis,
          "Alle Glieder gehören zusammengefasst."),
    ], [("Doppelzeichen auflösen",
         f"{MINUS}({MINUS}…) wird +…"),
        ("Zusammenzählen", zeige(l))], TIPPS)


BF6 = Bauform("BF6", "Minus vor einer Klammer mitten im Term",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [2],
                    "zahlen": [ZAHLEN["A"]], "dreh": [0, 1]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [3],
                    "zahlen": [ZAHLEN["B"]], "dreh": [0, 1, 2]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [4, 5],
                    "zahlen": [ZAHLEN["C"]], "dreh": [0, 1, 2]}},
    bauen=bf6, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                       symbole_verschieden("var", "var2")])


def bf7(p):
    """Sonderfall: das Ergebnis ist null. Die Gliederzahl trägt das Level."""
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    k = p["zahl"]
    basis = v1 ** 2 if p["potenz"] else v1 * v2
    if anzahl == 2:
        glieder = [(k, basis, "+"), (-k, basis, "-")]
    elif anzahl == 3:
        glieder = [(k, basis, "+"), (k + 1, basis, "+"), (-(2 * k + 1), basis, "-")]
    else:
        zweite = v1 * v2 if p["potenz"] else v1
        glieder = [(k, basis, "+"), (k + 1, zweite, "+"),
                   (-k, basis, "-"), (-(k + 1), zweite, "-")]
    return bau(glieder, [
        F("nicht_null", sum(abs(k_) for k_, _, _ in glieder) * basis,
          "Die Vorzeichen zählen mit — hier heben sich alle Glieder auf."),
    ], [("Sorten sortieren", "gleiche Basis zusammen"),
        ("Zusammenzählen", "die Zahlen ergeben null"),
        ("Ergebnis", "0")], TIPPS, loesung=0)


BF7 = Bauform("BF7", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [2],
                    "zahl": [2, 3, 4], "potenz": [True, False]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [3],
                    "zahl": [2, 3, 4], "potenz": [True, False]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [4],
                    "zahl": [2, 3, 4], "potenz": [True, False]}},
    bauen=bf7, filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf8(p):
    """Sonderfall: der Koeffizient wird eins."""
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    k = p["zahl"]
    basis = v1 ** 2 if p["potenz"] else v1 * v2
    if anzahl == 2:
        glieder = [(k + 1, basis, "+"), (-k, basis, "-")]
    elif anzahl == 3:
        glieder = [(k + 2, basis, "+"), (-k, basis, "-"), (-1, basis, "-")]
    else:
        zweite = v1 * v2 if p["potenz"] else v1
        glieder = [(k + 1, basis, "+"), (k, zweite, "+"),
                   (-k, basis, "-"), (-k, zweite, "-")]
    l = wert(glieder)
    return bau(glieder, [
        F("null_geschrieben", 0,
          f"{k+1} minus {k} ist eins, nicht null — geschrieben wird "
          f"{zeige(basis)}."),
    ], [("Zahlen verrechnen", "die Differenz ist 1"),
        ("Eins wird nicht geschrieben", zeige(l))], TIPPS)


BF8 = Bauform("BF8", "Sonderfall: der Koeffizient wird eins",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "anzahl": [2],
                    "zahl": [3, 4, 5], "potenz": [True, False]},
              "B": {"var": SORTE1, "var2": SORTE2, "anzahl": [3],
                    "zahl": [3, 4, 5], "potenz": [True, False]},
              "C": {"var": SORTE1, "var2": SORTE2, "anzahl": [4],
                    "zahl": [3, 4, 5], "potenz": [True, False]}},
    bauen=bf8, filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf9(p):
    """Sonderfall: nichts lässt sich zusammenfassen.

    Ohne diese Bauform lernt der Schüler, dass am Schluss immer etwas
    Kürzeres steht — das ist die wichtigste Ergänzung der neuen Fassung.
    """
    v1, v2 = p["var"], p["var2"]
    muster = p["muster"]
    basen = [v1 ** 2, v2 ** 2, v1 * v2, v1, v2][:len(muster)]
    koeff = _koeffs(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen == "-" else koeff[i]
        glieder.append((k, basen[i], "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, [
        F("zusammengezogen", sum(k for k, _, _ in glieder) * basen[0],
          "Diese Glieder sind nicht gleichartig — der Term ist bereits die "
          "Antwort."),
    ], [("Sorten vergleichen", "alle Basen sind verschieden"),
        ("Ergebnis", "der Term bleibt, wie er ist")], TIPPS,
       loesung_text=zeige_glieder(glieder))


BF9 = Bauform("BF9", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2,
                   "muster": [mm for mm in MUSTER[lv] if len(mm) <= 5],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf9, filter=[kopfrechenbar, fehler_eindeutig,
                       symbole_verschieden("var", "var2")])


def bf10(p):
    v1, muster = p["var"], p["muster"]
    koeff = _koeffs(p, len(muster))
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen in "-K" else koeff[i]
        basis = v1 ** 2 if i % 2 == 0 else v1
        glieder.append((k, basis, "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, [
        F("sorten_gemischt", sum(k for k, _, _ in glieder) * v1 ** 3,
          f"{zeige(v1**2)} und {zeige(v1)} sind verschiedene Sorten."),
        F("nur_einfache", sum(k for k, bs, _ in glieder if bs == v1) * v1,
          f"Auch die {zeige(v1**2)}-Glieder bleiben stehen."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS,
       loesung_text=zeige_summe(
           sum(k for k, bs, _ in glieder if bs == v1 ** 2) * v1 ** 2,
           sum(k for k, bs, _ in glieder if bs == v1) * v1),
       sorten=[v1 ** 2, v1])


BF10 = Bauform("BF10", "Potenz und einfache Variable nebeneinander",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf10, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                        beide_sorten_bleiben])


def bf11(p):
    v1, muster = p["var"], p["muster"]
    koeff = _koeffs(p, len(muster))
    basis = v1 ** 2
    #: Das erste Glied ist immer negativ — das macht die Bauform aus.
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
        F("hochzahlen_addiert", sum(k for k, _, _ in glieder) * v1 ** (2 * len(muster)),
          "Beim Zusammenfassen bleibt die Hochzahl gleich."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS)


BF11 = Bauform("BF11", "Minuszeichen am Anfang",
    bereiche={lv: {"var": SORTE1, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf11, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null])


def bf12(p):
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    koeff = _koeffs(p, len(muster))
    #: a²b und ab² sehen fast gleich aus und sind verschieden.
    basen = [v1 ** 2 * v2, v1 * v2 ** 2]
    glieder = []
    for i, zeichen in enumerate(muster):
        k = -koeff[i] if zeichen in "-K" else koeff[i]
        glieder.append((k, basen[i % 2], "+" if k > 0 else "-"))
    l = wert(glieder)
    return bau(glieder, [
        F("vertauscht_gleichgesetzt", sum(k for k, _, _ in glieder) * basen[0],
          f"{zeige(basen[0])} und {zeige(basen[1])} sind verschieden — schau "
          f"auf die Hochzahlen."),
        F("nur_erste_sorte",
          sum(k for k, bs, _ in glieder if bs == basen[0]) * basen[0],
          "Auch die zweite Sorte bleibt stehen."),
    ], schritte_standard(zeige_glieder(glieder), l), TIPPS,
       loesung_text=zeige_summe(
           sum(k for k, bs, _ in glieder if bs == basen[0]) * basen[0],
           sum(k for k, bs, _ in glieder if bs == basen[1]) * basen[1]),
       sorten=basen)


BF12 = Bauform("BF12", "Potenz und Produkt kombiniert",
    bereiche={lv: {"var": SORTE1, "var2": SORTE2, "muster": MUSTER[lv],
                   "zahlen": [ZAHLEN[lv]], "dreh": [0, 1, 2]}
              for lv in ("A", "B", "C")},
    bauen=bf12, filter=[kopfrechenbar, fehler_eindeutig, loesung_nicht_null,
                        symbole_verschieden("var", "var2"),
                        beide_sorten_bleiben])


S16 = Schablone(
    nr="S16", titel="Gleichartige Terme zusammenfassen",
    lektionen="4.2 – 4.6 · 4.8", erhebung="2a",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Gleichartig sind nur Terme mit genau denselben Variablen und "
              "denselben Hochzahlen. Beim Zusammenfassen werden ihre Zahlen "
              "addiert — die Variablen bleiben unverändert."),
)
