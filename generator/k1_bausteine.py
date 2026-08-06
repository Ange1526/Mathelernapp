# -*- coding: utf-8 -*-
"""
Bausteine für Kapitel 1 — Vorzeichen, Zahlengerade, Grundoperationen.

Kapitel 1 hat keine `.docx`-Schablone. Die Bauformen sind aus den
Lektionstiteln in `netz_daten.py` entwickelt, und dieser Baukasten hält
zusammen, was alle vier Schablonen (S1, S3, S5, S6) gemeinsam brauchen.

WARUM EIN EIGENER BAUKASTEN UND NICHT `s9_division` ODER `s10_klammern_neu`:
in Kapitel 1 gibt es noch keine Variablen, dafür etwas, das später nie mehr
vorkommt — das VORZEICHEN als eigenes Zeichen neben dem Operationszeichen.
`8 − (−3)` hat zwei Minus mit ganz verschiedenen Aufgaben, und genau diese
Unterscheidung ist Lektion 1.3. Ein Baustein, der das Vorzeichen in die Zahl
schiebt, kann die Aufgabe gar nicht mehr stellen.

    Z(-7)                  −7          eine Zahl, das Minus gehört ihr
    Z(9, mit_plus=True)    +9          mit ausgeschriebenem Vorzeichen
    VZ("−", Z(-7))         −(−7)       ein Vorzeichen VOR einer Zahl
    K(Z(8), ("−", Z(-3)))  8 − (−3)    Operationszeichen zwischen Zahlen

DER RECHNER kennt Punkt vor Strich und rechnet sonst von links nach rechts.
Beide Regeln lassen sich abschalten — daraus entstehen die Fehlerkandidaten,
und zwar als ECHTE Rechnung nach der falschen Regel, nicht als geratene Zahl.

Alle Ergebnisse sind ganze Zahlen. Divisionen werden rückwärts gebaut
(Quotient mal Divisor), damit nie ein Bruch entsteht — Brüche sind Kapitel 2.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform

ANLEITUNG = "Rechne aus."

PUNKT = ("·", ":")
STRICH = ("+", "−")


def F(schluessel, ergebnis, text) -> Fehler:
    return Fehler(schluessel, Loesung.zahl(sympify(ergebnis)), text)


# ══════════════════════════════════════════════════════════════════════════
# Die Bausteine
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Z:
    """Eine Zahl. Ihr Vorzeichen gehört IHR, nicht der Rechnung."""
    zahl: int
    mit_plus: bool = False

    @property
    def wert(self):
        return Integer(self.zahl)

    def text(self, im_term: bool = False) -> str:
        if self.zahl < 0:
            roh = f"{MINUS}{abs(self.zahl)}"
            return f"({roh})" if im_term else roh
        if self.mit_plus:
            return f"(+{self.zahl})" if im_term else f"+{self.zahl}"
        return str(self.zahl)


@dataclass(frozen=True)
class VZ:
    """Ein Vorzeichen VOR einem Baustein:  −(−7)   ·   +(−4)   ·   −(3 − 8)

    Das ist Lektion 1.3 in Reinform. Das äussere Zeichen ist ein
    Vorzeichen, kein Operationszeichen — es steht vor nichts.
    """
    zeichen: str
    inhalt: object

    @property
    def wert(self):
        w = self.inhalt.wert
        return w if self.zeichen == "+" else -w

    def text(self, im_term: bool = False) -> str:
        innen = self.inhalt.text(im_term=False)
        zeichen = "+" if self.zeichen == "+" else MINUS
        return f"{zeichen}({innen})"


@dataclass(frozen=True)
class Kl:
    """Klammern um einen Baustein, auch wenn er ganz vorne steht:  (−5) + (−3)

    Im Lehrmittel steht die erste negative Zahl einer Summe in Klammern.
    Ohne diesen Baustein würde daraus `−5 + (−3)`, und das sieht nach einer
    anderen Aufgabe aus, als es ist.
    """
    inhalt: object

    @property
    def wert(self):
        return self.inhalt.wert

    def text(self, im_term: bool = False) -> str:
        return self.inhalt.text(im_term=True)


@dataclass(frozen=True)
class K:
    """Eine Rechenkette:  8 − (−3) + 5

    `schritte` ist eine Folge von (Operationszeichen, Baustein).
    """
    erst: object
    schritte: tuple

    @property
    def wert(self):
        return rechne(self)

    def text(self, im_term: bool = False) -> str:
        teile = [self.erst.text(im_term=False)]
        for op, atom in self.schritte:
            teile.append(op)
            teile.append(atom.text(im_term=True))
        roh = " ".join(teile)
        return f"({roh})" if im_term else roh


def kette(erst, *schritte) -> K:
    return K(erst, tuple(schritte))


# ══════════════════════════════════════════════════════════════════════════
# Der Rechner
# ══════════════════════════════════════════════════════════════════════════

class NichtRechenbar(Exception):
    """Division durch null — kommt nur in Fehlervarianten vor."""


def _verknuepfen(links, op, rechts):
    if op == "+":
        return links + rechts
    if op == MINUS or op == "−":
        return links - rechts
    if op == "·":
        return links * rechts
    if rechts == 0:
        raise NichtRechenbar
    return Rational(links, rechts)


def rechne(k: K, punkt_vor_strich: bool = True,
           punkt_von_rechts: bool = False):
    """Den Wert einer Kette bestimmen.

    Beide Regeln lassen sich abschalten. `punkt_vor_strich=False` rechnet
    stur von links nach rechts — das ist der Fehler aus Lektion 1.16.
    `punkt_von_rechts=True` faltet Mal und Geteilt von hinten — das ist der
    Fehler aus 1.17, wegen dem `36 : 6 : 2` als 12 statt 3 herauskommt.
    """
    werte = [k.erst.wert]
    ops = []
    for op, atom in k.schritte:
        ops.append(op)
        werte.append(atom.wert)

    if punkt_vor_strich:
        stellen = [i for i, op in enumerate(ops) if op in PUNKT]
        while stellen:
            i = stellen[-1] if punkt_von_rechts else stellen[0]
            werte[i] = _verknuepfen(werte[i], ops[i], werte[i + 1])
            del werte[i + 1]
            del ops[i]
            stellen = [j for j, op in enumerate(ops) if op in PUNKT]

    ergebnis = werte[0]
    for i, op in enumerate(ops):
        ergebnis = _verknuepfen(ergebnis, op, werte[i + 1])
    return ergebnis


# ══════════════════════════════════════════════════════════════════════════
# Der Fehlerkatalog, aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════

def _ohne_vorzeichen(atom):
    """Jede negative ZAHL als positive gelesen — das Vorzeichen übersehen.

    Das Vorzeichen VOR der Klammer bleibt dabei stehen: `−(−7)` wird zu
    `−(7)`, nicht zu `+(7)`. Genau so liest ein Schüler, der das innere
    Minus überliest — und nur so ist der Fehlerwert ein anderer als die
    Lösung.
    """
    if isinstance(atom, Z):
        return Z(abs(atom.zahl), atom.mit_plus)
    if isinstance(atom, Kl):
        return Kl(_ohne_vorzeichen(atom.inhalt))
    if isinstance(atom, VZ):
        return VZ(atom.zeichen, _ohne_vorzeichen(atom.inhalt))
    return K(_ohne_vorzeichen(atom.erst),
             tuple((op, _ohne_vorzeichen(a)) for op, a in atom.schritte))


def _minus_zu_plus(k: K) -> K:
    """Jedes Minus als Plus gelesen."""
    return K(k.erst, tuple((("+" if op == "−" else op), a)
                           for op, a in k.schritte))


def _klammer_nicht_gedreht(k: K) -> K:
    """`8 − (−3)` als `8 − 3` gerechnet.

    Der häufigste Fehler von Lektion 1.9: das Minuszeichen der Zahl wird
    gesehen, aber nicht mit dem Operationszeichen verrechnet.
    """
    neu = []
    for op, atom in k.schritte:
        if op == "−" and isinstance(atom, Z) and atom.zahl < 0:
            neu.append((op, Z(abs(atom.zahl))))
        elif op == "+" and isinstance(atom, Z) and atom.zahl < 0:
            neu.append((op, Z(abs(atom.zahl))))
        else:
            neu.append((op, atom))
    return K(k.erst, tuple(neu))


def _alle_zahlen(atom) -> list:
    """Jede Zahl, die in der Aufgabe steht — auch die in einer Klammer."""
    if isinstance(atom, Z):
        return [atom.zahl]
    if isinstance(atom, (Kl, VZ)):
        return _alle_zahlen(atom.inhalt)
    raus = _alle_zahlen(atom.erst)
    for _, a in atom.schritte:
        raus += _alle_zahlen(a)
    return raus


def _hat(k: K, zeichen) -> bool:
    return any(op in zeichen for op, _ in k.schritte)


def _negative(atom) -> int:
    """Wie viele negative ZAHLEN stehen in der Aufgabe?

    Gezählt wird, was dasteht, nicht was herauskommt: in `−(−7)` steht eine
    negative Zahl, obwohl der Baustein den Wert +7 hat. Nach dem Wert zu
    fragen hiesse, den Fehler «Vorzeichen übersehen» genau dort nicht
    anzubieten, wo er am ehesten passiert.
    """
    if isinstance(atom, Z):
        return 1 if atom.zahl < 0 else 0
    if isinstance(atom, (Kl, VZ)):
        return _negative(atom.inhalt)
    return _negative(atom.erst) + sum(_negative(a) for _, a in atom.schritte)


def kandidaten(k: K, loesung):
    """Die typischen Fehler dieses Kapitels — jeder als echte Rechnung
    nach der falschen Regel."""
    raus = []

    def versuch(schluessel, bauen, text):
        try:
            wert = bauen()
        except (NichtRechenbar, ZeroDivisionError):
            return
        if wert is None:
            return
        raus.append(F(schluessel, wert, text))

    #: 1 · Punkt vor Strich nicht beachtet, stur von links gerechnet.
    if _hat(k, PUNKT) and _hat(k, STRICH):
        versuch("von_links", lambda: rechne(k, punkt_vor_strich=False),
                "Punkt vor Strich: Mal und Geteilt kommen vor Plus und "
                "Minus, egal wo sie stehen.")

    #: 2 · Mehrere Punktoperationen von hinten gerechnet.
    if sum(1 for op, _ in k.schritte if op in PUNKT) > 1:
        versuch("punkt_von_rechts",
                lambda: rechne(k, punkt_von_rechts=True),
                "Stehen mehrere Mal und Geteilt nebeneinander, wird von "
                "LINKS nach rechts gerechnet.")

    #: 3 · Das Minuszeichen einer Zahl übersehen.
    if _negative(k) > 0:
        versuch("vorzeichen_uebersehen",
                lambda: rechne(_ohne_vorzeichen(k)),
                "Eine Zahl mit Minus davor ist kleiner als null. Das "
                "Vorzeichen gehört zur Zahl.")

    #: 4 · Zwei Minus hintereinander nicht zu einem Plus gemacht.
    if any(op in ("−", "+") and isinstance(a, Z) and a.zahl < 0
           for op, a in k.schritte):
        versuch("doppeltes_minus",
                lambda: rechne(_klammer_nicht_gedreht(k)),
                "Minus und Minus ergeben zusammen ein Plus: "
                "8 − (−3) ist 8 + 3.")

    #: 5 · Nur EINES von zwei doppelten Minus gedreht.
    #:     `11 − (−2) − (−5)` wird zu `11 + 2 − 5`. Wer den ersten Fall
    #:     erkennt und den zweiten übersieht, hat ein anderes Ergebnis als
    #:     wer beide übersieht — und braucht eine andere Rückmeldung.
    doppelte = [i for i, (op, a) in enumerate(k.schritte)
                if op == "−" and isinstance(a, Z) and a.zahl < 0]
    if len(doppelte) > 1:
        i = doppelte[-1]
        halb = K(k.erst,
                 k.schritte[:i]
                 + ((k.schritte[i][0], Z(abs(k.schritte[i][1].zahl))),)
                 + k.schritte[i + 1:])
        versuch("nur_eines_gedreht", lambda: rechne(halb),
                "Zwei Minus hintereinander ergeben ein Plus — das gilt an "
                "JEDER Stelle, nicht nur an der ersten.")

    #: 6 · Jedes Minus als Plus gelesen.
    if _hat(k, ("−",)):
        versuch("minus_als_plus", lambda: rechne(_minus_zu_plus(k)),
                "Zwischen den Zahlen steht ein Minus, kein Plus.")

    #: 7 · Das Vorzeichen des ganzen Ergebnisses gedreht.
    versuch("vorzeichen_gesamt", lambda: -sympify(loesung),
            "Zähl die Minuszeichen noch einmal — beim Ergebnis stimmt das "
            "Vorzeichen nicht.")

    #: 8 · Das Vorzeichen vorne auf die ganze Kette bezogen.
    #:     `−(−7) + 3` wird dann zu `−(−7 + 3)`. Ein Vorzeichen steht aber
    #:     nur vor SEINER Zahl, nicht vor allem, was danach kommt.
    if isinstance(k.erst, VZ) and k.schritte:
        rest = K(k.erst.inhalt, k.schritte)
        versuch("vorzeichen_auf_alles",
                lambda: (rechne(rest) if k.erst.zeichen == "+"
                         else -rechne(rest)),
                "Ein Vorzeichen gehört zu SEINER Zahl. Es gilt nicht für "
                "alles, was danach noch kommt.")

    #: 9 · Ein Glied vergessen — vorne oder hinten.
    if k.schritte:
        versuch("letztes_glied_vergessen",
                lambda: rechne(K(k.erst, k.schritte[:-1])),
                "Das letzte Glied gehört auch zur Aufgabe.")
        #: Auch beim Malnehmen: `6 · 9` und nur die 9 hingeschrieben. Nur
        #: bei der Division nicht — dort ist «die erste Zahl weglassen»
        #: keine Rechnung, die jemand ausführt.
        erst_op = k.schritte[0][0]
        #: Beim Malnehmen nur, wenn danach ausschliesslich weitere
        #: Punktoperationen kommen — sonst entstünde aus `48 · 3 : 8` der
        #: Fehlwert 3/8, und einen Bruch schreibt in Kapitel 1 niemand hin.
        rest_ganz = (erst_op != "·"
                     or all(op == "·" for op, _ in k.schritte[1:]))
        if erst_op in ("+", "−", "·") and rest_ganz:
            vorzeichen = -1 if erst_op == "−" else 1
            versuch("erstes_glied_vergessen",
                    lambda: vorzeichen * rechne(K(k.schritte[0][1],
                                                  k.schritte[1:])),
                    "Auch die Zahl ganz vorne zählt mit.")

    #: 10 · Das erste Rechenzeichen verwechselt.
    if k.schritte and k.schritte[0][0] in STRICH:
        gedreht = ("−" if k.schritte[0][0] == "+" else "+")
        versuch("zeichen_verwechselt",
                lambda: rechne(K(k.erst,
                                 ((gedreht, k.schritte[0][1]),)
                                 + k.schritte[1:])),
                "Schau noch einmal hin: steht dort ein Plus oder ein Minus?")

    #: 11 · Ein Minus vor einer KLAMMER nur auf das erste Glied darin
    #:      angewandt: `−(3 − 8)` wird zu `−3 − 8`. Das ist derselbe Fehler,
    #:      der im ganzen Netz am häufigsten nach 10.6 zurückführt — hier
    #:      kommt er zum ersten Mal vor.
    if isinstance(k.erst, VZ) and isinstance(k.erst.inhalt, K):
        innen = k.erst.inhalt
        vz = 1 if k.erst.zeichen == "+" else -1

        def nur_erstes():
            wert = vz * innen.erst.wert
            for op, atom in innen.schritte:
                wert = _verknuepfen(wert, op, atom.wert)
            return wert + _rest(k)

        versuch("nur_erstes_glied", nur_erstes,
                "Ein Minus vor der Klammer gilt für ALLES darin, nicht nur "
                "für das erste Glied.")

    #: 12 · Der Übertrag vergessen. Nur bei reinen Additionen — dort ist
    #:      es der einzige Fehler, der überhaupt noch vorkommt, und ohne
    #:      ihn hätte `7 + 5` bloss vier unterscheidbare Fehlwerte.
    zahlen = _alle_zahlen(k)
    if (k.schritte and all(op == "+" for op, _ in k.schritte)
            and all(z >= 0 for z in zahlen) and sum(zahlen) >= 10):
        versuch("uebertrag_vergessen",
                lambda: (sum(z // 10 for z in zahlen) * 10
                         + sum(z % 10 for z in zahlen) % 10),
                "Beim Zusammenzählen entsteht ein Übertrag: aus 7 + 5 wird "
                "12, nicht 2.")

    #: 13 · Die Punktoperation als Strichoperation gelesen: `48 : 6` wird
    #:      zu `48 − 6`. Bei der Division ist das der einzige Fehler ausser
    #:      dem Vorzeichen, der überhaupt vorkommt.
    if _hat(k, PUNKT):
        ersetzt = K(k.erst, tuple((("+" if op == "·" else
                                    ("−" if op == ":" else op)), a)
                                  for op, a in k.schritte))
        versuch("punkt_als_strich", lambda: rechne(ersetzt),
                "Der Punkt zwischen den Zahlen heisst mal beziehungsweise "
                "geteilt, nicht plus oder minus.")

    #: 14 · Mal und Geteilt verwechselt. Nur, wenn dabei eine ganze Zahl
    #:      herauskommt — einen Bruch schreibt in Kapitel 1 niemand hin.
    for i, (op, _) in enumerate(k.schritte):
        if op in PUNKT:
            anders = ":" if op == "·" else "·"
            getauscht = K(k.erst,
                          k.schritte[:i]
                          + ((anders, k.schritte[i][1]),)
                          + k.schritte[i + 1:])

            def punkt_getauscht():
                wert = rechne(getauscht)
                return wert if sympify(wert).is_Integer else None

            versuch("punkt_verwechselt", punkt_getauscht,
                    "Schau das Rechenzeichen noch einmal an: heisst es mal "
                    "oder geteilt?")
            break

    #: 15 · Alles addiert, kein Zeichen beachtet.
    versuch("alles_addiert",
            lambda: sum(abs(z) for z in _alle_zahlen(k)),
            "Nicht jedes Zeichen in dieser Aufgabe ist ein Plus.")

    #: 16 · Alles abgezogen — der Gegenfall.
    #:      `4 − 9` wird zu −13 statt −5: beide Zahlen als negativ gelesen.
    if k.schritte or isinstance(k.erst, VZ):
        versuch("alles_abgezogen",
                lambda: -sum(abs(z) for z in _alle_zahlen(k)),
                "Nur die Zahlen HINTER einem Minus werden abgezogen, nicht "
                "auch die erste.")

    return raus


def _rest(k: K):
    """Was nach dem ersten Baustein noch kommt, als Zahl."""
    wert = Integer(0)
    for op, atom in k.schritte:
        wert = _verknuepfen(wert, op, atom.wert)
    return wert


def siebe(fehler, loesung):
    """Doppelte weg und alles, was gleich der Lösung ist."""
    raus, gesehen = [], set()
    ziel = sympify(loesung)
    for fe in fehler:
        e = fe.ergebnis.expr
        if e is None or e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(fe)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Bauen
# ══════════════════════════════════════════════════════════════════════════

def bau(k: K, schritte=None, tipps=None, extra=()):
    """Aus einer Kette wird eine fertige Aufgabe."""
    l = rechne(k)
    frage = k.text()
    fehler = siebe(list(extra) + kandidaten(k, l), l)
    return {
        "frage": frage,
        "loesung_text": zeige(l),
        "kette": k,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=set(),
                           zielform=Zielform.BELIEBIG, fehlerkatalog=fehler),
        "schritte": schritte or [("Die Aufgabe anschauen", frage),
                                 ("Ausrechnen", zeige(l))],
        "tipps": tipps or [
            "Schau zuerst, welche Zeichen Vorzeichen sind und welche "
            "Operationszeichen.",
            "Rechne Mal und Geteilt zuerst, dann Plus und Minus — und "
            "innerhalb einer Sorte von links nach rechts.",
            f"Am Schluss steht {zeige(l)}."],
    }


# ══════════════════════════════════════════════════════════════════════════
# Filter
# ══════════════════════════════════════════════════════════════════════════

def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def drei(p, g) -> bool:
    """Für die Sonderfälle mit Ergebnis null oder eins.

    Dort fallen die meisten gerechneten Fehler auf denselben Wert — mehr
    als drei unterscheidbare gibt es nicht. Lieber drei echte als fünf
    ausgedachte.
    """
    return len(g["aufgabe"].fehlerkatalog) >= 3


def ganz(p, g) -> bool:
    """Kapitel 1 kennt noch keine Brüche."""
    w = g["aufgabe"].loesung.expr
    return w is not None and sympify(w).is_Integer


def nicht_null(p, g) -> bool:
    return g["aufgabe"].loesung.expr != 0


def klein(p, g, grenze=200) -> bool:
    """Im Kopf rechenbar: kein Zwischenschritt und kein Ergebnis über 200."""
    return abs(sympify(g["aufgabe"].loesung.expr)) <= grenze


STANDARD = [kopfrechenbar, klein, ganz, fehler_eindeutig, fuenf, nicht_null]
SONDER = [kopfrechenbar, klein, ganz, fehler_eindeutig, drei]


def BF(nr, beschreibung, bereiche, bauen, filter=None) -> Bauform:
    return Bauform(nr, beschreibung, bereiche=bereiche, bauen=bauen,
                   filter=filter or STANDARD)
