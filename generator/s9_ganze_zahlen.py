# -*- coding: utf-8 -*-
"""
S9 · Brüche mit ganzen Zahlen addieren und subtrahieren   (Lektionen 2.7 – 2.8)

    «Rechne aus. Gib das Resultat in gekürzter Form an.»
    3/4 + 1     →   7/4
    2 − 2/3     →   4/3
    5/6 + 2 − 1/3

Quelle: Lehrmittel A, Kapitel 1.5, Seite 50 — der blaue Kasten zeigt genau
diese Form (3/4 + 1 = 3/4 + 4/4 = 7/4 und 2 − 2/3 = 6/3 − 2/3 = 4/3), dazu
die Aufgaben 39 und 41.

DER EINE GEDANKE, UM DEN ES GEHT: eine ganze Zahl ist auch ein Bruch. Wer
2 als 6/3 schreiben kann, hat die Lektion verstanden; wer die 2 stehen
lässt und nur die Brüche verrechnet, hat den häufigsten Fehler gemacht.
Der Fehlerkatalog führt ihn als «ganze_zahl_vergessen».

LEVELACHSE (Teil 2): **Zahl der Glieder** — A zwei, B drei, C vier. Die
Zahlenvorräte sind auf allen drei Stufen dieselben.

WARUM HIER KEINE GEMISCHTEN BRÜCHE VORKOMMEN, obwohl das Lehrmittel sie
verwendet (Aufgabe 39 a: 1¾ + 2 + ¾):
Der Parser liest «1 3/4» als 3/4 und wirft die ganze Zahl stillschweigend
weg. Stünde ein gemischter Bruch in der Aufgabe, würde ein Schüler seine
Antwort genauso schreiben — und bekäme sie als falsch zurück, ohne zu
erfahren, warum. Solange die Eingabe das nicht kann, gehört die
Schreibweise nicht in die Aufgabe. Als unechter Bruch (7/4) steht dieselbe
Zahl da und wird richtig gelesen.
"""
from __future__ import annotations

from sympy import Integer, Rational

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .s8_addition_subtraktion import (F, ZAEHLER, br, _frage_gekuerzt,
                                      _nenner_zahm, als_text)
from .schablone import Bauform, Schablone

VARS: set[str] = set()
ANLEITUNG = "Rechne aus. Gib das Resultat in gekürzter Form an."

NENNER = [2, 3, 4, 5, 6, 8, 9, 10, 12]
GANZE = [1, 2, 3, 4, 5]

TIPPS = [
    "Eine ganze Zahl lässt sich als Bruch schreiben: 2 = 2/1.",
    "Schreib die ganze Zahl mit dem Nenner der Brüche — dann kannst du "
    "verrechnen.",
    "",
]


def _siebe(katalog, ziel: Rational):
    """Wertgleiche, doppelte und rundungsgleiche Einträge entfernen.

    Die Rundungsprüfung ist nicht Zierde: die Korrektur akzeptiert gerundete
    Dezimalantworten auf zwei Stellen, und ein Katalogeintrag, der auf
    dieselben zwei Stellen fällt wie die Lösung, käme im Betrieb als RICHTIG
    zurück, obwohl er als Fehler gedacht war.
    """
    raus, gesehen = [], set()
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        wert = Rational(e)
        if wert == ziel or str(wert) in gesehen:
            continue
        # Nicht nur die gerundete Form vergleichen, sondern den ABSTAND.
        # Die Korrektur akzeptiert Dezimalantworten auf zwei Stellen; liegen
        # zwei Werte näher als eine Hundertstel beieinander, kann derselbe
        # Tastendruck beide treffen. round() allein reicht nicht, weil 0.075
        # und 0.0833 verschieden runden und trotzdem beide als 0.08 getippt
        # werden. Genau daran ist ein Katalogeintrag als «richtig» erkannt
        # worden.
        if abs(float(wert) - float(ziel)) < 0.01:
            continue
        gesehen.add(str(wert))
        raus.append(f)
    return raus


