# -*- coding: utf-8 -*-
"""
K1 · Teil 1 — Lektionen 1.1 bis 1.6, jede mit EIGENER Schablone

    S1a  1.1  Positive und negative Zahlen verstehen   Gegenzahl von −7  →  7
    S1b  1.2  Zahlen auf der Zahlengeraden            −3, 5 nach rechts →  2
    S1c  1.3  Vorzeichen und Operationszeichen        −(+7)             → −7
    S1d  1.4  Strich- und Punktoperatoren erkennen    6 · 3             → 18
    S2a  1.5  Addition mit positiven Zahlen           7 + 5             → 12
    S2b  1.6  Subtraktion mit positiven Zahlen        12 − 4            →  8

WARUM SECHS SCHABLONEN UND NICHT ZWEI
-------------------------------------
Der erste Anlauf fasste 1.1 bis 1.4 in eine Schablone und 1.5 mit 1.6 in
eine zweite. Ergebnis: in der Lektion «Subtraktion mit positiven Zahlen»
standen Additionsaufgaben, und alle vier Lektionen am Anfang zeigten
dieselbe Aufgabenart. Das ist genau der Vorwurf, wegen dem Kapitel 1
überhaupt neu gebaut wird — und beim ersten Versuch habe ich ihn
wiederholt.

Vier Lektionen mit vier verschiedenen Titeln brauchen vier verschiedene
Aufgabenarten. Wenn im Titel «Subtraktion» steht, darf kein Pluszeichen
vorkommen.

EIN RECHENZEICHEN, NICHT DREI
-----------------------------
In einer Einstiegslektion steht EINE Operation. Ketten wie «7 + 3 + 4 − 2»
gehören nach 1.18 («Mehrere Strichoperationen»), nicht nach 1.5.

DIE LEVELACHSE SIND HIER DIE ZAHLEN
-----------------------------------
Sonst gilt: Level müssen sich im Aufbau unterscheiden, nicht in der Grösse
der Zahlen. Für Kapitel 1 und 2 ist das ausdrücklich anders — dort SIND die
Zahlen der Lernstoff. Der Aufbau bleibt gleich, weil er gleich bleiben
muss: eine Rechnung, zwei Zahlen.

    A   einstellig, kein Zehnerübergang     7 + 2
    B   mit Zehnerübergang                  7 + 5
    C   zweistellig                        24 + 17
"""
from __future__ import annotations

from sympy import Integer

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .schablone import Bauform, Schablone

VARS: set[str] = set()


def F(schluessel: str, wert, text: str) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(wert), text)


def _siebe(katalog, ziel: int):
    """Doppelte und wertgleiche Einträge entfernen.

    Bei ganzen Zahlen liegen die Fehlerkandidaten dicht beieinander. Ein
    Eintrag, der mit der Lösung zusammenfällt, würde eine richtige Antwort
    als Fehler diagnostizieren.
    """
    raus, gesehen = [], set()
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        wert = int(e)
        if wert == ziel or wert in gesehen:
            continue
        gesehen.add(wert)
        raus.append(f)
    return raus


def streuung(loesung: int):
    """Zusätzliche Fehlerwerte, die weit genug auseinanderliegen.

    Bei kleinen ganzen Zahlen fallen «eins zu viel» und «Zahl abgeschrieben»
    schnell auf denselben Wert; nach dem Sieben blieben dann weniger als
    fünf Einträge übrig. Diese Werte liegen garantiert daneben und sind
    untereinander verschieden.
    """
    return [
        F("um_drei", loesung + 3, "Rechne nochmals nach — das liegt daneben."),
        F("um_vier", loesung - 4, "Rechne nochmals nach — das liegt daneben."),
        F("um_fuenf", loesung + 5, "Rechne nochmals nach — das liegt daneben."),
        F("um_sechs", loesung - 6, "Rechne nochmals nach — das liegt daneben."),
        F("um_sieben", loesung + 7, "Rechne nochmals nach — das liegt daneben."),
    ]


