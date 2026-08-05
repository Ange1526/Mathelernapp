# -*- coding: utf-8 -*-
"""
Erhebungsaufgabe 4 · Faktorisieren      (Schablone S42/S43/S44, Lektionen 12.1–12.8)

    «Klammere so viele Faktoren wie möglich aus.»
    4a) 16x + 32        4b) 12a² − 8a
    4c) xy³ − x²y²      4d) 6x − 12xy + 3x²y²

Zwölf Bauformen. Level über Parameterbereiche UND Gliederzahl — nicht über
eigene Schablonen pro Level (siehe LIESMICH, Punkt 3).

WICHTIG: Alle Symbole kommen aus symbole(), nicht aus symbols(). Sonst hebt
sich antwort − lösung nie auf.
"""
from __future__ import annotations

from sympy import expand, factor

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .schablone import Bauform, Schablone
from .qualitaet import (STANDARD, echt_zu_tun, faktor_ist_groesster,
                        fehler_eindeutig, loesung_nicht_null,
                        parameter_verschieden)

a, b, c, d, m, n, p, q, r, s, u, v, w, x, y, z = symbole(
    "a b c d m n p q r s u v w x y z")

VARS = {"a", "b", "c", "d", "m", "n", "p", "q", "r", "s", "u", "v", "w", "x", "y", "z"}

ANLEITUNG = "Klammere so viele Faktoren wie möglich aus."


from .anzeige import MINUS, klammer, zeige, zeige_produkt, zeige_summe


def tipps_ausklammern(faktor) -> list[str]:
    return [
        "Ausklammern heisst: den gemeinsamen Faktor vor die Klammer ziehen. "
        "Er muss in JEDEM Glied stecken.",
        "Zerlege jedes Glied in seine Faktoren und schau, was überall vorkommt. "
        "Bei den Zahlen ist es der grösste gemeinsame Teiler, bei den Variablen "
        "die kleinste vorkommende Hochzahl.",
        f"Der gemeinsame Faktor ist {zeige(faktor)}. Teil jedes Glied dadurch — "
        f"das ergibt die Klammer.",
    ]


def bau(term, faktor, klammer, fehler: list[Fehler], anzeige: str | None = None,
        klammer_text: str | None = None):
    """Baut aus Term, gemeinsamem Faktor und Klammer eine fertige Aufgabe."""
    text = anzeige or zeige(term)
    # Musterlösung in Schülerschreibweise: Faktor mal Klammer, nicht das,
    # was factor() ausspuckt. SymPy schreibt xy³ − x²y² als −xy²(x − y);
    # der Schüler schreibt xy²(y − x), und beides ist richtig.
    loesung_text = f"{zeige(faktor)}({klammer_text or zeige(klammer)})"
    schritte = [
        ("Jedes Glied in Faktoren zerlegen", text),
        ("Suchen, was in ALLEN Gliedern steckt", f"der Faktor {zeige(faktor)}"),
        ("Faktor vor die Klammer, jedes Glied dadurch teilen",
         f"{zeige(faktor)} · ({zeige(klammer)})"),
        ("Rückprobe durch Ausmultiplizieren", f"{zeige(faktor * klammer)} — stimmt"),
    ]
    return {
        "frage": text,
        "loesung_text": loesung_text,
        "klammer": klammer,          # für den Filter faktor_ist_groesster
        "faktor": faktor,
        "aufgabe": Aufgabe(
            loesung=Loesung.zahl(faktor * klammer),
            variablen=VARS,
            zielform=Zielform.FAKTORISIERT,
            fehlerkatalog=fehler,
        ),
        "schritte": schritte,
        "tipps": tipps_ausklammern(faktor),
    }


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(ergebnis), text)


# ================================================================ Bauformen
#
# WICHTIG — beim ersten Testlauf gefunden:
#
# «Nicht der grösste Faktor ausgeklammert» gehört NICHT in den Fehlerkatalog.
# 8(2x+4) und 16(x+2) haben denselben WERT. Ein wertbasierter Vergleich kann
# sie nie unterscheiden. Diesen Fall fängt die Zielform FAKTORISIERT mit
# content_streng=True ab — er kommt als UNFERTIG zurück, nicht als FALSCH.
# Das ist auch didaktisch richtig: der Schüler hat richtig gerechnet.
#
# In den Fehlerkatalog gehören nur Fehler, die den Wert ÄNDERN.
#
# Levelachse: A = zwei Glieder, kleine Zahlen       (Erhebung 4a, 4b)
#             B = zwei Glieder, Potenzen/zwei Vars  (Erhebung 4c)
#             C = drei Glieder                       (Erhebung 4d)

