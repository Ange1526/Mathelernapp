# -*- coding: utf-8 -*-
"""
S20 · Punkt vor Strich mit Variablen        (Lektionen 6.1 – 6.4)
S21 · Ausrechnen und danach zusammenfassen  (Lektionen 6.5 – 6.7)

    «Rechne aus.»
    3x + 2 · 4x        5b − 5b · 2c        5b − 5b · 2c + 3bc

Zusammen ersetzen die beiden `s2_grundoperationen.py` für Kapitel 6. S2 hatte
auf allen drei Level denselben Aufbau und nur andere Zahlen — genau der
Konstruktionsfehler, den die Schülerin beim Üben gemerkt hat. S2 bleibt
vorerst für die Lektionen 9.4 bis 9.6 (Division) im Einsatz, bis S30 und S31
gebaut sind.

Erhebungsaufgabe 2a ist `5b − 5b · 2c + 3bc` — das ist S21/BF7 auf Level A.
S20/BF3 ist dieselbe Form ohne das dritte Glied.

LEVELACHSE (Teil 2 der Schablonen, wörtlich):

    S20   Anzahl Glieder   zwei          →  zwei bis drei  →  drei bis vier
    S21   Anzahl Glieder   drei          →  drei           →  vier bis fünf
    beide Vorzeichen       alles positiv →  ein Minus      →  mehrere Minus

Gesperrt bleiben: wo das Produkt steht (das trennt BF1, BF6 und BF7), die
Anzahl Variablensorten (das trennt BF1 von BF2) und was nach dem Ausrechnen
passiert (das trennt die Bauformen von S21). Klammern gibt es nicht — das ist
10.6 und liegt nicht in der Kette von 6.1 bis 6.7.

Die Zahlen kommen auf ALLEN drei Stufen aus demselben Vorrat. Sie sind
ausdrücklich nicht die Levelachse.

ZWEI STELLEN, AN DENEN TEIL 2 UND DIE BEISPIELE IN TEIL 1 SICH WIDERSPRECHEN
— massgebend ist Teil 2:

  * Wo ein Vorzeichen die Bauform AUSMACHT (S20/BF3 «Produkt wird abgezogen»,
    S21/BF7, S21/BF11 «Minuszeichen am Anfang»), gehört das Minus zur Bauform
    und nicht zum Level. Diese Bauformen bekommen ein eigenes Muster, damit
    sich A und B trotzdem im Aufbau unterscheiden.
  * S21/BF6 zeigt in Teil 1 auf B und C ein `x²` in der AUFGABE. Teil 2 sagt
    dazu: «Potenzen als Aufgabe — nur als Ergebnis, sonst wäre es 7.2 und
    damit zu früh.» Die Potenz entsteht hier also nur durchs Multiplizieren.
"""
from __future__ import annotations

from sympy import Integer, expand, sympify

from korrektur import Aufgabe, Fehler, Loesung, Zielform, symbole
from .anzeige import MINUS, zeige, zeige_summe
from .qualitaet import (fehler_eindeutig, kopfrechenbar, loesung_nicht_null,
                        symbole_verschieden)
from .schablone import Bauform, Schablone

a, b, c, d, m, n, u, v, w, x, y, z = symbole("a b c d m n u v w x y z")
VARS = {"a", "b", "c", "d", "m", "n", "u", "v", "w", "x", "y", "z"}
ANLEITUNG = "Rechne aus."

SORTE1 = [a, x, u, m, b]
SORTE2 = [b, y, v, n, c]

#: Derselbe Vorrat auf A, B und C. Die Zahlengrösse ist NICHT die Levelachse.
ZAHLEN = [2, 3, 4, 5, 6]
DREH = [0, 1, 2, 3, 4]


def F(s, e, t):
    return Fehler(s, Loesung.zahl(e), t)


def koeffizienten(p, anzahl):
    """Zahlen aus dem Vorrat, mit Schrittweite 7 durchlaufen.

    Die Schrittweite muss zur Vorratsgrösse teilerfremd sein, sonst
    wiederholen sich die Zahlen (CLAUDE.md, «Zahlen ziehen»). Der Vorrat hat
    fünf Einträge, 7 ist dazu teilerfremd.
    """
    vorrat = p["zahlen"]
    return [vorrat[(i * 7 + p["dreh"]) % len(vorrat)] for i in range(anzahl)]


# ══════════════════════════════════════════════════════════════════════════
# Glieder
# ══════════════════════════════════════════════════════════════════════════
#
# Ein Glied ist entweder ein einzelner Term oder ein Produkt:
#
#     T(3, x)          ->  3x            Wert 3x
#     P(2, 4 * x)      ->  2 · 4x        Wert 8x
#     P(5*b, 2*c)      ->  5b · 2c       Wert 10bc
#
# Das Vorzeichen steht NICHT im Glied, sondern im Muster. So bleibt die
# Levelachse (Anzahl Glieder, Anzahl Minus) an einer einzigen Stelle.


def T(k, basis=1):
    return ("term", sympify(k) * sympify(basis))


def P(*faktoren):
    return ("prod", [sympify(f) for f in faktoren])


