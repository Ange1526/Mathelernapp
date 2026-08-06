# -*- coding: utf-8 -*-
"""
S1 · Vorzeichen und Zahlengerade          (Lektionen 1.1 – 1.4)
S3 · Addieren und Subtrahieren            (Lektionen 1.5 – 1.9)

    «Rechne aus.»
    −(−7) + 3      5 + (−3)      8 − (−3)      (−5) + (−4)

KAPITEL 1 HAT KEINE SCHABLONE. Die Bauformen sind aus den Lektionstiteln
in `netz_daten.py` entwickelt; jede Lektion des Kapitels kommt in mindestens
einer Bauform vor. Was der Titel als VERSTEHEN formuliert («positive und
negative Zahlen verstehen»), steht hier als Rechnung — die Studie erlaubt
nur «rechne aus», und ein Verständnis, das sich nicht rechnen lässt, kann
die App ohnehin nicht prüfen.

DIE NUMMERN S1 UND S3 statt S1 und S2: S2 und S4 gehören den abgelösten
Altgeneratoren `s2_grundoperationen.py` und `s4_faktorisieren.py`. Zwei
Schablonen mit derselben Nummer würden die Mastery-Zeilen vermischen —
wer früher das alte S2 geübt hat, hätte hier ohne eigenes Zutun Häkchen.

WORUM ES IN S1 GEHT: um den Unterschied zwischen VORZEICHEN und
OPERATIONSZEICHEN (Lektion 1.3). In `8 − (−3)` stehen zwei Minus mit ganz
verschiedenen Aufgaben — das eine sagt «subtrahiere», das andere gehört zur
Zahl. Der Baustein `VZ` hält die beiden auseinander, siehe
`k1_bausteine.py`.

LEVELACHSE — strukturell, in beiden Schablonen die Anzahl der Glieder und
die Anzahl der Vorzeichen:

    A   zwei Glieder, ein Vorzeichen
    B   drei Glieder oder ein zweites Vorzeichen
    C   drei bis vier Glieder mit gemischten Vorzeichen

Die Zahlenvorräte sind auf allen drei Stufen dieselben. Was A von C trennt,
ist die Zahl der Zeichen, nicht die Grösse der Zahlen.
"""
from __future__ import annotations

from .k1_bausteine import (ANLEITUNG, BF, F, K, Kl, SONDER, STANDARD, VZ, Z,
                           bau, kette, rechne)
from .schablone import Schablone


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"a": [3, 5, 7, 9], "b": [2, 4, 6, 8], "c": [3, 4, 5, 7],
            "d": [2, 3, 5, 6], "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


# ══════════════════════════════════════════════════════════════════════════
# S1 · Vorzeichen und Zahlengerade          (1.1 – 1.4)
# ══════════════════════════════════════════════════════════════════════════

def bf1_1(p):
    """Die Gegenzahl der Gegenzahl:  −(−7) + 3        (Lektion 1.1)

    Zwei Minus, die nichts miteinander zu tun haben: das äussere ist ein
    Vorzeichen, das innere gehört zur Zahl. Zusammen ergeben sie ein Plus.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = VZ("−", Z(-a))
    if st == 1:
        return bau(kette(erst, ("+", Z(b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(b)), ("−", Z(c))))
    return bau(kette(erst, ("+", Z(b)), ("−", Z(-c)), ("+", Z(p["d"]))))


BF1_1 = BF("BF1", "Die Gegenzahl der Gegenzahl", BEREICH, bf1_1)


def bf1_2(p):
    """Ein Plus als Vorzeichen:  +(−4) − 5            (Lektion 1.3)

    Das Pluszeichen ändert nichts — und genau das muss man einmal gesehen
    haben, sonst wird es für ein Additionszeichen gehalten.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = VZ("+", Z(-a))
    if st == 1:
        return bau(kette(erst, ("−", Z(b))))
    if st == 2:
        return bau(kette(erst, ("−", Z(b)), ("+", Z(c))))
    return bau(kette(erst, ("−", Z(-b)), ("+", Z(c)), ("−", Z(p["d"]))))


BF1_2 = BF("BF2", "Ein Plus als Vorzeichen", BEREICH, bf1_2)


