# -*- coding: utf-8 -*-
"""
Vertiefung — was passiert, wenn jemand vor Ablauf der vier Wochen durch ist?

Wer bei über 70 Prozent einsteigt, hat den Weg nach zwei bis drei Wochen
hinter sich. Ohne Anschluss würde er die restliche Studienzeit nichts tun —
und das verzerrt den Vergleich mit der Kontrollgruppe, die weiterarbeitet.

Drei Modi, in dieser Reihenfolge:

1  PROBE_ERHEBUNG   Ein vollständiger Testdurchgang in Prüfungsform.
                    Zeigt, ob das Ziel wirklich erreicht ist — und wo nicht.
2  SCHWACHSTELLEN   Wiederholung der Bauformen, die am meisten Mühe machten.
                    Aus den echten Fehlerzahlen, nicht geraten.
3  LEVEL_C          Alles nochmals auf Level C, auch dort, wo er über den
                    Levelsprung eingestiegen ist und C nie gesehen hat.

Die Reihenfolge ist nicht willkürlich: zuerst messen, dann gezielt üben, erst
zuletzt breit wiederholen.
"""
from __future__ import annotations

from dataclasses import dataclass

from .netz import ZIEL, KLARTEXT, SCHABLONE_FUER

PROBE_ERHEBUNG = "probe"
SCHWACHSTELLEN = "schwach"
LEVEL_C = "level_c"

MODI = (PROBE_ERHEBUNG, SCHWACHSTELLEN, LEVEL_C)

TITEL = {
    PROBE_ERHEBUNG: "Probe-Erhebung",
    SCHWACHSTELLEN: "Deine Wackelkandidaten",
    LEVEL_C: "Alles nochmals auf Level C",
}

BESCHREIBUNG = {
    PROBE_ERHEBUNG: ("Ein kompletter Durchgang wie in der richtigen Prüfung: "
                     "19 Aufgaben, eine pro Teilaufgabe. Danach siehst du, "
                     "was schon sitzt."),
    SCHWACHSTELLEN: ("Die Aufgabenarten, bei denen du am meisten Fehler "
                     "gemacht hast — noch einmal, bis sie sicher sind."),
    LEVEL_C: ("Die schwerste Stufe für alle Lektionen. Auch für die, bei "
              "denen du direkt auf Level B eingestiegen bist."),
}


@dataclass
class Probelauf:
    """Ein Durchgang durch die 19 Teilaufgaben der Erhebung."""
    reihenfolge: list[str]          # ["1a", "1b", "2a", ...]
    position: int = 0
    richtig: list[str] | None = None
    falsch: list[str] | None = None

    def __post_init__(self):
        self.richtig = self.richtig if self.richtig is not None else []
        self.falsch = self.falsch if self.falsch is not None else []

    @classmethod
    def neu(cls) -> "Probelauf":
        # Reihenfolge wie in der echten Prüfung, damit die Erfahrung stimmt.
        return cls(reihenfolge=sorted(ZIEL))

    def aktuelle(self) -> str | None:
        if self.position >= len(self.reihenfolge):
            return None
        return self.reihenfolge[self.position]

    def lektion(self) -> str | None:
        a = self.aktuelle()
        return ZIEL.get(a) if a else None

    def antwort(self, war_richtig: bool) -> None:
        a = self.aktuelle()
        if a is None:
            return
        (self.richtig if war_richtig else self.falsch).append(a)
        self.position += 1

    def fertig(self) -> bool:
        return self.position >= len(self.reihenfolge)

    def uebersprungen(self) -> None:
        """Für Teilaufgaben, deren Lektion noch keinen Generator hat."""
        a = self.aktuelle()
        if a is not None:
            self.position += 1

    def bericht(self) -> dict:
        gesamt = len(self.richtig) + len(self.falsch)
        return {
            "richtig": len(self.richtig),
            "falsch": len(self.falsch),
            "gesamt": gesamt,
            "quote": int(len(self.richtig) / gesamt * 100) if gesamt else 0,
            "fehlerhafte": [(a, KLARTEXT.get(ZIEL[a], ZIEL[a])) for a in self.falsch],
            "fehlerfrei": len(self.falsch) == 0 and gesamt > 0,
            "nicht_geprueft": len(self.reihenfolge) - gesamt,
        }

    def als_dict(self) -> dict:
        return {"reihenfolge": self.reihenfolge, "position": self.position,
                "richtig": self.richtig, "falsch": self.falsch}

    @classmethod
    def aus_dict(cls, d: dict) -> "Probelauf":
        return cls(d.get("reihenfolge") or sorted(ZIEL), d.get("position", 0),
                   d.get("richtig"), d.get("falsch"))


def schwachstellen(staende, wieviele: int = 8) -> list[tuple[str, str, str, int]]:
    """Die Bauformen mit den meisten Fehlversuchen.

    `staende` sind BauformStand-Objekte. Zurück kommt
    [(kapitel, level, bauform, fehler), ...], die schlimmsten zuerst.

    Grundlage sind die echten Fehlerzahlen aus dem Üben — nicht eine Annahme
    darüber, was schwer sein könnte.
    """
    mit_fehlern = [s for s in staende if (s.fehler or 0) > 0]
    mit_fehlern.sort(key=lambda s: (-(s.fehler or 0), s.chapter, s.level, s.bauform))
    return [(s.chapter, s.level, s.bauform, s.fehler or 0)
            for s in mit_fehlern[:wieviele]]


def naechster_modus(probe_gemacht: bool, hat_schwachstellen: bool) -> str:
    """Was ist nach dem Durchlauf als Nächstes dran?"""
    if not probe_gemacht:
        return PROBE_ERHEBUNG
    if hat_schwachstellen:
        return SCHWACHSTELLEN
    return LEVEL_C
