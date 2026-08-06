# -*- coding: utf-8 -*-
"""
S11 · Division von Brüchen   (Lektion 2.10)

    «Rechne aus. Gib das Resultat in gekürzter Form an.»
    3/11 : 5/6      →   18/55
    2 : 3/5         →   10/3
    7/6 : 5         →   7/30

Quelle: Lehrmittel A, Kapitel 1.5, Seiten 53 und 54 — der blaue Kasten auf
Seite 53 gibt die Regel (mit dem Kehrwert malnehmen), dazu die Aufgaben 56
bis 62.

DER FEHLER, UM DEN ES GEHT: gestürzt wird der ZWEITE Bruch, nicht der
erste und nicht beide. Wer 3/4 : 2/5 rechnet und 4/3 · 2/5 bildet, hat den
falschen gestürzt; wer 4/3 · 5/2 bildet, hat beide gestürzt. Beide Fehler
stehen in jedem Katalog dieser Schablone, weil sie zusammen den grössten
Teil der Fehler an dieser Stelle ausmachen.

LEVELACHSE (Teil 2): **Zahl der Rechenzeichen** — A eines, B zwei, C drei.
Die Zahlenvorräte sind auf allen drei Stufen dieselben.

Warum nicht «wie gross die Zahlen werden»? Weil man das der Aufgabe nicht
ansieht. Dieselbe Lehre wie bei S8 und S10; dort steht die lange Fassung.

DIE REIHENFOLGE BEI MEHREREN ZEICHEN ist der eigentliche Inhalt von Level
B und C. Aufgabe 59 e im Lehrmittel zeigt genau das: 6/13 : 3/26 · 3/4 und
6/13 : 3/26 : 3/4 sind verschieden, und wer von rechts nach links rechnet,
bekommt etwas anderes heraus. Der Katalogeintrag «falsche_reihenfolge»
führt das vor.
"""
from __future__ import annotations

from sympy import Integer, Rational

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .s8_addition_subtraktion import F, br, als_text, _frage_gekuerzt
from .schablone import Bauform, Schablone

VARS: set[str] = set()
ANLEITUNG = "Rechne aus. Gib das Resultat in gekürzter Form an."

ZAEHLER = [1, 2, 3, 4, 5, 7]
NENNER = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
GANZE = [2, 3, 4, 5, 6, 8]

TIPPS = [
    "Durch einen Bruch teilen heisst: mit seinem Kehrwert malnehmen.",
    "Gestürzt wird der ZWEITE Bruch — der hinter dem Doppelpunkt.",
    "",
]


def _siebe(katalog, ziel: Rational):
    """Wertgleiche, doppelte und zu nahe Einträge entfernen.

    Zur Abstandsregel siehe S10: die Korrektur akzeptiert Dezimalantworten
    auf zwei Stellen, und zwei Werte, die näher als ein Hundertstel
    beieinanderliegen, lassen sich mit demselben Tastendruck treffen.
    """
    raus, gesehen = [], set()
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        wert = Rational(e)
        if wert == ziel or str(wert) in gesehen:
            continue
        if abs(float(wert) - float(ziel)) < 0.01:
            continue
        gesehen.add(str(wert))
        raus.append(f)
    return raus


def _rechne(glieder, zeichen) -> Rational:
    """Von LINKS nach rechts — genau darum geht es bei mehreren Zeichen."""
    wert = Rational(glieder[0][0], glieder[0][1])
    for (z, n), vz in zip(glieder[1:], zeichen):
        wert = wert * Rational(z, n) if vz == "*" else wert / Rational(z, n)
    return wert


def _von_rechts(glieder, zeichen) -> Rational:
    """Falsch gerechnet: von rechts nach links. Ergibt den Katalogeintrag."""
    wert = Rational(glieder[-1][0], glieder[-1][1])
    for i in range(len(glieder) - 2, -1, -1):
        z, n = glieder[i]
        vz = zeichen[i]
        wert = Rational(z, n) * wert if vz == "*" else Rational(z, n) / wert
        if vz == ":" or vz == "/":
            pass
    return wert


