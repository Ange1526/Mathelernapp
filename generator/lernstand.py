# -*- coding: utf-8 -*-
"""
Lernstand — Mastery pro Bauform, Level pro Kapitel, Lückensuche.

Behebt drei Dinge, die dem Ziel «am Schluss löst jeder den Test fehlerfrei»
entgegenstanden:

1  QUOTENLOGIK LIESS LÜCKEN BESTEHEN.
   Bisher: 10 Aufgaben, 80 % richtig, Aufstieg. Wer ausgerechnet die
   Minusklammer nie konnte, stieg trotzdem auf. Neu: jede Bauform braucht ihr
   eigenes Häkchen. Das Level gilt erst als fertig, wenn alle sitzen.

2  DAS LEVEL HING AM SCHÜLER, NICHT AN DER LEKTION.
   Bisher: ein `current_level` für alles. Wer bei Brüchen schwach und beim
   Faktorisieren stark ist, bekam für beides dasselbe — einmal Überforderung,
   einmal Langeweile. Neu: ein Level pro Kapitel.

3  KEINE LÜCKENSUCHE.
   Bisher: wer scheitert, bekommt dieselbe Aufgabe nochmals. Neu: wer an
   derselben Bauform mehrfach scheitert, wird auf das Kapitel verwiesen, das
   diese Lektion voraussetzt.

Dieses Modul enthält nur die Logik, keine Datenbank. Die Modelle stehen in
app.py, damit dein bestehendes Schema unangetastet bleibt — es kommen nur
zwei Tabellen dazu.
"""
from __future__ import annotations

import random

#: Wie oft eine Bauform richtig gelöst sein muss, damit sie als sicher gilt.
#: Zwei, weil einmal Glück sein kann und drei die Lektion unnötig lang macht.
MASTERY = 2

#: Nach so vielen Fehlversuchen an DERSELBEN Bauform greift die Lückensuche.
LUECKE_AB = 3

#: Voraussetzungen aus der Lektionslandkarte v5.
#: Kapitel -> Liste der Kapitel, die es voraussetzt.
#: Wer hier scheitert, hat die Lücke meist eine Stufe darunter.
VORAUSSETZUNGEN = {
    "6.1":  ["5.7", "4.8"],     # Punkt vor Strich mit Variablen
    "6.5":  ["6.1"],            # zuerst ausrechnen koennen, dann zusammenfassen
    "12.1": ["11.6"],           # Faktorisieren
}

#: Klartext für die Rückmeldung an den Schüler.
KAPITEL_KLARTEXT = {
    "4.8":  "Gleichartige Terme zusammenfassen",
    "5.7":  "Produkte vereinfachen",
    "11.6": "Ausmultiplizieren und zusammenfassen",
    "6.1":  "Punkt vor Strich mit Variablen",
    "6.5":  "Ausrechnen und danach zusammenfassen",
    "12.1": "Faktorisieren",
}

LEVELS = ("A", "B", "C")


def naechstes_level(level: str) -> str | None:
    i = LEVELS.index(level)
    return LEVELS[i + 1] if i + 1 < len(LEVELS) else None


def vorheriges_level(level: str) -> str | None:
    i = LEVELS.index(level)
    return LEVELS[i - 1] if i > 0 else None


class Ziehung:
    """Welche Bauform kommt als Nächstes?

    Reihum, nicht zufällig. Der Generator mischt die Bauformen des Levels und
    teilt sie der Reihe nach aus; erst wenn alle durch sind, mischt er neu.

    Warum: bei zufälliger Ziehung mit Zurücklegen sieht ein Schüler bei zwölf
    Aufgaben im Schnitt nur knapp acht von zwölf Bauformen. Vier bekommt er nie
    zu Gesicht — und genau die fehlen ihm dann in der Prüfung.
    """

    def __init__(self, alle: list[str], gemeistert: set[str],
                 offen: list[str] | None = None, rng=None):
        self.alle = alle
        self.gemeistert = gemeistert
        self.offen = [b for b in (offen or []) if b in alle and b not in gemeistert]
        self.rng = rng or random.Random()

    def naechste(self) -> str | None:
        kandidaten = [b for b in self.alle if b not in self.gemeistert]
        if not kandidaten:
            return None                      # Level fertig
        if not self.offen:
            self.offen = kandidaten[:]
            self.rng.shuffle(self.offen)
        return self.offen.pop(0)


def bewerten(treffer: int, fehler: int, richtig: bool) -> tuple[int, int, bool]:
    """Gibt (treffer, fehler, gemeistert) zurück.

    Ein Fehler setzt die Bauform zurück — nicht auf null, sondern um eins.
    Wer zweimal richtig und dann einmal falsch antwortet, hat nicht alles
    verloren, muss aber nochmals zeigen, dass es sitzt.
    """
    if richtig:
        treffer += 1
        return treffer, fehler, treffer >= MASTERY
    return max(0, treffer - 1), fehler + 1, False


def luecke_suchen(kapitel: str, fehler_in_folge: int) -> dict | None:
    """Wo liegt die Lücke, wenn jemand an einer Bauform hängen bleibt?

    Gibt das Kapitel zurück, das die aktuelle Lektion voraussetzt — oder None,
    wenn es keine Voraussetzung gibt oder noch zu früh ist.
    """
    if fehler_in_folge < LUECKE_AB:
        return None
    vor = VORAUSSETZUNGEN.get(kapitel) or []
    if not vor:
        return None
    ziel = vor[0]
    return {
        "kapitel": ziel,
        "name": KAPITEL_KLARTEXT.get(ziel, ziel),
        "text": (f"Diese Aufgabenart macht dir mehrfach Mühe. Das liegt oft "
                 f"nicht an der Aufgabe selbst, sondern an dem, was sie "
                 f"voraussetzt: «{KAPITEL_KLARTEXT.get(ziel, ziel)}». "
                 f"Willst du das zuerst nochmals anschauen?"),
    }


def fortschritt(alle: list[str], gemeistert: set[str]) -> tuple[int, int, int]:
    """(gemeistert, gesamt, Prozent) — für den Balken in der Lektion."""
    g, ges = len(gemeistert & set(alle)), len(alle)
    return g, ges, int(g / ges * 100) if ges else 0
