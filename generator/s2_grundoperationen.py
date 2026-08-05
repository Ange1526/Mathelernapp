# -*- coding: utf-8 -*-
"""
ABGELOEST. Diese Schablone haengt an keiner Lektion mehr: S20 und S21
haben Kapitel 6 uebernommen, S30 bis S32 die Division in Kapitel 9.
Grund: die Levelachse war numerisch — A, B und C hatten denselben
Aufbau und nur groessere Zahlen.

Die Datei bleibt zum Vergleichen liegen und ist in `anbindung.py`
und `netz.py` nicht mehr eingetragen.

Erhebungsaufgabe 2 · Grundoperationen    (Lektionen 6.1–6.7, 10.12–10.15, 9.4–9.6)

    «Vereinfache so viel wie möglich.»
    2a) 5b − 5b · 2c + 3bc
    2b) 11w − 2 · (5w + 4u)
    2c) 12ab + 21a²b² : (7ab) + 24a²/(3a) − a · (2 − 5b)

Zielform ist ZUSAMMENGEFASST — «vereinfache so weit wie möglich». Anders als
beim Faktorisieren ändern hier die typischen Fehler den Wert, der
Fehlerkatalog trägt also.

Alle Symbole aus symbole(), nicht aus symbols().
"""
from __future__ import annotations