def wert_glied(g):
    art, inhalt = g
    if art != "prod":
        return inhalt
    p = Integer(1)
    for f in inhalt:
        p *= f
    return p


def zeige_glied(g) -> str:
    art, inhalt = g
    if art != "prod":
        return zeige(inhalt)
    return " · ".join(zeige(f) for f in inhalt)


def frage_text(muster, glieder) -> str:
    teile = []
    for i, (zeichen, g) in enumerate(zip(muster, glieder)):
        t = zeige_glied(g)
        if i == 0:
            teile.append(t if zeichen == "+" else f"{MINUS}{t}")
        else:
            teile.append(f"{'+' if zeichen == '+' else MINUS} {t}")
    return " ".join(teile)


def sammeln(muster, glieder):
    """Was am Schluss dasteht: [(Koeffizient, Basis)] in der Reihenfolge,
    in der die Sorten in der Aufgabe zum ersten Mal auftauchen.

    Selber sortieren statt SymPy sortieren lassen: SymPy ordnet Summen
    alphabetisch um, und dann steht in der Musterlösung `−10bc + 5b`, wo
    `5b − 10bc` stehen müsste.
    """
    reihenfolge, summe = [], {}
    for zeichen, g in zip(muster, glieder):
        roh = wert_glied(g) * (1 if zeichen == "+" else -1)
        k, basis = sympify(roh).as_coeff_Mul()
        if k == 0:
            continue
        if basis not in summe:
            reihenfolge.append(basis)
            summe[basis] = Integer(0)
        summe[basis] += k
    return [(summe[bs], bs) for bs in reihenfolge if summe[bs] != 0]


def teile_text(teile) -> str:
    if not teile:
        return "0"
    return zeige_summe(*[k * bs for k, bs in teile])


# ══════════════════════════════════════════════════════════════════════════
# Fehlerkatalog — aus der Aufgabe gerechnet, nicht je Bauform hingeschrieben
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 5 von S20 und S21 nennt zusammen sechs Fehler. Sie stehen hier EINMAL
# und gelten für jede Bauform, in der sie überhaupt auftreten können.


def _links_nach_rechts(muster, glieder):
    """Der Term stur von links nach rechts, ohne Punkt vor Strich.

        3x + 2 · 4x   ->   (3x + 2) · 4x   =   12x² + 8x

    Steht das Produkt vorne, kommt dasselbe heraus wie richtig gerechnet —
    dann fällt der Eintrag beim Sieben von selbst weg.
    """
    acc = None
    for i, (zeichen, (art, inhalt)) in enumerate(zip(muster, glieder)):
        faktoren = list(inhalt) if art == "prod" else [inhalt]
        if i == 0:
            acc = faktoren[0] if zeichen == "+" else -faktoren[0]
        elif zeichen == "+":
            acc = acc + faktoren[0]
        else:
            acc = acc - faktoren[0]
        for f in faktoren[1:]:
            acc = acc * f
    return expand(acc)


def _zahlen_addiert(g):
    """Beim Produkt die Zahlen addiert statt multipliziert:  2a · 3b -> 5ab"""
    art, inhalt = g
    if art != "prod":
        return wert_glied(g)
    zahlen, monome = Integer(0), Integer(1)
    for f in inhalt:
        k, mo = sympify(f).as_coeff_Mul()
        zahlen += k
        monome *= mo
    return zahlen * monome


def _ohne_potenz(g):
    """Variable beim Multiplizieren vergessen:  2x · 3y · x -> 6xy"""
    art, inhalt = g
    if art != "prod":
        return wert_glied(g)
    zahl, monome = Integer(1), Integer(1)
    for f in inhalt:
        k, mo = sympify(f).as_coeff_Mul()
        zahl *= k
        monome *= mo
    flach = Integer(1)
    for s in sorted(monome.free_symbols, key=str):
        flach *= s
    return zahl * flach


def _hat_potenz(glieder) -> bool:
    for g in glieder:
        if g[0] == "prod" and _ohne_potenz(g) != wert_glied(g):
            return True
    return False


def _summe(muster, glieder, ersatz=None):
    """Die ganze Summe, wobei `ersatz(g)` den Wert eines Glieds liefert."""
    gesamt = Integer(0)
    for zeichen, g in zip(muster, glieder):
        w = ersatz(g) if ersatz else wert_glied(g)
        gesamt += w if zeichen == "+" else -w
    return expand(gesamt)


