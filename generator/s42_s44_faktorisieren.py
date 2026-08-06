# -*- coding: utf-8 -*-
"""
S42 · Zahl und Variable ausklammern              (Lektionen 12.1 – 12.4)
S43 · Ausklammern mit Potenzen und Variablen     (Lektionen 12.5 – 12.6)
S44 · Dreigliedrige Terme, Vollständigkeit       (Lektionen 12.7 – 12.8)

    «Klammere so viele Faktoren wie möglich aus.»
    10x + 15      10x² − 18x      z⁴ − z³ + z²      6x − 12xy + 3x²y²

Damit ist Kapitel 12 vollständig; es deckt die Erhebungsaufgaben 4a bis 4d
ab. S42/S43/S44 lösen `s4_faktorisieren.py` ab, den letzten Generator mit
numerischer Levelachse.

SO WIRD HIER GEBAUT — und darum stimmt der Lösungsweg immer:
nicht der Term wird vorgegeben und danach faktorisiert, sondern der FAKTOR
und die QUOTIENTEN. Der Term entsteht als `faktor · quotient` je Glied. Der
Generator kann also gar nicht behaupten, der Faktor sei ein anderer als der,
den er selbst hingeschrieben hat. Dass es wirklich der GRÖSSTE ist, prüft
`faktor_ist_groesster` — in der Klammer darf nichts Gemeinsames übrig sein.

DIE DREI PRÜFREGELN (Schablonentext, Abschnitt «Prüfregeln für alle drei»):

    richtig    expand(Antwort) muss dem Term gleichen
    fertig     factor(Antwort) muss die Antwort selbst sein
    Produkt    die Antwort muss ein Produkt sein — sonst ginge bei
               175 + 70 die ausgerechnete 245 als richtig durch

Alle drei stecken in `Zielform.FAKTORISIERT`. Die dritte ist der Grund,
warum BF1 überhaupt existiert.

WAS NICHT IN DEN FEHLERKATALOG GEHÖRT: «nicht vollständig ausgeklammert».
`8(2x + 4)` und `16(x + 2)` haben denselben WERT — ein wertbasierter
Vergleich kann sie nie unterscheiden. Diesen Fall meldet die Zielform als
UNFERTIG, nicht als FALSCH. Im Katalog stehen darum nur Fehler, die den
Wert wirklich verändern.

LEVELACHSE (Teil 2 aller drei Schablonen: «Struktur»): Gliederzahl, Anzahl
Variablen, Potenzstufe und ob eine 1 in der Klammer stehen bleibt. Die
Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from sympy import Integer, expand, factor, gcd, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import zeige, zeige_summe
from .qualitaet import echt_zu_tun, fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}

ANLEITUNG = "Klammere so viele Faktoren wie möglich aus."

SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]
SORTE3 = [z, c, w, d]


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(expand(ergebnis)), text)


# ══════════════════════════════════════════════════════════════════════════
# Der Fehlerkatalog, aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def kandidaten(faktor, quotienten):
    """Die Fehler aus Teil 5 — nur solche, die den Wert verändern."""
    raus = []
    f = sympify(faktor)
    qs = [sympify(q) for q in quotienten]
    glieder = [f * q for q in qs]
    zahl = f.as_coeff_Mul()[0]
    varteil = f / zahl

    #: 1 · Beim Teilen ist nichts passiert — die Glieder blieben stehen.
    if f != 1:
        raus.append(F("nicht_geteilt", f * sum(glieder),
            "Jedes Glied wird durch den Faktor GETEILT, bevor es in die "
            "Klammer kommt."))

    #: 2 · Nur das erste Glied wurde geteilt.
    if f != 1 and len(qs) > 1:
        raus.append(F("nur_erstes_geteilt", f * (qs[0] + sum(glieder[1:])),
            "Der Faktor wird aus JEDEM Glied gezogen, nicht nur aus dem "
            "ersten."))

    #: 3 · Ein Vorzeichen in der Klammer ist verloren gegangen.
    if any(q.could_extract_minus_sign() for q in qs):
        alle_plus = [(-q if q.could_extract_minus_sign() else q) for q in qs]
        raus.append(F("vorzeichen_verloren", f * sum(alle_plus),
            "Mach die Gegenprobe: beim Ausmultiplizieren muss der Term von "
            "vorne wieder herauskommen. Ein Minus bleibt ein Minus."))

    #: 4 · Ein Glied ist beim Teilen verloren gegangen.
    if len(qs) > 1:
        raus.append(F("glied_verloren", f * sum(qs[:-1]),
            f"Der Term hat {len(qs)} Glieder — dann stehen auch "
            f"{len(qs)} Glieder in der Klammer."))

    #: 5 · Die 1 vergessen. Geht ein Glied ganz auf, bleibt eine 1 stehen.
    if any(q == 1 for q in qs):
        raus.append(F("eins_vergessen", f * sum(q for q in qs if q != 1),
            f"{zeige(f)} : {zeige(f)} = 1. Wenn ein Glied vollständig "
            f"aufgeht, bleibt eine 1 in der Klammer stehen."))

    #: 6 · Nur die Zahl vor die Klammer gezogen, die Variable aber trotzdem
    #:     aus jedem Glied genommen.
    if varteil != 1:
        raus.append(F("variable_im_faktor_vergessen", zahl * sum(qs),
            "Der gemeinsame Faktor besteht aus der Zahl UND der Variablen. "
            "Beide gehören vor die Klammer."))

    #: 7 · Umgekehrt: nur die Variable vorgezogen, die Zahl vergessen.
    if zahl != 1 and varteil != 1:
        raus.append(F("zahl_im_faktor_vergessen", varteil * sum(qs),
            "Auch die Zahl ist gemeinsam. Sie gehört mit vor die Klammer."))

    #: 8 · Das Vorzeichen des ganzen Ergebnisses gedreht.
    raus.append(F("vorzeichen_gesamt", -f * sum(qs),
        "Zähl die Minuszeichen noch einmal."))

    #: 9 · Statt geteilt wurde subtrahiert.
    if f != 1:
        raus.append(F("subtrahiert", f * sum(q - f for q in qs),
            "Vor der Klammer steht ein Faktor — das heisst mal, nicht plus."))

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    ziel = expand(sympify(loesung))
    for fe in fehler:
        e = fe.ergebnis.expr
        if e is None:
            continue
        e = expand(sympify(e))
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(fe)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Bauen
# ══════════════════════════════════════════════════════════════════════════

def bau(faktor, quotienten):
    """Aus Faktor und Quotienten wird der Term — nie umgekehrt."""
    f = sympify(faktor)
    qs = [sympify(q) for q in quotienten]
    glieder = [f * q for q in qs]
    klammer = sum(qs)
    term = sum(glieder)

    frage = zeige_summe(*glieder)
    klammer_text = zeige_summe(*qs)
    loesung_text = (f"{zeige(f)}({klammer_text})" if f != 1
                    else f"({klammer_text})")

    fehler = siebe(kandidaten(f, qs), term)
    return {
        "frage": frage,
        "loesung_text": loesung_text,
        #: Für `faktor_ist_groesster` — in der Klammer darf nichts
        #: Gemeinsames mehr stecken.
        "klammer": sympify(klammer),
        "faktor": f,
        "quotienten": qs,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(f * klammer), variablen=VARS,
                           zielform=Zielform.FAKTORISIERT,
                           fehlerkatalog=fehler),
        "schritte": [
            ("Jedes Glied einzeln anschauen", frage),
            ("Suchen, was in ALLEN Gliedern steckt", f"der Faktor {zeige(f)}"),
            ("Faktor vorziehen und jedes Glied dadurch teilen", loesung_text),
            ("Gegenprobe durch Ausmultiplizieren",
             f"{zeige_summe(*glieder)} — stimmt")],
        "tipps": [
            "Suche etwas, das in JEDEM Glied steckt — eine Zahl, eine "
            "Variable oder beides.",
            "Prüfe die Zahlen und jede Variable getrennt. Bei Potenzen "
            "zählt immer die kleinste Hochzahl.",
            f"Der gemeinsame Faktor ist {zeige(f)}. Was bleibt übrig, wenn "
            f"du jedes Glied dadurch teilst?"],
    }


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def echt_gemeinsam(p, g) -> bool:
    """Der Faktor muss wirklich etwas hergeben — 1 wäre keine Aufgabe."""
    return g["faktor"] != 1


def teilerfremd(p, g) -> bool:
    """Der ausgeklammerte Faktor muss der GRÖSSTE sein.

    `faktor_ist_groesster` aus `qualitaet` prüft die fertige Klammer und
    stolpert bei reinen Zahlenaufgaben: `35(5 + 2)` hat als Klammer die
    Zahl 7, und darin steckt natürlich noch etwas. Hier wird stattdessen
    die Liste der Quotienten geprüft, wie sie in der Klammer STEHEN — dort
    darf kein gemeinsamer Teiler mehr sein, weder Zahl noch Variable.
    """
    gemeinsam = g["quotienten"][0]
    for q in g["quotienten"][1:]:
        gemeinsam = gcd(gemeinsam, q)
    return gemeinsam == 1


def verschieden(p, g) -> bool:
    """Keine zwei gleichartigen Glieder in der Klammer.

    Sonst liessen sie sich vorher zusammenfassen — `4a³ − 18a² + 4a − 2a`
    ist keine Faktorisieraufgabe, sondern eine zum Zusammenfassen.
    """
    monome = [str(sympify(q).as_coeff_Mul()[1]) for q in g["quotienten"]]
    if all(mo == "1" for mo in monome):
        #: Reine Zahlenaufgabe (BF1) — dort ist jedes Glied eine Zahl, und
        #: das ist der Sinn der Bauform, nicht ein Fehler.
        return True
    return len(set(monome)) == len(monome)


def klammer_unteilbar(p, g) -> bool:
    """Was in der Klammer steht, darf sich nicht weiter zerlegen lassen.

    Beim ersten Testlauf gefunden: `28x³ − 63x` ergibt `7x(4x² − 9)`, und
    `4x² − 9` ist `(2x − 3)(2x + 3)`. Die App meldet die eigene Musterlösung
    dann als «stimmt, aber noch nicht fertig» — dritte Prüfregel. Solche
    Ziehungen werden hier verworfen; binomische Formeln kommen erst in
    Kapitel 17.
    """
    k = g["klammer"]
    if not getattr(k, "is_Add", False):
        return True
    zerlegt = factor(k)
    return not (zerlegt.is_Mul or zerlegt.is_Pow)


STANDARD = [kopfrechenbar, fehler_eindeutig, teilerfremd, verschieden,
            klammer_unteilbar, echt_zu_tun, echt_gemeinsam, fuenf]


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3,
            "f1": [2, 3, 5, 7], "f2": [3, 4, 5, 6],
            "q1": [2, 3, 4, 5], "q2": [3, 5, 7, 9], "q3": [2, 3, 5, 7],
            "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


# ══════════════════════════════════════════════════════════════════════════
# S42 · Zahl und Variable ausklammern            (12.1 – 12.4)
# ══════════════════════════════════════════════════════════════════════════

def bf42_1(p):
    """Reine Zahlen, kein Buchstabe:  175 + 70

    Diese Bauform gibt es wegen der dritten Prüfregel: ohne sie ginge bei
    175 + 70 die ausgerechnete 245 als richtige Antwort durch.
    """
    st = p["stufe"]
    qs = [p["q1"], p["q2"], p["q3"] + 1, p["q1"] + p["q2"]][:st + 1]
    return bau(p["f1"] * p["f2"], qs)


BF42_1 = Bauform("BF1", "Reine Zahlen, kein Buchstabe",
    bereiche=BEREICH, bauen=bf42_1, filter=STANDARD)


def bf42_2(p):
    """Nur die Zahl lässt sich ausklammern:  10x + 15"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"]]
    else:
        qs = [p["q1"] * v1, -p["q2"], p["q3"] * v1 ** 2]
    return bau(p["f1"], qs)


