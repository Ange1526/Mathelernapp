# -*- coding: utf-8 -*-
"""
S8 · Addition und Subtraktion von Brüchen   (Lektionen 2.3 – 2.6)

    «Gib das Resultat in gekürzter Form an.»
    2/3 + 5/3     →   7/3
    1/4 + 1/6     →   5/12
    3/2 + 5/6 + 2/3

Quelle: Lehrmittel A, Kapitel 1.5, Seite 46 (Aufgaben 21 und 22,
Gleichnamigmachen) und Seite 50 (Aufgaben 39 bis 42, Addition und
Subtraktion). Der blaue Kasten auf Seite 50 gibt die Regel vor, die hier
als Kernidee steht.

VIER LEKTIONEN, EINE SCHABLONE — warum das zusammengehört:
2.3 (Addition, gleicher Nenner), 2.4 (Subtraktion, gleicher Nenner),
2.5 (Hauptnenner über das kgV) und 2.6 (ungleiche Nenner) sind derselbe
Rechenweg in drei Ausbaustufen. Das Netz führt sie einzeln, damit ein
Schüler gezielt zurückspringen kann; die Aufgaben stammen aus einer
Schablone, weil sie sich nur in der Stufe unterscheiden.

AUFTEILUNG — erst der zweite Anlauf war richtig:

    BAUFORM  trägt das Verhältnis der Nenner
             gleich · ein Nenner ist Vielfaches des andern · teilerfremd
    LEVEL    trägt die Zahl der Summanden
             A zwei · B drei · C vier

Zuerst hatte ich es umgekehrt: das Level sollte das Verhältnis der Nenner
tragen. Rechnerisch ist das die richtige Schwierigkeitsachse — der Testlauf
hat es trotzdem beanstandet, und zu Recht. Er vergleicht den AUFBAU der
Aufgabe, und «1/3 + 1/6» und «1/3 + 1/9» sehen gleich aus. Ein Level, das
man der Aufgabe nicht ansieht, ist für den Schüler kein Level, sondern
Zufall. Die Nennerart gehört darum in die Bauform, wo sie sichtbar
nebeneinandersteht.

Die Zahlenvorräte sind auf allen drei Stufen dieselben.

DIE RUNDUNGSFALLE, die schon bei S7 zugeschlagen hat:
Die Prüfung nimmt gerundete Dezimalantworten auf zwei Stellen an. Ein
Katalogeintrag, der auf dieselben zwei Stellen rundet wie die Lösung, käme
im Betrieb als RICHTIG zurück, obwohl er als Fehler gedacht war. `_siebe`
wirft solche Einträge darum weg — hier ist das Risiko grösser als bei S7,
weil Bruchsummen dicht beieinanderliegen.
"""
from __future__ import annotations

import math

from sympy import Integer, Rational

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .schablone import Bauform, Schablone

VARS: set[str] = set()
ANLEITUNG = "Rechne aus. Gib das Resultat in gekürzter Form an."


def F(schluessel: str, ergebnis, text: str) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def br(z: int, n: int) -> str:
    """«2/3», und «2» wenn der Nenner 1 ist."""
    return str(z) if n == 1 else f"{z}/{n}"


def als_text(r: Rational) -> str:
    return str(r.p) if r.q == 1 else f"{r.p}/{r.q}"


