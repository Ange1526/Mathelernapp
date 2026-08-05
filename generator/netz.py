# -*- coding: utf-8 -*-
"""
Netz — der personalisierte Weg durch alle 170 Lektionen.

Das Ziel ist nicht nur, die Erhebungsprüfung zu bestehen, sondern eine solide
Algebra-Basis. Deshalb gehören ALLE 170 Lektionen zum Weg — auch die 39, die
für die Prüfung nicht nötig wären.

Die Erhebung bleibt der Massstab: `ZIEL` sagt, welche Lektion welche
Teilaufgabe prüft. Daran misst sich, ob jemand den Test fehlerfrei lösen kann.

Der Graph kommt aus `netz_daten.py` und wird aus der Landkarte erzeugt —
nicht von Hand gepflegt. Beim Generieren wird geprüft, dass er zyklenfrei ist
und dass keine Voraussetzung auf eine fehlende Lektion zeigt.
"""
from __future__ import annotations

from collections import deque

from .netz_daten import LEKTIONEN

#: Lektion -> Voraussetzungen
NETZ: dict[str, list[str]] = {nr: vor for nr, (vor, _) in LEKTIONEN.items()}

#: Lektion -> Titel im Klartext
KLARTEXT: dict[str, str] = {nr: titel for nr, (_, titel) in LEKTIONEN.items()}

#: Erhebungsaufgabe -> die Lektion, die sie prüft.
ZIEL: dict[str, str] = {
    "1a": "13.9", "1b": "15.6",
    "2a": "6.7",  "2b": "11.8", "2c": "9.6",
    "3a": "8.8",  "3b": "8.2",  "3c": "7.4", "3d": "10.16", "3e": "8.9",
    "4a": "12.4", "4b": "12.6", "4c": "12.6", "4d": "12.8",
    "5a": "14.8", "5b": "14.4", "5c": "14.11",
    "6a": "15.5", "6b": "15.3",
}

#: Lektion -> Kapitelnummer der Schablone, die sie übt.
#: Wird gefüllt, sobald die Generatoren da sind. Was hier fehlt, kann noch
#: nicht geübt werden — und zählt darum auch nicht als sicher.
SCHABLONE_FUER: dict[str, str] = {
    # Klammern — deckt 10.1 bis 10.11 ab, darunter 10.6, das haeufigste
    # Ruecksprungziel im ganzen Netz.
    "10.1": "10.1", "10.2": "10.1", "10.3": "10.1", "10.4": "10.1",
    "10.5": "10.1", "10.6": "10.1", "10.7": "10.1", "10.8": "10.1",
    "10.9": "10.1", "10.10": "10.1", "10.11": "10.1",
    # Gleichartige Terme — 4.8 ist eines der drei haeufigen Ruecksprungziele
    "4.1": "4.1", "4.2": "4.1", "4.3": "4.1", "4.4": "4.1", "4.5": "4.1",
    "4.6": "4.1", "4.7": "4.1", "4.8": "4.1", "4.9": "4.1", "4.10": "4.1",
    # Potenzen — 7.10 ist das dritte haeufige Ruecksprungziel
    "7.1": "7.1", "7.2": "7.1", "7.3": "7.1", "7.4": "7.1", "7.5": "7.1",
    "7.6": "7.1", "7.7": "7.1", "7.8": "7.1", "7.9": "7.1", "7.10": "7.1",
    "7.11": "7.1",
    # Grundoperationen
    "6.5": "6.1", "6.6": "6.1", "6.7": "6.1",
    # Faktorisieren
    "12.1": "12.1", "12.2": "12.1", "12.3": "12.1", "12.4": "12.1",
}


#: «Schablone/Bauform/Fehlerschlüssel»  ->  Lektion, an der es wirklich fehlt.
#:
#: Der Kern der Lückensuche. Bei einer Bruchgleichung kann derselbe falsche
#: Wert drei Ursachen haben — Minusklammer, Hauptnenner oder
#: Gleichungsumformung. Der Fehlerkatalog weiss, welche es war; hier steht,
#: wohin sie zeigt.
#:
#: Kein Eintrag heisst: der Fehler gehört zur Lektion selbst, nicht darunter.
#: Dann wird nicht zurückgesprungen, sondern weitergeübt.
RUECKSPRUNG: dict[str, str] = {
    # ── S2 Grundoperationen ──────────────────────────────────────────────────
    "S2/BF1/punkt_vor_strich":   "1.19",
    "S2/BF1/alles_zusammen":     "4.8",
    "S2/BF1/minus_verloren":     "10.6",
    "S2/BF2/nur_erster":         "10.6",
    "S2/BF2/vorzeichen":         "10.6",
    "S2/BF2/klammer_ignoriert":  "11.4",
    "S2/BF3/hochzahl":           "7.10",
    "S2/BF3/ganze_summe":        "1.19",
    "S2/BF3/nicht_gekuerzt":     "9.3",
    "S2/BF4/alles_zusammen":     "4.8",
    "S2/BF4/vorzeichen":         "1.9",
    "S2/BF5/hochzahl":           "7.10",
    "S2/BF5/nur_zahl":           "9.3",
    "S2/BF5/variable_weg":       "9.3",
    "S2/BF6/klammer_vorzeichen": "10.6",
    "S2/BF6/bruch_hochzahl":     "7.10",
    "S2/BF6/division_zu_weit":   "1.19",
    "S2/BF7/sorte_geblieben":    "4.8",
    "S2/BF7/vorzeichen":         "10.6",
    "S2/BF8/zusammengezogen":    "4.8",
    "S2/BF8/nur_zahlen":         "4.8",

    # ── S4 Faktorisieren ─────────────────────────────────────────────────────
    "S4/BF1/vorzeichen":             "1.9",
    "S4/BF1/nur_erstes":             "11.6",
    "S4/BF2/variable_geblieben":     "11.6",
    "S4/BF2/nur_erstes_geteilt":     "11.6",
    "S4/BF3/vorzeichen":             "1.9",
    "S4/BF3/hochzahl":               "7.10",
    "S4/BF4/eins_weggelassen":       "11.6",
    "S4/BF4/vorzeichen":             "1.9",
    "S4/BF5/hochzahl":               "7.10",
    "S4/BF5/vorzeichen":             "1.9",
    "S4/BF6/zweite_variable":        "12.4",
    "S4/BF6/vorzeichen":             "1.9",
    "S4/BF7/variable_ausgeklammert": "12.4",
    "S4/BF7/letztes_vergessen":      "11.6",
    "S4/BF8/etwas_ausgeklammert":    "12.4",
}


