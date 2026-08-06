# -*- coding: utf-8 -*-
"""
S46 · Klammern, Variablen auf beiden Seiten   (Lektionen 13.5 – 13.6)
S47 · Klammern beidseitig, Lösung als Bruch   (Lektionen 13.7 – 13.9)

    «Löse die Gleichung.»
    2(x + 3) = 10      3x + 2 = x + 10      2x − (3 + 4x) = 9
    5x + 10(2 − 6x) = 22 − 6(x − 2)     →  x = −2/7   (Erhebung 1a)

Zusammen mit S45 ist Kapitel 13 damit bis auf die Gemischt-Lektion 13.10
vollständig, und **Erhebungsaufgabe 1a ist übbar**: sie steht als S47/BF1 auf
Level C.

Der Unterschied zwischen den beiden: bei S46 ist die Lösung immer ganzzahlig,
weil K2 nicht in der Kette von 13.5 und 13.6 liegt. Erst 13.9 setzt 2.2
voraus — dort, in S47, darf die Lösung ein Bruch sein, und der letzte Schritt
ist immer derselbe: kürzen.

LEVELACHSE (Teil 2, wörtlich):

    S46   Anzahl Glieder   zwei bis drei → drei bis vier → vier bis fünf
    S46   Vorzeichen       positiv       → ein Minus     → mehrere Minus
    S47   Struktur der Lösung — ganzzahlig, Bruch, gekürzter Bruch

DREI ANTWORTEN SIND MÖGLICH, nicht nur eine Zahl: eine Gleichung kann auch
KEINE LÖSUNG haben (8 = 0) oder von JEDER ZAHL erfüllt werden (6 = 6). Beides
sind eigene Bauformen — S46/BF8, S46/BF9 und S47/BF5, S47/BF8. Die App kennt
dafür `Loesung.keine()` und `Loesung.alle()`, und der Fehlerkatalog fängt den
häufigsten Irrtum ab: beides als «x = 0» zu lesen.
"""
from __future__ import annotations

from dataclasses import dataclass

from sympy import Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .anzeige import MINUS, zeige
from .qualitaet import fehler_eindeutig, kopfrechenbar
from .s45_gleichungen import (ANLEITUNG, F, TIPPS, VARS, X, Z, _sammeln,
                              kandidaten, loesen, reihe, siebe)
from .schablone import Bauform, Schablone


# ══════════════════════════════════════════════════════════════════════════
# Ein Baustein kommt dazu: die Klammer
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class KL:
    """Ein Faktor mal eine Klammer:  2(x + 3)  ·  −(3 + 4x)  ·  (x + 1)

    Der Anteil an x und die Konstante werden durchmultipliziert — damit
    bleibt die Gleichung linear und `loesen()` aus S45 funktioniert
    unverändert weiter.
    """
    faktor: int
    muster: str
    glieder: tuple

    @property
    def _innen(self):
        return _sammeln(self.muster, self.glieder)

    @property
    def anteil(self):
        return self.faktor * self._innen[0]

    @property
    def konstante(self):
        return self.faktor * self._innen[1]

    @property
    def text(self) -> str:
        innen = f"({reihe(self.muster, self.glieder)})"
        if self.faktor == 1:
            return innen
        if self.faktor == -1:
            return f"{MINUS}{innen}"
        return f"{zeige(Integer(self.faktor))}{innen}"