BF42_2 = Bauform("BF2", "Nur die Zahl lässt sich ausklammern",
    bereiche=BEREICH, bauen=bf42_2, filter=STANDARD)


def bf42_3(p):
    """Nur die Variable:  x² + ax"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [v1, v2]
    elif st == 2:
        qs = [v1, -p["q1"] * v2]
    else:
        qs = [v1, -p["q1"] * v2, p["q2"]]
    return bau(v1, qs)


BF42_3 = Bauform("BF3", "Nur die Variable",
    bereiche=BEREICH, bauen=bf42_3, filter=STANDARD)


def bf42_4(p):
    """Zahl UND Variable:  10x² − 18x"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        #: A ohne Minus, B mit — der Exponent allein trägt kein Level.
        qs = [p["q1"] * v1, p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -p["q2"]]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v1, p["q3"]]
    return bau(p["f1"] * v1, qs)


BF42_4 = Bauform("BF4", "Zahl UND Variable",
    bereiche=BEREICH, bauen=bf42_4, filter=STANDARD)


def bf42_5(p):
    """Zwei Variablen, eine gemeinsam:  5ab + 20ac"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [v2, p["q1"] * v3]
    elif st == 2:
        qs = [v2, -p["q1"] * v3]
    else:
        qs = [v2, -p["q1"] * v3, p["q2"] * v2 * v3]
    return bau(p["f1"] * v1, qs)


BF42_5 = Bauform("BF5", "Zwei Variablen, eine gemeinsam",
    bereiche=BEREICH, bauen=bf42_5, filter=STANDARD)


def bf42_6(p):
    """Die Variable ist NICHT gemeinsam:  10x² − 12

    Der Punkt der Bauform: man muss prüfen, nicht raten. Im zweiten Glied
    steckt kein x, also geht nur die Zahl.
    """
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1 ** 2, p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v1 ** 3, -p["q2"]]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"]]
    return bau(p["f1"], qs)


BF42_6 = Bauform("BF6", "Die Variable ist NICHT gemeinsam",
    bereiche=BEREICH, bauen=bf42_6, filter=STANDARD)


# ── Varianten zu BF1 bis BF6 ───────────────────────────────────────────────
# Die Schablone nennt sechs Bauformen. Damit die Ziehung nicht immer
# dieselben sechs Formen liefert, kommen sechs Varianten dazu — jede eine
# echte Abwandlung, keine blosse Zahlenvariante.

def bf42_7(p):
    """Die Zahl steht vorne:  15 + 10x"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [p["q2"], p["q1"] * v1]
    elif st == 2:
        qs = [p["q2"], -p["q1"] * v1]
    else:
        qs = [p["q2"], -p["q1"] * v1, p["q3"] * v1 ** 2]
    return bau(p["f1"], qs)


