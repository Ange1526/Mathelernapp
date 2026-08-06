# -*- coding: utf-8 -*-
"""
Testlauf über alle Schablonen — mit Schaltern, damit er nicht bei jeder
Kleinigkeit acht Minuten dauert.

    python tests/test_alle.py --liste        zeigt alle Schablonen
    python tests/test_alle.py K6 --wenig     ein Kapitel, Stichprobe, ~5 s
    python tests/test_alle.py K6             ein Kapitel, voll
    python tests/test_alle.py --geaendert    nur was sich seit dem letzten
                                             vollen Lauf geändert hat
    python tests/test_alle.py                voller Lauf über alles
    python tests/test_alle.py --einzeln      ohne Parallelbetrieb, für die
                                             Fehlersuche (Traceback bleibt lesbar)

WARUM DAS SCHNELL IST. Der alte Lauf prüfte 27 280 Aufgaben nacheinander in
einem Prozess und brauchte dafür rund vierzehn Minuten. Zwei Änderungen:

  1. Jede Bauform ist eine eigene Arbeitseinheit und läuft in einem eigenen
     Prozess. SymPy rechnet, der Rechner hat mehrere Kerne — es gibt keinen
     Grund, elf davon zuschauen zu lassen.
  2. `--wenig` nimmt zehn statt vierzig Aufgaben je Bauform und Level. Das
     findet beim Bauen fast alles und dauert Sekunden.

Nach `--wenig` wird der Stand bewusst NICHT gemerkt: eine Stichprobe von zehn
ist keine Freigabe. Vor dem Abschluss einer Runde immer den vollen Lauf.

WAS GEPRÜFT WIRD, je Bauform und Level:

  1. Die Bauform lässt sich überhaupt erzeugen
  2. Die Musterlösung wird als RICHTIG erkannt
  3. Jeder Eintrag im Fehlerkatalog wird als genau dieser Fehler erkannt
  4. Kein Exponent über zehn — der Parser weist solche Antworten ab, die
     Aufgabe wäre für die Schülerin unlösbar
  5. Die Levelachse: A, B und C müssen sich im AUFBAU unterscheiden
  6. Die Fehlerdichte: mindestens 1,6 Einträge je Aufgabe, keine Aufgabe
     ohne Eintrag

NEUE SCHABLONE? Trag sie in LAEUFE ein. Ohne diesen Eintrag wird sie nie
geprüft, und der Lauf meldet trotzdem ALLES BESTANDEN.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))

STAND = Path(__file__).resolve().parent / ".teststand.json"

VIEL, WENIG = 40, 10
MINDESTDICHTE = 1.6


# ══════════════════════════════════════════════════════════════════════════
# Die Schablonen
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Lauf:
    kapitel: str          # "K6"
    modul: str            # "generator.s6_punktrechnung"
    schablone: str        # "S20"
    #: Wie die Levelachse gemessen wird.
    #:   "streng"     hochgestellte Ziffern zählen NICHT als Aufbaumerkmal
    #:   "exponent"   sie zählen — nur wo Teil 2 den Exponenten als Regler
    #:                nennt (S22, S25)
    #:   "alt"        numerische Levelachse, bekannt und zur Ablösung
    #:                vorgemerkt. Wird gemessen, aber nicht beanstandet.
    achse: str = "streng"
    #: Bauformen, bei denen die Schablone selbst keinen Regler übrig lässt.
    ausnahmen: tuple = ()


LAEUFE = [
    # ── fertig, strukturelle Levelachse ──────────────────────────────────
    Lauf("K3", "generator.s3_terme", "S12"),
    Lauf("K3", "generator.s3_terme", "S13"),
    Lauf("K3", "generator.s3_terme", "S14"),
    Lauf("K4", "generator.s15_s17_sorten", "S15"),
    Lauf("K4", "generator.s16_gleichartig", "S16"),
    Lauf("K4", "generator.s15_s17_sorten", "S17"),
    Lauf("K5", "generator.s5_produkte", "S18"),
    Lauf("K5", "generator.s5_produkte", "S19"),
    Lauf("K6", "generator.s6_punktrechnung", "S20"),
    Lauf("K6", "generator.s6_punktrechnung", "S21"),
    #: S22 und S25: Teil 2 nennt den Exponenten als Regler. S22/BF4 sperrt
    #: ihn selbst — dort bleibt nur die Zahlengrösse, wie in Teil 1.
    Lauf("K7", "generator.s22_s23_potenzen", "S22", "exponent", ("BF4",)),
    Lauf("K7", "generator.s22_s23_potenzen", "S23"),
    Lauf("K7", "generator.s24_s25_potenzgesetze", "S24"),
    Lauf("K7", "generator.s24_s25_potenzgesetze", "S25", "exponent"),
    #: Kapitel 8: unter einer Wurzel gibt es weder Glieder noch Faktoren zu
    #: zaehlen — die Radikandengroesse IST der Regler. CLAUDE.md nennt S26
    #: ausdruecklich als die eine erlaubte Ausnahme. Fuer S27 bis S29 ist das
    #: bisher nur angenommen und in Teil 2 nachzulesen, wenn Kapitel 8 an die
    #: Reihe kommt — deshalb «zahl» und nicht «streng».
    Lauf("K8", "generator.s8_wurzeln", "S26", "zahl"),
    Lauf("K8", "generator.s8_wurzeln", "S27", "zahl"),
    Lauf("K8", "generator.s8_wurzeln", "S28", "zahl"),
    Lauf("K8", "generator.s8_wurzeln", "S29", "zahl"),
    Lauf("K9", "generator.s9_division", "S30"),
    Lauf("K9", "generator.s9_division", "S31"),
    Lauf("K9", "generator.s9_division", "S32"),
    #: Mischaufgaben. Die Levelachse traegt hier die Zahl der Teilschritte,
    #: der Glieder und der Variablen. Die Exponenten unter der Wurzel
    #: gehoeren zum Aufbau (a² gegen a⁴ ist ein anderer Rechenweg, nicht
    #: bloss eine andere Zahl) — darum «exponent» und nicht «streng».
    Lauf("K16", "generator.s60_mischen", "S60", "exponent"),
    Lauf("K13", "generator.s45_gleichungen", "S45"),
    Lauf("K13", "generator.s46_s47_klammern", "S46"),
    Lauf("K13", "generator.s47_brueche", "S47"),
    Lauf("K14", "generator.s14_bruchterme", "S49"),
    Lauf("K14", "generator.s50_s51_bruchterme", "S50"),
    Lauf("K14", "generator.s50_s51_bruchterme", "S51"),
    Lauf("K15", "generator.s15_bruchgleichungen", "S52"),
    Lauf("K15", "generator.s53_s54_bruchgleichungen", "S53"),
    Lauf("K15", "generator.s53_s54_bruchgleichungen", "S54"),
    # ── noch im alten Format, numerische Levelachse ──────────────────────
    #: S2 haengt an keiner Lektion mehr, wird aber weiter geprueft,
    #: solange die Datei existiert.
    Lauf("abgeloest", "generator.s2_grundoperationen", "S2", "alt"),
    Lauf("K10", "generator.s10_klammern", "S10", "alt"),
    Lauf("K12", "generator.s4_faktorisieren", "S4", "alt"),
]


#: ALTBEFUNDE — gefunden, als diese Messung zum ersten Mal über den ganzen
#: Bestand lief. Es sind keine neuen Fehler, sondern alte, die vorher niemand
#: gemessen hat: dort trägt zwischen zwei Stufen nur die Zahl.
#:
#: Sie stehen hier, damit der Lauf nicht dauerhaft rot ist und trotzdem
#: niemand sie vergisst — jeder Lauf zählt sie am Schluss auf. Wer das
#: betreffende Kapitel anfasst, streicht seine Zeile hier und baut die
#: Bauform nach Teil 2 der Schablone um.
ALTBEFUNDE = {
    "S13/BF9", "S14/BF5",           # Kapitel 3
    "S15/BF7", "S15/BF11",          # Kapitel 4
    "S18/BF1", "S18/BF11",          # Kapitel 5
    "S19/BF1", "S19/BF2", "S19/BF3", "S19/BF4",
}

#: Dasselbe für die Fehlerdichte. S10 wird in Runde K10 ersetzt, S18 hat
#: Bauformen ohne Katalogeintrag.
ALTBEFUNDE_DICHTE = {"S10", "S18"}


def auswahl(namen: list[str]) -> list[Lauf]:
    """K6, S20 oder generator/s6_punktrechnung.py — alles wird verstanden."""
    if not namen:
        return list(LAEUFE)
    raus = []
    for n in namen:
        stamm = Path(n).stem
        treffer = [l for l in LAEUFE
                   if n.upper() in (l.kapitel, l.schablone)
                   or l.modul.endswith("." + stamm)]
        if not treffer:
            print(f"Kenne «{n}» nicht. `--liste` zeigt, was es gibt.")
            sys.exit(2)
        for l in treffer:
            if l not in raus:
                raus.append(l)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Die Prüfung einer Bauform — läuft in einem eigenen Prozess
# ══════════════════════════════════════════════════════════════════════════

def _muster(text: str, streng: bool) -> str:
    """Zahlen zu #, Buchstaben zu ~. Was bleibt, ist der Aufbau."""
    if streng:
        for h in "¹²³⁴⁵⁶⁷⁸⁹⁰":
            text = text.replace(h, "#")
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"[a-zA-Z]", "~", text)
    return re.sub(r"\s+", "", text)