def bau(links, rechts, extra=(), art=None, loesung=None, tipps=None):
    """Wie `s45.bau`, aber mit den drei möglichen Antwortarten.

    `art` ist "keine" oder "alle", wenn die Gleichung keine oder unendlich
    viele Lösungen hat. Sonst wird gerechnet.
    """
    frage = f"{reihe(*links)} = {reihe(*rechts)}"
    al, kl = _sammeln(*links)
    ar, kr = _sammeln(*rechts)

    if art == "keine":
        l = Loesung.keine()
        text = "keine Lösung"
        katalog = [
            F("null_statt_keine", Integer(0),
              "Hier fallen alle x weg, und übrig bleibt eine falsche "
              "Aussage. Das stimmt für KEINE Zahl — auch nicht für null."),
            F("drei", Integer(3),
              "Was am Schluss übrig bleibt, ist kein Wert für x, sondern "
              "ein Widerspruch."),
            F("eins", Integer(1),
              "Es gibt keine Zahl, die diese Gleichung erfüllt."),
            F("eins_negativ", Integer(-1),
              "Auch −1 löst diese Gleichung nicht. Es gibt gar keine Lösung."),
            F("zwei", Integer(2),
              "Probier es aus: keine Zahl passt, weil die x wegfallen."),
        ]
    elif art == "alle":
        l = Loesung.alle()
        text = "jede Zahl"
        katalog = [
            F("null_statt_alle", Integer(0),
              "Beide Seiten sind gleich. Dann ist JEDE Zahl eine Lösung, "
              "nicht bloss die null."),
            F("keine_statt_alle", Integer(1),
              "Beide Seiten sind wirklich gleich — probier eine beliebige "
              "Zahl aus, sie passt."),
            F("zwei_a", Integer(2),
              "2 ist eine Lösung — aber nicht die einzige."),
            F("drei_a", Integer(3),
              "3 ist eine Lösung — aber nicht die einzige."),
            F("minus_eins", Integer(-1),
              "Auch −1 ist eine Lösung, genau wie jede andere Zahl."),
        ]
    else:
        wert = loesen(links, rechts) if loesung is None else sympify(loesung)
        if wert is None:
            return {"frage": frage, "loesung_text": "", "ungueltig": True,
                    "aufgabe": Aufgabe(loesung=Loesung.zahl(0),
                                       variablen=VARS,
                                       zielform=Zielform.BELIEBIG,
                                       fehlerkatalog=[]),
                    "schritte": [], "tipps": TIPPS}
        l = Loesung.zahl(wert)
        text = zeige(wert)
        katalog = siebe(list(extra) + kandidaten(links, rechts, wert), wert)

    if art in ("keine", "alle"):
        katalog = _sieben_zahlen(katalog)

    grund = tipps or TIPPS
    return {
        "frage": frage, "loesung_text": text, "ungueltig": False,
        "links": links, "rechts": rechts,
        "aufgabe": Aufgabe(loesung=l, variablen=VARS,
                           zielform=Zielform.BELIEBIG, fehlerkatalog=katalog),
        "schritte": [
            ("Alle Klammern ausmultiplizieren", frage),
            ("Jede Seite für sich zusammenfassen",
             f"{zeige(Integer(al))}x + {zeige(Integer(kl))} = "
             f"{zeige(Integer(ar))}x + {zeige(Integer(kr))}"),
            ("Alle x auf eine Seite, alle Zahlen auf die andere",
             f"{zeige(Integer(al - ar))}x = {zeige(Integer(kr - kl))}"),
            ("Durch den Koeffizienten teilen", f"x = {text}"),
        ],
        "tipps": [grund[0], grund[1], f"Am Schluss steht x = {text}."],
    }


def vz_glied(wert):
    """(Vorzeichen, Glied) — damit nie «− −4» dasteht."""
    return ("+", Z(wert)) if wert >= 0 else ("-", Z(-wert))


def _sieben_zahlen(katalog):
    """Doppelte Zahlen aus einem festen Katalog entfernen."""
    raus, gesehen = [], set()
    for f in katalog:
        s = str(f.ergebnis.expr)
        if s in gesehen:
            continue
        gesehen.add(s)
        raus.append(f)
    return raus


# ── Filter ────────────────────────────────────────────────────────────────

def loesbar(p, g) -> bool:
    return not g.get("ungueltig")