def fertig(frage, loesung, katalog, schritte, tipps, anleitung=None):
    return {
        "anleitung": anleitung,
        "frage": frage,
        "loesung_text": str(loesung),
        "aufgabe": Aufgabe(loesung=Loesung.zahl(Integer(loesung)),
                           variablen=VARS, zielform=Zielform.BELIEBIG,
                           dezimal_stellen=None,
                           fehlerkatalog=_siebe(list(katalog)
                                                + streuung(loesung),
                                                loesung)),
        "schritte": schritte,
        "tipps": tipps,
    }


#: Zahlenvorräte je Stufe. Sie sind der einzige Unterschied zwischen den
#: Level — siehe Kopfkommentar.
EINSTELLIG = [2, 3, 4, 5, 6, 7]
KLEIN = [1, 2, 3, 4, 5, 6, 7, 8, 9]
ZWEISTELLIG = [11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 23, 24, 26, 27]

STUFEN = {"A": EINSTELLIG, "B": KLEIN, "C": ZWEISTELLIG}


# ══════════════════════════════════════════════════════════════════════════
#  1.1 · Positive und negative Zahlen verstehen
# ══════════════════════════════════════════════════════════════════════════
def bau_gegenzahl(zahl: int):
    """«Wie heisst die Gegenzahl von −7?»

    Die Gegenzahl ist der erste Begriff, den ein Schüler über negative
    Zahlen wirklich braucht: gleich weit von der Null entfernt, andere
    Seite. Ohne ihn ist alles Weitere Regelraten.
    """
    loesung = -zahl
    return fertig(
        f"{zahl}" if zahl > 0 else f"(−{abs(zahl)})",
        loesung,
        [F("zahl_abgeschrieben", zahl,
           "Die Gegenzahl liegt auf der ANDEREN Seite der Null."),
         F("null", 0, "Die Gegenzahl ist nicht null — sie ist gleich weit "
                      "von der Null entfernt, nur auf der anderen Seite."),
         F("um_eins_daneben", loesung + 1,
           "Die Entfernung zur Null bleibt genau gleich."),
         F("um_eins_daneben2", loesung - 1,
           "Die Entfernung zur Null bleibt genau gleich."),
         F("verdoppelt", loesung * 2,
           "Die Zahl wird nicht verdoppelt, nur gespiegelt."),
         F("halbiert", loesung // 2 if loesung % 2 == 0 else None,
           "Die Zahl wird nicht halbiert, nur gespiegelt.")],
        [("Gleich weit von der Null, andere Seite", str(loesung))],
        ["Die Gegenzahl liegt gleich weit von der Null entfernt — nur auf "
         "der anderen Seite.",
         "Aus plus wird minus und aus minus wird plus. Die Zahl selbst "
         "bleibt.", ""],
        anleitung="Wie heisst die Gegenzahl dieser Zahl?")


def _gegenzahl(p):
    zahl = p["zahl"] * (1 if p["vz"] == "+" else -1)
    return bau_gegenzahl(zahl)


BEREICH_11 = {lv: {"zahl": vorrat, "vz": ["+", "-"]}
              for lv, vorrat in STUFEN.items()}

