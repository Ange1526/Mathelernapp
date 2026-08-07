# -*- coding: utf-8 -*-
"""
S24 · Potenzgesetze                          (Lektionen 7.5 – 7.8)
S25 · Potenz eines Produkts, mehrere Variablen  (Lektionen 7.9 – 7.10)

    «Rechne aus.»
    x² · x³      x⁵ : x²      (x²)³      x⁵ + x⁵      (5a)²      4a²b²

Zusammen mit S22 und S23 ersetzen sie `s7_potenzen.py`. S25 ist die Vorstufe
zu Erhebungsaufgabe 3e (√(25a²)): wer 25a² als (5a)² sieht, zieht die Wurzel
im Kopf.

LEVELACHSE (Teil 2 der Schablonen, wörtlich):

    S24   Anzahl Faktoren    zwei     →  zwei       →  drei
    S24   Vorzeichen         positiv  →  ein Minus  →  zwei Minus
    S25   Anzahl Variablen   eine     →  eine bis zwei  →  zwei bis drei
    S25   Vorzeichen         positiv  →  ein Minus  →  ein Minus mit
                                                        ungeradem Exponenten

Bei S24 haben A und B gleich viele Faktoren. Der Unterschied liegt anderswo,
und Teil 1 zeigt wo: auf A tragen beide Faktoren eine sichtbare Hochzahl
(x² · x³), auf B ist einer davon nackt (y⁴ · y) oder trägt ein Minus. Das ist
ein Unterschied im Aufbau, nicht in den Zahlen — genau das verlangt die
Regel. Auf C kommt der dritte Faktor dazu.

DIE RÜCKWÄRTSFORMEN. S25/BF2 und S25/BF11 verlangen die andere Richtung:
aus 25a² soll (5a)² werden. Als Aufgabe steht deshalb

    25a² = (?)²

da, und gefragt ist, was in der Klammer steht — hier 5a. Anders liesse sich
die Antwort nicht prüfen: 25a² und (5a)² sind derselbe Wert, jede Prüfung auf
Gleichheit würde die unveränderte Aufgabe als richtig durchgehen lassen.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sympy import Expr, Integer, Rational, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (exponent_hoechstens, fehler_eindeutig,
                        kopfrechenbar)
from .s22_s23_potenzen import hoch
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

#: Drei Plätze, damit (xyz)² möglich ist. Die Filter sorgen dafür, dass die
#: Plätze verschiedene Buchstaben bekommen.
SORTE1 = [x, a, u, m]
SORTE2 = [y, b, v, n]
SORTE3 = [z, c, w, d]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


# ══════════════════════════════════════════════════════════════════════════
# Bausteine
# ══════════════════════════════════════════════════════════════════════════
#
#   FP(2, ((x, 2),))                     ->  2x²
#   FP(1, ((x, 5),))                     ->  x⁵
#   FP(2, ((x, 1),), klammer=True, aussen=2)   ->  (2x)²
#   FP(1, ((a, 2), (b, 1)), klammer=True, aussen=2)  ->  (a²b)²
#   FP(-2, ((y, 1),))                    ->  −2y
#
# Der Wert ist immer (Koeffizient · Monom) hoch `aussen`.


@dataclass(frozen=True)
class FP:
    koeff: Expr = Integer(1)
    basen: tuple = ()          # ((Symbol, Exponent), ...)
    klammer: bool = False
    aussen: int = 1

    @property
    def monom(self) -> Expr:
        raus = Integer(1)
        for s, e in self.basen:
            raus *= s ** e
        return raus

    @property
    def wert(self) -> Expr:
        return (sympify(self.koeff) * self.monom) ** self.aussen

    @property
    def kern(self) -> str:
        k = sympify(self.koeff)
        if not self.basen:
            return zeige(k)
        vorne = "" if k == 1 else (MINUS if k == -1 else zeige(k))
        return vorne + "".join(zeige(s) + (hoch(e) if e > 1 else "")
                               for s, e in self.basen)

    @property
    def text(self) -> str:
        if self.klammer:
            return f"({self.kern}){hoch(self.aussen)}" if self.aussen > 1 \
                   else f"({self.kern})"
        return self.kern


@dataclass(frozen=True)
class Roh:
    """Ein Teil mit eigenem Text — für Verschachtelungen wie ((z²)²)²."""
    text: str
    wert: Expr


def teil_wert(t) -> Expr:
    return t.wert


def teil_text(t, erster: bool) -> str:
    """Ein negativer Faktor bekommt Klammern, wenn er nicht vorne steht:
    `5y⁴ · (−2y)` — so steht es auch in der Schablone."""
    txt = t.text
    if not erster and txt.startswith(MINUS):
        return f"({txt})"
    return txt


@dataclass(frozen=True)
class Kette:
    teile: tuple
    ops: tuple = ()

    @property
    def wert(self) -> Expr:
        gesamt = teil_wert(self.teile[0])
        for i, op in enumerate(self.ops):
            rechts = teil_wert(self.teile[i + 1])
            gesamt = gesamt / rechts if op == ":" else gesamt * rechts
        return gesamt

    @property
    def text(self) -> str:
        raus = teil_text(self.teile[0], True)
        for i, op in enumerate(self.ops):
            raus += f" {op} {teil_text(self.teile[i + 1], False)}"
        return raus


def K(*teile, ops=None) -> Kette:
    return Kette(tuple(teile), tuple(ops or ["·"] * (len(teile) - 1)))


def frage_text(muster, glieder) -> str:
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = g.text
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def reihenfolge(glieder) -> list:
    """Die Variablen in der Reihenfolge, in der sie in der Aufgabe stehen."""
    raus = []
    for g in glieder:
        for teil in g.teile:
            for s, _ in getattr(teil, "basen", ()):
                if s not in raus:
                    raus.append(s)
    return raus


def monom_text(wert, folge) -> str:
    """Ein Monom in der Reihenfolge der Aufgabe hinschreiben.

    SymPy sortiert Produkte alphabetisch um: aus (uv)² wird beim Ausgeben
    `n²u²`, obwohl in der Aufgabe u vor n steht. Wo die Reihenfolge
    zählt, wird sie darum hier selbst gesetzt (CLAUDE.md, «SymPy
    sortiert um»).
    """
    wert = sympify(wert)
    if wert.is_Add or wert == 0:
        return zeige(wert)
    k, rest = wert.as_coeff_Mul()
    potenzen = rest.as_powers_dict()
    if any(not s.is_Symbol for s in potenzen):
        return zeige(wert)
    txt = "" if k == 1 else (MINUS if k == -1 else zeige(k))
    for s in folge:
        e = potenzen.get(s)
        if e is None:
            continue
        e = int(e)
        txt += zeige(s) + (hoch(e) if e > 1 else "")
    return txt or zeige(wert)


def summe(muster, glieder) -> Expr:
    gesamt = Integer(0)
    for zeichen, g in zip(muster, glieder):
        gesamt += g.wert if zeichen == "+" else -g.wert
    return gesamt


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 5 von S24 und S25 nennt zusammen neun Fehler. Welche davon in einer
# Aufgabe überhaupt entstehen können, hängt vom Gesetz ab, das sie braucht —
# darum wird hier die Aufgabe abgefragt und nicht die Bauform.


def _fps(glieder):
    return [t for g in glieder for t in g.teile if isinstance(t, FP)]


def _exp_summe(fp: FP) -> int:
    return sum(e for _, e in fp.basen) * fp.aussen


def kandidaten(muster, glieder, loesung):
    raus = []
    fps = _fps(glieder)
    if not fps:
        return raus
    kette = glieder[0]
    teile = [t for t in kette.teile if isinstance(t, FP)]
    ops = kette.ops
    #: Alle Variablen der Aufgabe, in fester Reihenfolge
    variablen = []
    for t in fps:
        for s, _ in t.basen:
            if s not in variablen:
                variablen.append(s)

    # 1 · Beim Multiplizieren die Hochzahlen multipliziert:  x² · x³ -> x⁶
    if (len(muster) == 1 and len(teile) > 1 and all(o == "·" for o in ops)
            and len(variablen) == 1 and all(not t.klammer for t in teile)):
        v1 = variablen[0]
        produkt = 1
        koeff = Integer(1)
        for t in teile:
            produkt *= max(_exp_summe(t), 1)
            koeff *= sympify(t.koeff)
        if produkt <= 10:
            raus.append(F("hochzahlen_multipliziert", koeff * v1 ** produkt,
                f"Beim Multiplizieren werden die Hochzahlen ADDIERT: "
                f"{' + '.join(str(_exp_summe(t)) for t in teile)} = "
                f"{sum(_exp_summe(t) for t in teile)}."))

    # 2 · Beim Dividieren die Hochzahlen addiert:  x⁵ : x² -> x⁷
    if (len(muster) == 1 and ":" in ops and len(variablen) == 1
            and all(not t.klammer for t in teile)):
        v1 = variablen[0]
        if sum(_exp_summe(t) for t in teile) <= 10:
            raus.append(F("beim_teilen_addiert",
                v1 ** sum(_exp_summe(t) for t in teile),
            f"Beim Dividieren werden die Hochzahlen SUBTRAHIERT: "
                f"{_exp_summe(teile[0])} − "
                f"{' − '.join(str(_exp_summe(t)) for t in teile[1:])} = "
                f"{_exp_summe(teile[0]) - sum(_exp_summe(t) for t in teile[1:])}."))

    # 3 · Bei der Potenz einer Potenz addiert:  (x²)³ -> x⁵
    klammern = [t for t in teile if t.klammer and t.aussen > 1
                and any(e > 1 for _, e in t.basen)]
    if klammern and len(muster) == 1:
        t0 = klammern[0]
        ersatz = sympify(t0.koeff) ** t0.aussen
        for s, e in t0.basen:
            ersatz *= s ** (e + t0.aussen)
        rest = Integer(1)
        for t in teile:
            if t is not t0:
                rest *= t.wert
        raus.append(F("potenz_addiert", ersatz * rest,
            f"Bei einer Potenz einer Potenz werden die Hochzahlen "
            f"MULTIPLIZIERT: {t0.text} ist {zeige(t0.wert)}."))

    # 4 · Der Koeffizient wurde nicht mitpotenziert:  (2x)² -> 2x²
    koeffiziert = [t for t in teile if t.klammer and t.aussen > 1
                   and sympify(t.koeff) not in (1, -1)]
    if koeffiziert and len(muster) == 1:
        t0 = koeffiziert[0]
        ersatz = sympify(t0.koeff) * t0.monom ** t0.aussen
        rest = Integer(1)
        for t in teile:
            if t is not t0:
                rest *= t.wert
        raus.append(F("koeffizient_nicht_potenziert", ersatz * rest,
            f"Die Klammer gilt für alles darin — auch für die Zahl: "
            f"{t0.text} ist {zeige(t0.wert)}."))

    # 5 · Nur die erste Variable potenziert:  (a²b)² -> a⁴b
    mehrere = [t for t in teile if t.klammer and t.aussen > 1
               and len(t.basen) > 1]
    if mehrere and len(muster) == 1:
        t0 = mehrere[0]
        ersatz = sympify(t0.koeff) ** t0.aussen
        for i, (s, e) in enumerate(t0.basen):
            ersatz *= s ** (e * t0.aussen if i == 0 else e)
        rest = Integer(1)
        for t in teile:
            if t is not t0:
                rest *= t.wert
        raus.append(F("nur_erste_variable", ersatz * rest,
            f"Die Klammer gilt für JEDEN Faktor darin: {t0.text} ist "
            f"{zeige(t0.wert)}."))

    # 6 · Verschiedene Variablen zusammengezogen:  x³ · y² -> (xy)⁵
    if (len(muster) == 1 and len(teile) > 1 and all(o == "·" for o in ops)
            and len(variablen) > 1):
        gesamt = sum(_exp_summe(t) for t in teile)
        koeff = Integer(1)
        for t in teile:
            koeff *= sympify(t.koeff)
        produkt = Integer(1)
        for s in variablen:
            produkt *= s
        if gesamt <= 10:
            raus.append(F("variablen_zusammengezogen",
                koeff * produkt ** gesamt,
                f"{' und '.join(zeige(s) for s in variablen)} sind "
                f"verschiedene Variablen. Jede zählt für sich."))

    # 7 · Nur der erste Faktor gerechnet
    if len(muster) == 1 and len(teile) > 1:
        raus.append(F("nur_erster_faktor", teile[0].wert,
            f"Auch {teil_text(kette.teile[-1], False)} zählt mit."))

    # 8 · Beim Addieren die Hochzahlen verrechnet:  x⁵ + x⁵ -> x¹⁰
    if len(muster) > 1 and all(len(g.teile) == 1 for g in glieder) \
            and len(variablen) == 1:
        v1 = variablen[0]
        exp = sum(_exp_summe(g.teile[0]) for g in glieder)
        if exp <= 10:
            raus.append(F("beim_addieren_gerechnet", v1 ** exp,
                f"Beim Addieren wird gezählt, nicht gerechnet — die Hochzahl "
                f"bleibt stehen: {zeige(loesung)}."))

    # ── Allgemeine Kandidaten ────────────────────────────────────────────
    #
    # WARUM ES SIE BRAUCHT: Die Eintraege oben treffen jeweils EINEN
    # bestimmten Denkfehler und greifen darum nur bei der passenden
    # Aufgabenform. Gemessen hatten neun der zwoelf Bauformen dieser
    # Schablone am Ende genau EINEN Katalogeintrag — verlangt sind fuenf.
    # Ein Schueler bekam dort bei fast jedem Fehler nur «falsch» statt
    # einer Erklaerung, und das ausgerechnet in Kapitel 7, an dem
    # Erhebungsaufgabe 3c haengt.
    #
    # In der urspruenglichen Schablone fiel das nicht auf: ueber zwoelf
    # Bauformen gemittelt ergab sich 1,6 — knapp ueber der Schwelle. Erst
    # beim Aufteilen nach Lektionen wurde es sichtbar.
    #
    # Die folgenden Kandidaten sind bewusst grob. Sie sagen nicht, WELCHER
    # Denkfehler vorlag, sondern nur, in welche Richtung es danebenging.
    # Das ist weniger wert als ein gezielter Eintrag, aber deutlich mehr
    # als nichts — und `siebe` wirft sie weg, sobald ein gezielter Eintrag
    # denselben Wert hat.
    ziel = sympify(loesung)
    if not variablen:
        # Zahlenbasis — «2⁴ : 2²». Hier gibt es keine Variable, an der man
        # die Hochzahl verschieben koennte; die Kandidaten muessen darum
        # rein rechnerisch sein.
        for name, wert, text in [
            ("um_eins_zu_gross", ziel + 1, "Rechne nochmals nach."),
            ("um_eins_zu_klein", ziel - 1, "Rechne nochmals nach."),
            ("verdoppelt", ziel * 2, "Das Ergebnis ist doppelt so gross."),
            ("halbiert", ziel / 2, "Das Ergebnis ist halb so gross."),
            ("quadriert", ziel ** 2 if abs(ziel) < 100 else None,
             "Hier wird nicht nochmals potenziert."),
        ]:
            try:
                if wert is not None:
                    raus.append(F(name, wert, text))
            except Exception:                          # noqa: BLE001
                pass
        return raus

    if variablen:
        v = variablen[0]
        for name, wert, text in [
            ("hochzahl_eins_zu_viel", ziel * v,
             "Die Hochzahl ist um eins zu gross. Zähl nochmals nach."),
            ("hochzahl_eins_zu_wenig", ziel / v,
             "Die Hochzahl ist um eins zu klein. Zähl nochmals nach."),
            ("koeffizient_verdoppelt", ziel * 2,
             "Die Zahl vor der Variablen stimmt nicht."),
            ("vorzeichen_gedreht", -ziel,
             "Das Vorzeichen stimmt nicht."),
            ("koeffizient_um_eins", ziel + ziel / 2 if ziel != 0 else None,
             "Die Zahl vor der Variablen stimmt nicht."),
        ]:
            try:
                if wert is not None:
                    raus.append(F(name, wert, text))
            except Exception:                          # noqa: BLE001
                pass

    return raus


def siebe(fehler, loesung):
    raus, gesehen = [], set()
    for f in fehler:
        e = f.ergebnis.expr
        if e is None or e == sympify(loesung) or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Der gemeinsame Bauplan
# ══════════════════════════════════════════════════════════════════════════

TIPPS24 = [
    "Beim Multiplizieren werden die Hochzahlen addiert, beim Dividieren "
    "subtrahiert, bei einer Potenz einer Potenz multipliziert.",
    "Geh von links nach rechts vor und wende bei jedem Schritt das passende "
    "Gesetz an.",
    "",
]

TIPPS25 = [
    "Eine Potenz eines Produkts gilt für jeden Faktor darin: (ab)² = a²b².",
    "Schau Zahl und Variablen getrennt an.",
    "",
]


def bau(muster, glieder, extra=(), tipps=None, loesung=None,
        loesung_text=None, zielform=Zielform.BELIEBIG, schritte=None,
        frage=None):
    l = summe(muster, glieder) if loesung is None else sympify(loesung)
    fehler = siebe(list(extra) + kandidaten(muster, glieder, l), l)
    txt = frage or frage_text(muster, glieder)
    if loesung_text is None:
        loesung_text = monom_text(l, reihenfolge(glieder))
    return {"frage": txt,
            "loesung_text": loesung_text,
            "glieder": glieder,
            "muster": muster,
            "aufgabe": Aufgabe(loesung=Loesung.zahl(l), variablen=VARS,
                               zielform=zielform, fehlerkatalog=fehler),
            "schritte": schritte or [("Die Aufgabe hinschreiben", txt),
                                     ("Ergebnis", loesung_text)],
            "tipps": (tipps or TIPPS24)[:2] + [
                f"Aus {txt} wird {loesung_text}."]}


def hat_fehler(p, g) -> bool:
    return len(g["aufgabe"].fehlerkatalog) >= 1


def verschieden(*namen):
    def f(p, g):
        werte = [str(p[nn]) for nn in namen if nn in p]
        return len(set(werte)) == len(werte)
    return f


STANDARD = [kopfrechenbar, fehler_eindeutig, hat_fehler,
            exponent_hoechstens(10)]
ZWEI = STANDARD + [verschieden("var", "var2")]
DREI = STANDARD + [verschieden("var", "var2", "var3")]


# ══════════════════════════════════════════════════════════════════════════
# S24 · Potenzgesetze        (Lektionen 7.5 – 7.8)
# ══════════════════════════════════════════════════════════════════════════
#
# A: zwei Faktoren, beide mit sichtbarer Hochzahl, alles positiv
# B: zwei Faktoren, einer davon nackt oder mit Minus
# C: drei Faktoren, zwei Minus wo die Bauform Vorzeichen zulaesst

BEREICH24 = {
    "A": {"var": SORTE1, "var2": SORTE2, "e1": [2, 3], "e2": [2, 3],
          "e3": [2], "k1": [2], "k2": [3], "drei": [False], "nackt": [False],
          "minus": [0]},
    "B": {"var": SORTE1, "var2": SORTE2, "e1": [4, 5], "e2": [1],
          "e3": [2], "k1": [5], "k2": [2], "drei": [False], "nackt": [True],
          "minus": [1]},
    "C": {"var": SORTE1, "var2": SORTE2, "e1": [2, 3], "e2": [3, 4],
          "e3": [4, 2], "k1": [3], "k2": [4], "drei": [True],
          "nackt": [False], "minus": [2]},
}


def V(sym, e=1, k=1):
    return FP(Integer(k), ((sym, e),))


def bf24_1(p):
    """Potenzen multiplizieren — Hochzahlen addieren:  x² · x³"""
    v1, e1, e2 = p["var"], p["e1"], p["e2"]
    teile = [V(v1, e1), V(v1, e2)]
    if p["drei"]:
        teile.append(V(v1, p["e3"]))
    return bau("+", [K(*teile)])


BF24_1 = Bauform("BF1", "Potenzen multiplizieren — Hochzahlen addieren",
    bereiche=BEREICH24, bauen=bf24_1, filter=STANDARD)


def bf24_2(p):
    """Potenzen dividieren — Hochzahlen subtrahieren:  x⁵ : x²"""
    v1, e1, e2 = p["var"], p["e1"] + 3, p["e2"]
    teile, ops = [V(v1, e1), V(v1, e2)], [":"]
    if p["drei"]:
        teile.append(V(v1, 1))
        ops.append(":")
    rest = e1 - e2 - (1 if p["drei"] else 0)
    return bau("+", [Kette(tuple(teile), tuple(ops))],
               loesung=v1 ** rest)


BF24_2 = Bauform("BF2", "Potenzen dividieren — Hochzahlen subtrahieren",
    bereiche=BEREICH24, bauen=bf24_2, filter=STANDARD)


def bf24_3(p):
    """Potenz einer Potenz — Hochzahlen multiplizieren:  (x²)³"""
    v1, e1, e2 = p["var"], p["e1"], p["e2"]
    if p["drei"]:
        #: ((z²)²)² — die Verschachtelung braucht einen eigenen Text.
        innen = FP(Integer(1), ((v1, 2),), klammer=True, aussen=2)
        teil = Roh(f"({innen.text}){hoch(2)}", v1 ** 8)
        # Ein `Roh`-Teil traegt keine Bausteine, aus denen `kandidaten()`
        # weitere Fehler ableiten koennte — hier stand darum genau EIN
        # Eintrag im Katalog. Die uebrigen vier werden von Hand gesetzt.
        return bau("+", [K(teil)], extra=[
            F("alle_addiert", v1 ** 6,
              "Auch bei zwei Klammern werden die Hochzahlen multipliziert: "
              "2 · 2 · 2 = 8."),
            F("nur_innere_klammer", v1 ** 4,
              "Die äussere Klammer zählt auch: nach (a²)² = a⁴ kommt noch "
              "einmal hoch zwei."),
            F("hochzahl_eins_zu_viel", v1 ** 9,
              "2 · 2 · 2 ist 8, nicht 9."),
            F("hochzahl_eins_zu_wenig", v1 ** 7,
              "2 · 2 · 2 ist 8, nicht 7."),
            F("verdoppelt", 2 * v1 ** 8,
              "Vor der Variablen steht keine Zahl."),
            #: v1**16 faellt am Filter `exponent_hoechstens(10)` durch und
            #: verwarf die ganze Aufgabe. Ein Katalogeintrag darf die
            #: Ziehung nicht scheitern lassen — darum bleibt er weg.
        ], loesung=v1 ** 8)
    aussen = max(e2, 2)
    #: Auf B traegt das Vorzeichen die Stufe: (−u⁴)² ist u⁸, das Minus
    #: verschwindet bei gerader Hochzahl.
    koeff = Integer(-1) if p["minus"] == 1 else Integer(1)
    return bau("+", [K(FP(koeff, ((v1, e1),), klammer=True,
                          aussen=aussen))])


BF24_3 = Bauform("BF3", "Potenz einer Potenz — Hochzahlen multiplizieren",
    bereiche=BEREICH24, bauen=bf24_3, filter=STANDARD)


def bf24_4(p):
    """Potenzen addieren — die Hochzahl bleibt:  x⁵ + x⁵"""
    v1, e1 = p["var"], p["e1"]
    if p["drei"]:
        muster = "+--"
        glieder = [K(V(v1, e1, 5)), K(V(v1, e1, 2)), K(V(v1, e1))]
    elif p["nackt"]:
        muster = "+++"
        glieder = [K(V(v1, e1))] * 3
    else:
        muster = "++"
        glieder = [K(V(v1, e1)), K(V(v1, e1))]
    return bau(muster, glieder, zielform=Zielform.ZUSAMMENGEFASST)


BF24_4 = Bauform("BF4", "Potenzen addieren — die Hochzahl bleibt",
    bereiche={"A": dict(BEREICH24["A"], e1=[5, 4]),
              "B": dict(BEREICH24["B"], e1=[3], muster=["+++"]),
              "C": dict(BEREICH24["C"], e1=[4, 3])},
    bauen=bf24_4, filter=STANDARD)


def bf24_5(p):
    """Dieselben Gesetze mit Zahlenbasis:  2³ · 2²"""
    bs = Integer(p["basis"])
    e1, e2 = p["e1"], p["e2"]
    if p["art"] == "mal":
        return bau("+", [K(FP(bs), FP(bs))], loesung=bs ** (e1 + e2),
                   frage=f"{zeige(bs)}{hoch(e1)} · {zeige(bs)}{hoch(e2)}",
                   loesung_text=zeige(bs ** (e1 + e2)), extra=[
            F("hochzahlen_multipliziert", bs ** (e1 * e2),
              f"Beim Multiplizieren werden die Hochzahlen addiert: "
              f"{e1} + {e2} = {e1 + e2}."),
            F("basen_multipliziert", (bs * bs) ** (e1 + e2),
              f"Die Basis bleibt {zeige(bs)} — nur die Hochzahlen werden "
              f"verrechnet."),
        ])
    if p["art"] == "geteilt":
        return bau("+", [K(FP(bs))], loesung=bs ** (e1 - e2),
                   frage=f"{zeige(bs)}{hoch(e1)} : {zeige(bs)}{hoch(e2)}",
                   loesung_text=zeige(bs ** (e1 - e2)), extra=[
            F("hochzahlen_addiert", bs ** (e1 + e2),
              f"Beim Dividieren werden die Hochzahlen subtrahiert: "
              f"{e1} − {e2} = {e1 - e2}."),
            F("basis_auch_geteilt", Integer(1),
              f"Nur die Hochzahlen werden verrechnet, die Basis bleibt "
              f"{zeige(bs)}."),
        ])
    return bau("+", [K(FP(bs))], loesung=bs ** (e1 * e2),
               frage=f"({zeige(bs)}{hoch(e1)}){hoch(e2)}",
               loesung_text=zeige(bs ** (e1 * e2)), extra=[
        F("hochzahlen_addiert", bs ** (e1 + e2),
          f"Bei einer Potenz einer Potenz werden die Hochzahlen "
          f"multipliziert: {e1} · {e2} = {e1 * e2}."),
    ])


BF24_5 = Bauform("BF5", "Dieselben Gesetze mit Zahlenbasis",
    bereiche={"A": {"basis": [2, 3], "e1": [3], "e2": [2], "art": ["mal"]},
              "B": {"basis": [3, 2], "e1": [4], "e2": [2], "art": ["geteilt"]},
              "C": {"basis": [2], "e1": [2], "e2": [3], "art": ["potenz"]}},
    bauen=bf24_5,
    filter=[kopfrechenbar, fehler_eindeutig, hat_fehler])


def bf24_6(p):
    """Sonderfall: das Ergebnis ist eins:  x³ : x³"""
    v1, e1 = p["var"], p["e1"]
    if p["drei"]:
        teile = (V(v1, e1), V(v1, p["e2"]), V(v1, e1 + p["e2"]))
        kette = Kette(teile, ("·", ":"))
    elif p["minus"] == 1:
        #: Minus durch Minus — auch das ergibt eins.
        kette = Kette((V(v1, e1, -1), V(v1, e1, -1)), (":",))
    else:
        kette = Kette((V(v1, e1), V(v1, e1)), (":",))
    return bau("+", [kette], loesung=1, extra=[
        F("hochzahl_null", Integer(0),
          f"{zeige(v1)}{hoch(e1)} : {zeige(v1)}{hoch(e1)} ist eins — jede "
          f"Zahl geteilt durch sich selbst ergibt eins, nicht null."),
        F("variable_geblieben", v1,
          "Die Hochzahlen heben sich ganz auf. Übrig bleibt die blosse 1."),
    ])


BF24_6 = Bauform("BF6", "Sonderfall: das Ergebnis ist eins",
    bereiche=BEREICH24, bauen=bf24_6, filter=[fehler_eindeutig, hat_fehler])


def bf24_7(p):
    """Zwei verschiedene Variablen:  x³ · y²"""
    v1, v2, e1, e2 = p["var"], p["var2"], p["e1"], p["e2"]
    if p["drei"]:
        teile = [FP(Integer(1), ((v1, e1), (v2, e2))),
                 FP(Integer(1), ((v1, p["e3"]), (v2, 1)))]
    elif p["nackt"]:
        teile = [V(v1, e1), V(v1, 1), V(v2, 3)]
    else:
        teile = [V(v1, e1), V(v2, e2)]
    return bau("+", [K(*teile)])


BF24_7 = Bauform("BF7", "Zwei verschiedene Variablen",
    bereiche=BEREICH24, bauen=bf24_7, filter=ZWEI)


def bf24_8(p):
    """Potenzen mit Koeffizienten:  2x² · 3x³  ·  5y⁴ · (−2y)"""
    v1, e1, e2 = p["var"], p["e1"], p["e2"]
    k1, k2 = Integer(p["k1"]), Integer(p["k2"])
    if p["minus"] == 1:
        k2 = -k2
    elif p["minus"] == 2:
        k1, k2 = -k1, -k2
    return bau("+", [K(V(v1, e1, k1), V(v1, e2, k2))])


BF24_8 = Bauform("BF8", "Potenzen mit Koeffizienten",
    bereiche={"A": dict(BEREICH24["A"], k1=[2], k2=[3]),
              "B": dict(BEREICH24["B"], k1=[5], k2=[2], e1=[4], e2=[1]),
              "C": dict(BEREICH24["C"], k1=[3], k2=[4], e1=[2], e2=[3])},
    bauen=bf24_8, filter=STANDARD)


def bf24_9(p):
    """Sonderfall: Hochzahl eins bleibt übrig:  x⁴ : x"""
    v1, e1 = p["var"], p["e1"] + 2
    if p["drei"]:
        #: Drei Faktoren — das ist der Regler von Level C.
        kette = Kette((V(v1, e1 + 1), V(v1, e1 - 1), V(v1, 1)), (":", ":"))
    elif p["nackt"]:
        #: Der Divisor ist nackt: x² : x
        kette = Kette((V(v1, 2), V(v1, 1)), (":",))
    else:
        kette = Kette((V(v1, e1), V(v1, e1 - 1)), (":",))
    return bau("+", [kette], loesung=v1, extra=[
        F("hochzahl_geschrieben", v1 ** 2,
          "Die Hochzahlen ergeben zusammen 1 — und die 1 wird nicht "
          "hingeschrieben."),
        F("eins_statt_variable", Integer(1),
          f"Es bleibt eine Hochzahl 1 übrig, also {zeige(v1)} — nicht 1."),
    ])


BF24_9 = Bauform("BF9", "Sonderfall: Hochzahl eins bleibt übrig",
    bereiche=BEREICH24, bauen=bf24_9, filter=[fehler_eindeutig, hat_fehler])


def bf24_10(p):
    """Sonderfall: nichts lässt sich zusammenfassen:  x² + x³"""
    v1, e1, e2 = p["var"], p["e1"], p["e2"] + 1
    if p["drei"]:
        muster = "++-"
        glieder = [K(V(v1, e2)), K(V(v1, e1)), K(V(v1, e2))]
        text = zeige(v1 ** e1)
        return bau(muster, glieder, zielform=Zielform.ZUSAMMENGEFASST,
                   loesung_text=text)
    muster = "+-" if p["minus"] else "++"
    glieder = [K(V(v1, e2)), K(V(v1, e1))]
    l = summe(muster, glieder)
    return bau(muster, glieder, zielform=Zielform.ZUSAMMENGEFASST,
               loesung_text=zeige_summe(v1 ** e2,
                                        v1 ** e1 if muster[1] == "+"
                                        else -v1 ** e1))


BF24_10 = Bauform("BF10", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche={"A": dict(BEREICH24["A"], e1=[3], e2=[1]),
              "B": dict(BEREICH24["B"], e1=[2], e2=[3]),
              "C": dict(BEREICH24["C"], e1=[2], e2=[2])},
    bauen=bf24_10, filter=[fehler_eindeutig, hat_fehler,
                           exponent_hoechstens(10)])


def bf24_11(p):
    """Klammer mit Koeffizient wird potenziert:  (2x)²"""
    v1, k1 = p["var"], Integer(p["k1"])
    innen_exp = 2 if p["drei"] else 1
    aussen = max(p["e2"], 2)
    #: Auf B ist der Koeffizient negativ — das ist der Vorzeichenregler.
    if p["minus"] == 1:
        k1 = -k1
    return bau("+", [K(FP(k1, ((v1, innen_exp),), klammer=True,
                          aussen=aussen))])


BF24_11 = Bauform("BF11", "Klammer mit Koeffizient wird potenziert",
    bereiche={"A": dict(BEREICH24["A"], k1=[2], e2=[2]),
              "B": dict(BEREICH24["B"], k1=[3], e2=[3]),
              "C": dict(BEREICH24["C"], k1=[2], e2=[3])},
    bauen=bf24_11, filter=STANDARD)


def bf24_12(p):
    """Mehrere Gesetze in einer Aufgabe:  x² · x³ : x⁴"""
    v1, e1, e2 = p["var"], p["e1"], p["e2"]
    if p["drei"]:
        teile = (FP(Integer(1), ((v1, 2),), klammer=True, aussen=3),
                 V(v1, 4))
        kette = Kette(teile, (":",))
        return bau("+", [kette], loesung=v1 ** 2)
    if p["nackt"]:
        teile = (V(v1, 5), V(v1, 1), V(v1, 3))
        return bau("+", [Kette(teile, ("·", ":"))], loesung=v1 ** 3)
    teile = (V(v1, e1), V(v1, e2), V(v1, e1 + e2 - 1))
    return bau("+", [Kette(teile, ("·", ":"))], loesung=v1)


BF24_12 = Bauform("BF12", "Mehrere Gesetze in einer Aufgabe",
    bereiche=BEREICH24, bauen=bf24_12, filter=STANDARD)


S24 = Schablone(
    nr="S24", titel="Potenzgesetze",
    lektionen="7.5 – 7.8", erhebung="Vorstufe zu 3e",
    anleitung=ANLEITUNG,
    levelachse="Anzahl Faktoren und Vorzeichen",
    bauformen=[BF24_1, BF24_2, BF24_3, BF24_4, BF24_5, BF24_6,
               BF24_7, BF24_8, BF24_9, BF24_10, BF24_11, BF24_12],
    kernidee=("Beim Multiplizieren werden die Hochzahlen addiert, beim "
              "Dividieren subtrahiert, bei einer Potenz einer Potenz "
              "multipliziert — und beim Addieren bleibt die Hochzahl "
              "unverändert."),
)


# ══════════════════════════════════════════════════════════════════════════
# S25 · Potenz eines Produkts, mehrere Variablen   (Lektionen 7.9 – 7.10)
# ══════════════════════════════════════════════════════════════════════════
#
# A: eine Variable, alles positiv
# B: eine bis zwei Variablen, ein Minus
# C: zwei bis drei Variablen, ein Minus mit ungeradem Exponenten

BEREICH25 = {
    "A": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3, "zahl": [5, 3, 4],
          "exp": [2], "anzahl": [1], "minus": [False]},
    "B": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3, "zahl": [3, 2],
          "exp": [3], "anzahl": [2], "minus": [True]},
    "C": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3, "zahl": [2, 3],
          "exp": [3, 5], "anzahl": [3], "minus": [True]},
}


def bau25(muster, glieder, extra=(), **kw):
    kw.setdefault("tipps", TIPPS25)
    return bau(muster, glieder, extra=extra, **kw)


def bf25_1(p):
    """Produkt aus Zahl und Variable potenzieren:  (5a)²"""
    v1, k, e = p["var"], Integer(p["zahl"]), p["exp"]
    return bau25("+", [K(FP(k, ((v1, 1),), klammer=True, aussen=e))])


BF25_1 = Bauform("BF1", "Produkt aus Zahl und Variable potenzieren",
    bereiche={"A": dict(BEREICH25["A"], exp=[2]),
              "B": dict(BEREICH25["B"], exp=[3], minus=[False]),
              "C": dict(BEREICH25["C"], exp=[4, 5], zahl=[2])},
    bauen=bf25_1, filter=STANDARD)


def bf25_2(p):
    """Rückwärts: als Potenz eines Produkts schreiben.

        25a² = (?)²        gefragt ist der Inhalt der Klammer: 5a
    """
    v1, k, e = p["var"], Integer(p["zahl"]), p["exp"]
    gegeben = (k * v1) ** e
    frage = f"{zeige(gegeben)} = (?){hoch(e)}"
    return bau25("+", [K(FP(k, ((v1, 1),)))], loesung=k * v1,
                 frage=frage, loesung_text=zeige(k * v1), extra=[
        F("zahl_nicht_radiziert", gegeben,
          f"({zeige(gegeben)}){hoch(e)} wäre viel mehr. Gesucht ist die Zahl, "
          f"die {e}-mal mit sich selbst multipliziert {zeige(k ** e)} ergibt: "
          f"{zeige(k)}."),
        F("nur_zahl", k,
          f"Auch die Variable gehört in die Klammer: {zeige(k * v1)}."),
    ], schritte=[("Zahl und Variable getrennt anschauen",
                  f"{zeige(k ** e)} und {zeige(v1 ** e)}"),
                 (f"Welche Zahl ergibt {e}-mal sich selbst {zeige(k ** e)}?",
                  zeige(k)),
                 ("Bei der Variablen die Hochzahl teilen",
                  f"{zeige(v1 ** e)} wird {zeige(v1)}"),
                 ("Zusammensetzen", f"({zeige(k * v1)}){hoch(e)}")])


BF25_2 = Bauform("BF2", "Rückwärts: als Potenz eines Produkts schreiben",
    bereiche={"A": dict(BEREICH25["A"], zahl=[5, 4, 3], exp=[2]),
              "B": dict(BEREICH25["B"], zahl=[2, 3], exp=[3]),
              "C": dict(BEREICH25["C"], zahl=[3, 2], exp=[4])},
    bauen=bf25_2, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler,
                          exponent_hoechstens(10)])


def bf25_3(p):
    """Produkt zweier Variablen:  (ab)²  ·  (xyz)²"""
    v1, v2, v3, e = p["var"], p["var2"], p["var3"], p["exp"]
    basen = [(v1, 1), (v2, 1)] if p["anzahl"] < 3 else \
            [(v1, 1), (v2, 1), (v3, 1)]
    return bau25("+", [K(FP(Integer(1), tuple(basen), klammer=True,
                            aussen=e))])


BF25_3 = Bauform("BF3", "Produkt zweier Variablen",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], exp=[2]),
              "B": dict(BEREICH25["B"], anzahl=[2], exp=[3]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[2])},
    bauen=bf25_3, filter=DREI)


def bf25_4(p):
    """Zahl und zwei Variablen:  (2ab)²

    A und B haben beide zwei Variablen — den Unterschied trägt der Exponent,
    auf C kommt die dritte Variable dazu.
    """
    v1, v2, k, e = p["var"], p["var2"], Integer(p["zahl"]), p["exp"]
    basen = ((v1, 1), (v2, 1))
    if p["anzahl"] == 3:
        basen = ((v1, 1), (v2, 1), (p["var3"], 1))
    return bau25("+", [K(FP(k, basen, klammer=True, aussen=e))])


BF25_4 = Bauform("BF4", "Zahl und zwei Variablen",
    bereiche={"A": dict(BEREICH25["A"], zahl=[2], exp=[2], anzahl=[2]),
              "B": dict(BEREICH25["B"], zahl=[3], exp=[3], anzahl=[2]),
              "C": dict(BEREICH25["C"], zahl=[2], exp=[3], anzahl=[3])},
    bauen=bf25_4, filter=DREI)


def bf25_5(p):
    """In der Klammer steht schon eine Potenz:  (a²b)²"""
    v1, v2, e = p["var"], p["var2"], p["exp"]
    basen = ((v1, 2), (v2, 1)) if p["anzahl"] < 3 else ((v1, 2), (v2, 3))
    return bau25("+", [K(FP(Integer(1), basen, klammer=True, aussen=e))])


BF25_5 = Bauform("BF5", "In der Klammer steht schon eine Potenz",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], exp=[2]),
              "B": dict(BEREICH25["B"], anzahl=[2], exp=[3]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[2])},
    bauen=bf25_5, filter=ZWEI)


def bf25_6(p):
    """Produkt mit gemischten Hochzahlen zusammenfassen:  a²b · ab²"""
    v1, v2 = p["var"], p["var2"]
    #: Auf B steht vorne eine hoehere Hochzahl — u³v · uv², so wie in Teil 1.
    erste = 3 if p["hoch"] else 2
    teile = [FP(Integer(1), ((v1, erste), (v2, 1))),
             FP(Integer(1), ((v1, 1), (v2, 2)))]
    if p["anzahl"] == 3:
        teile.append(FP(Integer(1), ((v1, 1),)))
    kette = K(*teile)
    e1 = sum(e for t in teile for s, e in t.basen if s == v1)
    e2 = sum(e for t in teile for s, e in t.basen if s == v2)
    return bau25("+", [kette], extra=[
        F("hochzahlen_multipliziert", v1 ** 2 * v2 ** 2,
          f"Die Hochzahlen werden addiert, nicht multipliziert: "
          f"{zeige(v1)} kommt {e1}-mal vor, {zeige(v2)} {e2}-mal."),
        F("nur_erste_variable", v1 ** e1,
          f"Auch {zeige(v2)} zählt mit: {zeige(v2)}{hoch(e2)}."),
    ])


BF25_6 = Bauform("BF6", "Produkt mit gemischten Hochzahlen zusammenfassen",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], hoch=[False]),
              "B": dict(BEREICH25["B"], anzahl=[2], hoch=[True]),
              "C": dict(BEREICH25["C"], anzahl=[3], hoch=[False])},
    bauen=bf25_6, filter=ZWEI)


def bf25_7(p):
    """Negative Basis im Produkt:  (−2a)²  ·  (−2b)³"""
    v1, v2, k, e = p["var"], p["var2"], Integer(p["zahl"]), p["exp"]
    basen = ((v1, 1),) if p["anzahl"] < 3 else ((v1, 1), (v2, 1))
    return bau25("+", [K(FP(-k, basen, klammer=True, aussen=e))], extra=[
        F("vorzeichen_ignoriert", abs((k * (basen[0][0])) ** e *
                                      (basen[1][0] ** e if len(basen) > 1
                                       else 1)),
          f"{e} ist {'ungerade' if e % 2 else 'gerade'} — "
          f"{'das Minus bleibt' if e % 2 else 'das Ergebnis wird positiv'}."),
    ])


BF25_7 = Bauform("BF7", "Negative Basis im Produkt",
    bereiche={"A": dict(BEREICH25["A"], zahl=[2], exp=[2], anzahl=[1]),
              "B": dict(BEREICH25["B"], zahl=[2], exp=[3], anzahl=[1]),
              "C": dict(BEREICH25["C"], zahl=[3, 2], exp=[3], anzahl=[3])},
    bauen=bf25_7, filter=ZWEI)


def bf25_8(p):
    """Potenz eines Produkts geteilt:  (ab)² : (ab)"""
    v1, v2, e = p["var"], p["var2"], p["exp"]
    basen = ((v1, 1), (v2, 1)) if p["anzahl"] < 3 else ((v1, 2), (v2, 1))
    oben = FP(Integer(1), basen, klammer=True, aussen=e)
    unten = FP(Integer(1), basen, klammer=True, aussen=e - 1)
    return bau25("+", [Kette((oben, unten), (":",))],
                 loesung=oben.wert / unten.wert)


BF25_8 = Bauform("BF8", "Potenz eines Produkts geteilt",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], exp=[2]),
              "B": dict(BEREICH25["B"], anzahl=[3], exp=[2]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[3])},
    bauen=bf25_8, filter=ZWEI)


def bf25_9(p):
    """Sonderfall: Hochzahl oder Faktor eins:  (ab)¹  ·  (2uv)¹ · 3"""
    v1, v2, k = p["var"], p["var2"], Integer(p["zahl"])
    if p["anzahl"] == 1:
        teil = FP(Integer(1), ((v1, 1),), klammer=True, aussen=p["exp"])
        return bau25("+", [K(FP(Integer(1)), teil)],
                     frage=f"(1 · {zeige(v1)}){hoch(p['exp'])}",
                     loesung=v1 ** p["exp"], extra=[
            F("eins_dazu", 1 + v1 ** p["exp"],
              "Der Faktor 1 ändert nichts — er wird nicht dazugezählt."),
        ])
    if p["anzahl"] == 2:
        teil = FP(Integer(1), ((v1, 1), (v2, 1)), klammer=True, aussen=1)
        return bau25("+", [K(teil)],
                     frage=f"({zeige(v1 * v2)}){hoch(1)}",
                     loesung=v1 * v2, extra=[
            F("exponent_eins", Integer(1),
              f"Die Hochzahl 1 heisst: alles kommt einmal vor. "
              f"({zeige(v1 * v2)})¹ ist {zeige(v1 * v2)}."),
        ])
    teil = FP(k, ((v1, 1), (v2, 1)), klammer=True, aussen=1)
    return bau25("+", [K(teil, FP(Integer(3)))],
                 frage=f"({teil.kern}){hoch(1)} · 3",
                 loesung=3 * k * v1 * v2, extra=[
        F("exponent_eins", Integer(3),
          f"Die Hochzahl 1 ändert nichts: ({teil.kern})¹ ist {teil.kern}."),
    ])


BF25_9 = Bauform("BF9", "Sonderfall: Hochzahl oder Faktor eins",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[1], exp=[3]),
              "B": dict(BEREICH25["B"], anzahl=[2], exp=[1]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[1], zahl=[2, 3])},
    bauen=bf25_9, filter=ZWEI)


def bf25_10(p):
    """Potenz eines Produkts mal ein Einzelfaktor:  (ab)² · a"""
    v1, v2, e = p["var"], p["var2"], p["exp"]
    klammer = FP(Integer(1), ((v1, 1), (v2, 1)), klammer=True, aussen=e)
    zweiter = klammer if p["anzahl"] == 3 else FP(Integer(1), ((v2, 1),))
    return bau25("+", [K(klammer, zweiter)])


BF25_10 = Bauform("BF10", "Potenz eines Produkts mal ein Einzelfaktor",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], exp=[2]),
              "B": dict(BEREICH25["B"], anzahl=[2], exp=[3]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[2])},
    bauen=bf25_10, filter=ZWEI)


def bf25_11(p):
    """Rückwärts mit zwei Variablen:  4a²b² = (?)²"""
    v1, v2, k = p["var"], p["var2"], Integer(p["zahl"])
    innen = k * v1 ** p["e1"] * v2
    if p.get("drei"):
        #: Level C: drei Variablen — 36x⁴y²z² = (6x²yz)²
        innen = k * v1 ** p["e1"] * v2 * p["var3"]
    gegeben = innen ** 2
    return bau25("+", [K(FP(k, ((v1, 1), (v2, 1))))], loesung=innen,
                 frage=f"{zeige(gegeben)} = (?){hoch(2)}",
                 loesung_text=zeige(innen), extra=[
        F("zahl_nicht_radiziert", k * innen,
          f"Auch die Zahl wird radiziert: {zeige(k ** 2)} ist "
          f"{zeige(k)}², also steht {zeige(k)} in der Klammer."),
        F("hochzahl_nicht_halbiert", innen * v1 ** p["e1"] * v2,
          "Bei jeder Variablen wird die Hochzahl halbiert."),
    ], schritte=[("Zahl und Variablen getrennt anschauen", zeige(gegeben)),
                 ("Die Wurzel der Zahl suchen",
                  f"{zeige(k ** 2)} = {zeige(k)}²"),
                 ("Bei jeder Variablen die Hochzahl halbieren",
                  zeige(v1 ** p["e1"] * v2)),
                 ("Zusammensetzen", f"({zeige(innen)})²")])


BF25_11 = Bauform("BF11", "Rückwärts mit zwei Variablen",
    bereiche={"A": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "zahl": [2, 3], "e1": [1], "drei": [False]},
              "B": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "zahl": [4, 3], "e1": [2], "drei": [False]},
              "C": {"var": SORTE1, "var2": SORTE2, "var3": SORTE3,
                    "zahl": [5, 6], "e1": [2], "drei": [True]}},
    bauen=bf25_11, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler,
                           exponent_hoechstens(10),
                           verschieden("var", "var2", "var3")])


def bf25_12(p):
    """Zwei Gesetze kombiniert:  (a²)² · b"""
    v1, v2, e = p["var"], p["var2"], p["exp"]
    klammer = FP(Integer(1), ((v1, p["innen"]),), klammer=True, aussen=e)
    if p["anzahl"] == 3:
        teile = [FP(Integer(1), ((v1, 2), (v2, 1)), klammer=True, aussen=3),
                 FP(Integer(1), ((v1, 1),))]
    else:
        #: innen und aussen dürfen nicht beide 2 sein — 2 + 2 ist
        #: dasselbe wie 2 · 2, und dann fällt der Fehler
        #: «addiert statt multipliziert» mit der Lösung zusammen.
        teile = [klammer, FP(Integer(1), ((v2, p["zweiter"]),))]
    return bau25("+", [K(*teile)])


BF25_12 = Bauform("BF12", "Zwei Gesetze kombiniert",
    bereiche={"A": dict(BEREICH25["A"], anzahl=[2], exp=[2], innen=[3],
                        zweiter=[1]),
              "B": dict(BEREICH25["B"], anzahl=[2], exp=[2], innen=[3],
                        zweiter=[2]),
              "C": dict(BEREICH25["C"], anzahl=[3], exp=[3], innen=[2],
                        zweiter=[1])},
    bauen=bf25_12, filter=ZWEI)


S25 = Schablone(
    nr="S25", titel="Potenz eines Produkts, mehrere Variablen",
    lektionen="7.9 – 7.10", erhebung="3e",
    anleitung=ANLEITUNG,
    levelachse="Anzahl Variablen und Vorzeichen",
    bauformen=[BF25_1, BF25_2, BF25_3, BF25_4, BF25_5, BF25_6,
               BF25_7, BF25_8, BF25_9, BF25_10, BF25_11, BF25_12],
    kernidee=("Eine Potenz eines Produkts gilt für jeden Faktor darin: "
              "(2ab)² ist 4a²b². Rückwärts heisst das: bei der Zahl die "
              "Wurzel ziehen, bei jeder Variablen die Hochzahl halbieren."),
)