BF42_7 = Bauform("BF7", "Die Zahl steht vorne",
    bereiche=BEREICH, bauen=bf42_7, filter=STANDARD)


def bf42_8(p):
    """Ein Glied geht ganz auf — die 1 bleibt stehen:  5a + 15ab"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [1, p["q1"] * v2]
    elif st == 2:
        qs = [1, -p["q1"] * v2]
    else:
        qs = [1, -p["q1"] * v2, p["q2"] * v1]
    return bau(p["f1"] * v1, qs)


BF42_8 = Bauform("BF8", "Ein Glied geht ganz auf — die 1 bleibt stehen",
    bereiche=BEREICH, bauen=bf42_8, filter=STANDARD)


def bf42_9(p):
    """Der Faktor ist eine Potenz:  x³ + x²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [v1, 1]
    elif st == 2:
        qs = [v1, -p["q1"]]
    else:
        qs = [v1 ** 2, -p["q1"] * v2, p["q2"]]
    return bau(v1 ** 2, qs)


BF42_9 = Bauform("BF9", "Der Faktor ist eine Potenz",
    bereiche=BEREICH, bauen=bf42_9, filter=STANDARD)


def bf42_10(p):
    """Zwei Variablen, beide gemeinsam:  6xy + 9xy²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"], p["q2"] * v2]
    elif st == 2:
        qs = [p["q1"], -p["q2"] * v2]
    else:
        qs = [p["q1"], -p["q2"] * v2, p["q3"] * v1]
    return bau(p["f1"] * v1 * v2, qs)


BF42_10 = Bauform("BF10", "Zwei Variablen, beide gemeinsam",
    bereiche=BEREICH, bauen=bf42_10, filter=STANDARD)


def bf42_11(p):
    """Das erste Glied trägt ein Minus im zweiten:  12a − 8"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q2"] * v1, -p["q1"]]
    elif st == 2:
        qs = [p["q2"] * v1, -p["q1"] * v2]
    else:
        qs = [p["q2"] * v1, -p["q1"] * v2, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"], qs)


BF42_11 = Bauform("BF11", "Grösserer gemeinsamer Teiler",
    bereiche=BEREICH, bauen=bf42_11, filter=STANDARD)


def bf42_12(p):
    """Der Faktor ist nur eine Variable, die Zahlen sind teilerfremd"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"] * v2, p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v2, -p["q2"] * v3]
    else:
        qs = [p["q1"] * v2, -p["q2"] * v3, p["q3"] * v2 * v3]
    return bau(v1, qs)


BF42_12 = Bauform("BF12", "Nur die Variable, Zahlen teilerfremd",
    bereiche=BEREICH, bauen=bf42_12, filter=STANDARD)


S42 = Schablone(
    nr="S42", titel="Zahl und Variable ausklammern",
    lektionen="12.1 – 12.4", erhebung="4a", anleitung=ANLEITUNG,
    levelachse="Struktur: Gliederzahl, Vorzeichen, Anzahl Variablen",
    bauformen=[BF42_1, BF42_2, BF42_3, BF42_4, BF42_5, BF42_6,
               BF42_7, BF42_8, BF42_9, BF42_10, BF42_11, BF42_12],
    kernidee="Ausklammern heisst: etwas suchen, das in JEDEM Glied steckt, "
             "und es vor die Klammer ziehen.")


# ══════════════════════════════════════════════════════════════════════════
# S43 · Ausklammern mit Potenzen und Variablen   (12.5 – 12.6)
# ══════════════════════════════════════════════════════════════════════════

def bf43_1(p):
    """Potenz im ersten Glied:  10x² + 15x"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -p["q2"]]
    else:
        qs = [p["q1"] * v1 ** 3, -p["q2"] * v1, p["q3"]]
    return bau(p["f1"] * v1, qs)


BF43_1 = Bauform("BF1", "Potenz im ersten Glied",
    bereiche=BEREICH, bauen=bf43_1, filter=STANDARD)


def bf43_2(p):
    """Drei Potenzen, die kleinste zählt:  z⁴ − z³ + z²"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [v1 ** 2, 1]
    elif st == 2:
        qs = [v1 ** 2, -v1, 1]
    else:
        qs = [v1 ** 3, -p["q1"] * v1 ** 2, p["q2"] * v1, -1]
    return bau(v1 ** 2, qs)


BF43_2 = Bauform("BF2", "Mehrere Potenzen, die kleinste zählt",
    bereiche=BEREICH, bauen=bf43_2, filter=STANDARD)


def bf43_3(p):
    """Zwei Variablen, Zahlen teilerfremd:  2x² − 3xy"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"] * v2]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"] * v2]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"] * v1 * v2]
    return bau(v1, qs)