def bau(glieder, zeichen, frage, extra=()):
    """glieder: [(z, n), ...] · zeichen: «:» oder «*» je Zwischenraum."""
    loesung = _rechne(glieder, zeichen)
    text = als_text(loesung)

    erster = Rational(glieder[0][0], glieder[0][1])
    zweiter = Rational(glieder[1][0], glieder[1][1]) if len(glieder) > 1 else None

    katalog = list(extra) + [
        F("mal_statt_geteilt", erster * zweiter if zweiter else None,
          "Durch einen Bruch teilen heisst NICHT, ihn einfach malzunehmen — "
          "er muss zuerst gestürzt werden."),
        F("ersten_gestuerzt",
          (Rational(glieder[0][1], glieder[0][0]) * zweiter)
          if zweiter and glieder[0][0] else None,
          "Gestürzt wird der zweite Bruch, der hinter dem Doppelpunkt."),
        F("beide_gestuerzt",
          (Rational(glieder[0][1], glieder[0][0])
           / zweiter) if zweiter and glieder[0][0] and zweiter else None,
          "Nur der zweite Bruch wird gestürzt, nicht beide."),
        F("falsche_reihenfolge",
          _von_rechts(glieder, zeichen) if len(glieder) > 2 else None,
          "Punktrechnungen werden von links nach rechts abgearbeitet."),
        F("gestuerzt", Rational(loesung.q, loesung.p) if loesung.p else None,
          "Zähler und Nenner des Ergebnisses sind vertauscht."),
        F("zaehler_geteilt",
          Rational(glieder[0][0], glieder[0][1]) - zweiter if zweiter else None,
          "Hier steht ein Doppelpunkt, kein Minus."),
        F("nur_erster", erster, "Der zweite Bruch fehlt im Ergebnis."),
        F("um_eins_zu_gross", loesung + 1,
          "Da ist eine ganze Einheit zu viel im Ergebnis."),
    ]
    katalog = _siebe(katalog, loesung)

    kehr = (f"{br(zweiter.q, zweiter.p)}" if zweiter and zweiter.p else "?")
    return {
        "frage": frage,
        "loesung_text": text,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                           zielform=Zielform.GEKUERZT,
                           # Keine Dezimaltoleranz in Kapitel 2. Sonst gilt
                           # «0.78» fuer 7/9 als richtig — in einer Lektion,
                           # deren ganzer Sinn die gekuerzte Bruchform ist.
                           # In spaeteren Kapiteln bleibt die Toleranz, dort
                           # ist die Kommazahl eine legitime Antwort.
                           dezimal_stellen=None,
                           fehlerkatalog=katalog),
        "schritte": [
            ("Den zweiten Bruch stürzen", f"aus {br(*glieder[1])} wird {kehr}"
             if len(glieder) > 1 else "—"),
            ("Aus dem Doppelpunkt wird ein Malpunkt",
             f"{br(*glieder[0])} · {kehr}"),
            ("Zähler mal Zähler, Nenner mal Nenner", ""),
            ("Kürzen", text),
        ],
        "tipps": TIPPS,
    }


# ── Bereiche · Level = Zahl der Rechenzeichen ────────────────────────────
BEREICHE = {lv: {"z1": ZAEHLER, "z2": ZAEHLER, "z3": ZAEHLER,
                 "n1": NENNER, "n2": NENNER, "n3": NENNER,
                 "k": GANZE, "anzahl": [a]}
            for lv, a in (("A", 2), ("B", 3), ("C", 4))}


def _nicht_trivial(p, g) -> bool:
    return g["loesung_text"] not in ("0", "1")


def _handlich(p, g) -> bool:
    """Zähler und Nenner der Lösung bleiben im Kopfrechenbereich."""
    import re as _re
    return all(int(x) <= 300 for x in _re.findall(r"\d+", g["loesung_text"]))


STANDARD = [fehler_eindeutig, _nicht_trivial, _frage_gekuerzt, _handlich]


def _liste(p):
    zaehler = [p["z1"], p["z2"], p["z3"], 3]
    nenner = [p["n1"], p["n2"], p["n3"], 7]
    return [(zaehler[i], nenner[i]) for i in range(p["anzahl"])]


