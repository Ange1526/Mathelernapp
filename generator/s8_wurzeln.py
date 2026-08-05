# -*- coding: utf-8 -*-
"""
Kapitel 8 · Wurzeln       (Lektionen 8.1 – 8.9)

Vier Schablonen aus dem Matrixformat, je zwölf Bauformen mal drei Level:

    S26  Wurzeln verstehen              8.1 – 8.2    Vorstufe zu 3a, 3b, 3e
    S27  Wurzel aus einer Summe         8.3 · 8.7    Erhebung 3b
    S28  Wurzelgesetze                  8.4 – 8.8    Erhebung 3a
    S29  Wurzel aus Produkt mit Variable      8.9    Erhebung 3e

Damit sind drei Erhebungsteilaufgaben auf einmal abgedeckt.

Zwei Dinge, die beim Bauen aufgefallen sind und die Schablone nicht vorsehen
KONNTE, weil sie sich erst im Code zeigen:

1  «Radikand ausgerechnet, aber Wurzel stehen gelassen» (√25 statt 5) laesst
   sich NICHT in den Fehlerkatalog aufnehmen. SymPy wertet √25 sofort zu 5
   aus — der Eintrag waere wertgleich mit der Loesung, und der Filter
   `fehler_eindeutig` verwirft jede solche Aufgabe. Ein Schueler, der √25
   eintippt, bekommt RICHTIG. Das ist vertretbar: er hat gerechnet, nur nicht
   zu Ende geschrieben.

2  Brueche, die sich erst kuerzen lassen (S26 BF3), muessen als TEXT gebaut
   werden. `Rational(48, 75)` kuerzt beim Erzeugen von selbst zu 16/25 — die
   Aufgabe waere dann eine andere als gemeint.
"""
from __future__ import annotations

import re

from sympy import Integer, Rational, sqrt

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import HOCH, MINUS, zeige
from .qualitaet import (exponent_hoechstens, fehler_eindeutig, kopfrechenbar,
                        nenner_freundlich, symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, c, m, u, v, x, y, z = symbole("a b c m u v x y z")
VARS = {"a", "b", "c", "m", "u", "v", "x", "y", "z"}
EINE = [a, x, u, y, m]
ZWEI = [b, y, v, z, c]


def Zb(*w):
    return [Integer(i) if isinstance(i, int) else i for i in w]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def zeige_w(e) -> str:
    """Wie `zeige`, aber mit Wurzelzeichen.

    `zeige` kennt SymPys `sqrt` nicht und liefert «2sqrt(2)». Die Schuelerin
    liest 2√2. Der Rueckweg ueber `als_eingabe` funktioniert weiterhin: der
    Parser wandelt √2 selbst wieder in sqrt(2) um.
    """
    t = zeige(e)
    t = re.sub(r"sqrt\((\d+)\)", r"√\1", t)
    return t.replace("sqrt", "√")


def bau(frage, loesung, fehler, schritte, tipps, loesung_text=None,
        zielform=Zielform.BELIEBIG):
    """Zielform BELIEBIG ist hier die Regel, nicht die Ausnahme.

    Bei Wurzeln ist das Ergebnis eine Zahl oder ein einfaches Produkt. Eine
    Formpruefung wuerde nur Schreibweisen bestrafen, die sachlich richtig
    sind — etwa 5a gegen a·5.

    KATALOGEINTRAEGE, DIE DER LOESUNG GLEICHEN, WERDEN HIER VERWORFEN.
    Beispiel aus dem Testlauf: bei √(a⁴) ist die Loesung a², und der Fehler
    «Hochzahl um zwei verringert statt halbiert» ergibt ebenfalls a². Ohne
    diese Zeile wirft `fehler_eindeutig` die ganze Aufgabe weg, und die
    Bauform laesst sich auf Level A gar nicht mehr erzeugen — bei fuenf
    Bauformen ist genau das passiert.

    Der Eintrag faellt nur fuer DIESE Zahlenkombination weg, nicht
    grundsaetzlich: auf Level B und C traegt er weiterhin.
    """
    ziel = Loesung.zahl(loesung).expr
    brauchbar = [f for f in fehler
                 if f.ergebnis.expr is None or f.ergebnis.expr != ziel]
    return {"frage": frage, "loesung_text": loesung_text or zeige_w(loesung),
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=zielform, fehlerkatalog=brauchbar),
            "schritte": schritte, "tipps": tipps}


STD = [kopfrechenbar, nenner_freundlich, fehler_eindeutig,
       exponent_hoechstens(10)]


def pot(basis, e) -> str:
    """6² statt 6^2, ab zehn wieder ^10."""
    return f"{basis}{HOCH.get(int(e), f'^{e}')}"


def W(inhalt) -> str:
    """√49 bei einer blanken Zahl, sonst √(...) mit Klammer."""
    t = str(inhalt)
    return f"√{t}" if t.isdigit() else f"√({t})"


# ══════════════════════════════════════════════════════════════════════════
# S26 · Wurzeln verstehen           Lektionen 8.1 – 8.2
# ══════════════════════════════════════════════════════════════════════════

TIPPS_26 = [
    "Die Wurzel fragt: welche Zahl ergibt mal sich selbst den Radikanden?",
    "Bei einem Bruch darfst du Zähler und Nenner einzeln nehmen — kürze "
    "aber zuerst.",
    "Prüfe zum Schluss, ob dein Ergebnis mal sich selbst den Radikanden gibt.",
]


def bf26_1(p):
    n = p["n"]
    return bau(W(n * n), n, [
        F("halbiert", Rational(n * n, 2),
          f"Die Wurzel halbiert nicht. Gesucht ist die Zahl, die MAL SICH "
          f"SELBST {n*n} ergibt: {n} · {n}."),
        F("quadriert", n * n * n * n,
          "Das ist das Quadrat, nicht die Wurzel. Radizieren ist die "
          "Umkehrung des Quadrierens."),
    ], [("Frage stellen", f"welche Zahl mal sich selbst ergibt {n*n}?"),
        ("Ergebnis", f"{n} · {n} = {n*n}, also {n}")], TIPPS_26)


BF26_1 = Bauform("BF1", "Reine Quadratzahl",
    bereiche={"A": {"n": Zb(2, 3, 4, 5, 6, 7)},
              "B": {"n": Zb(12, 15, 20, 25, 30)},
              "C": {"n": Zb(41, 43, 47, 49)}},
    bauen=bf26_1, filter=STD)


def bf26_2(p):
    zr, nr = p["zr"], p["nr"]
    loesung = Rational(zr, nr)
    return bau(W(f"{zr*zr}/{nr*nr}"), loesung, [
        F("nur_zaehler", Rational(zr, nr * nr),
          f"Die Wurzel gilt für Zähler UND Nenner: √{zr*zr} = {zr} und "
          f"√{nr*nr} = {nr}, zusammen {zr}/{nr}."),
        F("nur_nenner", Rational(zr * zr, nr),
          f"Auch der Zähler steht unter der Wurzel: √{zr*zr} = {zr}."),
    ], [("Zähler radizieren", f"√{zr*zr} = {zr}"),
        ("Nenner radizieren", f"√{nr*nr} = {nr}"),
        ("Zusammensetzen", f"{zr}/{nr}")], TIPPS_26)


BF26_2 = Bauform("BF2", "Bruch — Zähler und Nenner einzeln",
    bereiche={"A": {"zr": Zb(2, 3), "nr": Zb(3, 5)},
              "B": {"zr": Zb(4, 5), "nr": Zb(3, 7)},
              "C": {"zr": Zb(13, 11), "nr": Zb(18, 15)}},
    bauen=bf26_2, filter=STD)