def bf1_3(p):
    """Ein Minus vor einer positiven Zahl:  −(+9) + 12   (Lektion 1.3)

    Der Gegenfall zu BF2: hier steht das Vorzeichen der Zahl ausgeschrieben,
    und davor ein zweites. Wer beide für Operationszeichen hält, sucht
    vergeblich, wovon er abziehen soll.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = VZ("−", Z(a, mit_plus=True))
    if st == 1:
        return bau(kette(erst, ("+", Z(a + b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(a + b)), ("−", Z(c))))
    return bau(kette(erst, ("+", Z(a + b)), ("−", Z(-c)), ("−", Z(p["d"]))))


BF1_3 = BF("BF3", "Ein Minus vor einer positiven Zahl", BEREICH, bf1_3)


def bf1_4(p):
    """Drei Vorzeichen hintereinander:  −(−(−5)) + 3     (Lektion 1.1)

    Der Zähltest: bei einer UNGERADEN Zahl von Minuszeichen bleibt es
    negativ. Wer die Zeichen paarweise wegstreicht, statt sie zu zählen,
    verliert hier den Überblick — darum eine eigene Bauform.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = VZ("−", VZ("−", Z(-a)))
    if st == 1:
        return bau(kette(erst, ("+", Z(a + b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(a + b)), ("−", Z(c))))
    return bau(kette(erst, ("+", Z(a + b)), ("−", Z(-c)), ("+", Z(p["d"]))))


BF1_4 = BF("BF4", "Drei Vorzeichen hintereinander", BEREICH, bf1_4)


def bf1_5(p):
    """Auf der Zahlengeraden nach rechts:  −6 + 2        (Lektion 1.2)

    Start links von der Null, alle Schritte nach rechts. Wer die
    Zahlengerade vor Augen hat, sieht sofort, ob er die Null überquert.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = Z(-(a + b))
    if st == 1:
        return bau(kette(erst, ("+", Z(b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(b)), ("+", Z(c))))
    return bau(kette(erst, ("+", Z(b)), ("+", Z(c)), ("+", Z(a + p["d"]))))


BF1_5 = BF("BF5", "Auf der Zahlengeraden nach rechts", BEREICH, bf1_5)


def bf1_6(p):
    """Auf der Zahlengeraden nach links:  4 − 9          (Lektion 1.2)

    Start rechts von der Null, alle Schritte nach links, und unterwegs wird
    die Null überquert. Das ist die Stelle, an der «die kleinere von der
    grösseren» abziehen zum ersten Mal nicht mehr funktioniert.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = Z(a)
    if st == 1:
        return bau(kette(erst, ("−", Z(a + b))))
    if st == 2:
        return bau(kette(erst, ("−", Z(b)), ("−", Z(a + c))))
    return bau(kette(erst, ("−", Z(b)), ("−", Z(a + c)), ("−", Z(p["d"]))))


BF1_6 = BF("BF6", "Auf der Zahlengeraden nach links", BEREICH, bf1_6)


def bf1_7(p):
    """Operationszeichen und Vorzeichen nebeneinander:  5 + (−3)  (Lektion 1.4)

    Das erste Zeichen sagt, was zu tun ist; das zweite gehört zur Zahl.
    Beide stehen hier direkt nebeneinander — das ist der Unterschied
    zwischen Strichoperator und Vorzeichen, und er ist der ganze Inhalt
    von 1.3 und 1.4.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = Z(a + b)
    if st == 1:
        return bau(kette(erst, ("+", Z(-b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(-b)), ("−", Z(-c))))
    return bau(kette(erst, ("+", Z(-b)), ("−", Z(-c)), ("+", Z(-p["d"]))))


BF1_7 = BF("BF7", "Operationszeichen und Vorzeichen nebeneinander",
           BEREICH, bf1_7)


def bf1_8(p):
    """Ein Punktoperator zwischen Strichoperatoren:  4 + 2 · 3  (Lektion 1.4)

    Lektion 1.4 heisst «Strich- und Punktoperatoren erkennen». Erkennen
    heisst hier: sehen, dass der Punktoperator zuerst dran ist. Die Faktoren
    bleiben klein — gerechnet wird das Malnehmen erst ab 1.10, hier geht es
    nur darum, den Operator auseinanderzuhalten.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = Z(a + b)
    if st == 1:
        return bau(kette(erst, ("+", Z(2)), ("·", Z(3))))
    if st == 2:
        return bau(kette(erst, ("−", Z(2)), ("·", Z(c))))
    return bau(kette(erst, ("−", Z(2)), ("·", Z(c)), ("+", Z(-p["d"]))))


BF1_8 = BF("BF8", "Ein Punktoperator zwischen Strichoperatoren",
           BEREICH, bf1_8)


def bf1_9(p):
    """Sonderfall: das Ergebnis ist null:  −7 + 7

    Eine Zahl und ihre Gegenzahl heben sich auf. Wer das nicht kennt,
    hält die Null für ein Zeichen, dass er sich verrechnet hat, und sucht
    weiter.

    Der Fehlerkatalog hat hier nur drei Einträge statt fünf, und das ist
    kein Versehen: bei der Lösung null fallen `vorzeichen_gesamt` und die
    ±-Paare alle auf denselben Wert. Drei echte sind mehr wert als fünf
    ausgedachte.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = Z(-(a + b))
    if st == 1:
        return bau(kette(erst, ("+", Z(a + b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(a)), ("+", Z(b))))
    return bau(kette(Z(-(a + b + c)), ("+", Z(a)), ("−", Z(-b)),
                     ("+", Z(c))))


BF1_9 = BF("BF9", "Sonderfall: das Ergebnis ist null", BEREICH, bf1_9,
           filter=SONDER)


def bf1_10(p):
    """Sonderfall: die Null ändert nichts:  −8 + 0

    Die Null ist das neutrale Element der Addition. Wer sie für «nichts»
    hält, streicht sie samt der Zahl davor weg. Und wer `0 − 7` sieht,
    muss wissen, dass links von der Null die negativen Zahlen liegen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    #: Auf jeder Stufe mindestens drei Glieder. Mit nur `−8 + 0` bleiben
    #: nach dem Sieben zwei Fehlerwerte übrig — zu wenig, um dem Schüler
    #: etwas zu sagen.
    if st == 1:
        return bau(kette(Z(0), ("−", Z(a + b)), ("+", Z(c))))
    if st == 2:
        return bau(kette(Z(-(a + b)), ("+", Z(0)), ("+", Z(c))))
    return bau(kette(Z(0), ("−", Z(a + b)), ("+", Z(0)), ("−", Z(-c))))


BF1_10 = BF("BF10", "Sonderfall: die Null ändert nichts", BEREICH, bf1_10,
            filter=SONDER)


def bf1_11(p):
    """Ein Vorzeichen vor einer ganzen Rechnung:  −(3 − 8)

    Hier steht das Vorzeichen nicht vor einer Zahl, sondern vor allem, was
    in der Klammer herauskommt. Das ist der Übergang zu Kapitel 10 und
    zugleich die Probe darauf, ob «Vorzeichen» wirklich verstanden ist:
    zuerst die Klammer, dann das Zeichen davor.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    innen = kette(Z(a), ("−", Z(a + b)))
    if st == 1:
        return bau(kette(VZ("−", innen), ("+", Z(c))))
    if st == 2:
        return bau(kette(VZ("−", innen), ("+", Z(c)), ("−", Z(p["d"]))))
    innen3 = kette(Z(a), ("−", Z(a + b)), ("+", Z(c)))
    return bau(kette(VZ("−", innen3), ("−", Z(-p["d"]))))


BF1_11 = BF("BF11", "Ein Vorzeichen vor einer ganzen Rechnung",
            BEREICH, bf1_11)


def bf1_12(p):
    """Alles zusammen: Vorzeichen, Gegenzahl und Strichoperatoren

    Die Sammelform von S1. Sie stellt nichts Neues, sondern verlangt, dass
    man die Zeichen im selben Term auseinanderhält — genau das, was Lektion
    1.3 und 1.4 verlangen und was in den Bauformen davor je einzeln geübt
    wurde.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    erst = VZ("−", Z(-a))
    if st == 1:
        return bau(kette(erst, ("+", Z(-b))))
    if st == 2:
        return bau(kette(erst, ("+", Z(-b)), ("−", Z(-c))))
    return bau(kette(erst, ("+", Z(-b)), ("−", Z(-c)),
                     ("+", Z(p["d"], mit_plus=True))))


BF1_12 = BF("BF12", "Alles zusammen: Vorzeichen und Strichoperatoren",
            BEREICH, bf1_12)


S1 = Schablone(
    nr="S1", titel="Vorzeichen und Zahlengerade",
    lektionen="1.1 – 1.4", erhebung="", anleitung=ANLEITUNG,
    levelachse="Anzahl Glieder und Anzahl Vorzeichen",
    bauformen=[BF1_1, BF1_2, BF1_3, BF1_4, BF1_5, BF1_6,
               BF1_7, BF1_8, BF1_9, BF1_10, BF1_11, BF1_12],
    kernidee="Ein Vorzeichen gehört zu SEINER Zahl, ein Operationszeichen "
             "steht zwischen zwei Zahlen. Zwei Minus hintereinander ergeben "
             "ein Plus — zähl sie, statt sie wegzustreichen.")


# ══════════════════════════════════════════════════════════════════════════
# S3 · Addieren und Subtrahieren            (1.5 – 1.9)
# ══════════════════════════════════════════════════════════════════════════
#
# Die fünf Lektionen sind fünf Vorzeichenfälle, und jeder hat seine eigene
# Bauform. Sie in eine einzige «Addition» zusammenzuwerfen wäre bequem und
# genau falsch: der Schüler, der `(−5) + (−3)` nicht kann, kann `5 + 3`
# meistens sehr wohl. Nur getrennte Bauformen bekommen getrennte Häkchen —
# und nur so sieht die Einstufung, wo es wirklich fehlt.

def bf3_1(p):
    """Addition mit positiven Zahlen:  7 + 5              (Lektion 1.5)"""
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("+", Z(b + c))))
    if st == 2:
        return bau(kette(Z(a + b), ("+", Z(b + c)), ("+", Z(a + c))))
    return bau(kette(Z(a + b), ("+", Z(b + c)), ("+", Z(a + c)),
                     ("+", Z(p["d"] + a))))