def _text(glieder, zeichen, ganz_bei=()):
    teile = [str(glieder[0][0]) if 0 in ganz_bei else br(*glieder[0])]
    for i, vz in enumerate(zeichen, start=1):
        teile.append(":" if vz == ":" else "·")
        teile.append(str(glieder[i][0]) if i in ganz_bei else br(*glieder[i]))
    return " ".join(teile)


def _bf(nr, beschreibung, muster, ganz_bei=(), bauer=None, levels=None):
    def bauen(p):
        glieder = bauer(p) if bauer else _liste(p)
        zeichen = (muster * 4)[:len(glieder) - 1]
        return bau(glieder, zeichen, _text(glieder, zeichen, ganz_bei))
    zusatz = {"levels": levels} if levels else {}
    return Bauform(nr, beschreibung, bereiche=BEREICHE, bauen=bauen,
                   filter=STANDARD, **zusatz)


# ── BF1 bis BF3 · Bruch durch Bruch, verschiedene Zeichenfolgen ──────────
BF1 = _bf("BF1", "Bruch durch Bruch", ":")
BF2 = _bf("BF2", "Erst teilen, dann malnehmen", ":*")
#: Level A hat nur EIN Rechenzeichen. «Erst malnehmen, dann teilen» braucht
#: zwei — auf A stünde sonst eine reine Multiplikationsaufgabe in einer
#: Divisionslektion. Regel 5: nicht jede Bauform passt auf jedes Level.
BF3 = _bf("BF3", "Erst malnehmen, dann teilen", "*:", levels=("B", "C"))


# ── BF4 · Ganze Zahl durch Bruch ─────────────────────────────────────────
def _ganz_vorne(p):
    return [(p["k"], 1)] + _liste(p)[1:]


BF4 = _bf("BF4", "Ganze Zahl durch Bruch", ":", ganz_bei=(0,),
          bauer=_ganz_vorne)


# ── BF5 · Bruch durch ganze Zahl ─────────────────────────────────────────
def _ganz_hinten(p):
    g = _liste(p)
    g[1] = (p["k"], 1)
    return g


BF5 = _bf("BF5", "Bruch durch ganze Zahl", ":", ganz_bei=(1,),
          bauer=_ganz_hinten)


# ── BF6 · Durch einen Stammbruch teilen ──────────────────────────────────
def _stammbruch(p):
    g = _liste(p)
    g[1] = (1, p["n2"])
    return g


BF6 = _bf("BF6", "Durch einen Stammbruch teilen — das Ergebnis wird grösser",
          ":", bauer=_stammbruch)


# ── BF7 · Der Divisor ist ein unechter Bruch ─────────────────────────────
def _unecht(p):
    g = _liste(p)
    z, n = p["z2"], p["n2"]
    g[1] = (n, z) if n > z else (z + 1, z)
    return g


BF7 = _bf("BF7", "Der Divisor ist ein unechter Bruch", ":", bauer=_unecht)


# ── BF8 · Gleiche Nenner ─────────────────────────────────────────────────
def _gleiche_nenner(p):
    n = p["n1"]
    zaehler = [p["z1"], p["z2"], p["z3"], 3]
    return [(zaehler[i], n) for i in range(p["anzahl"])]


BF8 = _bf("BF8", "Gleiche Nenner — es lässt sich viel wegkürzen", ":",
          bauer=_gleiche_nenner)


# ── BF9 · Zwei Doppelpunkte hintereinander ───────────────────────────────
BF9 = _bf("BF9", "Mehrere Doppelpunkte hintereinander", "::")


