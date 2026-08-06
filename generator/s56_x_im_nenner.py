# -*- coding: utf-8 -*-
"""
S56 · Term im Nenner, x im Nenner              (Lektionen 15.7 – 15.8)

    «Löse die Gleichung. Gib nur den Wert von x an.»
    6/x = 3      25/(x − 1) = 1      (4x + 5)/(2x − 6) = 17/(2x − 6)

DIE EINE STELLE, WO DIE DEFINITIONSMENGE ZÄHLT. Steht x im Nenner, kann
rechnerisch eine Zahl herauskommen, die genau diesen Nenner null macht —
dann ist sie keine Lösung. Das ist BF4, und wegen dieser Bauform gibt es
die Lektion überhaupt; sie steht so in der Theoriebox des Lehrmittels.

WAS BEWUSST FEHLT: In der Schablone gibt es eine Bauform BF6, deren Antwort
«jede Zahl ausser 2 und −2» lautet. CLAUDE.md hält Definitionsbereiche
ausserhalb des Umfangs, und die App kann eine Lösungsmenge mit Ausnahmen
nicht entgegennehmen — sie kennt eine Zahl, «keine Lösung» und «jede Zahl».
Diese eine Bauform ist darum nicht gebaut. An ihrer Stelle steht BF6 hier
für Lektion 15.7: ein Nenner, der erst ausgerechnet werden muss und noch
kein x enthält. Wer das anders haben will, muss zuerst entscheiden, wie
eine Antwort mit Ausnahmen aussehen soll — das ist eine Entscheidung über
die Eingabe, nicht über den Generator.

DER FALL «KEINE LÖSUNG» IST DAGEGEN DA: er braucht keine Mengenschreibweise,
sondern nur den Knopf «keine Lösung», den die App schon hat.

WIE GERECHNET WIRD: `solve()` wird nicht benutzt (CLAUDE.md — es liefert bei
`positive=True` keine negativen Lösungen). Stattdessen wird die Differenz
beider Seiten gekürzt, in Zähler und Nenner zerlegt, und der Zähler ist
linear in x. Die verbotenen Stellen kommen aus den Nennern der Aufgabe
selbst, nicht aus dem Ergebnis.

LEVELACHSE (Teil 2): Struktur des Nenners — x allein → Term mit x → zwei
verschiedene Terme — und die Anzahl Brüche. Die Zahlenvorräte sind auf
allen drei Stufen dieselben.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Poly, Rational, cancel, expand, lcm, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

x = symbole("x")[0]
VARS = {"x"}
ANLEITUNG = "Löse die Gleichung. Gib nur den Wert von x an."


def F(schluessel, wert, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(wert), text)


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class T:
    """Ein Summand einer Seite: sein Text und sein Wert.

    `zaehler` ist der Wert OHNE Nenner — daraus wird der Fehler «den Nenner
    einfach weggelassen» gerechnet.
    """
    text: str
    wert: object
    zaehler: object = None

    @property
    def oben(self):
        return self.wert if self.zaehler is None else self.zaehler


def lin(k, c) -> tuple:
    """Ein linearer Term als (Text, Wert):  2x − 6"""
    wert = Integer(k) * x + Integer(c)
    if k == 0:
        return zeige(Integer(c)), wert
    vorne = "x" if k == 1 else (f"{MINUS}x" if k == -1 else f"{k}x")
    if c == 0:
        return vorne, wert
    return f"{vorne} {'+' if c > 0 else MINUS} {abs(c)}", wert


def _klammer(text: str) -> str:
    """Ein Nenner bekommt Klammern, sobald er aus mehr als einem Stück
    besteht — `6/x` und `6/12`, aber `25/(x − 1)` und `5/(2x)`.

    `5/2x` OHNE Klammer heisst nach Punkt vor Strich (5/2)·x. Genau die
    Verwechslung, um die es in dieser Lektion geht.
    """
    if text.startswith("(") and text.endswith(")"):
        return text
    if len(text) == 1 or text.isdigit():
        return text
    return f"({text})"


def BR(zt, zw, nt, nw) -> T:
    """Ein Bruch:  (4x + 5)/(2x − 6)"""
    return T(f"{_klammer(zt) if ' ' in zt else zt}/{_klammer(nt)}",
             sympify(zw) / sympify(nw), sympify(zw))


def ZA(wert) -> T:
    return T(zeige(Integer(wert)), Integer(wert))


def XT(k) -> T:
    t, w = lin(k, 0)
    return T(t, w)


def seite(muster, teile) -> tuple:
    """(Text, Wert) einer Gleichungsseite."""
    stuecke, wert = [], Integer(0)
    for i, (zeichen, t) in enumerate(zip(muster, teile)):
        if i == 0:
            stuecke.append(t.text if zeichen == "+" else f"{MINUS}{t.text}")
        else:
            stuecke.append(f"{'+' if zeichen == '+' else MINUS} {t.text}")
        wert += t.wert if zeichen == "+" else -t.wert
    return " ".join(stuecke), wert


def _oben(muster, teile):
    """Dieselbe Seite, aber jeder Bruch ohne seinen Nenner."""
    wert = Integer(0)
    for zeichen, t in zip(muster, teile):
        wert += t.oben if zeichen == "+" else -t.oben
    return wert


# ══════════════════════════════════════════════════════════════════════════
# Lösen — ohne solve()
# ══════════════════════════════════════════════════════════════════════════

def rechnerisch(links, rechts, nenner=()):
    """Der Wert, der herauskommt, wenn man nur rechnet.

    Beide Seiten werden mit dem HAUPTNENNER durchmultipliziert — genau wie
    im Lösungsweg. `cancel()` waere hier falsch: bei
    `(x + 1)/(x − 1) = 2/(x − 1)` kuerzt es die Gleichung zu `1 = 1` weg und
    verschluckt damit die Zahl, um die es geht.
    """
    hn = Integer(1)
    for n in nenner:
        hn = lcm(hn, sympify(n))
    #: Erst mit dem Hauptnenner MULTIPLIZIEREN, dann kuerzen. In dieser
    #: Reihenfolge bleibt die Zahl stehen, um die es geht.
    z = expand(cancel((sympify(links) - sympify(rechts)) * hn))
    try:
        p = Poly(z, x)
    except Exception:
        return None
    if p.degree() != 1:
        return None
    return Rational(-p.coeff_monomial(1), p.coeff_monomial(x))


def verboten(*nenner) -> set:
    """Wo wird ein Nenner null? Aus der AUFGABE, nicht aus dem Ergebnis."""
    raus = set()
    for n in nenner:
        n = sympify(n)
        if not n.free_symbols:
            continue
        p = Poly(expand(n), x)
        if p.degree() == 1:
            raus.add(Rational(-p.coeff_monomial(1), p.coeff_monomial(x)))
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Bauen
# ══════════════════════════════════════════════════════════════════════════

TIPPS = [
    "Ein Nenner darf nie null werden. Schau zuerst nach, für welches x das "
    "passieren würde.",
    "Multipliziere beide Seiten mit dem Hauptnenner. Dann verschwinden die "
    "Brüche und es bleibt eine gewöhnliche Gleichung.",
    "",
]


def bau(lmus, lteile, rmus, rteile, nenner=()):
    ltext, lwert = seite(lmus, lteile)
    rtext, rwert = seite(rmus, rteile)
    frage = f"{ltext} = {rtext}"

    wert = rechnerisch(lwert, rwert, nenner)
    tabu = verboten(*nenner)
    ausgeschlossen = wert is not None and wert in tabu

    if wert is None or ausgeschlossen:
        l = Loesung.keine()
        loesung_text = "keine Lösung"
    else:
        l = Loesung.zahl(wert)
        loesung_text = zeige(wert)

    #: Der Fehlerkatalog. Alles wird aus der Aufgabe gerechnet.
    roh = []
    if ausgeschlossen:
        #: DER Fehler dieser Lektion: gerechnet, aber D nicht geprüft.
        roh.append(F("d_uebersehen", wert,
            f"Rechnerisch kommt {zeige(wert)} heraus — aber genau dort wird "
            f"ein Nenner null. Diese Zahl ist keine Lösung, also hat die "
            f"Gleichung keine."))
    ohne = rechnerisch(_oben(lmus, lteile), _oben(rmus, rteile))
    if ohne is not None:
        roh.append(F("nenner_gestrichen", ohne,
            "Die Nenner verschwinden nicht von selbst. Multipliziere beide "
            "Seiten mit dem Hauptnenner."))
    gedreht = rechnerisch(lwert, -rwert, nenner)
    if gedreht is not None:
        roh.append(F("vorzeichen_seite", gedreht,
            "Beim Hinüberbringen dreht sich das Vorzeichen — aber nur "
            "einmal."))
    if wert is not None and wert != 0:
        roh.append(F("kehrwert", Rational(1, 1) / wert,
            "Am Schluss steht x, nicht 1/x. Kehr den Bruch nicht noch "
            "einmal um."))
        roh.append(F("vorzeichen_gesamt", -wert,
            "Zähl die Minuszeichen noch einmal."))
    for verb in sorted(tabu):
        roh.append(F("nenner_null", verb,
            f"Für x = {zeige(verb)} wird ein Nenner null. Diese Zahl kann "
            f"nie eine Lösung sein."))

    fehler, gesehen = [], set()
    for fe in roh:
        e = fe.ergebnis.expr
        if e is None or (wert is not None and e == wert and
                         not ausgeschlossen):
            continue
        if str(e) in gesehen:
            continue
        gesehen.add(str(e))
        fehler.append(fe)

    return {
        "frage": frage,
        "loesung_text": loesung_text,
        "aufgabe": Aufgabe(loesung=l, variablen=VARS,
                           zielform=Zielform.BELIEBIG, fehlerkatalog=fehler),
        "verboten": tabu,
        "wert": wert,
        "schritte": [
            ("Zuerst: wann wird ein Nenner null?",
             ", ".join(f"x = {zeige(v)}" for v in sorted(tabu))
             or "kein Nenner mit x"),
            ("Beide Seiten mit dem Hauptnenner multiplizieren", frage),
            ("Die Gleichung normal auflösen",
             f"x = {zeige(wert)}" if wert is not None else "kein x übrig"),
            ("Das Ergebnis mit den verbotenen Stellen vergleichen",
             loesung_text)],
        "tipps": [TIPPS[0], TIPPS[1],
                  (f"Verboten ist {', '.join('x = ' + zeige(v) for v in sorted(tabu))}."
                   if tabu else "Hier kann kein Nenner null werden.")],
    }


# ══════════════════════════════════════════════════════════════════════════
# Filter
# ══════════════════════════════════════════════════════════════════════════

def drei(p, g) -> bool:
    """Drei Einträge genügen hier.

    Wo die Antwort «keine Lösung» heisst, gibt es nur wenige Zahlen, die ein
    Schüler überhaupt hinschreiben kann — mehr als drei unterscheidbare
    Fehlwerte sind ausgedacht, nicht beobachtet.
    """
    return len(g["aufgabe"].fehlerkatalog) >= 3


def handlich(p, g) -> bool:
    """Die Lösung muss im Kopf hinschreibbar bleiben."""
    w = g["wert"]
    if w is None:
        return True
    return abs(w.p) <= 200 and w.q <= 12


def nicht_verboten_leer(p, g) -> bool:
    """In 15.8 muss wirklich ein x im Nenner stehen."""
    return bool(g["verboten"])


STANDARD = [kopfrechenbar, fehler_eindeutig, drei, handlich,
            nicht_verboten_leer]
OHNE_X = [kopfrechenbar, fehler_eindeutig, drei, handlich]


# ══════════════════════════════════════════════════════════════════════════
# Zahlenvorräte — auf allen drei Stufen dieselben
# ══════════════════════════════════════════════════════════════════════════

def _vorrat(stufe):
    return {"k1": [2, 3, 4, 5], "k2": [2, 3, 5, 6], "z1": [1, 2, 3, 4],
            "z2": [2, 3, 4, 6], "stufe": [stufe]}


BEREICH = {"A": _vorrat(1), "B": _vorrat(2), "C": _vorrat(3)}


def _br(zaehler, k, c) -> T:
    """Ein Bruch mit linearem Nenner:  25/(x − 1)"""
    nt, nw = lin(k, c)
    return BR(zeige(Integer(zaehler)), Integer(zaehler), nt, nw), nw


# ══════════════════════════════════════════════════════════════════════════
# Die zwölf Bauformen
# ══════════════════════════════════════════════════════════════════════════

def bf1(p):
    """x nur im Nenner, im Kopf lösbar:  6/x = 3"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    if st == 1:
        t, nw = _br(k1 * k2, 1, 0)
        return bau("+", [t], "+", [ZA(k2)], nenner=[nw])
    if st == 2:
        t, nw = _br(k1 * k2, 1, -p["z1"])
        return bau("+", [t], "+", [ZA(k2)], nenner=[nw])
    t, nw = _br(k1 * k2 * 2, 2, -2 * p["z1"])
    return bau("+", [t], "+", [ZA(k2)], nenner=[nw])


