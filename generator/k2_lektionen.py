# -*- coding: utf-8 -*-
"""
K2 — eine Schablone je Lektion

WARUM DIESE DATEI
-----------------
Kapitel 2 hatte dasselbe Problem wie Kapitel 1 vor der Neufassung: sechs
Schablonen bedienten dreizehn Lektionen, und was der Titel versprach, stand
nicht in der Aufgabe. Nachgemessen:

    2.1  «Brüche verstehen»                 zeigte  «Kürze 7/9»
    2.3  «Addition bei gleichem Nenner»     zeigte  «4/3 − 5/4»
    2.5  «Hauptnenner bestimmen»            zeigte  «1/3 + 4/3»
    2.8  «Brüche mit ganzen Zahlen
          subtrahieren»                     zeigte  «3/2 + 1»
    2.11 «Brüche mal und durch ganze
          Zahlen»                           zeigte  «(7/12)²»

In der Lektion zur Subtraktion stand also eine Addition, und beim
Hauptnenner hatten beide Brüche denselben. Wer danach den Test schreibt,
merkt es zum ersten Mal — und dann ist es zu spät.

WIE ES BEHOBEN IST
------------------
Die Bauformen selbst waren in Ordnung: sie sind sauber getrennt, es fehlte
nur die Zuordnung. Statt sie neu zu schreiben, setzt diese Datei aus den
vorhandenen Bauformen je Lektion eine eigene Schablone zusammen — mit
genau den Formen, die zum Titel gehören.

Das hat einen Nebeneffekt, den man kennen muss: eine Lektion hat jetzt
zwei bis fünf Bauformen statt zwölf. Sie gilt darum FRÜHER als sicher —
vier bis zehn richtige Antworten statt vierundzwanzig. Für eine Lektion
mit einer einzigen Regel («gleicher Nenner: Zähler addieren») ist das
richtig; zwölf Bauformen brauchte es nur, weil zwölf Lektionen darin
steckten.
"""
from __future__ import annotations

from .s7_kuerzen_erweitern import S7
from .s8_addition_subtraktion import S8
from .s9_ganze_zahlen import S9
from .s10_multiplikation import S10
from .s11_division import S11
from .s12_doppelbrueche import S58
from .schablone import Schablone


def _bf(schablone: Schablone, *nummern: str) -> list:
    """Holt Bauformen aus einer bestehenden Schablone heraus."""
    nach_nr = {b.nr: b for b in schablone.bauformen}
    fehlend = [n for n in nummern if n not in nach_nr]
    if fehlend:
        raise KeyError(f"{schablone.nr}: Bauform {fehlend} gibt es nicht")
    return [nach_nr[n] for n in nummern]


def _neu(nr, titel, lektion, quelle, nummern, anleitung, kernidee,
         levelachse=None):
    return Schablone(
        nr=nr, titel=titel, lektionen=lektion, erhebung="",
        anleitung=anleitung,
        levelachse=levelachse or quelle.levelachse,
        bauformen=_bf(quelle, *nummern),
        kernidee=kernidee,
    )


