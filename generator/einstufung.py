# -*- coding: utf-8 -*-
"""
Einstufungstest — wo steigt dieser Schüler ein?

Ohne ihn beginnt jeder bei 1.9, auch der Gute. Das ist Unterforderung und
kostet in einer vierwöchigen Studie zu viel Zeit.

Das Verfahren ist eine binäre Suche durch das Netz, keine feste Aufgabenliste:

    Löst er die Leitaufgabe   -> alle Vorstufen gelten als sicher (E3),
                                 weiter oben suchen
    Löst er sie nicht         -> weiter unten suchen

Mit rund zwölf Aufgaben ist er eingeordnet, weil jede richtige Antwort viele
Lektionen auf einmal gutschreibt. Wer 15.6 löst, hat damit 32 Lektionen belegt.

Der Test ordnet NICHT nach Kapiteln ein, sondern nach dem Netz. Zwei Schüler
können bei derselben Aufgabenzahl an ganz verschiedenen Stellen landen.
"""
from __future__ import annotations

from .netz import (KLARTEXT, NETZ, ZIEL, alle_nachfolger, alle_vorstufen,
                   naechste_lektion, rueckwaerts_gutschreiben, zielmenge)

#: Die Leitaufgaben, grob von leicht nach schwer. Jede steht für eine Stelle
#: im Netz; wer sie löst, bekommt alles darunter gutgeschrieben.
#:
#: Ausgewählt so, dass sie das Netz gleichmässig abdecken — nicht die
#: Kapitelreihenfolge, sondern die Tiefe im Graphen.
#: Auf welchem Level die Leitaufgaben gestellt werden.
#: B, weil A zu leicht ist, um zu unterscheiden, und C zu schwer.
LEIT_LEVEL = "B"

LEITAUFGABEN: list[str] = [
    "1.19",   # Punkt vor Strich
    "3.11",   # Terme mit Zahlen und Variablen
    "4.8",    # gleichartige Terme
    "6.7",    # ausrechnen und zusammenfassen
    "7.10",   # Potenzen mit mehreren Variablen
    "9.6",    # Division in längeren Termen
    "10.6",   # Minus vor der Klammer
    "11.8",   # negativer Faktor mal Klammer
    "12.8",   # dreigliedrige Terme faktorisieren
    "13.9",   # Lösung als gekürzter Bruch
    "14.8",   # Klammer im Zähler mit Minus davor
    "15.6",   # Bruch mal Klammer in der Gleichung
]

#: So viele Aufgaben höchstens, damit der Test in einer Lektion durch ist.
MAX_AUFGABEN = 12


class Einstufung:
    """Der Zustand während des Tests. Wird in der Session gehalten."""

    def __init__(self, offen: list[str] | None = None,
                 sicher: set[str] | None = None,
                 gescheitert: set[str] | None = None,
                 gestellt: int = 0,
                 einstiegslevel: dict[str, str] | None = None):
        self.offen = list(offen) if offen is not None else list(LEITAUFGABEN)
        self.sicher = set(sicher or ())
        self.gescheitert = set(gescheitert or ())
        self.gestellt = gestellt
        #: Lektion -> Level, auf dem der Schueler einsteigt.
        #: Wer die Leitaufgabe auf B loest, faengt bei B an statt bei A.
        #: Das spart rund zwei Drittel der Uebungszeit — und A waere fuer ihn
        #: Unterforderung. Die Theorie sieht er trotzdem.
        self.einstiegslevel = dict(einstiegslevel or {})

    # ------------------------------------------------------------ Ablauf

    def naechste(self) -> str | None:
        """Welche Leitaufgabe kommt als Nächstes? None heisst: fertig."""
        if self.gestellt >= MAX_AUFGABEN:
            return None
        kandidaten = [l for l in self.offen
                      if l not in self.sicher and l not in self.gescheitert]
        if not kandidaten:
            return None
        # Binäre Suche: die mittlere der noch offenen nehmen.
        return kandidaten[len(kandidaten) // 2]

    def antwort(self, lektion: str, richtig: bool) -> None:
        self.gestellt += 1
        if richtig:
            # E3 · Rückwärts-Propagation: die Vorstufen gelten als sicher.
            self.sicher = rueckwaerts_gutschreiben(lektion, self.sicher)
            # Wer die Leitaufgabe auf B loest, steigt auch in den FOLGENDEN
            # Lektionen bei B ein — nicht bei A.
            for l in alle_nachfolger(lektion):
                self.einstiegslevel.setdefault(l, LEIT_LEVEL)
            # Alles, was jetzt sicher ist, muss nicht mehr geprüft werden.
            self.offen = [l for l in self.offen if l not in self.sicher]
        else:
            # Die Lektion und alles, was sie voraussetzt, bleibt fraglich —
            # aber nur SIE gilt als gescheitert. Die Vorstufen werden weiter
            # geprüft, denn die Lücke kann tiefer liegen.
            self.gescheitert.add(lektion)
            self.offen = [l for l in self.offen
                          if l == lektion or l in alle_vorstufen(lektion)
                          or l not in alle_nachfolger(lektion)]

    # ------------------------------------------------------------ Ergebnis

    def fertig(self) -> bool:
        return self.naechste() is None

    def startpunkt(self) -> str | None:
        """Die Lektion, bei der dieser Schüler beginnt."""
        return naechste_lektion(self.sicher)

    def bericht(self) -> dict:
        ziel = zielmenge()
        g = len(ziel & self.sicher)
        start = self.startpunkt()
        return {
            "gestellt": self.gestellt,
            "sicher": sorted(self.sicher),
            "sicher_anzahl": g,
            "ziel_anzahl": len(ziel),
            "prozent": int(g / len(ziel) * 100) if ziel else 0,
            "start": start,
            "start_name": KLARTEXT.get(start, start or "—"),
            "noch_offen": len(ziel) - g,
            "einstiegslevel": self.einstiegslevel,
            "start_level": self.einstiegslevel.get(start, "A"),
        }

    # ------------------------------------------------------------ Session

    def als_dict(self) -> dict:
        return {"offen": self.offen, "sicher": sorted(self.sicher),
                "gescheitert": sorted(self.gescheitert), "gestellt": self.gestellt,
                "einstiegslevel": self.einstiegslevel}

    @classmethod
    def aus_dict(cls, d: dict) -> "Einstufung":
        return cls(d.get("offen"), set(d.get("sicher", ())),
                   set(d.get("gescheitert", ())), d.get("gestellt", 0),
                   d.get("einstiegslevel"))