def kandidaten(muster, glieder, loesung, teile):
    """Teil 5 von S20 und S21, aus der Aufgabe gerechnet.

    Jeder Eintrag steht nur da, wo er überhaupt entstehen kann: «Minus vor
    dem Produkt verloren» braucht ein abgezogenes Produkt, «Variable
    vergessen» eine Variable, die zweimal im Produkt vorkommt.
    """
    raus = []
    produkte = [g for g in glieder if g[0] == "prod"]

    # 1 · Von links nach rechts gerechnet
    if produkte:
        erstes = zeige_glied(produkte[0])
        raus.append(F("links_nach_rechts", _links_nach_rechts(muster, glieder),
            f"Punkt vor Strich: zuerst {erstes} ausrechnen, erst danach plus "
            f"und minus."))

    # 2 · Nach dem Ausrechnen weiter zusammengefasst, obwohl die Glieder
    #     nicht gleichartig sind
    if len(teile) > 1:
        reichste = max(teile, key=lambda t: len(t[1].free_symbols))[1]
        namen = " und ".join(zeige(k * bs) for k, bs in teile)
        raus.append(F("alles_zusammengefasst",
            sum(k for k, _ in teile) * reichste,
            f"{namen} sind nicht gleichartig — sie haben nicht dieselben "
            f"Variablen. Der Term bleibt so stehen."))

    # 3 · Beim Produkt die Zahlen addiert
    if produkte:
        p0 = produkte[0]
        raus.append(F("zahlen_addiert", _summe(muster, glieder, _zahlen_addiert),
            f"Bei einem Produkt werden die Zahlen multipliziert: "
            f"{zeige_glied(p0)} ergibt {zeige(wert_glied(p0))}."))

    # 4 · Variable beim Multiplizieren vergessen
    if _hat_potenz(glieder):
        p0 = next(g for g in produkte if _ohne_potenz(g) != wert_glied(g))
        raus.append(F("variable_vergessen", _summe(muster, glieder, _ohne_potenz),
            f"In {zeige_glied(p0)} kommt eine Variable zweimal vor — daraus "
            f"wird eine Hochzahl: {zeige(wert_glied(p0))}."))

    # 5 · Das Minus vor dem Produkt verloren
    minus_produkt = [i for i, (zn, g) in enumerate(zip(muster, glieder))
                     if zn == "-" and g[0] == "prod"]
    if minus_produkt:
        i = minus_produkt[0]
        gedreht = list(muster)
        gedreht[i] = "+"
        raus.append(F("produkt_vorzeichen", _summe("".join(gedreht), glieder),
            f"Das Minus gehört zum ganzen Produkt {zeige_glied(glieder[i])}, "
            f"nicht nur zum ersten Faktor."))

    # 6 · Beim Zusammenfassen die Variablen mitmultipliziert. Nur dort, wo
    #     am Schluss eine einzige Sorte steht — sonst greift Eintrag 2.
    if len(teile) == 1 and teile[0][1] != 1:
        k0, bs = teile[0]
        raus.append(F("basis_multipliziert", k0 * bs ** 2,
            f"{zeige(bs)} bleibt {zeige(bs)} — beim Zusammenfassen werden "
            f"nur die Zahlen davor verrechnet."))

    # 7 · Eine Sorte hebt sich auf, wird aber trotzdem hingeschrieben
    vorhanden = {str(bs) for _, bs in teile}
    for zeichen, g in zip(muster, glieder):
        k, basis = sympify(wert_glied(g)).as_coeff_Mul()
        if k == 0 or str(basis) in vorhanden:
            continue
        k = k if zeichen == "+" else -k
        raus.append(F("sorte_geblieben", loesung + k * basis,
            f"Die {zeige(basis)}-Glieder heben sich auf — sie ergeben "
            f"zusammen null und fallen ganz weg."))
        break

    return raus


def siebe(fehler, loesung):
    """Doppelte und die Lösung selbst aus dem Katalog entfernen.

    Ohne das wird eine richtige Antwort als Fehler gemeldet, oder zwei
    Einträge ergeben dieselbe Zahl und die Diagnose ist nicht mehr eindeutig.
    """
    raus, gesehen = [], set()
    ziel = expand(loesung)
    for f in fehler:
        e = f.ergebnis.expr
        if e is None:
            continue
        e = expand(e)
        if e == ziel or str(e) in gesehen:
            continue
        gesehen.add(str(e))
        raus.append(f)
    return raus


# ══════════════════════════════════════════════════════════════════════════
# Lösungsweg und Tipps  (Teil 3 und Teil 4)
# ══════════════════════════════════════════════════════════════════════════

TIPPS20 = [
    "Punkt vor Strich gilt auch mit Variablen: erst multiplizieren, dann "
    "addieren oder subtrahieren.",
    "Rechne zuerst nur das Produkt aus und schreib den Term neu hin.",
    "",   # Stufe 3 wird je Aufgabe berechnet
]

TIPPS21 = [
    "Erst alle Produkte ausrechnen, dann prüfen, welche Glieder gleichartig "
    "sind.",
    "Schreib den Term nach dem Ausrechnen neu hin und sortiere dann nach "
    "Sorten.",
    "",
]


def _ausgerechnet(muster, glieder) -> str:
    """Der Term, nachdem alle Produkte ausgerechnet sind."""
    return frage_text(muster, [("term", wert_glied(g)) for g in glieder])


def tipps_fuer(muster, glieder, teile, basis_tipps):
    produkte = [g for g in glieder if g[0] == "prod"]
    neu = _ausgerechnet(muster, glieder)
    if produkte:
        p0 = produkte[0]
        konkret = (f"{zeige_glied(p0)} ergibt {zeige(wert_glied(p0))}. "
                   f"Damit steht da {neu}.")
    else:
        konkret = f"Sortiere nach Sorten: {neu}"
    return [basis_tipps[0], basis_tipps[1], konkret]


