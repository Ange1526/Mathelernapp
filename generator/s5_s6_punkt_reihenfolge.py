# -*- coding: utf-8 -*-
"""
S5 · Multiplizieren und Dividieren        (Lektionen 1.10 – 1.15)
S6 · Die Reihenfolge der Operationen      (Lektionen 1.16 – 1.19)

    «Rechne aus.»
    6 · (−7)      (−6) · (−7)      (−48) : 6      5 + 3 · (−4)      36 : 6 : 2

Wie S1 und S3 ohne `.docx`-Vorlage gebaut, aus den Lektionstiteln in
`netz_daten.py`. Der Baukasten steht in `k1_bausteine.py`.

DIE VORZEICHENREGEL IST EINE ZÄHLREGEL. `(−6) · (−7)` ist positiv, nicht
weil sich zwei Minus «aufheben», sondern weil eine GERADE Anzahl davon
dasteht. Bei drei Faktoren merkt man den Unterschied — darum hat S5 mit BF11
eine eigene Bauform für drei Vorzeichen. Wer paarweise wegstreicht, kommt
bei zweien durch und bei dreien nicht.

DIVISIONEN GEHEN IMMER AUF. Sie werden rückwärts gebaut: erst der Quotient,
dann mal dem Divisor. Ein Bruch als Ergebnis wäre Kapitel 2, und der Filter
`ganz` verwirft ihn ohnehin.

WORAN S6 HÄNGT: an zwei Regeln, die verwechselt werden. «Punkt vor Strich»
sagt, WELCHE Operation zuerst kommt; «von links nach rechts» sagt, in
welcher Reihenfolge gleichrangige drankommen. `36 : 6 : 2` ist 3, nicht 12 —
und das ist ein anderer Fehler als `5 + 3 · 4` als 32 zu rechnen. Beide
stehen als eigener Katalogeintrag drin, `punkt_von_rechts` und `von_links`.

LEVELACHSE — strukturell:

    S5   A zwei Faktoren · B drei Glieder oder ein zweites Vorzeichen ·
         C drei Faktoren mit gemischten Vorzeichen
    S6   A zwei Operationen · B drei · C vier, beide Sorten gemischt

Die Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from .k1_bausteine import (ANLEITUNG, BF, Kl, SONDER, STANDARD, VZ, Z, bau,
                           kette)
from .schablone import Schablone


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"a": [3, 4, 6, 7], "b": [2, 3, 5, 8], "c": [2, 3, 4, 5],
            "d": [2, 3, 6, 9], "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


# ══════════════════════════════════════════════════════════════════════════
# S5 · Multiplizieren und Dividieren        (1.10 – 1.15)
# ══════════════════════════════════════════════════════════════════════════

def bf5_1(p):
    """Multiplikation mit positiven Zahlen:  6 · 7      (Lektion 1.10)

    Der bekannte Fall. Er steht hier, damit ein Schüler, der ganz unten
    einsteigt, mit etwas beginnt, das er kann — und damit die Bauformen mit
    Vorzeichen einen Vergleich haben.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("·", Z(b + 4))))
    if st == 2:
        return bau(kette(Z(a), ("·", Z(b)), ("·", Z(c))))
    return bau(kette(Z(a), ("·", Z(b)), ("·", Z(c)), ("·", Z(2))))


BF5_1 = BF("BF1", "Multiplikation mit positiven Zahlen", BEREICH, bf5_1)


def bf5_2(p):
    """Positiv mal negativ:  6 · (−7)                    (Lektion 1.11)

    Ein Minus unter den Faktoren, also ist das Ergebnis negativ. Die Zahl
    selbst ändert sich nicht — nur ihr Vorzeichen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("·", Z(-(b + 4)))))
    if st == 2:
        return bau(kette(Z(a), ("·", Z(-b)), ("·", Z(c))))
    return bau(kette(Z(a), ("·", Z(-b)), ("·", Z(c)), ("·", Z(2))))


BF5_2 = BF("BF2", "Positiv mal negativ", BEREICH, bf5_2)


def bf5_3(p):
    """Negativ mal positiv:  (−6) · 7                    (Lektion 1.11)

    Derselbe Fall wie BF2, aber das Minus steht vorne. Dass die Reihenfolge
    nichts ändert, ist nicht selbstverständlich — beim Subtrahieren ändert
    sie alles.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("·", Z(b + 4))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("·", Z(b)), ("·", Z(c))))
    return bau(kette(Kl(Z(-a)), ("·", Z(b)), ("·", Z(c)), ("·", Z(2))))


