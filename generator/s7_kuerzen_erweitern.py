# -*- coding: utf-8 -*-
"""
S7 · Kürzen und Erweitern   (Lektionen 2.1 – 2.2)

    «Kürze so weit wie möglich.»
    16/40   →   2/5
    25/35   →   5/7

Quelle: Lehrmittel A, Kapitel 1.5 «Brüche und Dezimalbrüche», Seiten 45–47,
Aufgaben 10 bis 20. Die Bauformen bilden genau die dort vorkommenden Formen
ab — deshalb sind auch die Produktschreibweise (Aufgabe 16 d–f) und der
gemischte Bruch (Aufgabe 16 b) dabei, obwohl beide auf den ersten Blick
exotisch wirken.

LEVELACHSE (Teil 2): **Struktur der Zerlegung**, nicht Grösse der Zahlen.

    A   ein einziger Kürzungsfaktor, sofort sichtbar         16/40
    B   der Faktor ist zusammengesetzt, es braucht zwei      72/84
        Schritte oder das Erkennen des ggT
    C   Zähler und Nenner stehen als Produkt da, oder es     (5·7·16)/(15·4·21)
        ist ein gemischter Bruch, oder der Bruch ist
        unecht und muss danach noch umgeschrieben werden

Die Zahlenvorräte sind auf allen drei Stufen dieselben. Was sich ändert, ist
die Zahl der Schritte, nicht die Grösse der Brüche — sonst hiesse Level C
bloss «grössere Zahlen», und das misst nichts.

WARUM DIE LÖSUNG ALS BRUCH GEPRÜFT WIRD, NICHT ALS KOMMAZAHL:
16/40 und 0.4 sind derselbe Wert, `Zielform.GEKUERZT` verlangt aber die
gekürzte Bruchform. Wer 0.4 eintippt, bekommt UNFERTIG statt FALSCH — das
ist die richtige Rückmeldung, denn gerechnet hat er korrekt, nur nicht zu
Ende gekürzt. Genau diese Unterscheidung ist der Sinn der Lektion.
"""
from __future__ import annotations

import math

from sympy import Integer, Rational

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .schablone import Bauform, Schablone

VARS: set[str] = set()          # reine Zahlenbrüche, keine Variablen
ANLEITUNG = "Kürze so weit wie möglich."


def F(schluessel: str, ergebnis, text: str) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def bruch(z: int, n: int) -> str:
    """«16/40» — so, wie der Schüler es eintippt."""
    return f"{z}/{n}"


def _kleinster(g: int) -> int:
    """Kleinster Primfaktor von g. Für g = 12 also 2, nicht 12."""
    d = 2
    while d * d <= g:
        if g % d == 0:
            return d
        d += 1
    return g


def _siebe(katalog, ziel):
    """Einträge weg, die wertgleich mit der Lösung oder untereinander sind.

    Ohne das diagnostiziert die App eine richtige Antwort als Fehler. Der
    Fall ist hier besonders leicht zu produzieren: bei 16/40 ergibt «nur
    Zähler gekürzt» und «nur mit 2 gekürzt» schnell dasselbe.

    ZWEITE, WENIGER OFFENSICHTLICHE BEDINGUNG — auf zwei Stellen gerundet
    darf ein Eintrag ebenfalls nicht mit der Lösung zusammenfallen. Die
    Prüfung akzeptiert gerundete Dezimalantworten, und 31/40 rundet auf
    0.78, genau wie 7/9. Ein solcher Katalogeintrag käme im Betrieb als
    RICHTIG zurück, obwohl er als Fehler gedacht war. Das ist beim Bauen
    dieser Schablone dreimal passiert, bevor die Zeile hier stand.
    """
    raus, gesehen = [], set()
    zielwert = Rational(ziel)
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        wert = Rational(e)
        if wert == zielwert or str(wert) in gesehen:
            continue
        # Nicht nur die gerundete Form vergleichen, sondern den ABSTAND.
        # Die Korrektur akzeptiert Dezimalantworten auf zwei Stellen; liegen
        # zwei Werte näher als eine Hundertstel beieinander, kann derselbe
        # Tastendruck beide treffen. round() allein reicht nicht, weil 0.075
        # und 0.0833 verschieden runden und trotzdem beide als 0.08 getippt
        # werden. Genau daran ist ein Katalogeintrag als «richtig» erkannt
        # worden.
        if abs(float(wert) - float(zielwert)) < 0.01:
            continue
        gesehen.add(str(wert))
        raus.append(f)
    return raus


