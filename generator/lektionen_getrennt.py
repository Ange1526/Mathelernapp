# -*- coding: utf-8 -*-
"""
Sieben Lektionen, deren Aufgaben nicht zu ihrem Titel passten

Gefunden bei der Durchsicht des ganzen Netzes, nachdem dieselbe Fehlerart
in Kapitel 1 und Kapitel 2 aufgetreten war. Der Befund im Einzelnen:

    7.5  «Multiplikation von Potenzen»      zeigte  a⁷ : a  und  u⁴ − u²
    7.6  «Division von Potenzen»            zeigte  m⁴ · m · n³
    8.6  «Wurzelgesetz bei Division»        zeigte  3√5 + √5,  √5 · √20
    13.7 «Klammern auf beiden Seiten»       zeigte  6x − 5 = 6
    3.8  «Subtrahieren unterschiedlicher
          Variablen»                        zeigte  m + m + v
    4.3  «Subtraktion gleichartiger Terme»  zeigte  überwiegend Additionen
    12.3 «Gemeinsame Variable ausklammern»  zeigte  105u − 70v

Bei 7.5 und 7.6 waren Multiplikation und Division schlicht vertauscht:
wer die Multiplikationslektion übte, trainierte Division. Beide hängen an
Erhebungsaufgabe 3c.

WIE ES BEHOBEN IST — wie schon bei Kapitel 2: Die Bauformen selbst sind
richtig und bleiben unverändert. Nur die Zuordnung wird je Lektion neu
zusammengesetzt, aus genau den Formen, die zum Titel gehören. Kein
Eingriff in die Rechnung, keine neuen Aufgaben.

NEBENEFFEKT: Eine Lektion hat danach zwei bis vier Bauformen statt zwölf
und gilt entsprechend früher als sicher. Für eine Lektion mit EINER Regel
ist das richtig — zwölf Bauformen brauchte es nur, weil mehrere Lektionen
in derselben Schablone steckten.
"""
from __future__ import annotations

from .s3_terme import S13
from .s8_wurzeln import S28
from .s16_gleichartig import S16
from .s24_s25_potenzgesetze import S24
from .s42_s44_faktorisieren import S42
from .s47_brueche import S47
from .schablone import Schablone


def _bf(schablone: Schablone, *nummern: str) -> list:
    nach_nr = {b.nr: b for b in schablone.bauformen}
    fehlend = [n for n in nummern if n not in nach_nr]
    if fehlend:
        raise KeyError(f"{schablone.nr}: Bauform {fehlend} gibt es nicht")
    return [nach_nr[n] for n in nummern]


def _neu(nr, titel, lektion, quelle, nummern, kernidee, anleitung=None):
    return Schablone(
        nr=nr, titel=titel, lektionen=lektion, erhebung="",
        anleitung=anleitung or quelle.anleitung,
        levelachse=quelle.levelachse,
        bauformen=_bf(quelle, *nummern),
        kernidee=kernidee,
    )


# ══════════════════════════════════════════════════════════════════════════
#  7.5 · Multiplikation von Potenzen        (Erhebung 3c)
# ══════════════════════════════════════════════════════════════════════════
# NUR Multiplikation. BF1 «Hochzahlen addieren», BF6 «Ergebnis ist eins»
# (entsteht beim Malnehmen mit einer negativen Hochzahl), BF8 «mit
# Koeffizienten» — alle drei ohne Doppelpunkt.
P_MAL = _neu(
    "S24a", "Multiplikation von Potenzen", "7.5", S24,
    ("BF1", "BF8"),
    "Werden zwei Potenzen mit derselben Basis multipliziert, werden die "
    "Hochzahlen ADDIERT: a³ · a² = a⁵. Die Basis bleibt.")

# ══════════════════════════════════════════════════════════════════════════
#  7.6 · Division von Potenzen              (Erhebung 3c)
# ══════════════════════════════════════════════════════════════════════════
P_GETEILT = _neu(
    "S24b", "Division von Potenzen", "7.6", S24,
    ("BF2", "BF6"),
    "Werden zwei Potenzen mit derselben Basis dividiert, werden die "
    "Hochzahlen SUBTRAHIERT: a⁵ : a² = a³.")