BF5_3 = BF("BF3", "Negativ mal positiv", BEREICH, bf5_3)


def bf5_4(p):
    """Zwei negative Faktoren:  (−6) · (−7)              (Lektion 1.12)

    Zwei Minus, also ein positives Ergebnis. Der Grund ist eine ZÄHLREGEL:
    bei gerader Anzahl positiv, bei ungerader negativ. Wer stattdessen
    «zwei Minus heben sich auf» lernt, kommt bei BF11 mit drei Faktoren
    nicht durch.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("·", Z(-(b + 4)))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("·", Z(-b)), ("·", Z(c))))
    return bau(kette(Kl(Z(-a)), ("·", Z(-b)), ("·", Z(c)), ("·", Z(2))))


BF5_4 = BF("BF4", "Zwei negative Faktoren", BEREICH, bf5_4)


def bf5_5(p):
    """Division mit positiven Zahlen:  48 : 6           (Lektion 1.13)

    Die Aufgabe wird rückwärts gebaut — erst der Quotient, dann mal dem
    Divisor. So geht sie immer auf; ein Bruch als Ergebnis wäre Kapitel 2.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * (b + 4)), (":", Z(b + 4))))
    if st == 2:
        return bau(kette(Z(a * b * c), (":", Z(b)), (":", Z(c))))
    return bau(kette(Z(a * b * c * 2), (":", Z(b)), ("·", Z(c)),
                     (":", Z(2))))


BF5_5 = BF("BF5", "Division mit positiven Zahlen", BEREICH, bf5_5)


def bf5_6(p):
    """Division mit unterschiedlichen Vorzeichen:  48 : (−6)  (Lektion 1.14)

    Dieselbe Zählregel wie beim Malnehmen. Dass sie auch beim Teilen gilt,
    ist eine eigene Lektion — und für viele eine eigene Überraschung.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-(a * (b + 4)))), (":", Z(b + 4))))
    if st == 2:
        return bau(kette(Z(a * b * c), (":", Z(-b)), (":", Z(c))))
    return bau(kette(Z(a * b * c * 2), (":", Z(-b)), ("·", Z(c)),
                     (":", Z(2))))


#: Vier Katalogeinträge auf Level A, aus demselben Grund wie bei S3/BF7:
#: steht in einer Division mit zwei Zahlen genau EIN Minus, dann sind
#: «Vorzeichen übersehen» und «Vorzeichen des Ergebnisses gedreht» derselbe
#: Zahlenwert. Ab Level B mit drei Zahlen sind es wieder fünf.
BF5_6 = BF("BF6", "Division mit unterschiedlichen Vorzeichen", BEREICH,
           bf5_6, filter=SONDER)


def bf5_7(p):
    """Division zweier negativer Zahlen:  (−48) : (−6)  (Lektion 1.15)

    Zwei Minus, also ein positives Ergebnis — dieselbe Zählregel wie bei
    BF4, nur mit dem Divisionszeichen. Wer sie beim Malnehmen kann und
    hier nicht, hat sie als Sonderregel für das Malnehmen gelernt.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-(a * (b + 4)))), (":", Z(-(b + 4)))))
    if st == 2:
        return bau(kette(Kl(Z(-(a * b * c))), (":", Z(-b)), (":", Z(c))))
    return bau(kette(Kl(Z(-(a * b * c * 2))), (":", Z(-b)), ("·", Z(c)),
                     (":", Z(2))))


BF5_7 = BF("BF7", "Division zweier negativer Zahlen", BEREICH, bf5_7)