def bf26_3(p):
    zr, nr, k = p["zr"], p["nr"], p["k"]
    loesung = Rational(zr, nr)
    gekuerzt = Rational(zr * zr, nr * nr)
    return bau(W(f"{k*zr*zr}/{k*nr*nr}"), loesung, [
        F("nicht_radiziert", gekuerzt,
          f"Richtig gekürzt, aber noch nicht fertig: von {zr*zr}/{nr*nr} ist "
          f"noch die Wurzel zu ziehen, das ergibt {zr}/{nr}."),
        F("nur_zaehler", Rational(zr, nr * nr),
          "Die Wurzel gilt für Zähler UND Nenner."),
    ], [("Bruch kürzen", f"{k*zr*zr}/{k*nr*nr} = {zr*zr}/{nr*nr}"),
        ("Beide radizieren", f"√{zr*zr} = {zr}, √{nr*nr} = {nr}"),
        ("Ergebnis", f"{zr}/{nr}")], TIPPS_26)


BF26_3 = Bauform("BF3", "Bruch, der sich erst kürzen lässt",
    bereiche={"A": {"zr": Zb(2, 3), "nr": Zb(3, 5), "k": Zb(2)},
              "B": {"zr": Zb(4, 3), "nr": Zb(5, 4), "k": Zb(3, 2)},
              "C": {"zr": Zb(3, 5), "nr": Zb(4, 6), "k": Zb(5, 3)}},
    bauen=bf26_3, filter=STD)


def bf26_4(p):
    n = p["n"]
    return bau(W(pot(n, 2)), n, [
        F("hochzahl_behalten", n * n,
          f"Die Wurzel hebt das Quadrat auf: √({n}²) = {n}."),
        F("halbiert", Rational(n, 2),
          "Nicht die Basis wird halbiert, sondern die Hochzahl: aus ² wird ¹."),
    ], [("Wurzel und Quadrat heben sich auf", f"√({n}²) = {n}")], TIPPS_26)


BF26_4 = Bauform("BF4", "Potenz als Radikand — Wurzel hebt das Quadrat auf",
    bereiche={"A": {"n": Zb(4, 5, 6, 7)},
              "B": {"n": Zb(11, 13, 14)},
              "C": {"n": Zb(23, 27, 31)}},
    bauen=bf26_4, filter=STD)


def bf26_5(p):
    n = p["n"]
    return bau(W(f"({MINUS}{n})²"), n, [
        F("minus_mitgenommen", -n,
          f"({MINUS}{n})² ist {n*n}, also positiv. Eine Quadratwurzel ist nie "
          f"negativ — das Ergebnis ist {n}."),
        F("nicht_quadriert", -n * n,
          f"Zuerst wird quadriert: ({MINUS}{n})² = {n*n}. Erst dann die Wurzel."),
    ], [("Klammer quadrieren", f"({MINUS}{n})² = {n*n}"),
        ("Wurzel ziehen", f"√{n*n} = {n}")], TIPPS_26)


BF26_5 = Bauform("BF5", "Negative Basis, gerader Exponent",
    bereiche={"A": {"n": Zb(3, 4, 5)},
              "B": {"n": Zb(12, 15, 21)},
              "C": {"n": Zb(29, 31)}},
    bauen=bf26_5, filter=STD)


def bf26_6(p):
    n = p["n"]
    return bau(f"{MINUS}{W(n * n)}", -n, [
        F("minus_verschluckt", n,
          f"Das Minus steht VOR der Wurzel und gilt für das Ergebnis: "
          f"{MINUS}√{n*n} = {MINUS}{n}."),
        F("halbiert", Rational(-n * n, 2),
          "Die Wurzel halbiert nicht."),
    ], [("Wurzel ziehen", f"√{n*n} = {n}"),
        ("Minus davorsetzen", f"{MINUS}{n}")], TIPPS_26)


BF26_6 = Bauform("BF6", "Minus VOR der Wurzel",
    bereiche={"A": {"n": Zb(2, 3, 4)},
              "B": {"n": Zb(7, 9, 11)},
              "C": {"n": Zb(20, 25, 30)}},
    bauen=bf26_6, filter=STD)


def bf26_7(p):
    n = p["n"]
    return bau(f"√a = {n}   ·   Wie heisst a?", n * n, [
        F("halbiert", Rational(n, 2),
          f"Gesucht ist die Zahl, deren Wurzel {n} ist — also {n} · {n}."),
        F("verdoppelt", 2 * n,
          "Nicht verdoppeln, sondern quadrieren: das Gegenstück zur Wurzel."),
    ], [("Umkehren", "die Wurzel wird durch Quadrieren rückgängig gemacht"),
        ("Ergebnis", f"a = {n}² = {n*n}")], [
        "Die Wurzel und das Quadrat heben sich gegenseitig auf.",
        "Wenn √a die Zahl n ist, dann ist a das Quadrat von n.",
        f"a = {n} · {n}.",
    ])


BF26_7 = Bauform("BF7", "Rückwärts: der Radikand ist gesucht",
    bereiche={"A": {"n": Zb(4, 5, 6)},
              "B": {"n": Zb(12, 16, 18)},
              "C": {"n": Zb(21, 25, 27)}},
    bauen=bf26_7, filter=STD)


def bf26_8(p):
    n = p["n"]
    if n == 0:
        return bau(W(0), Integer(0), [
            F("eins", Integer(1), "√0 ist 0, nicht 1: 0 · 0 = 0."),
        ], [("Frage stellen", "welche Zahl mal sich selbst ergibt 0?"),
            ("Ergebnis", "0")], TIPPS_26)
    return bau(W(1), Integer(1), [
        F("null", Integer(0), "√1 ist 1, nicht 0: 1 · 1 = 1."),
    ], [("Frage stellen", "welche Zahl mal sich selbst ergibt 1?"),
        ("Ergebnis", "1")], TIPPS_26)


BF26_8 = Bauform("BF8", "Sonderfall: Radikand null oder eins",
    bereiche={"A": {"n": Zb(0, 1)}, "B": {"n": Zb(0, 1)}, "C": {"n": Zb(0, 1)}},
    bauen=bf26_8, filter=[fehler_eindeutig])


