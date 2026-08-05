"""
Erhebung Vorkenntnisse Algebra 1m 2025, Kantonsschule Frauenfeld.
Alle 17 Teilaufgaben als Aufgabe-Objekte, je mit Fehlerkatalog.

Zweck: messen, wie oft der Katalog trifft und wie oft "unbekannt" kommt.
Nur "unbekannt" darf spaeter an den KI-Fallback gehen.
"""

from sympy import Rational as R

from .eingabe_parser import symbole
from .pruefung import Aufgabe, Fehler, Loesung, Zielform

a, b, c, u, w, x, y, z = symbole("a b c u w x y z")


def A(loesung, variablen, zielform=Zielform.BELIEBIG, **fehler):
    return Aufgabe(
        loesung=Loesung.zahl(loesung),
        variablen=set(variablen),
        zielform=zielform,
        fehlerkatalog=[Fehler(k, Loesung.zahl(v), t) for k, (v, t) in fehler.items()],
    )


AUFGABEN = {
    # --- 1  Gleichungen I ------------------------------------------------
    # 5x + 10(2 - 6x) = 22 - 6(x - 2)
    "1a": A(R(-2, 7), "x", Zielform.GEKUERZT,
            vorzeichen_rechts=(R(10, 49), "Rechts wird -6·(-2) = +12, nicht -12."),
            klammer_links=(R(14, 5), "Die 10 muss auf beide Summanden der Klammer."),
            vorzeichen_final=(R(2, 7), "Beim Teilen durch -49 kippt das Vorzeichen.")),
    # 2/7 (3 + x) = 5x/14 + 8
    "1b": A(-100, "x", Zielform.GEKUERZT,
            acht_nicht_erweitert=(4, "Auch die 8 muss mit 14 multipliziert werden."),
            vorzeichen_final=(100, "Aus -x = 100 folgt x = -100."),
            nur_zaehler=(R(-100, 7), "Beim Erweitern wurde ein Nenner stehen gelassen.")),

    # --- 2  Grundoperationen ---------------------------------------------
    # 5b - 5b·2c + 3bc
    "2a": A(5*b - 7*b*c, "abc", Zielform.ZUSAMMENGEFASST,
            punkt_vor_strich=(3*b*c, "Erst 5b·2c rechnen, dann subtrahieren."),
            vorzeichen=(5*b - 13*b*c, "Das +3bc wird addiert, nicht subtrahiert."),
            alles_addiert=(5*b + 13*b*c, "Das Minus vor 5b·2c ist verlorengegangen.")),
    # 11w - 2(5w + 4u)
    "2b": A(w - 8*u, "uw", Zielform.ZUSAMMENGEFASST,
            klammer_nur_erster=(w + 4*u, "Die -2 muss auf beide Summanden."),
            vorzeichen=(w + 8*u, "-2·4u ergibt -8u."),
            w_verschluckt=(1 - 8*u, "11w - 10w ist w, nicht 1.")),
    # 12ab + 21a²b² : (7ab) + 24a²/(3a) - a(2 - 5b)
    "2c": A(20*a*b + 6*a, "ab", Zielform.ZUSAMMENGEFASST,
            klammer_vorzeichen=(10*a*b + 6*a, "-a·(-5b) ergibt +5ab."),
            bruch_falsch=(20*a*b + 8*a**2 - 2*a, "24a²:(3a) kuerzt zu 8a, nicht 8a²."),
            division_vergessen=(12*a*b + 3*a*b + 8*a - 2*a + 5*a*b - 3*a*b,
                                "Die Division gilt nur fuer 21a²b².")),

    # --- 3  Potenzen und Wurzeln -----------------------------------------
    "3a": A(10, "", Zielform.BELIEBIG,
            nicht_gewurzelt=(100, "√700 : √7 = √100, und davon noch die Wurzel."),
            subtrahiert=(693, "Wurzeln werden dividiert, nicht die Radikanden subtrahiert.")),
    "3b": A(3, "", Zielform.BELIEBIG,
            termweise=(5, "√(4+4+1) ist nicht √4 + √4 + √1."),
            radikand=(9, "Nach dem Zusammenzaehlen fehlt noch die Wurzel.")),
    # 2·4² - (-3) + 2³
    "3c": A(43, "", Zielform.BELIEBIG,
            reihenfolge=(75, "Erst 4² rechnen, dann mal 2 — nicht (2·4)²."),
            doppeltes_minus=(37, "-(-3) ergibt +3."),
            potenz_als_mal=(25, "2³ ist 8, nicht 2·3.")),
    # (5-7)²·(3²-2) : 2²
    "3d": A(7, "", Zielform.BELIEBIG,
            quadrat_negativ=(-7, "(-2)² ist +4, nicht -4."),
            falscher_teiler=(14, "2² ist 4, geteilt wird durch 4."),
            klammer_potenz=(1, "3² - 2 ist 7, nicht (3-2)².")),
    # √(25a²)
    "3e": A(5*a, "a", Zielform.BELIEBIG,
            nur_zahl_gewurzelt=(5*a**2, "Auch a² kommt unter der Wurzel heraus."),
            gar_nicht=(25*a, "Die Wurzel wirkt auf das ganze Produkt."),
            beides_halbiert=(R(25, 2)*a, "Wurzel ziehen ist nicht halbieren.")),

    # --- 4  Faktorisieren -------------------------------------------------
    "4a": A(16*(x + 2), "x", Zielform.FAKTORISIERT,
            rest_falsch=(16*(x + 16), "32 : 16 ist 2."),
            summe_statt_produkt=(16*x + 32, "Das ist die Ausgangsform.")),
    "4b": A(4*a*(3*a - 2), "a", Zielform.FAKTORISIERT,
            rest_falsch=(4*a*(3*a - 8), "8a : 4a ist 2.")),
    "4c": A(x*y**2*(y - x), "xy", Zielform.FAKTORISIERT,
            vorzeichen=(x*y**2*(y + x), "Das Minus bleibt beim Ausklammern erhalten.")),
    "4d": A(3*x*(2 - 4*y + x*y**2), "xy", Zielform.FAKTORISIERT,
            rest_falsch=(3*x*(2 - 4*y + x*y), "3x²y² : 3x ist xy².")),

    # --- 5  Brueche -------------------------------------------------------
    # (3a+2)/5 - (3+6a)/15 + a
    "5a": A((6*a + 1)/5, "a", Zielform.GEKUERZT,
            vorzeichen_zaehler=((36*a + 9)/15, "Der ganze Zaehler 3+6a wird subtrahiert."),
            a_nicht_erweitert=((3*a + 3)/15, "Das +a muss auch auf den Nenner 15."),
            nur_zaehler_erweitert=((18*a + 3)/45, "Erweitert wird Zaehler und Nenner gemeinsam.")),
    # (8z - 12z²)/(12z²)
    "5b": A((2 - 3*z)/(3*z), "z", Zielform.GEKUERZT,
            aus_summe_gekuerzt=((8*z - 12)/12, "Aus einer Summe darf man nicht kuerzen."),
            nur_teilweise=((2*z - 3*z**2)/(3*z**2), "Da geht noch ein z weg.")),
    # (8b/9a) : (4a/3b)
    "5c": A(2*b**2/(3*a**2), "ab", Zielform.GEKUERZT,
            ohne_kehrwert=(R(32, 27), "Durch einen Bruch teilen heisst mit dem Kehrwert malnehmen."),
            kehrwert_falsch=(R(27, 32), "Der Kehrwert gehoert zum zweiten Bruch."),
            nicht_gekuerzt=(24*b**2/(36*a**2), "Das laesst sich noch kuerzen.")),

    # --- 6  Gleichungen II ------------------------------------------------
    # (3x+1)/9 - (2x-3)/5 = 0
    "6a": A(R(32, 3), "x", Zielform.GEKUERZT,
            vorzeichen_klammer=(R(-22, 3), "-9·(-3) ergibt +27."),
            kreuzweise=(R(4, 3), "Beide Brueche muessen auf denselben Nenner.")),
    # 6x/5 - 7 = (8x-35)/7
    "6b": A(35, "x", Zielform.GEKUERZT,
            sieben_nicht_erweitert=(R(35, 8), "Die -7 muss auch mit 35 multipliziert werden."),
            vorzeichen=(-35, "Aus 2x = 70 folgt x = 35.")),
}