def _siebe(katalog, ziel: Rational):
    """Wertgleiche, doppelte und rundungsgleiche Einträge entfernen.

    Siehe Kopfkommentar: ohne die Rundungsprüfung wird ein Fehlereintrag
    im Betrieb als richtige Antwort durchgewinkt.
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


TIPPS = [
    "Nur gleichnamige Brüche lassen sich addieren — erst den Hauptnenner "
    "suchen.",
    "Der Hauptnenner ist das kgV der Nenner. Danach jeden Bruch erweitern.",
    "",
]


def bau(glieder, zeichen, frage, extra=(), tipps=None):
    """glieder: [(z, n), ...] · zeichen: «+» oder «−» je Zwischenraum."""
    loesung = Rational(glieder[0][0], glieder[0][1])
    for (z, n), vz in zip(glieder[1:], zeichen):
        loesung += Rational(z, n) if vz == "+" else -Rational(z, n)
    text = als_text(loesung)

    nenner = [n for _, n in glieder]
    hn = nenner[0]
    for n in nenner[1:]:
        hn = hn * n // math.gcd(hn, n)

    # Der Klassiker: Zähler und Nenner getrennt addiert.
    z_summe = glieder[0][0]
    n_summe = glieder[0][1]
    for (z, n), vz in zip(glieder[1:], zeichen):
        z_summe = z_summe + z if vz == "+" else z_summe - z
        n_summe = n_summe + n if vz == "+" else n_summe - n

    katalog = list(extra) + [
        F("nenner_mitaddiert", Rational(z_summe, n_summe) if n_summe else None,
          "Der Nenner wird NICHT mitaddiert. Er sagt nur, in wie viele Teile "
          "geteilt wurde."),
        F("nicht_erweitert", Rational(z_summe, hn) if hn else None,
          "Vor dem Addieren müssen beide Brüche denselben Nenner haben."),
        F("nenner_multipliziert",
          Rational(sum(z for z, _ in glieder), nenner[0] * nenner[1])
          if len(nenner) > 1 else None,
          "Das Produkt der Nenner ist ein gemeinsamer Nenner, aber nicht der "
          f"kleinste. Der Hauptnenner ist {hn}."),
        F("hauptnenner_als_antwort", Integer(hn),
          f"{hn} ist der Hauptnenner, nicht das Ergebnis."),
        F("gestuerzt", Rational(loesung.q, loesung.p) if loesung.p else None,
          "Zähler und Nenner sind vertauscht."),
        F("vorzeichen_vertauscht", -loesung if loesung != 0 else None,
          "Achte auf Plus und Minus."),
        F("nur_erster_summand", Rational(glieder[0][0], glieder[0][1]),
          "Der zweite Bruch fehlt im Ergebnis."),
        F("nur_zweiter_summand", Rational(glieder[1][0], glieder[1][1])
          if len(glieder) > 1 else None,
          "Der erste Bruch fehlt im Ergebnis."),
        F("zaehler_summe_roh", Integer(z_summe),
          "Das ist nur die Summe der Zähler. Der Nenner gehört dazu."),
        F("um_hauptnenner_verrechnet",
          Rational(z_summe, hn) + 1 if hn else None,
          "Da ist eine ganze Einheit zu viel."),
    ]
    katalog = _siebe(katalog, loesung)

    schritte = [("Hauptnenner suchen",
                 f"kgV von {', '.join(str(n) for n in nenner)} ist {hn}")]
    erweitert = []
    for z, n in glieder:
        erweitert.append(br(z * (hn // n), hn))
    schritte.append(("Alle Brüche erweitern", "   ".join(erweitert)))
    schritte.append(("Zähler verrechnen, Nenner behalten",
                     br(sum(int(e.split('/')[0]) * (1 if i == 0 or
                            zeichen[i - 1] == "+" else -1)
                            for i, e in enumerate(erweitert)), hn)))
    schritte.append(("Kürzen", text))

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
        "schritte": schritte,
        "tipps": tipps or TIPPS,
    }


# ── Zahlenvorräte · auf allen drei Level dieselben ───────────────────────
ZAEHLER = [1, 2, 3, 4, 5, 7]
NENNER = [2, 3, 4, 5, 6, 8, 9, 10, 12]
FAKTOR = [2, 3, 4]

def _bereiche(stufe: str) -> dict:
    """Level A/B/C = zwei, drei, vier Summanden. Die Nennerart ist fest."""
    return {lv: {"z1": ZAEHLER, "z2": ZAEHLER, "z3": ZAEHLER, "n": NENNER,
                 "f": FAKTOR, "stufe": [stufe], "anzahl": [k]}
            for lv, k in (("A", 2), ("B", 3), ("C", 4))}


GLEICH = _bereiche("gleich")
VIELFACHES = _bereiche("vielfaches")
TEILERFREMD = _bereiche("teilerfremd")


def _nenner_paar(p):
    """Gibt (n1, n2) je nach Stufe. Hier sitzt die Levelachse.

    Ohne diese Funktion unterscheiden sich A, B und C nur in den gezogenen
    Zahlen — und das beanstandet der Testlauf zu Recht.
    """
    n, f, stufe = p["n"], p["f"], p["stufe"]
    if stufe == "gleich":
        return n, n
    if stufe == "vielfaches":
        return n, n * f
    # teilerfremd: zwei Nenner ohne gemeinsamen Teiler
    kandidat = n + 1
    while math.gcd(n, kandidat) != 1:
        kandidat += 1
    return n, kandidat


def _kein_ganzes(p, g) -> bool:
    """Verhindert, dass eine Additionsaufgabe glatt aufgeht.

    2/6 + 4/6 = 1 ist keine schlechte Aufgabe, aber als REGELFALL wäre sie
    irreführend: der Schüler lernt sonst, dass am Ende immer eine ganze Zahl
    steht. Der Sonderfall bleibt BF5 vorbehalten, dort ist er der Punkt.
    """
    return "/" in g["loesung_text"]


def _nicht_null(p, g) -> bool:
    return g["loesung_text"] != "0"


def _frage_gekuerzt(p, g) -> bool:
    """Kein «4/2» und kein «6/4» in der Aufgabenstellung.

    Die Ziehung würfelt Zähler und Nenner unabhängig, und ein ungekürzter
    Bruch in der FRAGE steht in keinem Lehrmittel. Für die Rechnung ist es
    gleichgültig, für die Glaubwürdigkeit nicht.
    """
    import re as _re
    for z, n in _re.findall(r"(\d+)/(\d+)", g["frage"]):
        if math.gcd(int(z), int(n)) > 1:
            return False
    return True


def _nenner_zahm(p, g) -> bool:
    """Der Hauptnenner muss im Kopf zu schaffen sein.

    Ohne diese Grenze entstehen Aufgaben wie 1/12 + 4/13 + 1/52 mit
    Hauptnenner 156. Rechnerisch korrekt, aber keine Kopfrechenaufgabe mehr
    — und Kapitel 2 ist die Grundlage, nicht die Kür.
    """
    import re as _re
    nenner = [int(n) for _, n in _re.findall(r"(\d+)/(\d+)", g["frage"])]
    if not nenner:
        return True
    hn = nenner[0]
    for n in nenner[1:]:
        hn = hn * n // math.gcd(hn, n)
    return hn <= 60


STANDARD = [fehler_eindeutig, _kein_ganzes, _nicht_null,
            _frage_gekuerzt, _nenner_zahm]


def _nenner_liste(p):
    """Die Nenner für alle Summanden — Zahl der Summanden aus dem Level."""
    n1, n2 = _nenner_paar(p)
    anzahl, f = p["anzahl"], p["f"]
    nenner = [n1, n2]
    while len(nenner) < anzahl:
        if p["stufe"] == "gleich":
            nenner.append(n1)
        elif p["stufe"] == "vielfaches":
            nenner.append(n1 * (len(nenner)))
        else:
            nenner.append(n2 * (len(nenner)))
    return nenner[:anzahl]


def _zaehler_liste(p, anzahl):
    """Zähler so, dass keine zwei Summanden identisch sind.

    Zwei gleiche Summanden mit gleichem Nenner heben sich bei Minus weg,
    und dann fällt «nur der erste Summand» mit der Lösung zusammen.
    """
    vorrat = [p["z1"], p["z2"], p["z3"]] + ZAEHLER
    raus = []
    for z in vorrat:
        if z not in raus:
            raus.append(z)
        if len(raus) == anzahl:
            break
    while len(raus) < anzahl:
        raus.append(max(raus) + 1)
    return raus


def _mach(p, zeichen_muster):
    anzahl = p["anzahl"]
    nenner = _nenner_liste(p)
    zaehler = _zaehler_liste(p, anzahl)
    glieder = list(zip(zaehler, nenner))
    zeichen = (zeichen_muster * anzahl)[:anzahl - 1]
    teile = [br(zaehler[0], nenner[0])]
    for i in range(1, anzahl):
        teile.append("+" if zeichen[i - 1] == "+" else "−")
        teile.append(br(zaehler[i], nenner[i]))
    return bau(glieder, zeichen, " ".join(teile))


def _paar(nr, beschreibung, bereiche, muster, extra_filter=()):
    return Bauform(nr, beschreibung, bereiche=bereiche,
                   bauen=lambda p, m=muster: _mach(p, m),
                   filter=STANDARD + list(extra_filter))


# ── Gleiche Nenner ───────────────────────────────────────────────────────
BF1 = _paar("BF1", "Addition, gleiche Nenner", GLEICH, "+")
BF2 = _paar("BF2", "Subtraktion, gleiche Nenner", GLEICH, "-")
BF3 = _paar("BF3", "Plus und Minus, gleiche Nenner", GLEICH, "+-")

# ── Ein Nenner ist Vielfaches des andern ─────────────────────────────────
BF4 = _paar("BF4", "Addition, ein Nenner ist Vielfaches", VIELFACHES, "+")
BF5 = _paar("BF5", "Subtraktion, ein Nenner ist Vielfaches", VIELFACHES, "-")
BF6 = _paar("BF6", "Plus und Minus, Vielfaches", VIELFACHES, "+-")

# ── Teilerfremde Nenner ──────────────────────────────────────────────────
BF7 = _paar("BF7", "Addition, teilerfremde Nenner", TEILERFREMD, "+")
BF8 = _paar("BF8", "Subtraktion, teilerfremde Nenner", TEILERFREMD, "-")
BF9 = _paar("BF9", "Plus und Minus, teilerfremde Nenner", TEILERFREMD, "+-")


# ── BF10 · Sonderfall: das Ergebnis ist eine ganze Zahl ──────────────────
#: Zerlegungen einer Primzahl in lauter VERSCHIEDENE Summanden. Nur mit
#: einem Primnenner steht jeder Summand von selbst gekürzt da — bei n = 6
#: wäre 2/6 dabei, und das gehört nicht in eine Aufgabenstellung.
ZERLEGUNG = {
    2: [(5, (1, 4)), (5, (2, 3)), (7, (2, 5)), (7, (3, 4)),
        (11, (4, 7)), (11, (5, 6))],
    3: [(7, (1, 2, 4)), (11, (1, 2, 8)), (11, (2, 3, 6)), (11, (1, 4, 6)),
        (13, (2, 4, 7)), (13, (1, 5, 7))],
    4: [(11, (1, 2, 3, 5)), (13, (1, 2, 4, 6)), (13, (1, 3, 4, 5)),
        (17, (2, 3, 5, 7)), (17, (1, 4, 5, 7))],
}


def bf10(p):
    """1/3 + 2/3 = 1. Wer immer einen Bruch erwartet, schreibt 3/3.

    WARUM ALLE NENNER GLEICH SIND — das ist keine Bequemlichkeit, sondern
    Rechnung. Soll z1/n1 + z2/n2 eine ganze Zahl ergeben und sollen beide
    Brüche gekürzt dastehen, dann MUSS n1 = n2 sein: aus
    z1·n2 + z2·n1 = k·n1·n2 folgt modulo n1, dass n1 den Ausdruck z1·n2
    teilt, und bei teilerfremden Nennern hiesse das z1 ≥ n1. Mit
    verschiedenen Nennern gibt es diese Aufgabe gar nicht. Das war beim
    ersten Anlauf der Grund, warum der Generator auf Level B und C nach
    dreihundert Versuchen aufgab.
    """
    anzahl = p["anzahl"]
    kandidaten = ZERLEGUNG[anzahl]
    n, zaehler = kandidaten[p["z1"] % len(kandidaten)]
    glieder = [(z, n) for z in zaehler]
    frage = " + ".join(br(z, n) for z in zaehler)
    return bau(glieder, "+" * (anzahl - 1), frage, extra=[
        F("nenner_stehen_gelassen", Rational(1, n),
          f"Die Zähler ergeben zusammen {n}, und {n}/{n} ist eins."),
        F("zaehler_summe_roh", Integer(sum(zaehler)),
          f"Die Zähler ergeben zusammen {sum(zaehler)} — das ist der Zähler, "
          f"nicht das Ergebnis."),
        F("nenner_summiert", Integer(n * anzahl),
          "Die Nenner werden nicht addiert."),
        F("einer_zu_viel", Integer(anzahl),
          "Das ist die Zahl der Summanden, nicht ihr Wert."),
        F("groesster_zaehler", Rational(max(zaehler), n),
          "Das ist nur der grösste der Summanden."),
    ])


def _ergibt_ganze_zahl(p, g) -> bool:
    return "/" not in g["loesung_text"] and g["loesung_text"] != "0"


def _summanden_verschieden(p, g) -> bool:
    """Zwei gleiche Summanden lassen zu viele Katalogeinträge zusammenfallen."""
    import re as _re
    teile = _re.findall(r"\d+/\d+", g["frage"])
    return len(set(teile)) == len(teile)


BF10 = Bauform("BF10", "Sonderfall: das Ergebnis ist eine ganze Zahl",
    bereiche=GLEICH, bauen=bf10,
    filter=[fehler_eindeutig, _ergibt_ganze_zahl, _frage_gekuerzt,
            _summanden_verschieden])


# ── BF11 · Sonderfall: das Ergebnis ist null ─────────────────────────────
def bf11(p):
    """3/4 − 3/4 = 0. Steht so im Lehrmittel, Aufgabe 39 b: 9/14 − 9/14.

    Ab drei Summanden heben sich die hinteren gegenseitig auf, damit die
    Aufgabe auf jedem Level anders aussieht und trotzdem null ergibt.
    """
    n, z, anzahl = p["n"], p["z1"], p["anzahl"]
    if anzahl == 2:
        glieder, zeichen = [(z, n), (z, n)], "-"
        frage = f"{br(z, n)} − {br(z, n)}"
    elif anzahl == 3:
        glieder, zeichen = [(z, n), (z, n), (z, n)], "-+"
        frage = f"{br(z, n)} − {br(z, n)} + {br(z, n)} − {br(z, n)}"
        glieder, zeichen = [(z, n), (z, n), (z, n), (z, n)], "-+-"
    else:
        glieder = [(z, n)] * 4
        zeichen = "-+-"
        frage = (f"{br(z, n)} − {br(z, n)} + {br(z, n)} − {br(z, n)}")
    if anzahl == 3:
        glieder, zeichen = [(z, n), (z, n), (z, n)], "+-"
        frage = f"{br(z, n)} + {br(z, n)} − {br(2 * z, n)}"
        glieder = [(z, n), (z, n), (2 * z, n)]
    return bau(glieder, zeichen, frage, extra=[
        F("bruch_abgeschrieben", Rational(z, n),
          "Was gleich viel ist, hebt sich weg. Es bleibt nichts."),
        F("eins", Integer(1), "Gleich minus gleich ist null, nicht eins."),
        F("nenner_als_antwort", Integer(n),
          "Das ist der Nenner. Die Zähler ergeben null."),
        F("zaehler_mal_zwei", Integer(2 * z),
          "Hier wird abgezogen, nicht verdoppelt."),
        F("minus_eins", Integer(-1),
          "Gleich minus gleich ist null, nicht minus eins."),
    ])


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


def _bruch_nicht_zu_klein(p, g) -> bool:
    """Bei «1/2 − 1/2» fallen zu viele Katalogeinträge auf 1 und 2 zusammen."""
    import re as _re
    treffer = _re.findall(r"(\d+)/(\d+)", g["frage"])
    if not treffer:
        return True
    z, n = int(treffer[0][0]), int(treffer[0][1])
    return z >= 2 and n >= 3


BF11 = Bauform("BF11", "Sonderfall: das Ergebnis ist null",
    bereiche=GLEICH, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_null, _frage_gekuerzt,
            _bruch_nicht_zu_klein])


# ── BF12 · Sonderfall: ein Summand ist eine ganze Zahl ───────────────────
def bf12(p):
    """3/4 + 1 — steht so im Lehrmittel im blauen Kasten auf Seite 50.

    Der Klassiker: die ganze Zahl wird vergessen oder als Zähler behandelt.
    """
    n1, n2 = _nenner_paar(p)
    anzahl = p["anzahl"]
    #: Die Zahl der BRUCH-Summanden wächst mit dem Level: einer, zwei, drei.
    #: Ohne das sähen A und B gleich aus — «max(2, anzahl - 1)» lieferte auf
    #: beiden Stufen zwei Brüche, und der Testlauf hat das beanstandet.
    zaehler = _zaehler_liste(p, anzahl - 1)
    glieder = [(zaehler[0], n1)]
    teile = [br(zaehler[0], n1)]
    for i in range(1, len(zaehler)):
        nn = n2 if i == 1 else n1 * (i + 1)
        glieder.append((zaehler[i], nn))
        teile += ["+", br(zaehler[i], nn)]
    glieder.append((p["f"], 1))
    teile += ["+", str(p["f"])]
    return bau(glieder, "+" * (len(glieder) - 1), " ".join(teile), extra=[
        F("ganze_zahl_vergessen",
          sum((Rational(z, n) for z, n in glieder[:-1]), Rational(0)),
          f"Die {p['f']} gehört mit ins Ergebnis."),
        F("als_zaehler_behandelt",
          sum((Rational(z, n) for z, n in glieder[:-1]), Rational(0))
          + Rational(p["f"], n1),
          f"{p['f']} ist eine ganze Zahl, kein Zähler. Als Bruch geschrieben "
          f"ist sie {p['f']}/1."),
    ])


BF12 = Bauform("BF12", "Sonderfall: ein Summand ist eine ganze Zahl",
    bereiche=VIELFACHES, bauen=bf12, filter=STANDARD)


S8 = Schablone(
    nr="S8", titel="Addition und Subtraktion von Brüchen",
    lektionen="2.3 – 2.6", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Anzahl der Summanden",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Nur gleichnamige Brüche lassen sich addieren. Erst den "
              "Hauptnenner suchen, dann erweitern, dann die Zähler "
              "verrechnen — der Nenner bleibt stehen."),
)