# ══════════════════════════════════════════════════════════════════════════
#  7.7 · Potenzen und Strichoperatoren
# ══════════════════════════════════════════════════════════════════════════
# Hier gehört die Addition hin — und der Fall, in dem sich nichts
# zusammenfassen lässt. Genau das ist der Inhalt dieser Lektion.
P_STRICH = _neu(
    "S24c", "Potenzen und Strichoperatoren", "7.7", S24,
    ("BF4", "BF10"),
    "Beim Addieren und Subtrahieren gilt KEIN Potenzgesetz. a³ + a³ ist "
    "2a³, und a³ + a² lässt sich gar nicht zusammenfassen.")

# ══════════════════════════════════════════════════════════════════════════
#  7.8 · Potenz einer Potenz
# ══════════════════════════════════════════════════════════════════════════
P_HOCH = _neu(
    "S24d", "Potenz einer Potenz", "7.8", S24,
    ("BF3", "BF11", "BF12"),
    "Wird eine Potenz nochmals potenziert, werden die Hochzahlen "
    "MULTIPLIZIERT: (a³)² = a⁶.")


# ══════════════════════════════════════════════════════════════════════════
#  8.5 · Wurzeln multiplizieren und dividieren
# ══════════════════════════════════════════════════════════════════════════
W_PUNKT = _neu(
    "S28a", "Wurzeln multiplizieren und dividieren", "8.5", S28,
    ("BF1", "BF2", "BF6"),
    "Zwei Wurzeln lassen sich unter EINE Wurzel zusammenziehen: "
    "√a · √b = √(a·b) und √a : √b = √(a:b).")

# ══════════════════════════════════════════════════════════════════════════
#  8.6 · Wurzelgesetz bei Division          (Erhebung 3a)
# ══════════════════════════════════════════════════════════════════════════
# NUR Division. BF2 «Quotient zweier Wurzeln», BF4 «Quotient unter einer
# Wurzel», BF11 «Division, beide keine Quadratzahlen» — kein Pluszeichen,
# kein Malpunkt.
W_GETEILT = _neu(
    "S28b", "Wurzelgesetz bei Division anwenden", "8.6", S28,
    ("BF2", "BF4", "BF11"),
    "√a : √b = √(a:b). Oft geht der Bruch unter der Wurzel auf, und dann "
    "bleibt eine glatte Zahl.")

# ══════════════════════════════════════════════════════════════════════════
#  8.4 · Wurzeln addieren und subtrahieren
# ══════════════════════════════════════════════════════════════════════════
#: NUR BF5. BF9 («Ergebnis ist eins») benutzt intern eine Division und
#: zeigte «√36 : √36» in einer Lektion ueber Addition.
W_STRICH = _neu(
    "S28c", "Wurzeln addieren und subtrahieren", "8.4", S28,
    ("BF5",),
    "Beim Addieren gilt das Wurzelgesetz NICHT: √a + √b ist nicht "
    "√(a+b). Nur gleiche Wurzeln lassen sich zusammenzählen.")


# ══════════════════════════════════════════════════════════════════════════
#  13.7 · Klammern auf beiden Seiten        (Erhebung 1a)
# ══════════════════════════════════════════════════════════════════════════
# NUR Formen mit Klammer. BF3, BF4 und BF10 haben eine, BF1 und BF2 nicht.
G_KLAMMER = _neu(
    "S47a", "Klammern auf beiden Seiten", "13.7", S47,
    ("BF3", "BF4", "BF10"),
    "Stehen auf beiden Seiten Klammern, werden zuerst beide "
    "ausmultipliziert. Danach ist es eine gewöhnliche Gleichung.")

# ══════════════════════════════════════════════════════════════════════════
#  13.9 · Lösung als gekürzter Bruch oder Dezimalzahl
# ══════════════════════════════════════════════════════════════════════════
G_BRUCH = _neu(
    "S47b", "Lösung als gekürzter Bruch oder Dezimalzahl", "13.9", S47,
    ("BF1", "BF2", "BF9"),
    "Geht die Division nicht auf, bleibt die Lösung ein Bruch — und der "
    "wird gekürzt. −4/6 ist nicht fertig, −2/3 schon.")


