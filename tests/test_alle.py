# -*- coding: utf-8 -*-
"""C3 · Alle fertigen Schablonen in einem Lauf prüfen."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import test_s10
import test_s2
import test_s4
import test_s4k
import test_s7

if __name__ == "__main__":
    fehler = []
    for name, modul in (("S2 Grundoperationen", test_s2),
                        ("S4 Faktorisieren", test_s4),
                        ("S10 Klammern", test_s10),
                        ("S4K Gleichartige Terme", test_s4k),
                        ("S7 Potenzen", test_s7)):
        print(f"\n{'=' * 96}\n{name}\n{'=' * 96}")
        fehler += modul.lauf()
    print(f"\n{'=' * 96}")
    print("ALLES BESTANDEN" if not fehler else f"{len(fehler)} BEANSTANDUNGEN")