BF43_3 = Bauform("BF3", "Zwei Variablen, Zahlen teilerfremd",
    bereiche=BEREICH, bauen=bf43_3, filter=STANDARD)


def bf43_4(p):
    """Zahl und Potenz, drei Glieder:  18y⁴ − 60y³ + 12y"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [p["q1"] * v1 ** 2, -p["q2"]]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v1, p["q3"]]
    else:
        qs = [p["q1"] * v1 ** 3, -p["q2"] * v1 ** 2, p["q3"] * v1, -1]
    return bau(p["f1"] * p["f2"] * v1, qs)


BF43_4 = Bauform("BF4", "Zahl und Potenz, drei Glieder",
    bereiche=BEREICH, bauen=bf43_4, filter=STANDARD)


def bf43_5(p):
    """Keine Variable steckt in allen dreien:  3ab − 9ac + 6bc"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        #: Auf A zwei Glieder ohne gemeinsame Variable — nur die Zahl geht.
        qs = [v1 * v2, p["q1"] * v3]
    elif st == 2:
        qs = [v1 * v2, -p["q1"] * v1 * v3, p["q2"] * v2 * v3]
    else:
        qs = [v1 * v2, -p["q1"] * v1 * v3, p["q2"] * v2 * v3,
              -p["q3"] * v1 ** 2]
    return bau(p["f1"], qs)


