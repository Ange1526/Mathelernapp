# -*- coding: utf-8 -*-
"""
S48 · Bruchterme verstehen und erweitern   (Lektionen 14.1 – 14.2 · 14.8)

    «Womit muss erweitert werden? Gib den neuen Zähler an.»
    6/(7x) = ?/(84xyz)      →   72yz
    2r = ?/(3s)             →   6rs

**Erhebungsaufgabe 5a** hängt an 14.8 («Ganze Terme auf den Hauptnenner
bringen») und wird von dieser Schablone abgedeckt: BF2 ist genau diese Form.

ZWEI DINGE ZUR LAGE DIESER SCHABLONE, damit später niemand rätselt:

1. Von S48 liegt nur die KURZFASSUNG mit sechs Bauformen vor, nicht die
   Matrixfassung mit zwölf wie bei allen anderen. Die sechs dokumentierten
   sind BF1 bis BF6 und stehen unverändert. BF7 bis BF12 sind Varianten
   derselben sechs Lernschritte — Sonderfälle, die in jeder anderen
   Schablone auch vorkommen (Erweiterungsfaktor eins, Zähler null,
   Vorzeichen). Sie sind hier als solche gekennzeichnet.

2. Die Aufgabe hat die Form `alt = ?/neu`, und gefragt ist der neue ZÄHLER.
   Anders liesse sie sich nicht prüfen: `6/(7x)` und `72yz/(84xyz)` sind
   derselbe Wert, jede Prüfung auf Gleichheit würde die unveränderte
   Aufgabe durchgehen lassen. Dasselbe Vorgehen wie bei den
   Rückwärtsformen von S25.

LEVELACHSE (Teil 2): Struktur des Nenners — Erweiterungsfaktor direkt
ablesbar, dann als Monom, dann erst nach dem Faktorisieren sichtbar.
"""
from __future__ import annotations

from sympy import Integer, cancel, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s9_division import M, Su, als_text, reihenfolge
from .schablone import Bauform, Schablone

a, b, c, n, q, r, u, v, w, x, y, z = symbole("a b c n q r u v w x y z")
VARS = {"a", "b", "c", "n", "q", "r", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Erweitere den Bruch. Gib nur den neuen Zähler an."

#: Drei Buchstaben fehlen hier mit Absicht:
#:   s  —  aus a und s entsteht das Monom «as», ein Python-Schluesselwort
#:   d  —  aus a, n und d entsteht «and», dasselbe Problem
#:   r  —  ein einzelnes «r» liest der Parser als «alle reellen Zahlen».
#:         Eine Antwort, die nur aus r besteht, kaeme darum nie als Term an.
#: Alle drei sind im Testlauf aufgefallen, das letzte mit «r» als
#: Katalogeintrag, der nie erkannt wurde.
SORTE1 = [x, a, u, v]
SORTE2 = [y, b, n, q]
SORTE3 = [z, c, w, b]


def F(s_, e, t):
    return Fehler(s_, Loesung.zahl(e), t)


def frage_text(alt_zaehler, alt_nenner, neu_nenner) -> str:
    """«6/(7x)  =  ?/(84xyz)» — die Aufgabe steht als Gleichung da."""
    links = f"{alt_zaehler.text}/({alt_nenner.text})" if alt_nenner else \
            alt_zaehler.text
    return f"{links}  =  ?/({neu_nenner.text})"


def bau(alt_zaehler, alt_nenner, neu_nenner, extra=(), tipps=None):
    """Der neue Zähler ergibt sich aus dem Erweiterungsfaktor."""
    az = sympify(alt_zaehler.wert)
    an = sympify(alt_nenner.wert) if alt_nenner else Integer(1)
    nn = sympify(neu_nenner.wert)
    faktor = cancel(nn / an)
    l = expand(az * faktor)
    frage = frage_text(alt_zaehler, alt_nenner, neu_nenner)
    folge = reihenfolge([alt_zaehler, neu_nenner]
                        + ([alt_nenner] if alt_nenner else []))
    text = als_text(l, folge)
    katalog = list(extra) + [
        F("nicht_erweitert", az,
          "Der Zähler muss mit demselben Faktor malgenommen werden wie der "
          "Nenner — sonst ist es nicht mehr derselbe Bruch."),
        F("nur_faktor", expand(faktor),
          f"Das ist der Erweiterungsfaktor. Gefragt ist der neue Zähler: "
          f"{text}."),
        F("nenner_abgeschrieben", nn,
          "Das ist der neue Nenner. Gefragt ist, was oben stehen muss."),
        F("geteilt_statt_mal", cancel(az / faktor) if faktor != 0 else az,
          "Beim Erweitern wird multipliziert, nicht dividiert."),
        F("faktor_addiert", expand(az + faktor),
          "Erweitern heisst mal, nicht plus."),
    ]
    katalog = _siebe(katalog, l)
    return {"frage": frage, "loesung_text": text,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=Zielform.BELIEBIG,
                               fehlerkatalog=katalog),
            "schritte": [
                ("Die beiden Nenner vergleichen",
                 f"{alt_nenner.text if alt_nenner else '1'}  →  "
                 f"{neu_nenner.text}"),
                ("Womit wurde der Nenner malgenommen?",
                 als_text(faktor, folge)),
                ("Denselben Faktor auf den Zähler anwenden", text),
            ],
            "tipps": (tipps or TIPPS)[:2] + [
                f"Der Nenner wurde mit {als_text(faktor, folge)} "
                f"malgenommen. Damit auch den Zähler."]}


