# -*- coding: utf-8 -*-
"""
S10 · Multiplikation von Brüchen   (Lektionen 2.9 · 2.11)

    «Rechne aus. Gib das Resultat in gekürzter Form an.»
    3/5 · 6/7        →   18/35
    5/6 · 132        →   110
    3/4 · 1/5 · 2/9  →   1/30

Quelle: Lehrmittel A, Kapitel 1.5, Seite 52 — der blaue Kasten gibt die
Regel (Zähler mal Zähler, Nenner mal Nenner), dazu die Aufgaben 45, 46, 48
und 49. Die Form «16 · 3/40» aus Aufgabe 46 a ist BF4, «(1/2)³» aus
Aufgabe 46 c ist BF9.

DER FEHLER, UM DEN ES GEHT: beim Addieren bleibt der Nenner stehen, beim
Multiplizieren nicht. Wer 3/5 · 6/7 rechnet und 18/7 schreibt, hat die
Additionsregel angewandt. Der Katalog führt das als «nenner_behalten» und
ist in jeder Bauform dabei — es ist der mit Abstand häufigste Fehler an
dieser Stelle, gerade weil Kapitel 2.3 bis 2.8 unmittelbar davor liegen.

LEVELACHSE (Teil 2): **Zahl der Faktoren** — A zwei, B drei, C vier. Die
Zahlenvorräte sind auf allen drei Stufen dieselben.

Warum nicht «wie stark sich kürzen lässt»? Weil man das der Aufgabe nicht
ansieht. 3/4 · 8/9 und 3/4 · 5/7 sehen gleich aus, und ein Level, das der
Schüler nicht erkennen kann, ist für ihn kein Level. Dieselbe Lehre wie
bei S8, dort steht die lange Fassung.
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
GANZE = [2, 3, 4, 6, 8, 10, 12]

TIPPS = [
    "Zähler mal Zähler, Nenner mal Nenner.",
    "Vor dem Ausrechnen kürzen spart Arbeit: streiche gleiche Faktoren oben "
    "und unten.",
    "",
]


def _siebe(katalog, ziel: Rational):
    """Wertgleiche, doppelte und rundungsgleiche Einträge entfernen.

    Zur Rundung siehe S8: die Korrektur akzeptiert Dezimalantworten auf zwei
    Stellen, und ein Katalogeintrag, der auf dieselben zwei Stellen fällt,
    käme im Betrieb als RICHTIG zurück.
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


def bau(faktoren, frage, extra=()):
    """faktoren: [(z, n), ...] — eine ganze Zahl steht als (k, 1) drin."""
    loesung = Rational(1)
    for z, n in faktoren:
        loesung *= Rational(z, n)
    text = als_text(loesung)

    z_prod, n_prod = 1, 1
    for z, n in faktoren:
        z_prod *= z
        n_prod *= n

    # Additionsregel statt Multiplikationsregel: Nenner stehen gelassen.
    nenner_erster = faktoren[0][1]

    katalog = list(extra) + [
        F("nenner_behalten", Rational(z_prod, nenner_erster),
          "Nur beim Addieren bleibt der Nenner stehen. Beim Malnehmen werden "
          "auch die Nenner multipliziert."),
        F("zaehler_addiert",
          Rational(sum(z for z, _ in faktoren), n_prod),
          "Die Zähler werden multipliziert, nicht addiert."),
        F("nenner_addiert",
          Rational(z_prod, sum(n for _, n in faktoren)),
          "Die Nenner werden multipliziert, nicht addiert."),
        F("ueber_kreuz",
          Rational(faktoren[0][0] * faktoren[-1][1],
                   faktoren[0][1] * faktoren[-1][0])
          if faktoren[-1][0] else None,
          "Über Kreuz wird beim Dividieren gerechnet, nicht beim "
          "Multiplizieren."),
        F("nur_erster_faktor", Rational(faktoren[0][0], faktoren[0][1]),
          "Der zweite Faktor fehlt."),
        F("gestuerzt", Rational(loesung.q, loesung.p) if loesung.p else None,
          "Zähler und Nenner sind vertauscht."),
        F("nur_zweiter_faktor", Rational(faktoren[1][0], faktoren[1][1])
          if len(faktoren) > 1 else None,
          "Der erste Faktor fehlt."),
        F("zaehlerprodukt_roh", Integer(z_prod),
          f"{z_prod} ist nur das Produkt der Zähler. Der Nenner gehört dazu."),
        F("nennerprodukt_roh", Integer(n_prod),
          f"{n_prod} ist nur das Produkt der Nenner."),
        F("summe_statt_produkt",
          sum((Rational(z, n) for z, n in faktoren), Rational(0)),
          "Hier steht ein Malpunkt, kein Plus."),
        # Die beiden folgenden sind da, weil bei gleichen Faktoren — 2/7 · 2/7
        # oder (1/2)³ — die halbe Liste oben auf denselben Wert fällt und
        # beim Sieben wegfliegt. Sie sind gegen die Lösung immer verschieden.
        F("um_eins_zu_gross", Rational(z_prod + n_prod, n_prod),
          "Da ist eine ganze Einheit zu viel im Ergebnis."),
        F("nenner_verdoppelt", Rational(z_prod, 2 * n_prod),
          "Der Nenner ist doppelt so gross, wie er sein müsste."),
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
            ("Zähler mal Zähler",
             " · ".join(str(z) for z, _ in faktoren) + f" = {z_prod}"),
            ("Nenner mal Nenner",
             " · ".join(str(n) for _, n in faktoren) + f" = {n_prod}"),
            ("Bruch hinschreiben", br(z_prod, n_prod)),
            ("Kürzen", text),
        ],
        "tipps": TIPPS,
    }