S1a = Schablone(
    nr="S1a", titel="Positive und negative Zahlen verstehen",
    lektionen="1.1", erhebung="",
    anleitung="Wie heisst die Gegenzahl?",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Gegenzahl einer positiven Zahl",
                bereiche={lv: {**b, "vz": ["+"]} for lv, b in BEREICH_11.items()},
                bauen=_gegenzahl, filter=[fehler_eindeutig]),
        Bauform("BF2", "Gegenzahl einer negativen Zahl",
                bereiche={lv: {**b, "vz": ["-"]} for lv, b in BEREICH_11.items()},
                bauen=_gegenzahl, filter=[fehler_eindeutig]),
    ],
    kernidee=("Jede Zahl hat eine Gegenzahl: gleich weit von der Null "
              "entfernt, aber auf der anderen Seite."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.2 · Zahlen auf der Zahlengeraden
# ══════════════════════════════════════════════════════════════════════════
def bau_zahlengerade(start: int, schritte_anzahl: int, nach_rechts: bool):
    """«Starte bei −3 und geh 5 Schritte nach rechts.»

    Die Zahlengerade ist das Bild, auf das später jede Vorzeichenregel
    zurückgeführt wird. Wer hier sicher ist, muss die Regeln nicht auswendig
    lernen — er kann sie nachzählen.
    """
    loesung = start + schritte_anzahl if nach_rechts else start - schritte_anzahl
    richtung = "nach rechts" if nach_rechts else "nach links"
    zeig_start = str(start) if start >= 0 else f"(−{abs(start)})"

    return fertig(
        zeig_start, loesung,
        [F("falsche_richtung", start - schritte_anzahl if nach_rechts
           else start + schritte_anzahl,
           f"«{richtung}» heisst: {'grösser' if nach_rechts else 'kleiner'} "
           f"werden."),
         F("start_vergessen", schritte_anzahl if nach_rechts else -schritte_anzahl,
           "Die Schritte werden vom Startpunkt aus gezählt."),
         F("nur_start", start, "Die Schritte fehlen."),
         F("einen_zu_weit", loesung + 1, "Ein Schritt zu viel."),
         F("einen_zu_wenig", loesung - 1, "Ein Schritt zu wenig."),
         F("gegenzahl", -loesung, "Das Vorzeichen stimmt nicht.")],
        [(f"Bei {zeig_start} starten", ""),
         (f"{schritte_anzahl} Schritte {richtung}", str(loesung))],
        ["Auf der Zahlengeraden geht rechts nach oben, links nach unten.",
         "Zähl die Schritte einzeln — über die Null hinweg zählt sie mit.",
         ""],
        anleitung=(f"Geh von dieser Zahl aus {schritte_anzahl} Schritte "
                   f"{richtung}. Wo kommst du heraus?"))


def _zahlengerade(p):
    start = p["start"] * (1 if p["vz"] == "+" else -1)
    return bau_zahlengerade(start, p["schritte"], p["richtung"] == "rechts")


BEREICH_12 = {lv: {"start": vorrat, "schritte": vorrat,
                   "vz": ["+", "-"], "richtung": ["rechts", "links"]}
              for lv, vorrat in STUFEN.items()}

S1b = Schablone(
    nr="S1b", titel="Zahlen auf der Zahlengeraden",
    lektionen="1.2", erhebung="",
    anleitung="Wo kommst du heraus?",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Von einer positiven Zahl nach rechts",
                bereiche={lv: {**b, "vz": ["+"], "richtung": ["rechts"]}
                          for lv, b in BEREICH_12.items()},
                bauen=_zahlengerade, filter=[fehler_eindeutig]),
        Bauform("BF2", "Von einer positiven Zahl nach links",
                bereiche={lv: {**b, "vz": ["+"], "richtung": ["links"]}
                          for lv, b in BEREICH_12.items()},
                bauen=_zahlengerade, filter=[fehler_eindeutig]),
        Bauform("BF3", "Von einer negativen Zahl nach rechts",
                bereiche={lv: {**b, "vz": ["-"], "richtung": ["rechts"]}
                          for lv, b in BEREICH_12.items()},
                bauen=_zahlengerade, filter=[fehler_eindeutig]),
        Bauform("BF4", "Von einer negativen Zahl nach links",
                bereiche={lv: {**b, "vz": ["-"], "richtung": ["links"]}
                          for lv, b in BEREICH_12.items()},
                bauen=_zahlengerade, filter=[fehler_eindeutig]),
    ],
    kernidee=("Auf der Zahlengeraden liegt rechts das Grössere. Nach rechts "
              "gehen heisst grösser werden, nach links kleiner."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.3 · Vorzeichen und Operationszeichen unterscheiden
# ══════════════════════════════════════════════════════════════════════════
def bau_vorzeichen(aussen: str, innen: str, zahl: int):
    """«−(+7)» — ein Vorzeichen vor einem Vorzeichen, nichts wird gerechnet.

    Das ist der Unterschied, um den es in dieser Lektion geht: das erste
    Zeichen sagt etwas über die Rechnung, das zweite gehört zur Zahl.
    """
    vz = (-1 if aussen == "-" else 1) * (-1 if innen == "-" else 1)
    loesung = vz * zahl
    frage = f"{aussen.replace('-', '−')}({innen.replace('-', '−')}{zahl})"

    return fertig(
        frage, loesung,
        [F("aussen_ignoriert", (-1 if innen == "-" else 1) * zahl,
           "Das Zeichen VOR der Klammer zählt mit."),
         F("innen_ignoriert", (-1 if aussen == "-" else 1) * zahl,
           "Das Zeichen IN der Klammer zählt mit."),
         F("immer_negativ", -abs(zahl) if loesung > 0 else abs(zahl),
           "Zwei gleiche Zeichen ergeben ein Plus, zwei verschiedene ein "
           "Minus."),
         F("null", 0, "Die Zeichen ändern die Zahl nicht zu null."),
         F("um_eins", loesung + 1,
           "Die Zahl selbst ändert sich nicht — nur ihr Vorzeichen."),
         F("verdoppelt", loesung * 2,
           "Die Zeichen werden nicht mit der Zahl multipliziert."),
         F("um_eins2", loesung - 1,
           "Die Zahl selbst ändert sich nicht — nur ihr Vorzeichen."),
         F("eins", 1, "Die Zeichen ergeben kein Ergebnis, sie stehen vor "
                      "der Zahl."),
         F("minus_eins", -1, "Die Zeichen ergeben kein Ergebnis, sie stehen "
                             "vor der Zahl."),
         F("zwei", 2, "Die Anzahl der Zeichen ist nicht das Ergebnis.")],
        [("Zeichen vor der Klammer", aussen.replace('-', '−')),
         ("Zeichen in der Klammer", innen.replace('-', '−')),
         ("Gleich ergibt Plus, verschieden ergibt Minus", str(loesung))],
        ["Das Zeichen vor der Klammer und das Zeichen an der Zahl werden "
         "zusammengefasst.",
         "Gleiche Zeichen ergeben ein Plus, verschiedene ein Minus.", ""])


def _vorzeichen(p):
    return bau_vorzeichen(p["aussen"], p["innen"], p["zahl"])


BEREICH_13 = {lv: {"zahl": vorrat, "aussen": ["+", "-"], "innen": ["+", "-"]}
              for lv, vorrat in STUFEN.items()}


def _fest(aussen=None, innen=None):
    return {lv: {**b,
                 **({"aussen": [aussen]} if aussen else {}),
                 **({"innen": [innen]} if innen else {})}
            for lv, b in BEREICH_13.items()}


S1c = Schablone(
    nr="S1c", titel="Vorzeichen und Operationszeichen unterscheiden",
    lektionen="1.3", erhebung="",
    anleitung="Schreib die Zahl ohne Klammern.",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Plus vor Plus", bereiche=_fest("+", "+"),
                bauen=_vorzeichen, filter=[fehler_eindeutig]),
        Bauform("BF2", "Plus vor Minus", bereiche=_fest("+", "-"),
                bauen=_vorzeichen, filter=[fehler_eindeutig]),
        Bauform("BF3", "Minus vor Plus", bereiche=_fest("-", "+"),
                bauen=_vorzeichen, filter=[fehler_eindeutig]),
        Bauform("BF4", "Minus vor Minus", bereiche=_fest("-", "-"),
                bauen=_vorzeichen, filter=[fehler_eindeutig]),
    ],
    kernidee=("Das Zeichen vor der Klammer sagt etwas über die Rechnung, "
              "das Zeichen an der Zahl gehört zur Zahl. Gleiche Zeichen "
              "ergeben ein Plus, verschiedene ein Minus."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.4 · Strich- und Punktoperatoren erkennen
# ══════════════════════════════════════════════════════════════════════════
def _kein_null(p, g) -> bool:
    """Null als Ergebnis ist am Anfang verwirrend und lehrt hier nichts."""
    return g["loesung_text"] != "0"


def bau_operator(a: int, b: int, zeichen: str):
    """Eine Rechnung, mal Strich, mal Punkt — und man muss erkennen, welche.

    «Erkennen» allein wäre keine Rechenaufgabe. Geübt wird es dadurch, dass
    beide Sorten gemischt kommen und man nicht raten kann: bei 6 · 3 und
    6 + 3 stehen dieselben Zahlen, das Ergebnis ist völlig verschieden.
    """
    if zeichen == "+":
        loesung, anzeige = a + b, "+"
    elif zeichen == "-":
        loesung, anzeige = a - b, "−"
    elif zeichen == "*":
        loesung, anzeige = a * b, "·"
    else:
        loesung, anzeige = a // b, ":"

    andere = {"+": a * b, "-": a * b, "*": a + b, "/": a - b}[zeichen]
    name = "Strichrechnung" if zeichen in "+-" else "Punktrechnung"

    return fertig(
        f"{a} {anzeige} {b}", loesung,
        [F("andere_rechenart", andere,
           f"Hier steht «{anzeige}» — das ist eine {name}."),
         F("summe_statt", a + b if zeichen != "+" else a - b,
           f"Schau nochmals auf das Rechenzeichen: {anzeige}"),
         F("produkt_statt", a * b if zeichen != "*" else a + b,
           f"Schau nochmals auf das Rechenzeichen: {anzeige}"),
         F("um_eins", loesung + 1, "Rechne nochmals nach."),
         F("um_eins2", loesung - 1, "Rechne nochmals nach."),
         F("nur_erste", a, "Die zweite Zahl fehlt.")],
        [(f"«{anzeige}» ist eine {name}", ""),
         ("Ausrechnen", str(loesung))],
        ["Punkt heisst mal oder geteilt, Strich heisst plus oder minus.",
         "Schau zuerst auf das Zeichen, dann rechne.", ""])


def _operator(p):
    a, b = p["a"], p["b"]
    if p["zeichen"] == "/":
        a = a * b                       # damit die Division aufgeht
    if p["zeichen"] == "-" and b > a:
        a, b = b, a                     # kein negatives Ergebnis in 1.4
    return bau_operator(a, b, p["zeichen"])


#: Der zweite Operand bleibt IMMER einstellig. Auf Level C sind sonst
#: «27 · 24» und «26 : 19» dabei — das ist kein Kopfrechnen mehr, und
#: ausserdem war der Vorrat dort leer, weil ZWEISTELLIG keine Zahl unter
#: zehn enthält. Der Generator brach mit «Cannot choose from an empty
#: sequence» ab.
BEREICH_14 = {lv: {"a": vorrat, "b": EINSTELLIG,
                   "zeichen": ["+", "-", "*", "/"]}
              for lv, vorrat in STUFEN.items()}

S1d = Schablone(
    nr="S1d", titel="Strich- und Punktoperatoren erkennen",
    lektionen="1.4", erhebung="",
    anleitung="Rechne aus. Achte auf das Rechenzeichen.",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Strichrechnung: plus",
                bereiche={lv: {**b, "zeichen": ["+"]}
                          for lv, b in BEREICH_14.items()},
                bauen=_operator, filter=[fehler_eindeutig]),
        Bauform("BF2", "Strichrechnung: minus",
                bereiche={lv: {**b, "zeichen": ["-"]}
                          for lv, b in BEREICH_14.items()},
                bauen=_operator, filter=[fehler_eindeutig, _kein_null]),
        Bauform("BF3", "Punktrechnung: mal",
                bereiche={lv: {**b, "zeichen": ["*"]}
                          for lv, b in BEREICH_14.items()},
                bauen=_operator, filter=[fehler_eindeutig]),
        Bauform("BF4", "Punktrechnung: geteilt",
                bereiche={lv: {**b, "zeichen": ["/"]}
                          for lv, b in BEREICH_14.items()},
                bauen=_operator, filter=[fehler_eindeutig]),
    ],
    kernidee=("Punkt heisst mal oder geteilt, Strich heisst plus oder "
              "minus. Schau zuerst auf das Zeichen, dann rechne."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.5 · Addition mit positiven Zahlen   ·   1.6 · Subtraktion
# ══════════════════════════════════════════════════════════════════════════
def bau_strich(a: int, b: int, plus: bool):
    """EIN Rechenzeichen, zwei positive Zahlen, positives Ergebnis.

    Keine Ketten. «7 + 3 + 4 − 2» gehört nach 1.18, nicht hierher.
    """
    loesung = a + b if plus else a - b
    frage = f"{a} {'+' if plus else '−'} {b}"

    return fertig(
        frage, loesung,
        [F("andere_richtung", a - b if plus else a + b,
           f"Hier steht ein {'Plus' if plus else 'Minus'}."),
         F("um_eins", loesung + 1, "Eins zu viel. Rechne nochmals nach."),
         F("um_eins2", loesung - 1, "Eins zu wenig. Rechne nochmals nach."),
         F("um_zehn", loesung + 10,
           "Ein Zehner zu viel. Rechne Zehner und Einer getrennt."),
         F("um_zehn2", loesung - 10,
           "Ein Zehner zu wenig. Rechne Zehner und Einer getrennt."),
         F("nur_erste", a, "Die zweite Zahl fehlt."),
         F("nur_zweite", b, "Die erste Zahl fehlt."),
         F("mal_gerechnet", a * b, "Hier steht kein Malpunkt.")],
        [(f"{a} {'+' if plus else '−'} {b}", str(loesung))],
        ["Rechne die Zehner und die Einer getrennt, dann setz sie zusammen."
         if max(a, b) > 9 else
         "Zähl im Kopf weiter — oder stell dir die Zahlengerade vor.",
         "Bei einem Zehnerübergang: erst bis zum nächsten Zehner, dann "
         "weiter.", ""])


def _addition(p):
    return bau_strich(p["a"], p["b"], True)


def _subtraktion(p):
    a, b = p["a"], p["b"]
    if b > a:
        a, b = b, a          # in 1.6 gibt es noch keine negativen Ergebnisse
    return bau_strich(a, b, False)


BEREICH_STRICH = {"A": {"a": EINSTELLIG, "b": EINSTELLIG},
                  "B": {"a": KLEIN, "b": KLEIN},
                  "C": {"a": ZWEISTELLIG, "b": ZWEISTELLIG}}

S2a = Schablone(
    nr="S2a", titel="Addition mit positiven Zahlen",
    lektionen="1.5", erhebung="",
    anleitung="Rechne aus.",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Zwei Zahlen addieren", bereiche=BEREICH_STRICH,
                bauen=_addition, filter=[fehler_eindeutig, _kein_null]),
    ],
    kernidee=("Beim Addieren wird die Zahl grösser. Bei einem "
              "Zehnerübergang: erst bis zum nächsten Zehner, dann weiter."),
)

S2b = Schablone(
    nr="S2b", titel="Subtraktion mit positiven Zahlen",
    lektionen="1.6", erhebung="",
    anleitung="Rechne aus.",
    levelachse="Grösse der Zahlen",
    bauformen=[
        Bauform("BF1", "Zwei Zahlen subtrahieren", bereiche=BEREICH_STRICH,
                bauen=_subtraktion, filter=[fehler_eindeutig, _kein_null]),
    ],
    kernidee=("Beim Subtrahieren wird die Zahl kleiner. Die grössere Zahl "
              "steht vorne — negative Ergebnisse kommen erst später."),
)
