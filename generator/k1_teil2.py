# -*- coding: utf-8 -*-
"""
K1 · Teil 2 — Addieren und Subtrahieren mit negativen Zahlen
Lektionen 1.7 bis 1.9

    S3   «Rechne aus.»    (−4) + 7   →   3
                          (−4) + (−7) →  −11
                          5 − (−3)   →   8

Quelle für den Aufbau: die Lektionstitel im Netz. Sie geben eine feine
Staffelung vor, und genau die wird hier abgebildet:

    1.7  Addition positiver UND negativer Zahlen   (−4) + 7
    1.8  Addition ZWEIER negativer Zahlen          (−4) + (−7)
    1.9  Subtraktion mit negativen Zahlen          5 − (−3)

DIE DREI SIND NICHT DASSELBE, auch wenn sie sich für einen Erwachsenen so
anfühlen. Bei 1.7 wandert man auf der Zahlengeraden über die Null hinweg.
Bei 1.8 bleibt man auf der linken Seite und addiert Schulden. Bei 1.9
kippt ein Minus vor der Klammer die Rechenrichtung — das ist der Schritt,
an dem die meisten hängenbleiben. Jede Lektion bekommt darum eigene
Bauformen, statt alles in einen Topf zu werfen.

WAS VORHER DORT STAND
---------------------
Lektion 1.7 zeigte auf Level A «7 + 6» — zwei positive Zahlen, in einer
Lektion, deren Titel ausdrücklich negative Zahlen verspricht. Der Schüler
übt also nicht das, was er üben soll, und merkt beim nächsten Test nichts
davon. Genau diese Sorte Fehler haben die Testpersonen gemeldet.

LEVELACHSE: **Zahl der Glieder** — A zwei, B drei, C vier. Sichtbar an der
Aufgabe, auf allen Stufen derselbe Zahlenvorrat.
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .k1_teil1 import F, KLEIN, ZWEISTELLIG as MITTEL, _siebe
from .qualitaet import fehler_eindeutig
from .schablone import Bauform, Schablone

VARS: set[str] = set()
ANLEITUNG = "Rechne aus."

TIPPS = [
    "Stell dir die Zahlengerade vor: plus geht nach rechts, minus nach links.",
    "Minus vor einer Klammer dreht das Vorzeichen darin um: "
    "5 − (−3) heisst 5 + 3.",
    "",
]


def zeig(zahl: int) -> str:
    """Eine negative Zahl steht in Klammern — so wie im Lehrmittel.

    «7 + −4» schreibt niemand. «7 + (−4)» ist die übliche Form, und sie
    macht auch beim Lesen klar, dass das Minus zur Zahl gehört und nicht
    zum Rechenzeichen. Genau diese Unterscheidung ist Lektion 1.3.
    """
    return f"(−{abs(zahl)})" if zahl < 0 else str(zahl)


def bau(zahlen: list[int], zeichen: list[str]):
    loesung = zahlen[0]
    for zahl, z in zip(zahlen[1:], zeichen):
        loesung = loesung + zahl if z == "+" else loesung - zahl

    teile = [zeig(zahlen[0])]
    for zahl, z in zip(zahlen[1:], zeichen):
        teile += ["+" if z == "+" else "−", zeig(zahl)]
    frage = " ".join(teile)

    #: Der klassische Fehler: das Minus vor der Klammer wird als Rechenzeichen
    #: gelesen und das Vorzeichen der Zahl gleich mit — «5 − (−3) = 2».
    ohne_umkehr = zahlen[0]
    for zahl, z in zip(zahlen[1:], zeichen):
        ohne_umkehr = ohne_umkehr + abs(zahl) if z == "+" else ohne_umkehr - abs(zahl)

    #: Und der zweite: alle Vorzeichen ignoriert, alles addiert.
    alles_positiv = sum(abs(z) for z in zahlen)

    katalog = _siebe([
        F("vorzeichen_uebersehen", ohne_umkehr,
          "Ein Minus vor einer Klammer dreht das Vorzeichen darin um."),
        F("alles_addiert", alles_positiv,
          "Achte auf die Vorzeichen — nicht alles wird addiert."),
        F("gegenzahl", -loesung,
          "Das Vorzeichen des Ergebnisses stimmt nicht. Zähl auf der "
          "Zahlengeraden nach."),
        F("nur_erste_zahl", zahlen[0],
          "Der Rest der Rechnung fehlt."),
        F("eins_daneben", loesung + 1,
          "Eins zu viel. Rechne nochmals nach."),
        F("eins_zu_wenig", loesung - 1,
          "Eins zu wenig. Rechne nochmals nach."),
        F("betraege_subtrahiert", abs(zahlen[0]) - sum(abs(z) for z in zahlen[1:]),
          "Die Vorzeichen gehören zu den Zahlen und dürfen nicht "
          "weggelassen werden."),
        F("letzte_vergessen",
          (loesung - zahlen[-1] if zeichen[-1] == "+" else loesung + zahlen[-1]),
          "Die letzte Zahl wurde nicht mitgerechnet."),
        F("um_zwei_daneben", loesung + 2,
          "Zwei zu viel. Zähl die Schritte auf der Zahlengeraden nochmals."),
        F("doppelt", loesung * 2 if loesung else 1,
          "Da wurde etwas doppelt gezählt."),
    ], loesung)

    schritte, stand = [], zahlen[0]
    for zahl, z in zip(zahlen[1:], zeichen):
        neu = stand + zahl if z == "+" else stand - zahl
        richtung = "nach rechts" if neu > stand else "nach links"
        schritte.append((f"{stand} {'+' if z == '+' else '−'} {zeig(zahl)}",
                         f"{abs(neu - stand)} Schritte {richtung} → {neu}"))
        stand = neu

    return {
        "frage": frage,
        "loesung_text": str(loesung),
        "aufgabe": Aufgabe(loesung=Loesung.zahl(Integer(loesung)),
                           variablen=VARS, zielform=Zielform.BELIEBIG,
                           dezimal_stellen=None, fehlerkatalog=katalog),
        "schritte": schritte,
        "tipps": TIPPS,
    }


BEREICHE = {lv: {"a": MITTEL, "b": KLEIN, "c": KLEIN, "d": KLEIN,
                 "anzahl": [n]}
            for lv, n in (("A", 2), ("B", 3), ("C", 4))}


def _nicht_null(p, g) -> bool:
    """Null als Ergebnis ist ein Sonderfall und gehoert BF11, nicht ueberall."""
    return g["loesung_text"] != "0"


def _handlich(p, g) -> bool:
    """Im Kopfrechenbereich bleiben — Kapitel 1 ist die Grundlage."""
    return abs(int(g["loesung_text"])) <= 40


STANDARD = [fehler_eindeutig, _nicht_null, _handlich]


def _zahlen(p, muster: list[int]):
    """muster: +1 fuer positiv, -1 fuer negativ, je Stelle."""
    roh = [p["a"], p["b"], p["c"], p["d"]][:p["anzahl"]]
    vz = (muster * 4)[:p["anzahl"]]
    return [z * v for z, v in zip(roh, vz)]


def _bf(nr, beschreibung, muster, zeichen_muster):
    def bauen(p):
        zahlen = _zahlen(p, muster)
        zeichen = list((zeichen_muster * 4)[:p["anzahl"] - 1])
        return bau(zahlen, zeichen)
    return Bauform(nr, beschreibung, bereiche=BEREICHE, bauen=bauen,
                   filter=STANDARD)


# ── 1.7 · Addition positiver UND negativer Zahlen ────────────────────────
BF1 = _bf("BF1", "Negative Zahl zuerst, dann plus", [-1, 1], "+")
BF2 = _bf("BF2", "Positive Zahl zuerst, dann plus eine negative", [1, -1], "+")
BF3 = _bf("BF3", "Abwechselnd positiv und negativ", [1, -1, 1, -1], "+")

# ── 1.8 · Addition ZWEIER negativer Zahlen ───────────────────────────────
BF4 = _bf("BF4", "Zwei negative Zahlen addieren", [-1, -1], "+")
BF5 = _bf("BF5", "Mehrere negative Zahlen addieren", [-1, -1, -1, -1], "+")

# ── 1.9 · Subtraktion mit negativen Zahlen ───────────────────────────────
BF6 = _bf("BF6", "Minus vor einer negativen Zahl", [1, -1], "-")
BF7 = _bf("BF7", "Negative Zahl minus positive", [-1, 1], "-")
BF8 = _bf("BF8", "Minus vor mehreren negativen Zahlen", [1, -1, -1, -1], "-")
BF9 = _bf("BF9", "Gemischt: plus und minus, mit negativen Zahlen",
          [1, -1, 1, -1], "+-")


# ── BF10 · Sonderfall: das Ergebnis ist negativ ──────────────────────────
def bf10(p):
    """Der Fall, der Anfänger am meisten irritiert: man rutscht unter null.

    Er kommt in den anderen Bauformen auch vor, aber zufällig. Hier ist er
    garantiert — wer ihn nie geübt hat, rechnet beim ersten Mal 3 − 8 = 5.
    """
    zahlen = _zahlen(p, [1, 1, 1, 1])
    zahlen[0] = min(zahlen[0], 5)
    zeichen = ["-"] * (p["anzahl"] - 1)
    return bau(zahlen, zeichen)


def _ergibt_negativ(p, g) -> bool:
    return int(g["loesung_text"]) < 0


BF10 = Bauform("BF10", "Sonderfall: das Ergebnis ist negativ",
    bereiche=BEREICHE, bauen=bf10,
    filter=[fehler_eindeutig, _ergibt_negativ, _handlich])


# ── BF11 · Sonderfall: das Ergebnis ist null ─────────────────────────────
def bf11(p):
    """(−7) + 7 = 0 — die Gegenzahl hebt auf. Steht in jedem Lehrmittel."""
    a = p["a"]
    if p["anzahl"] == 2:
        zahlen, zeichen = [-a, a], ["+"]
    elif p["anzahl"] == 3:
        zahlen, zeichen = [-a, p["b"], a - p["b"]], ["+", "+"]
    else:
        zahlen, zeichen = [-a, p["b"], a, -p["b"]], ["+", "+", "+"]
    return bau(zahlen, zeichen)


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


BF11 = Bauform("BF11", "Sonderfall: die Gegenzahl hebt auf",
    bereiche=BEREICHE, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_null])


# ── BF12 · Sonderfall: zwei Minuszeichen hintereinander ──────────────────
def bf12(p):
    """5 − (−3) − (−2) — das Minus vor der Klammer, mehrfach.

    Die reine Form des Gedankens aus Lektion 1.9, ohne Ablenkung durch
    positive Summanden.
    """
    zahlen = [p["a"]] + [-z for z in [p["b"], p["c"], p["d"]][:p["anzahl"] - 1]]
    zeichen = ["-"] * (p["anzahl"] - 1)
    return bau(zahlen, zeichen)


BF12 = Bauform("BF12", "Sonderfall: Minus vor Minus",
    bereiche=BEREICHE, bauen=bf12, filter=STANDARD)


S3 = Schablone(
    nr="S3", titel="Addieren und Subtrahieren mit negativen Zahlen",
    lektionen="1.7 – 1.9", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Zahl der Glieder",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Plus geht auf der Zahlengeraden nach rechts, minus nach "
              "links. Ein Minus vor einer Klammer dreht das Vorzeichen "
              "darin um."),
)