# ── BF10 · Sonderfall: durch eins teilen ─────────────────────────────────
def bf10(p):
    """3/5 : 1 — durch eins teilen ändert nichts."""
    glieder = _liste(p)
    glieder[1] = (1, 1)
    zeichen = (":" + "*" * 3)[:len(glieder) - 1]
    return bau(glieder, zeichen, _text(glieder, zeichen, ganz_bei=(1,)),
               extra=[
        F("eins_abgezogen", Rational(glieder[0][0], glieder[0][1]) - 1,
          "Durch eins teilen ändert nichts. Abgezogen wird hier nichts."),
        F("kehrwert_gebildet",
          Rational(glieder[0][1], glieder[0][0]) if glieder[0][0] else None,
          "Gestürzt wird der zweite Bruch — und eins gestürzt bleibt eins."),
        F("eins_addiert", Rational(glieder[0][0], glieder[0][1]) + 1,
          "Durch eins teilen ändert nichts. Addiert wird hier nichts."),
        F("verdoppelt", Rational(glieder[0][0], glieder[0][1]) * 2,
          "Durch eins teilen verdoppelt nicht."),
        F("halbiert", Rational(glieder[0][0], 2 * glieder[0][1]),
          "Durch eins teilen halbiert nicht."),
    ])


BF10 = Bauform("BF10", "Sonderfall: durch eins teilen",
    bereiche=BEREICHE, bauen=bf10, filter=STANDARD)


# ── BF11 · Sonderfall: das Ergebnis ist eins ─────────────────────────────
def bf11(p):
    """3/5 : 3/5 = 1 — gleich durch gleich. Aufgabe 62 a im Lehrmittel."""
    z, n = p["z1"], p["n1"]
    glieder = [(z, n), (z, n)]
    zeichen = ":"
    for i in range(p["anzahl"] - 2):
        glieder.append((1, 1))
        zeichen += ":"
    return bau(glieder, zeichen, _text(glieder, zeichen,
                                       ganz_bei=tuple(range(2, len(glieder)))),
               extra=[
        F("zaehler_durch_nenner", Rational(z, n),
          "Gleich durch gleich ist eins."),
        F("quadriert", Rational(z * z, n * n),
          "Beim Teilen wird der zweite Bruch gestürzt — dann steht oben und "
          "unten dasselbe."),
        F("null", Integer(0), "Gleich durch gleich ist eins, nicht null."),
        F("zwei", Integer(2), "Nachrechnen: es bleibt genau eins."),
        F("nenner_als_antwort", Integer(n),
          "Das ist der Nenner, nicht das Ergebnis."),
    ])


def _ergibt_eins(p, g) -> bool:
    return g["loesung_text"] == "1"


BF11 = Bauform("BF11", "Sonderfall: gleich durch gleich",
    bereiche=BEREICHE, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_eins, _frage_gekuerzt])


# ── BF12 · Sonderfall: null geteilt durch etwas ──────────────────────────
def bf12(p):
    """0 : 3/5 = 0. Null durch irgendetwas ist null — aber NICHT umgekehrt.

    Die Umkehrung, durch null zu teilen, kommt hier bewusst nicht vor: sie
    ist nicht definiert, und eine Aufgabe ohne Lösung gehört nicht in eine
    Übung, in der jede Eingabe eine Rückmeldung bekommen soll.
    """
    glieder = [(0, 1)] + _liste(p)[1:]
    zeichen = (":" + "*" * 3)[:len(glieder) - 1]
    return bau(glieder, zeichen, _text(glieder, zeichen, ganz_bei=(0,)),
               extra=[
        F("null_ignoriert",
          Rational(glieder[1][1], glieder[1][0]) if glieder[1][0] else None,
          "Null geteilt durch irgendetwas bleibt null."),
        F("eins", Integer(1), "Null durch etwas ist null, nicht eins."),
        F("divisor_abgeschrieben",
          Rational(glieder[1][0], glieder[1][1]),
          "Das ist der Divisor. Null geteilt durch ihn ist null."),
        F("minus_eins", Integer(-1), "Null geteilt durch etwas ist null."),
        F("zwei", Integer(2), "Nachrechnen: null bleibt null."),
    ])


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


BF12 = Bauform("BF12", "Sonderfall: null geteilt durch einen Bruch",
    bereiche=BEREICHE, bauen=bf12,
    filter=[fehler_eindeutig, _ergibt_null, _frage_gekuerzt])


S11 = Schablone(
    nr="S11", titel="Division von Brüchen",
    lektionen="2.10", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Zahl der Rechenzeichen",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Durch einen Bruch teilen heisst: mit seinem Kehrwert "
              "malnehmen. Gestürzt wird der ZWEITE Bruch."),
)
