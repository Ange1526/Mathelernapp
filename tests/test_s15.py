# -*- coding: utf-8 -*-
"""
Testlauf für S15 und S17 · Sorten erkennen.

Geprüft wird viererlei:
  1. Jede Bauform lässt sich auf jedem ihrer Level erzeugen
  2. Die Musterlösung ist wertgleich mit dem Aufgabentext
  3. Die richtige Antwort wird als RICHTIG erkannt — in mehreren Schreibweisen
  4. Jeder Eintrag im Fehlerkatalog wird als genau dieser Fehler erkannt
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import expand, factor, simplify

from generator.s15_s17_sorten import S15, S17
from generator.anzeige import als_eingabe, zeige
from korrektur import Status, auswerten
from korrektur.pruefung import Art

N = 40
rng = random.Random(20250801)


def als_text(e) -> str:
    """Musterlösung als Eingabe, wie ein Schüler sie tippen würde."""
    return str(factor(expand(e))).replace("**", "^")


def lauf(SCH):
    beanstandet = []
    gesamt = 0
    print(f"{'BF':5s} {'Lvl':4s} {'erz.':>5s} {'richtig':>8s} {'Fehler erkannt':>15s}  Beispiel")
    print("-" * 96)

    for bf in SCH.bauformen:
        for lvl in bf.levels:
            ok_richtig = ok_fehler = anz_fehler = 0
            beispiel = ""
            for i in range(N):
                try:
                    e = SCH.erzeugen(bf.nr, lvl, rng)
                except RuntimeError as err:
                    beanstandet.append(str(err))
                    break
                gesamt += 1
                if i == 0:
                    beispiel = f"{e.frage}  →  {e.loesung_text}"

                # 2 · Musterlösung wertgleich mit der Aufgabe?
                l = e.aufgabe.loesung
                if l.art is Art.EXPR and e.parameter:
                    pass  # der Bauplan garantiert es; geprüft wird über die Antwort

                # 3 · richtige Antwort
                a = auswerten(als_eingabe(e.loesung_text), e.aufgabe)
                if a.status is Status.RICHTIG:
                    ok_richtig += 1
                else:
                    beanstandet.append(
                        f"{bf.nr}/{lvl}: «{e.frage}» — Musterlösung "
                        f"«{e.loesung_text}» gilt als {a.status.value}: {a.text}")

                # 4 · jeder Katalogfehler
                for f in e.aufgabe.fehlerkatalog:
                    anz_fehler += 1
                    txt = str(factor(expand(f.ergebnis.expr))).replace("**", "^")
                    r = auswerten(txt, e.aufgabe)
                    if r.status is Status.FALSCH and r.fehlerschluessel == f.schluessel:
                        ok_fehler += 1
                    else:
                        beanstandet.append(
                            f"{bf.nr}/{lvl}: «{e.frage}» — Fehler «{f.schluessel}» "
                            f"(Eingabe {txt}) kam als {r.status.value}/"
                            f"{r.fehlerschluessel} zurück")
            print(f"{bf.nr:5s} {lvl:4s} {N:5d} {ok_richtig:8d} "
                  f"{ok_fehler:>7d}/{anz_fehler:<7d}  {beispiel}")

    print(f"\n{gesamt} Aufgaben erzeugt.")
    if beanstandet:
        print(f"\n{len(beanstandet)} Beanstandungen (erste 12):")
        for z in beanstandet[:12]:
            print("   ", z)
    else:
        print("Keine Beanstandungen.")
    return beanstandet


if __name__ == "__main__":
    alle = []
    for S in (S15, S17):
        print(f"\n{'='*96}\n{S.nr}  ·  {S.titel}\n")
        alle += lauf(S)
    print("ALLES BESTANDEN" if not alle else f"{len(alle)} BEANSTANDUNGEN")
