# -*- coding: utf-8 -*-
"""
Testlauf für S20 und S21 · Punkt vor Strich mit Variablen.

Geprüft wird fünferlei:
  1. Jede Bauform lässt sich auf jedem ihrer Level erzeugen
  2. Der ANGEZEIGTE Aufgabentext ist wertgleich mit der Musterlösung
  3. Die richtige Antwort wird als RICHTIG erkannt
  4. Jeder Eintrag im Fehlerkatalog wird als genau dieser Fehler erkannt
  5. Im Aufgabentext stehen nie zwei Rechenzeichen nebeneinander

Punkt 2 und 5 gibt es nur hier. Bei diesen beiden Schablonen wird die Aufgabe
aus Gliedern und einem Vorzeichenmuster zusammengesetzt, und beim Bauen ist
genau das zweimal schiefgegangen: einmal war die Aufgabe ein Glied kürzer als
das Muster, einmal stand `+ −8av` im Text. Beides sieht man dem Ergebnis nicht
an — darum wird der Text selbst nachgerechnet.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sympy import expand, factor

from generator.s6_punktrechnung import S20, S21
from generator.anzeige import MINUS, als_eingabe
from korrektur import Status, auswerten

N = 40
rng = random.Random(20250801)

#: Zwei Rechenzeichen nebeneinander — `+ −8av` oder `− + 3x`.
ZEICHEN = ("+ +", "+ " + MINUS, MINUS + " +", MINUS + " " + MINUS,
           "+ ·", MINUS + " ·")


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

                # 5 · zwei Rechenzeichen nebeneinander
                for zwei in ZEICHEN:
                    if zwei in e.frage:
                        beanstandet.append(
                            f"{bf.nr}/{lvl}: «{e.frage}» — zwei Rechenzeichen "
                            f"nebeneinander («{zwei}»)")
                        break

                # 2 · der angezeigte Term muss die Musterlösung ergeben.
                #     UNFERTIG heisst hier «wertgleich, aber noch nicht
                #     zusammengefasst» — das ist bei der Aufgabe selbst normal.
                t = auswerten(als_eingabe(e.frage), e.aufgabe)
                if t.status not in (Status.RICHTIG, Status.UNFERTIG):
                    beanstandet.append(
                        f"{bf.nr}/{lvl}: der Aufgabentext «{e.frage}» ergibt "
                        f"nicht «{e.loesung_text}» ({t.status.value})")

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
    for S in (S20, S21):
        print(f"\n{'=' * 96}\n{S.nr}  ·  {S.titel}\n")
        alle += lauf(S)
    print("ALLES BESTANDEN" if not alle else f"{len(alle)} BEANSTANDUNGEN")
