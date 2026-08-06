# -*- coding: utf-8 -*-
"""
S45 · Einfache lineare Gleichungen      (Lektionen 13.1 – 13.4)

    «Löse die Gleichung.»
    x + 20 = 80        20 = 80 − x        5x + 6 = 21        −x = 9

Vorstufe zu den Erhebungsaufgaben 1a und 1b. Die erste Schablone im Projekt,
bei der die Aufgabe eine GLEICHUNG ist und nicht ein Term: gefragt ist der
Wert von x, nicht ein umgeformter Ausdruck.

MASSGEBEND IST DIE KORRIGIERTE FASSUNG aus `Runde1_S12_S45.docx`. Die
frühere Fassung hatte `(2/3)x = 6`, `x − 1/4 = 2/3` und `0.6x = 21`. Brüche
und Dezimalzahlen stehen bei 13.1 bis 13.4 nicht zur Verfügung — K2 liegt
nicht in der Voraussetzungskette. Erst 13.9 setzt 2.2 voraus; dort, in S47,
sind Bruchlösungen erlaubt und auch nötig.

LEVELACHSE (Teil 2 der Schablone, wörtlich):

    Vorzeichen der Zahlen   alles positiv  →  negative Zahl oder negative
                                              Lösung  →  wie B
    Anzahl Glieder          Minimum der Bauform  →  Minimum  →  ein Glied
                                                                mehr auf
                                                                einer Seite

Gesperrt bleibt die Rechenoperation: ob x addiert, abgezogen, malgenommen
oder geteilt wird, trennt die Bauformen voneinander und ist kein Regler.

Alle elf Bauformen der Schablone sind gebaut.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Expr, Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .schablone import Bauform, Schablone

x = symbole("x")[0]
VARS = {"x"}

#: Die Aufgabe ist eine Gleichung, die Antwort eine Zahl. Ohne den zweiten
#: Satz tippt die Schülerin «x = 60» — das kann der Parser nicht lesen.
ANLEITUNG = "Löse die Gleichung. Gib nur den Wert von x an."


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════
#
# Ein GLIED ist entweder eine Zahl oder ein Vielfaches von x:
#
#     Z(20)      ->  20          Anteil an x: 0,  Konstante: 20
#     X(1)       ->  x           Anteil an x: 1,  Konstante: 0
#     X(5)       ->  5x
#
# Eine SEITE ist ein Muster aus Vorzeichen und eine Liste von Gliedern —
# dieselbe Mechanik wie in `s6_punktrechnung`. Der Anzeigetext wird aus den
# Gliedern gebaut, NIE über `str()` eines SymPy-Ausdrucks: SymPy sortiert
# Summen alphabetisch um, und dann steht in der App eine andere Aufgabe, als
# gerechnet wurde.


@dataclass(frozen=True)
class Z:
    """Eine blosse Zahl."""
    wert: int

    @property
    def text(self) -> str:
        return zeige(Integer(self.wert))

    @property
    def anteil(self) -> int:
        return 0

    @property
    def konstante(self) -> int:
        return self.wert


@dataclass(frozen=True)
class X:
    """Ein Vielfaches von x.  X(1) -> x   ·   X(5) -> 5x   ·   X(-1) -> −x"""
    koeff: int = 1

    @property
    def text(self) -> str:
        if self.koeff == 1:
            return "x"
        if self.koeff == -1:
            return f"{MINUS}x"
        return f"{zeige(Integer(self.koeff))}x"

    @property
    def anteil(self) -> int:
        return self.koeff

    @property
    def konstante(self) -> int:
        return 0


@dataclass(frozen=True)
class XD:
    """x geteilt durch eine Zahl:  x : 20   ·   x : (−8)

    Bleibt linear — der Anteil an x ist 1/nenner. Die Klammer um einen
    negativen Nenner steht so in der Schablone.
    """
    nenner: int

    @property
    def text(self) -> str:
        n = zeige(Integer(self.nenner))
        return f"x : ({n})" if self.nenner < 0 else f"x : {n}"

    @property
    def anteil(self):
        return Rational(1, self.nenner)

    @property
    def konstante(self) -> int:
        return 0


@dataclass(frozen=True)
class ZD:
    """Eine Zahl geteilt durch x:  80 : x

    Die einzige Form der Schablone, bei der x im NENNER steht. Sie ist nicht
    linear, darum rechnet ihre Bauform die Lösung selbst aus. Teil 1 sagt
    dazu: sie gehört hierher, weil sie im Lehrmittel neben den anderen
    Grundformen steht — und weil sie bei den Bruchgleichungen (15.8, S56)
    wiederkommt.
    """
    zaehler: int

    @property
    def text(self) -> str:
        z = zeige(Integer(self.zaehler))
        return f"({z}) : x" if self.zaehler < 0 else f"{z} : x"

    @property
    def anteil(self) -> int:
        return 0

    @property
    def konstante(self) -> int:
        return 0


def reihe(muster, glieder) -> str:
    """Eine Seite hinschreiben:  «50 − x − 12»"""
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def _sammeln(muster, glieder):
    """(Anteil an x, Konstante) einer Seite."""
    anteil = konstante = 0
    for zeichen, g in zip(muster, glieder):
        vz = 1 if zeichen == "+" else -1
        anteil += vz * g.anteil
        konstante += vz * g.konstante
    return anteil, konstante


def loesen(links, rechts) -> Expr:
    """Die Lösung einer linearen Gleichung, ohne `solve`.

    `solve` ist hier zweimal unnötig: es kostet Zeit, und mit
    `positive=True` liefert es negative Lösungen gar nicht erst (CLAUDE.md,
    erste Falle). Bei einer linearen Gleichung genügt Kopfrechnen.
    """
    al, kl = _sammeln(*links)
    ar, kr = _sammeln(*rechts)
    if al == ar:
        return None                      # keine eindeutige Lösung
    return Rational(kr - kl, al - ar)


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Gleichung gerechnet
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 5 der Schablone nennt fünf Fehler. Sie stehen hier einmal und gelten
# für jede Bauform, in der sie auftreten können; dazu kommen zwei weitere,
# die aus derselben Verwechslung entstehen. Gefordert sind fünf EINTRÄGE je
# Aufgabe, darum werden mehr Kandidaten gerechnet, als am Schluss übrig
# bleiben — Doppelte und alles, was zufällig die Lösung trifft, fällt weg.


def kandidaten(links, rechts, loesung):
    ml, gl = links
    mr, gr = rechts
    al, kl = _sammeln(ml, gl)
    ar, kr = _sammeln(mr, gr)
    diff = al - ar
    raus = []
    if diff == 0:
        #: x steht im Nenner (BF6). Alles hier unten teilt durch `diff` und
        #: lieferte `zoo` — SymPys komplexe Unendlichkeit, die der Parser
        #: nicht lesen kann. Solche Bauformen bringen ihren Katalog selbst
        #: mit.
        return raus

    # 1 · Vorzeichen beim Hinüberbringen:  20 = 80 − x  ->  x = −60
    raus.append(F("vorzeichen_hinueber", -loesung,
        "Schau das Vorzeichen an. Was auf der einen Seite abgezogen wird, "
        "kommt auf der anderen dazu."))

    # 2 · Die Strichoperation in die falsche Richtung gerechnet:
    #     statt −20 wurde +20 gerechnet
    if kl != 0:
        raus.append(F("falsche_richtung", Rational(kr + kl, diff),
            f"Auf der linken Seite steht {zeige(Integer(kl))}. Um sie "
            f"wegzuschaffen, musst du auf BEIDEN Seiten das Gegenteil "
            f"rechnen."))

    # 3 · Nur auf einer Seite gerechnet — die rechte Seite blieb stehen
    if kl != 0:
        raus.append(F("nur_eine_seite", Rational(kr, diff),
            "Du hast nur links gerechnet. Was du auf einer Seite machst, "
            "musst du auf der anderen auch machen."))

    # 4 · Die Zahl der rechten Seite als Lösung abgeschrieben
    if kr != 0:
        raus.append(F("rechte_zahl_abgeschrieben", Integer(kr),
            "Rechts steht das Ergebnis der ganzen Seite, nicht der Wert von "
            "x. Die Gleichung ist noch nicht aufgelöst."))

    # 5 · Bei mehreren Zahlen auf einer Seite nur die erste verrechnet
    zahlen_links = [(zn, g) for zn, g in zip(ml, gl) if g.anteil == 0]
    if len(zahlen_links) > 1:
        erste = zahlen_links[0][1].konstante * (1 if zahlen_links[0][0] == "+"
                                                else -1)
        raus.append(F("nur_erste_zahl", Rational(kr - erste, diff),
            "Auf der linken Seite stehen zwei Zahlen. Beide müssen weg, "
            "nicht nur die erste."))

    # 6 · Die Zahl der linken Seite als Lösung abgeschrieben
    if kl != 0:
        raus.append(F("linke_zahl_abgeschrieben", Integer(kl),
            f"{zeige(Integer(kl))} steht in der Gleichung, ist aber nicht "
            f"der Wert von x."))

    # 7 · Die Zahl doppelt abgezogen — links weggeschafft UND rechts
    #     nochmals von der schon verkleinerten Seite
    if kl != 0:
        raus.append(F("doppelt_abgezogen", Rational(kr - 2 * kl, diff),
            f"{zeige(Integer(abs(kl)))} wird EINMAL auf beiden Seiten "
            f"weggerechnet, nicht zweimal auf derselben."))

    # 8 · Statt geteilt malgenommen — der Fehler aus Teil 5:
    #     x : 20 = 80  ->  x = 4   und   20x = 80  ->  x = 1600
    if abs(diff) != 1 and kr - kl != 0:
        raus.append(F("mal_statt_geteilt", (kr - kl) * diff,
            f"Vor dem x steht {zeige(diff)}. Zum Auflösen wird durch "
            f"{zeige(diff)} GETEILT, nicht malgenommen — oder umgekehrt."))

    # 9 · Zähler und Nenner vertauscht
    if abs(diff) != 1 and kr - kl != 0:
        raus.append(F("kehrwert", Rational(diff, kr - kl) if kr - kl != 0
                      else Integer(0),
            "Der Kehrwert steht verkehrt herum. Teile das Ergebnis der "
            "rechten Seite durch die Zahl vor dem x."))

    # 10 · Der Koeffizient wurde abgezogen statt geteilt
    if abs(diff) != 1 and kr - kl != 0:
        zahl = diff if abs(diff) > 1 else Rational(1, diff)
        raus.append(F("koeffizient_abgezogen", (kr - kl) - zahl,
            f"{zeige(zahl)} steht nicht neben dem x, sondern davor — das ist "
            f"eine Punktrechnung, keine Strichrechnung."))

    # 11 · Die Differenz verkehrt herum gebildet
    if diff != 0 and kr - kl != kl - kr:
        raus.append(F("differenz_vertauscht", Rational(kl - kr, diff),
            "Achte auf die Richtung: gefragt ist, was von der einen Seite "
            "auf der anderen übrig bleibt."))

    # 7 · Durch den Koeffizienten nicht geteilt
    if abs(diff) != 1:
        raus.append(F("nicht_geteilt", Integer(kr - kl),
            f"Vor dem x steht {zeige(Integer(diff))}. Zum Schluss musst du "
            f"noch durch {zeige(Integer(diff))} teilen."))

    return raus


def siebe(fehler, loesung):
    """Doppelte und die Lösung selbst aus dem Katalog entfernen."""
    raus, gesehen = [], set()
    ziel = sympify(loesung)
    for f in fehler:
        e = f.ergebnis.expr
        if e is None or sympify(e) == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Der gemeinsame Bauplan
# ══════════════════════════════════════════════════════════════════════════

TIPPS = [
    "Was du auf einer Seite machst, musst du auf der anderen auch machen.",
    "Schaff zuerst die Zahl weg, die addiert oder abgezogen wird. Die Zahl "
    "vor dem x kommt danach.",
    "",
]


def bau(links, rechts, extra=(), schritte=None, loesung=None):
    l = loesen(links, rechts) if loesung is None else sympify(loesung)
    if l is None:
        #: Kommt vor, wenn sich x auf beiden Seiten aufhebt. Der Filter
        #: verwirft die Aufgabe dann.
        return {"frage": "", "loesung_text": "", "links": links,
                "rechts": rechts,
                "aufgabe": Aufgabe(loesung=Loesung.zahl(0), variablen=VARS,
                                   zielform=Zielform.BELIEBIG,
                                   fehlerkatalog=[]),
                "schritte": [], "tipps": TIPPS, "ungueltig": True}
    frage = f"{reihe(*links)} = {reihe(*rechts)}"
    fehler = siebe(list(extra) + kandidaten(links, rechts, l), l)
    al, kl = _sammeln(*links)
    ar, kr = _sammeln(*rechts)
    diff, rest = al - ar, kr - kl
    return {
        "frage": frage,
        "loesung_text": zeige(l),
        "links": links, "rechts": rechts, "ungueltig": False,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                           zielform=Zielform.BELIEBIG, fehlerkatalog=fehler),
        "schritte": schritte or [
            ("Anschauen, was mit x geschieht", frage),
            ("Die Strichoperation wegschaffen — auf beiden Seiten",
             f"{zeige(Integer(diff))}x = {zeige(Integer(rest))}"
             if diff != 1 else f"x = {zeige(Integer(rest))}"),
            ("Dann die Punktoperation — auf beiden Seiten",
             f"x = {zeige(l)}"),
            ("Probe: die Lösung einsetzen", f"x = {zeige(l)}"),
        ],
        "tipps": [TIPPS[0], TIPPS[1],
                  f"Schaff zuerst die Zahlen weg. Am Schluss steht "
                  f"x = {zeige(l)}."],
    }


# ── Filter ────────────────────────────────────────────────────────────────

def loesbar(p, g) -> bool:
    return not g.get("ungueltig")


def fuenf_fehler(p, g) -> bool:
    """Fünf Einträge im Fehlerkatalog — so verlangt es der Auftrag.

    Wer nur drei bekommt, diagnostiziert die Hälfte der falschen Antworten
    mit «Das stimmt leider nicht».
    """
    return len(g["aufgabe"].fehlerkatalog) >= 5


def ganzzahlig(p, g) -> bool:
    """Bruchlösungen gehören erst zu 13.9, also zu S47."""
    l = g["aufgabe"].loesung.expr
    return bool(getattr(l, "is_Integer", False))


def nicht_null(p, g) -> bool:
    """Lösung null ist der Sonderfall BF10, kein Zufallstreffer."""
    return g["aufgabe"].loesung.expr != 0


STANDARD = [loesbar, kopfrechenbar, fehler_eindeutig, fuenf_fehler,
            ganzzahlig, nicht_null]


# ══════════════════════════════════════════════════════════════════════════
# Die Bauformen
# ══════════════════════════════════════════════════════════════════════════
#
# Level A: alles positiv, Minimum an Gliedern.
# Level B: eine negative Zahl oder eine negative Lösung, gleich viele Glieder.
# Level C: ein Glied mehr auf einer Seite.

#: Zahlenvorrat. Auf allen drei Stufen derselbe — die Zahlengrösse ist NICHT
#: die Levelachse.
ZAHL = [5, 7, 8, 12, 20, 31]
KLEIN = [4, 5, 6, 7, 8, 9]

BEREICH = {
    "A": {"a": ZAHL, "b": KLEIN, "vz": [1], "extra": [False]},
    "B": {"a": ZAHL, "b": KLEIN, "vz": [-1], "extra": [False]},
    "C": {"a": ZAHL, "b": KLEIN, "vz": [1, -1], "extra": [True]},
}


def bf1(p):
    """x plus eine Zahl:  x + 20 = 80

    B kehrt das Ergebnis um (x + 31 = 21 ergibt −10), C hängt ein zweites
    Glied an (x + 12 + 9 = 40).
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    if p["extra"]:
        links = ("+++", (X(1), Z(b), Z(b + 3)))
        rechts = ("+", (Z(a + b + b + 3 + 7 * vz),))
    else:
        links = ("++", (X(1), Z(a)))
        #: Auf B steht rechts eine NEGATIVE Zahl. Eine bloss negative
        #: Loesung wuerde man der Aufgabe nicht ansehen — dann haetten A und
        #: B denselben Aufbau, und genau das verbietet die Levelachse.
        rechts = ("-", (Z(b),)) if vz < 0 else ("+", (Z(a + b),))
    return bau(links, rechts)