def schritte_fuer(muster, glieder, teile, zusammenfassen: bool):
    """Teil 3 der Schablone, aus der Aufgabe erzeugt."""
    produkte = [g for g in glieder if g[0] == "prod"]
    schritte = [("Term durchgehen und die Produkte markieren",
                 frage_text(muster, glieder))]
    if produkte:
        p0 = produkte[0]
        schritte.append(("Jedes Produkt für sich ausrechnen",
                         f"{zeige_glied(p0)} = {zeige(wert_glied(p0))}"))
    schritte.append(("Term neu hinschreiben, mit dem ausgerechneten Produkt",
                     _ausgerechnet(muster, glieder)))
    if zusammenfassen:
        schritte.append(("Sorten bestimmen und innerhalb jeder Sorte "
                         "zusammenfassen", teile_text(teile)))
        schritte.append(("Gegenprobe: lässt sich noch etwas zusammenfassen?",
                         "nein — ungleichartige Glieder bleiben nebeneinander"))
    else:
        schritte.append(("Prüfen: sind die verbliebenen Glieder gleichartig?",
                         "nur gleiche Variablen gehören zusammen"))
        schritte.append(("Ergebnis", teile_text(teile)))
    return schritte


# ══════════════════════════════════════════════════════════════════════════
# Der gemeinsame Bauplan
# ══════════════════════════════════════════════════════════════════════════

def bau(muster, glieder, extra=(), sorten=None, tipps=TIPPS20,
        zusammenfassen=False):
    teile = sammeln(muster, glieder)
    loesung = sum((k * bs for k, bs in teile), Integer(0))
    fehler = siebe(list(extra) + kandidaten(muster, glieder, loesung, teile),
                   loesung)
    return {"frage": frage_text(muster, glieder),
            "loesung_text": teile_text(teile),
            "teile": teile,
            "glieder": glieder,
            "muster": muster,
            "sorten": sorten or [],
            "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                               zielform=Zielform.ZUSAMMENGEFASST,
                               fehlerkatalog=fehler),
            "schritte": schritte_fuer(muster, glieder, teile, zusammenfassen),
            "tipps": tipps_fuer(muster, glieder, teile, tipps)}


# ── Filter ────────────────────────────────────────────────────────────────

def sorten_bleiben(p, g) -> bool:
    """Keine Sorte darf sich zufällig ganz aufheben.

    `4x − 3x · 2y + x` soll zweigliedrig bleiben. Wenn die x sich zufällig
    aufheben, ist das ein anderer Aufgabentyp — der hat seine eigene Bauform
    (S21/BF10). Sonst sieht die Schülerin eine Aufgabe, deren Ergebnis nichts
    mit dem Aufbau zu tun hat.
    """
    erwartet = g.get("sorten") or []
    if not erwartet:
        return True
    vorhanden = {str(bs) for _, bs in g["teile"]}
    return all(str(bs) in vorhanden for bs in erwartet)


def hat_fehler(p, g) -> bool:
    """Keine Aufgabe ohne Eintrag im Fehlerkatalog."""
    return len(g["aufgabe"].fehlerkatalog) >= 1


def glieder_positiv(p, g) -> bool:
    """Jedes Glied wird positiv hingeschrieben, das Vorzeichen steht im Muster.

    Sonst entsteht `2a · 4v + 6a + −8av`: zwei Zeichen nebeneinander. Bei den
    Sonderfall-Bauformen, wo sich ein Glied aus den anderen ergibt, kann das
    passieren — dann wird die Aufgabe verworfen und neu gezogen.
    """
    for gl in g.get("glieder", []):
        k, _ = sympify(wert_glied(gl)).as_coeff_Mul()
        if k < 0:
            return False
    return True


STANDARD = [kopfrechenbar, fehler_eindeutig, hat_fehler, sorten_bleiben,
            glieder_positiv]

#: Für Bauformen mit zwei Variablenplätzen. Ohne diesen Filter erwischen
#: beide Plätze irgendwann dieselbe Variable, und aus `5b · 2c` wird `5b · 2b`
#: — eine ganz andere Aufgabe als gemeint.
ZWEI = STANDARD + [symbole_verschieden("var", "var2")]


# ══════════════════════════════════════════════════════════════════════════
# S20 · Punkt vor Strich mit Variablen        (Lektionen 6.1 – 6.4)
# ══════════════════════════════════════════════════════════════════════════
#
# Ein Zeichen je Glied. A hat zwei Glieder und kein Minus, B zwei bis drei
# Glieder und ein Minus, C drei bis vier Glieder und mehrere Minus.

MUSTER20 = {
    "A": ["++"],
    "B": ["+-", "+-+", "++-"],
    "C": ["+--", "+-+-", "+--+", "+---"],
}