def stimmt(p, g) -> bool:
    """Setzt die Lösung ein und prüft, ob die Gleichung wirklich aufgeht.

    Wo eine Bauform ihre Lösung VORGIBT (Sonderfall «Lösung ist null»),
    kann sie an der Aufgabe vorbeirechnen. Beim Testlauf stand
    `3(2x − 5) = 15  →  x = 0` da, richtig waeren 5 gewesen. Die App haette
    eine richtige Antwort als falsch abgestempelt. Kostet nichts, weil nur
    Koeffizient und Konstante eingesetzt werden.
    """
    from korrektur.pruefung import Art
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR or "links" not in g:
        return True
    al, kl = _sammeln(*g["links"])
    ar, kr = _sammeln(*g["rechts"])
    return al * l.expr + kl == ar * l.expr + kr


def fuenf(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 5


def ganz(p, g) -> bool:
    from korrektur.pruefung import Art
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    return bool(getattr(l.expr, "is_Integer", False))


def echter_bruch(p, g) -> bool:
    """Bei S47 MUSS die Lösung ein Bruch sein — das ist die Bauform."""
    from korrektur.pruefung import Art
    l = g["aufgabe"].loesung
    if l.art is not Art.EXPR:
        return True
    return l.expr.is_Rational and l.expr.q != 1


def nicht_null(p, g) -> bool:
    from korrektur.pruefung import Art
    l = g["aufgabe"].loesung
    return l.art is not Art.EXPR or l.expr != 0


TIPPS46 = [
    "Zuerst alle Klammern auflösen. Ein Minus vor der Klammer dreht jedes "
    "Vorzeichen darin um.",
    "Fasse jede Seite für sich zusammen, bevor du etwas hin- und "
    "herschiebst.",
    "",
]

TIPPS47 = [
    "Rechne wie immer — und lass am Schluss den Bruch stehen, statt zu "
    "runden.",
    "Kürze den Bruch, so weit es geht.",
    "",
]

STANDARD = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
            ganz, nicht_null]
SONDER = [loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf]


# ══════════════════════════════════════════════════════════════════════════
# S46 · Klammern, Variablen auf beiden Seiten     (13.5 – 13.6)
# ══════════════════════════════════════════════════════════════════════════

#: `mus` ist das Vorzeichenmuster INNERHALB der Klammer und damit der
#: Regler, den Teil 2 nennt: A alles positiv, B ein Minus, C ein Minus und
#: ein Glied mehr. Ohne diesen Unterschied haetten A und B denselben Aufbau —
#: der Testlauf hat genau das beanstandet.
BEREICH46 = {
    "A": {"f": [2, 3], "k": [3, 4, 5], "z": [2, 3], "mus": ["++"],
          "lang": [False]},
    "B": {"f": [3, 4], "k": [4, 5, 6], "z": [2, 3], "mus": ["+-"],
          "lang": [False]},
    "C": {"f": [5, 6], "k": [3, 4, 7], "z": [2, 4], "mus": ["+-"],
          "lang": [True]},
}


def bau46(links, rechts, **kw):
    kw.setdefault("tipps", TIPPS46)
    return bau(links, rechts, **kw)


def bf46_1(p):
    """Eine Klammer, Zahl auf der anderen Seite:  2(x + 3) = 10"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        #: 5(2x − 3) = 25
        links = ("+", (KL(f, "+-", (X(z), Z(k))),))
        rechts = ("+", (Z(f * (z * 2 - k)),))
    else:
        links = ("+", (KL(f, mus, (X(1), Z(k))),))
        rechts = ("+", (Z(f * (z + k)),))
    return bau46(links, rechts)


BF46_1 = Bauform("BF1", "Eine Klammer, Zahl auf der anderen Seite",
    bereiche=BEREICH46, bauen=bf46_1, filter=STANDARD)


def bf46_2(p):
    """Variablen beidseitig, ohne Klammer:  3x + 2 = x + 10"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("++-", (X(f + 2), Z(k), Z(z)))
        rechts = ("++", (X(f), Z(k + 2 * (f + 2 - f))))
    else:
        vz = "-" if mus == "+-" else "+"
        links = ("+" + vz, (X(f + 1), Z(k)))
        kl = k if vz == "+" else -k
        rechts = ("++", (X(1), Z(kl + f * z)))
    return bau46(links, rechts)


