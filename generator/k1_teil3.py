# -*- coding: utf-8 -*-
"""
K1 · Teil 3 — Mal, Geteilt und die Reihenfolge der Rechenarten
Lektionen 1.10 bis 1.20

    S4a  1.10  Multiplikation mit positiven Zahlen        6 · 7      →  42
    S4b  1.11  Multiplikation mit unterschiedlichen VZ    (−6) · 7   → −42
    S4c  1.12  Multiplikation zweier negativer Zahlen     (−6) · (−7) →  42
    S5a  1.13  Division mit positiven Zahlen              42 : 7     →   6
    S5b  1.14  Division mit unterschiedlichen VZ          (−42) : 7  →  −6
    S5c  1.15  Division zweier negativer Zahlen           (−42) : (−7) →  6
    S6a  1.16  Punkt vor Strich ohne Klammern             3 + 4 · 5  →  23
    S6b  1.17  Mehrere Punktoperationen                   2 · 6 : 4  →   3
    S6c  1.18  Mehrere Strichoperationen                  9 − 4 + 3  →   8
    S6d  1.19  Gemischte Punkt- und Strichoperationen     8 − 2 · 3 + 5
    M1   1.20  Gemischt: alles aus Kapitel 1              alle Formen

WARUM ELF SCHABLONEN
--------------------
Weil es elf Lektionen mit elf verschiedenen Titeln sind. Der erste Anlauf
fasste sie zu dreien zusammen, und dann stand in «Multiplikation zweier
negativer Zahlen» eine Aufgabe mit einer positiven — der Schüler übt nicht,
was der Titel verspricht, und merkt es beim nächsten Test.

Die Staffelung 1.10 → 1.11 → 1.12 ist kein Zufall des Lehrmittels. Erst
das Einmaleins, dann ein Vorzeichen, dann zwei: jede Stufe fügt genau eine
Schwierigkeit hinzu. Wer 1.12 nicht kann, scheitert oft schon an 1.11, und
dorthin schickt ihn die Lückensuche.

DIE LEVELACHSE SIND HIER DIE ZAHLEN — wie in Teil 1 und aus demselben
Grund: eine Multiplikation bleibt eine Multiplikation. Die Struktur kann
sich nicht ändern, ohne die Lektion zu verlassen.

    A   kleines Einmaleins                2 · 6
    B   grosses Einmaleins                7 · 8
    C   über hundert / zweistellig       12 · 7
"""
from __future__ import annotations

from .k1_teil1 import EINSTELLIG, F, ZWEISTELLIG, fertig
from .qualitaet import fehler_eindeutig
from .schablone import Bauform, Schablone

VARS: set[str] = set()


def _kopfrechenbar(p, g) -> bool:
    """Das Ergebnis muss im Kopf zu schaffen sein.

    Kapitel 1 ist Kopfrechnen ohne Taschenrechner. «13 · 12 · 15 = 2340» ist
    rechnerisch richtig und didaktisch wertlos: geübt wird dann Stellenwert-
    verschieben, nicht die Reihenfolge der Rechenarten. Die Grenze liegt bei
    dreihundert — darüber wird die Ziehung verworfen und neu gewürfelt.
    """
    return abs(int(g["loesung_text"])) <= 300

KLEIN = [2, 3, 4, 5, 6]
GROSS = [4, 5, 6, 7, 8, 9]
STUFEN = {"A": KLEIN, "B": GROSS, "C": [11, 12, 13, 14, 15]}


def zeig(zahl: int) -> str:
    """Negative Zahlen stehen in Klammern — «6 · (−7)», nicht «6 · −7»."""
    return f"(−{abs(zahl)})" if zahl < 0 else str(zahl)


