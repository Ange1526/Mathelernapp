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
MISCHAUFGABEN = "mischen"
LEVEL_C = "level_c"

MODI = (PROBE_ERHEBUNG, SCHWACHSTELLEN, MISCHAUFGABEN, LEVEL_C)

TITEL = {
    PROBE_ERHEBUNG: "Probe-Erhebung",
    SCHWACHSTELLEN: "Deine Wackelkandidaten",
    MISCHAUFGABEN: "Mischaufgaben",
    LEVEL_C: "Alles nochmals auf Level C",
}

BESCHREIBUNG = {
    PROBE_ERHEBUNG: ("Ein kompletter Durchgang wie in der richtigen Prüfung: "
                     "19 Aufgaben, eine pro Teilaufgabe. Danach siehst du, "
                     "was schon sitzt."),
    SCHWACHSTELLEN: ("Die Aufgabenarten, bei denen du am meisten Fehler "
                     "gemacht hast — noch einmal, bis sie sicher sind."),
    MISCHAUFGABEN: ("Aufgaben, in denen mehrere Kapitel gleichzeitig "
                    "vorkommen — Wurzel, Potenz, Klammer und Zusammenfassen "
                    "in einem Term. Kein neuer Stoff, aber eine Stufe "
                    "schwerer als die Erhebung. Genau so sind die Aufgaben "
                    "gebaut, an denen man in der Prüfung hängen bleibt."),
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

    #: So viele Mischaufgaben hängen hinten an der Probe-Erhebung.
    #: Sie machen den Durchgang bewusst etwas schwerer als das Original:
    #: die Erhebung kombiniert, die App übte bisher nur Einzelteile.
    MISCHAUFGABEN_ANZAHL = 3

    @classmethod
    def neu(cls, mit_mischen: bool = True) -> "Probelauf":
        # Reihenfolge wie in der echten Prüfung, damit die Erfahrung stimmt.
        reihe = sorted(ZIEL)
        if mit_mischen:
            reihe += [f"M{i+1}" for i in range(cls.MISCHAUFGABEN_ANZAHL)]
        return cls(reihenfolge=reihe)

    @staticmethod
    def ist_mischaufgabe(teilaufgabe: str | None) -> bool:
        return bool(teilaufgabe) and teilaufgabe.startswith("M")

    def aktuelle(self) -> str | None:
        if self.position >= len(self.reihenfolge):
            return None
        return self.reihenfolge[self.position]

    def lektion(self) -> str | None:
        """Welche Lektion prüft die aktuelle Teilaufgabe?

        Bei den angehängten Mischaufgaben ist das keine Lektion des Netzes —
        sie stehen eine Stufe darüber. Sie geben `None` zurück; die App holt
        die Aufgabe dann direkt aus Kapitel 16.1.
        """
        a = self.aktuelle()
        if a is None or self.ist_mischaufgabe(a):
            return None
        return ZIEL.get(a)

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

    def falsche_lektionen(self) -> list[str]:
        """Die Lektionen hinter den falsch gelösten Teilaufgaben.

        Sie werden in `Lernweg` wieder aus «sicher» gestrichen. Ohne diesen
        Rückweg bleibt eine Lücke, die in der Probe-Erhebung auffällt, in der
        App unsichtbar — und der Schüler übt vier Wochen alles ausser der
        einen Sache, die er nicht kann.
        """
        return [ZIEL[a] for a in self.falsch if a in ZIEL]

    def bericht(self) -> dict:
        gesamt = len(self.richtig) + len(self.falsch)
        return {
            "richtig": len(self.richtig),
            "falsch": len(self.falsch),
            "gesamt": gesamt,
            "quote": int(len(self.richtig) / gesamt * 100) if gesamt else 0,
            "fehlerhafte": [(a, KLARTEXT.get(ZIEL[a], ZIEL[a])) if a in ZIEL
                            else (a, "Mischaufgabe") for a in self.falsch],
            "mischaufgaben": [a for a in self.reihenfolge
                              if self.ist_mischaufgabe(a)],
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


def naechster_modus(probe_gemacht: bool, hat_schwachstellen: bool,
                    mischen_moeglich: bool = False) -> str:
    """Was ist nach dem Durchlauf als Nächstes dran?

    Die Reihenfolge ist nicht willkürlich: zuerst MESSEN, wo man steht, dann
    GEZIELT üben, was wackelt, dann die Mischaufgaben — und erst zuletzt die
    breite Wiederholung auf Level C. Für den Gymnasiasten, der schon fast
    alles kann, ist der dritte Schritt der wichtigste: dort liegt der
    Unterschied zwischen «kann die Regeln» und «löst die Prüfung fehlerfrei».
    """
    if not probe_gemacht:
        return PROBE_ERHEBUNG
    if hat_schwachstellen:
        return SCHWACHSTELLEN
    if mischen_moeglich:
        return MISCHAUFGABEN
    return LEVEL_C
