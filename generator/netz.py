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
    # 10.1 — S33 · Klammern setzen und weglassen
    "10.1": "10.1",
    # 10.2 bis 10.6 — S34 · Strichoperation vor der Klammer.
    # 10.6 ist das haeufigste Ruecksprungziel im ganzen Netz.
    "10.2": "10.2", "10.3": "10.2", "10.4": "10.2",
    "10.5": "10.2", "10.6": "10.2",
    # 10.7 bis 10.11 — S35 · Punktoperation und Klammer
    "10.7": "10.7", "10.8": "10.7",
    "10.9": "10.7", "10.10": "10.7", "10.11": "10.7",
    # 10.12 bis 10.15 — S36 · Klammern mit Variablen und gemischt
    "10.12": "10.12", "10.13": "10.12",
    "10.14": "10.12", "10.15": "10.12",
    # 10.16 — S37. Das ist das Ziel von Erhebungsaufgabe 3d.
    "10.16": "10.16",
    # Gleichartige Terme — S16 deckt 4.2 bis 4.6 und 4.8 ab, mehr nicht.
    # 4.1 und 4.7 sind Schablone S15, 4.9 ist S17, 4.10 ist die
    # Gemischt-Lektion. Sie standen frueher faelschlich hier drin.
    # Kapitel 3 — S12, S13, S14. 3.12 «Gemischt» bleibt offen.
    "3.1": "3.1", "3.2": "3.1", "3.3": "3.1",
    "3.4": "3.4", "3.5": "3.4", "3.6": "3.4", "3.7": "3.4",
    "3.8": "3.4", "3.9": "3.4",
    "3.10": "3.10", "3.11": "3.10",
    # Kapitel 5 — S18 und S19. 5.9 «Gemischt» bleibt offen.
    "5.1": "5.1", "5.2": "5.1", "5.3": "5.1", "5.4": "5.1",
    "5.5": "5.5", "5.6": "5.5", "5.7": "5.5", "5.8": "5.5",
    "4.1": "4.1", "4.7": "4.1",
    "4.2": "4.2", "4.3": "4.2", "4.4": "4.2", "4.5": "4.2",
    "4.6": "4.2", "4.8": "4.2",
    "4.9": "4.9",
    # Kapitel 7 — vier Schablonen statt einer. S22 deckt 7.1 und 7.2 ab,
    # S23 die Lektionen 7.3 und 7.4 (Erhebung 3c), S24 die Potenzgesetze
    # 7.5 bis 7.8 und S25 die Lektionen 7.9 und 7.10 — letztere ist das
    # dritte haeufige Ruecksprungziel im Netz.
    # 7.11 «Gemischt» bleibt offen, wie 4.10, 5.9, 6.8 und 8.10.
    "7.1": "7.1", "7.2": "7.1",
    "7.3": "7.3", "7.4": "7.3",
    "7.5": "7.5", "7.6": "7.5", "7.7": "7.5", "7.8": "7.5",
    "7.9": "7.9", "7.10": "7.9",
    # Kapitel 8 Wurzeln — vier Schablonen, S26 bis S29.
    # 8.10 «Gemischt» bleibt bewusst offen: keine der vier Schablonen baut
    # Aufgaben, die alle Formen des Kapitels mischen.
    "8.1": "8.1", "8.2": "8.1",
    "8.3": "8.3", "8.7": "8.3",
    "8.4": "8.4", "8.5": "8.4", "8.6": "8.4", "8.8": "8.4",
    "8.9": "8.9",
    # Kapitel 6 — S20 deckt 6.1 bis 6.4 ab (Punkt vor Strich, eine und zwei
    # Variablen, Vorzeichen), S21 die Lektionen 6.5 bis 6.7 (nach dem
    # Ausrechnen zusammenfassen). Beide ersetzen S2, das hier auf allen drei
    # Level denselben Aufbau hatte.
    # 6.8 «Gemischt» bleibt offen — wie 4.10, 5.9 und 8.10 auch.
    "6.1": "6.1", "6.2": "6.1", "6.3": "6.1", "6.4": "6.1",
    "6.5": "6.5", "6.6": "6.5", "6.7": "6.5",
    # Kapitel 9 vollstaendig — drei Schablonen. S30 bringt die nackte
    # Division ohne Potenzen (9.1 bis 9.3), S31 die Monome mit Potenzen und
    # die Summe im Zaehler (9.4, 9.5), S32 die Einordnung in einen laengeren
    # Term (9.6). 9.6 ist das Ziel von Erhebungsaufgabe 2c.
    "9.1": "9.1", "9.2": "9.1", "9.3": "9.1",
    "9.4": "9.4", "9.5": "9.4",
    "9.6": "9.6",
    # Kapitel 13 — S45 deckt 13.1 bis 13.4 ab (die vier Grundformen der
    # linearen Gleichung). 13.5 bis 13.9 sind S46 und S47, 13.10 ist die
    # Gemischt-Lektion und bleibt offen.
    "13.1": "13.1", "13.2": "13.1", "13.3": "13.1", "13.4": "13.1",
    "13.5": "13.5", "13.6": "13.5",
    "13.7": "13.7", "13.8": "13.7", "13.9": "13.7",
    # Kapitel 14 — Bruchterme. S48 erweitert (14.1, 14.2 und 14.8 — das ist
    # Erhebungsaufgabe 5a), S49 kuerzt (14.3, 14.4), S50 addiert bei
    # gleichem Nenner (14.6, 14.7), S51 multipliziert und dividiert
    # (14.9 bis 14.11). Nur 14.5 bleibt offen.
    "14.1": "14.1", "14.2": "14.1", "14.8": "14.1",
    "14.3": "14.3", "14.4": "14.3",
    # 14.5 — S49B · Kuerzen nach dem Ausklammern (14.4 und 12.5 davor)
    "14.5": "14.5",
    "14.6": "14.6", "14.7": "14.6",
    "14.9": "14.9", "14.10": "14.9", "14.11": "14.9",
    # Kapitel 15 — Bruchgleichungen. S52 bestimmt den Hauptnenner
    # (15.1, 15.2), S53 nimmt jeden Summanden damit mal (15.3,
    # Erhebung 6b), S54 hat den Term im Zaehler (15.4, 15.5,
    # Erhebung 6a).
    "15.1": "15.1", "15.2": "15.1",
    "15.3": "15.3",
    "15.4": "15.4", "15.5": "15.4",
    "15.6": "15.6",
    # Kapitel 11 — Ausmultiplizieren. S38 deckt 11.1 bis 11.4 ab, S39
    # die Lektionen 11.5 und 11.6, S40 die Lektionen 11.7 und 11.8 —
    # letztere ist das Ziel von Erhebungsaufgabe 2b.
    # 11.9 und 11.10 bleiben offen.
    "11.1": "11.1", "11.2": "11.1", "11.3": "11.1", "11.4": "11.1",
    "11.5": "11.5", "11.6": "11.5",
    "11.7": "11.7", "11.8": "11.7",
    # 11.9 — S41 · Bruch mal Klammer, die letzte Zutat fuer 1b.
    "11.9": "11.9",
    # Faktorisieren — BF5 bringt Potenzen und zwei Variablen (12.5, 12.6),
    # BF6 und BF7 die dreigliedrigen Terme (12.7), die Zielform FAKTORISIERT
    # zusammen mit BF8 prueft die Vollstaendigkeit (12.8). Damit sind die
    # Erhebungsteilaufgaben 4b, 4c und 4d abgedeckt.
    # 12.1 bis 12.4 — S42 · Zahl und Variable ausklammern
    "12.1": "12.1", "12.2": "12.1", "12.3": "12.1", "12.4": "12.1",
    # 12.5 und 12.6 — S43 · Potenzen und mehrere Variablen
    "12.5": "12.5", "12.6": "12.5",
    # 12.7 und 12.8 — S44 · dreigliedrige Terme
    "12.7": "12.7", "12.8": "12.7",
    # 12.9 hat keinen Generator und zaehlt darum als uebersprungen.

    # ── Die Gemischt-Lektionen am Ende jedes Kapitels ────────────────────
    # Kein neuer Stoff, sondern alle Bauformen des Kapitels nebeneinander.
    # Siehe `mischung.py`. Kapitel 16 bleibt bewusst draussen — dort liegt
    # die Stufe UEBER dem Weg, nicht auf ihm.
    "3.12": "3.12", "4.10": "4.10", "5.9": "5.9", "6.8": "6.8",
    "7.11": "7.11", "8.10": "8.10", "9.7": "9.7", "10.17": "10.17",
    "11.10": "11.10", "12.9": "12.9", "13.10": "13.10", "14.12": "14.12",
    "15.9": "15.9",
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

    # ── S42, S43, S44 Faktorisieren ──────────────────────────────────────────
    #: Diese drei rechnen ihren Fehlerkatalog aus der Aufgabe. Die Schluessel
    #: sind darum in allen zwoelf Bauformen dieselben — der Stern steht fuer
    #: «jede Bauform dieser Schablone».
    "S42/*/vorzeichen_verloren":            "1.9",
    "S42/*/vorzeichen_gesamt":              "1.9",
    "S42/*/nicht_geteilt":                  "11.6",
    "S42/*/nur_erstes_geteilt":             "11.6",
    "S42/*/subtrahiert":                    "11.6",
    "S42/*/glied_verloren":                 "11.6",
    "S42/*/eins_vergessen":                 "12.4",
    "S42/*/variable_im_faktor_vergessen":   "12.4",
    "S42/*/zahl_im_faktor_vergessen":       "12.4",
    "S43/*/vorzeichen_verloren":            "1.9",
    "S43/*/vorzeichen_gesamt":              "1.9",
    "S43/*/nicht_geteilt":                  "11.6",
    "S43/*/nur_erstes_geteilt":             "11.6",
    "S43/*/subtrahiert":                    "11.6",
    "S43/*/glied_verloren":                 "11.6",
    "S43/*/eins_vergessen":                 "12.4",
    "S43/*/variable_im_faktor_vergessen":   "12.4",
    "S43/*/zahl_im_faktor_vergessen":       "12.4",
    "S44/*/vorzeichen_verloren":            "1.9",
    "S44/*/vorzeichen_gesamt":              "1.9",
    "S44/*/nicht_geteilt":                  "11.6",
    "S44/*/nur_erstes_geteilt":             "11.6",
    "S44/*/subtrahiert":                    "11.6",
    "S44/*/glied_verloren":                 "11.6",
    "S44/*/eins_vergessen":                 "12.4",
    "S44/*/variable_im_faktor_vergessen":   "12.4",
    "S44/*/zahl_im_faktor_vergessen":       "12.4",

    # ── S34, S35, S36 Klammern ───────────────────────────────────────────────
    #: 10.6 ist das haeufigste Ruecksprungziel im ganzen Netz.
    "S34/*/nur_erstes_glied":    "10.6",
    "S34/*/minus_vergessen":     "10.6",
    "S34/*/vorzeichen_34":       "1.9",
    "S36/*/nur_erstes_glied":    "10.6",
    "S36/*/minus_vergessen":     "10.6",
    "S36/*/zuviel_gedreht":      "10.6",
    "S36/*/variablen_gemischt":  "4.8",
    "S36/*/ungleichartig":       "4.8",
    "S36/*/variable_bleibt":     "4.8",
    "S36/*/vorzeichen_gesamt":   "1.9",

    # ── S41 Bruch mal Klammer ────────────────────────────────────────────────
    "S41/*/nur_erstes":                 "11.4",
    "S41/*/nur_letztes":                "11.4",
    "S41/*/nenner_auch_multipliziert":  "2.9",
    "S41/*/kehrwert":                   "2.9",
    "S41/*/vorzeichen_glied":           "1.9",
    "S41/*/vorzeichen_gesamt":          "1.9",
    "S41/*/faktor_vergessen":           "11.4",
    "S41/*/addiert":                    "11.4",
}


def rueckwaerts_zu(schablone: str, bauform: str,
                   fehlerschluessel: str | None) -> str | None:
    """Wohin führt DIESER Fehler zurück?

    Gibt die Lektion, an der es wirklich fehlt — oder None, wenn der Fehler
    zur Lektion selbst gehört und nicht zu einer Voraussetzung.
    """
    if not fehlerschluessel:
        return None
    treffer = RUECKSPRUNG.get(f"{schablone}/{bauform}/{fehlerschluessel}")
    if treffer:
        return treffer
    #: Wo der Fehlerkatalog aus der Aufgabe gerechnet wird, heisst der
    #: Schluessel in allen zwoelf Bauformen gleich. Dafuer der Stern.
    return RUECKSPRUNG.get(f"{schablone}/*/{fehlerschluessel}")


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