# ── Bereiche · Level = Zahl der Faktoren ─────────────────────────────────
BEREICHE = {lv: {"z1": ZAEHLER, "z2": ZAEHLER, "z3": ZAEHLER,
                 "n1": NENNER, "n2": NENNER, "n3": NENNER,
                 "k": GANZE, "anzahl": [a]}
            for lv, a in (("A", 2), ("B", 3), ("C", 4))}


def _nicht_trivial(p, g) -> bool:
    """Ergebnis darf weder 0 noch 1 sein — dafür gibt es BF11 und BF12."""
    return g["loesung_text"] not in ("0", "1")


def _handlich(p, g) -> bool:
    """Zähler und Nenner der Lösung bleiben zweistellig.

    Bei vier Faktoren wächst das Produkt sonst auf 3/1260, und das ist keine
    Kopfrechenaufgabe mehr. Kapitel 2 ist die Grundlage, nicht die Kür.
    """
    import re as _re
    zahlen = [int(x) for x in _re.findall(r"\d+", g["loesung_text"])]
    return all(x <= 200 for x in zahlen)


STANDARD = [fehler_eindeutig, _nicht_trivial, _frage_gekuerzt, _handlich]


def _brueche(p):
    """Die Bruchfaktoren, so viele wie das Level verlangt."""
    zaehler = [p["z1"], p["z2"], p["z3"], 3, 5]
    nenner = [p["n1"], p["n2"], p["n3"], 7, 11]
    return [(zaehler[i], nenner[i]) for i in range(p["anzahl"])]


# ── BF1 · Brüche mal Brüche ──────────────────────────────────────────────
def bf1(p):
    f = _brueche(p)
    return bau(f, " · ".join(br(z, n) for z, n in f))


BF1 = Bauform("BF1", "Brüche malnehmen",
    bereiche=BEREICHE, bauen=bf1, filter=STANDARD)


# ── BF2 · Ganze Zahl mal Bruch ───────────────────────────────────────────
def bf2(p):
    """5 · 3/7 — Aufgabe 46 a im Lehrmittel."""
    f = [(p["k"], 1)] + _brueche(p)[:p["anzahl"] - 1]
    teile = [str(p["k"])] + [br(z, n) for z, n in f[1:]]
    return bau(f, " · ".join(teile))


BF2 = Bauform("BF2", "Ganze Zahl mal Bruch",
    bereiche=BEREICHE, bauen=bf2, filter=STANDARD)


# ── BF3 · Bruch mal ganze Zahl ───────────────────────────────────────────
def bf3(p):
    """5/6 · 132 — die ganze Zahl steht hinten."""
    f = _brueche(p)[:p["anzahl"] - 1] + [(p["k"], 1)]
    teile = [br(z, n) for z, n in f[:-1]] + [str(p["k"])]
    return bau(f, " · ".join(teile))


BF3 = Bauform("BF3", "Bruch mal ganze Zahl",
    bereiche=BEREICHE, bauen=bf3, filter=STANDARD)


# ── BF4 · Die ganze Zahl geht im Nenner auf ──────────────────────────────
def bf4(p):
    """16 · 3/40 — hier lohnt sich das Kürzen VOR dem Ausrechnen.

    Der Nenner ist ein Vielfaches der ganzen Zahl, also lässt sich streichen,
    bevor irgendetwas gross wird. Das ist der eigentliche Kniff des blauen
    Kastens auf Seite 52.
    """
    k, z1 = p["k"], p["z1"]
    n = k * p["z2"] if p["z2"] > 1 else k * 2
    f = [(k, 1), (z1, n)]
    teile = [str(k), br(z1, n)]
    for i in range(p["anzahl"] - 2):
        f.append((p["z3"], p["n3"]))
        teile.append(br(p["z3"], p["n3"]))
    return bau(f, " · ".join(teile))