#: Für Bauformen, deren zweites Glied ein Pflicht-Minus trägt (BF3: «das
#: Produkt wird abgezogen»). Ohne eigenes Muster sähen A und B gleich aus:
#: beide zwei Glieder mit einem Minus. Hier trägt A zwei Glieder, B drei,
#: C drei bis vier mit einem zweiten Minus.
MUSTER20_M = {
    "A": ["+-"],
    "B": ["+-+", "+-+"],
    "C": ["+--", "+-+-", "+--+"],
}

BEREICH20 = {lv: {"muster": MUSTER20[lv], "var": SORTE1, "var2": SORTE2,
                  "zahlen": [ZAHLEN], "dreh": DREH} for lv in ("A", "B", "C")}
BEREICH20_M = {lv: {"muster": MUSTER20_M[lv], "var": SORTE1, "var2": SORTE2,
                    "zahlen": [ZAHLEN], "dreh": DREH}
               for lv in ("A", "B", "C")}


def bf20_1(p):
    """Eine Variable, Produkt hinten:  3x + 2 · 4x"""
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [T(k[0], v1), P(k[1], k[2] * v1)]
    glieder += [T(k[i + 2], v1) for i in range(1, len(muster) - 1)]
    return bau(muster, glieder)


BF20_1 = Bauform("BF1", "Eine Variable, Produkt hinten",
    bereiche=BEREICH20, bauen=bf20_1, filter=STANDARD + [loesung_nicht_null])


def bf20_2(p):
    """Zwei Variablen, Produkt und gleichartiger Term:  5b · 2c + 3bc"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2)]
    glieder += [T(k[i + 1], v1 * v2) for i in range(1, len(muster))]
    return bau(muster, glieder)


BF20_2 = Bauform("BF2", "Zwei Variablen, Produkt und gleichartiger Term",
    bereiche=BEREICH20, bauen=bf20_2, filter=ZWEI + [loesung_nicht_null])


def bf20_3(p):
    """Produkt wird abgezogen — das Ergebnis bleibt zweigliedrig:
       5b − 5b · 2c.  Das ist die Form der Erhebungsaufgabe 2a ohne das
       dritte Glied."""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [T(k[0], v1), P(k[1] * v1, k[2] * v2)]
    glieder += [T(k[i + 2], v1) for i in range(1, len(muster) - 1)]
    return bau(muster, glieder, sorten=[v1, v1 * v2])


BF20_3 = Bauform("BF3", "Produkt wird abgezogen, Ergebnis bleibt zweigliedrig",
    bereiche=BEREICH20_M, bauen=bf20_3, filter=ZWEI)


def bf20_4(p):
    """Nur Punktoperationen, mehrere Faktoren:  2x · 3y · x

    Hier gibt es kein Plus und kein Minus zwischen Gliedern — die Levelachse
    ist deshalb die Anzahl FAKTOREN und das Vorzeichen vor dem Term.
    """
    v1, v2 = p["var"], p["var2"]
    k = koeffizienten(p, 4)
    if p["anzahl"] == 3:
        faktoren = [k[0] * v1, k[1] * v2, v1 if p["blank"] else k[2] * v1]
    else:
        faktoren = [k[0] * v1, k[1] * v2, k[2] * v1,
                    v2 if p["blank"] else k[3] * v2]
    muster = "-" if p["minus"] else "+"
    return bau(muster, [P(*faktoren)])


BF20_4 = Bauform("BF4", "Nur Punktoperationen, mehrere Faktoren",
    bereiche={"A": {"anzahl": [3], "blank": [True], "minus": [False],
                    "var": SORTE1, "var2": SORTE2, "zahlen": [ZAHLEN],
                    "dreh": DREH},
              "B": {"anzahl": [3], "blank": [False], "minus": [True],
                    "var": SORTE1, "var2": SORTE2, "zahlen": [ZAHLEN],
                    "dreh": DREH},
              "C": {"anzahl": [4], "blank": [True, False], "minus": [True],
                    "var": SORTE1, "var2": SORTE2, "zahlen": [ZAHLEN],
                    "dreh": DREH}},
    bauen=bf20_4, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler,
                          glieder_positiv,
                          symbole_verschieden("var", "var2")])


def bf20_5(p):
    """Beide Glieder sind schon Produkte derselben Sorte:  −10bc + 3bc

    Ab drei Gliedern steht vorne ein echtes Produkt:  2x · 3y − 8xy + xy.
    """
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    if len(muster) >= 3:
        glieder = [P(k[0] * v1, k[1] * v2)]
        glieder += [T(k[i + 1], v1 * v2) for i in range(1, len(muster))]
    else:
        glieder = [T(k[0] * k[1], v1 * v2)]
        glieder += [T(k[i + 1], v1 * v2) for i in range(1, len(muster))]
    return bau(muster, glieder)


BF20_5 = Bauform("BF5", "Beide Glieder sind schon Produkte derselben Sorte",
    bereiche=BEREICH20, bauen=bf20_5, filter=ZWEI + [loesung_nicht_null])


def bf20_6(p):
    """Produkt aus Variable und Zahl:  2a + 3a · 4"""
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [T(k[0], v1), P(k[1] * v1, k[2])]
    glieder += [T(k[i + 2], v1) for i in range(1, len(muster) - 1)]
    return bau(muster, glieder)


BF20_6 = Bauform("BF6", "Produkt aus Variable und Zahl",
    bereiche=BEREICH20, bauen=bf20_6, filter=STANDARD + [loesung_nicht_null])


def bf20_7(p):
    """Produkt vorne, Zahl hinten:  3x · 2 + 4"""
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1])]
    glieder += [T(k[i + 1]) for i in range(1, len(muster))]
    return bau(muster, glieder, sorten=[v1, Integer(1)])


BF20_7 = Bauform("BF7", "Produkt vorne, Zahl hinten",
    bereiche=BEREICH20, bauen=bf20_7, filter=STANDARD)


def bf20_8(p):
    """Produkt zweier Variablen, Zahl hinten:  2a · 3b + 4"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2)]
    glieder += [T(k[i + 1]) for i in range(1, len(muster))]
    return bau(muster, glieder, sorten=[v1 * v2, Integer(1)])