BF43_5 = Bauform("BF5", "Keine Variable steckt in allen Gliedern",
    bereiche=BEREICH, bauen=bf43_5, filter=STANDARD)


def bf43_6(p):
    """Hohe Potenzen auf beiden Seiten:  x⁵ + x³"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [v1 ** 2, 1]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -p["q2"]]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"]]
    return bau(p["f1"] * v1 ** 3, qs)


BF43_6 = Bauform("BF6", "Hohe Potenzen auf beiden Seiten",
    bereiche=BEREICH, bauen=bf43_6, filter=STANDARD)


def bf43_7(p):
    """Zwei Variablen mit Potenzen:  6x²y − 9xy²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"] * v2]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2 ** 2, p["q3"] * v1 * v2]
    return bau(p["f1"] * v1 * v2, qs)


BF43_7 = Bauform("BF7", "Zwei Variablen mit Potenzen",
    bereiche=BEREICH, bauen=bf43_7, filter=STANDARD)


def bf43_8(p):
    """Die Potenz steckt im zweiten Glied:  4x + 6x³"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"], p["q2"] * v1 ** 2]
    elif st == 2:
        qs = [p["q1"], -p["q2"] * v1 ** 3]
    else:
        qs = [p["q1"], -p["q2"] * v1 ** 3, p["q3"] * v2]
    return bau(p["f1"] * v1, qs)


BF43_8 = Bauform("BF8", "Die Potenz steckt im zweiten Glied",
    bereiche=BEREICH, bauen=bf43_8, filter=STANDARD)


def bf43_9(p):
    """Nur die Zahl geht, obwohl überall Potenzen stehen"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1 ** 2, p["q2"] * v2 ** 2]
    elif st == 2:
        qs = [p["q1"] * v1 ** 3, -p["q2"] * v2 ** 2]
    else:
        qs = [p["q1"] * v1 ** 3, -p["q2"] * v2 ** 2, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"], qs)


BF43_9 = Bauform("BF9", "Nur die Zahl geht, obwohl überall Potenzen stehen",
    bereiche=BEREICH, bauen=bf43_9, filter=STANDARD)


def bf43_10(p):
    """Der Faktor enthält eine Potenz:  12x³ − 8x²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q2"] * v1, -p["q1"]]
    elif st == 2:
        qs = [p["q2"] * v1 ** 2, -p["q1"] * v2]
    else:
        qs = [p["q2"] * v1 ** 2, -p["q1"] * v2, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"] * v1 ** 2, qs)


BF43_10 = Bauform("BF10", "Der Faktor enthält selbst eine Potenz",
    bereiche=BEREICH, bauen=bf43_10, filter=STANDARD)


def bf43_11(p):
    """Drei Variablen, nur eine gemeinsam:  4uv − 6uw"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"] * v2, p["q2"] * v3]
    elif st == 2:
        qs = [p["q1"] * v2 ** 2, -p["q2"] * v3]
    else:
        qs = [p["q1"] * v2 ** 2, -p["q2"] * v3, p["q3"] * v2 * v3]
    return bau(p["f1"] * p["f2"] * v1, qs)