BF1 = Bauform("BF1", "x nur im Nenner, im Kopf lösbar",
    bereiche=BEREICH, bauen=bf1, filter=STANDARD)


def bf2(p):
    """x im Nenner und ein bruchfreier Summand:  1/x + 1 = 3"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    t1, nw = _br(k1, 1, 0)
    if st == 1:
        return bau("++", [t1, ZA(p["z1"])], "+", [ZA(p["z1"] + k2)],
                   nenner=[nw])
    t2, _ = _br(k1 + k2, 1, 0)
    if st == 2:
        return bau("++", [t1, ZA(p["z1"])], "+", [t2], nenner=[nw])
    return bau("+-", [t1, ZA(p["z1"])], "++", [t2, ZA(p["z2"])], nenner=[nw])


BF2 = Bauform("BF2", "x im Nenner und ein bruchfreier Summand",
    bereiche=BEREICH, bauen=bf2, filter=STANDARD)


def bf3(p):
    """Terme mit x in beiden Nennern:  2/(x − 3) = 3/(x + 5)"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    if st == 1:
        #: Auf A steht links x allein im Nenner — das ist die Levelachse
        #: dieser Schablone: x allein, dann Term mit x, dann zwei
        #: verschiedene Terme.
        t1, n1 = _br(k1, 1, 0)
        t2, n2 = _br(k2, 1, p["z2"])
        return bau("+", [t1], "+", [t2], nenner=[n1, n2])
    if st == 2:
        t1, n1 = _br(k1, 1, -p["z1"])
        t2, n2 = _br(k2, 1, p["z2"])
        return bau("+", [t1], "+", [t2], nenner=[n1, n2])
    t1, n1 = _br(k1 * 2, 2, -2 * p["z1"])
    t2, n2 = _br(k2, 1, p["z2"])
    return bau("+", [t1], "+", [t2], nenner=[n1, n2])