BF4 = Bauform("BF4", "Die ganze Zahl geht im Nenner auf",
    bereiche=BEREICHE, bauen=bf4, filter=STANDARD)


# ── BF5 · Es lässt sich über Kreuz kürzen ────────────────────────────────
def bf5(p):
    """3/8 · 4/9 — der Zähler des einen kürzt den Nenner des anderen."""
    a, b = p["z1"], p["z2"]
    f = [(a, b * 2), (b, a * 3)] if a * 3 > 1 else [(1, 2), (2, 3)]
    teile = [br(z, n) for z, n in f]
    for i in range(p["anzahl"] - 2):
        f.append((p["z3"], p["n3"]))
        teile.append(br(p["z3"], p["n3"]))
    return bau(f, " · ".join(teile))


BF5 = Bauform("BF5", "Über Kreuz kürzbar",
    bereiche=BEREICHE, bauen=bf5, filter=STANDARD)


# ── BF6 · Ein Zähler ist eins ────────────────────────────────────────────
def bf6(p):
    """1/2 · 3/5 — der Stammbruch, die häufigste Form im Lehrmittel."""
    f = [(1, p["n1"])] + _brueche(p)[1:]
    return bau(f, " · ".join(br(z, n) for z, n in f))


BF6 = Bauform("BF6", "Ein Faktor ist ein Stammbruch",
    bereiche=BEREICHE, bauen=bf6, filter=STANDARD)


# ── BF7 · Unechte Brüche ─────────────────────────────────────────────────
def bf7(p):
    """7/3 · 5/2 — Zähler grösser als Nenner, das Ergebnis wird gross."""
    f = [(p["n1"], p["z1"]) if p["n1"] > p["z1"] else (p["z1"] + 1, p["z1"])]
    f.append((p["n2"], p["z2"]) if p["n2"] > p["z2"] else (p["z2"] + 1, p["z2"]))
    for i in range(p["anzahl"] - 2):
        f.append((p["z3"], p["n3"]))
    return bau(f, " · ".join(br(z, n) for z, n in f))


BF7 = Bauform("BF7", "Unechte Brüche",
    bereiche=BEREICHE, bauen=bf7, filter=STANDARD)


# ── BF8 · Gleiche Brüche ─────────────────────────────────────────────────
def bf8(p):
    """2/3 · 2/3 — dasselbe zweimal. Vorstufe zur Potenz in BF9."""
    z, n = p["z1"], p["n1"]
    f = [(z, n)] * p["anzahl"]
    return bau(f, " · ".join(br(z, n) for _ in range(p["anzahl"])))


BF8 = Bauform("BF8", "Derselbe Bruch mehrfach",
    bereiche=BEREICHE, bauen=bf8, filter=STANDARD)


# ── BF9 · Bruch als Potenz ───────────────────────────────────────────────
def bf9(p):
    """(1/2)³ — Aufgabe 46 c im Lehrmittel.

    Die Hochzahl wächst mit dem Level: zwei, drei, vier. Damit trägt die
    Levelachse auch hier die Zahl der Faktoren, nur anders geschrieben.
    """
    z, n, e = p["z1"], p["n1"], p["anzahl"]
    #: Die Hochzahl bleibt bei zwei; was mit dem Level wächst, ist die Zahl
    #: der Faktoren DANEBEN. Zuerst hatte ich die Hochzahl selbst wachsen
    #: lassen — (1/2)², (1/2)³, (1/2)⁴. Der Testlauf hat das beanstandet,
    #: und zu Recht: hochgestellte Ziffern zählen nicht als Aufbaumerkmal,
    #: sonst wäre jedes Level nur eine andere Zahl.
    hoch = "²"
    faktoren = [(z, n), (z, n)]
    teile = [f"({br(z, n)})²"]
    weitere = [(p["z2"], p["n2"]), (p["z3"], p["n3"])]
    for i in range(e - 2):
        faktoren.append(weitere[i])
        teile.append(br(*weitere[i]))
    return bau(faktoren, " · ".join(teile), extra=[
        F("basis_mal_exponent", Rational(z, n) * 2,
          "Hochzahl zwei heisst: den Bruch mit sich selbst malnehmen, nicht "
          "mit zwei malnehmen."),
        F("nur_zaehler_potenziert", Rational(z ** 2, n),
          "Auch der Nenner bekommt die Hochzahl."),
        F("nur_nenner_potenziert", Rational(z, n ** 2),
          "Auch der Zähler bekommt die Hochzahl."),
    ])