def _siebe(katalog, l):
    raus, gesehen = [], set()
    ziel = expand(sympify(l))
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        e = expand(sympify(e))
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


TIPPS = [
    "Erweitern heisst: Zähler UND Nenner mit derselben Zahl malnehmen.",
    "Vergleich die beiden Nenner — womit wurde der alte malgenommen?",
    "",
]


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def klein(p, g) -> bool:
    from sympy import Rational
    for t_ in sympify(g["aufgabe"].loesung.expr).atoms(Rational):
        if abs(t_.p) > 500 or t_.q != 1:
            return False
    return True


def verschieden(*namen):
    def f(p, g):
        werte = [str(p[nn]) for nn in namen if nn in p]
        return len(set(werte)) == len(werte)
    return f


STANDARD = [fehler_eindeutig, fuenf, klein]
DREI = STANDARD + [verschieden("v1", "v2", "v3")]

BEREICH = {
    "A": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [2, 3],
          "k": [2, 3, 6], "stufe": [1]},
    "B": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [3, 4],
          "k": [3, 4, 7], "stufe": [2]},
    "C": {"v1": SORTE1, "v2": SORTE2, "v3": SORTE3, "f": [4, 6],
          "k": [2, 5, 7], "stufe": [3]},
}


def _m(koeff, *basen):
    return M(Integer(koeff), tuple(basen))


# ══════════════════════════════════════════════════════════════════════════
# BF1 bis BF6 — die sechs Bauformen der Schablone
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    """Erweiterungsfaktor ist ein Monom, direkt ablesbar:
       6/(7x) = ?/(84xyz)"""
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    alt_z = _m(f * 3)
    alt_n = _m(k + 5, (v1, 1))
    if st == 3:
        neu_n = _m((k + 5) * f * 2, (v1, 1), (v2, 1), (v3, 1))
    elif st == 2:
        neu_n = _m((k + 5) * f, (v1, 1), (v2, 1))
    else:
        neu_n = _m((k + 5) * f, (v1, 1))
    return bau(alt_z, alt_n, neu_n)


BF1 = Bauform("BF1", "Erweiterungsfaktor direkt ablesbar",
    bereiche=BEREICH, bauen=bf1, filter=DREI)


def bf2(p):
    """Ein ganzer Term wird als Bruch geschrieben:  2r = ?/(3s)

    Das ist Lektion 14.8 und damit Erhebungsaufgabe 5a: ein Term ohne
    Bruchstrich muss auf den Hauptnenner gebracht werden.
    """
    v1, v2, v3, f, k, st = (p["v1"], p["v2"], p["v3"], p["f"], p["k"],
                            p["stufe"])
    alt_z = _m(f, (v1, 1))
    if st == 3:
        neu_n = _m(k, (v2, 1), (v3, 1))
    elif st == 2:
        neu_n = _m(k, (v2, 2))
    else:
        neu_n = _m(k, (v2, 1))
    #: Ohne alten Nenner ist der Erweiterungsfaktor gleich dem neuen Nenner
    #: — dann fallen zwei der allgemeinen Eintraege zusammen.
    return bau(alt_z, None, neu_n, extra=[
        F("nur_zaehler_verdoppelt", expand(sympify(alt_z.wert) * 2),
          "Der ganze Term kommt ueber den Bruchstrich, mal dem neuen "
          "Nenner."),
        F("nenner_als_zaehler_48", expand(sympify(neu_n.wert)
                                          + sympify(alt_z.wert)),
          "Erweitern heisst mal, nicht plus."),
    ])