from sympy import expand

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (STANDARD, alle_sorten_bleiben, fehler_eindeutig,
                        kopfrechenbar, loesung_nicht_null,
                        parameter_verschieden, symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, c, d, m, n, p, q, r, s, u, v, w, x, y, z = symbole(
    "a b c d m n p q r s u v w x y z")

VARS = {"a", "b", "c", "d", "m", "n", "p", "q", "r", "s", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Vereinfache so viel wie möglich."

EINVAR = [b, w, x, a, u, m]
ZWEIVAR = [c, u, y, b, v, n]


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


def bau(anzeige_text, loesung, fehler, schritte, tipps, loesung_text=None,
        sorten=None):
    return {
        "frage": anzeige_text,
        "loesung_text": loesung_text or zeige(loesung),
        "sorten": sorten or [],
        "aufgabe": Aufgabe(
            loesung=Loesung.zahl(loesung),
            variablen=VARS,
            zielform=Zielform.ZUSAMMENGEFASST,
            fehlerkatalog=fehler,
        ),
        "schritte": schritte,
        "tipps": tipps,
    }


def Zb(*w):
    return list(w)


# --- BF1 · Produkt in der Mitte      5b − 5b·2c + 3bc   (Erhebung 2a) -------

def bf1(p_):
    k1, k2, k3, v1, v2 = p_["k1"], p_["k2"], p_["k3"], p_["var"], p_["var2"]
    produkt = k1 * k2                      # k1·v1 · k2·v2  ->  k1k2·v1v2
    loesung = k1 * v1 - produkt * v1 * v2 + k3 * v1 * v2
    anzeige = (f"{zeige(k1 * v1)} {MINUS} {zeige(k1 * v1)} · {zeige(k2 * v2)} "
               f"+ {zeige(k3 * v1 * v2)}")
    return bau(anzeige, loesung, [
        F("punkt_vor_strich", (k1 * v1 - k1 * v1) * k2 * v2 + k3 * v1 * v2,
          "Punkt vor Strich: zuerst das Produkt ausrechnen, dann subtrahieren."),
        F("vorzeichen", k1 * v1 - produkt * v1 * v2 - k3 * v1 * v2,
          f"Das letzte Glied wird addiert, nicht subtrahiert."),
        F("minus_verloren", k1 * v1 + produkt * v1 * v2 + k3 * v1 * v2,
          "Das Minus vor dem Produkt ist verlorengegangen."),
        F("alles_zusammen", k1 * v1 * (1 - produkt * v2 + k3 * v2) * 0
          + (k1 - produkt + k3) * v1 * v2,
          f"{zeige(k1 * v1)} hat kein {zeige(v2)} und gehört nicht zu den "
          f"anderen Gliedern."),
    ], schritte=[
        ("Das Produkt markieren", f"{zeige(k1 * v1)} · {zeige(k2 * v2)}"),
        ("Produkt ausrechnen", f"= {zeige(produkt * v1 * v2)}"),
        ("Term neu hinschreiben",
         zeige_summe(k1 * v1, -produkt * v1 * v2, k3 * v1 * v2)),
        ("Gleichartige Glieder zusammenfassen",
         f"{zeige(-produkt * v1 * v2)} und {zeige(k3 * v1 * v2)} gehören zusammen"),
        ("Ergebnis", zeige(loesung)),
    ], loesung_text=zeige_summe(k1 * v1, (k3 - produkt) * v1 * v2), sorten=[v1, v2], tipps=[
        "Punkt vor Strich gilt auch mit Variablen: erst multiplizieren, dann addieren.",
        "Rechne zuerst nur das Produkt aus und schreib den Term neu hin. "
        "Erst danach prüfst du, welche Glieder gleichartig sind.",
        f"{zeige(k1 * v1)} · {zeige(k2 * v2)} ergibt {zeige(produkt * v1 * v2)}.",
    ])


BF1 = Bauform("BF1", "Produkt in der Mitte, gleichartiges Glied dahinter",
    bereiche={"A": {"k1": Zb(2, 3, 5), "k2": Zb(2, 3), "k3": Zb(2, 3, 4),
                    "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k1": Zb(4, 5, 7), "k2": Zb(2, 3, 4), "k3": Zb(3, 5, 6),
                    "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k1": Zb(5, 7, 9), "k2": Zb(3, 4, 5), "k3": Zb(4, 6, 8),
                    "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf1, filter=STANDARD + [loesung_nicht_null, alle_sorten_bleiben,
                                  symbole_verschieden("var", "var2")])


# --- BF2 · Negativer Faktor mal Klammer   11w − 2(5w + 4u)  (Erhebung 2b) ---

def bf2(p_):
    k, f_, g_, h_, v1, v2 = p_["k"], p_["f"], p_["g"], p_["h"], p_["var"], p_["var2"]
    loesung = k * v1 - f_ * (g_ * v1 + h_ * v2)
    anzeige = f"{zeige(k * v1)} {MINUS} {f_} · ({zeige_summe(g_ * v1, h_ * v2)})"
    return bau(anzeige, loesung, [
        F("nur_erster", k * v1 - f_ * g_ * v1 + h_ * v2,
          f"Die {MINUS}{f_} gilt für beide Summanden der Klammer."),
        F("vorzeichen", k * v1 - f_ * g_ * v1 + f_ * h_ * v2,
          f"{MINUS}{f_} · {zeige(h_ * v2)} ergibt {zeige(-f_ * h_ * v2)}."),
        F("klammer_ignoriert", k * v1 - f_ + g_ * v1 + h_ * v2,
          "Der Faktor gehört zur ganzen Klammer, nicht nur zur ersten Zahl."),
    ], schritte=[
        ("Faktor bestimmen — mitsamt Vorzeichen", f"der Faktor ist {MINUS}{f_}"),
        ("Faktor mal erstes Glied", f"{MINUS}{f_} · {zeige(g_ * v1)} = {zeige(-f_ * g_ * v1)}"),
        ("Faktor mal zweites Glied", f"{MINUS}{f_} · {zeige(h_ * v2)} = {zeige(-f_ * h_ * v2)}"),
        ("Alles hinschreiben", zeige_summe(k * v1, -f_ * g_ * v1, -f_ * h_ * v2)),
        ("Gleichartige zusammenfassen", zeige(loesung)),
    ], loesung_text=zeige_summe((k - f_ * g_) * v1, -f_ * h_ * v2), sorten=[v1, v2], tipps=[
        "Ein negativer Faktor dreht jedes Vorzeichen in der Klammer um – auch das zweite.",
        "Nimm das Minus zum Faktor dazu und multipliziere damit jedes Glied einzeln.",
        f"Der Faktor ist {MINUS}{f_}. Damit ergibt sich {zeige(-f_ * g_ * v1)} "
        f"und {zeige(-f_ * h_ * v2)}.",
    ])


BF2 = Bauform("BF2", "Negativer Faktor mal Klammer",
    bereiche={"A": {"k": Zb(7, 9, 11), "f": Zb(2, 3), "g": Zb(2, 3), "h": Zb(2, 4),
                    "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k": Zb(11, 13, 15), "f": Zb(2, 3, 4), "g": Zb(3, 5), "h": Zb(3, 4, 5),
                    "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k": Zb(15, 17, 20), "f": Zb(3, 4, 5), "g": Zb(4, 5, 6), "h": Zb(4, 6, 7),
                    "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf2, filter=STANDARD + [loesung_nicht_null, alle_sorten_bleiben,
                                  symbole_verschieden("var", "var2"),
                                  parameter_verschieden("g", "h")])


# --- BF3 · Division von Monomen      21a²b² : (7ab) ------------------------

def bf3(p_):
    k1, k2, v1, v2 = p_["k1"], p_["k2"], p_["var"], p_["var2"]
    k3 = p_["k3"]
    zaehler = k1 * k2 * v1**2 * v2**2
    nenner = k2 * v1 * v2
    quotient = k1 * v1 * v2
    loesung = k3 * v1 * v2 + quotient
    anzeige = (f"{zeige(k3 * v1 * v2)} + {zeige(zaehler)} : ({zeige(nenner)})")
    return bau(anzeige, loesung, [
        F("hochzahl", k3 * v1 * v2 + k1 * v1**2 * v2**2,
          f"Beim Dividieren werden die Hochzahlen subtrahiert: {zeige(v1**2)} : "
          f"{zeige(v1)} = {zeige(v1)}."),
        F("ganze_summe", (k3 * v1 * v2 + zaehler) / nenner,
          "Ohne Klammer gilt die Division nur für das Glied direkt davor."),
        F("nicht_gekuerzt", k3 * v1 * v2 + k1 * k2 * v1 * v2,
          f"Die Zahlen werden ebenfalls geteilt: {k1 * k2} : {k2} = {k1}."),
    ], schritte=[
        ("Prüfen: was genau wird geteilt?", f"nur {zeige(zaehler)}, nicht die ganze Summe"),
        ("Zahlen dividieren", f"{k1 * k2} : {k2} = {k1}"),
        ("Für jede Variable die Hochzahlen subtrahieren",
         f"{zeige(v1**2)} : {zeige(v1)} = {zeige(v1)}"),
        ("Quotient", zeige(quotient)),
        ("Gleichartige zusammenfassen", zeige(loesung)),
    ], loesung_text=zeige((k3 + k1) * v1 * v2), sorten=[v1, v2], tipps=[
        "Eine Division ist eine Punktoperation und bindet stärker als Plus und Minus.",
        "Schau genau, was geteilt wird: nur das Glied direkt vor dem Doppelpunkt.",
        f"{zeige(zaehler)} : ({zeige(nenner)}) ergibt {zeige(quotient)}.",
    ])


BF3 = Bauform("BF3", "Division von Monomen in einem längeren Term",
    bereiche={"A": {"k1": Zb(2, 3), "k2": Zb(2, 3), "k3": Zb(2, 4), "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k1": Zb(3, 4, 5), "k2": Zb(3, 5, 7), "k3": Zb(3, 6, 9), "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k1": Zb(4, 6, 7), "k2": Zb(5, 7, 8), "k3": Zb(5, 8, 12), "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf3, filter=STANDARD + [loesung_nicht_null, alle_sorten_bleiben,
                                  symbole_verschieden("var", "var2")])


# --- BF4 · Zwei Sorten bleiben nebeneinander stehen ------------------------

def bf4(p_):
    k1, k2, k3, v1, v2 = p_["k1"], p_["k2"], p_["k3"], p_["var"], p_["var2"]
    loesung = k1 * v1 * v2 + (k2 - k3) * v1
    anzeige = f"{zeige(k1 * v1)} · {zeige(v2)} + {zeige(k2 * v1)} {MINUS} {zeige(k3 * v1)}"
    return bau(anzeige, loesung, [
        F("alles_zusammen", (k1 + k2 - k3) * v1 * v2,
          f"{zeige(k1 * v1 * v2)} und {zeige((k2 - k3) * v1)} sind verschiedene "
          f"Sorten – das eine hat ein {zeige(v2)}, das andere nicht."),
        F("vorzeichen", k1 * v1 * v2 + (k2 + k3) * v1,
          f"{zeige(k3 * v1)} wird abgezogen, nicht addiert."),
    ], schritte=[
        ("Produkt ausrechnen", f"{zeige(k1 * v1)} · {zeige(v2)} = {zeige(k1 * v1 * v2)}"),
        ("Sorten bestimmen", f"{zeige(v1 * v2)}-Glieder und {zeige(v1)}-Glieder"),
        ("Innerhalb jeder Sorte rechnen", f"{k2} {MINUS} {k3} = {k2 - k3}"),
        ("Verschiedene Sorten bleiben nebeneinander", zeige_summe(k1 * v1 * v2, (k2 - k3) * v1)),
    ], loesung_text=zeige_summe(k1 * v1 * v2, (k2 - k3) * v1), sorten=[v1, v2], tipps=[
        "Nur Glieder mit genau denselben Variablen lassen sich zusammenfassen.",
        "Rechne erst das Produkt aus, dann sortiere nach Sorten.",
        f"{zeige(k1 * v1 * v2)} und {zeige(k2 * v1)} sind verschiedene Sorten.",
    ])


BF4 = Bauform("BF4", "Zwei Sorten bleiben nebeneinander stehen",
    bereiche={"A": {"k1": Zb(2, 3), "k2": Zb(4, 5, 6), "k3": Zb(1, 2), "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k1": Zb(3, 4, 5), "k2": Zb(6, 7, 9), "k3": Zb(2, 3, 4), "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k1": Zb(4, 6, 7), "k2": Zb(8, 9, 11), "k3": Zb(3, 5, 6), "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf4, filter=STANDARD + [loesung_nicht_null, alle_sorten_bleiben,
                                  symbole_verschieden("var", "var2"),
                                  parameter_verschieden("k2", "k3")])


# --- BF5 · Bruchschreibweise      24a² / (3a) ------------------------------

def bf5(p_):
    k1, k2, k3, v1 = p_["k1"], p_["k2"], p_["k3"], p_["var"]
    zaehler = k1 * k2 * v1**2
    nenner = k2 * v1
    quotient = k1 * v1
    loesung = (k3 + k1) * v1
    anzeige = f"{zeige(k3 * v1)} + {zeige(zaehler)}/({zeige(nenner)})"
    return bau(anzeige, loesung, [
        F("hochzahl", k3 * v1 + k1 * v1**2,
          f"{zeige(v1**2)} geteilt durch {zeige(v1)} ergibt {zeige(v1)}, "
          f"nicht {zeige(v1**2)}."),
        F("nur_zahl", k3 * v1 + k1 * k2 * v1,
          f"Auch die Zahlen werden geteilt: {k1 * k2} : {k2} = {k1}."),
        F("variable_weg", k3 * v1 + k1,
          f"Oben steht {zeige(v1**2)}, unten {zeige(v1)}. Es bleibt ein "
          f"{zeige(v1)} übrig."),
    ], schritte=[
        ("Zahlen kürzen", f"{k1 * k2} : {k2} = {k1}"),
        ("Hochzahlen subtrahieren", f"{zeige(v1**2)} : {zeige(v1)} = {zeige(v1)}"),
        ("Quotient", zeige(quotient)),
        ("Gleichartige zusammenfassen", f"{zeige(k3 * v1)} + {zeige(quotient)} = {zeige(loesung)}"),
    ], loesung_text=zeige(loesung), sorten=[v1], tipps=[
        "Ein Bruchstrich ist dasselbe wie ein Geteiltzeichen.",
        "Kürze die Zahlen und die Variablen getrennt.",
        f"{zeige(zaehler)} geteilt durch {zeige(nenner)} ergibt {zeige(quotient)}.",
    ])


BF5 = Bauform("BF5", "Division in Bruchschreibweise",
    bereiche={"A": {"k1": Zb(2, 3, 4), "k2": Zb(2, 3), "k3": Zb(2, 5), "var": EINVAR},
              "B": {"k1": Zb(4, 6, 8), "k2": Zb(3, 4, 5), "k3": Zb(3, 7, 9), "var": EINVAR},
              "C": {"k1": Zb(6, 8, 9), "k2": Zb(4, 5, 7), "k3": Zb(5, 8, 11), "var": EINVAR}},
    bauen=bf5, filter=STANDARD + [loesung_nicht_null])


# --- BF6 · Alles zusammen        die volle Erhebungsaufgabe 2c -------------

def bf6(p_):
    k1, k2, k3, k4, v1, v2 = (p_["k1"], p_["k2"], p_["k3"], p_["k4"],
                              p_["var"], p_["var2"])
    # k1·v1v2  +  k2k3·v1²v2² : (k3·v1v2)  +  k4k3·v1² / (k3·v1)  −  v1·(2 − k2·v2)
    quotient1 = k2 * v1 * v2
    quotient2 = k4 * v1
    klammerteil = 2 * v1 - k2 * v1 * v2
    loesung = k1 * v1 * v2 + quotient1 + quotient2 - klammerteil
    anzeige = (f"{zeige(k1 * v1 * v2)} + {zeige(k2 * k3 * v1**2 * v2**2)} : "
               f"({zeige(k3 * v1 * v2)}) + {zeige(k4 * k3 * v1**2)}/({zeige(k3 * v1)}) "
               f"{MINUS} {zeige(v1)} · ({zeige_summe(2, -k2 * v2)})")
    return bau(anzeige, loesung, [
        F("klammer_vorzeichen", k1 * v1 * v2 + quotient1 + quotient2 - 2 * v1 - k2 * v1 * v2,
          f"{MINUS}{zeige(v1)} · ({MINUS}{zeige(k2 * v2)}) ergibt "
          f"+{zeige(k2 * v1 * v2)}."),
        F("bruch_hochzahl", k1 * v1 * v2 + quotient1 + k4 * v1**2 - klammerteil,
          f"{zeige(k4 * k3 * v1**2)} geteilt durch {zeige(k3 * v1)} kürzt zu "
          f"{zeige(quotient2)}, nicht zu {zeige(k4 * v1**2)}."),
        F("division_zu_weit", (k1 * v1 * v2 + k2 * k3 * v1**2 * v2**2) / (k3 * v1 * v2)
          + quotient2 - klammerteil,
          "Die Division gilt nur für das Glied direkt davor."),
    ], schritte=[
        ("Erste Division", f"{zeige(k2 * k3 * v1**2 * v2**2)} : ({zeige(k3 * v1 * v2)}) = {zeige(quotient1)}"),
        ("Zweite Division", f"{zeige(k4 * k3 * v1**2)} : ({zeige(k3 * v1)}) = {zeige(quotient2)}"),
        ("Klammer ausmultiplizieren",
         f"{MINUS}{zeige(v1)} · ({zeige_summe(2, -k2 * v2)}) = {zeige_summe(-2 * v1, k2 * v1 * v2)}"),
        ("Alles hinschreiben",
         zeige_summe(k1 * v1 * v2, quotient1, quotient2, -2 * v1, k2 * v1 * v2)),
        ("Nach Sorten zusammenfassen", zeige_summe((k1 + 2 * k2) * v1 * v2, (k4 - 2) * v1)),
    ], loesung_text=zeige_summe((k1 + 2 * k2) * v1 * v2, (k4 - 2) * v1),
       sorten=[v1, v2], tipps=[
        "Punkt vor Strich: erst alle Divisionen und Produkte, dann zusammenfassen.",
        "Geh Glied für Glied vor und schreib den Term nach jedem Schritt neu hin.",
        f"Die erste Division ergibt {zeige(quotient1)}, die zweite {zeige(quotient2)}.",
    ])


BF6 = Bauform("BF6", "Alles zusammen — die volle Erhebungsform",
    bereiche={"B": {"k1": Zb(6, 12), "k2": Zb(2, 3), "k3": Zb(5, 7), "k4": Zb(6, 8),
                    "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k1": Zb(12, 15, 18), "k2": Zb(3, 4, 5), "k3": Zb(7, 9), "k4": Zb(8, 10, 12),
                    "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf6, filter=STANDARD + [loesung_nicht_null, alle_sorten_bleiben,
                                  symbole_verschieden("var", "var2")],
    levels=("B", "C"))


# --- BF7 · Sonderfall: eine Sorte fällt ganz weg ---------------------------

def bf7(p_):
    k, f_, v1, v2 = p_["k"], p_["f"], p_["var"], p_["var2"]
    g_ = k // f_                       # so gewählt, dass sich v1 aufhebt
    h_ = p_["h"]
    loesung = -f_ * h_ * v2
    anzeige = f"{zeige(k * v1)} {MINUS} {f_} · ({zeige_summe(g_ * v1, h_ * v2)})"
    return bau(anzeige, loesung, [
        F("sorte_geblieben", k * v1 - f_ * h_ * v2,
          f"Die {zeige(v1)}-Glieder heben sich auf: {zeige(k * v1)} {MINUS} "
          f"{zeige(f_ * g_ * v1)} = 0."),
        F("vorzeichen", f_ * h_ * v2,
          f"{MINUS}{f_} · {zeige(h_ * v2)} ergibt {zeige(-f_ * h_ * v2)}."),
    ], schritte=[
        ("Klammer ausmultiplizieren", zeige_summe(-f_ * g_ * v1, -f_ * h_ * v2)),
        ("Alles hinschreiben", zeige_summe(k * v1, -f_ * g_ * v1, -f_ * h_ * v2)),
        (f"Die {zeige(v1)}-Glieder zusammenfassen", f"{k} {MINUS} {f_ * g_} = 0"),
        ("Übrig bleibt nur eine Sorte", zeige(loesung)),
    ], loesung_text=zeige(loesung), sorten=[v2], tipps=[
        "Multipliziere zuerst die Klammer aus, dann sortiere nach Sorten.",
        "Rechne die Sorten einzeln zusammen – manchmal bleibt von einer nichts übrig.",
        f"{zeige(k * v1)} {MINUS} {zeige(f_ * g_ * v1)} ergibt null.",
    ])


BF7 = Bauform("BF7", "Sonderfall: eine Sorte fällt ganz weg",
    bereiche={"A": {"k": Zb(6, 8, 10), "f": Zb(2), "h": Zb(2, 3, 4), "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k": Zb(9, 12, 15), "f": Zb(3), "h": Zb(3, 4, 5), "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k": Zb(16, 20, 24), "f": Zb(4), "h": Zb(4, 5, 7), "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf7, filter=STANDARD + [loesung_nicht_null, symbole_verschieden("var", "var2")])


# --- BF8 · Sonderfall: nichts lässt sich zusammenfassen --------------------

def bf8(p_):
    k1, k2, v1, v2 = p_["k1"], p_["k2"], p_["var"], p_["var2"]
    loesung = k1 * v1 + k2 * v2
    anzeige = zeige_summe(k1 * v1, k2 * v2)
    return bau(anzeige, loesung, [
        F("zusammengezogen", (k1 + k2) * v1 * v2,
          f"{zeige(v1)} und {zeige(v2)} sind verschieden und lassen sich nicht "
          f"zusammenzählen. Der Term ist bereits die Antwort."),
        F("nur_zahlen", (k1 + k2) * v1,
          "Verschiedene Variablen bleiben nebeneinander stehen."),
    ], schritte=[
        ("Sorten bestimmen", f"{zeige(v1)}-Glieder und {zeige(v2)}-Glieder"),
        ("Jede Sorte für sich", f"von jeder gibt es nur eines"),
        ("Antwort", f"{anzeige} — hier ist nichts zusammenzufassen"),
    ], loesung_text=anzeige, sorten=[v1, v2], tipps=[
        "Zusammenfassen darf man nur Glieder mit genau derselben Variablen.",
        "Prüfe: haben die Glieder wirklich dieselben Variablen?",
        f"{zeige(v1)} und {zeige(v2)} sind verschieden. Dann ist der Term schon fertig.",
    ])


BF8 = Bauform("BF8", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche={"A": {"k1": Zb(2, 3, 5), "k2": Zb(4, 7), "var": EINVAR, "var2": ZWEIVAR},
              "B": {"k1": Zb(4, 6, 9), "k2": Zb(5, 8, 11), "var": EINVAR, "var2": ZWEIVAR},
              "C": {"k1": Zb(7, 11, 13), "k2": Zb(9, 12, 17), "var": EINVAR, "var2": ZWEIVAR}},
    bauen=bf8, filter=STANDARD + [symbole_verschieden("var", "var2"),
                                  parameter_verschieden("k1", "k2")])


S2 = Schablone(
    nr="S2",
    titel="Grundoperationen",
    lektionen="6.1 – 6.7 · 9.4 – 9.6 · 10.12 – 10.15",
    erhebung="2a · 2b · 2c",
    anleitung=ANLEITUNG,
    levelachse="A: zwei Sorten, kleine Zahlen · B: längere Terme · C: alle Operationen gemischt",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8],
    kernidee=("Punkt vor Strich gilt auch mit Variablen. Erst nach dem "
              "Ausrechnen der Produkte und Quotienten wird geprueft, ob die "
              "Glieder gleichartig sind - oft sind sie es nicht."),
)