BF46_2 = Bauform("BF2", "Variablen beidseitig, ohne Klammer",
    bereiche=BEREICH46, bauen=bf46_2, filter=STANDARD)


def bf46_3(p):
    """Klammer auf jeder Seite:  3(4x + 2) = 2(x + 8)"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("+", (KL(f, mus, (X(1), Z(k))),))
        rechts = ("++", (KL(z, "+-", (X(1), Z(k))), Z(f * k + z * k)))
    else:
        links = ("+", (KL(f, mus, (X(z), Z(1))),))
        rechts = ("+", (KL(z, mus, (X(1), Z(f))),))
    return bau46(links, rechts)


BF46_3 = Bauform("BF3", "Klammer auf jeder Seite",
    bereiche=BEREICH46, bauen=bf46_3, filter=STANDARD)


def bf46_4(p):
    """Zwei Klammern auf derselben Seite:
       2(3x + 1) + 3(2x + 4) = 62"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        links = ("++", (KL(f, mus, (X(1), Z(k))), KL(z, "+-", (X(2), Z(k)))))
    else:
        links = ("++", (KL(f, mus, (X(z), Z(1))), KL(z, "++", (X(f), Z(k)))))
    al, kl = _sammeln(*links)
    #: Die rechte Seite wird aus der gewuenschten Loesung gerechnet, sonst
    #: kommt bei zufaelligen Zahlen fast nie eine ganze Zahl heraus.
    ziel = 3 if not p["lang"] else 5
    rechts = ("+", (Z(al * ziel + kl),))
    return bau46(links, rechts)


BF46_4 = Bauform("BF4", "Zwei Klammern auf derselben Seite",
    bereiche=BEREICH46, bauen=bf46_4, filter=STANDARD)


