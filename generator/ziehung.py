"""
Ziehung — welche Bauform kommt als Nächstes.

Regel 1 aus der Notiz: reihum, nicht zufällig.
Der Generator mischt die Bauformen des Levels und teilt sie der Reihe nach aus.
Erst wenn alle durch sind, mischt er neu.

Warum: bei zufälliger Ziehung mit Zurücklegen sieht ein Schüler bei zwölf
Aufgaben im Schnitt nur knapp acht von zwölf Bauformen. Vier bekommt er nie zu
Gesicht und steigt trotzdem auf.

Regel 2: Mastery pro Bauform. Eine Bauform, die sitzt, wird nicht mehr gezogen.
Die Lektion gilt erst als fertig, wenn jede Bauform des Levels ihr Häkchen hat.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import random


@dataclass
class Ziehungsstand:
    """Der Zustand EINES Schülers in EINEM Level EINER Schablone.

    Wird in B1 mitprotokolliert, damit die Reihenfolge auch nach einer
    Unterbrechung stimmt.
    """
    schablone: str
    level: str
    offen: list[str] = field(default_factory=list)      # in dieser Runde noch nicht dran
    gemeistert: set[str] = field(default_factory=set)   # sitzt – kommt nicht mehr
    treffer: dict[str, int] = field(default_factory=dict)  # richtige Antworten je Bauform

    MASTERY_SCHWELLE = 2   # so viele richtige Antworten, dann sitzt die Bauform

    def naechste(self, alle_bauformen: list[str], rng: random.Random) -> str | None:
        """Gibt die nächste Bauform zurück, oder None wenn das Level fertig ist."""
        kandidaten = [b for b in alle_bauformen if b not in self.gemeistert]
        if not kandidaten:
            return None                      # Level fertig
        self.offen = [b for b in self.offen if b in kandidaten]
        if not self.offen:                   # Runde durch – neu mischen
            self.offen = kandidaten[:]
            rng.shuffle(self.offen)
        return self.offen.pop(0)

    def bewerten(self, bauform: str, richtig: bool) -> None:
        if richtig:
            self.treffer[bauform] = self.treffer.get(bauform, 0) + 1
            if self.treffer[bauform] >= self.MASTERY_SCHWELLE:
                self.gemeistert.add(bauform)
        else:
            # Ein Fehler setzt die Bauform zurück und schiebt sie wieder in die Runde.
            self.treffer[bauform] = 0
            self.gemeistert.discard(bauform)
            if bauform not in self.offen:
                self.offen.append(bauform)

    def fertig(self, alle_bauformen: list[str]) -> bool:
        return all(b in self.gemeistert for b in alle_bauformen)

    def fortschritt(self, alle_bauformen: list[str]) -> tuple[int, int]:
        return len(self.gemeistert), len(alle_bauformen)