def bf5_8(p):
    """Mal und Geteilt gemischt:  6 · 8 : 4             (Lektion 1.17)

    Beide sind Punktoperationen, also gilt keine Vorfahrt — es wird von
    LINKS nach rechts gerechnet. Wer zuerst das Geteilt nimmt, bekommt bei
    `36 : 6 : 2` ein anderes Ergebnis; dieser Fehler steht als
    `punkt_von_rechts` in jeder Aufgabe dieser Bauform.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * b), ("·", Z(c)), (":", Z(b))))
    if st == 2:
        return bau(kette(Z(a * b * c), (":", Z(c)), ("·", Z(-b))))
    return bau(kette(Z(a * b * c * 2), (":", Z(-c)), ("·", Z(b)),
                     (":", Z(2))))


BF5_8 = BF("BF8", "Mal und Geteilt gemischt", BEREICH, bf5_8)


def bf5_9(p):
    """Sonderfall: ein Faktor ist null:  5 + (−7) · 0

    Null mal irgendetwas ist null, ganz gleich wie viele Minuszeichen
    dastehen. Die Null steht hier absichtlich MITTEN in einer längeren
    Rechnung: wer von links nach rechts rechnet, multipliziert die 5 mit
    hinein und bekommt null heraus. Dieser Fehler — `von_links` — ist der
    Grund für die Bauform.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(b + 4), ("+", Kl(Z(-a))), ("·", Z(0))))
    if st == 2:
        return bau(kette(Z(b + 4), ("+", Kl(Z(-a))), ("·", Z(0)),
                         ("−", Z(c))))
    return bau(kette(Z(b + 4), ("+", Kl(Z(-a))), ("·", Z(0)),
                     ("·", Z(-c)), ("+", Z(p["d"]))))


BF5_9 = BF("BF9", "Sonderfall: ein Faktor ist null", BEREICH, bf5_9,
           filter=SONDER)


def bf5_10(p):
    """Sonderfall: der Faktor ist eins oder minus eins:  (−1) · 9

    Mal eins ändert nichts, mal minus eins dreht nur das Vorzeichen. Wer
    das nicht sieht, rechnet — und wer `(−1) · 9` für −1 hält, hat den
    Faktor mit dem Ergebnis verwechselt.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-1)), ("·", Z(a * b))))
    if st == 2:
        #: Nicht `(−1) · n · (−1)` — dort fallen «letztes Glied vergessen»
        #: und «erstes Glied vergessen» auf denselben Wert, und es bleiben
        #: vier Katalogeinträge.
        return bau(kette(Z(a * b), ("·", Kl(Z(-1))), ("·", Z(-c))))
    return bau(kette(Kl(Z(-1)), ("·", Z(a * b)), ("·", Z(-1)),
                     ("·", Z(-c))))


BF5_10 = BF("BF10", "Sonderfall: der Faktor ist eins oder minus eins",
            BEREICH, bf5_10)


def bf5_11(p):
    """Drei Vorzeichen im Produkt:  (−2) · (−3) · (−4)   (Lektion 1.12)

    DIE Probe auf die Zählregel. Bei zwei Minuszeichen kommt man mit
    «heben sich auf» durch, bei dreien nicht mehr: das Ergebnis ist
    negativ. Wer hier positiv rechnet, hat paarweise weggestrichen und das
    übrig gebliebene Minus vergessen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("·", Z(-b)), ("·", Z(-c))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("·", Z(-b)), ("·", Z(-c)),
                         ("·", Z(2))))
    return bau(kette(Kl(Z(-(a * b * c))), (":", Z(-b)), ("·", Z(-c)),
                     (":", Z(-1))))


BF5_11 = BF("BF11", "Drei Vorzeichen im Produkt", BEREICH, bf5_11)