BF2 = Bauform("BF2", "Ganzer Term wird als Bruch geschrieben",
    bereiche=BEREICH, bauen=bf2, filter=DREI)


def bf3(p):
    """Summe im Zähler — der Faktor gilt für beide Summanden:
       (a + b)/(ab²) = ?/(a³b³)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    #: Der Zaehler waechst mit der Stufe: A zwei Glieder, B ein Minus,
    #: C drei Glieder.
    if st == 3:
        alt_z = Su("+-+", (_m(1, (v1, 1)), _m(1, (v2, 1)), _m(k)))
    elif st == 2:
        alt_z = Su("+-", (_m(1, (v1, 1)), _m(1, (v2, 1))))
    else:
        alt_z = Su("++", (_m(1, (v1, 1)), _m(1, (v2, 1))))
    alt_n = _m(1, (v1, 1), (v2, 2))
    if st == 3:
        #: Auf C eine hoehere Potenz UND ein Zahlfaktor.
        neu_n = _m(k * 2, (v1, 4), (v2, 3))
    elif st == 2:
        #: Auf B kommt ein Zahlfaktor dazu — sonst traegt zwischen A und B
        #: nur die Hochzahl.
        neu_n = _m(k, (v1, 2), (v2, 2))
    else:
        neu_n = _m(1, (v1, 2), (v2, 2))
    return bau(alt_z, alt_n, neu_n, extra=[
        F("nur_erster_summand",
          expand(sympify(alt_z.glieder[0].wert)
                 * cancel(sympify(neu_n.wert) / sympify(alt_n.wert))),
          "Der Erweiterungsfaktor gilt für JEDEN Summanden im Zähler, nicht "
          "nur für den ersten."),
    ])


BF3 = Bauform("BF3", "Summe im Zähler",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD + [verschieden("v1", "v2")])


def bf4(p):
    """Der Nenner muss erst faktorisiert werden:
       x/(x − 3) = ?/(x² − x − 6)   mit  x² − x − 6 = (x − 3)(x + 2)"""
    v1, k, st = p["v1"], p["k"], p["stufe"]
    m1, m2 = 3, 2
    #: Nicht die nackte Variable als Zaehler — dann ist der Eintrag
    #: «nicht erweitert» ein einzelnes Symbol und faellt mit der
    #: Vorzeichenpruefung der App zusammen.
    alt_z = _m(2, (v1, 1))
    alt_n = Su("+-", (_m(1, (v1, 1)), _m(m1)))
    #: (x − 3)(x + 2) = x² − x − 6
    neu_n = Su("+-" if m2 - m1 < 0 else "++",
               (_m(1, (v1, 2)), _m(abs(m2 - m1), (v1, 1))))
    neu_n = Su("+--", (_m(1, (v1, 2)), _m(abs(m1 - m2), (v1, 1)),
                       _m(m1 * m2)))
    if st == 3:
        alt_z = Su("++", (_m(1, (v1, 1)), _m(k)))
    elif st == 2:
        #: Auf B eine Potenz im Zaehler.
        alt_z = _m(k, (v1, 2))
    return bau(alt_z, alt_n, neu_n, extra=[
        F("nenner_nicht_faktorisiert", sympify(neu_n.wert),
          "Zerleg den neuen Nenner zuerst in Faktoren — dann siehst du, "
          "womit erweitert wurde."),
    ])


BF4 = Bauform("BF4", "Der Nenner muss erst faktorisiert werden",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """Dritte binomische Formel im neuen Nenner:
       2z/(u − 4) = ?/(u² − 16)"""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    m1 = 4
    alt_z = _m(2, (v2, 1))
    alt_n = Su("+-", (_m(1, (v1, 1)), _m(m1)))
    neu_n = Su("+-", (_m(1, (v1, 2)), _m(m1 * m1)))
    if st == 3:
        alt_z = Su("++", (_m(2, (v2, 1)), _m(k)))
    elif st == 2:
        #: Auf B steht im Zaehler eine Potenz — das unterscheidet den Aufbau.
        alt_z = _m(k, (v2, 2))
    return bau(alt_z, alt_n, neu_n, extra=[
        F("binom_uebersehen", sympify(alt_z.wert) * 2,
          f"{zeige(sympify(v1) ** 2 - m1 * m1)} ist "
          f"({zeige(v1)} − {m1})({zeige(v1)} + {m1}) — erweitert wurde also "
          f"mit {zeige(v1)} + {m1}."),
    ])


BF5 = Bauform("BF5", "Dritte binomische Formel im neuen Nenner",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD + [verschieden("v1", "v2")])


def bf6(p):
    """Erweitern mit −1 dreht oben und unten alle Vorzeichen:
       (b − a)/(−a − c)  →  (a − b)/(a + c)"""
    v1, v2, v3, st = p["v1"], p["v2"], p["v3"], p["stufe"]
    #: Der Zaehler waechst mit der Stufe, damit sich der Aufbau
    #: unterscheidet und nicht bloss die Zahlen.
    if st == 3:
        alt_z = Su("+-+", (_m(1, (v2, 1)), _m(1, (v1, 1)), _m(2)))
        neu_n = Su("++", (_m(3, (v1, 1)), _m(3, (v3, 1))))
    elif st == 2:
        alt_z = Su("+-", (_m(2, (v2, 1)), _m(1, (v1, 1))))
        neu_n = Su("++", (_m(2, (v1, 1)), _m(2, (v3, 1))))
    else:
        #: Auf A ein Zahlfaktor im neuen Nenner, damit der
        #: Erweiterungsfaktor nicht −1 ist und der Katalog fuenf
        #: unterscheidbare Eintraege bekommt.
        alt_z = Su("+-", (_m(1, (v2, 1)), _m(1, (v1, 1))))
        neu_n = Su("++", (_m(4, (v1, 1)), _m(4, (v3, 1))))
    alt_n = Su("--", (_m(1, (v1, 1)), _m(1, (v3, 1))))
    return bau(alt_z, alt_n, neu_n, extra=[
        F("vorzeichen_nur_oben", expand(sympify(alt_z.wert)),
          "Beim Erweitern mit −1 drehen ALLE Vorzeichen um — oben wie "
          "unten."),
    ])


BF6 = Bauform("BF6", "Erweitern mit minus eins",
    bereiche=BEREICH, bauen=bf6, filter=DREI)


# ══════════════════════════════════════════════════════════════════════════
# BF7 bis BF12 — Varianten und Sonderfälle
# ══════════════════════════════════════════════════════════════════════════
#
# Die Kurzfassung von S48 nennt sechs Bauformen. Die folgenden sechs sind
# keine neuen Lernschritte, sondern die Sonderfälle, die in jeder anderen
# Schablone des Projekts auch vorkommen: Faktor eins, Zähler null,
# Potenzen, Vorzeichen. Sie sind hier als Varianten gekennzeichnet.

def bf7(p):
    """Variante: der Erweiterungsfaktor ist eine reine Zahl."""
    v1, f, k, st = p["v1"], p["f"], p["k"], p["stufe"]
    alt_z = _m(f, (v1, 1))
    alt_n = _m(k)
    #: Auf B kommt eine Variable in den neuen Nenner, auf C eine Potenz —
    #: sonst traegt zwischen den Stufen nur die Zahl.
    if st == 3:
        neu_n = _m(k * (f + 1), (v1, 2))
    elif st == 2:
        neu_n = _m(k * (f + 1), (v1, 1))
    else:
        neu_n = _m(k * (f + 1))
    return bau(alt_z, alt_n, neu_n)


BF7 = Bauform("BF7", "Variante: Erweiterungsfaktor ist eine Zahl",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def bf8(p):
    """Variante: der Erweiterungsfaktor ist eine reine Variable."""
    v1, v2, v3, f, st = p["v1"], p["v2"], p["v3"], p["f"], p["stufe"]
    alt_z = _m(f)
    alt_n = _m(1, (v1, 1))
    if st == 3:
        neu_n = _m(1, (v1, 1), (v2, 1), (v3, 1))
    elif st == 2:
        #: Nicht v1², sonst ist der Erweiterungsfaktor genau der alte
        #: Nenner — dann fallen zwei Katalogeintraege zusammen.
        neu_n = _m(2, (v1, 1), (v2, 1))
    else:
        neu_n = _m(1, (v1, 1), (v2, 1))
    return bau(alt_z, alt_n, neu_n)


BF8 = Bauform("BF8", "Variante: Erweiterungsfaktor ist eine Variable",
    bereiche=BEREICH, bauen=bf8, filter=DREI)


def bf9(p):
    """Sonderfall: der Zähler ist null — er bleibt null."""
    v1, v2, k, st = p["v1"], p["v2"], p["k"], p["stufe"]
    alt_z = _m(0)
    alt_n = _m(k, (v1, 1))
    if st == 3:
        neu_n = _m(k * 3, (v1, 2), (v2, 1))
    elif st == 2:
        neu_n = _m(k * 2, (v1, 2))
    else:
        neu_n = _m(k * 3, (v1, 1))
    g = bau(alt_z, alt_n, neu_n)
    g["aufgabe"].fehlerkatalog = _siebe([
        F("nenner_null", sympify(neu_n.wert),
          "Null mal irgendetwas bleibt null — der neue Zähler ist auch null."),
        F("eins_null", Integer(1), "Null erweitert bleibt null."),
        F("faktor_null", cancel(sympify(neu_n.wert) / sympify(alt_n.wert)),
          "Das ist der Erweiterungsfaktor. Null mal diesem Faktor ist null."),
        F("minus_null", Integer(-1), "Null bleibt null."),
        F("zwei_null", Integer(2), "Null bleibt null."),
    ], Integer(0))
    return g


BF9 = Bauform("BF9", "Sonderfall: der Zähler ist null",
    bereiche=BEREICH, bauen=bf9, filter=[fehler_eindeutig, fuenf])


def bf10(p):
    """Variante: Potenzen im Zähler und im Nenner."""
    v1, v2, f, st = p["v1"], p["v2"], p["f"], p["stufe"]
    alt_z = _m(f, (v1, 2))
    alt_n = _m(1, (v2, 1))
    if st == 3:
        neu_n = _m(1, (v2, 3), (v1, 1))
    elif st == 2:
        #: Auf B kommt ein Zahlfaktor dazu — sonst waere der Aufbau gleich.
        neu_n = _m(f, (v2, 2))
    else:
        neu_n = _m(1, (v2, 2))
    return bau(alt_z, alt_n, neu_n)


BF10 = Bauform("BF10", "Variante: Potenzen in Zähler und Nenner",
    bereiche=BEREICH, bauen=bf10, filter=STANDARD + [verschieden("v1", "v2")])


def bf11(p):
    """Variante: negativer Zähler."""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    alt_z = _m(-f, (v1, 1))
    alt_n = _m(k)
    if st == 3:
        neu_n = _m(k * 3, (v2, 2))
    elif st == 2:
        neu_n = _m(k * 2, (v2, 1))
    else:
        neu_n = _m(k * 2)
    return bau(alt_z, alt_n, neu_n)


BF11 = Bauform("BF11", "Variante: negativer Zähler",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD + [verschieden("v1", "v2")])


def bf12(p):
    """Variante: Summe im Zähler und Zahl als Faktor."""
    v1, v2, f, k, st = p["v1"], p["v2"], p["f"], p["k"], p["stufe"]
    alt_z = Su("+-", (_m(1, (v1, 1)), _m(k)))
    alt_n = _m(f)
    if st == 3:
        neu_n = _m(f * 3, (v2, 2))
    elif st == 2:
        neu_n = _m(f * 2, (v2, 1))
    else:
        #: mal 3 statt mal 2 — sonst faellt «Faktor addiert» mit einem
        #: anderen Katalogeintrag zusammen.
        neu_n = _m(f * 3)
    return bau(alt_z, alt_n, neu_n, extra=[
        F("nur_erstes_glied_48",
          expand(sympify(alt_z.glieder[0].wert)
                 * cancel(sympify(neu_n.wert) / sympify(alt_n.wert))),
          "Der Faktor gilt für beide Glieder des Zählers."),
    ])


BF12 = Bauform("BF12", "Variante: Summe im Zähler und Zahl als Faktor",
    bereiche=BEREICH, bauen=bf12, filter=STANDARD + [verschieden("v1", "v2")])


S48 = Schablone(
    nr="S48", titel="Bruchterme verstehen und erweitern",
    lektionen="14.1 – 14.2 · 14.8", erhebung="5a",
    anleitung=ANLEITUNG,
    levelachse="Struktur des Nenners",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Erweitern heisst: Zähler UND Nenner mit demselben Faktor "
              "malnehmen. Der Wert des Bruchs ändert sich dabei nicht."),
)