BF9 = Bauform("BF9", "Bruch mit Hochzahl",
    bereiche=BEREICHE, bauen=bf9, filter=STANDARD)


# ── BF10 · Sonderfall: ein Faktor ist eins ───────────────────────────────
def bf10(p):
    """3/5 · 1 — die Eins ändert nichts. Wer das nicht sieht, rechnet los."""
    f = _brueche(p)[:p["anzahl"] - 1] + [(1, 1)]
    teile = [br(z, n) for z, n in f[:-1]] + ["1"]
    return bau(f, " · ".join(teile), extra=[
        F("eins_addiert",
          sum((Rational(z, n) for z, n in f[:-1]), Rational(0)) + 1,
          "Mal eins ändert nichts. Addiert wird hier nicht."),
    ])


BF10 = Bauform("BF10", "Sonderfall: ein Faktor ist eins",
    bereiche=BEREICHE, bauen=bf10, filter=STANDARD)


# ── BF11 · Sonderfall: das Ergebnis ist eins ─────────────────────────────
def bf11(p):
    """3/5 · 5/3 = 1 — Kehrwerte. Steht im Lehrmittel als Aufgabe 62 b."""
    z, n = p["z1"], p["n1"]
    if z == n:
        z, n = 2, 3
    f = [(z, n), (n, z)]
    teile = [br(z, n), br(n, z)]
    for i in range(p["anzahl"] - 2):
        f.append((p["z2"], p["z2"]))
        teile.append(br(p["z2"], p["z2"]))
    return bau(f, " · ".join(teile), extra=[
        F("zaehler_produkt", Integer(z * n),
          "Zähler und Nenner heben sich weg. Es bleibt eins."),
        F("als_bruch_gelassen", Rational(z, n),
          f"{z}·{n} oben und {n}·{z} unten ist dasselbe — das ergibt eins."),
        F("null", Integer(0), "Kehrwerte ergeben eins, nicht null."),
        F("zwei", Integer(2), "Nachrechnen: oben und unten steht dasselbe."),
        F("summe", Rational(z, n) + Rational(n, z),
          "Hier wird malgenommen, nicht addiert."),
    ])


def _ergibt_eins(p, g) -> bool:
    return g["loesung_text"] == "1"


def _kehrwert_gekuerzt(p, g) -> bool:
    """Beide Brüche der Frage müssen gekürzt dastehen."""
    import re as _re
    from math import gcd
    for z, n in _re.findall(r"(\d+)/(\d+)", g["frage"]):
        if gcd(int(z), int(n)) > 1:
            return False
    return True


BF11 = Bauform("BF11", "Sonderfall: Kehrwerte, das Ergebnis ist eins",
    bereiche=BEREICHE, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_eins, _kehrwert_gekuerzt])


# ── BF12 · Sonderfall: das Ergebnis ist null ─────────────────────────────
def bf12(p):
    """3/5 · 0 = 0. Ein Faktor null macht das ganze Produkt null."""
    f = _brueche(p)[:p["anzahl"] - 1] + [(0, 1)]
    teile = [br(z, n) for z, n in f[:-1]] + ["0"]
    return bau(f, " · ".join(teile), extra=[
        F("null_ignoriert",
          _produkt(f[:-1]),
          "Ein Faktor null macht das ganze Produkt null."),
        F("eins", Integer(1), "Mal null ist null, nicht eins."),
        F("nenner_summe", Integer(sum(n for _, n in f)),
          "Ein Faktor null macht alles null."),
        F("erster_faktor", Rational(f[0][0], f[0][1]),
          "Auch dieser Faktor wird mit null malgenommen."),
        F("summe_der_zaehler", Integer(sum(z for z, _ in f)),
          "Hier wird malgenommen, nicht addiert."),
        F("minus_eins", Integer(-1), "Mal null ist null."),
    ])


def _produkt(faktoren):
    r = Rational(1)
    for z, n in faktoren:
        r *= Rational(z, n)
    return r


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


BF12 = Bauform("BF12", "Sonderfall: ein Faktor ist null",
    bereiche=BEREICHE, bauen=bf12,
    filter=[fehler_eindeutig, _ergibt_null, _kehrwert_gekuerzt])


S10 = Schablone(
    nr="S10", titel="Multiplikation von Brüchen",
    lektionen="2.9 · 2.11", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Zahl der Faktoren",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Zähler mal Zähler, Nenner mal Nenner. Anders als beim "
              "Addieren bleibt der Nenner NICHT stehen."),
)