BF3_1 = BF("BF1", "Addition mit positiven Zahlen", BEREICH, bf3_1)


def bf3_2(p):
    """Subtraktion, das Ergebnis bleibt positiv:  9 − 4    (Lektion 1.6)

    Der vertraute Fall aus der Primarschule. Er steht hier, damit die
    schwierigen Fälle einen Vergleich haben — und damit ein Schüler, der
    ganz unten einsteigt, mit etwas beginnt, das er kann.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b + c), ("−", Z(b))))
    if st == 2:
        return bau(kette(Z(a + b + c + p["d"]), ("−", Z(b)), ("−", Z(c))))
    return bau(kette(Z(a + b + c + p["d"] + 4), ("−", Z(b)), ("−", Z(c)),
                     ("−", Z(p["d"]))))


BF3_2 = BF("BF2", "Subtraktion, das Ergebnis bleibt positiv", BEREICH, bf3_2)


def bf3_3(p):
    """Subtraktion über die Null hinaus:  4 − 9           (Lektion 1.6)

    Hier hört die Primarschulregel «die kleinere von der grösseren» auf zu
    funktionieren. Wer sie trotzdem anwendet, schreibt 5 statt −5 — dieser
    Fehler steht in jeder Aufgabe dieser Bauform im Katalog.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a), ("−", Z(a + b))))
    if st == 2:
        return bau(kette(Z(a), ("−", Z(b)), ("−", Z(a + c))))
    return bau(kette(Z(a), ("−", Z(b)), ("+", Z(c)), ("−", Z(a + c + 2))))