def bf46_5(p):
    """Minus vor der Klammer ohne Faktor:  2x − (3 + 4x) = 9"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    links = ("+-", (X(z), KL(1, mus, (Z(k), X(f)))))
    al, kl = _sammeln(*links)
    ziel = -(k // 2 + 1)
    if p["lang"]:
        rechts = ("+-", (Z(al * ziel - kl + k), Z(k)))
    else:
        rechts = ("+", (Z(al * ziel - kl),))
    return bau46(links, rechts)


BF46_5 = Bauform("BF5", "Minus vor der Klammer ohne Faktor",
    bereiche=BEREICH46, bauen=bf46_5, filter=STANDARD)


def bf46_6(p):
    """Minus vor der Klammer auf der rechten Seite:
       7x − 15 = 15 − x   ·   7x − 15 = 15 − (x − 14)

    A hat rechts ein blosses Minus, B eine Klammer dahinter, C zwei
    Klammern auf der linken Seite. Die Gliederzahl waechst mit.
    """
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    ziel = 2
    if p["lang"]:
        #: (14 − x) − (5 − 2x) = 14
        links = ("+-", (KL(1, "+-", (Z(k * 3), X(1))),
                        KL(1, "+-", (Z(k), X(2)))))
        al, kl = _sammeln(*links)
        rechts = ("+", (Z(al * ziel + kl),))
    elif mus == "+-":
        #: 7x − 15 = 15 − (x − 14)
        rechts = ("+-", (Z(k * 3), KL(1, "+-", (X(1), Z(k * 2)))))
        ar, kr = _sammeln(*rechts)
        vz, gl = vz_glied(-((f + 1) * ziel - ar * ziel - kr))
        links = ("+" + vz, (X(f + 1), gl))
    else:
        #: 7x − 15 = 15 − x
        rechts = ("+-", (Z(k * 3), X(1)))
        ar, kr = _sammeln(*rechts)
        vz, gl = vz_glied(-((f + 1) * ziel - ar * ziel - kr))
        links = ("+" + vz, (X(f + 1), gl))
    return bau46(links, rechts)


BF46_6 = Bauform("BF6", "Minus vor der Klammer auf der rechten Seite",
    bereiche=BEREICH46, bauen=bf46_6, filter=STANDARD)


def bf46_7(p):
    """Negative Koeffizienten beidseitig:  −3x + 5 = −8x − 15

    Auf B kommt links ein Glied dazu, auf C auch rechts.
    """
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    ziel = -(z + 1)
    #: links −f·x + k (+ ein Glied auf B und C)
    if p["lang"]:
        links = ("-+-", (X(f), Z(k * 2), Z(k)))
    elif mus == "+-":
        links = ("-+-", (X(f), Z(k), Z(1)))
    else:
        links = ("-+", (X(f), Z(k)))
    al, kl = _sammeln(*links)
    ar = -(f + k)
    kr = al * ziel + kl - ar * ziel
    if p["lang"]:
        rechts = ("-++", (X(f + k), Z(kr + k), Z(-k))) if kr + k >= 0             else ("--+", (X(f + k), Z(-(kr + k)), Z(-k)))
        rechts = (rechts[0][:2] + ("+" if -k >= 0 else "-"),
                  (rechts[1][0], rechts[1][1], Z(abs(k))))
    else:
        rechts = ("-+", (X(f + k), Z(kr))) if kr >= 0             else ("--", (X(f + k), Z(-kr)))
    return bau46(links, rechts)


BF46_7 = Bauform("BF7", "Negative Koeffizienten beidseitig",
    bereiche=BEREICH46, bauen=bf46_7, filter=STANDARD)


def bf46_8(p):
    """Sonderfall: unlösbar oder allgemeingültig:
       2(x + 3) = 2x + 8   ·   3(x − 2) = 3x − 6

    Beide Antworten sind hier moeglich und beide sind KEINE Zahl. Der
    Fehlerkatalog faengt den haeufigsten Irrtum ab: sie als x = 0 zu lesen.
    """
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    if p["lang"]:
        #: 57 − 2(x + 21) = 23 − 2(x + 4)  —  jede Zahl, drei Glieder
        links = ("+-", (Z(k * 8), KL(f, "++", (X(1), Z(k * 3)))))
        al, kl = _sammeln(*links)
        vz, gl = vz_glied(kl - k * 4 + f * k)
        rechts = ("+-" + vz, (Z(k * 4), KL(f, "++", (X(1), Z(k))), gl))
        return bau46(links, rechts, art="alle")
    if mus == "+-":
        #: 3(x − 2) = 3x − 6  —  jede Zahl
        links = ("+", (KL(f, "+-", (X(1), Z(k))),))
        rechts = ("+-", (X(f), Z(f * k)))
        return bau46(links, rechts, art="alle")
    #: 2(x + 3) = 2x + 8  —  keine Loesung
    links = ("+", (KL(f, "++", (X(1), Z(k))),))
    rechts = ("++", (X(f), Z(f * k + 2)))
    return bau46(links, rechts, art="keine")


BF46_8 = Bauform("BF8", "Sonderfall: unlösbar oder allgemeingültig",
    bereiche=BEREICH46, bauen=bf46_8, filter=SONDER)


def bf46_9(p):
    """Sonderfall: die x fallen weg, ein Widerspruch bleibt:
       2(x + 4) = 2x"""
    f, k, mus = p["f"], p["k"], p["mus"]
    if p["lang"]:
        #: Level C: 5(x − 1) = 5x + 3   — vier Glieder, zwei Minus
        links = ("+", (KL(f, "+-", (X(1), Z(k))),))
        rechts = ("++", (X(f), Z(k)))
    elif mus == "+-":
        #: Level B: 2(x − 4) = 2x
        links = ("+", (KL(f, "+-", (X(1), Z(k))),))
        rechts = ("+", (X(f),))
    else:
        #: Level A: 3x = x + 2x + 5  — die x heben sich auf
        links = ("+", (X(f),))
        rechts = ("+++", (X(1), Z(k), X(f - 1)))
    return bau46(links, rechts, art="keine")


BF46_9 = Bauform("BF9", "Sonderfall: die x fallen weg, ein Widerspruch bleibt",
    bereiche=BEREICH46, bauen=bf46_9, filter=SONDER)


def bf46_10(p):
    """Sonderfall: die Lösung ist null:  4(x + 2) = 8"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    links = ("+", (KL(f, mus, (X(z), Z(k))),))
    _, kl = _sammeln(*links)
    #: Bei x = 0 bleibt links genau die Konstante stehen — die muss rechts
    #: auch stehen, sonst ist null gar nicht die Loesung.
    if p["lang"]:
        rechts = ("++-", (Z(kl), X(f), X(f)))
    else:
        rechts = ("+",) if False else ("+", (Z(kl),))
    return bau46(links, rechts, loesung=0, extra=[
        F("faktor_als_loesung", Integer(f),
          f"{zeige(Integer(f))} ist der Faktor vor der Klammer, nicht die "
          f"Lösung."),
        F("klammerzahl", Integer(k),
          f"{zeige(Integer(k))} steht in der Klammer, ist aber nicht x."),
        F("produkt", Integer(f * k),
          "Das ist die rechte Seite, nicht der Wert von x."),
        F("eins", Integer(1),
          "Setz null ein und rechne nach — es stimmt."),
        F("negativ", Integer(-k),
          "Beide Seiten sind schon gleich, wenn x null ist."),
    ])