BF1 = Bauform("BF1", "x plus eine Zahl",
    bereiche=BEREICH, bauen=bf1, filter=STANDARD)


def bf2(p):
    """x minus eine Zahl:  x − 20 = 80"""
    a, b, vz = p["a"], p["b"], p["vz"]
    if p["extra"]:
        links = ("+--", (X(1), Z(b), Z(b + 2)))
        rechts = ("+", (Z(a),))
    else:
        links = ("+-", (X(1), Z(a)))
        #: Auf B steht rechts eine negative Zahl — x − 7 = −13.
        rechts = ("-", (Z(b),)) if vz < 0 else ("+", (Z(a + b),))
    return bau(links, rechts)


BF2 = Bauform("BF2", "x minus eine Zahl",
    bereiche=BEREICH, bauen=bf2, filter=STANDARD)


def bf3(p):
    """x wird von einer Zahl abgezogen:  20 = 80 − x

    Die Vorzeichenfalle der Schablone. Auf A steht die Gleichung
    umgedreht — x rechts, die Zahl links.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    if p["extra"]:
        #: 50 − x − 12 = 15
        links = ("+--", (Z(a + b + 12), X(1), Z(12)))
        rechts = ("+", (Z(b),))
    elif vz < 0:
        #: 31 − x = 40  ergibt  x = −9
        links = ("+-", (Z(a), X(1)))
        rechts = ("+", (Z(a + b),))
    else:
        #: 20 = 80 − x  —  x steht auf der rechten Seite
        links = ("+", (Z(b),))
        rechts = ("+-", (Z(a + b), X(1)))
    return bau(links, rechts)


BF3 = Bauform("BF3", "x wird von einer Zahl abgezogen",
    bereiche=BEREICH, bauen=bf3, filter=STANDARD)


def bf4(p):
    """Zahl mal x:  20x = 80

    B dreht das Vorzeichen des Koeffizienten um (−5x = 15), C hängt ein
    zweites Glied auf der rechten Seite an (20x = −80 − 40).
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    k = b * vz
    if p["extra"]:
        #: 20x = −80 − 40
        links = ("+", (X(b),))
        rechts = ("--", (Z(b * 4), Z(b * 2)))
    else:
        links = ("+", (X(k),))
        rechts = ("+", (Z(k * (a % 7 + 2)),))
    return bau(links, rechts)