def bau(glieder, zeichen, frage, extra=()):
    """glieder: [(z, n), ...] — eine ganze Zahl steht als (z, 1) drin."""
    loesung = Rational(glieder[0][0], glieder[0][1])
    for (z, n), vz in zip(glieder[1:], zeichen):
        loesung += Rational(z, n) if vz == "+" else -Rational(z, n)
    text = als_text(loesung)

    # Die Brüche ohne die ganzen Zahlen — das ist der häufigste Fehler.
    nur_brueche = Rational(0)
    nur_ganze = Integer(0)
    vorzeichen = ["+"] + list(zeichen)
    for (z, n), vz in zip(glieder, vorzeichen):
        wert = Rational(z, n)
        if n == 1:
            nur_ganze += wert if vz == "+" else -wert
        else:
            nur_brueche += wert if vz == "+" else -wert

    nenner = [n for _, n in glieder if n != 1]
    hn = nenner[0] if nenner else 1
    for n in nenner[1:]:
        hn = hn * n // _ggt(hn, n)

    katalog = list(extra) + [
        F("ganze_zahl_vergessen", nur_brueche,
          "Die ganze Zahl gehört mit ins Ergebnis. Schreib sie als Bruch mit "
          f"dem Nenner {hn}."),
        F("nur_ganze_zahlen", nur_ganze,
          "Die Brüche gehören auch dazu."),
        F("als_zaehler_behandelt", nur_brueche + Rational(int(nur_ganze), hn),
          f"Eine ganze Zahl ist kein Zähler. {nur_ganze} ist "
          f"{int(nur_ganze) * hn}/{hn}, nicht {nur_ganze}/{hn}."),
        F("nenner_mitgerechnet", nur_brueche + Rational(1, hn) * 0
          + Rational(int(nur_ganze) * hn, hn + 1) if hn > 1 else None,
          "Der Nenner ändert sich beim Erweitern der ganzen Zahl nicht."),
        F("gestuerzt", Rational(loesung.q, loesung.p) if loesung.p else None,
          "Zähler und Nenner sind vertauscht."),
        F("vorzeichen_vertauscht", -loesung if loesung != 0 else None,
          "Achte auf Plus und Minus."),
        F("hauptnenner_als_antwort", Integer(hn),
          f"{hn} ist der Hauptnenner, nicht das Ergebnis."),
    ]
    katalog = _siebe(katalog, loesung)

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
            ("Die ganze Zahl als Bruch schreiben",
             f"{int(abs(nur_ganze))} = {int(abs(nur_ganze)) * hn}/{hn}"),
            ("Jetzt haben alle denselben Nenner", f"Hauptnenner {hn}"),
            ("Zähler verrechnen, Nenner behalten", text),
        ],
        "tipps": TIPPS,
    }