def bf5_12(p):
    """Punkt und Strich nebeneinander:  5 + 3 · (−4)     (Lektion 1.16)

    Die Sammelform von S5 und zugleich der Übergang zu S6: das Malnehmen
    kommt zuerst, auch wenn es hinten steht. Wer von links rechnet,
    addiert erst und multipliziert dann alles.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(-b))))
    if st == 2:
        return bau(kette(Z(a + b), ("−", Z(c)), ("·", Z(-b)),
                         ("+", Z(-a))))
    return bau(kette(Z(a * b), (":", Z(-b)), ("+", Z(c)), ("·", Z(-2))))


BF5_12 = BF("BF12", "Punkt und Strich nebeneinander", BEREICH, bf5_12)


S5 = Schablone(
    nr="S5", titel="Multiplizieren und Dividieren",
    lektionen="1.10 – 1.15", erhebung="", anleitung=ANLEITUNG,
    levelachse="Anzahl Faktoren und Anzahl Vorzeichen",
    bauformen=[BF5_1, BF5_2, BF5_3, BF5_4, BF5_5, BF5_6,
               BF5_7, BF5_8, BF5_9, BF5_10, BF5_11, BF5_12],
    kernidee="Zähl die Minuszeichen: bei einer geraden Anzahl ist das "
             "Produkt positiv, bei einer ungeraden negativ. Für das Teilen "
             "gilt dieselbe Regel wie für das Malnehmen.")


# ══════════════════════════════════════════════════════════════════════════
# S6 · Die Reihenfolge der Operationen      (1.16 – 1.19)
# ══════════════════════════════════════════════════════════════════════════
#
# Zwei Regeln, die verwechselt werden:
#
#     Punkt vor Strich      sagt, WELCHE Operation zuerst kommt
#     von links nach rechts sagt, in welcher REIHENFOLGE gleichrangige
#                           Operationen drankommen
#
# `5 + 3 · 4` als 32 zu rechnen ist ein Verstoss gegen die erste Regel,
# `36 : 6 : 2` als 12 einer gegen die zweite. Die beiden Fehler stehen
# darum getrennt im Katalog — `von_links` und `punkt_von_rechts` — und
# führen zu verschiedenen Rückmeldungen.

def bf6_1(p):
    """Punkt vor Strich, der Punkt steht hinten:  5 + 3 · 4  (Lektion 1.16)

    Der Klassiker. Wer von links rechnet, addiert zuerst und multipliziert
    dann die Summe — das gibt ein viel zu grosses Ergebnis.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(b))))
    if st == 2:
        return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(b)), ("−", Z(a))))
    return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(b)), ("−", Z(a)),
                     ("·", Z(2))))


BF6_1 = BF("BF1", "Punkt vor Strich, der Punkt steht hinten", BEREICH, bf6_1)


def bf6_2(p):
    """Punkt vor Strich, der Punkt steht vorne:  3 · 4 + 5  (Lektion 1.16)

    Hier führt das Rechnen von links zufällig zum richtigen Ergebnis —
    und genau darum steht die Bauform hier. Wer nur diese Form übt, merkt
    nie, dass er die Regel gar nicht anwendet.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("·", Z(b)), ("+", Z(c + 4))))
    if st == 2:
        return bau(kette(Z(a), ("·", Z(b)), ("+", Z(c + 4)), ("−", Z(b))))
    return bau(kette(Z(a), ("·", Z(b)), ("+", Z(c + 4)), ("−", Z(b)),
                     ("+", Z(-c))))


BF6_2 = BF("BF2", "Punkt vor Strich, der Punkt steht vorne", BEREICH, bf6_2)


def bf6_3(p):
    """Punkt vor Strich mit negativem Faktor:  5 + 3 · (−4)  (Lektion 1.16)

    Beide Regeln des Kapitels auf einmal: erst die Vorzeichenregel für das
    Produkt, dann Punkt vor Strich. Das Ergebnis ist kleiner als die erste
    Zahl, obwohl ein Pluszeichen dasteht.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(-b))))
    if st == 2:
        return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(-b)), ("−", Z(-a))))
    return bau(kette(Z(a + b), ("+", Z(c)), ("·", Z(-b)), ("−", Z(-a)),
                     ("·", Z(-2))))


BF6_3 = BF("BF3", "Punkt vor Strich mit negativem Faktor", BEREICH, bf6_3)