# ══════════════════════════════════════════════════════════════════════════
#  1.10 – 1.12 · Multiplikation
# ══════════════════════════════════════════════════════════════════════════
def bau_mal(a: int, b: int):
    loesung = a * b
    return fertig(
        f"{zeig(a)} · {zeig(b)}", loesung,
        [F("vorzeichen_falsch", -loesung,
           "Minus mal Minus ergibt Plus, Minus mal Plus ergibt Minus."),
         F("addiert", a + b, "Hier steht ein Malpunkt, kein Plus."),
         F("betrag", abs(a) * abs(b) if loesung < 0 else -abs(a) * abs(b),
           "Die Vorzeichen gehören zur Rechnung."),
         F("um_eins", loesung + abs(a),
           f"Ein {abs(a)}er zu viel. Zähl die Reihe nochmals."),
         F("um_eins2", loesung - abs(a),
           f"Ein {abs(a)}er zu wenig. Zähl die Reihe nochmals."),
         F("subtrahiert", a - b, "Hier steht ein Malpunkt, kein Minus.")],
        [("Zahlen malnehmen", f"{abs(a)} · {abs(b)} = {abs(loesung)}"),
         ("Vorzeichen bestimmen",
          "gleich → Plus" if loesung > 0 else "verschieden → Minus"),
         ("Ergebnis", str(loesung))],
        ["Gleiche Vorzeichen ergeben ein Plus, verschiedene ein Minus.",
         "Rechne zuerst die Zahlen, dann bestimm das Vorzeichen.", ""])


def _mal(vz_a: int, vz_b: int):
    def bauen(p):
        return bau_mal(p["a"] * vz_a, p["b"] * vz_b)
    return bauen


BEREICH_MAL = {lv: {"a": v, "b": [x for x in v if x <= 9] or v}
               for lv, v in STUFEN.items()}


def _schablone_mal(nr, titel, lektion, vz_a, vz_b, kernidee):
    return Schablone(
        nr=nr, titel=titel, lektionen=lektion, erhebung="",
        anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
        bauformen=[Bauform("BF1", titel, bereiche=BEREICH_MAL,
                           bauen=_mal(vz_a, vz_b), filter=[fehler_eindeutig, _kopfrechenbar])],
        kernidee=kernidee)


S4a = _schablone_mal("S4a", "Multiplikation mit positiven Zahlen", "1.10",
                     1, 1,
                     "Malnehmen heisst: eine Zahl mehrfach addieren. "
                     "6 · 7 sind sieben Sechser.")
S4b = _schablone_mal("S4b", "Multiplikation mit unterschiedlichen Vorzeichen",
                     "1.11", -1, 1,
                     "Minus mal Plus ergibt Minus. Sieben Mal minus sechs "
                     "sind minus zweiundvierzig.")
S4c = _schablone_mal("S4c", "Multiplikation zweier negativer Zahlen", "1.12",
                     -1, -1,
                     "Minus mal Minus ergibt Plus. Das Minus vor der "
                     "Klammer dreht die ganze Rechnung um.")


# ══════════════════════════════════════════════════════════════════════════
#  1.13 – 1.15 · Division
# ══════════════════════════════════════════════════════════════════════════
def bau_geteilt(produkt: int, teiler: int):
    """Die Division geht immer auf — in Kapitel 1 gibt es noch keine Brüche."""
    loesung = produkt // teiler
    return fertig(
        f"{zeig(produkt)} : {zeig(teiler)}", loesung,
        [F("vorzeichen_falsch", -loesung,
           "Minus geteilt durch Minus ergibt Plus, Minus geteilt durch Plus "
           "ergibt Minus."),
         F("mal_gerechnet", produkt * teiler,
           "Hier steht ein Doppelpunkt, kein Malpunkt."),
         F("subtrahiert", produkt - teiler,
           "Hier steht ein Doppelpunkt, kein Minus."),
         F("um_eins", loesung + 1, "Rechne nochmals nach."),
         F("um_eins2", loesung - 1, "Rechne nochmals nach."),
         F("umgekehrt", teiler, "Die erste Zahl wird durch die zweite "
                                "geteilt, nicht umgekehrt.")],
        [("Zahlen teilen", f"{abs(produkt)} : {abs(teiler)} = {abs(loesung)}"),
         ("Vorzeichen bestimmen",
          "gleich → Plus" if loesung > 0 else "verschieden → Minus"),
         ("Ergebnis", str(loesung))],
        ["Frag dich: mal was ergibt die erste Zahl?",
         "Die Vorzeichenregel ist dieselbe wie beim Malnehmen: gleich ergibt "
         "Plus, verschieden ergibt Minus.", ""])


def _geteilt(vz_produkt: int, vz_teiler: int):
    def bauen(p):
        teiler = p["b"]
        produkt = teiler * p["a"]
        return bau_geteilt(produkt * vz_produkt, teiler * vz_teiler)
    return bauen


