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
from .s4_faktorisieren import S4
from .s6_punktrechnung import S20, S21
from .s22_s23_potenzen import S22, S23
from .s24_s25_potenzgesetze import S24, S25
from .s9_division import S30, S31, S32
from .s45_gleichungen import S45
from .s46_s47_klammern import S46
from .s47_brueche import S47
from .s14_bruchterme import S49
from .s50_s51_bruchterme import S50, S51
from .s60_mischen import S60

#: Kapitelnummer in der App  ->  Schablone
#: Die Nummern folgen deiner Lektionslandkarte.
KAPITEL = {
    # Kapitel 6 — S20 und S21 haben S2 hier abgeloest.
    "6.1": S20,     # Punkt vor Strich mit Variablen        6.1 – 6.4
    "6.5": S21,     # Ausrechnen und zusammenfassen         6.5 – 6.7 — Erhebung 2a
    # Kapitel 9 — S30, S31 und S32 haben S2 endgueltig abgeloest. Damit ist
    # S2 an keiner Lektion mehr eingetragen.
    "9.1": S30,     # Terme dividieren, einfache Faelle   9.1 – 9.3
    "9.4": S31,     # Monome mit Potenzen dividieren      9.4 – 9.5 — Erhebung 2c
    "9.6": S32,     # Division in laengeren Termen        9.6      — Erhebung 2c
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
    # Kapitel 7 — S22 bis S25 haben S7 abgeloest. 7.10 ist das dritte
    # haeufige Ruecksprungziel im Netz und liegt jetzt bei S25.
    "7.1": S22,     # Potenzen verstehen            7.1 – 7.2
    "7.3": S23,     # Potenz vor Punkt vor Strich   7.3 – 7.4 — Erhebung 3c
    "7.5": S24,     # Potenzgesetze                 7.5 – 7.8
    "7.9": S25,     # Potenz eines Produkts         7.9 – 7.10 — Vorstufe 3e
    # Kapitel 13 — Gleichungen. S45 deckt 13.1 bis 13.4 ab.
    "13.1": S45,    # Einfache lineare Gleichungen  13.1 – 13.4
    "13.5": S46,    # Klammern, Variablen beidseitig 13.5 – 13.6 — Erhebung 1a
    "13.7": S47,    # Loesung als Bruch              13.7 – 13.9 — Erhebung 1a
    # Kapitel 14 — Bruchterme. 14.1, 14.2, 14.5 und 14.8 fehlen: dafuer
    # waere S48 noetig, das nur in einer Kurzfassung mit sechs Bauformen
    # vorliegt. Erhebungsaufgabe 5a haengt an 14.8 und ist darum noch
    # nicht uebbar.
    "14.3": S49,    # Bruchterme kuerzen             14.3 – 14.4 — Erhebung 5b
    "14.6": S50,    # Addieren bei gleichem Nenner   14.6 – 14.7
    "14.9": S51,    # Mal, geteilt, Doppelbruch      14.9 – 14.11 — Erhebung 5c
    "10.1": S10,    # Klammern           — Vorstufe zu 2b und 3d
    "12.1": S4,     # Faktorisieren    — Erhebung 4a bis 4d
    # Kapitel 8 Wurzeln — bringt die Erhebungsteilaufgaben 3a, 3b und 3e.
    "8.1": S26,     # Wurzeln verstehen        8.1 – 8.2
    "8.3": S27,     # Wurzel aus einer Summe   8.3 · 8.7   — Erhebung 3b
    "8.4": S28,     # Wurzelgesetze            8.4 – 8.8   — Erhebung 3a
    "8.9": S29,     # Wurzel mit Variable      8.9         — Erhebung 3e
    # Mischaufgaben. Bewusst KEIN Eintrag in netz.SCHABLONE_FUER: sie sind
    # keine Lektion auf dem Weg, sondern die Stufe darueber. Erreichbar ueber
    # /gemischt und ueber die Vertiefung, und erst dann, wenn die beteiligten
    # Kapitel sicher sind.
    "16.1": S60,    # zwei bis drei Kapitel in einer Aufgabe
}

#: Welche Kapitel muessen sitzen, damit eine Mischaufgabe ueberhaupt fair ist?
#: Aus den Bauformen von S60: Wurzeln, Potenzen, Produkte, Division,
#: Klammern und das Zusammenfassen. Ohne diese Pruefung bekaeme ein Anfaenger
#: nach der ersten Lektion eine Aufgabe mit drei fremden Regeln.
MISCHEN = "16.1"
MISCH_VORAUSSETZUNG = ["4.2", "5.1", "7.1", "8.1", "9.1", "10.1"]


def mischen_moeglich(sichere_kapitel) -> bool:
    """Mindestens vier der sechs Grundlagen muessen sitzen.

    Vier statt sechs, weil sonst niemand vor der letzten Studienwoche
    hinkommt — und die Mischaufgaben sind genau das, was den Starken
    weiterbringt.
    """
    da = sum(1 for k in MISCH_VORAUSSETZUNG if k in sichere_kapitel)
    return da >= 4


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