def Zb(*werte):
    return list(werte)


EINVAR = [x, y, a, b, u, m]
ZWEIVAR = [y, z, b, c, v, n]


# --- BF1 · nur eine Zahl ausklammern      16x + 32  (Erhebung 4a) ----------

def bf1(p):
    g, u_, v_, var = p["g"], p["u"], p["v"], p["var"]
    term = g * u_ * var + g * v_
    klammer = u_ * var + v_
    return bau(term, g, klammer, anzeige=zeige_summe(g * u_ * var, g * v_), fehler=[
        F("vorzeichen", g * (u_ * var - v_),
          "In der Klammer bleibt das Vorzeichen so stehen, wie es im Term war."),
        F("nur_erstes", g * (u_ * var + g * v_),
          "Auch das zweite Glied wird durch den gemeinsamen Faktor GETEILT, "
          "nicht unverändert in die Klammer übernommen."),
    ])


BF1 = Bauform("BF1", "Nur eine Zahl ausklammern",
    bereiche={"A": {"g": Zb(2, 3, 4, 5, 8, 16), "u": Zb(1, 2, 3), "v": Zb(2, 3, 5, 7), "var": EINVAR},
              "B": {"g": Zb(3, 6, 7, 9, 12), "u": Zb(2, 3, 4, 5), "v": Zb(3, 5, 7, 11), "var": EINVAR},
              "C": {"g": Zb(6, 9, 12, 15), "u": Zb(3, 4, 5, 7), "v": Zb(5, 7, 11, 13), "var": EINVAR}},
    bauen=bf1, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])


# --- BF2 · nur eine Variable ausklammern       xy + xz ---------------------

def bf2(p):
    var, zwei, u_, v_ = p["var"], p["var2"], p["u"], p["v"]
    term = u_ * var + v_ * var * zwei
    klammer = u_ + v_ * zwei
    return bau(term, var, klammer, anzeige=zeige_summe(u_ * var, v_ * var * zwei), fehler=[
        F("variable_geblieben", var * (u_ * var + v_ * var * zwei),
          f"Nach dem Teilen durch {zeige(var)} bleibt in der Klammer kein {zeige(var)} mehr."),
        F("nur_erstes_geteilt", var * (u_ + v_ * var * zwei),
          f"Auch das zweite Glied wird durch {zeige(var)} geteilt."),
    ])


BF2 = Bauform("BF2", "Nur eine Variable ausklammern",
    bereiche={"A": {"var": EINVAR, "var2": ZWEIVAR, "u": Zb(1, 2, 3), "v": Zb(1, 2, 3)},
              "B": {"var": EINVAR, "var2": ZWEIVAR, "u": Zb(2, 3, 5), "v": Zb(2, 3, 4)},
              "C": {"var": EINVAR, "var2": ZWEIVAR, "u": Zb(3, 5, 7), "v": Zb(3, 4, 6)}},
    bauen=bf2, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])


# --- BF3 · Zahl UND Variable       12a² − 8a  (Erhebung 4b) ----------------

def bf3(p):
    g, var, u_, v_ = p["g"], p["var"], p["u"], p["v"]
    term = g * u_ * var**2 - g * v_ * var
    klammer = u_ * var - v_
    return bau(term, g * var, klammer,
               anzeige=zeige_summe(g * u_ * var**2, -g * v_ * var), fehler=[
        F("vorzeichen", g * var * (u_ * var + v_),
          "In der Klammer bleibt das Minus stehen."),
        F("hochzahl", g * var * (u_ * var**2 - v_),
          f"{zeige(g*u_*var**2)} geteilt durch {zeige(g*var)} ergibt {zeige(u_*var)}, "
          f"nicht {zeige(u_*var**2)}."),
    ])


BF3 = Bauform("BF3", "Zahl und Variable gemeinsam ausklammern",
    bereiche={"A": {"g": Zb(2, 3, 4), "var": EINVAR, "u": Zb(2, 3), "v": Zb(1, 2, 3)},
              "B": {"g": Zb(4, 6, 8), "var": EINVAR, "u": Zb(2, 3, 4), "v": Zb(1, 2, 3, 5)},
              "C": {"g": Zb(6, 8, 12), "var": EINVAR, "u": Zb(3, 4, 5), "v": Zb(2, 3, 5, 7)}},
    bauen=bf3, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])


# --- BF4 · Ein Glied bleibt als Eins stehen        2rs + s ------------------