# ── 2.1 · Brüche verstehen ───────────────────────────────────────────────
# Der Einstieg. Hier wird noch nicht gekürzt, sondern nur geschaut, ob sich
# überhaupt etwas kürzen lässt — und was passiert, wenn der Bruch aufgeht.
K2_1 = _neu(
    "S7a", "Brüche verstehen", "2.1", S7, ("BF4", "BF5"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Ein Bruch sagt, in wie viele Teile geteilt wurde (Nenner) und wie "
    "viele davon gemeint sind (Zähler). Geht die Division auf, steht am "
    "Ende eine ganze Zahl.")

# ── 2.2 · Kürzen und Erweitern ───────────────────────────────────────────
K2_2 = _neu(
    "S7b", "Kürzen und Erweitern", "2.2", S7, ("BF1", "BF4", "BF5"),
    "Kürze so weit wie möglich.",
    "Kürzen heisst: Zähler UND Nenner durch dieselbe Zahl teilen. Der Wert "
    "des Bruchs ändert sich dabei nicht.")

# ── 2.3 · Addition bei gleichem Nenner ───────────────────────────────────
# NUR Addition, NUR gleiche Nenner. Kein Minus, kein Erweitern.
K2_3 = _neu(
    "S8a", "Addition bei gleichem Nenner", "2.3", S8, ("BF1", "BF10"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Haben zwei Brüche denselben Nenner, werden nur die Zähler addiert. "
    "Der Nenner bleibt stehen.")

# ── 2.4 · Subtraktion bei gleichem Nenner ────────────────────────────────
#: NUR BF2. Der Sonderfall «Ergebnis ist null» (BF11) benutzt intern die
#: Form «plus, dann minus» — in einer Lektion mit dem Titel «Subtraktion»
#: stand dadurch ein Pluszeichen. Genau der Fehler, um den es hier geht.
K2_4 = _neu(
    "S8b", "Subtraktion bei gleichem Nenner", "2.4", S8, ("BF2",),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Wie beim Addieren: nur die Zähler werden verrechnet, der Nenner "
    "bleibt stehen.")

# ── 2.5 · Hauptnenner bestimmen ──────────────────────────────────────────
# Hier MÜSSEN die Nenner verschieden sein — sonst gibt es nichts zu
# bestimmen. Genommen werden die Formen, bei denen ein Nenner ein
# Vielfaches des anderen ist: der leichteste Fall des Erweiterns.
K2_5 = _neu(
    "S8c", "Hauptnenner bestimmen", "2.5", S8, ("BF4", "BF5"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Verschiedene Nenner müssen erst gleichnamig werden. Der Hauptnenner "
    "ist die kleinste Zahl, die beide Nenner teilen — oft der grössere "
    "der beiden.")

# ── 2.6 · Addition und Subtraktion bei ungleichen Nennern ────────────────
K2_6 = _neu(
    "S8d", "Addition und Subtraktion bei ungleichen Nennern", "2.6", S8,
    #: BF12 («ein Summand ist eine ganze Zahl») gehört NICHT hierher —
    #: das ist der Inhalt von 2.7. Genau diese Sorte Vermischung soll die
    #: Datei ja beheben.
    ("BF7", "BF8", "BF9"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Erst den Hauptnenner suchen, dann jeden Bruch erweitern, dann die "
    "Zähler verrechnen.")

# ── 2.7 · Brüche mit ganzen Zahlen addieren ──────────────────────────────
K2_7 = _neu(
    "S9a", "Brüche mit ganzen Zahlen addieren", "2.7", S9,
    ("BF1", "BF2", "BF9"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Eine ganze Zahl ist auch ein Bruch: 2 = 2/1. Schreib sie mit dem "
    "Nenner des anderen Bruchs, dann lässt sich addieren.")

# ── 2.8 · Brüche mit ganzen Zahlen subtrahieren ──────────────────────────
# NUR Minus. BF3 «Bruch minus ganze Zahl», BF4 «Ganze Zahl minus Bruch»,
# BF12 «Ergebnis negativ» — alle drei ohne Pluszeichen.
K2_8 = _neu(
    "S9b", "Brüche mit ganzen Zahlen subtrahieren", "2.8", S9,
    ("BF3", "BF4", "BF12"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Auch beim Abziehen wird die ganze Zahl zuerst als Bruch geschrieben. "
    "Steht sie hinten, kann das Ergebnis negativ werden.")

# ── 2.9 · Multiplikation von Brüchen ─────────────────────────────────────
# Nur Bruch mal Bruch. Ganze Zahlen sind 2.11, die Hochzahl gehört nicht
# in diese Lektion.
K2_9 = _neu(
    "S10a", "Multiplikation von Brüchen", "2.9", S10,
    ("BF1", "BF5", "BF6", "BF11"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Zähler mal Zähler, Nenner mal Nenner. Anders als beim Addieren bleibt "
    "der Nenner NICHT stehen.")

# ── 2.10 · Division von Brüchen ──────────────────────────────────────────
K2_10 = _neu(
    "S11a", "Division von Brüchen", "2.10", S11,
    ("BF1", "BF6", "BF8", "BF11"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Durch einen Bruch teilen heisst: mit seinem Kehrwert malnehmen. "
    "Gestürzt wird der ZWEITE Bruch.")

# ── 2.11 · Brüche mal und durch ganze Zahlen ─────────────────────────────
# Hier gehören die ganzen Zahlen hin — aus beiden Schablonen.
K2_11 = Schablone(
    nr="S10b", titel="Brüche mal und durch ganze Zahlen", lektionen="2.11",
    erhebung="", anleitung="Rechne aus. Gib das Resultat in gekürzter Form an.",
    levelachse="Zahl der Faktoren",
    bauformen=(_bf(S10, "BF2", "BF3", "BF4")
               + _bf(S11, "BF4", "BF5")),
    kernidee=("Eine ganze Zahl ist ein Bruch mit dem Nenner eins. Beim "
              "Malnehmen wächst der Zähler, beim Teilen der Nenner."),
)

# ── 2.12 · Doppelbrüche ──────────────────────────────────────────────────
K2_12 = _neu(
    "S58a", "Doppelbrüche", "2.12", S58,
    ("BF1", "BF2", "BF3", "BF4", "BF5", "BF11"),
    "Rechne aus. Gib das Resultat in gekürzter Form an.",
    "Ein Doppelbruch ist nichts Neues: der grosse Bruchstrich ist ein "
    "Doppelpunkt. (a/b)/(c/d) heisst a/b : c/d.")

# ── 2.13 · Gemischt ──────────────────────────────────────────────────────
# Die Mischlektion darf alles — sie ist die einzige, in der Formen aus
# mehreren Themen nebeneinanderstehen dürfen.
K2_13 = Schablone(
    nr="M2", titel="Gemischt: alles aus Kapitel 2", lektionen="2.13",
    erhebung="", anleitung="Rechne aus. Gib das Resultat in gekürzter Form an.",
    levelachse="Zahl der Glieder",
    bauformen=(_bf(S8, "BF7", "BF9")
               + _bf(S9, "BF1", "BF3")
               + _bf(S10, "BF1", "BF4")
               + _bf(S11, "BF1", "BF5")
               + _bf(S58, "BF6", "BF10")),
    kernidee=("Alles aus Kapitel 2 gemischt: erst hinschauen, welche "
              "Rechenart dasteht, dann die passende Regel anwenden."),
)


#: Zusaetzliche Namen unter der Schablonennummer.
#:
#: Der Testlauf sucht die Schablone ueber `getattr(modul, "S7a")`. Die
#: Variablen heissen hier aber K2_1 bis K2_13, weil das beim Lesen der
#: Zuordnung hilft. Beides ist dasselbe Objekt — die folgenden Zeilen geben
#: ihm nur seinen zweiten Namen.
S7a, S7b = K2_1, K2_2
S8a, S8b, S8c, S8d = K2_3, K2_4, K2_5, K2_6
S9a, S9b = K2_7, K2_8
S10a, S11a, S10b = K2_9, K2_10, K2_11
S58a, M2 = K2_12, K2_13