BF43_11 = Bauform("BF11", "Drei Variablen, nur eine gemeinsam",
    bereiche=BEREICH, bauen=bf43_11, filter=STANDARD)


def bf43_12(p):
    """Ein Glied ist der Faktor selbst — die 1 bleibt:  9x³ + 3x"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, 1]
    elif st == 2:
        qs = [p["q1"] * v1 ** 2, -1]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, 1]
    return bau(p["f1"] * v1, qs)


BF43_12 = Bauform("BF12", "Ein Glied ist der Faktor selbst — die 1 bleibt",
    bereiche=BEREICH, bauen=bf43_12, filter=STANDARD)


S43 = Schablone(
    nr="S43", titel="Ausklammern mit Potenzen und mehreren Variablen",
    lektionen="12.5 – 12.6", erhebung="4b · 4c", anleitung=ANLEITUNG,
    levelachse="Struktur: Gliederzahl, Potenzstufe, Anzahl Variablen",
    bauformen=[BF43_1, BF43_2, BF43_3, BF43_4, BF43_5, BF43_6,
               BF43_7, BF43_8, BF43_9, BF43_10, BF43_11, BF43_12],
    kernidee="Zahlen und Variablen getrennt prüfen. Bei Potenzen zählt "
             "immer die kleinste Hochzahl.")


# ══════════════════════════════════════════════════════════════════════════
# S44 · Dreigliedrige Terme, Vollständigkeit prüfen   (12.7 – 12.8)
# ══════════════════════════════════════════════════════════════════════════
#
# Hier steht immer die Frage: steckt die Variable WIRKLICH in allen drei
# Gliedern? Und: bleibt eine 1 stehen? Die Levelachse ist darum die Zahl der
# Variablen und die Potenzstufe, nicht die Gliederzahl — drei Glieder sind
# der Inhalt dieser Lektionen.

def bf44_1(p):
    """Nur die Zahl gemeinsam:  14f + 21g + 35"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"] * v2, p["q3"]]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"] * v2, p["q3"]]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"], qs)