def bf4(p):
    g, var, zwei, u_ = p["g"], p["var"], p["var2"], p["u"]
    term = g * u_ * var * zwei + g * var
    klammer = u_ * zwei + 1
    return bau(term, g * var, klammer,
               anzeige=zeige_summe(g * u_ * var * zwei, g * var), fehler=[
        F("eins_weggelassen", g * var * (u_ * zwei),
          "Das zweite Glied ergibt beim Teilen 1, nicht nichts. Die 1 gehört in die Klammer."),
        F("vorzeichen", g * var * (u_ * zwei - 1),
          "Beide Glieder werden addiert, also steht in der Klammer ein Plus."),
    ])


BF4 = Bauform("BF4", "Ein Glied bleibt als Eins stehen",
    bereiche={"A": {"g": Zb(1, 2, 3), "var": EINVAR, "var2": ZWEIVAR, "u": Zb(2, 3, 5)},
              "B": {"g": Zb(2, 3, 5), "var": EINVAR, "var2": ZWEIVAR, "u": Zb(3, 4, 7)},
              "C": {"g": Zb(3, 5, 7), "var": EINVAR, "var2": ZWEIVAR, "u": Zb(4, 5, 9)}},
    bauen=bf4, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])


# --- BF5 · Zwei Variablen mit Potenzen     xy³ − x²y²  (Erhebung 4c) --------

def bf5(p):
    v1, v2, e1, e2 = p["var"], p["var2"], p["e1"], p["e2"]
    term = v1 * v2**(e1 + 1) - v1**2 * v2**e1
    faktor = v1 * v2**e1
    klammer = v2 - v1
    return bau(term, faktor, klammer,
               anzeige=zeige_summe(v1 * v2**(e1 + 1), -v1**2 * v2**e1),
               klammer_text=zeige_summe(v2, -v1), fehler=[
        F("hochzahl", faktor * (v2 - v1**2),
          f"{zeige(v1**2 * v2**e1)} geteilt durch {zeige(faktor)} ergibt {zeige(v1)}, "
          f"nicht {zeige(v1**2)}."),
        F("vorzeichen", faktor * (v2 + v1),
          "In der Klammer bleibt das Minus stehen."),
    ])


BF5 = Bauform("BF5", "Zwei Variablen mit Potenzen",
    bereiche={"A": {"var": [x, a], "var2": [y, b], "e1": Zb(1), "e2": Zb(1)},
              "B": {"var": [x, a, u], "var2": [y, b, v], "e1": Zb(1, 2), "e2": Zb(1)},
              "C": {"var": [x, a, u, m], "var2": [y, b, v, n], "e1": Zb(2, 3), "e2": Zb(1)}},
    bauen=bf5, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster])


# --- BF6 · Drei Glieder, Zahl und Variable   6x − 12xy + 3x²y² (Erhebung 4d)

def bf6(p):
    g, v1, v2, u_, w_ = p["g"], p["var"], p["var2"], p["u"], p["w"]
    term = g * u_ * v1 - g * w_ * v1 * v2 + g * v1**2 * v2**2
    faktor = g * v1
    klammer = u_ - w_ * v2 + v1 * v2**2
    return bau(term, faktor, klammer,
               anzeige=zeige_summe(g * u_ * v1, -g * w_ * v1 * v2, g * v1**2 * v2**2),
               fehler=[
        F("zweite_variable", g * v1 * v2 * (u_ - w_ + v1 * v2),
          f"Im ersten Glied {zeige(g*u_*v1)} steckt kein {zeige(v2)}. "
          f"Ausklammern lässt sich nur {zeige(faktor)}."),
        F("vorzeichen", faktor * (u_ + w_ * v2 + v1 * v2**2),
          "Das mittlere Glied wird abgezogen – in der Klammer bleibt das Minus."),
    ])


BF6 = Bauform("BF6", "Drei Glieder, Zahl und Variable",
    bereiche={"B": {"g": Zb(2, 3), "var": [x, a], "var2": [y, b], "u": Zb(2, 3), "w": Zb(3, 4)},
              "C": {"g": Zb(3, 5, 6), "var": [x, a, u], "var2": [y, b, v], "u": Zb(2, 4, 5), "w": Zb(3, 4, 7)}},
    bauen=bf6, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster,
                                  parameter_verschieden("u", "w")],
    levels=("B", "C"))


# --- BF7 · Drei Glieder, nur die Zahl gemeinsam     14f + 21g + 35 ----------