BF4 = Bauform("BF4", "Zahl mal x",
    bereiche=BEREICH, bauen=bf4, filter=STANDARD)


def bf5(p):
    """x geteilt durch eine Zahl:  x : 20 = 80"""
    a, b, vz = p["a"], p["b"], p["vz"]
    if p["extra"]:
        #: x : 6 = 12 − 4.  Beide Zahlen rechts muessen echt positiv sein,
        #: sonst steht «7 − 0» da.
        links = ("+", (XD(b),))
        rechts = ("+-", (Z(a + b), Z(b)))
    else:
        links = ("+", (XD(b * vz),))
        rechts = ("+", (Z(a),))
    return bau(links, rechts)


BF5 = Bauform("BF5", "x geteilt durch eine Zahl",
    bereiche=BEREICH, bauen=bf5, filter=STANDARD)


def bf6(p):
    """Zahl geteilt durch x — x steht im Nenner:  80 : x = 20

    Nicht linear, darum wird die Lösung hier ausgerechnet und nicht über
    `loesen()` bestimmt: aus a : x = b folgt x = a : b.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    zaehler = b * (a % 5 + 3) * vz
    if p["extra"]:
        #: (−52) : x = 20 − 7   —   ein Glied mehr auf der rechten Seite
        links = ("+", (ZD(zaehler),))
        rechts = ("+-", (Z(b + 7), Z(7)))
        nenner = b
    else:
        links = ("+", (ZD(zaehler),))
        rechts = ("+", (Z(b),))
        nenner = b
    l = Rational(zaehler, nenner)
    return bau(links, rechts, loesung=l, extra=[
        F("mal_statt_geteilt_nenner", Integer(zaehler) * nenner,
          f"{zeige(Integer(zaehler))} wird durch x geteilt. Um x zu "
          f"bekommen, teilst du {zeige(Integer(zaehler))} durch das Ergebnis "
          f"der rechten Seite."),
        F("kehrwert_nenner", Rational(nenner, zaehler),
          "Zähler und Nenner stehen verkehrt herum."),
        F("zaehler_abgeschrieben", Integer(zaehler),
          f"{zeige(Integer(zaehler))} steht über dem Bruchstrich, ist aber "
          f"nicht der Wert von x."),
        F("differenz", Integer(zaehler - nenner),
          "Hier wird geteilt, nicht subtrahiert."),
        F("vorzeichen_nenner", -l,
          "Zähl die Minuszeichen: minus durch minus ergibt plus."),
    ])


BF6 = Bauform("BF6", "Zahl geteilt durch x — x steht im Nenner",
    bereiche=BEREICH, bauen=bf6, filter=STANDARD)


def bf7(p):
    """Zahl mal x, plus eine Zahl — zwei Schritte:  5x + 6 = 21

    Der Kern von Lektion 13.2: erst die Strich-, dann die Punktoperation.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    k, l = b, (a % 4 + 2) * vz
    if p["extra"]:
        #: 5x + 6 + 4 = 30
        links = ("+++", (X(k), Z(b), Z(b + 2)))
        rechts = ("+", (Z(k * 4 + b + b + 2),))
    else:
        links = ("++", (X(k), Z(b + 1)))
        rechts = ("+", (Z(k * l + b + 1),))
    return bau(links, rechts)