TIPPS = [
    "Suche eine Zahl, durch die Zähler UND Nenner teilbar sind.",
    "Kürzen heisst: beide durch dieselbe Zahl teilen. Der Wert bleibt gleich.",
    "",
]


def bau(z: int, n: int, frage: str, extra=(), schritte=None, tipps=None):
    """Baut die Aufgabe aus dem ungekürzten Bruch z/n."""
    g = math.gcd(z, n)
    loesung = Rational(z, n)
    text = (str(loesung.p) if loesung.q == 1
            else f"{loesung.p}/{loesung.q}")

    katalog = list(extra) + [
        # Ein Kürzungsschritt zu wenig: nur durch den kleinsten Primfaktor
        # geteilt statt durch den ggT. Das ist der häufigste Fehler bei
        # zusammengesetzten Faktoren und der Grund, warum es Level B gibt.
        F("nur_ein_schritt",
          Rational(z // _kleinster(g), n // _kleinster(g)) if g > 1 else None,
          "Das lässt sich noch weiter kürzen — es gibt einen grösseren "
          "gemeinsamen Teiler."),
        F("nur_zaehler_geteilt", Rational(z // g, n) if g > 1 else None,
          f"Beim Kürzen wird auch der Nenner geteilt: {n} : {g} = {n // g}."),
        F("nur_nenner_geteilt", Rational(z, n // g) if g > 1 else None,
          f"Beim Kürzen wird auch der Zähler geteilt: {z} : {g} = {z // g}."),
        F("gestuerzt", Rational(n, z) if z != 0 else None,
          "Zähler und Nenner sind vertauscht. Oben steht der Zähler."),
        F("subtrahiert", Integer(abs(z - n)),
          "Kürzen heisst teilen, nicht abziehen."),
        F("halb_gekuerzt", Rational(z // 2, n // 2)
          if (g > 2 and z % 2 == 0 and n % 2 == 0) else None,
          "Das war ein Schritt in die richtige Richtung, aber es geht noch "
          "weiter."),
        F("faktor_als_antwort", Integer(g) if g > 1 else None,
          f"{g} ist die Zahl, durch die gekürzt wird — nicht das Ergebnis."),
        F("nur_zaehler_hingeschrieben", Integer(z // g),
          "Das ist nur der neue Zähler. Der Bruch braucht auch einen Nenner."),
        F("addiert", Integer(z + n),
          "Kürzen heisst teilen. Zähler und Nenner werden nicht addiert."),
        F("nenner_allein", Integer(n // g),
          "Das ist nur der neue Nenner. Gefragt ist der ganze Bruch."),
        F("um_eins_verrechnet", Rational(z + 1, n) if n > 1 else None,
          "Beim Teilen darf nichts dazukommen — Zähler und Nenner werden "
          "nur durch dieselbe Zahl geteilt."),
        F("beide_minus_eins", Rational(z - 1, n - 1) if n > 2 and z > 1 else None,
          "Kürzen heisst teilen, nicht von beiden dasselbe abziehen."),
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
        "schritte": schritte or [
            ("Gemeinsamen Teiler suchen",
             f"{z} und {n} sind beide durch {g} teilbar" if g > 1
             else f"{z} und {n} haben keinen gemeinsamen Teiler"),
            ("Zähler teilen", f"{z} : {g} = {z // g}" if g > 1 else str(z)),
            ("Nenner teilen", f"{n} : {g} = {n // g}" if g > 1 else str(n)),
            ("Ergebnis", text),
        ],
        "tipps": tipps or TIPPS,
    }


# ── Zahlenvorräte ────────────────────────────────────────────────────────
# Auf allen drei Level dieselben. Die Levelachse trägt die STRUKTUR.
KLEIN = [2, 3, 4, 5, 6, 7]
FAKTOR = [2, 3, 4, 5, 6]
GRUND = [(2, 5), (3, 4), (2, 7), (5, 7), (3, 8), (4, 9), (5, 6), (3, 10),
         (7, 9), (2, 9), (5, 8), (4, 7)]

#: Die Levelachse steckt in «form», nicht in den Zahlen. Die Zahlenvorräte
#: sind auf allen drei Stufen identisch — was sich ändert, ist die Zahl der
#: Schritte und die Schreibweise:
#:     einfach   ein Bruch, ein Kürzungsschritt                12/30
#:     produkt   Zähler und Nenner als Produkt, EIN gemeinsamer  (3 · 4)/(5 · 4)
#:               Faktor zum Streichen
#:     doppelt   Produkt mit ZWEI gemeinsamen Faktoren —     (3 · 4 · 5)/(7 · 4 · 5)
#:               entspricht Aufgabe 16 d–f im Lehrmittel
BEREICH_A = {"grund": GRUND, "f": FAKTOR, "g": KLEIN, "form": ["einfach"]}
BEREICH_B = {"grund": GRUND, "f": FAKTOR, "g": KLEIN, "form": ["produkt"]}
BEREICH_C = {"grund": GRUND, "f": FAKTOR, "g": KLEIN, "form": ["doppelt"]}


def _zahlen(p, zg, ng):
    """Gibt (zaehler, nenner, frage) je nach Aufbaustufe zurück.

    Genau hier sitzt die Levelachse dieser Schablone. Ohne diese Funktion
    unterscheiden sich A, B und C nur in der Grösse der gezogenen Zahlen —
    und das beanstandet der Testlauf zu Recht, denn dann misst das Level
    nichts über das Können.
    """
    f, g, form = p["f"], p["g"], p["form"]
    if form == "einfach":
        z, n = zg * f, ng * f
        return z, n, bruch(z, n)
    if form == "produkt":
        return zg * f, ng * f, f"({zg} · {f})/({ng} · {f})"
    # doppelt
    return (zg * f * g, ng * f * g,
            f"({zg} · {f} · {g})/({ng} · {f} · {g})")

STANDARD = [fehler_eindeutig]


# ── BF1 · Ein Faktor, sofort sichtbar ────────────────────────────────────
def bf1(p):
    (zg, ng) = p["grund"]
    z, n, frage = _zahlen(p, zg, ng)
    return bau(z, n, frage)


BF1 = Bauform("BF1", "Bruch kürzen",
    bereiche={"A": BEREICH_A, "B": BEREICH_B, "C": BEREICH_C},
    bauen=bf1, filter=STANDARD)


# ── BF4 · Sonderfall: schon gekürzt ──────────────────────────────────────
def bf4(p):
    """25/35 lässt sich kürzen — 25/36 nicht. Beides muss vorkommen, sonst
    lernt der Schüler «hier ist immer etwas zu tun» statt hinzuschauen.

    Die Aufbaustufe steckt in der Schreibweise: auf C steht derselbe nicht
    kürzbare Bruch als Produkt da, und der Schüler muss erst ausrechnen,
    bevor er sieht, dass nichts geht.
    """
    (zg, ng), form = p["grund"], p["form"]
    z, n = zg, ng
    f, g = p["f"], p["g"]
    # In Produktform stehen VERSCHIEDENE Faktoren oben und unten — sonst
    # liesse sich doch etwas streichen, und die Bauform verlöre genau das,
    # wofür es sie gibt: die Aufgabe, bei der nichts zu tun ist.
    if form == "produkt":
        z, n = zg * f, ng * (f + 1)
        frage = f"({zg} · {f})/({ng} · {f + 1})"
    elif form == "doppelt":
        z, n = zg * f * g, ng * (f + 1) * (g + 1)
        frage = f"({zg} · {f} · {g})/({ng} · {f + 1} · {g + 1})"
    else:
        frage = bruch(z, n)
    # KEIN eigener Katalogeintrag hier. «Trotzdem gekürzt» klingt naheliegend,
    # lässt sich aber nicht als EIN Wert hinschreiben: wer bei 12/49 kürzen
    # will, kann auf beliebig viel Falsches kommen. Ein erfundener Wert wäre
    # im Testlauf mit einer richtigen Antwort zusammengefallen — genau das ist
    # beim ersten Anlauf passiert. Die sechs allgemeinen Einträge greifen hier.
    return bau(z, n, frage, extra=[], schritte=[
        ("Gemeinsamen Teiler suchen", f"{z} und {n} haben keinen"),
        ("Ergebnis", bruch(z, n)),
    ])


def _nichts_zu_kuerzen(p, g) -> bool:
    """Sicherheitsnetz für BF4: die Frage muss wirklich unkürzbar sein.

    Bei Produktschreibweise können sich die gezogenen Faktoren zufällig doch
    teilen — (3 · 4)/(5 · 5) ist harmlos, (3 · 4)/(6 · 5) nicht. Ohne diesen
    Filter würde die Bauform gelegentlich das Gegenteil dessen zeigen, wofür
    es sie gibt.
    """
    import math as _m
    import re as _re
    frage = g["frage"]
    zahlen = [int(x) for x in _re.findall(r"\d+", frage)]
    if "/" not in frage:
        return True
    oben, unten = frage.split("/", 1)
    zo = [int(x) for x in _re.findall(r"\d+", oben)]
    zu = [int(x) for x in _re.findall(r"\d+", unten)]
    prod_o, prod_u = 1, 1
    for x in zo:
        prod_o *= x
    for x in zu:
        prod_u *= x
    return _m.gcd(prod_o, prod_u) == 1


BF4 = Bauform("BF4", "Sonderfall: lässt sich nicht kürzen",
    bereiche={"A": BEREICH_A, "B": BEREICH_B, "C": BEREICH_C},
    bauen=bf4, filter=STANDARD + [_nichts_zu_kuerzen])


# ── BF5 · Sonderfall: Ergebnis ist eine ganze Zahl ───────────────────────
def bf5(p):
    """24/8 = 3. Wer immer einen Bruch erwartet, schreibt 3/1.

    Aufbaustufen wie bei BF1: erst ein Schritt, dann ein zusammengesetzter
    Faktor, dann Produktschreibweise.
    """
    f, g, form = p["f"], p["g"], p["form"]
    if form == "einfach":
        n, z = f, f * g
        frage = bruch(z, n)
    elif form == "produkt":
        n, z = f, f * g
        frage = f"({f} · {g})/({f} · 1)"
    else:
        n, z = f * 2, f * g * 2
        frage = f"({f} · {g} · 2)/({f} · 1 · 2)"
    return bau(z, n, frage, extra=[
        F("als_bruch_gelassen", None,
          f"{z} : {n} geht auf. Schreib die ganze Zahl."),
    ], schritte=[
        ("Geht die Division auf?", f"{z} : {n} = {z // n}"),
        ("Ergebnis", str(z // n)),
    ])


BF5 = Bauform("BF5", "Sonderfall: das Ergebnis ist eine ganze Zahl",
    bereiche={"A": BEREICH_A, "B": BEREICH_B, "C": BEREICH_C},
    bauen=bf5, filter=STANDARD)


S7 = Schablone(
    nr="S7", titel="Kürzen und Erweitern",
    lektionen="2.1 – 2.2", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Struktur der Zerlegung",
    bauformen=[BF1, BF4, BF5],
    kernidee=("Kürzen heisst: Zähler UND Nenner durch dieselbe Zahl teilen. "
              "Der Wert des Bruchs ändert sich dabei nicht."),
)
