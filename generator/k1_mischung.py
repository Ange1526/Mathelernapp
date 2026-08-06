# -*- coding: utf-8 -*-
"""
M1 · Gemischt: alles aus Kapitel 1 kombiniert       (Lektion 1.20)

Die Gemischt-Lektion am Ende von Kapitel 1. Wie alle anderen (M3 bis M16)
erfindet sie keinen neuen Stoff: `mischung()` nimmt die Bauformen von S1,
S3, S5 und S6 im Round Robin und nummeriert sie neu durch. Es sind
DIESELBEN Objekte — ein Fehler kann sich hier nicht anders verhalten als in
der Quelle. Siehe `mischung.py`.

WARUM SIE IN EINER EIGENEN DATEI STEHT und nicht wie M3 bis M16 in
`anbindung.py`: an `anbindung.py` wird parallel gearbeitet. Steht M1 dort,
verschwindet der Testlauf für 1.20 bei jedem Überschreiben. Hier steht sie
sicher, und `anbindung.py` braucht nur noch eine Importzeile.

Alle vier Quellschablonen haben dieselbe Anleitung «Rechne aus.», es fällt
also keine Bauform weg — anders als bei M3, wo S12 eine andere Anleitung
trägt als S13 und S14.
"""
from __future__ import annotations

from .mischung import mischung
from .s1_s3_vorzeichen import S1, S3
from .s5_s6_punkt_reihenfolge import S5, S6

M1 = mischung(
    "M1", "Gemischt: Kapitel 1", "1.20", [S1, S3, S5, S6],
    "Zuerst hinschauen: welche Zeichen sind Vorzeichen und welche "
    "Operationszeichen — und was kommt zuerst dran? Erst danach rechnen.")