def pruefe_bauform(auftrag) -> dict:
    """(Lauf, Bauformnummer, Anzahl) -> Ergebnis. Muss importierbar sein,
    damit Windows den Prozess starten kann."""
    lauf, bf_nr, n = auftrag
    from sympy import Pow, expand

    from generator.anzeige import als_eingabe
    from korrektur import Status, auswerten

    modul = importlib.import_module(lauf.modul)
    S = getattr(modul, lauf.schablone)
    bf = S.bauform(bf_nr)

    rng = random.Random(20250801 + hash(bf_nr) % 1000)
    beanstandet, beispiele, muster = [], {}, {}
    anzahl = fehler_summe = ohne_eintrag = 0

    for lvl in bf.levels:
        muster[lvl] = set()
        for i in range(n):
            try:
                e = S.erzeugen(bf.nr, lvl, rng)
            except Exception as err:
                beanstandet.append(f"{S.nr}/{bf.nr}/{lvl}: {err}")
                break
            anzahl += 1
            muster[lvl].add(_muster(e.frage, lauf.achse != "exponent"))
            if lvl not in beispiele:
                beispiele[lvl] = f"{e.frage}  →  {e.loesung_text}"

            katalog = e.aufgabe.fehlerkatalog
            fehler_summe += len(katalog)
            if not katalog:
                ohne_eintrag += 1

            # 4 · Exponentengrenze des Parsers
            l = e.aufgabe.loesung.expr
            if l is not None and any(
                    t.exp.is_Integer and abs(int(t.exp)) > 10
                    for t in l.atoms(Pow)):
                beanstandet.append(
                    f"{S.nr}/{bf.nr}/{lvl}: «{e.frage}» — die Musterlösung "
                    f"hat einen Exponenten über zehn, der Parser weist sie ab")

            # 2 · die Musterlösung muss als richtig gelten
            a = auswerten(als_eingabe(e.loesung_text), e.aufgabe)
            if a.status is not Status.RICHTIG:
                beanstandet.append(
                    f"{S.nr}/{bf.nr}/{lvl}: «{e.frage}» — Musterlösung "
                    f"«{e.loesung_text}» gilt als {a.status.value}: {a.text}")

            # 3 · jeder Katalogeintrag muss als genau dieser Fehler kommen
            for f in katalog:
                txt = str(expand(f.ergebnis.expr)).replace("**", "^")
                r = auswerten(txt, e.aufgabe)
                if not (r.status is Status.FALSCH
                        and r.fehlerschluessel == f.schluessel):
                    beanstandet.append(
                        f"{S.nr}/{bf.nr}/{lvl}: «{e.frage}» — Fehler "
                        f"«{f.schluessel}» (Eingabe {txt}) kam als "
                        f"{r.status.value}/{r.fehlerschluessel} zurück")

    # 5 · Levelachse: gleiche Mustermenge heisst, das Level trägt nur Zahlen
    achse_gleich = []
    for x, y in (("A", "B"), ("A", "C"), ("B", "C")):
        if muster.get(x) and muster[x] == muster.get(y):
            achse_gleich.append(f"{x}={y}")
    ausnahme = (lauf.achse in ("alt", "zahl") or bf.nr in lauf.ausnahmen
                or f"{S.nr}/{bf.nr}" in ALTBEFUNDE)
    if achse_gleich and not ausnahme:
        beanstandet.append(
            f"{S.nr}/{bf.nr}: Levelachse — {', '.join(achse_gleich)} haben "
            f"denselben Aufbau. Das Level trägt hier nur die Zahlen.")

    return {"schablone": S.nr, "titel": S.titel, "bauform": bf.nr,
            "kapitel": lauf.kapitel, "beanstandet": beanstandet,
            "altbefund": f"{S.nr}/{bf.nr}" if (achse_gleich and
                                               f"{S.nr}/{bf.nr}" in ALTBEFUNDE)
                         else None,
            "anzahl": anzahl, "fehler_summe": fehler_summe,
            "ohne_eintrag": ohne_eintrag, "beispiele": beispiele,
            "achse_gleich": achse_gleich,
            "achse_ausnahme": bool(achse_gleich) and ausnahme}