BF3 = Bauform("BF3", "Terme mit x in beiden Nennern",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD)


def bf4(p):
    """Die Rechnung ergibt genau die Zahl, die D ausschliesst.

    Wegen dieser Bauform gibt es die Lektion. Rechnerisch kommt eine Zahl
    heraus — und genau dort wird der Nenner null. Gebaut wird rueckwaerts:
    zuerst die verbotene Stelle w, dann zwei Zaehler, die sich genau bei
    x = w schneiden.
    """
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    w = p["z1"]
    if st == 1:
        #: (x + k1)/(x − w) = (w + k1)/(x − w)
        nt, nw = lin(1, -w)
        links = BR(*lin(1, k1), nt, nw)
        rechts = BR(zeige(Integer(w + k1)), Integer(w + k1), nt, nw)
    elif st == 2:
        #: (k1·x + k2)/(2x − 2w) = (k1·w + k2)/(2x − 2w)
        nt, nw = lin(2, -2 * w)
        links = BR(*lin(k1, k2), nt, nw)
        rechts = BR(zeige(Integer(k1 * w + k2)), Integer(k1 * w + k2), nt, nw)
    else:
        #: (2x − k1)/(x + z2) = (x + c)/(x + z2), Schnittpunkt bei x = −z2
        nullstelle = -p["z2"]
        nt, nw = lin(1, p["z2"])
        links = BR(*lin(2, -k1), nt, nw)
        rechts = BR(*lin(1, 2 * nullstelle - k1 - nullstelle), nt, nw)
    return bau("+", [links], "+", [rechts], nenner=[nw])


