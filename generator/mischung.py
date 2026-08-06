# -*- coding: utf-8 -*-
"""
Die Gemischt-Lektionen — je eine am Ende jedes Kapitels.

Im Netz heisst die letzte Lektion jedes Kapitels «Gemischt: alles aus
Kapitel N kombiniert». Dreizehn solche Lektionen gab es, und keine hatte
Aufgaben. Sie standen damit als «übersprungen» im Weg jedes Schülers.

WAS HIER PASSIERT — und was ausdrücklich NICHT:

Eine Gemischt-Lektion erfindet keinen neuen Stoff. Sie stellt die Bauformen
des ganzen Kapitels nebeneinander, statt eine Schablone nach der anderen
durchzugehen. Genau das ist der Unterschied: wer S34 übt, weiss vorher, dass
ein Minus vor der Klammer kommt. Wer die Gemischt-Lektion übt, weiss es
nicht und muss erst hinschauen.

Darum werden die Bauformen WIEDERVERWENDET, nicht nachgebaut. Es sind
dieselben Objekte wie in den Quellschablonen, nur neu durchnummeriert. Ein
Fehler in einer Bauform kann sich hier also nicht anders verhalten als dort,
und der Testlauf muss sie kein zweites Mal prüfen.

    ACHTUNG · Die Mastery hängt an (Schablone, Bauform). Eine Gemischt-
    Lektion hat darum ihre EIGENEN Häkchen. Das ist gewollt: dass jemand
    `20 − (7 + 5)` kann, wenn die Aufgabe angekündigt ist, heisst nicht,
    dass er sie zwischen zwölf anderen Formen erkennt.

Zur Auswahl: Round Robin über die Schablonen des Kapitels — erst von jeder
die BF1, dann von jeder die BF2, und so weiter, bis zwölf beisammen sind.
So kommt aus jeder Schablone etwas vor, auch wenn eine davon zwölf Bauformen
hat und die andere neun.

Zur Anleitung: sie steht an der Schablone, nicht an der Bauform. In einem
Kapitel mit zwei verschiedenen Anleitungen — Kapitel 3 sagt einmal «rechne
aus» und zweimal «fasse zusammen» — wären sonst ein Drittel der Aufgaben
falsch angeschrieben. Es kommen darum nur die Schablonen in die Mischung,
die die HÄUFIGSTE Anleitung des Kapitels tragen. Lieber eine Bauform
weniger als eine falsche Aufforderung.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace

from .schablone import Bauform, Schablone


def _auswahl(schablonen: list[Schablone], anzahl: int = 12) -> list[Bauform]:
    """Round Robin: von jeder Schablone die erste, dann die zweite, ..."""
    raus: list[Bauform] = []
    i = 0
    while len(raus) < anzahl:
        gefunden = False
        for s in schablonen:
            if i < len(s.bauformen):
                raus.append(s.bauformen[i])
                gefunden = True
                if len(raus) == anzahl:
                    return raus
        if not gefunden:
            break
        i += 1
    return raus


def mischung(nr: str, titel: str, lektion: str, quellen: list[Schablone],
             kernidee: str) -> Schablone:
    """Baut aus den Schablonen eines Kapitels eine Gemischt-Schablone."""
    if not quellen:
        raise ValueError(f"{nr}: keine Quellschablonen")
    haeufigste = Counter(s.anleitung for s in quellen).most_common(1)[0][0]
    passend = [s for s in quellen if s.anleitung == haeufigste]

    bauformen = []
    for i, bf in enumerate(_auswahl(passend), 1):
        #: Neu durchnummeriert — sonst gäbe es BF1 zweimal in derselben
        #: Schablone, und `Schablone.bauform()` fände immer nur die erste.
        neu = replace(bf, nr=f"BF{i}",
                      beschreibung=f"{bf.beschreibung}  ({_woher(passend, bf)})")
        bauformen.append(neu)

    return Schablone(
        nr=nr, titel=titel, lektionen=lektion, erhebung="",
        anleitung=haeufigste,
        levelachse="wie in den Quellschablonen",
        bauformen=bauformen, kernidee=kernidee)


def _woher(schablonen: list[Schablone], bf: Bauform) -> str:
    """Aus welcher Schablone stammt diese Bauform?

    Steht in der Beschreibung, damit beim Nachschauen im Protokoll klar ist,
    woher die Aufgabe kommt.
    """
    for s in schablonen:
        for eigene in s.bauformen:
            if eigene is bf:
                return f"{s.nr}/{bf.nr}"
    return "?"
