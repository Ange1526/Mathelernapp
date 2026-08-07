# -*- coding: utf-8 -*-
"""
Prüft den Einstufungstest, indem er künstliche Schüler durch ihn hindurchschickt.

Ein echter Test lässt sich nicht mit einer Behauptung prüfen («er ist adaptiv»),
sondern nur mit Zahlen: wie viele Aufgaben braucht er, wie nahe kommt seine
Einschätzung an das, was der Schüler wirklich kann, und findet er die Lücken?

Vier Schülertypen, jeder in mehreren Ausprägungen:

    ANFAENGER     kann nichts ausser den ersten Kapiteln
    AUFBAU        kann die halbe Landkarte
    GYMNASIAST    kann fast alles, hat aber drei bis vier gezielte Lücken —
                  das ist der Fall, für den die Studie gebaut ist
    PERFEKT       kann alles (Kontrollfall: der Test darf ihn nicht bremsen)

Gemessen wird:
    Aufgaben        wie viele Fragen der Test gestellt hat
    Trefferquote    Anteil der Lektionen, die er richtig eingeschätzt hat
    Lücken gefunden wie viele der eingebauten Lücken im Plan landen

    python tests/test_einstufung.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

from generator.einstufung import Einstufung, straenge          # noqa: E402
from generator.netz import NETZ, SCHABLONE_FUER                # noqa: E402

LEVELWERT = {"A": 0, "B": 1, "C": 2}
UEBBAR = sorted(set(SCHABLONE_FUER), key=lambda l: tuple(int(x) for x in l.split(".")))


class Schueler:
    """Ein künstlicher Schüler.

    `kann` sind die Lektionen, die er beherrscht, `decke` sagt bis zu welchem
    Level. Was nicht in `kann` steht, löst er nicht — auch nicht auf Level A.
    """

    def __init__(self, name: str, kann: set[str], decke: str = "C",
                 luecken: set[str] | None = None):
        self.name = name
        self.kann = set(kann)
        self.decke = decke
        self.luecken = set(luecken or ())
        self.kann -= self.luecken

    def loest(self, lektion: str, level: str) -> bool:
        if lektion in self.luecken or lektion not in self.kann:
            return False
        return LEVELWERT[level] <= LEVELWERT[self.decke]


def durchlauf(s: Schueler) -> dict:
    e = Einstufung()
    while True:
        lektion = e.naechste()
        if lektion is None:
            break
        level = e.naechstes_level()
        e.antwort(lektion, s.loest(lektion, level))
    b = e.bericht()

    # Zwei Zahlen zählen, und sie sind nicht gleich schlimm.
    #
    #   ZU HOCH  Die App hält eine Lektion für sicher, die der Schüler auf
    #            Level B nicht löst. Das ist der teure Fehler: die Lücke
    #            bleibt vier Wochen unentdeckt und steht in der Erhebung.
    #   ZU TIEF  Die App lässt ihn bei A anfangen, obwohl er das Thema auf C
    #            beherrscht. Kostet Zeit, aber keine Punkte.
    im_plan = {p["lektion"]: p["level"] for p in b["plan"]}
    kontrolle = {p["lektion"]: p["level"] for p in b["kontrolle"]}
    beruehrt = set(im_plan) | set(kontrolle)
    zu_hoch, zu_tief = [], []
    for l in UEBBAR:
        if l not in beruehrt:
            if not s.loest(l, "B"):
                zu_hoch.append(l)
        elif l in im_plan and s.loest(l, "C") and im_plan[l] == "A":
            zu_tief.append(l)

    return {
        "name": s.name,
        "aufgaben": b["gestellt"],
        "richtig": b["richtig"],
        "prozent": b["prozent"],
        "profil": b["profil"],
        "planlaenge": b["plan_laenge"],
        "zu_hoch": zu_hoch,
        "zu_tief": zu_tief,
        "luecken_gesamt": len(s.luecken),
        "kontrolle": len(kontrolle),
        "luecken_gefunden": len(s.luecken & beruehrt),
        "start": b["start"],
    }


def schuelerschar() -> list[Schueler]:
    rng = random.Random(20250806)
    schar: list[Schueler] = []

    # ── Anfänger: kann nur die ersten drei Stränge ──────────────────────
    st = straenge()
    for i, decke in ((2, "A"), (3, "B")):
        kann = set()
        for s in st[:i]:
            kann |= set(s.lektionen)
        schar.append(Schueler(f"Anfänger (bis {st[i-1].nr}, Decke {decke})",
                              kann, decke))

    # ── Aufbau: die halbe Landkarte ─────────────────────────────────────
    for decke in ("A", "B", "C"):
        kann = set()
        for s in st[:len(st) // 2 + 1]:
            kann |= set(s.lektionen)
        schar.append(Schueler(f"Aufbau (halbe Karte, Decke {decke})", kann, decke))

    # ── Gymnasiast: kann alles, hat aber gezielte Lücken ────────────────
    alles = set(UEBBAR)
    for versuch in range(5):
        luecken = set(rng.sample(UEBBAR, 3 if versuch < 3 else 4))
        # Echte Lücken sind örtlich: er kann alles ausser diesen Stellen und
        # dem, was DIREKT darauf aufbaut. Ein Loch bei den Brüchen macht
        # ihn nicht zum Anfänger.
        kann = set(alles)
        for l in luecken:
            kann -= {x for x in alles if l in NETZ.get(x, [])}
        kann -= luecken
        schar.append(Schueler(
            f"Gymnasiast (Lücken {', '.join(sorted(luecken))})",
            kann, "C", luecken))

    # ── Perfekt ─────────────────────────────────────────────────────────
    schar.append(Schueler("Perfekt (kann alles auf C)", alles, "C"))
    schar.append(Schueler("Fast perfekt (Decke B)", alles, "B"))
    return schar


def main() -> int:
    print("Einstufungstest · Simulation")
    print(f"{len(straenge())} Stränge, {len(UEBBAR)} übbare Lektionen\n")

    zeilen = [durchlauf(s) for s in schuelerschar()]

    kopf = (f"{'Schüler':44} {'Aufg':>4} {'rtg':>4} {'Plan':>5} {'Ktrl':>5} "
            f"{'hoch':>5} {'tief':>5} {'Lücken':>8}")
    print(kopf)
    print("-" * len(kopf))
    fehler = []
    for z in zeilen:
        luecken = (f"{z['luecken_gefunden']}/{z['luecken_gesamt']}"
                   if z["luecken_gesamt"] else "—")
        print(f"{z['name'][:44]:44} {z['aufgaben']:>4} {z['richtig']:>4} "
              f"{z['planlaenge']:>5} {z['kontrolle']:>5} {len(z['zu_hoch']):>5} "
              f"{len(z['zu_tief']):>5} {luecken:>8}")
        if z["aufgaben"] > 31:
            fehler.append(f"{z['name']}: {z['aufgaben']} Aufgaben — über dem Limit")
        if z["aufgaben"] < 8:
            fehler.append(f"{z['name']}: nur {z['aufgaben']} Aufgaben — zu grob")
        if len(z["zu_hoch"]) > 6:
            fehler.append(f"{z['name']}: {len(z['zu_hoch'])} Lektionen zu hoch "
                          f"eingestuft ({', '.join(z['zu_hoch'][:8])})")
        if z["luecken_gesamt"] and z["luecken_gefunden"] < z["luecken_gesamt"] - 1:
            fehler.append(f"{z['name']}: {z['luecken_gefunden']} von "
                          f"{z['luecken_gesamt']} Lücken gefunden "
                          f"(offen: {', '.join(sorted(z['zu_hoch']))})")

    schnitt = sum(z["aufgaben"] for z in zeilen) / len(zeilen)
    hoch = sum(len(z["zu_hoch"]) for z in zeilen) / len(zeilen)
    tief = sum(len(z["zu_tief"]) for z in zeilen) / len(zeilen)
    print(f"\nDurchschnitt: {schnitt:.1f} Aufgaben · "
          f"{hoch:.1f} Lektionen zu hoch · {tief:.1f} zu tief")
    print("Plan = muss geübt werden · Ktrl = gutgeschrieben, kommt als "
          "Kontrollrunde auf Level C wieder")

    if fehler:
        print("\nBEFUNDE:")
        for f in fehler:
            print("  •", f)
        return 1
    print("\nAlles im Rahmen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
