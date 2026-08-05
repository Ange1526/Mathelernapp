# -*- coding: utf-8 -*-
"""
Qualitätsfilter — hässliche Zufallsaufgaben verwerfen.

Ohne diese Filter erzeugt jeder Zufallsgenerator irgendwann Aufgaben, die
formal richtig, aber didaktisch wertlos oder schlicht gemein sind. Die
folgenden Fälle sind beim Durchrechnen der Schablonen tatsächlich aufgetreten.

Jeder Filter bekommt (parameter, gebaut) und gibt True zurück, wenn die
Aufgabe brauchbar ist.
"""
from __future__ import annotations

from sympy import Rational, factorint, expand

from korrektur.pruefung import Art


# ------------------------------------------------------------------ Lösung

def loesung_nicht_null(p, g) -> bool:
    """Lösung 0 ist fast immer ein Zufallsunfall.

    Wo sie didaktisch gewollt ist (Sonderfall-Bauformen), wird der Filter
    einfach nicht gesetzt.
    """
    l = g["aufgabe"].loesung
    return not (l.art is Art.EXPR and l.expr == 0)


def loesung_nicht_trivial(p, g) -> bool:
    """Lösung 1 oder −1 bei Termaufgaben: sieht aus wie ein Fehler."""
    l = g["aufgabe"].loesung
    return not (l.art is Art.EXPR and l.expr in (1, -1))


def nenner_freundlich(p, g, erlaubt=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15,
                                     16, 18, 20, 21, 24, 25, 27, 28, 30, 32,
                                     35, 36, 40, 42, 45, 48, 49, 50)) -> bool:
    """Kein Bruch mit Nenner 137.

    Ohne Taschenrechner muss der Nenner im Kopf handhabbar bleiben. Die Liste
    deckt alles ab, was aus Zahlen bis 50 entstehen kann und noch zumutbar ist.
    """
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    for teil in l.expr.atoms(Rational):
        if teil.q not in erlaubt:
            return False
    return True


def kopfrechenbar(p, g, grenze=1000) -> bool:
    """Kein Taschenrechner erlaubt: keine Zahl im Ergebnis über der Grenze."""
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    for teil in l.expr.atoms(Rational):
        if abs(teil.p) > grenze or teil.q > grenze:
            return False
    return True


# ------------------------------------------------------------------ Aufgabe

def parameter_verschieden(*namen):
    """Keine zwei gleichen Zahlen in den genannten Feldern.

    Sonst entstehen Aufgaben wie 6x + 6x, die anders aussehen als gemeint.
    """
    def f(p, g):
        werte = [p[n] for n in namen if n in p]
        return len(set(werte)) == len(werte)
    return f


def echt_zu_tun(p, g) -> bool:
    """Die Aufgabe muss überhaupt eine Umformung verlangen.

    Wenn Frage und Lösung sich nur in der Schreibweise unterscheiden, hat der
    Schüler nichts gelernt.
    """
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    return str(l.expr).replace(" ", "") != g["frage"].replace(" ", "").replace("·", "*")


# ------------------------------------------------------------------ Katalog

def fehler_eindeutig(p, g) -> bool:
    """Kein vorberechnetes Fehlerergebnis darf gleich der Lösung sein.

    Sonst diagnostiziert die App eine RICHTIGE Antwort als Fehler. Das ist
    beim Testlauf von S34 in sechs Bauformen vorgekommen — bei 47 − (2+4) + 8
    ergibt der Fehler «Minus nur aufs erste Glied» genau 49, also dasselbe wie
    die Lösung.

    Ausserdem dürfen zwei Fehler nicht dieselbe Zahl ergeben, sonst ist die
    Diagnose nicht eindeutig und der Schüler bekommt einen zufälligen der
    beiden Texte.
    """
    aufgabe = g["aufgabe"]
    if aufgabe.loesung.art is not Art.EXPR:
        return True
    ziel = expand(aufgabe.loesung.expr)
    gesehen = set()
    for f in aufgabe.fehlerkatalog:
        if f.ergebnis.art is not Art.EXPR:
            continue
        e = expand(f.ergebnis.expr)
        if e == ziel:
            return False
        schluessel = str(e)
        if schluessel in gesehen:
            return False
        gesehen.add(schluessel)
    return True