def _ggt(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


# ── Bereiche · Level = Zahl der Glieder ──────────────────────────────────
BEREICHE = {lv: {"z1": ZAEHLER, "z2": ZAEHLER, "n": NENNER, "k": GANZE,
                 "anzahl": [k]}
            for lv, k in (("A", 2), ("B", 3), ("C", 4))}


def _nicht_null(p, g) -> bool:
    return g["loesung_text"] != "0"


def _kein_ganzes(p, g) -> bool:
    """Das Ergebnis soll ein Bruch bleiben — der ganzzahlige Fall ist BF10."""
    return "/" in g["loesung_text"]


STANDARD = [fehler_eindeutig, _nicht_null, _kein_ganzes,
            _frage_gekuerzt, _nenner_zahm]


def _glieder(p, ganze_vorne: bool, minus_ab: int | None):
    """Baut Glieder und Frage. Die ganze Zahl steht vorne oder hinten."""
    n, k, anzahl = p["n"], p["k"], p["anzahl"]
    zaehler = [p["z1"], p["z2"]] + [z for z in ZAEHLER if z not in (p["z1"], p["z2"])]
    brueche = []
    nenner_folge = [n, n * 2, n * 3]
    for i in range(anzahl - 1):
        brueche.append((zaehler[i], nenner_folge[i % 3]))

    teile, glieder, zeichen = [], [], ""
    folge = ([(k, 1)] + brueche) if ganze_vorne else (brueche + [(k, 1)])
    for i, (z, nn) in enumerate(folge):
        if i:
            minus = minus_ab is not None and i >= minus_ab
            zeichen += "-" if minus else "+"
            teile.append("−" if minus else "+")
        glieder.append((z, nn))
        teile.append(str(z) if nn == 1 else br(z, nn))
    return glieder, zeichen, " ".join(teile)


def _bf(nr, beschreibung, ganze_vorne, minus_ab, extra_filter=()):
    def bauen(p):
        glieder, zeichen, frage = _glieder(p, ganze_vorne, minus_ab)
        return bau(glieder, zeichen, frage)
    return Bauform(nr, beschreibung, bereiche=BEREICHE, bauen=bauen,
                   filter=STANDARD + list(extra_filter))


# ── Addition ─────────────────────────────────────────────────────────────
BF1 = _bf("BF1", "Bruch plus ganze Zahl", False, None)
BF2 = _bf("BF2", "Ganze Zahl plus Bruch", True, None)

# ── Subtraktion ──────────────────────────────────────────────────────────
BF3 = _bf("BF3", "Bruch minus ganze Zahl", False, 1)
BF4 = _bf("BF4", "Ganze Zahl minus Bruch", True, 1)

# ── Gemischt ─────────────────────────────────────────────────────────────
BF5 = _bf("BF5", "Ganze Zahl vorne, Minus erst später", True, 2)
BF6 = _bf("BF6", "Bruch vorne, Minus erst später", False, 2)


# ── BF7 · Zwei ganze Zahlen ──────────────────────────────────────────────
def bf7(p):
    """5/6 + 2 + 3 — zwei ganze Zahlen, damit das Zusammenfassen geübt wird."""
    n, k, anzahl = p["n"], p["k"], p["anzahl"]
    glieder = [(p["z1"], n), (k, 1), (k + 1, 1)]
    teile = [br(p["z1"], n), "+", str(k), "+", str(k + 1)]
    zeichen = "++"
    for i in range(anzahl - 2):
        glieder.append((p["z2"], n * (i + 2)))
        teile += ["+", br(p["z2"], n * (i + 2))]
        zeichen += "+"
    return bau(glieder, zeichen, " ".join(teile))


BF7 = Bauform("BF7", "Zwei ganze Zahlen im Term",
    bereiche=BEREICHE, bauen=bf7, filter=STANDARD)


# ── BF8 · Die ganze Zahl steht in der Mitte ──────────────────────────────
def bf8(p):
    n, k, anzahl = p["n"], p["k"], p["anzahl"]
    glieder = [(p["z1"], n), (k, 1)]
    teile = [br(p["z1"], n), "+", str(k)]
    zeichen = "+"
    for i in range(anzahl - 2):
        glieder.append((p["z2"], n * (i + 2)))
        teile += ["−", br(p["z2"], n * (i + 2))]
        zeichen += "-"
    return bau(glieder, zeichen, " ".join(teile))


BF8 = Bauform("BF8", "Ganze Zahl in der Mitte, danach Minus",
    bereiche=BEREICHE, bauen=bf8, filter=STANDARD)


# ── BF9 · Sonderfall: die ganze Zahl ist eins ────────────────────────────
def bf9(p):
    """3/4 + 1 — steht wörtlich im blauen Kasten des Lehrmittels.

    Die Eins ist der Fall, bei dem das Erweitern am leichtesten vergessen
    wird: «plus eins» sieht aus, als müsste man nichts umschreiben.
    """
    n, anzahl = p["n"], p["anzahl"]
    glieder = [(p["z1"], n), (1, 1)]
    teile = [br(p["z1"], n), "+", "1"]
    zeichen = "+"
    for i in range(anzahl - 2):
        glieder.append((p["z2"], n * (i + 2)))
        teile += ["+", br(p["z2"], n * (i + 2))]
        zeichen += "+"
    return bau(glieder, zeichen, " ".join(teile), extra=[
        F("eins_als_zaehler", Rational(p["z1"] + 1, n),
          f"Die Eins ist eine ganze Zahl. Als Bruch mit dem Nenner {n} ist "
          f"sie {n}/{n}, nicht 1/{n}."),
    ])


BF9 = Bauform("BF9", "Sonderfall: die ganze Zahl ist eins",
    bereiche=BEREICHE, bauen=bf9, filter=STANDARD)


# ── BF10 · Sonderfall: das Ergebnis ist eine ganze Zahl ──────────────────
def bf10(p):
    """1/4 + 3/4 + 2 = 3. Das Ergebnis ist ganz — wer immer einen Bruch
    erwartet, schreibt 12/4."""
    n, k, anzahl = p["n"], p["k"], p["anzahl"]
    z1 = p["z1"] % n or 1
    #: Zwei Brüche, die zusammen eins ergeben, sind das Minimum — darunter
    #: gibt es die Aufgabe nicht. Das Level zählt darum ab drei Gliedern
    #: aufwärts: A drei, B vier, C fünf. Ohne diesen Versatz sehen A und B
    #: gleich aus, und der Testlauf beanstandet die Levelachse zu Recht.
    glieder = [(z1, n), (n - z1, n), (k, 1)]
    teile = [br(z1, n), "+", br(n - z1, n), "+", str(k)]
    zeichen = "++"
    for i in range(anzahl - 2):
        glieder.append((k + 1 + i, 1))
        teile += ["+", str(k + 1 + i)]
        zeichen += "+"
    return bau(glieder, zeichen, " ".join(teile), extra=[
        F("als_bruch_gelassen", Rational((k + 1) * n, n) * 0
          + Rational(1, n), "Die Brüche ergeben zusammen eins. Am Ende steht "
          "eine ganze Zahl."),
    ])


def _ergibt_ganze_zahl(p, g) -> bool:
    return "/" not in g["loesung_text"] and g["loesung_text"] != "0"


BF10 = Bauform("BF10", "Sonderfall: das Ergebnis ist eine ganze Zahl",
    bereiche=BEREICHE, bauen=bf10,
    filter=[fehler_eindeutig, _ergibt_ganze_zahl, _frage_gekuerzt])


# ── BF11 · Sonderfall: das Ergebnis ist null ─────────────────────────────
def bf11(p):
    """1 − 1/2 − 1/2 = 0."""
    n, anzahl = p["n"], p["anzahl"]
    z1 = p["z1"] % n or 1
    #: Wie bei BF10: drei Glieder sind das Minimum, das Level zählt ab da
    #: aufwärts. Der frühere Anlauf hängte «+ n/n» an — das ist ein
    #: ungekürzter Bruch in der Frage UND macht das Ergebnis eins statt null.
    if anzahl == 2:
        glieder = [(1, 1), (z1, n), (n - z1, n)]
        teile = ["1", "−", br(z1, n), "−", br(n - z1, n)]
        zeichen = "--"
    elif anzahl == 3:
        glieder = [(1, 1), (1, 1), (z1, n), (2 * n - z1, n)]
        teile = ["1", "+", "1", "−", br(z1, n), "−", br(2 * n - z1, n)]
        zeichen = "+--"
    else:
        glieder = [(1, 1), (1, 1), (1, 1), (z1, n), (3 * n - z1, n)]
        teile = ["1", "+", "1", "+", "1", "−", br(z1, n),
                 "−", br(3 * n - z1, n)]
        zeichen = "++--"
    return bau(glieder, zeichen, " ".join(teile), extra=[
        F("eins_stehen_gelassen", Integer(1),
          "Die beiden Brüche ergeben zusammen eins und heben die ganze Zahl "
          "auf."),
        F("nur_der_erste_bruch", Rational(z1, n),
          "Beide Brüche werden abgezogen."),
        F("minus_eins", Integer(-1), "Da ist ein Vorzeichen verrutscht."),
        F("nenner_als_antwort", Integer(n),
          "Das ist der Nenner, nicht das Ergebnis."),
        F("zwei", Integer(2), "Nachrechnen: es bleibt nichts übrig."),
    ])


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


BF11 = Bauform("BF11", "Sonderfall: das Ergebnis ist null",
    bereiche=BEREICHE, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_null, _frage_gekuerzt])