def bf26_9(p):
    basis, e = p["basis"], p["e"]
    loesung = basis ** (e // 2)
    return bau(W(pot(basis, e)), loesung, [
        F("hochzahl_behalten", basis ** e,
          f"Beim Radizieren wird die Hochzahl halbiert: aus {basis}{HOCH[e]} "
          f"wird {basis}{HOCH.get(e//2, '')}."),
        F("basis_halbiert", Rational(basis, 2) ** e,
          "Halbiert wird die Hochzahl, nicht die Basis."),
    ], [("Hochzahl halbieren", f"{e} : 2 = {e//2}"),
        ("Ausrechnen", f"{basis}{HOCH.get(e//2, '')} = {loesung}")], TIPPS_26)


BF26_9 = Bauform("BF9", "Potenz mit hoher gerader Hochzahl",
    bereiche={"A": {"basis": Zb(2), "e": Zb(4, 6)},
              "B": {"basis": Zb(3), "e": Zb(4, 6)},
              "C": {"basis": Zb(2, 10), "e": Zb(4, 8)}},
    bauen=bf26_9, filter=STD)


def bf26_10(p):
    n = p["n"]
    return bau(W(n * n), n, [
        F("halbiert", Rational(n * n, 2),
          f"Die Wurzel halbiert nicht: gesucht ist die Zahl mit {n} · {n} = {n*n}."),
        F("verzehnfacht", 10 * n,
          "Zehnerstellen helfen beim Schätzen, ersetzen aber die Probe nicht."),
    ], [("Schätzen", f"{n} · {n} liegt bei {n*n}"),
        ("Ergebnis", f"{n}")], TIPPS_26)


BF26_10 = Bauform("BF10", "Grosse Quadratzahl",
    bereiche={"A": {"n": Zb(17, 19, 22)},
              "B": {"n": Zb(62, 68, 74)},
              "C": {"n": Zb(85, 96, 110)}},
    bauen=bf26_10, filter=[nenner_freundlich, fehler_eindeutig])


def bf26_11(p):
    n1, n2, zeichen = p["n1"], p["n2"], p["zeichen"]
    if zeichen == 1:
        loesung = n1 + n2
        frage = f"{W(n1*n1)} + {W(n2*n2)}"
    else:
        loesung = n1 - n2
        frage = f"{W(n1*n1)} {MINUS} {W(n2*n2)}"
    return bau(frage, loesung, [
        F("radikanden_verrechnet",
          sqrt(n1 * n1 + zeichen * n2 * n2) if zeichen == 1
          else sqrt(n1 * n1 - n2 * n2),
          "Jede Wurzel wird einzeln gezogen. Zusammenfassen darf man nur bei "
          "mal und geteilt, nicht bei plus und minus."),
        F("halbiert", Rational(n1 * n1 + zeichen * n2 * n2, 2),
          "Die Wurzel halbiert nicht."),
    ], [("Erste Wurzel", f"√{n1*n1} = {n1}"),
        ("Zweite Wurzel", f"√{n2*n2} = {n2}"),
        ("Verrechnen", zeige(loesung))], TIPPS_26)


BF26_11 = Bauform("BF11", "Zwei Wurzeln addieren oder subtrahieren",
    bereiche={"A": {"n1": Zb(3, 4), "n2": Zb(2), "zeichen": Zb(1)},
              "B": {"n1": Zb(5, 6), "n2": Zb(3, 4), "zeichen": Zb(1, -1)},
              "C": {"n1": Zb(8, 9), "n2": Zb(5, 6), "zeichen": Zb(1, -1)}},
    bauen=bf26_11, filter=STD)


def bf26_12(p):
    nr = p["nr"]
    loesung = Rational(1, nr)
    return bau(W(f"1/{nr*nr}"), loesung, [
        F("nur_nenner", Rational(1, nr * nr),
          f"Auch der Nenner wird radiziert: √{nr*nr} = {nr}, also 1/{nr}."),
        F("gekippt", Integer(nr),
          "Der Bruch bleibt ein Bruch: der Zähler ist √1 = 1."),
    ], [("Zähler radizieren", "√1 = 1"),
        ("Nenner radizieren", f"√{nr*nr} = {nr}"),
        ("Ergebnis", f"1/{nr}")], TIPPS_26)


BF26_12 = Bauform("BF12", "Bruch kleiner als eins",
    bereiche={"A": {"nr": Zb(2, 3)},
              "B": {"nr": Zb(4, 5)},
              "C": {"nr": Zb(6, 7)}},
    bauen=bf26_12, filter=STD)


S26 = Schablone(
    nr="S26", titel="Wurzeln verstehen",
    lektionen="8.1 – 8.2", erhebung="Vorstufe zu 3a, 3b und 3e",
    anleitung="Rechne aus.",
    levelachse="Struktur des Radikanden",
    bauformen=[BF26_1, BF26_2, BF26_3, BF26_4, BF26_5, BF26_6,
               BF26_7, BF26_8, BF26_9, BF26_10, BF26_11, BF26_12],
    kernidee=("Die Quadratwurzel aus a ist die nicht negative Zahl, die mit "
              "sich selbst multipliziert a ergibt. Radizieren ist die "
              "Umkehrung des Quadrierens."),
)


# ══════════════════════════════════════════════════════════════════════════
# S27 · Wurzel aus einer Summe      Lektionen 8.3 · 8.7      Erhebung 3b
# ══════════════════════════════════════════════════════════════════════════

TIPPS_27 = [
    "Der Wurzelstrich wirkt wie eine Klammer: alles darunter gehört zusammen.",
    "Rechne zuerst aus, was unter dem Strich steht. Erst dann ziehst du die "
    "Wurzel.",
    "Erst den Radikanden zusammenzählen, dann eine einzige Wurzel ziehen.",
]

#: Pythagoreische Tripel — damit die Summe zweier Quadrate wieder eine
#: Quadratzahl ist. Ohne sie waere √(a² + b²) fast nie ganzzahlig.
TRIPEL_A = [(3, 4, 5), (6, 8, 10)]
TRIPEL_B = [(5, 12, 13), (8, 15, 17), (9, 12, 15)]
TRIPEL_C = [(7, 24, 25), (12, 16, 20), (20, 21, 29)]


def bf27_1(p):
    k1, k2, s = p["t"]
    return bau(f"{W(f'{k1*k1} + {k2*k2}')}", Integer(s), [
        F("verteilt", Integer(k1 + k2),
          f"Der Wurzelstrich ist eine Klammer. √({k1*k1}+{k2*k2}) = "
          f"√{k1*k1+k2*k2} = {s}, nicht √{k1*k1} + √{k2*k2}."),
        F("halbiert", Rational(k1 * k1 + k2 * k2, 2),
          "Die Wurzel halbiert nicht."),
    ], [("Radikand ausrechnen", f"{k1*k1} + {k2*k2} = {k1*k1+k2*k2}"),
        ("Wurzel ziehen", f"√{k1*k1+k2*k2} = {s}")], TIPPS_27)


BF27_1 = Bauform("BF1", "Summe zweier Quadratzahlen",
    bereiche={"A": {"t": TRIPEL_A}, "B": {"t": TRIPEL_B}, "C": {"t": TRIPEL_C}},
    bauen=bf27_1, filter=STD)


def bf27_2(p):
    k1, k2, s = p["t"]
    return bau(f"{W(f'{s*s} {MINUS} {k2*k2}')}", Integer(k1), [
        F("verteilt", Integer(s - k2),
          f"√{s*s} {MINUS} √{k2*k2} ergibt {s-k2}, gefragt ist aber "
          f"√({s*s}{MINUS}{k2*k2}) = √{s*s-k2*k2} = {k1}."),
        F("halbiert", Rational(s * s - k2 * k2, 2),
          "Die Wurzel halbiert nicht."),
    ], [("Radikand ausrechnen", f"{s*s} {MINUS} {k2*k2} = {s*s-k2*k2}"),
        ("Wurzel ziehen", f"√{s*s-k2*k2} = {k1}")], TIPPS_27)


BF27_2 = Bauform("BF2", "Differenz zweier Quadratzahlen",
    bereiche={"A": {"t": TRIPEL_A}, "B": {"t": TRIPEL_B}, "C": {"t": TRIPEL_C}},
    bauen=bf27_2, filter=STD)


def bf27_3(p):
    k1, k2, s = p["t"]
    return bau(W(f"{pot(k1,2)} + {pot(k2,2)}"), Integer(s), [
        F("einzeln_radiziert", Integer(k1 + k2),
          f"Das wäre {k1} + {k2}. Richtig: {k1*k1} + {k2*k2} = {k1*k1+k2*k2}, "
          f"und √{k1*k1+k2*k2} = {s}."),
        F("basen_addiert", Integer((k1 + k2) ** 2),
          "Die Potenzen werden zuerst ausgerechnet, nicht die Basen addiert."),
    ], [("Potenzen ausrechnen", f"{k1}² = {k1*k1}, {k2}² = {k2*k2}"),
        ("Addieren", f"{k1*k1} + {k2*k2} = {k1*k1+k2*k2}"),
        ("Wurzel ziehen", f"√{k1*k1+k2*k2} = {s}")], TIPPS_27)


BF27_3 = Bauform("BF3", "Potenzen in der Summe",
    bereiche={"A": {"t": TRIPEL_A}, "B": {"t": TRIPEL_B}, "C": {"t": TRIPEL_C}},
    bauen=bf27_3, filter=STD)


def bf27_4(p):
    k1, k2, s = p["t"]
    return bau(W(f"{pot(s,2)} {MINUS} {pot(k2,2)}"), Integer(k1), [
        F("einzeln_radiziert", Integer(s - k2),
          f"Das wäre {s} {MINUS} {k2}. Richtig: {s*s} {MINUS} {k2*k2} = "
          f"{s*s-k2*k2}, und √{s*s-k2*k2} = {k1}."),
        F("halbiert", Rational(s * s - k2 * k2, 2),
          "Die Wurzel halbiert nicht."),
    ], [("Potenzen ausrechnen", f"{s}² = {s*s}, {k2}² = {k2*k2}"),
        ("Subtrahieren", f"{s*s} {MINUS} {k2*k2} = {s*s-k2*k2}"),
        ("Wurzel ziehen", f"√{s*s-k2*k2} = {k1}")], TIPPS_27)


BF27_4 = Bauform("BF4", "Potenzen in der Differenz",
    bereiche={"A": {"t": TRIPEL_A}, "B": {"t": TRIPEL_B}, "C": {"t": TRIPEL_C}},
    bauen=bf27_4, filter=STD)


def bf27_5(p):
    basis, e, anzahl = p["basis"], p["e"], p["anzahl"]
    radikand = anzahl * basis ** e
    loesung = sqrt(Integer(radikand))
    frage = " + ".join([pot(basis, e)] * anzahl)
    return bau(W(frage), loesung, [
        F("basen_addiert", Integer(anzahl * basis) ** (e // 2 if e % 2 == 0 else e),
          f"{basis}{HOCH[e]} + {basis}{HOCH[e]} ist nicht ({anzahl}·{basis}){HOCH[e]}. "
          f"Gleiche Summanden ergeben das {anzahl}-fache: {anzahl} · {basis**e} "
          f"= {radikand}."),
        F("einzeln_radiziert", anzahl * sqrt(Integer(basis ** e)),
          "Der Wurzelstrich ist eine Klammer — erst addieren, dann radizieren."),
    ], [("Gleiche Summanden zusammenfassen",
         f"{anzahl} · {basis**e} = {radikand}"),
        ("Wurzel ziehen", f"√{radikand} = {zeige(loesung)}")], TIPPS_27)


BF27_5 = Bauform("BF5", "Zwei gleiche Potenzen",
    bereiche={"A": {"basis": Zb(2), "e": Zb(3), "anzahl": Zb(2)},
              "B": {"basis": Zb(2), "e": Zb(5, 7), "anzahl": Zb(2)},
              "C": {"basis": Zb(3), "e": Zb(3), "anzahl": Zb(3)}},
    bauen=bf27_5, filter=STD)


def bf27_6(p):
    s, teile = p["s"], p["teile"]
    rest = s * s - sum(teile)
    glieder = list(teile) + [rest]
    frage = W(" + ".join(str(g) for g in glieder))
    return bau(frage, Integer(s), [
        F("verteilt", sum(sqrt(Integer(g)) for g in glieder),
          f"Der Wurzelstrich ist eine Klammer: erst {' + '.join(str(g) for g in glieder)} "
          f"= {s*s}, dann √{s*s} = {s}."),
        F("halbiert", Rational(s * s, 2), "Die Wurzel halbiert nicht."),
    ], [("Radikand ausrechnen",
         f"{' + '.join(str(g) for g in glieder)} = {s*s}"),
        ("Wurzel ziehen", f"√{s*s} = {s}")], TIPPS_27)


BF27_6 = Bauform("BF6", "Drei und mehr Summanden",
    bereiche={"A": {"s": Zb(3), "teile": [(4, 4), (1, 4)]},
              "B": {"s": Zb(6), "teile": [(9, 16), (4, 16)]},
              "C": {"s": Zb(10), "teile": [(16, 9, 25), (25, 25, 25)]}},
    bauen=bf27_6, filter=STD)


def bf27_7(p):
    k, f2 = p["k"], p["f2"]
    radikand = k * f2
    loesung = sqrt(Integer(radikand))
    return bau(W(f"{k} · {f2}"), loesung, [
        F("addiert", sqrt(Integer(k + f2)),
          f"Unter der Wurzel steht ein Produkt: {k} · {f2} = {radikand}."),
        F("einzeln", sqrt(Integer(k)) * f2,
          "Erst das Produkt ausrechnen, dann die Wurzel ziehen."),
    ], [("Produkt ausrechnen", f"{k} · {f2} = {radikand}"),
        ("Wurzel ziehen", f"√{radikand} = {zeige(loesung)}")], TIPPS_27)


BF27_7 = Bauform("BF7", "Produkt unter der Wurzel",
    bereiche={"A": {"k": Zb(2), "f2": Zb(8, 18)},
              "B": {"k": Zb(3), "f2": Zb(12, 27)},
              "C": {"k": Zb(5), "f2": Zb(20, 45)}},
    bauen=bf27_7, filter=STD)


def bf27_8(p):
    n = p["n"]
    return bau(W(f"{n} {MINUS} {n}"), Integer(0), [
        F("nicht_gerechnet", Integer(n),
          f"Zuerst der Radikand: {n} {MINUS} {n} = 0. Und √0 = 0."),
    ], [("Radikand ausrechnen", f"{n} {MINUS} {n} = 0"),
        ("Wurzel ziehen", "√0 = 0")], TIPPS_27)


BF27_8 = Bauform("BF8", "Sonderfall: der Radikand wird null",
    bereiche={"A": {"n": Zb(4, 9)}, "B": {"n": Zb(16, 100)},
              "C": {"n": Zb(64, 144)}},
    bauen=bf27_8, filter=[fehler_eindeutig])


def bf27_9(p):
    n = p["n"]
    return bau(W(f"{n+1} {MINUS} {n}"), Integer(1), [
        F("verteilt", sqrt(Integer(n + 1)) - sqrt(Integer(n)),
          f"Erst rechnen: {n+1} {MINUS} {n} = 1. Und √1 = 1."),
    ], [("Radikand ausrechnen", f"{n+1} {MINUS} {n} = 1"),
        ("Wurzel ziehen", "√1 = 1")], TIPPS_27)


BF27_9 = Bauform("BF9", "Sonderfall: der Radikand wird eins",
    bereiche={"A": {"n": Zb(3, 8)}, "B": {"n": Zb(9, 15)},
              "C": {"n": Zb(24, 35)}},
    bauen=bf27_9, filter=[fehler_eindeutig])


def bf27_10(p):
    s, sub = p["s"], p["sub"]
    gross = s * s + sub
    return bau(W(f"{gross} {MINUS} {sub}"), Integer(s), [
        F("verteilt", sqrt(Integer(gross)) - sqrt(Integer(sub)),
          f"Der Wurzelstrich ist eine Klammer: {gross} {MINUS} {sub} = {s*s}, "
          f"dann √{s*s} = {s}."),
        F("halbiert", Rational(s * s, 2), "Die Wurzel halbiert nicht."),
    ], [("Radikand ausrechnen", f"{gross} {MINUS} {sub} = {s*s}"),
        ("Wurzel ziehen", f"√{s*s} = {s}")], TIPPS_27)


BF27_10 = Bauform("BF10", "Radikand ist keine Summe von Quadratzahlen",
    bereiche={"A": {"s": Zb(5), "sub": Zb(25, 11)},
              "B": {"s": Zb(6), "sub": Zb(14, 19)},
              "C": {"s": Zb(9), "sub": Zb(19, 23)}},
    bauen=bf27_10, filter=STD)


def bf27_11(p):
    k1, k2, s = p["t"]
    zusatz, art = p["zusatz"], p["art"]
    if art == 1:
        loesung = Integer(s + zusatz)
        frage = f"{W(f'{k1*k1} + {k2*k2}')} + {zusatz}"
    else:
        loesung = Integer(s * zusatz)
        frage = f"{zusatz} · {W(f'{k1*k1} + {k2*k2}')}"
    return bau(frage, loesung, [
        F("verteilt", Integer(k1 + k2 + zusatz) if art == 1
          else Integer((k1 + k2) * zusatz),
          f"Zuerst der Radikand: {k1*k1} + {k2*k2} = {k1*k1+k2*k2}, "
          f"dann √{k1*k1+k2*k2} = {s}."),
        F("zusatz_vergessen", Integer(s),
          "Die Rechnung nach der Wurzel gehört noch dazu."),
    ], [("Radikand ausrechnen", f"{k1*k1} + {k2*k2} = {k1*k1+k2*k2}"),
        ("Wurzel ziehen", f"√{k1*k1+k2*k2} = {s}"),
        ("Rest ausrechnen", zeige(loesung))], TIPPS_27)


BF27_11 = Bauform("BF11", "Nach der Wurzel kommt noch eine Rechnung",
    bereiche={"A": {"t": TRIPEL_A, "zusatz": Zb(1, 2), "art": Zb(1)},
              "B": {"t": TRIPEL_B, "zusatz": Zb(3, 4), "art": Zb(1, 2)},
              "C": {"t": TRIPEL_C, "zusatz": Zb(2, 3), "art": Zb(1, 2)}},
    bauen=bf27_11, filter=STD)


def bf27_12(p):
    n1, n2 = p["n1"], p["n2"]
    loesung = sqrt(Integer(n1 * n1 + n2 * n2))
    return bau(W(f"{n1*n1} + {n2*n2}"), loesung, [
        F("verteilt", Integer(n1 + n2),
          f"√{n1*n1} + √{n2*n2} wäre {n1+n2}. Unter EINEM Wurzelstrich steht "
          f"aber √{n1*n1+n2*n2} — und das ist keine ganze Zahl."),
    ], [("Radikand ausrechnen", f"{n1*n1} + {n2*n2} = {n1*n1+n2*n2}"),
        ("Wurzel ziehen", f"√{n1*n1+n2*n2} lässt sich nicht vereinfachen"),
        ("Vergleich", f"√{n1*n1} + √{n2*n2} wäre {n1+n2} — ein anderer Wert")],
        [
        "Der Wurzelstrich ist eine Klammer — √(a+b) ist NICHT √a + √b.",
        "Rechne beide Wege aus und vergleiche die Ergebnisse.",
        "Wenn der Radikand keine Quadratzahl ist, bleibt die Wurzel stehen.",
    ])


BF27_12 = Bauform("BF12", "Der Vergleich: verteilt oder nicht",
    bereiche={"A": {"n1": Zb(2), "n2": Zb(3)},
              "B": {"n1": Zb(2, 3), "n2": Zb(3, 4)},
              "C": {"n1": Zb(4, 5), "n2": Zb(5, 6)}},
    bauen=bf27_12, filter=[nenner_freundlich, fehler_eindeutig])


S27 = Schablone(
    nr="S27", titel="Wurzel aus einer Summe",
    lektionen="8.3 · 8.7", erhebung="3b",
    anleitung="Rechne aus.",
    levelachse="Gliederzahl und Struktur",
    bauformen=[BF27_1, BF27_2, BF27_3, BF27_4, BF27_5, BF27_6,
               BF27_7, BF27_8, BF27_9, BF27_10, BF27_11, BF27_12],
    kernidee=("Der Wurzelstrich wirkt wie eine Klammer. √(a + b) ist nicht "
              "√a + √b — erst den Radikanden ausrechnen, dann die Wurzel "
              "ziehen."),
)


# ══════════════════════════════════════════════════════════════════════════
# S28 · Wurzelgesetze       Lektionen 8.4 – 8.6 · 8.8       Erhebung 3a
# ══════════════════════════════════════════════════════════════════════════

TIPPS_28 = [
    "Mal und geteilt darfst du unter einer Wurzel zusammenfassen. Plus und "
    "minus nicht.",
    "Schreibe beide Zahlen unter einen einzigen Wurzelstrich.",
    "Erst den Radikanden ausrechnen, dann die Wurzel ziehen.",
]


def bf28_1(p):
    k, s = p["k"], p["s"]
    zweiter = s * s // k if (s * s) % k == 0 else None
    if zweiter is None:
        zweiter = s * s
        k = 1
    return bau(f"{W(k)} · {W(zweiter)}", Integer(s), [
        F("radikanden_addiert", sqrt(Integer(k + zweiter)),
          f"Beim Multiplizieren werden die Radikanden multipliziert: "
          f"{k} · {zweiter} = {k*zweiter}, also {s}."),
        F("nur_einer", sqrt(Integer(zweiter)),
          "Beide Wurzeln zählen — auch die erste kommt unter den Strich."),
    ], [("Zusammenfassen", f"√({k} · {zweiter})"),
        ("Radikand ausrechnen", f"{k} · {zweiter} = {k*zweiter}"),
        ("Wurzel ziehen", f"√{k*zweiter} = {s}")], TIPPS_28)


BF28_1 = Bauform("BF1", "Produkt zweier Wurzeln",
    bereiche={"A": {"k": Zb(2), "s": Zb(4, 6)},
              "B": {"k": Zb(5), "s": Zb(10, 15)},
              "C": {"k": Zb(12), "s": Zb(18, 24)}},
    bauen=bf28_1, filter=STD)


def bf28_2(p):
    teiler, s = p["teiler"], p["s"]
    zaehler = teiler * s * s
    return bau(f"{W(zaehler)} : {W(teiler)}", Integer(s), [
        F("verkehrt", Rational(1, s),
          f"Die Reihenfolge zählt: {zaehler} : {teiler} = {s*s}, also {s}."),
        F("radikanden_subtrahiert", sqrt(Integer(zaehler - teiler)),
          f"Beim Dividieren werden die Radikanden geteilt, nicht subtrahiert."),
    ], [("Zusammenfassen", f"√({zaehler} : {teiler})"),
        ("Radikand ausrechnen", f"{zaehler} : {teiler} = {s*s}"),
        ("Wurzel ziehen", f"√{s*s} = {s}")], TIPPS_28)


BF28_2 = Bauform("BF2", "Quotient zweier Wurzeln",
    bereiche={"A": {"teiler": Zb(5), "s": Zb(2, 3)},
              "B": {"teiler": Zb(7), "s": Zb(10)},
              "C": {"teiler": Zb(10), "s": Zb(10, 12)}},
    bauen=bf28_2, filter=STD)


def bf28_3(p):
    k1, k2 = p["k1"], p["k2"]
    return bau(W(f"{k1*k1} · {k2*k2}"), Integer(k1 * k2), [
        F("nur_erster", Integer(k1),
          f"Beide Faktoren stehen unter der Wurzel: √{k1*k1} · √{k2*k2} = "
          f"{k1} · {k2} = {k1*k2}."),
        F("addiert", sqrt(Integer(k1 * k1 + k2 * k2)),
          "Unter der Wurzel steht ein Produkt, keine Summe."),
    ], [("Produkt aufteilen", f"√{k1*k1} · √{k2*k2}"),
        ("Einzeln radizieren", f"{k1} und {k2}"),
        ("Multiplizieren", f"{k1} · {k2} = {k1*k2}")], TIPPS_28)


BF28_3 = Bauform("BF3", "Produkt unter EINER Wurzel aufteilen",
    bereiche={"A": {"k1": Zb(2), "k2": Zb(3)},
              "B": {"k1": Zb(4), "k2": Zb(5)},
              "C": {"k1": Zb(2, 3), "k2": Zb(6, 8)}},
    bauen=bf28_3, filter=STD)


def bf28_4(p):
    k1, k2 = p["k1"], p["k2"]
    loesung = Rational(k1, k2)
    return bau(W(f"{k1*k1}/{k2*k2}"), loesung, [
        F("verkehrt", Rational(k2, k1),
          f"Die Reihenfolge zählt: √{k1*k1} : √{k2*k2} = {k1}/{k2}."),
        F("nur_zaehler", Rational(k1, k2 * k2),
          "Auch der Nenner wird radiziert."),
    ], [("Aufteilen", f"√{k1*k1} : √{k2*k2}"),
        ("Einzeln radizieren", f"{k1} und {k2}"),
        ("Ergebnis", zeige(loesung))], TIPPS_28)


BF28_4 = Bauform("BF4", "Quotient unter einer Wurzel",
    bereiche={"A": {"k1": Zb(6), "k2": Zb(2)},
              "B": {"k1": Zb(1, 3), "k2": Zb(3, 9)},
              "C": {"k1": Zb(10, 4), "k2": Zb(5, 12)}},
    bauen=bf28_4, filter=STD)


def bf28_5(p):
    r, c1, c2 = p["r"], p["c1"], p["c2"]
    loesung = (c1 + c2) * sqrt(Integer(r))
    frage = (f"{c1 if c1 != 1 else ''}{W(r)} + "
             f"{c2 if c2 != 1 else ''}{W(r)}")
    return bau(frage, loesung, [
        F("radikanden_addiert", sqrt(Integer(r * (c1 + c2) ** 0 + r)),
          f"Zusammenfassen darfst du nur bei mal und geteilt. Gleiche Wurzeln "
          f"werden gezählt: {c1} + {c2} = {c1+c2} Stück √{r}."),
        F("wurzel_verschwunden", Integer((c1 + c2) * r),
          f"Die Wurzel bleibt stehen — √{r} ist keine ganze Zahl."),
    ], [("Gleiche Wurzeln erkennen", f"beide Male √{r}"),
        ("Anzahl zählen", f"{c1} + {c2} = {c1+c2}"),
        ("Ergebnis", zeige(loesung))], TIPPS_28)


BF28_5 = Bauform("BF5", "Addition — das Gesetz gilt hier NICHT",
    bereiche={"A": {"r": Zb(2), "c1": Zb(1), "c2": Zb(1)},
              "B": {"r": Zb(5), "c1": Zb(3), "c2": Zb(1, 2)},
              "C": {"r": Zb(3, 7), "c1": Zb(2, 4), "c2": Zb(3, 5)}},
    bauen=bf28_5, filter=[nenner_freundlich, fehler_eindeutig])


def bf28_6(p):
    r, anzahl = p["r"], p["anzahl"]
    loesung = Integer(r) ** Rational(anzahl, 2)
    frage = " · ".join([W(r)] * anzahl)
    return bau(frage, loesung, [
        F("verdoppelt", 2 * sqrt(Integer(r)),
          f"√{r} · √{r} ist √({r}·{r}) = √{r*r} = {r}, nicht 2√{r}."),
        F("radikand_behalten", sqrt(Integer(r)),
          f"Die beiden Wurzeln heben sich zu {r} auf."),
    ], [("Zusammenfassen", f"√({' · '.join([str(r)]*anzahl)})"),
        ("Ergebnis", zeige(loesung))], TIPPS_28)


BF28_6 = Bauform("BF6", "Dieselbe Wurzel multipliziert",
    bereiche={"A": {"r": Zb(2, 5), "anzahl": Zb(2)},
              "B": {"r": Zb(7, 11), "anzahl": Zb(2)},
              "C": {"r": Zb(3), "anzahl": Zb(4)}},
    bauen=bf28_6, filter=STD)


def bf28_7(p):
    r, n1 = p["r"], p["n1"]
    loesung = Rational(r, n1)
    frage = f"({W(r)}/{n1}) · {W(r)}"
    return bau(frage, loesung, [
        F("nur_ein_faktor", Rational(1, n1) * sqrt(Integer(r)),
          f"Auch die zweite Wurzel wird mitmultipliziert: √{r} · √{r} = {r}."),
        F("nenner_vergessen", Integer(r),
          f"Der Nenner {n1} bleibt stehen."),
    ], [("Wurzeln multiplizieren", f"√{r} · √{r} = {r}"),
        ("Durch den Nenner teilen", f"{r}/{n1} = {zeige(loesung)}")], TIPPS_28)


BF28_7 = Bauform("BF7", "Wurzeln in Brüchen",
    bereiche={"A": {"r": Zb(6), "n1": Zb(2, 3)},
              "B": {"r": Zb(8, 12), "n1": Zb(2, 4)},
              "C": {"r": Zb(18, 20), "n1": Zb(3, 5)}},
    bauen=bf28_7, filter=STD)


def bf28_8(p):
    r = p["r"]
    return bau(f"{W(r)} · {W(0)}", Integer(0), [
        F("null_ignoriert", sqrt(Integer(r)),
          f"√0 = 0, und alles mal null ist null."),
    ], [("Zusammenfassen", f"√({r} · 0) = √0"),
        ("Ergebnis", "0")], TIPPS_28)


BF28_8 = Bauform("BF8", "Sonderfall: ein Faktor ist null",
    bereiche={"A": {"r": Zb(3, 5)}, "B": {"r": Zb(48, 75)},
              "C": {"r": Zb(120, 200)}},
    bauen=bf28_8, filter=[fehler_eindeutig])


def bf28_9(p):
    k = p["k"]
    return bau(f"{W(k*k)} : {W(k*k)}", Integer(1), [
        F("null", Integer(0),
          f"Eine Zahl durch sich selbst ist 1, nicht 0."),
        F("radikand", Integer(k),
          f"√{k*k} : √{k*k} = {k} : {k} = 1."),
    ], [("Beide Wurzeln ziehen", f"√{k*k} = {k}"),
        ("Dividieren", f"{k} : {k} = 1")], TIPPS_28)


BF28_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist eins",
    bereiche={"A": {"k": Zb(3, 4)}, "B": {"k": Zb(4, 6)},
              "C": {"k": Zb(7, 9)}},
    bauen=bf28_9, filter=[fehler_eindeutig])


def bf28_10(p):
    k, s = p["k"], p["s"]
    zweiter = s * s // k
    return bau(f"{W(k)} · {W(zweiter)}", Integer(s), [
        F("radikanden_addiert", sqrt(Integer(k + zweiter)),
          f"Beim Multiplizieren werden die Radikanden multipliziert: "
          f"{k} · {zweiter} = {s*s}, also {s}."),
        F("nur_einer", sqrt(Integer(zweiter)),
          "Beide Radikanden kommen unter einen Strich."),
    ], [("Zusammenfassen", f"√({k} · {zweiter})"),
        ("Radikand ausrechnen", f"{k} · {zweiter} = {s*s}"),
        ("Wurzel ziehen", f"√{s*s} = {s}")], TIPPS_28)


BF28_10 = Bauform("BF10", "Keiner der Radikanden ist eine Quadratzahl",
    bereiche={"A": {"k": Zb(2), "s": Zb(10)},
              "B": {"k": Zb(3), "s": Zb(12)},
              "C": {"k": Zb(2, 3), "s": Zb(14, 18)}},
    bauen=bf28_10, filter=STD)


def bf28_11(p):
    teiler, s = p["teiler"], p["s"]
    zaehler = teiler * s * s
    return bau(f"{W(zaehler)} : {W(teiler)}", Integer(s), [
        F("subtrahiert", sqrt(Integer(zaehler - teiler)),
          f"Beim Dividieren werden die Radikanden geteilt: "
          f"{zaehler} : {teiler} = {s*s}."),
        F("verkehrt", Rational(1, s),
          "Die Reihenfolge zählt."),
    ], [("Zusammenfassen", f"√({zaehler} : {teiler})"),
        ("Radikand ausrechnen", f"{zaehler} : {teiler} = {s*s}"),
        ("Wurzel ziehen", f"√{s*s} = {s}")], TIPPS_28)


BF28_11 = Bauform("BF11", "Division, beide keine Quadratzahlen",
    bereiche={"A": {"teiler": Zb(2), "s": Zb(2, 3)},
              "B": {"teiler": Zb(5), "s": Zb(3, 4)},
              "C": {"teiler": Zb(2, 3), "s": Zb(6)}},
    bauen=bf28_11, filter=STD)


def bf28_12(p):
    z1, n1, z2, n2 = p["z1"], p["n1"], p["z2"], p["n2"]
    loesung = sqrt(Rational(z1 * z2, n1 * n2))
    frage = f"{W(f'{z1}/{n1}')} · {W(f'{z2}/{n2}')}"
    return bau(frage, loesung, [
        F("addiert", sqrt(Rational(z1, n1) + Rational(z2, n2)),
          "Die Brüche werden multipliziert, nicht addiert."),
        F("nicht_radiziert", Rational(z1 * z2, n1 * n2),
          "Richtig multipliziert, aber die Wurzel fehlt noch."),
    ], [("Brüche multiplizieren",
         f"{z1}/{n1} · {z2}/{n2} = {zeige(Rational(z1*z2, n1*n2))}"),
        ("Wurzel ziehen", zeige(loesung))], TIPPS_28)


BF28_12 = Bauform("BF12", "Kette aus mehreren Brüchen",
    bereiche={"A": {"z1": Zb(4), "n1": Zb(5), "z2": Zb(5), "n2": Zb(4)},
              "B": {"z1": Zb(4), "n1": Zb(5), "z2": Zb(5), "n2": Zb(9)},
              "C": {"z1": Zb(1, 9), "n1": Zb(2, 4), "z2": Zb(2, 4),
                    "n2": Zb(9, 25)}},
    bauen=bf28_12, filter=STD)


S28 = Schablone(
    nr="S28", titel="Wurzelgesetze",
    lektionen="8.4 – 8.6 · 8.8", erhebung="3a",
    anleitung="Rechne aus.",
    levelachse="Grösse der Zahlen und Anzahl Faktoren",
    bauformen=[BF28_1, BF28_2, BF28_3, BF28_4, BF28_5, BF28_6,
               BF28_7, BF28_8, BF28_9, BF28_10, BF28_11, BF28_12],
    kernidee=("√a · √b = √(a · b) und √a : √b = √(a : b). Für Summen und "
              "Differenzen gibt es kein entsprechendes Gesetz."),
)


# ══════════════════════════════════════════════════════════════════════════
# S29 · Wurzel aus Produkt mit Variable     Lektion 8.9     Erhebung 3e
# ══════════════════════════════════════════════════════════════════════════

TIPPS_29 = [
    "Ein Produkt unter der Wurzel darfst du in einzelne Wurzeln zerlegen.",
    "Nimm die Zahl und die Variable getrennt: einmal die Zahl, einmal die "
    "Potenz.",
    "Bei der Zahl wird radiziert, bei der Variablen die Hochzahl halbiert.",
]


def var(v, e=1) -> str:
    return str(v) if e == 1 else f"{v}{HOCH.get(int(e), f'^{e}')}"


def bf29_1(p):
    k, v = p["k"], p["var"]
    loesung = k * v
    return bau(W(f"{k*k}{var(v, 2)}"), loesung, [
        F("hochzahl_behalten", k * v ** 2,
          f"Beim Radizieren wird die Hochzahl halbiert: √({v}²) = {v}. "
          f"Probe: ({k}{v}²)² wäre {k*k}{v}⁴."),
        F("zahl_nicht_radiziert", k * k * v,
          f"Auch die Zahl steht unter der Wurzel: √{k*k} = {k}, nicht {k*k}."),
        F("zahl_halbiert", Rational(k * k, 2) * v,
          f"Die Wurzel halbiert nicht. Gesucht ist die Zahl mit {k} · {k} = {k*k}."),
    ], [("Radikand als Produkt", f"{k*k}{v}² = {k*k} · {v}²"),
        ("Zahl radizieren", f"√{k*k} = {k}"),
        ("Hochzahl halbieren", f"√({v}²) = {v}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_1 = Bauform("BF1", "Zahl mal Variablenquadrat",
    bereiche={"A": {"k": Zb(2, 3), "var": EINE},
              "B": {"k": Zb(5, 6), "var": EINE},
              "C": {"k": Zb(11, 12), "var": EINE}},
    bauen=bf29_1, filter=STD)


def bf29_2(p):
    k, v1, v2 = p["k"], p["var"], p["var2"]
    loesung = k * v1 * v2
    return bau(W(f"{k*k if k != 1 else ''}{var(v1,2)}{var(v2,2)}"), loesung, [
        F("nur_eine", k * v1 * v2 ** 2,
          f"Jede Hochzahl wird einzeln halbiert: aus {v2}² wird {v2}."),
        F("zahl_nicht_radiziert", k * k * v1 * v2,
          f"√{k*k} = {k}, nicht {k*k}."),
    ], [("Aufteilen", f"√{k*k} · √({v1}²) · √({v2}²)"),
        ("Einzeln radizieren", f"{k}, {v1}, {v2}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_2 = Bauform("BF2", "Zwei Variablen",
    bereiche={"A": {"k": Zb(1), "var": EINE, "var2": ZWEI},
              "B": {"k": Zb(3), "var": EINE, "var2": ZWEI},
              "C": {"k": Zb(4, 5), "var": EINE, "var2": ZWEI}},
    bauen=bf29_2, filter=STD + [symbole_verschieden("var", "var2")])


def bf29_3(p):
    v, e = p["var"], p["e"]
    loesung = v ** (e // 2)
    return bau(W(var(v, e)), loesung, [
        F("hochzahl_behalten", v ** e,
          f"Beim Radizieren wird die Hochzahl halbiert: {e} : 2 = {e//2}."),
        F("zwei_abgezogen", v ** (e - 2),
          "Die Hochzahl wird halbiert, nicht um zwei verringert."),
    ], [("Hochzahl halbieren", f"{e} : 2 = {e//2}"),
        ("Ergebnis", zeige(loesung))], TIPPS_29)


BF29_3 = Bauform("BF3", "Nur eine Variable mit höherer Potenz",
    bereiche={"A": {"var": EINE, "e": Zb(4)},
              "B": {"var": EINE, "e": Zb(6)},
              "C": {"var": EINE, "e": Zb(8, 10)}},
    bauen=bf29_3, filter=STD)


def bf29_4(p):
    v1, v2, e1, e2 = p["var"], p["var2"], p["e1"], p["e2"]
    loesung = v1 ** (e1 // 2) * v2 ** (e2 // 2)
    return bau(W(f"{var(v1,e1)}{var(v2,e2)}"), loesung, [
        F("nur_eine", v1 ** (e1 // 2) * v2 ** e2,
          f"Jede Hochzahl wird einzeln halbiert: aus {v2}{HOCH.get(e2,'')} "
          f"wird {v2}{HOCH.get(e2//2,'')}."),
        F("addiert", v1 ** e1 * v2 ** e2,
          "Die Wurzel halbiert die Hochzahlen — sie lässt sie nicht stehen."),
    ], [("Aufteilen", f"√({v1}{HOCH.get(e1,'')}) · √({v2}{HOCH.get(e2,'')})"),
        ("Hochzahlen halbieren", f"{e1}:2 = {e1//2},  {e2}:2 = {e2//2}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_4 = Bauform("BF4", "Zwei Variablen mit verschiedenen Hochzahlen",
    bereiche={"A": {"var": EINE, "var2": ZWEI, "e1": Zb(2), "e2": Zb(4)},
              "B": {"var": EINE, "var2": ZWEI, "e1": Zb(4), "e2": Zb(2)},
              "C": {"var": EINE, "var2": ZWEI, "e1": Zb(6), "e2": Zb(4)}},
    bauen=bf29_4, filter=STD + [symbole_verschieden("var", "var2")])


def bf29_5(p):
    k, v, e = p["k"], p["var"], p["e"]
    loesung = k * v ** (e // 2)
    return bau(W(f"{k*k}{var(v, e)}"), loesung, [
        F("hochzahl_behalten", k * v ** e,
          f"Die Hochzahl wird halbiert: {e} : 2 = {e//2}."),
        F("zahl_nicht_radiziert", k * k * v ** (e // 2),
          f"Auch die Zahl wird radiziert: √{k*k} = {k}."),
    ], [("Aufteilen", f"√{k*k} · √({v}{HOCH.get(e,'')})"),
        ("Zahl radizieren", f"√{k*k} = {k}"),
        ("Hochzahl halbieren", f"{e} : 2 = {e//2}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_5 = Bauform("BF5", "Zahl und höhere Potenz",
    bereiche={"A": {"k": Zb(2), "var": EINE, "e": Zb(4)},
              "B": {"k": Zb(7), "var": EINE, "e": Zb(6)},
              "C": {"k": Zb(9), "var": EINE, "e": Zb(8)}},
    bauen=bf29_5, filter=STD)


def bf29_6(p):
    k, v1, v2 = p["k"], p["var"], p["var2"]
    loesung = k * v1 * v2
    frage = f"{W(var(v1,2))} · {W(f'{k*k}{var(v2,2)}')}"
    return bau(frage, loesung, [
        F("nur_erster", v1 * v2,
          f"Die Zahl unter der zweiten Wurzel gehört dazu: √{k*k} = {k}."),
        F("zahl_nicht_radiziert", k * k * v1 * v2,
          f"√{k*k} = {k}, nicht {k*k}."),
    ], [("Jede Wurzel einzeln", f"√({v1}²) = {v1}"),
        ("Zweite Wurzel", f"√({k*k}{v2}²) = {k}{v2}"),
        ("Multiplizieren", zeige(loesung))], TIPPS_29)


BF29_6 = Bauform("BF6", "Das Produkt in einzelne Wurzeln zerlegt",
    bereiche={"A": {"k": Zb(2), "var": EINE, "var2": ZWEI},
              "B": {"k": Zb(3), "var": EINE, "var2": ZWEI},
              "C": {"k": Zb(4, 5), "var": EINE, "var2": ZWEI}},
    bauen=bf29_6, filter=STD + [symbole_verschieden("var", "var2")])


def bf29_7(p):
    v1, v2 = p["var"], p["var2"]
    anzahl = p["anzahl"]
    if anzahl == 1:
        loesung = v1
        frage = W(var(v1, 2))
    else:
        loesung = v1 * v2
        frage = W(f"{var(v1,2)}{var(v2,2)}")
    return bau(frage, loesung, [
        F("hochzahl_behalten", loesung ** 2,
          "Beim Radizieren wird jede Hochzahl halbiert."),
    ], [("Hochzahl halbieren", "aus ² wird ¹"),
        ("Ergebnis", zeige(loesung))], TIPPS_29)


BF29_7 = Bauform("BF7", "Sonderfall: kein Koeffizient",
    bereiche={"A": {"var": EINE, "var2": ZWEI, "anzahl": Zb(1)},
              "B": {"var": EINE, "var2": ZWEI, "anzahl": Zb(1)},
              "C": {"var": EINE, "var2": ZWEI, "anzahl": Zb(2)}},
    bauen=bf29_7, filter=[fehler_eindeutig, symbole_verschieden("var", "var2")])


def bf29_8(p):
    v = p["var"]
    return bau(W(f"0 · {var(v, 2)}"), Integer(0), [
        F("null_ignoriert", v, "Null mal irgendetwas ist null, und √0 = 0."),
    ], [("Radikand ausrechnen", f"0 · {v}² = 0"),
        ("Wurzel ziehen", "√0 = 0")], TIPPS_29)


BF29_8 = Bauform("BF8", "Sonderfall: der Radikand ist null",
    bereiche={"A": {"var": EINE}, "B": {"var": EINE}, "C": {"var": EINE}},
    bauen=bf29_8, filter=[fehler_eindeutig])


def bf29_9(p):
    zr, nr, v = p["zr"], p["nr"], p["var"]
    loesung = Rational(zr, nr) * v
    return bau(W(f"({zr*zr}/{nr*nr}){var(v, 2)}"), loesung, [
        F("nur_zaehler", Rational(zr, nr * nr) * v,
          f"Auch der Nenner wird radiziert: √{nr*nr} = {nr}."),
        F("hochzahl_behalten", Rational(zr, nr) * v ** 2,
          "Die Hochzahl der Variablen wird halbiert."),
    ], [("Bruch radizieren", f"√({zr*zr}/{nr*nr}) = {zr}/{nr}"),
        ("Variable radizieren", f"√({v}²) = {v}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_9 = Bauform("BF9", "Bruch als Koeffizient",
    bereiche={"A": {"zr": Zb(1), "nr": Zb(2), "var": EINE},
              "B": {"zr": Zb(3), "nr": Zb(4), "var": EINE},
              "C": {"zr": Zb(5), "nr": Zb(7), "var": EINE}},
    bauen=bf29_9, filter=STD)


def bf29_10(p):
    basis, e, v = p["basis"], p["e"], p["var"]
    loesung = basis ** (e // 2) * v
    return bau(W(f"{pot(basis, e)}{var(v, 2)}"), loesung, [
        F("basis_behalten", basis ** e * v,
          f"Auch die Zahlenpotenz wird radiziert: die Hochzahl {e} wird zu {e//2}."),
        F("hochzahl_behalten", basis ** (e // 2) * v ** 2,
          "Die Hochzahl der Variablen wird ebenfalls halbiert."),
    ], [("Zahlenpotenz radizieren",
         f"√({basis}{HOCH.get(e,'')}) = {basis}{HOCH.get(e//2,'')} = {basis**(e//2)}"),
        ("Variable radizieren", f"√({v}²) = {v}"),
        ("Zusammensetzen", zeige(loesung))], TIPPS_29)


BF29_10 = Bauform("BF10", "Zahl als Potenz geschrieben",
    bereiche={"A": {"basis": Zb(2), "e": Zb(2), "var": EINE},
              "B": {"basis": Zb(3), "e": Zb(4), "var": EINE},
              "C": {"basis": Zb(2), "e": Zb(6), "var": EINE}},
    bauen=bf29_10, filter=STD)


def bf29_11(p):
    k, v, zusatz = p["k"], p["var"], p["zusatz"]
    loesung = (k + zusatz) * v
    frage = f"{W(f'{k*k}{var(v,2)}')} + {zusatz if zusatz != 1 else ''}{v}"
    return bau(frage, loesung, [
        F("zusatz_vergessen", k * v,
          "Der Summand nach der Wurzel gehört noch dazu."),
        F("zahl_nicht_radiziert", (k * k + zusatz) * v,
          f"√{k*k} = {k}, nicht {k*k}."),
    ], [("Wurzel ziehen", f"√({k*k}{v}²) = {k}{v}"),
        ("Gleichartige Terme zusammenfassen",
         f"{k}{v} + {zusatz}{v} = {zeige(loesung)}")], TIPPS_29)


BF29_11 = Bauform("BF11", "Nach der Wurzel kommt noch eine Rechnung",
    bereiche={"A": {"k": Zb(5), "var": EINE, "zusatz": Zb(1, 2)},
              "B": {"k": Zb(3, 4), "var": EINE, "zusatz": Zb(2, 3)},
              "C": {"k": Zb(6, 7), "var": EINE, "zusatz": Zb(3, 4)}},
    bauen=bf29_11, filter=STD)


def bf29_12(p):
    k, v, e = p["k"], p["var"], p["e"]
    loesung = (k * v) ** (e // 2)
    return bau(W(f"({k}{v}){HOCH[e]}"), loesung, [
        F("zahl_vergessen", v ** (e // 2),
          f"Die Klammer gilt für beides — auch die {k} steht unter der "
          f"Wurzel: √(({k}{v}){HOCH[e]}) = {zeige(loesung)}."),
        F("hochzahl_behalten", (k * v) ** e,
          f"Die Hochzahl wird halbiert: {e} : 2 = {e//2}."),
    ], [("Klammer als Ganzes sehen", f"({k}{v}){HOCH[e]}"),
        ("Hochzahl halbieren", f"{e} : 2 = {e//2}"),
        ("Ergebnis", zeige(loesung))], TIPPS_29)


BF29_12 = Bauform("BF12", "Ganzes Produkt ist bereits eine Potenz",
    bereiche={"A": {"k": Zb(3), "var": EINE, "e": Zb(2)},
              "B": {"k": Zb(5), "var": EINE, "e": Zb(2)},
              "C": {"k": Zb(2), "var": EINE, "e": Zb(4)}},
    bauen=bf29_12, filter=STD)


S29 = Schablone(
    nr="S29", titel="Wurzel aus Produkt mit Variable",
    lektionen="8.9", erhebung="3e",
    anleitung="Rechne aus.",
    levelachse="Anzahl Variablen und Höhe der Potenzen",
    bauformen=[BF29_1, BF29_2, BF29_3, BF29_4, BF29_5, BF29_6,
               BF29_7, BF29_8, BF29_9, BF29_10, BF29_11, BF29_12],
    kernidee=("√(a · b) = √a · √b. Deshalb wird bei √(25a²) die Zahl "
              "radiziert und die Hochzahl der Variablen halbiert."),
)