BF7 = Bauform("BF7", "Zahl mal x, plus eine Zahl — zwei Schritte",
    bereiche=BEREICH, bauen=bf7, filter=STANDARD)


def bf8(p):
    """x wird abgezogen, zwei Schritte:  38 − 4x = 10

    Die Vorzeichenfalle: aus 38 − 4x = 10 folgt −4x = −28, und minus durch
    minus ergibt +7.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    #: Die Loesung wird vorgegeben und die rechte Seite daraus gerechnet —
    #: sonst kommt bei zufaelligen Zahlen fast immer ein Bruch heraus.
    #: Auf A bleibt rechts eine positive Zahl, auf B eine negative — das
    #: ist der Vorzeichenregler von Teil 2. Ohne diesen Unterschied haetten
    #: A und B denselben Aufbau.
    ziel = 2 if vz > 0 else 3
    k = b * 3
    kopf = b * 8
    rest = kopf - k * ziel
    if p["extra"]:
        links = ("+-", (Z(kopf), X(k)))
        #: 2b dazu und wieder weg — so bleibt kein Nullglied stehen.
        rechts = ("+-", (Z(rest + 2 * b), Z(2 * b)))
    else:
        links = ("+-", (Z(kopf), X(k)))
        rechts = ("+", (Z(rest),))
    return bau(links, rechts)


BF8 = Bauform("BF8", "x wird abgezogen, zwei Schritte",
    bereiche=BEREICH, bauen=bf8, filter=STANDARD)


def bf9(p):
    """Verhältnis auf beiden Seiten:  60 : x = 80 : 20

    Rechts steht ein ausrechenbarer Quotient, links x im Nenner — nicht
    linear, darum wieder mit eigener Lösung und eigenem Katalog.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    q = (a % 4 + 2) * vz
    zaehler = b * q * (2 if p["extra"] else 1)
    links = ("+", (ZD(zaehler),))
    #: 80 : 20 — der rechte Quotient ergibt q
    rechts = ("+", (Z(q * 4),)) if not p["extra"] else ("+", (Z(q * 4),))
    l = Rational(zaehler, q * 4) if q * 4 != 0 else None
    frage_rechts = ("+", (Z(q * 4),))
    return bau(links, frage_rechts, loesung=Rational(zaehler, q * 4), extra=[
        F("mal_statt_geteilt_v", Integer(zaehler) * q * 4,
          "Bei einem Verhältnis wird geteilt, nicht malgenommen."),
        F("kehrwert_v", Rational(q * 4, zaehler),
          "Zähler und Nenner stehen verkehrt herum."),
        F("zaehler_abgeschrieben_v", Integer(zaehler),
          "Das ist der Zähler, nicht der Wert von x."),
        F("rechte_seite_v", Integer(q * 4),
          "Rechts steht das Ergebnis des Verhältnisses, nicht x."),
        F("vorzeichen_v", -Rational(zaehler, q * 4),
          "Zähl die Minuszeichen: minus durch minus ergibt plus."),
    ])