BF3_3 = BF("BF3", "Subtraktion über die Null hinaus", BEREICH, bf3_3)


def bf3_4(p):
    """Positiv plus negativ:  6 + (−4)                    (Lektion 1.7)

    Plus und Minus stehen direkt nebeneinander. Zusammen heissen sie
    «abziehen» — aber nur, weil das eine ein Operationszeichen und das
    andere ein Vorzeichen ist.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("+", Z(-b))))
    if st == 2:
        return bau(kette(Z(a + b), ("+", Z(-b)), ("+", Z(-c))))
    #: Nicht `("+", Z(-a - c))` — dann hebt sich alles auf und die Lösung
    #: wäre immer null. Das ist BF9, nicht BF4.
    return bau(kette(Z(a + b), ("+", Z(-b)), ("+", Z(c)), ("+", Z(-a))))


BF3_4 = BF("BF4", "Positiv plus negativ", BEREICH, bf3_4)


def bf3_5(p):
    """Negativ plus positiv:  −6 + 4                      (Lektion 1.7)

    Der Gegenfall zu BF4. Er ist der schwierigere von beiden, weil die
    grössere Zahl hinten steht und das Ergebnis trotzdem negativ bleiben
    kann.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-(a + b))), ("+", Z(b))))
    if st == 2:
        return bau(kette(Kl(Z(-(a + b))), ("+", Z(b)), ("+", Z(c))))
    return bau(kette(Kl(Z(-(a + b))), ("+", Z(b)), ("+", Z(-c)),
                     ("+", Z(a))))