# ══════════════════════════════════════════════════════════════════════════
#  3.7 / 3.8 · Verschiedene Variablen addieren bzw. subtrahieren
# ══════════════════════════════════════════════════════════════════════════
# S13 hat für verschiedene Variablen nur BF4 (addieren). Für 3.8 wird
# darum BF2 genommen — «addieren UND subtrahieren» — zusammen mit dem
# Sonderfall, in dem sich eine Sorte aufhebt. Beide enthalten ein Minus.
V_ADD = _neu(
    "S13a", "Addieren unterschiedlicher Variablen", "3.7", S13,
    ("BF4",),
    "Nur gleiche Variablen lassen sich zusammenzählen. a + b bleibt a + b — "
    "das ist kein halbes Ergebnis, sondern das ganze.")

V_SUB = _neu(
    "S13b", "Subtrahieren unterschiedlicher Variablen", "3.8", S13,
    ("BF2", "BF8", "BF10"),
    "Auch beim Abziehen gilt: nur gleiche Variablen lassen sich "
    "verrechnen. Was übrig bleibt, bleibt stehen.")


# ══════════════════════════════════════════════════════════════════════════
#  4.2 / 4.3 · Gleichartige Terme addieren bzw. subtrahieren
# ══════════════════════════════════════════════════════════════════════════
#: EHRLICHERWEISE nur eine Teilloesung. In S16 enthaelt JEDE Bauform ein
#: Minuszeichen — eine reine Additionsaufgabe gibt es dort nicht. Die
#: Trennung hilft trotzdem: 4.3 bekommt die Formen, in denen das Minus der
#: Punkt ist (Klammer mit Minus davor, Minus am Anfang), 4.2 die uebrigen.
#: Ein sauberer 4.2-Fall braeuchte eine neue Bauform ohne Minus — das ist
#: eine Aenderung am Generator, keine Umsortierung, und steht darum aus.
T_ADD = _neu(
    "S16a", "Addition gleichartiger Terme", "4.2", S16,
    ("BF1", "BF2", "BF8"),
    "Gleichartige Terme haben dieselbe Variable in derselben Potenz. Nur "
    "sie lassen sich zusammenfassen — die Koeffizienten werden addiert.")

T_SUB = _neu(
    "S16b", "Subtraktion gleichartiger Terme", "4.3", S16,
    ("BF3", "BF6", "BF7", "BF11"),
    "Beim Abziehen zählt das Vorzeichen. Steht ein Minus vor einer "
    "Klammer, dreht es jedes Vorzeichen darin um.")


# ══════════════════════════════════════════════════════════════════════════
#  12.2 / 12.3 · Zahl bzw. Variable ausklammern
# ══════════════════════════════════════════════════════════════════════════
A_ZAHL = _neu(
    "S42a", "Gemeinsame Zahl ausklammern", "12.2", S42,
    ("BF1", "BF2", "BF11"),
    "Steht in allen Gliedern derselbe Zahlenfaktor, kommt er vor die "
    "Klammer. Genommen wird der GRÖSSTE gemeinsame Teiler.")

A_VARIABLE = _neu(
    "S42b", "Gemeinsame Variable ausklammern", "12.3", S42,
    ("BF3", "BF12"),
    "Steht in allen Gliedern dieselbe Variable, kommt sie vor die "
    "Klammer — auch wenn sich bei den Zahlen nichts ausklammern lässt.")


#: Zweitnamen unter der Schablonennummer — der Testlauf sucht sie ueber
#: `getattr(modul, "S24a")`.
S13a, S13b = V_ADD, V_SUB
S16a, S16b = T_ADD, T_SUB
S24a, S24b, S24c, S24d = P_MAL, P_GETEILT, P_STRICH, P_HOCH
S28a, S28b, S28c = W_PUNKT, W_GETEILT, W_STRICH
S42a, S42b = A_ZAHL, A_VARIABLE
S47a, S47b = G_KLAMMER, G_BRUCH