BF9 = Bauform("BF9", "Verhältnis auf beiden Seiten",
    bereiche=BEREICH, bauen=bf9, filter=STANDARD)


def bf10(p):
    """Sonderfall: die Lösung ist null:  4x = 0  ·  7x + 12 = 12

    Muss gezielt gebaut werden — bei zufälligen Zahlen kommt null praktisch
    nie vor. So steht es auch in Teil 1.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    k = b * vz
    if p["extra"]:
        #: 7x + 12 = 12
        links = ("++", (X(b), Z(a)))
        rechts = ("+", (Z(a),))
    else:
        links = ("+", (X(k),))
        rechts = ("+", (Z(0),))
    return bau(links, rechts, loesung=0, extra=[
        F("koeffizient_als_loesung", Integer(k),
          f"Die Zahl vor dem x ist nicht die Lösung. {zeige(Integer(k))} mal "
          f"null ergibt null — x ist null."),
        F("eins", Integer(1),
          "Null geteilt durch irgendetwas bleibt null, nicht eins."),
        F("konstante", Integer(a),
          "Auf beiden Seiten steht dieselbe Zahl. Sie fällt weg, und übrig "
          "bleibt nur das x."),
        F("negativ_eins", Integer(-1),
          "Es bleibt nichts übrig, was x von null verschieden macht."),
        F("summe", Integer(a + b),
          "Die Zahlen der Aufgabe sind nicht die Lösung."),
    ])


BF10 = Bauform("BF10", "Sonderfall: die Lösung ist null",
    bereiche=BEREICH, bauen=bf10,
    filter=[loesbar, kopfrechenbar, fehler_eindeutig, fuenf_fehler])


def bf11(p):
    """Minuszeichen direkt vor dem x:  −x = 9

    Wer das Minus übersieht, schreibt x = 9 statt x = −9.
    """
    a, b, vz = p["a"], p["b"], p["vz"]
    if p["extra"]:
        #: −x + 8 = 15
        links = ("++", (X(-1), Z(b)))
        rechts = ("+", (Z(a),))
    else:
        links = ("+", (X(-1),))
        rechts = ("+", (Z(a * vz),))
    l = loesen(links, rechts)
    #: Vor dem x steht −1. Damit faellt fast jeder allgemeine Kandidat weg,
    #: darum bringt diese Bauform ihre fuenf Eintraege selbst mit.
    return bau(links, rechts, extra=[
        F("minus_uebersehen", -l,
          "Vor dem x steht ein Minus. Multiplizierst du beide Seiten mit "
          "−1, dreht sich das Vorzeichen der Lösung um."),
        F("differenz_zahlen", Integer(a * vz - b),
          "Hier wird nichts subtrahiert: das Minus gehört zum x."),
        F("nur_zahl_links", Integer(b),
          "Die Zahl auf der linken Seite muss zuerst weg — und zwar auf "
          "beiden Seiten."),
        F("summe_beider", Integer(a * vz + b),
          "Hier wird nichts addiert: das Minus vor dem x wird aufgelöst."),
        F("kehrwert_eins", Integer(1),
          "−x heisst −1 · x. Zum Auflösen teilst du durch −1, das dreht nur "
          "das Vorzeichen."),
    ])


BF11 = Bauform("BF11", "Minuszeichen direkt vor dem x",
    bereiche=BEREICH, bauen=bf11, filter=STANDARD)


S45 = Schablone(
    nr="S45", titel="Einfache lineare Gleichungen",
    lektionen="13.1 – 13.4", erhebung="Vorstufe zu 1a",
    anleitung=ANLEITUNG,
    levelachse="Vorzeichen und Gliederzahl",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11],
    kernidee=("Eine Gleichung bleibt richtig, solange du auf beiden Seiten "
              "dasselbe tust. Löse zuerst die Strich-, dann die "
              "Punktoperation auf."),
)