BF4 = Bauform("BF4", "Die Rechnung ergibt eine Zahl, die D ausschliesst",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """Mehrere Brüche, zwei verschiedene Nenner:  1/x + 1/(2x) = 3"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    nt1, nw1 = lin(1, 0)
    nt2, nw2 = lin(2, 0)
    b1 = BR(zeige(Integer(k1)), Integer(k1), nt1, nw1)
    b2 = BR(zeige(Integer(k2)), Integer(k2), nt2, nw2)
    b3 = BR(zeige(Integer(k1 + k2)), Integer(k1 + k2), nt2, nw2)
    if st == 1:
        return bau("++", [b1, b2], "+", [ZA(p["z2"])], nenner=[nw1, nw2])
    if st == 2:
        return bau("++", [b1, b2], "++", [b3, ZA(p["z1"])],
                   nenner=[nw1, nw2])
    return bau("+-+", [b1, b2, b3], "+", [ZA(p["z1"] + p["z2"])],
               nenner=[nw1, nw2])


BF5 = Bauform("BF5", "Mehrere Brüche, zwei verschiedene Nenner",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD)


def bf6(p):
    """Lektion 15.7: der Nenner ist ein Term OHNE x:  (x + 3)/(2 + 4) = 2

    Der Nenner muss zuerst ausgerechnet werden. Ein x steckt nicht darin,
    also kann auch nichts verboten sein — genau darum ist das die Vorstufe
    zu 15.8.
    """
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    nt = f"{k1} + {k2}"
    nw = Integer(k1 + k2)
    if st == 1:
        links = BR(*lin(1, p["z1"]), nt, nw)
        return bau("+", [links], "+", [ZA(p["z2"])], nenner=[])
    if st == 2:
        links = BR(*lin(p["z1"], -p["z2"]), nt, nw)
        return bau("+", [links], "+", [ZA(p["z2"])], nenner=[])
    links = BR(*lin(p["z1"], -p["z2"]), f"{k1} · {k2}", Integer(k1 * k2))
    return bau("++", [links, ZA(p["z1"])], "+", [ZA(p["z2"] + 1)], nenner=[])


BF6 = Bauform("BF6", "Der Nenner ist ein Term ohne x (Lektion 15.7)",
    bereiche=BEREICH, bauen=bf6, filter=OHNE_X)


def bf7(p):
    """Der Nenner ist eine Summe mit x:  2/(x + 1) = 1"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    if st == 1:
        t, nw = _br(k1 * k2, 1, p["z1"])
        return bau("+", [t], "+", [ZA(k2)], nenner=[nw])
    if st == 2:
        t, nw = _br(k1 * k2 * 2, 2, p["z1"])
        return bau("+", [t], "+", [ZA(k2)], nenner=[nw])
    t, nw = _br(k1 * k2 * 2, 2, p["z1"])
    return bau("++", [t, ZA(p["z2"])], "+", [ZA(k2 + p["z2"])], nenner=[nw])


BF7 = Bauform("BF7", "Der Nenner ist eine Summe mit x",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def bf8(p):
    """Ein Bruch ist null — nur der Zähler zählt:  (x − 3)/(x + 2) = 0"""
    st, k1 = p["stufe"], p["k1"]
    if st == 1:
        nt, nw = lin(1, p["z2"])
        links = BR(*lin(1, -p["z1"]), nt, nw)
    elif st == 2:
        nt, nw = lin(2, p["z2"])
        links = BR(*lin(1, -p["z1"]), nt, nw)
    else:
        nt, nw = lin(1, p["z2"])
        links = BR(*lin(k1, k1 * p["z1"]), nt, nw)
    return bau("+", [links], "+", [ZA(0)], nenner=[nw])


BF8 = Bauform("BF8", "Ein Bruch ist null — nur der Zähler zählt",
    bereiche=BEREICH, bauen=bf8, filter=STANDARD)


def bf9(p):
    """Kehrwerte gleichgesetzt:  1/x = 1/5"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    if st == 1:
        t, nw = _br(1, 1, 0)
        return bau("+", [t], "+", [BR("1", Integer(1), zeige(Integer(k2)),
                                      Integer(k2))], nenner=[nw])
    if st == 2:
        t, nw = _br(k1, 2, 0)
        return bau("+", [t], "+", [BR("1", Integer(1),
                                      zeige(Integer(k2 * 2)),
                                      Integer(k2 * 2))], nenner=[nw])
    t, nw = _br(k1, 2, p["z1"])
    return bau("+", [t], "+", [BR("1", Integer(1), zeige(Integer(k2)),
                                  Integer(k2))], nenner=[nw])


BF9 = Bauform("BF9", "Kehrwerte gleichgesetzt",
    bereiche=BEREICH, bauen=bf9, filter=STANDARD)


def bf10(p):
    """Negativer Zähler:  −2/(x + 1) = 1"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    if st == 1:
        t, nw = _br(k1 * k2, 1, 0)
        return bau("-", [t], "+", [ZA(k2)], nenner=[nw])
    if st == 2:
        t, nw = _br(k1 * k2, 1, p["z1"])
        return bau("-", [t], "+", [ZA(k2)], nenner=[nw])
    t, nw = _br(k1 * k2 * 2, 2, -p["z1"])
    return bau("-", [t], "+", [ZA(k2)], nenner=[nw])


BF10 = Bauform("BF10", "Negativer Zähler",
    bereiche=BEREICH, bauen=bf10, filter=STANDARD)


def bf11(p):
    """Zwei Brüche mit x im Nenner, Zahl rechts:  1/x + 1/(2x) = 3/4"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    nt1, nw1 = lin(1, 0)
    nt2, nw2 = lin(2, 0)
    b1 = BR(zeige(Integer(k1)), Integer(k1), nt1, nw1)
    b2 = BR(zeige(Integer(k2)), Integer(k2), nt2, nw2)
    b3 = BR(zeige(Integer(k1)), Integer(k1), nt2, nw2)
    if st == 1:
        return bau("++", [b1, b2], "+", [ZA(p["z2"])], nenner=[nw1, nw2])
    if st == 2:
        return bau("+-", [b1, b2], "+", [ZA(p["z2"])], nenner=[nw1, nw2])
    return bau("+-+", [b1, b2, b3], "+", [ZA(p["z2"])], nenner=[nw1, nw2])


BF11 = Bauform("BF11", "Zwei Brüche mit x im Nenner, Zahl rechts",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD)


def bf12(p):
    """x steht in Zähler UND Nenner:  (x + 1)/(x − 1) = 3"""
    st, k1, k2 = p["stufe"], p["k1"], p["k2"]
    nt, nw = lin(1, -p["z1"])
    if st == 1:
        links = BR(*lin(1, 0), nt, nw)
    elif st == 2:
        links = BR(*lin(1, p["z2"]), nt, nw)
    else:
        nt, nw = lin(1, -p["z2"])
        links = BR(*lin(2, p["z1"]), nt, nw)
    return bau("+", [links], "+", [ZA(k2 + 1)], nenner=[nw])


BF12 = Bauform("BF12", "x steht in Zähler und Nenner",
    bereiche=BEREICH, bauen=bf12, filter=STANDARD)


S56 = Schablone(
    nr="S56", titel="Term im Nenner, x im Nenner",
    lektionen="15.7 – 15.8", erhebung="", anleitung=ANLEITUNG,
    levelachse="Struktur des Nenners und Anzahl Brüche",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee="Steht x im Nenner, wird zuerst geprüft, wann dieser Nenner "
             "null würde. Kommt am Schluss genau diese Zahl heraus, hat "
             "die Gleichung keine Lösung.")