def _schablone_geteilt(nr, titel, lektion, vz_p, vz_t, kernidee):
    return Schablone(
        nr=nr, titel=titel, lektionen=lektion, erhebung="",
        anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
        bauformen=[Bauform("BF1", titel, bereiche=BEREICH_MAL,
                           bauen=_geteilt(vz_p, vz_t),
                           filter=[fehler_eindeutig, _kopfrechenbar])],
        kernidee=kernidee)


S5a = _schablone_geteilt("S5a", "Division mit positiven Zahlen", "1.13",
                         1, 1,
                         "Teilen ist die Umkehrung des Malnehmens: "
                         "42 : 7 fragt, mal wie viel sieben zweiundvierzig "
                         "ergibt.")
S5b = _schablone_geteilt("S5b", "Division mit unterschiedlichen Vorzeichen",
                         "1.14", -1, 1,
                         "Beim Teilen gilt dieselbe Vorzeichenregel wie beim "
                         "Malnehmen: verschieden ergibt Minus.")
S5c = _schablone_geteilt("S5c", "Division zweier negativer Zahlen", "1.15",
                         -1, -1,
                         "Minus geteilt durch Minus ergibt Plus — genau wie "
                         "beim Malnehmen.")


# ══════════════════════════════════════════════════════════════════════════
#  1.16 – 1.19 · Reihenfolge der Rechenarten
# ══════════════════════════════════════════════════════════════════════════
def bau_reihenfolge(text: str, loesung: int, falsch_links: int, tipp: str):
    return fertig(
        text, loesung,
        [F("von_links", falsch_links,
           "Punkt vor Strich: die Malrechnung kommt zuerst, egal wo sie "
           "steht."),
         F("um_eins", loesung + 1, "Rechne nochmals nach."),
         F("um_eins2", loesung - 1, "Rechne nochmals nach."),
         F("gegenzahl", -loesung, "Das Vorzeichen stimmt nicht."),
         F("um_zwei", loesung + 2, "Rechne nochmals nach."),
         F("um_drei", loesung - 3, "Rechne nochmals nach."),
         F("null", 0, "Rechne nochmals nach.")],
        [("Punkt zuerst", ""), ("Dann Strich", str(loesung))],
        [tipp,
         "Rechne die Punktrechnung aus und schreib sie als eine Zahl hin, "
         "dann bleibt eine einfache Strichrechnung übrig.", ""])


def _punkt_vor_strich(p):
    """3 + 4 · 5 — die Malrechnung hinten."""
    a, b, c = p["a"], p["b"], p["c"]
    return bau_reihenfolge(f"{a} + {b} · {c}", a + b * c, (a + b) * c,
                           "Punkt vor Strich: erst mal, dann plus.")


def _punkt_vorne(p):
    """4 · 5 + 3 — die Malrechnung vorne. Sieht leichter aus, ist es auch —
    darum eine eigene Bauform: der Fehler passiert bei der anderen Form."""
    a, b, c = p["a"], p["b"], p["c"]
    return bau_reihenfolge(f"{a} · {b} + {c}", a * b + c, a * (b + c),
                           "Punkt vor Strich: erst mal, dann plus.")


def _punkt_minus(p):
    a, b, c = p["a"], p["b"], p["c"]
    return bau_reihenfolge(f"{a} − {b} · {c}", a - b * c, (a - b) * c,
                           "Punkt vor Strich: erst mal, dann minus.")


BEREICH_REIHE = {lv: {"a": v, "b": [x for x in v if x <= 9] or v,
                      "c": [x for x in v if x <= 9] or v}
                 for lv, v in STUFEN.items()}

S6a = Schablone(
    nr="S6a", titel="Punkt vor Strich ohne Klammern", lektionen="1.16",
    erhebung="", anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Mal hinten", bereiche=BEREICH_REIHE,
                bauen=_punkt_vor_strich, filter=[fehler_eindeutig, _kopfrechenbar]),
        Bauform("BF2", "Mal vorne", bereiche=BEREICH_REIHE,
                bauen=_punkt_vorne, filter=[fehler_eindeutig, _kopfrechenbar]),
        Bauform("BF3", "Mal nach einem Minus", bereiche=BEREICH_REIHE,
                bauen=_punkt_minus, filter=[fehler_eindeutig, _kopfrechenbar]),
    ],
    kernidee=("Punkt vor Strich: Mal und Geteilt kommen zuerst, egal wo sie "
              "stehen. Erst danach Plus und Minus."),
)