# --------------------------------------------------------------------------
# Aufgabentexte, damit die App etwas anzeigen kann.
# (anleitung, term) — bewusst getrennt vom Aufgabe-Objekt gehalten, weil der
# spätere Generator die Texte selbst erzeugen wird.
# --------------------------------------------------------------------------
TEXTE = {
    "1a": ("Löse nach x auf. Notiere als gekürzten Bruch oder Dezimalzahl.",
           "5x + 10 · (2 − 6x) = 22 − 6 · (x − 2)"),
    "1b": ("Löse nach x auf. Notiere als gekürzten Bruch oder Dezimalzahl.",
           "2/7 · (3 + x) = 5x/14 + 8"),
    "2a": ("Vereinfache so viel wie möglich.", "5b − 5b · 2c + 3bc"),
    "2b": ("Vereinfache so viel wie möglich.", "11w − 2 · (5w + 4u)"),
    "2c": ("Vereinfache so viel wie möglich.",
           "12ab + 21a²b² : (7ab) + 24a²/(3a) − a · (2 − 5b)"),
    "3a": ("Rechne so weit wie möglich aus.", "√700 : √7"),
    "3b": ("Rechne so weit wie möglich aus.", "√(4 + 4 + 1)"),
    "3c": ("Rechne so weit wie möglich aus.", "2 · 4² − (−3) + 2³"),
    "3d": ("Rechne so weit wie möglich aus.", "(5 − 7)² · (3² − 2) : 2²"),
    "3e": ("Rechne so weit wie möglich aus.", "√(25a²)"),
    "4a": ("Klammere so viele Faktoren wie möglich aus.", "16x + 32"),
    "4b": ("Klammere so viele Faktoren wie möglich aus.", "12a² − 8a"),
    "4c": ("Klammere so viele Faktoren wie möglich aus.", "xy³ − x²y²"),
    "4d": ("Klammere so viele Faktoren wie möglich aus.", "6x − 12xy + 3x²y²"),
    "5a": ("Vereinfache so weit wie möglich.", "(3a + 2)/5 − (3 + 6a)/15 + a"),
    "5b": ("Kürze so viel wie möglich.", "(8z − 12z²)/(12z²)"),
    "5c": ("Eliminiere den Doppelbruch und vereinfache.", "(8b/9a) : (4a/3b)"),
    "6a": ("Löse nach x auf. Notiere als gekürzten Bruch oder Dezimalzahl.",
           "(3x + 1)/9 − (2x − 3)/5 = 0"),
    "6b": ("Löse nach x auf. Notiere als gekürzten Bruch oder Dezimalzahl.",
           "6x/5 − 7 = (8x − 35)/7"),
}