def bf7(p):
    g, v1, v2, u_, w_, t_ = p["g"], p["var"], p["var2"], p["u"], p["w"], p["t"]
    term = g * u_ * v1 + g * w_ * v2 + g * t_
    klammer = u_ * v1 + w_ * v2 + t_
    return bau(term, g, klammer,
               anzeige=zeige_summe(g * u_ * v1, g * w_ * v2, g * t_), fehler=[
        F("variable_ausgeklammert", g * v1 * (u_ + w_ * v2 + t_),
          f"Im letzten Glied {zeige(g*t_)} steckt kein {zeige(v1)}. "
          f"Ausklammern lässt sich nur die {g}."),
        F("letztes_vergessen", g * (u_ * v1 + w_ * v2) + g * t_ * g,
          "Auch das letzte Glied wird durch den Faktor geteilt."),
    ])


BF7 = Bauform("BF7", "Drei Glieder, nur die Zahl gemeinsam",
    bereiche={"B": {"g": Zb(2, 3, 7), "var": [x, a], "var2": [y, b], "u": Zb(2, 3), "w": Zb(3, 4), "t": Zb(5)},
              "C": {"g": Zb(5, 7, 9), "var": [x, a, u], "var2": [y, b, v], "u": Zb(2, 3, 4), "w": Zb(3, 5), "t": Zb(7, 8)}},
    bauen=bf7, filter=STANDARD + [loesung_nicht_null, faktor_ist_groesster],
    levels=("B", "C"))


# --- BF8 · Kein gemeinsamer Faktor — nicht faktorisierbar -------------------

def bf8(p):
    v1, v2, u_, w_, t_ = p["var"], p["var2"], p["u"], p["w"], p["t"]
    term = u_ * v1 + w_ * v2 + t_
    return {
        "frage": zeige_summe(u_ * v1, w_ * v2, t_),
        "loesung_text": zeige_summe(u_ * v1, w_ * v2, t_),
        "klammer": None,
        "aufgabe": Aufgabe(
            loesung=Loesung.zahl(term),        # Antwort = der Term selbst
            variablen=VARS,
            zielform=Zielform.BELIEBIG,        # nichts zu faktorisieren
            fehlerkatalog=[
                F("etwas_ausgeklammert", u_ // 1 * (v1 + w_ * v2 + t_),
                  f"{u_}, {w_} und {t_} haben keinen gemeinsamen Teiler ausser 1. "
                  f"Hier lässt sich nichts ausklammern."),
            ],
        ),
        "schritte": [
            ("Zahlen anschauen", f"{u_}, {w_} und {t_}"),
            ("Grössten gemeinsamen Teiler suchen", "es gibt keinen ausser 1"),
            ("Variablen anschauen", f"{zeige(v1)} und {zeige(v2)} stehen nicht in allen Gliedern"),
            ("Antwort", f"{zeige(term)} — der Term lässt sich nicht faktorisieren"),
        ],
        "tipps": [
            "Ausgeklammert wird nur, was in JEDEM Glied steckt.",
            "Prüfe zuerst die Zahlen: haben sie einen gemeinsamen Teiler? Dann die Variablen.",
            "Hier gibt es weder bei den Zahlen noch bei den Variablen etwas Gemeinsames. "
            "Dann ist der Term schon fertig.",
        ],
    }


BF8 = Bauform("BF8", "Sonderfall: es gibt keinen gemeinsamen Faktor",
    bereiche={"A": {"var": [x, a], "var2": [y, b], "u": Zb(2, 3, 4), "w": Zb(5, 7), "t": Zb(9, 11)},
              "B": {"var": [x, a, u], "var2": [y, b, v], "u": Zb(3, 4, 5), "w": Zb(7, 8), "t": Zb(9, 11, 13)},
              "C": {"var": [x, a, u, m], "var2": [y, b, v, n], "u": Zb(4, 5, 6), "w": Zb(7, 9), "t": Zb(11, 13, 15)}},
    bauen=bf8, filter=[fehler_eindeutig])


# ================================================================ Schablone

S4 = Schablone(
    nr="S4",
    titel="Faktorisieren",
    lektionen="12.1 – 12.8",
    erhebung="4a · 4b · 4c · 4d",
    anleitung="Klammere so viele Faktoren wie möglich aus.",
    levelachse="A: zwei Glieder, kleine Zahlen · B: Potenzen und zwei Variablen · C: drei Glieder",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6, BF7, BF8],
    kernidee=("Ausklammern ist das Umgekehrte des Ausmultiplizierens: der "
              "groesste Faktor, der in JEDEM Glied steckt, kommt vor die "
              "Klammer. Was uebrig bleibt, steht darin."),
)