BF20_8 = Bauform("BF8", "Produkt zweier Variablen, Zahl hinten",
    bereiche=BEREICH20, bauen=bf20_8, filter=ZWEI)


def bf20_9(p):
    """Sonderfall: das Ergebnis ist null.

    Die Gliederzahl trägt das Level: zwei, drei, vier.
    """
    v1, v2, anzahl = p["var"], p["var2"], p["anzahl"]
    k = koeffizienten(p, 3)
    if anzahl == 2:
        muster = "+-"
        glieder = [T(k[0] * k[1], v1), P(k[0], k[1] * v1)]
    elif anzahl == 3:
        muster = "++-"
        glieder = [P(k[0] * v1, k[1]), T(k[2], v1),
                   T(k[0] * k[1] + k[2], v1)]
    else:
        muster = "+-+-"
        glieder = [T(k[0], v1 * v2), T(k[0], v1 * v2),
                   P(k[1] * v1, k[2] * v2), T(k[1] * k[2], v1 * v2)]
    return bau(muster, glieder, extra=[
        F("nicht_null", sum(abs(wert_glied(g)) for g in glieder),
          "Die Vorzeichen zählen mit — hier heben sich alle Glieder auf."),
    ])


BF20_9 = Bauform("BF9", "Sonderfall: das Ergebnis ist null",
    bereiche={"A": {"anzahl": [2], "var": SORTE1, "var2": SORTE2,
                    "zahlen": [ZAHLEN], "dreh": DREH},
              "B": {"anzahl": [3], "var": SORTE1, "var2": SORTE2,
                    "zahlen": [ZAHLEN], "dreh": DREH},
              "C": {"anzahl": [4], "var": SORTE1, "var2": SORTE2,
                    "zahlen": [ZAHLEN], "dreh": DREH}},
    bauen=bf20_9, filter=[kopfrechenbar, fehler_eindeutig, hat_fehler,
                          glieder_positiv,
                          symbole_verschieden("var", "var2")])


def bf20_10(p):
    """Sonderfall: ein Faktor ist null:  0 · 3x + 5x"""
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    erstes = P(0, k[0] * v1) if p["wo"] == "vorne" else P(k[0] * v1, 0)
    glieder = [erstes]
    glieder += [T(k[i + 1], v1) for i in range(1, len(muster))]
    return bau(muster, glieder, extra=[
        F("null_frisst_alles", Integer(0),
          "Nur das Produkt wird null, nicht der ganze Term — die übrigen "
          "Glieder bleiben stehen."),
    ])


BF20_10 = Bauform("BF10", "Sonderfall: ein Faktor ist null",
    bereiche={lv: {"muster": MUSTER20[lv], "wo": ["vorne", "hinten"],
                   "var": SORTE1, "zahlen": [ZAHLEN], "dreh": DREH}
              for lv in ("A", "B", "C")},
    bauen=bf20_10, filter=STANDARD + [loesung_nicht_null])