#: Der Satz, den jede Schablone bekommen sollte.
STANDARD = [nenner_freundlich, kopfrechenbar, fehler_eindeutig]


def faktor_ist_groesster(p, g) -> bool:
    """Der ausgeklammerte Faktor muss wirklich der grösste sein.

    Beim Testlauf aufgetreten: aus g=12, u=4, v=2 entsteht 48y² − 24y, und der
    Generator behauptete, der Faktor sei 12y. In der Klammer bleibt aber
    4y − 2, und darin steckt noch eine 2 — der grösste Faktor ist 24y.

    Die Schablone hätte dem Schüler also einen falschen Lösungsweg gezeigt.
    Der Filter verlangt: in der Klammer darf kein gemeinsamer Faktor mehr
    stecken, weder als Zahl noch als Variable.
    """
    klammer = g.get("klammer")
    if klammer is None:
        return True
    inhalt, rest = klammer.as_content_primitive()
    if inhalt != 1:
        return False
    # keine Variable, die in allen Summanden steckt
    from sympy import gcd
    summanden = rest.args if rest.is_Add else (rest,)
    if len(summanden) > 1:
        gemeinsam = summanden[0]
        for s in summanden[1:]:
            gemeinsam = gcd(gemeinsam, s)
        if gemeinsam != 1:
            return False
    return True


def symbole_verschieden(*namen):
    """Zwei Variablenplätze dürfen nicht dieselbe Variable erwischen.

    Beim Testlauf entstand `20u − 5 · (5u + 7u)` — beide Plätze hatten u
    gezogen. Die Aufgabe ist dann eine ganz andere als gemeint.
    """
    def f(p, g):
        werte = [p[n] for n in namen if n in p]
        return len(set(map(str, werte))) == len(werte)
    return f


def alle_sorten_bleiben(p, g) -> bool:
    """Keine Variablensorte darf sich zufällig ganz aufheben.

    `15w − 3(5w + 4b)` ergibt −12b: die w sind weg. Das ist ein legitimer
    Sonderfall, aber er gehört in eine eigene Bauform, nicht als Zufallstreffer
    in eine gewöhnliche — sonst sieht der Schüler eine Aufgabe, deren Ergebnis
    nichts mit dem Aufbau zu tun hat.
    """
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    erwartet = g.get("sorten")
    if not erwartet:
        return True
    vorhanden = {str(s) for s in expand(l.expr).free_symbols}
    return all(str(s) in vorhanden for s in erwartet)


def exponent_hoechstens(grenze: int = 10):
    """Kein Exponent über der Grenze — weder in der Lösung noch im Fehlerkatalog.

    `eingabe_parser` weist Exponenten über 10 als Sicherung ab. Ein Generator,
    der x^20 als Musterlösung baut, erzeugt damit eine Aufgabe, die der
    Schüler gar nicht beantworten KANN: seine richtige Eingabe wird als
    Eingabefehler abgewiesen.

    Beim Testlauf von S7 sind so 225 unlösbare Aufgaben entstanden.
    """
    from sympy import Pow

    def zu_hoch(ausdruck) -> bool:
        for teil in ausdruck.atoms(Pow):
            e = teil.exp
            if e.is_Integer and abs(int(e)) > grenze:
                return True
        return False

    def f(p, g):
        aufgabe = g["aufgabe"]
        if aufgabe.loesung.art is Art.EXPR and zu_hoch(aufgabe.loesung.expr):
            return False
        for fehler in aufgabe.fehlerkatalog:
            if fehler.ergebnis.art is Art.EXPR and zu_hoch(fehler.ergebnis.expr):
                return False
        return True

    return f