def auftraege(laeufe, n):
    for lauf in laeufe:
        modul = importlib.import_module(lauf.modul)
        S = getattr(modul, lauf.schablone)
        for bf in S.bauformen:
            yield (lauf, bf.nr, n)


# ══════════════════════════════════════════════════════════════════════════
# Was sich geändert hat
# ══════════════════════════════════════════════════════════════════════════

def _stand_lesen() -> dict:
    try:
        return json.loads(STAND.read_text(encoding="utf8"))
    except Exception:
        return {}


def _zeitstempel(lauf: Lauf) -> float:
    pfad = WURZEL / (lauf.modul.replace(".", "/") + ".py")
    try:
        return pfad.stat().st_mtime
    except OSError:
        return 0.0


def geaendert(laeufe) -> list[Lauf]:
    """Alles, dessen Generatordatei jünger ist als der letzte volle Lauf.

    Die gemeinsamen Bauteile zählen mit: wer `qualitaet.py` oder
    `anzeige.py` anfasst, ändert damit jede Schablone.
    """
    stand = _stand_lesen()
    gemeinsam = max(
        (WURZEL / "generator" / f).stat().st_mtime
        for f in ("anzeige.py", "qualitaet.py", "schablone.py")
        if (WURZEL / "generator" / f).exists())
    return [l for l in laeufe
            if max(_zeitstempel(l), gemeinsam) > stand.get(l.schablone, 0)]


