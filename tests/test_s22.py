# -*- coding: utf-8 -*-
"""
Testlauf für S22, S23, S24 und S25 · Kapitel 7.

Geprüft wird viererlei:
  1. Jede Bauform lässt sich auf jedem ihrer Level erzeugen
  2. Die richtige Antwort wird als RICHTIG erkannt
  3. Jeder Eintrag im Fehlerkatalog wird als genau dieser Fehler erkannt
  4. Kein Exponent über zehn — der Eingabeparser weist solche Antworten als
     Sicherung ab, und der Schüler könnte die Aufgabe gar nicht beantworten
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import Pow, expand, factor

from generator.s22_s23_potenzen import S22, S23
from generator.s24_s25_potenzgesetze import S24, S25
from generator.anzeige import als_eingabe
from korrektur import Status, auswerten

N = 40
rng = random.Random(20250801)


def zu_hoch(ausdruck) -> bool:
    for teil in ausdruck.atoms(Pow):
        if teil.exp.is_Integer and abs(int(teil.exp)) > 10:
            return True
    return False


def lauf(SCH):
    beanstandet = []
    gesamt = 0
    print(f"{'BF':5s} {'Lvl':4s} {'erz.':>5s} {'richtig':>8s} "
          f"{'Fehler erkannt':>15s}  Beispiel")
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

                # 4 · Exponentengrenze des Parsers
                if zu_hoch(e.aufgabe.loesung.expr):
                    beanstandet.append(
                        f"{bf.nr}/{lvl}: «{e.frage}» — die Musterlösung hat "
                        f"einen Exponenten über zehn")

                # 2 · richtige Antwort
                a = auswerten(als_eingabe(e.loesung_text), e.aufgabe)
                if a.status is Status.RICHTIG:
                    ok_richtig += 1
                else:
                    beanstandet.append(
                        f"{bf.nr}/{lvl}: «{e.frage}» — Musterlösung "
                        f"«{e.loesung_text}» gilt als {a.status.value}: {a.text}")

                # 3 · jeder Katalogfehler
                for f in e.aufgabe.fehlerkatalog:
                    anz_fehler += 1
                    txt = str(expand(f.ergebnis.expr)).replace("**", "^")
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
    for S in (S22, S23, S24, S25):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n")
        alle += lauf(S)
    print("ALLES BESTANDEN" if not alle else f"{len(alle)} BEANSTANDUNGEN")