def bf6_4(p):
    """Mehrere Punktoperationen:  36 : 6 : 2            (Lektion 1.17)

    Hier gilt nicht «Punkt vor Strich», sondern «von links nach rechts».
    `36 : 6 : 2` ist 3. Wer hinten anfängt, rechnet 6 : 2 = 3 und dann
    36 : 3 = 12 — dieser Fehler steht als `punkt_von_rechts` in jeder
    Aufgabe dieser Bauform.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * b * c), (":", Z(b)), (":", Z(c))))
    if st == 2:
        return bau(kette(Z(a * b * c * 2), (":", Z(b)), (":", Z(c)),
                         (":", Z(2))))
    return bau(kette(Z(a * b * c * 2), (":", Z(b)), ("·", Z(c)),
                     (":", Z(-c)), (":", Z(2))))


BF6_4 = BF("BF4", "Mehrere Punktoperationen", BEREICH, bf6_4)


def bf6_5(p):
    """Mehrere Strichoperationen:  12 − 5 + 3          (Lektion 1.18)

    Dieselbe Regel wie bei BF4, nur mit Plus und Minus. `12 − 5 + 3` ist
    10, nicht 4 — wer die 5 + 3 zuerst zusammenzieht, hat das Minus nur
    auf die 5 bezogen, obwohl es davorsteht.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b + c), ("−", Z(b)), ("+", Z(c))))
    if st == 2:
        return bau(kette(Z(a + b + c), ("−", Z(b)), ("+", Z(c)),
                         ("−", Z(a))))
    return bau(kette(Z(a + b + c), ("−", Z(b)), ("+", Z(-c)),
                     ("−", Z(a)), ("+", Z(b + c))))


BF6_5 = BF("BF5", "Mehrere Strichoperationen", BEREICH, bf6_5)


def bf6_6(p):
    """Division und Subtraktion:  18 : 3 − 7           (Lektion 1.19)

    Die beiden Operationen, die am ehesten in die falsche Reihenfolge
    geraten: das Teilen sieht nach «Rest» aus, das Minus nach «zuerst».
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * b), (":", Z(b)), ("−", Z(c + 4))))
    if st == 2:
        return bau(kette(Z(a * b), (":", Z(b)), ("−", Z(c + 4)),
                         ("+", Z(-b))))
    return bau(kette(Z(a * b * c), (":", Z(-b)), ("−", Z(c + 4)),
                     ("+", Z(-b)), ("−", Z(-a))))


BF6_6 = BF("BF6", "Division und Subtraktion", BEREICH, bf6_6)


def bf6_7(p):
    """Zwei Punktgruppen:  3 · 4 − 6 : 2               (Lektion 1.19)

    Beide Punktgruppen werden zuerst gerechnet, jede für sich, und erst
    danach voneinander abgezogen. Wer von links durchgeht, zieht die 6 vom
    Produkt ab und teilt am Schluss alles durch 2.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("·", Z(b)), ("−", Z(c * 2)), (":", Z(2))))
    if st == 2:
        return bau(kette(Z(a), ("·", Z(-b)), ("−", Z(c * 2)), (":", Z(2))))
    return bau(kette(Z(a), ("·", Z(-b)), ("−", Z(c * 4)), (":", Z(-2)),
                     ("+", Z(-b))))


BF6_7 = BF("BF7", "Zwei Punktgruppen", BEREICH, bf6_7)


def bf6_8(p):
    """Alle vier Operationen in einer Aufgabe:  20 − 3 · 4 + 8 : 2

    Die Sammelform. Nichts Neues, aber man muss die Aufgabe erst
    sortieren, bevor man rechnet: zuerst die beiden Punktgruppen, dann von
    links durch die Striche.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * b), ("−", Z(c)), ("·", Z(b)),
                         ("+", Z(a * 2)), (":", Z(2))))
    if st == 2:
        return bau(kette(Z(a * b), ("−", Z(c)), ("·", Z(-b)),
                         ("+", Z(a * 2)), (":", Z(2))))
    return bau(kette(Z(a * b), ("−", Z(c)), ("·", Z(-b)),
                     ("+", Z(a * 4)), (":", Z(-2)), ("−", Z(-c))))


BF6_8 = BF("BF8", "Alle vier Operationen in einer Aufgabe", BEREICH, bf6_8)


def bf6_9(p):
    """Sonderfall: das Ergebnis ist null:  3 · 4 − 12

    Das Produkt und die Zahl dahinter heben sich genau auf. Wer von links
    rechnet, bekommt hier etwas ganz anderes heraus — und wer die Null
    für einen Rechenfehler hält, rechnet sie so lange nach, bis sie falsch
    wird.

    Wie bei allen Null-Sonderfällen drei bis vier Katalogeinträge statt
    fünf: bei der Lösung null fallen die ±-Paare zusammen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("·", Z(b)), ("−", Z(a * b))))
    if st == 2:
        return bau(kette(Z(a), ("·", Z(b)), ("−", Z(a * b)), ("+", Z(c)),
                         ("−", Z(c))))
    return bau(kette(Z(a * b * 2), (":", Z(-b)), ("+", Z(a * 2)),
                     ("·", Z(1))))