BF44_1 = Bauform("BF1", "Nur die Zahl gemeinsam",
    bereiche=BEREICH, bauen=bf44_1, filter=STANDARD)


def bf44_2(p):
    """Ein Glied ist ein Produkt:  14f + 21g + 35fg"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"] * v2, p["q3"] * v1 * v2]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"] * v2, p["q3"] * v1 * v2]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"] * v1 * v2 ** 2]
    return bau(p["f1"] * p["f2"], qs)


BF44_2 = Bauform("BF2", "Ein Glied ist ein Produkt",
    bereiche=BEREICH, bauen=bf44_2, filter=STANDARD)


def bf44_3(p):
    """Zahl und eine Variable:  14fg + 21fb + 35f"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"] * v2, p["q2"] * v3, p["q3"]]
    elif st == 2:
        qs = [p["q1"] * v2, -p["q2"] * v3, p["q3"]]
    else:
        qs = [p["q1"] * v2 ** 2, -p["q2"] * v3, p["q3"] * v2 * v3]
    return bau(p["f1"] * p["f2"] * v1, qs)


BF44_3 = Bauform("BF3", "Zahl und eine Variable",
    bereiche=BEREICH, bauen=bf44_3, filter=STANDARD)


def bf44_4(p):
    """Die Variablen wechseln, keine steckt überall:  14fg + 21fb + 35bg"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"] * v1 * v2, p["q2"] * v1 * v3, p["q3"] * v2 * v3]
    elif st == 2:
        qs = [p["q1"] * v1 * v2, -p["q2"] * v1 * v3, p["q3"] * v2 * v3]
    else:
        qs = [p["q1"] * v1 ** 2 * v2, -p["q2"] * v1 * v3,
              p["q3"] * v2 * v3 ** 2]
    return bau(p["f1"] * p["f2"], qs)


BF44_4 = Bauform("BF4", "Die Variablen wechseln, keine steckt überall",
    bereiche=BEREICH, bauen=bf44_4, filter=STANDARD)


def bf44_5(p):
    """Drei Variablen, mit Minus:  15xy − 55zx + 40x"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"] * v2, p["q2"] * v3, p["q3"]]
    elif st == 2:
        qs = [p["q1"] * v2, -p["q2"] * v3, p["q3"]]
    else:
        qs = [p["q1"] * v2, -p["q2"] * v3, p["q3"] * v1, -1]
    return bau(p["f1"] * v1, qs)


BF44_5 = Bauform("BF5", "Drei Variablen, mit Minus",
    bereiche=BEREICH, bauen=bf44_5, filter=STANDARD)


def bf44_6(p):
    """Potenzen, und die 1 bleibt stehen:  10xy + 20x²y − 80xy²"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [1, p["q1"] * v1, p["q2"] * v2]
    elif st == 2:
        qs = [1, p["q1"] * v1, -p["q2"] * v2]
    else:
        qs = [1, p["q1"] * v1 ** 2, -p["q2"] * v2, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"] * v1 * v2, qs)


BF44_6 = Bauform("BF6", "Potenzen, und die 1 bleibt stehen",
    bereiche=BEREICH, bauen=bf44_6, filter=STANDARD)


def bf44_7(p):
    """Genau Erhebungsaufgabe 4d:  6x − 12xy + 3x²y²  →  3x(2 − 4y + xy²)"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        #: A zwei Glieder, B drei ohne Minus, C die Erhebungsaufgabe selbst.
        qs = [p["q1"], p["q2"] * v2]
    elif st == 2:
        qs = [p["q1"], p["q2"] * v2, v1 * v2]
    else:
        #: 6x − 12xy + 3x²y² — Wortlaut der Erhebung, mit x und y.
        return bau(3 * x, [Integer(2), -4 * y, x * y ** 2])
    return bau(p["f1"] * v1, qs)