def _stand_schreiben(laeufe):
    stand = _stand_lesen()
    jetzt = time.time()
    for l in laeufe:
        stand[l.schablone] = jetzt
    STAND.write_text(json.dumps(stand, indent=1), encoding="utf8")


# ══════════════════════════════════════════════════════════════════════════

def berichten(ergebnisse, sekunden, wenig) -> int:
    """Je Schablone eine Zeile, danach alle Beanstandungen."""
    nach_schablone = {}
    for e in ergebnisse:
        nach_schablone.setdefault(e["schablone"], []).append(e)

    beanstandet = []
    print(f"\n{'Schablone':11s} {'Kap':4s} {'BF':>3s} {'Aufg.':>6s} "
          f"{'Dichte':>7s}  {'Achse':7s}  Beispiel")
    print("-" * 100)
    for nr, teile in nach_schablone.items():
        anzahl = sum(t["anzahl"] for t in teile)
        summe = sum(t["fehler_summe"] for t in teile)
        ohne = sum(t["ohne_eintrag"] for t in teile)
        dichte = summe / anzahl if anzahl else 0
        eigene = [z for t in teile for z in t["beanstandet"]]
        achse = [t for t in teile if t["achse_gleich"]]
        nur_ausnahme = achse and all(t["achse_ausnahme"] for t in achse)

        if nr not in ALTBEFUNDE_DICHTE:
            if dichte < MINDESTDICHTE:
                eigene.append(f"{nr}: Fehlerdichte {dichte:.2f} — verlangt "
                              f"sind {MINDESTDICHTE}")
            if ohne:
                eigene.append(f"{nr}: {ohne} Aufgaben ohne Eintrag im "
                              f"Fehlerkatalog")
        beanstandet += eigene

        zeichen = "ok" if not eigene else "FEHLER"
        achse_txt = "ok" if not achse else ("Ausnahme" if nur_ausnahme
                                            else "GLEICH")
        beispiel = next((t["beispiele"].get("A", "") for t in teile
                         if t["beispiele"]), "")
        print(f"{nr + ' ' + zeichen:11s} {teile[0]['kapitel']:4s} "
              f"{len(teile):3d} {anzahl:6d} {dichte:7.2f}  {achse_txt:7s}  "
              f"{beispiel[:44]}")

    offen = sorted({e["altbefund"] for e in ergebnisse if e["altbefund"]})
    if offen:
        print(f"\nAltbefunde, noch offen ({len(offen)}): "
              f"{', '.join(offen)}")
        print("    Dort trägt zwischen zwei Stufen nur die Zahl. Gehört in "
              "die Runde des jeweiligen Kapitels.")

    gesamt = sum(e["anzahl"] for e in ergebnisse)
    print(f"\n{gesamt} Aufgaben in {sekunden:.1f} s"
          f"{'  (Stichprobe — keine Freigabe)' if wenig else ''}")
    if beanstandet:
        print(f"\n{len(beanstandet)} Beanstandungen:")
        for z in beanstandet[:25]:
            print("   ", z)
        if len(beanstandet) > 25:
            print(f"    … und {len(beanstandet) - 25} weitere")
        print("\nBEANSTANDUNGEN")
    else:
        print("\nALLES BESTANDEN")
    return len(beanstandet)


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("namen", nargs="*", help="Kapitel (K6) oder Schablone (S20)")
    p.add_argument("--wenig", action="store_true",
                   help="zehn statt vierzig Aufgaben je Bauform und Level")
    p.add_argument("--geaendert", action="store_true",
                   help="nur was sich seit dem letzten vollen Lauf änderte")
    p.add_argument("--einzeln", action="store_true",
                   help="ohne Parallelbetrieb")
    p.add_argument("--liste", action="store_true")
    a = p.parse_args()

    if a.liste:
        print(f"{'Kap':5s} {'Nr':5s} Modul")
        for l in LAEUFE:
            zusatz = {"alt": "   (alte, numerische Levelachse)",
                      "exponent": "   (Levelachse: Exponent)"}.get(l.achse, "")
            print(f"{l.kapitel:5s} {l.schablone:5s} {l.modul}{zusatz}")
        print(f"\n{len(LAEUFE)} Schablonen in "
              f"{len({l.kapitel for l in LAEUFE})} Kapiteln.")
        return 0

    laeufe = auswahl(a.namen)
    if a.geaendert:
        laeufe = geaendert(laeufe)
        if not laeufe:
            print("Nichts geändert seit dem letzten vollen Lauf.")
            return 0
        print("Geändert: " + ", ".join(l.schablone for l in laeufe))

    n = WENIG if a.wenig else VIEL
    jobs = list(auftraege(laeufe, n))
    print(f"{len(laeufe)} Schablonen · {len(jobs)} Bauformen · "
          f"{n} Aufgaben je Bauform und Level")

    beginn = time.time()
    if a.einzeln:
        ergebnisse = [pruefe_bauform(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=min(10, (os.cpu_count() or 2))) as pool:
            ergebnisse = list(pool.map(pruefe_bauform, jobs, chunksize=1))
    dauer = time.time() - beginn

    anzahl = berichten(ergebnisse, dauer, a.wenig)
    #: Nach einer Stichprobe wird der Stand NICHT gemerkt — sonst hielte
    #: `--geaendert` zehn Aufgaben für eine Freigabe.
    if not anzahl and not a.wenig:
        _stand_schreiben(laeufe)
    return 1 if anzahl else 0


if __name__ == "__main__":
    sys.exit(main())