BF6_9 = BF("BF9", "Sonderfall: das Ergebnis ist null", BEREICH, bf6_9,
           filter=SONDER)


def bf6_10(p):
    """Sonderfall: das Ergebnis wird negativ:  4 − 3 · 5

    Vorne steht eine positive Zahl, und trotzdem ist das Ergebnis negativ:
    das Produkt dahinter ist grösser. Wer meint, ein Ergebnis könne nicht
    kleiner als null werden, wenn die Aufgabe mit einer positiven Zahl
    beginnt, rechnet hier so lange, bis etwas Positives dasteht.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("−", Z(b)), ("·", Z(c + 4))))
    if st == 2:
        return bau(kette(Z(a), ("−", Z(b)), ("·", Z(c + 4)), ("+", Z(c))))
    return bau(kette(Z(a), ("−", Z(b)), ("·", Z(c + 4)), ("+", Z(c)),
                     ("·", Z(2))))


BF6_10 = BF("BF10", "Sonderfall: das Ergebnis wird negativ", BEREICH, bf6_10)


def bf6_11(p):
    """Negative Zahlen in beiden Punktgruppen:  (−4) · 3 − (−6) : 2

    Beide Regeln des Kapitels auf einmal, und in jeder Punktgruppe steckt
    ein Vorzeichen. Erst die Gruppen ausrechnen, dann von links durch die
    Striche — und bei jedem Schritt die Minuszeichen zählen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("·", Z(b)), ("−", Z(c * 2)),
                         (":", Z(2))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("·", Z(b)), ("−", Z(-(c * 2))),
                         (":", Z(2))))
    return bau(kette(Kl(Z(-a)), ("·", Z(-b)), ("−", Z(-(c * 4))),
                     (":", Z(-2)), ("+", Z(-b))))


BF6_11 = BF("BF11", "Negative Zahlen in beiden Punktgruppen", BEREICH,
            bf6_11)


def bf6_12(p):
    """Die längste Kette:  24 : (−4) + 3 · (−2) − 5

    Fünf Glieder, beide Regeln, beide Vorzeichenfälle. Wer bis hierher
    kommt, hat Kapitel 1 hinter sich.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a * b), (":", Z(-b)), ("+", Z(c)), ("·", Z(2))))
    if st == 2:
        return bau(kette(Z(a * b), (":", Z(-b)), ("+", Z(c)), ("·", Z(-2)),
                         ("−", Z(a))))
    return bau(kette(Z(a * b * 2), (":", Z(-b)), ("+", Z(c)), ("·", Z(-2)),
                     ("−", Z(-a)), ("+", Z(-c))))


BF6_12 = BF("BF12", "Die längste Kette", BEREICH, bf6_12)


S6 = Schablone(
    nr="S6", titel="Die Reihenfolge der Operationen",
    lektionen="1.16 – 1.19", erhebung="", anleitung=ANLEITUNG,
    levelachse="Anzahl Operationen und Anzahl Vorzeichen",
    bauformen=[BF6_1, BF6_2, BF6_3, BF6_4, BF6_5, BF6_6,
               BF6_7, BF6_8, BF6_9, BF6_10, BF6_11, BF6_12],
    kernidee="Zwei Regeln, und sie sagen Verschiedenes: «Punkt vor Strich» "
             "sagt, WELCHE Operation zuerst kommt, «von links nach rechts» "
             "sagt, in welcher Reihenfolge gleichrangige drankommen. "
             "36 : 6 : 2 ist 3, nicht 12.")