BF3_5 = BF("BF5", "Negativ plus positiv", BEREICH, bf3_5)


def bf3_6(p):
    """Zwei negative Zahlen addieren:  (−5) + (−3)        (Lektion 1.8)

    Beide Schritte gehen nach links, das Ergebnis ist weiter von der Null
    weg als beide Summanden. Wer hier die Beträge subtrahiert statt
    addiert, hat die Zahlengerade nicht vor Augen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    #: Auch auf A drei Glieder. Bei nur zweien fallen `zeichen_verwechselt`
    #: und `doppeltes_minus` auf denselben Wert, und es bleiben vier
    #: Katalogeinträge statt fünf.
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("+", Z(-b)), ("+", Z(-c))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("+", Z(-b)), ("+", Z(-c)),
                         ("+", Z(-p["d"]))))
    return bau(kette(Kl(Z(-a)), ("+", Z(-b)), ("+", Z(c)),
                     ("+", Z(-p["d"]))))


BF3_6 = BF("BF6", "Zwei negative Zahlen addieren", BEREICH, bf3_6)


def bf3_7(p):
    """Eine negative Zahl abziehen:  7 − (−3)             (Lektion 1.9)

    Die schwierigste Stelle des Kapitels. Minus und Minus ergeben zusammen
    ein Plus, und das Ergebnis wird GRÖSSER als die Zahl, von der man
    abzieht. Wer `7 − (−3)` als `7 − 3` liest, sieht nur eines der beiden
    Zeichen — dieser Fehler steht in jeder Aufgabe dieser Bauform.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("−", Z(-b))))
    if st == 2:
        return bau(kette(Z(a + b), ("−", Z(-b)), ("−", Z(c))))
    return bau(kette(Z(a + b), ("−", Z(-b)), ("+", Z(-c)), ("−", Z(-p["d"]))))


#: Vier Katalogeinträge auf Level A, und das ist kein Versehen: steht in
#: der Aufgabe genau EIN `− (−n)`, dann führen «Vorzeichen übersehen»,
#: «doppeltes Minus nicht gedreht» und «Minus als Plus gelesen» alle auf
#: denselben Wert. Mehr unterscheidbare Antworten gibt es dort nicht. Der
#: entscheidende Fehler — `7 − (−3)` als `7 − 3` — ist mit eigener
#: Rückmeldung dabei.
BF3_7 = BF("BF7", "Eine negative Zahl abziehen", BEREICH, bf3_7,
           filter=SONDER)


def bf3_8(p):
    """Negativ minus negativ:  −7 − (−3)                  (Lektion 1.9)

    Drei Minuszeichen in einem Term, jedes mit einer anderen Aufgabe: das
    erste gehört zur 7, das zweite sagt «abziehen», das dritte gehört zur 3.
    Wer sie zählt statt zu raten, kommt durch.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-(a + b))), ("−", Z(-b))))
    if st == 2:
        return bau(kette(Kl(Z(-(a + b))), ("−", Z(-b)), ("−", Z(c))))
    return bau(kette(Kl(Z(-(a + b))), ("−", Z(-b)), ("+", Z(-c)),
                     ("−", Z(-p["d"]))))


BF3_8 = BF("BF8", "Negativ minus negativ", BEREICH, bf3_8)


def bf3_9(p):
    """Sonderfall: Zahl und Gegenzahl heben sich auf:  8 − (−(−8))

    Hier hilft kein Rechenweg, sondern nur das Hinsehen: was übrig bleibt,
    ist null. Wie bei S1/BF9 hat der Katalog drei bis vier Einträge statt
    fünf — bei der Lösung null fallen die ±-Paare zusammen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b), ("−", Z(a + b))))
    if st == 2:
        return bau(kette(Z(a + b), ("+", Z(-b)), ("−", Z(a))))
    return bau(kette(Kl(Z(-(a + b))), ("−", Z(-b)), ("+", Z(c)),
                     ("+", Z(a - c))))