# ── BF12 · Sonderfall: das Ergebnis ist negativ ──────────────────────────
def bf12(p):
    """1/4 − 2 = −7/4. Wer das Vorzeichen vergisst, bekommt 7/4."""
    n, k, anzahl = p["n"], p["k"], p["anzahl"]
    glieder = [(p["z1"], n), (k + 1, 1)]
    teile = [br(p["z1"], n), "−", str(k + 1)]
    zeichen = "-"
    for i in range(anzahl - 2):
        glieder.append((p["z2"], n * (i + 2)))
        teile += ["−", br(p["z2"], n * (i + 2))]
        zeichen += "-"
    return bau(glieder, zeichen, " ".join(teile))


def _ergibt_negativ(p, g) -> bool:
    return g["loesung_text"].startswith("-")


BF12 = Bauform("BF12", "Sonderfall: das Ergebnis ist negativ",
    bereiche=BEREICHE, bauen=bf12,
    filter=STANDARD + [_ergibt_negativ])


S9 = Schablone(
    nr="S9", titel="Brüche mit ganzen Zahlen addieren und subtrahieren",
    lektionen="2.7 – 2.8", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Zahl der Glieder",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Eine ganze Zahl ist auch ein Bruch: 2 = 2/1. Schreib sie mit "
              "dem Hauptnenner, dann lässt sich alles verrechnen."),
)
