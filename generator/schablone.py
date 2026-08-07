# -*- coding: utf-8 -*-
"""
Schablonen-Struktur für den Aufgabengenerator.

Eine BAUFORM ist der Bauplan EINER Aufgabenart. Sie kennt:
  - die Parameterbereiche pro Level A/B/C
  - die Bauvorschrift: Parameter -> Aufgabe
  - die Qualitätsfilter, die hässliche Zufallsaufgaben verwerfen

Aus einer Bauform entsteht bei jedem Aufruf eine neue Aufgabe — mitsamt
Musterlösung, Zielform und vorausberechnetem Fehlerkatalog. Die App muss die
Aufgabe deshalb nie verstehen: sie hat sie selbst gebaut.

Rückgabe ist ein `korrektur.Aufgabe`, das direkt an `auswerten()` geht.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from korrektur import Aufgabe as KorrekturAufgabe

LEVELS = ("A", "B", "C")


@dataclass
class ErzeugteAufgabe:
    """Was der Generator liefert: Anzeigetext + Prüfobjekt + Didaktik."""
    schablone: str                  # "S42"
    bauform: str                    # "BF3"
    level: str                      # "A" | "B" | "C"
    anleitung: str                  # "Klammere so viele Faktoren wie möglich aus."
    frage: str                      # "12a² − 8a"
    aufgabe: KorrekturAufgabe       # geht an korrektur.auswerten()
    loesung_text: str = ""          # "4a(3a − 2)" — Musterlösung in Schülerschreibweise
    schritte: list[tuple[str, str]] = field(default_factory=list)
    tipps: list[str] = field(default_factory=list)
    parameter: dict = field(default_factory=dict)

    def protokoll(self) -> dict:
        """Felder für B1. Die Frage im Wortlaut MUSS mit — sonst weiss die
        Lehrperson beim Knopf «verstehe ich nicht» nachher nicht, worum es ging."""
        return {"schablone": self.schablone, "bauform": self.bauform,
                "level": self.level, "frage": self.frage,
                "loesung": str(self.aufgabe.loesung.expr),
                "parameter": {k: str(v) for k, v in self.parameter.items()}}


@dataclass
class Bauform:
    nr: str
    beschreibung: str
    #: {"A": {"g": [2,3], "u": [1,2,3]}, "B": {...}}  — Level über Bereiche
    bereiche: dict[str, dict]
    #: parameter -> dict(frage=..., aufgabe=..., schritte=..., tipps=...)
    bauen: Callable[[dict], dict]
    #: (parameter, gebaut) -> bool.  False = verwerfen und neu würfeln
    filter: list[Callable[[dict, dict], bool]] = field(default_factory=list)
    #: Nicht jede Bauform passt auf jedes Level (Regel 5).
    levels: tuple[str, ...] = LEVELS

    MAX_VERSUCHE = 300

    def erzeugen(self, level: str, rng: random.Random,
                 schablone: str, anleitung: str) -> ErzeugteAufgabe:
        if level not in self.levels:
            raise ValueError(f"{self.nr} hat kein Level {level}")
        bereich = self.bereiche[level]
        for _ in range(self.MAX_VERSUCHE):
            p = {name: rng.choice(werte) for name, werte in bereich.items()}
            g = self.bauen(p)
            if all(f(p, g) for f in self.filter):
                return ErzeugteAufgabe(
                    schablone=schablone, bauform=self.nr, level=level,
                    # Eine Bauform darf die Anleitung ueberschreiben. Gebraucht
                    # wird das in Kapitel 1: dort gehoert der Wortlaut der
                    # Aufgabe («Wie heisst die Gegenzahl von −7?») nach OBEN
                    # in die Anleitung, damit unten nur die Zahl steht — in
                    # grosser Schrift, wie bei jeder anderen Aufgabe auch.
                    anleitung=g.get("anleitung") or anleitung,
                    frage=g["frage"],
                    loesung_text=g.get("loesung_text", ""), aufgabe=g["aufgabe"],
                    schritte=g.get("schritte", []), tipps=g.get("tipps", []),
                    parameter=p)
        raise RuntimeError(
            f"{schablone}/{self.nr} Level {level}: nach {self.MAX_VERSUCHE} "
            f"Versuchen keine gültige Aufgabe. Filter zu eng oder Bereiche zu klein.")


@dataclass
class Schablone:
    nr: str
    titel: str
    lektionen: str
    erhebung: str
    anleitung: str                 # steht über der Aufgabe im Browser
    levelachse: str
    bauformen: list[Bauform]
    #: Teil 6 der Schablone. Wird beim Einstieg in die Lektion einmal gezeigt —
    #: auch dann, wenn der Schueler das Level ueberspringt. Wer B kann, muss A
    #: nicht ueben, soll die Regel aber trotzdem gelesen haben.
    kernidee: str = ""

    def bauformen_fuer(self, level: str) -> list[Bauform]:
        return [b for b in self.bauformen if level in b.levels]

    def bauform(self, nr: str) -> Bauform:
        for b in self.bauformen:
            if b.nr == nr:
                return b
        raise KeyError(nr)

    def erzeugen(self, bauform_nr: str, level: str, rng: random.Random) -> ErzeugteAufgabe:
        return self.bauform(bauform_nr).erzeugen(level, rng, self.nr, self.anleitung)