BF44_7 = Bauform("BF7", "Erhebungsaufgabe 4d",
    bereiche=BEREICH, bauen=bf44_7, filter=STANDARD)


def bf44_8(p):
    """Alle drei Glieder tragen dieselbe Variable in anderer Potenz"""
    st, v1 = p["stufe"], p["v1"]
    if st == 1:
        qs = [p["q1"] * v1, p["q2"], p["q3"] * v1 ** 2]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"], p["q3"] * v1 ** 2]
    else:
        qs = [p["q1"] * v1 ** 3, -p["q2"] * v1 ** 2, p["q3"] * v1, -1]
    return bau(p["f1"] * v1, qs)


BF44_8 = Bauform("BF8", "Dieselbe Variable in drei Potenzstufen",
    bereiche=BEREICH, bauen=bf44_8, filter=STANDARD)


def bf44_9(p):
    """Das mittlere Glied trägt das Minus"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v2, p["q2"], p["q3"] * v2 ** 2]
    elif st == 2:
        qs = [p["q1"] * v2, -p["q2"], p["q3"] * v2 ** 2]
    else:
        qs = [p["q1"] * v2 ** 2, -p["q2"] * v1, p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"] * v1, qs)


BF44_9 = Bauform("BF9", "Das mittlere Glied trägt das Minus",
    bereiche=BEREICH, bauen=bf44_9, filter=STANDARD)


def bf44_10(p):
    """Zwei Minus in drei Gliedern"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q1"] * v1, -p["q2"], p["q3"] * v2]
    elif st == 2:
        qs = [p["q1"] * v1, -p["q2"], -p["q3"] * v2]
    else:
        qs = [p["q1"] * v1 ** 2, -p["q2"] * v2, -p["q3"] * v1 * v2]
    return bau(p["f1"] * p["f2"], qs)


BF44_10 = Bauform("BF10", "Zwei Minus in drei Gliedern",
    bereiche=BEREICH, bauen=bf44_10, filter=STANDARD)


def bf44_11(p):
    """Der gemeinsame Faktor ist ein Produkt zweier Variablen"""
    st, v1, v2, v3 = p["stufe"], p["v1"], p["v2"], p["v3"]
    if st == 1:
        qs = [p["q1"], p["q2"] * v3, p["q3"] * v1]
    elif st == 2:
        qs = [p["q1"], -p["q2"] * v3, p["q3"] * v1]
    else:
        qs = [p["q1"], -p["q2"] * v3 ** 2, p["q3"] * v1 * v2]
    return bau(p["f1"] * v1 * v2, qs)


BF44_11 = Bauform("BF11", "Der Faktor ist ein Produkt zweier Variablen",
    bereiche=BEREICH, bauen=bf44_11, filter=STANDARD)


def bf44_12(p):
    """Grosse Zahlen, kleiner gemeinsamer Teiler"""
    st, v1, v2 = p["stufe"], p["v1"], p["v2"]
    if st == 1:
        qs = [p["q2"] * v1, p["q3"], p["q1"] * v2]
    elif st == 2:
        qs = [p["q2"] * v1, -p["q3"], p["q1"] * v2]
    else:
        qs = [p["q2"] * v1 ** 2, -p["q3"] * v2, p["q1"] * v1 * v2]
    return bau(p["f1"], qs)


BF44_12 = Bauform("BF12", "Kleiner gemeinsamer Teiler, drei Glieder",
    bereiche=BEREICH, bauen=bf44_12, filter=STANDARD)


S44 = Schablone(
    nr="S44", titel="Dreigliedrige Terme, Vollständigkeit prüfen",
    lektionen="12.7 – 12.8", erhebung="4d", anleitung=ANLEITUNG,
    levelachse="Struktur: Anzahl Variablen, Potenzstufe, die 1 in der "
               "Klammer",
    bauformen=[BF44_1, BF44_2, BF44_3, BF44_4, BF44_5, BF44_6,
               BF44_7, BF44_8, BF44_9, BF44_10, BF44_11, BF44_12],
    kernidee="Auch bei drei Gliedern: jede Zahl und jede Variable einzeln "
             "prüfen. Geht ein Glied ganz auf, bleibt eine 1.")