def rueckwaerts_zu(schablone: str, bauform: str,
                   fehlerschluessel: str | None) -> str | None:
    """Wohin führt DIESER Fehler zurück?

    Gibt die Lektion, an der es wirklich fehlt — oder None, wenn der Fehler
    zur Lektion selbst gehört und nicht zu einer Voraussetzung.
    """
    if not fehlerschluessel:
        return None
    return RUECKSPRUNG.get(f"{schablone}/{bauform}/{fehlerschluessel}")


def _num(lektion: str) -> tuple[int, int]:
    k, n = lektion.split(".")
    return int(k), int(n)


ALLE = sorted(NETZ, key=_num)


# ───────────────────────────────────────────────────────── Graph

def voraussetzungen(lektion: str) -> list[str]:
    return NETZ.get(lektion, [])


def alle_vorstufen(lektion: str) -> set[str]:
    """Alles, was vor dieser Lektion kommt — auch über mehrere Ecken."""
    gesehen, rand = set(), deque(voraussetzungen(lektion))
    while rand:
        l = rand.popleft()
        if l in gesehen:
            continue
        gesehen.add(l)
        rand.extend(voraussetzungen(l))
    return gesehen


def alle_nachfolger(lektion: str) -> set[str]:
    """Alles, was diese Lektion voraussetzt."""
    raus, geaendert = set(), True
    while geaendert:
        geaendert = False
        for l, vor in NETZ.items():
            if l in raus:
                continue
            if lektion in vor or any(v in raus for v in vor):
                raus.add(l)
                geaendert = True
    return raus


# ───────────────────────────────────────────────── Weg und Ziel

def zielmenge() -> set[str]:
    """Alle Lektionen. Das Ziel ist die solide Basis, nicht nur der Test."""
    return set(ALLE)


def pruefungsmenge() -> set[str]:
    """Nur was die Erhebung verlangt — für die Auswertung der Studie."""
    menge = set(ZIEL.values())
    for l in list(menge):
        menge |= alle_vorstufen(l)
    return menge


def offen(sicher: set[str]) -> set[str]:
    return zielmenge() - set(sicher)


def bereit(lektion: str, sicher: set[str]) -> bool:
    return all(v in sicher for v in voraussetzungen(lektion))


def naechste_lektion(sicher: set[str], zuletzt: str | None = None) -> str | None:
    """DIE eine Lektion, die jetzt dran ist.

    Von allen offenen, deren Voraussetzungen sitzen, die mit der kleinsten
    Nummer — so bleibt die Reihenfolge nachvollziehbar und folgt dem Lehrgang.
    """
    kandidaten = [l for l in offen(sicher) if bereit(l, sicher)]
    if not kandidaten:
        return None
    if zuletzt in kandidaten:
        return zuletzt
    return min(kandidaten, key=_num)


def rueckwaerts_gutschreiben(loeste: str, sicher: set[str]) -> set[str]:
    """Wer eine schwere Lektion löst, kann die Vorstufen."""
    return set(sicher) | {loeste} | alle_vorstufen(loeste)


def fortschritt(sicher: set[str]) -> tuple[int, int, int]:
    ziel = zielmenge()
    g = len(ziel & set(sicher))
    return g, len(ziel), int(g / len(ziel) * 100) if ziel else 0


def erhebung_abgedeckt(sicher: set[str]) -> dict[str, bool]:
    return {a: (l in sicher) for a, l in ZIEL.items()}


def restaufwand(sicher: set[str], aufgaben_je_lektion: float = 5.2,
                sekunden_je_aufgabe: int = 45) -> dict:
    """Wie viel liegt noch vor mir?

    Damit die Schülerin sich einteilen kann, ob sie zu Hause noch etwas macht.
    Die Kennzahlen stammen aus dem Testlauf: eine Schablone mit zwölf
    Bauformen über die Level braucht rund 15 Aufgaben, und eine Schablone
    deckt im Schnitt 2.9 Lektionen ab.
    """
    rest = len(offen(sicher))
    aufgaben = rest * aufgaben_je_lektion
    minuten = aufgaben * sekunden_je_aufgabe / 60
    return {"lektionen_offen": rest,
            "aufgaben": int(aufgaben),
            "minuten": int(minuten),
            "stunden": round(minuten / 60, 1)}