def bf20_11(p):
    """Zwei Sorten, nur eine wird ausgerechnet:  2 · 3a + b"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0], k[1] * v1), T(k[2], v2)]
    glieder += [T(k[i + 2], v1 if i % 2 else v2)
                for i in range(1, len(muster) - 1)]
    return bau(muster, glieder, sorten=[v1, v2])


BF20_11 = Bauform("BF11", "Zwei Sorten, nur eine wird ausgerechnet",
    bereiche=BEREICH20, bauen=bf20_11, filter=ZWEI)


S20 = Schablone(
    nr="S20", titel="Punkt vor Strich mit Variablen",
    lektionen="6.1 – 6.4", erhebung="2a",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF20_1, BF20_2, BF20_3, BF20_4, BF20_5, BF20_6,
               BF20_7, BF20_8, BF20_9, BF20_10, BF20_11],
    kernidee=("Punkt vor Strich gilt auch mit Variablen. Erst nach dem "
              "Ausrechnen der Produkte wird geprüft, ob die Glieder "
              "gleichartig sind — oft sind sie es nicht."),
)


# ══════════════════════════════════════════════════════════════════════════
# S21 · Ausrechnen und danach zusammenfassen  (Lektionen 6.5 – 6.7)
# ══════════════════════════════════════════════════════════════════════════
#
# Teil 2: drei → drei → vier bis fünf Glieder, kein Minus → ein Minus →
# mehrere Minus. A und B haben gleich viele Glieder; der Unterschied liegt
# im Vorzeichen. So steht es in der Schablone.

MUSTER21 = {
    "A": ["+++"],
    "B": ["+-+", "++-"],
    "C": ["+-+-", "+--+", "+-++-", "+--++"],
}

#: Pflicht-Minus am zweiten Glied (BF7: «Produkt wird abgezogen»).
MUSTER21_M = {
    "A": ["+-+"],
    "B": ["+--"],
    "C": ["+-+-", "+--+", "+-+-+"],
}

#: Pflicht-Minus am LETZTEN Glied. Zwei Sonderfaelle brauchen es: bei BF8
#: soll am Schluss null stehen, bei BF10 faellt die Produktsorte weg — beides
#: geht nur, wenn zuletzt etwas abgezogen wird. Das Minus gehoert also zur
#: Bauform. Die Levelachse traegt hier die Gliederzahl und das ZWEITE Minus.
MUSTER21_N = {
    "A": ["++-"],
    "B": ["+--"],
    "C": ["+-+-", "+--+-"],
}

#: Pflicht-Minus am ersten Glied (BF11: «Minuszeichen am Anfang»).
MUSTER21_V = {
    "A": ["-++"],
    "B": ["-+-", "--+"],
    "C": ["-+-+", "--++", "-+--"],
}

BEREICH21 = {lv: {"muster": MUSTER21[lv], "var": SORTE1, "var2": SORTE2,
                  "zahlen": [ZAHLEN], "dreh": DREH} for lv in ("A", "B", "C")}


def _bereich(muster_dict):
    return {lv: {"muster": muster_dict[lv], "var": SORTE1, "var2": SORTE2,
                 "zahlen": [ZAHLEN], "dreh": DREH} for lv in ("A", "B", "C")}


def bau21(muster, glieder, extra=(), sorten=None):
    return bau(muster, glieder, extra=extra, sorten=sorten, tipps=TIPPS21,
               zusammenfassen=True)


def bf21_1(p):
    """Produkt in der Mitte, gleichartiges Glied dahinter:
       2a + 3a · 4b + 5ab"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [T(k[0], v1), P(k[1] * v1, k[2] * v2), T(k[3], v1 * v2)]
    glieder += [T(k[i], v1 * v2) for i in range(4, len(muster) + 1)]
    return bau21(muster, glieder, sorten=[v1, v1 * v2])


BF21_1 = Bauform("BF1", "Produkt in der Mitte, gleichartiges Glied dahinter",
    bereiche=BEREICH21, bauen=bf21_1, filter=ZWEI)


def bf21_2(p):
    """Produkt vorne, zwei gleichartige Glieder dahinter:
       5b · 2c − 3bc + bc"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2)]
    glieder += [T(k[i + 1], v1 * v2) for i in range(1, len(muster))]
    return bau21(muster, glieder)


BF21_2 = Bauform("BF2", "Produkt vorne, zwei gleichartige Glieder dahinter",
    bereiche=BEREICH21, bauen=bf21_2, filter=ZWEI + [loesung_nicht_null])


def bf21_3(p):
    """Eine Variable, Produkt und Zahlen:  3a · 2 + 4a − a"""
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1]), T(k[2], v1), T(k[3], v1)]
    #: Ab dem vierten Glied kommen reine Zahlen dazu — 5b · 3 − 2b + 4.
    glieder += [T(k[i]) if i % 2 == 0 else T(k[i], v1)
                for i in range(4, len(muster) + 1)]
    return bau21(muster, glieder)


BF21_3 = Bauform("BF3", "Eine Variable, Produkt und Zahlen",
    bereiche=BEREICH21, bauen=bf21_3, filter=STANDARD + [loesung_nicht_null])


def bf21_4(p):
    """Zwei Sorten bleiben nebeneinander stehen:  2x · 3y + 4x − x"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2), T(k[2], v1), T(k[3], v1)]
    glieder += [T(k[i], v1) for i in range(4, len(muster) + 1)]
    return bau21(muster, glieder, sorten=[v1 * v2, v1])


BF21_4 = Bauform("BF4", "Zwei Sorten bleiben nebeneinander stehen",
    bereiche=BEREICH21, bauen=bf21_4, filter=ZWEI)


