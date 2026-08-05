# -*- coding: utf-8 -*-
"""
Anbindung an die Flask-App.

Ersetzt `generate_math_task()`. Der Unterschied: der alte Generator lieferte
nur (Frage, Lösung als Float). Damit gingen Zielform und Fehlerkatalog
verloren, sobald die Aufgabe in der Session lag — `check()` musste die Aufgabe
aus dem blossen Float neu bauen.

Hier wird stattdessen die GANZE Aufgabe in die Session gelegt, als einfaches
Dictionary aus Strings. `aufgabe_aus_session()` baut daraus wieder ein
`korrektur.Aufgabe` mit Zielform und Fehlerkatalog.

Zwei Routen sind betroffen:
    lektion()  ->  neue_aufgabe(...)      statt generate_math_task(...)
    check()    ->  aufgabe_aus_session(...) statt aufgabe_aus_generator(...)
"""
from __future__ import annotations

import random

from sympy import sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .s10_klammern import S10
from .s8_wurzeln import S26, S27, S28, S29
from .s16_gleichartig import S16
from .s15_s17_sorten import S15, S17
from .s3_terme import S12, S13, S14
from .s5_produkte import S18, S19
from .s7_potenzen import S7
from .s2_grundoperationen import S2
from .s4_faktorisieren import S4

#: Kapitelnummer in der App  ->  Schablone
#: Die Nummern folgen deiner Lektionslandkarte.
KAPITEL = {
    "6.1": S2,      # Grundoperationen — Erhebung 2a, 2b, 2c
    # Kapitel 3 — das Fundament: 4.1 setzt 3.11 voraus.
    "3.1": S12,     # Zahlen einsetzen        3.1 – 3.3
    "3.4": S13,     # Variablen verknuepfen   3.4 – 3.9
    "3.10": S14,    # Zahlen und eine Variable 3.10 – 3.11
    # Kapitel 5 — reine Produkte, Levelachse ist das Vorzeichen.
    "5.1": S18,     # Variablen multiplizieren   5.1 – 5.4
    "5.5": S19,     # Produkte mit Vorzeichen    5.5 – 5.8 — Erhebung 2b
    # Kapitel 4 vollstaendig: drei Schablonen statt einer.
    "4.1": S15,     # Sorten erkennen        4.1 · 4.7
    "4.2": S16,     # Zusammenfassen         4.2 – 4.6 · 4.8 — Ruecksprungziel
    "4.9": S17,     # Produkte als Sorten    4.9 — Erhebung 2a
    "7.1": S7,      # Potenzen           — Erhebung 3c, Ruecksprungziel 7.10
    "10.1": S10,    # Klammern           — Vorstufe zu 2b und 3d
    "12.1": S4,     # Faktorisieren    — Erhebung 4a bis 4d
    # Kapitel 8 Wurzeln — bringt die Erhebungsteilaufgaben 3a, 3b und 3e.
    "8.1": S26,     # Wurzeln verstehen        8.1 – 8.2
    "8.3": S27,     # Wurzel aus einer Summe   8.3 · 8.7   — Erhebung 3b
    "8.4": S28,     # Wurzelgesetze            8.4 – 8.8   — Erhebung 3a
    "8.9": S29,     # Wurzel mit Variable      8.9         — Erhebung 3e
}


def kernidee(kapitel: str) -> str:
    """Teil 6 der Schablone. Wird beim Einstieg einmal gezeigt."""
    s = KAPITEL.get(kapitel)
    return s.kernidee if s else ""

#: Für die Kapitelübersicht in der App
KAPITEL_NAMEN = {nr: s.titel for nr, s in KAPITEL.items()}

#: Alle Variablen, die in den Schablonen vorkommen. Der Parser muss sie kennen.
ALLE_VARIABLEN = {"a", "b", "c", "d", "m", "n", "p", "q", "r", "s",
                  "u", "v", "w", "x", "y", "z"}

_rng = random.Random()


def neue_aufgabe(kapitel: str, level: str, bauform: str | None = None) -> dict:
    """Eine neue Aufgabe erzeugen und als Session-Dictionary zurückgeben.

    `bauform` kommt aus der Reihum-Ziehung. Ohne Angabe wird gewürfelt —
    dann fehlt allerdings die Garantie, dass der Schüler alle Bauformen sieht.
    """
    schablone = KAPITEL[kapitel]
    moeglich = [b.nr for b in schablone.bauformen_fuer(level)]
    if not moeglich:
        raise ValueError(f"{schablone.nr} hat kein Level {level}")
    nr = bauform if bauform in moeglich else _rng.choice(moeglich)
    e = schablone.erzeugen(nr, level, _rng)

    return {
        "schablone": schablone.nr,
        "bauform": e.bauform,
        "level": e.level,
        "anleitung": e.anleitung,
        "frage": e.frage,
        "loesung": str(e.aufgabe.loesung.expr),
        "loesung_text": e.loesung_text,
        "zielform": e.aufgabe.zielform.value,
        "fehler": [[f.schluessel, str(f.ergebnis.expr), f.text]
                   for f in e.aufgabe.fehlerkatalog],
        "tipps": e.tipps,
        "schritte": [[was, wie] for was, wie in e.schritte],
    }


def aufgabe_aus_session(daten: dict) -> Aufgabe:
    """Session-Dictionary  ->  korrektur.Aufgabe mit Zielform und Katalog.

    Die Symbole werden über `symbole()` erzeugt, nicht über `symbols()` —
    sonst hebt sich antwort − lösung nie auf (Falle 1).
    """
    umgebung = {name: sym for name, sym in
                zip(sorted(ALLE_VARIABLEN),
                    symbole(" ".join(sorted(ALLE_VARIABLEN))))}

    def lesen(text: str):
        return sympify(text, locals=umgebung)

    return Aufgabe(
        loesung=Loesung.zahl(lesen(daten["loesung"])),
        variablen=set(ALLE_VARIABLEN),
        zielform=Zielform(daten.get("zielform", "beliebig")),
        fehlerkatalog=[Fehler(s, Loesung.zahl(lesen(e)), t)
                       for s, e, t in daten.get("fehler", [])],
    )


def tipp_text(daten: dict, stufe: int) -> str:
    """Gestufte Tipps. Stufe 1 nennt die Regel, 3 macht den Schritt vor."""
    tipps = daten.get("tipps") or []
    if not tipps:
        return ""
    return tipps[min(max(stufe, 1), len(tipps)) - 1]


def loesungsweg(daten: dict) -> list[tuple[str, str]]:
    return [(was, wie) for was, wie in daten.get("schritte", [])]