BF3_9 = BF("BF9", "Sonderfall: Zahl und Gegenzahl heben sich auf",
           BEREICH, bf3_9, filter=SONDER)


def bf3_10(p):
    """Sonderfall: Abziehen macht grösser:  −4 − (−9)     (Lektion 1.9)

    Das Ergebnis ist grösser als beide Zahlen, obwohl subtrahiert wird.
    Wer «minus macht kleiner» als Regel gelernt hat, hält das Ergebnis für
    falsch und rechnet noch einmal. Darum eine eigene Bauform: die Regel
    stimmt nur für positive Zahlen.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("−", Z(-(a + b)))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("−", Z(-(a + b))), ("−", Z(c))))
    return bau(kette(Kl(Z(-a)), ("−", Z(-(a + b))), ("+", Z(-c)),
                     ("−", Z(-p["d"]))))


BF3_10 = BF("BF10", "Sonderfall: Abziehen macht grösser", BEREICH, bf3_10)


def bf3_11(p):
    """Alle Vorzeichenfälle in einer Aufgabe:  (−6) + 9 − (−2)

    Die Sammelform von S3. Nichts Neues, aber die Fälle stehen nicht mehr
    angekündigt nebeneinander — man muss bei jedem Schritt neu hinsehen,
    welcher es ist.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Kl(Z(-a)), ("+", Z(a + b))))
    if st == 2:
        return bau(kette(Kl(Z(-a)), ("+", Z(a + b)), ("−", Z(-c))))
    return bau(kette(Kl(Z(-a)), ("+", Z(a + b)), ("−", Z(-c)),
                     ("+", Z(-p["d"]))))


BF3_11 = BF("BF11", "Alle Vorzeichenfälle in einer Aufgabe", BEREICH, bf3_11)


def bf3_12(p):
    """Sonderfall: die Zahl bleibt, wie sie war:  12 + 8 − 8

    Zwei Glieder heben sich auf, das dritte bleibt stehen. Wer stur von
    links rechnet, kommt auch hin — der Sinn der Bauform ist, dass man das
    Aufheben SIEHT und sich die Rechnung spart. Das ist dieselbe Bewegung,
    die in Kapitel 4 «gleichartige Glieder zusammenfassen» heisst.
    """
    st, a, b, c = p["stufe"], p["a"], p["b"], p["c"]
    if st == 1:
        return bau(kette(Z(a + b + c), ("+", Z(b)), ("−", Z(b))))
    if st == 2:
        return bau(kette(Z(a + b + c), ("−", Z(b)), ("+", Z(-c)),
                         ("+", Z(b + c))))
    return bau(kette(Kl(Z(-(a + b))), ("−", Z(-c)), ("+", Z(-c)),
                     ("+", Z(b))))


BF3_12 = BF("BF12", "Sonderfall: die Zahl bleibt, wie sie war",
            BEREICH, bf3_12)


S3 = Schablone(
    nr="S3", titel="Addieren und Subtrahieren",
    lektionen="1.5 – 1.9", erhebung="", anleitung=ANLEITUNG,
    levelachse="Anzahl Glieder und Anzahl Vorzeichen",
    bauformen=[BF3_1, BF3_2, BF3_3, BF3_4, BF3_5, BF3_6,
               BF3_7, BF3_8, BF3_9, BF3_10, BF3_11, BF3_12],
    kernidee="Auf der Zahlengeraden heisst Plus «nach rechts» und Minus "
             "«nach links». Eine negative Zahl abzuziehen heisst darum, "
             "nach rechts zu gehen: 7 − (−3) ist 10.")