def _zwei_punkt(p):
    """2 · 6 : 4 — zwei Punktrechnungen, von links nach rechts."""
    b, c = p["b"], p["c"]
    a = b * c
    return bau_reihenfolge(f"{a} : {b} · {c}", a // b * c, a // (b * c),
                           "Bei mehreren Punktrechnungen: von links nach "
                           "rechts.")


def _zwei_mal(p):
    #: Der dritte Faktor bleibt klein. Auf Level C liegt sonst JEDES
    #: Dreifachprodukt über dreihundert, der Filter verwirft alles, und die
    #: Ziehung gibt nach 300 Versuchen auf.
    a, b, c = p["a"], min(p["b"], 5), min(p["c"], 4)
    return bau_reihenfolge(f"{a} · {b} · {c}", a * b * c, a * b + c,
                           "Bei mehreren Malrechnungen ist die Reihenfolge "
                           "egal — das Ergebnis bleibt gleich.")


S6b = Schablone(
    nr="S6b", titel="Mehrere Punktoperationen", lektionen="1.17",
    erhebung="", anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Geteilt und mal", bereiche=BEREICH_REIHE,
                bauen=_zwei_punkt, filter=[fehler_eindeutig, _kopfrechenbar]),
        Bauform("BF2", "Zweimal mal", bereiche=BEREICH_REIHE,
                bauen=_zwei_mal, filter=[fehler_eindeutig, _kopfrechenbar]),
    ],
    kernidee=("Stehen nur Punktrechnungen da, wird von links nach rechts "
              "gerechnet."),
)


def _drei_strich(p):
    a, b, c = p["a"] + p["b"] + p["c"], p["b"], p["c"]
    return bau_reihenfolge(f"{a} − {b} + {c}", a - b + c, a - (b + c),
                           "Bei mehreren Strichrechnungen: von links nach "
                           "rechts.")


def _drei_strich2(p):
    a, b, c = p["a"] + p["b"] + p["c"], p["b"], p["c"]
    return bau_reihenfolge(f"{a} + {b} − {c}", a + b - c, a + (b - c) * 2,
                           "Bei mehreren Strichrechnungen: von links nach "
                           "rechts.")


S6c = Schablone(
    nr="S6c", titel="Mehrere Strichoperationen", lektionen="1.18",
    erhebung="", anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Minus, dann plus", bereiche=BEREICH_REIHE,
                bauen=_drei_strich, filter=[fehler_eindeutig, _kopfrechenbar]),
        Bauform("BF2", "Plus, dann minus", bereiche=BEREICH_REIHE,
                bauen=_drei_strich2, filter=[fehler_eindeutig, _kopfrechenbar]),
    ],
    kernidee=("Stehen nur Strichrechnungen da, wird von links nach rechts "
              "gerechnet. «9 − 4 + 3» ist nicht «9 − 7»."),
)


def _gemischt(p):
    """8 − 2 · 3 + 5 — Punkt in der Mitte, Strich aussen."""
    a, b, c, d = p["a"] + 10, p["b"], p["c"], p["a"]
    return bau_reihenfolge(f"{a} − {b} · {c} + {d}",
                           a - b * c + d, (a - b) * c + d,
                           "Punkt vor Strich, dann von links nach rechts.")


def _gemischt2(p):
    #: Gleicher Grund wie bei _zwei_mal: zwei Produkte plus Summe wachsen
    #: sonst über den Kopfrechenbereich hinaus.
    a, b, c, d = p["a"], min(p["b"], 5), min(p["c"], 5), 4
    return bau_reihenfolge(f"{a} · {b} + {c} · {d}",
                           a * b + c * d, a * (b + c) * d,
                           "Beide Malrechnungen zuerst, dann addieren.")


S6d = Schablone(
    nr="S6d", titel="Gemischte Punkt- und Strichoperationen", lektionen="1.19",
    erhebung="", anleitung="Rechne aus.", levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Punkt in der Mitte", bereiche=BEREICH_REIHE,
                bauen=_gemischt, filter=[fehler_eindeutig, _kopfrechenbar]),
        Bauform("BF2", "Zwei Malrechnungen, dazwischen ein Plus",
                bereiche=BEREICH_REIHE, bauen=_gemischt2,
                filter=[fehler_eindeutig, _kopfrechenbar]),
    ],
    kernidee=("Zuerst alle Punktrechnungen, dann die Strichrechnungen von "
              "links nach rechts."),
)