def bf21_5(p):
    """Beide Sorten kommen mehrfach vor:  2u · 3v + 4uv + 5u − 2u"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2), T(k[2], v1 * v2), T(k[3], v1)]
    glieder += [T(k[i], v1 * v2 if i % 2 == 0 else v1)
                for i in range(4, len(muster) + 1)]
    return bau21(muster, glieder, sorten=[v1 * v2, v1])


BF21_5 = Bauform("BF5", "Beide Sorten kommen mehrfach vor",
    bereiche=BEREICH21, bauen=bf21_5, filter=ZWEI)


def bf21_6(p):
    """Dieselbe Variable im Produkt — es entsteht eine Potenz:
       2a · 3a + 4a

    Die Potenz steht nur im ERGEBNIS. Als Bestandteil der Aufgabe wäre sie
    Lektion 7.2 und damit zu früh (Teil 2 der Schablone).
    """
    v1, muster = p["var"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v1)]
    glieder += [T(k[i + 1], v1) for i in range(1, len(muster))]
    return bau21(muster, glieder, sorten=[v1 ** 2, v1])


BF21_6 = Bauform("BF6", "Dieselbe Variable im Produkt — es entsteht eine Potenz",
    bereiche=BEREICH21, bauen=bf21_6, filter=STANDARD)


def bf21_7(p):
    """Produkt wird abgezogen, danach zusammengefasst:
       5b − 5b · 2c + 3bc

    Das ist Erhebungsaufgabe 2a auf Level A.
    """
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [T(k[0], v1), P(k[1] * v1, k[2] * v2), T(k[3], v1 * v2)]
    glieder += [T(k[i], v1 if i % 2 == 0 else v1 * v2)
                for i in range(4, len(muster) + 1)]
    return bau21(muster, glieder, sorten=[v1, v1 * v2])


BF21_7 = Bauform("BF7", "Produkt wird abgezogen, danach zusammengefasst",
    bereiche=_bereich(MUSTER21_M), bauen=bf21_7, filter=ZWEI)


def bf21_8(p):
    """Sonderfall: das Ergebnis ist null:  3a · 2b + 4ab − 10ab"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2)]
    rest = [k[i + 1] for i in range(1, len(muster) - 1)]
    glieder += [T(r, v1 * v2) for r in rest]
    # Das letzte Glied gleicht genau aus, was vorher dasteht.
    vorher = sammeln(muster[:len(glieder)], glieder)
    ausgleich = sum(kk for kk, _ in vorher) if vorher else Integer(0)
    zeichen = muster[len(glieder)]
    glieder.append(T(ausgleich if zeichen == "-" else -ausgleich, v1 * v2))
    return bau21(muster, glieder, extra=[
        F("nicht_null", sum(abs(wert_glied(g)) for g in glieder),
          "Die Vorzeichen zählen mit — hier heben sich alle Glieder auf."),
    ])


BF21_8 = Bauform("BF8", "Sonderfall: das Ergebnis ist null",
    bereiche=_bereich(MUSTER21_N), bauen=bf21_8,
    filter=[kopfrechenbar, fehler_eindeutig, hat_fehler, glieder_positiv,
            symbole_verschieden("var", "var2")])


def bf21_9(p):
    """Sonderfall: nichts lässt sich zusammenfassen:  2a · 3 + 4b"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1]), T(k[2], v2)]
    glieder += [T(k[i + 1], v1 if i % 2 else v2)
                for i in range(2, len(muster))]
    return bau21(muster, glieder, sorten=[v1, v2])


BF21_9 = Bauform("BF9", "Sonderfall: nichts lässt sich zusammenfassen",
    bereiche=BEREICH21, bauen=bf21_9, filter=ZWEI)


def bf21_10(p):
    """Sonderfall: die Produktsorte fällt ganz weg:
       3x · 2y + 5x − 6xy"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2), T(k[2], v1)]
    #: Das letzte Glied hebt die Produktsorte genau auf.
    mitte = [T(k[i + 1], v1) for i in range(2, len(muster) - 1)]
    glieder += mitte
    zeichen = muster[len(glieder)]
    wert = k[0] * k[1]
    glieder.append(T(wert if zeichen == "-" else -wert, v1 * v2))
    return bau21(muster, glieder, sorten=[v1])


BF21_10 = Bauform("BF10", "Sonderfall: die Produktsorte fällt ganz weg",
    bereiche=_bereich(MUSTER21_N), bauen=bf21_10,
    filter=ZWEI + [loesung_nicht_null])


def bf21_11(p):
    """Minuszeichen am Anfang:  −2x · 3y + xy"""
    v1, v2, muster = p["var"], p["var2"], p["muster"]
    k = koeffizienten(p, len(muster) + 2)
    glieder = [P(k[0] * v1, k[1] * v2)]
    glieder += [T(k[i + 1], v1 * v2) for i in range(1, len(muster))]
    return bau21(muster, glieder)


BF21_11 = Bauform("BF11", "Minuszeichen am Anfang",
    bereiche=_bereich(MUSTER21_V), bauen=bf21_11,
    filter=ZWEI + [loesung_nicht_null])


S21 = Schablone(
    nr="S21", titel="Ausrechnen und danach zusammenfassen",
    lektionen="6.5 – 6.7", erhebung="2a",
    anleitung=ANLEITUNG,
    levelachse="Gliederzahl und Vorzeichen",
    bauformen=[BF21_1, BF21_2, BF21_3, BF21_4, BF21_5, BF21_6,
               BF21_7, BF21_8, BF21_9, BF21_10, BF21_11],
    kernidee=("Erst alle Produkte ausrechnen, dann zusammenfassen — und nur "
              "Glieder mit genau denselben Variablen gehören zusammen."),
)
