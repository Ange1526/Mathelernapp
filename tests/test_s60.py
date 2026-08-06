# -*- coding: utf-8 -*-
"""
S60 · Mischaufgaben — jede erzeugte Aufgabe wird nachgerechnet.

Die schärfste Prüfung, die es hier gibt: die FRAGE wird durch denselben
Parser gelesen, den auch die Schülerin benutzt, und das Ergebnis mit der
Musterlösung verglichen. Stimmt der Anzeigetext nicht mit der gemeinten
Aufgabe überein, fällt es hier auf — und nur hier. Genau dieser Fehler hat
bei S11 dazu geführt, dass hundert Prozent der Aufgaben einer Bauform die
falsche Frage anzeigten.

Ausserdem geprüft:
    · Levelachse strukturell — A, B und C müssen sich im AUFBAU unterscheiden
    · Fehlerdichte — mindestens 1,6 Katalogeinträge je Aufgabe
    · kein Katalogeintrag ist wertgleich mit der Lösung
    · jede Bauform ist auf jedem Level erzeugbar
    · die Musterlösung wird als RICHTIG erkannt

    python tests/test_s60.py
"""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

from sympy import expand                                 # noqa: E402
from tests.schnellpruefung import gleich as wertgleich    # noqa: E402

from generator.anzeige import als_eingabe                # noqa: E402
from generator.s60_mischen import S60, VARS              # noqa: E402
from korrektur import Status, auswerten, parse_term      # noqa: E402

WIEVIEL = 40
MINDESTDICHTE = 1.6


def muster(t: str) -> str:
    """Zahlen und Buchstaben maskieren — übrig bleibt der AUFBAU.

    Sind die Mustermengen von A, B und C gleich, trägt das Level nur die
    Zahlen. Das ist der Fehler, den vier frühe Generatoren hatten.
    """
    t = re.sub(r"\d+", "#", t)
    t = re.sub(r"[a-z]", "~", t)
    return re.sub(r"\s+", "", t)


def main() -> int:
    rng = random.Random(4711)
    fehler: list[str] = []
    gesamt = 0
    katalog_gesamt = 0
    ohne_katalog = 0
    muster_je_level: dict[str, dict[str, set]] = {}

    for bf in S60.bauformen:
        muster_je_level[bf.nr] = {}
        for level in ("A", "B", "C"):
            if level not in bf.levels:
                fehler.append(f"{bf.nr}: Level {level} fehlt")
                continue
            gesehen = set()
            for _ in range(WIEVIEL):
                try:
                    e = S60.erzeugen(bf.nr, level, rng)
                except Exception as ex:            # noqa: BLE001
                    fehler.append(f"{bf.nr}/{level}: {type(ex).__name__} {ex}")
                    break
                gesamt += 1
                gesehen.add(muster(e.frage))

                # ── 1 · die Frage nachrechnen ────────────────────────────
                try:
                    gelesen = parse_term(als_eingabe(e.frage), VARS)
                except Exception as ex:            # noqa: BLE001
                    fehler.append(f"{bf.nr}/{level}: Frage «{e.frage}» nicht "
                                  f"lesbar ({ex})")
                    continue
                soll = e.aufgabe.loesung.expr
                if not wertgleich(expand(gelesen), expand(soll)):
                    fehler.append(f"{bf.nr}/{level}: «{e.frage}» ergibt "
                                  f"{gelesen}, Lösung sagt {soll}")

                # ── 2 · die Musterlösung muss RICHTIG sein ───────────────
                a = auswerten(als_eingabe(e.loesung_text), e.aufgabe)
                if a.status is not Status.RICHTIG:
                    fehler.append(f"{bf.nr}/{level}: Musterlösung "
                                  f"«{e.loesung_text}» gilt als {a.status.value}")

                # ── 3 · Fehlerkatalog ───────────────────────────────────
                k = e.aufgabe.fehlerkatalog
                katalog_gesamt += len(k)
                if not k:
                    ohne_katalog += 1
                for f in k:
                    if wertgleich(f.ergebnis.expr, soll):
                        fehler.append(f"{bf.nr}/{level}: Katalogeintrag "
                                      f"«{f.schluessel}» ist wertgleich mit "
                                      f"der Lösung")
                    if not (f.text or "").strip():
                        fehler.append(f"{bf.nr}/{level}: Katalogeintrag "
                                      f"«{f.schluessel}» hat keinen Text")
            muster_je_level[bf.nr][level] = gesehen

    # ── 4 · Levelachse ──────────────────────────────────────────────────
    print("Levelachse — unterscheiden sich A, B und C im Aufbau?")
    for bf_nr, je_level in muster_je_level.items():
        a, b, c = (je_level.get(l, set()) for l in ("A", "B", "C"))
        gleich = []
        if a and b and a == b:
            gleich.append("A=B")
        if b and c and b == c:
            gleich.append("B=C")
        if a and c and a == c:
            gleich.append("A=C")
        zeichen = "  " if not gleich else "!!"
        print(f"  {zeichen} {bf_nr:6} A:{len(a):>3} B:{len(b):>3} C:{len(c):>3}"
              f"{'   ' + ', '.join(gleich) if gleich else ''}")
        if gleich:
            fehler.append(f"{bf_nr}: Levelachse trägt nur Zahlen ({', '.join(gleich)})")

    dichte = katalog_gesamt / gesamt if gesamt else 0
    print(f"\nGeprüft: {gesamt} Aufgaben")
    print(f"Fehlerdichte: {dichte:.2f} Einträge je Aufgabe "
          f"(Richtwert {MINDESTDICHTE})")
    print(f"Aufgaben ohne Katalogeintrag: {ohne_katalog}")

    if dichte < MINDESTDICHTE:
        fehler.append(f"Fehlerdichte {dichte:.2f} unter {MINDESTDICHTE}")
    if ohne_katalog:
        fehler.append(f"{ohne_katalog} Aufgaben ohne Katalogeintrag")

    if fehler:
        print(f"\n{len(fehler)} BEFUNDE:")
        for f in dict.fromkeys(fehler):
            print("  •", f)
        return 1
    print("\nAlle Aufgaben nachgerechnet, keine Abweichung.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