BF46_10 = Bauform("BF10", "Sonderfall: die Lösung ist null",
    bereiche=BEREICH46, bauen=bf46_10,
    filter=[loesbar, stimmt, kopfrechenbar, fehler_eindeutig, fuenf,
            ganz])


def bf46_11(p):
    """Gleiche Struktur, andere Zahlen:  5x + 6 = 3x + 16"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    ziel = 5
    al, ar = f + 4, f
    kl = k
    kr = al * ziel + kl - ar * ziel
    if p["lang"]:
        #: Level C: drei Glieder links, zwei Minus
        links = ("+--", (X(al + 2), Z(k), Z(z)))
        kl = -k - z
        kr = (al + 2) * ziel + kl - ar * ziel
        rechts = ("++", (X(ar), Z(kr)))
    elif mus == "+-":
        #: Level B: ein Minus links
        links = ("+-", (X(al), Z(kl)))
        kr = al * ziel - kl - ar * ziel
        rechts = ("++", (X(ar), Z(kr)))
    else:
        links = ("++", (X(al), Z(kl)))
        rechts = ("++", (X(ar), Z(kr)))
    return bau46(links, rechts)


BF46_11 = Bauform("BF11", "Gleiche Struktur, andere Zahlen",
    bereiche=BEREICH46, bauen=bf46_11, filter=STANDARD)


def bf46_12(p):
    """Klammer gegen Klammer, beide zweigliedrig:
       3(x + 2) = 2(x + 5)"""
    f, k, z, mus = p["f"], p["k"], p["z"], p["mus"]
    links = ("+", (KL(f, mus, (X(1), Z(k))),))
    if p["lang"]:
        #: Level C: rechts kommt ein Glied dazu
        innen = KL(f - 1, mus, (X(1), Z(k + z)))
        rechts = ("++", (innen, Z(z)))
        links = ("++", (KL(f, mus, (X(1), Z(k))), Z(z)))
    else:
        rechts = ("+", (KL(f - 1, mus, (X(1), Z(k + z))),))
    return bau46(links, rechts)


BF46_12 = Bauform("BF12", "Klammer gegen Klammer, beide zweigliedrig",
    bereiche=BEREICH46, bauen=bf46_12, filter=STANDARD)


S46 = Schablone(
    nr="S46", titel="Klammern, Variablen auf beiden Seiten",
    lektionen="13.5 – 13.6", erhebung="1a",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF46_1, BF46_2, BF46_3, BF46_4, BF46_5, BF46_6,
               BF46_7, BF46_8, BF46_9, BF46_10, BF46_11, BF46_12],
    kernidee=("Erst alle Klammern auflösen, dann jede Seite zusammenfassen, "
              "dann die Variablen auf die eine und die Zahlen auf die andere "
              "Seite bringen."),
)
