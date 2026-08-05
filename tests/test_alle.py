# -*- coding: utf-8 -*-
"""C3 · Alle fertigen Schablonen in einem Lauf prüfen."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import test_s10
import test_s2
import test_s4
import test_s15
import test_s3
import test_s5
import test_s16
import test_s20
import test_s7
import test_s8

if __name__ == "__main__":
    fehler = []
    for name, modul in (("S2 Grundoperationen", test_s2),
                        ("S4 Faktorisieren", test_s4),
                        ("S10 Klammern", test_s10),
                        ("S16 Gleichartige Terme", test_s16),
                        ("S7 Potenzen", test_s7)):
        print(f"\n{'=' * 96}\n{name}\n{'=' * 96}")
        fehler += modul.lauf()

    # Kapitel 8 hat vier Schablonen in einer Datei — eigene Schleife.
    for S in (test_s3.S12, test_s3.S13, test_s3.S14):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n{'=' * 96}")
        fehler += test_s3.lauf(S)

    for S in (test_s5.S18, test_s5.S19):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n{'=' * 96}")
        fehler += test_s5.lauf(S)

    for S in (test_s15.S15, test_s15.S17):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n{'=' * 96}")
        fehler += test_s15.lauf(S)

    for S in (test_s20.S20, test_s20.S21):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n{'=' * 96}")
        fehler += test_s20.lauf(S)

    for S in (test_s8.S26, test_s8.S27, test_s8.S28, test_s8.S29):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n{'=' * 96}")
        fehler += test_s8.lauf(S)
    print(f"\n{'=' * 96}")
    print("ALLES BESTANDEN" if not fehler else f"{len(fehler)} BEANSTANDUNGEN")
