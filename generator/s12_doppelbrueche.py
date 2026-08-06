# -*- coding: utf-8 -*-
"""
S58 · Doppelbrüche und Gemischtes   (Lektionen 2.12 – 2.13)

    «Rechne aus. Gib das Resultat in gekürzter Form an.»
    (5/8)/(3/8)          →   5/3
    (5/8)/(10/9)         →   9/16
    (1/2 + 1/3)/(1/6)    →   5

WARUM S58 UND NICHT S12: die Nummer S12 ist seit Kapitel 3 vergeben
(generator/s3_terme.py). Kapitel 2 hat sechs Schablonen, für S7 bis S11
reichen fünf Nummern — die sechste musste woanders hin. S58 ist frei und
liegt neben S60, der anderen Schablone, die nachträglich dazugekommen ist.

Quelle: Lehrmittel A, Kapitel 1.5, Seite 55 (blauer Kasten «Doppelbrüche»
und die Aufgaben 63, 65, 66) sowie Seite 56 (Aufgabe 74, vermischte
Aufgaben zu den Brüchen).

ZWEI LEKTIONEN, EINE SCHABLONE:
2.12 sind die Doppelbrüche, 2.13 ist «alles aus Kapitel 2 kombiniert» —
die Mischlektion am Ende des Kapitels. Beide brauchen dieselbe Maschinerie:
mehrere Rechenarten in einer Aufgabe, Klammern, und am Ende kürzen.

DER GEDANKE, UM DEN ES GEHT: ein Doppelbruch ist nichts Neues. Der grosse
Bruchstrich ist ein Doppelpunkt. (a/b)/(c/d) ist a/b : c/d, und das kann
man seit Lektion 2.10. Wer das sieht, hat die Lektion; wer den Doppelbruch
für eine eigene Rechenart hält, rechnet Zähler durch Zähler und Nenner
durch Nenner — der häufigste Fehler und in jedem Katalog als
«getrennt_geteilt» vertreten.

SCHREIBWEISE: Der grosse Bruchstrich lässt sich in einer Textzeile nicht
darstellen, darum steht der Doppelbruch als (5/8)/(3/8) da. Das ist nicht
schön, aber eindeutig, und der Parser liest es richtig. Sobald die Anzeige
echte Bruchstriche kann, ändert sich hier nur der Anzeigetext, nicht die
Rechnung.

LEVELACHSE (Teil 2): **Aufbau von Zähler und Nenner des Doppelbruchs.**

    A   beide sind einfache Brüche          (5/8)/(3/8)
    B   einer davon ist eine ganze Zahl     (5/8)/2
        oder ein Produkt                    ((8/5)·(51/8))/(5/2)
    C   in Zähler oder Nenner steht         (1/2 + 1/3)/(1/6)
        eine Summe

Das ist eine STRUKTURELLE Achse: man sieht der Aufgabe an, auf welcher
Stufe sie steht. Die Zahlenvorräte sind auf allen drei Stufen dieselben.
"""
from __future__ import annotations

from sympy import Integer, Rational

from korrektur import Aufgabe, Fehler, Loesung, Zielform
from .qualitaet import fehler_eindeutig
from .s8_addition_subtraktion import F, br, als_text
from .schablone import Bauform, Schablone

VARS: set[str] = set()
ANLEITUNG = "Rechne aus. Gib das Resultat in gekürzter Form an."

ZAEHLER = [1, 2, 3, 4, 5, 7]
NENNER = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
GANZE = [2, 3, 4, 5, 6]

TIPPS = [
    "Der grosse Bruchstrich ist ein Doppelpunkt: (a/b)/(c/d) heisst a/b : c/d.",
    "Und Teilen heisst Malnehmen mit dem Kehrwert — den unteren Bruch stürzen.",
    "",
]


def _siebe(katalog, ziel: Rational):
    """Wertgleiche, doppelte und zu nahe Einträge entfernen.

    Zur Abstandsregel siehe S10: die Korrektur akzeptiert Dezimalantworten
    auf zwei Stellen, und zwei Werte, die näher als ein Hundertstel
    beieinanderliegen, lassen sich mit demselben Tastendruck treffen.
    """
    raus, gesehen = [], set()
    for f in katalog:
        e = f.ergebnis.expr
        if e is None:
            continue
        wert = Rational(e)
        if wert == ziel or str(wert) in gesehen:
            continue
        if abs(float(wert) - float(ziel)) < 0.01:
            continue
        gesehen.add(str(wert))
        raus.append(f)
    return raus


def bau(oben: Rational, unten: Rational, frage, teile_oben, teile_unten,
        extra=()):
    """oben und unten sind die WERTE von Zähler und Nenner des Doppelbruchs.

    teile_oben / teile_unten: die einzelnen Brüche, aus denen sie bestehen —
    daraus entstehen die Fehlereinträge «getrennt geteilt» und «gestürzt».
    """
    loesung = oben / unten
    text = als_text(loesung)

    # Zähler durch Zähler, Nenner durch Nenner — der Klassiker.
    getrennt = None
    if len(teile_oben) == 1 and len(teile_unten) == 1:
        (zo, no), (zu, nu) = teile_oben[0], teile_unten[0]
        if zu and nu:
            getrennt = Rational(zo, zu) / Rational(no, nu) * Rational(1) \
                if False else Rational(zo * nu, no * zu) * 0 + \
                Rational(zo, zu) / Rational(no, nu)
            getrennt = Rational(zo, zu) / Rational(no, nu)

    katalog = list(extra) + [
        F("getrennt_geteilt", getrennt,
          "Ein Doppelbruch wird nicht Zähler durch Zähler und Nenner durch "
          "Nenner gerechnet. Der grosse Strich ist ein Doppelpunkt."),
        F("nicht_gestuerzt", oben * unten,
          "Der untere Bruch muss gestürzt werden, bevor malgenommen wird."),
        F("falsch_herum", unten / oben if oben else None,
          "Oben geteilt durch unten — nicht umgekehrt."),
        F("nur_oben", oben, "Der Nenner des Doppelbruchs fehlt."),
        F("nur_unten", unten, "Der Zähler des Doppelbruchs fehlt."),
        F("gestuerzt", Rational(loesung.q, loesung.p) if loesung.p else None,
          "Zähler und Nenner des Ergebnisses sind vertauscht."),
        F("summe_statt_quotient", oben + unten,
          "Der Bruchstrich bedeutet teilen, nicht addieren."),
        F("um_eins_zu_gross", loesung + 1,
          "Da ist eine ganze Einheit zu viel im Ergebnis."),
        # Die folgenden drei sind gegen die Lösung immer verschieden und
        # fangen die Fälle ab, in denen oben und unten ähnlich gebaut sind
        # und darum die halbe Liste beim Sieben wegfliegt.
        F("um_eins_zu_klein", loesung - 1,
          "Da fehlt eine ganze Einheit im Ergebnis."),
        F("halbiert", loesung / 2,
          "Das Ergebnis ist halb so gross, wie es sein müsste."),
        F("verdoppelt", loesung * 2,
          "Das Ergebnis ist doppelt so gross, wie es sein müsste."),
    ]
    katalog = _siebe(katalog, loesung)

    return {
        "frage": frage,
        "loesung_text": text,
        "aufgabe": Aufgabe(loesung=Loesung.zahl(loesung), variablen=VARS,
                           zielform=Zielform.GEKUERZT,
                           # Keine Dezimaltoleranz in Kapitel 2. Sonst gilt
                           # «0.78» fuer 7/9 als richtig — in einer Lektion,
                           # deren ganzer Sinn die gekuerzte Bruchform ist.
                           # In spaeteren Kapiteln bleibt die Toleranz, dort
                           # ist die Kommazahl eine legitime Antwort.
                           dezimal_stellen=None,
                           fehlerkatalog=katalog),
        "schritte": [
            ("Zähler und Nenner einzeln ausrechnen",
             f"oben {als_text(oben)}, unten {als_text(unten)}"),
            ("Der grosse Strich ist ein Doppelpunkt",
             f"{als_text(oben)} : {als_text(unten)}"),
            ("Den unteren stürzen und malnehmen",
             f"{als_text(oben)} · {br(unten.q, unten.p)}"
             if unten.p else "—"),
            ("Kürzen", text),
        ],
        "tipps": TIPPS,
    }


BEREICHE = {lv: {"z1": ZAEHLER, "z2": ZAEHLER, "z3": ZAEHLER,
                 "n1": NENNER, "n2": NENNER, "n3": NENNER,
                 "k": GANZE, "stufe": [s]}
            for lv, s in (("A", "einfach"), ("B", "zusammengesetzt"),
                          ("C", "summe"))}


def _nicht_trivial(p, g) -> bool:
    return g["loesung_text"] not in ("0", "1")


def _handlich(p, g) -> bool:
    import re as _re
    return all(int(x) <= 300 for x in _re.findall(r"\d+", g["loesung_text"]))


def _frage_gekuerzt(p, g) -> bool:
    """Kein ungekürzter Bruch in der Aufgabenstellung."""
    import re as _re
    from math import gcd
    for z, n in _re.findall(r"(\d+)/(\d+)", g["frage"]):
        if gcd(int(z), int(n)) > 1:
            return False
    return True


STANDARD = [fehler_eindeutig, _nicht_trivial, _handlich, _frage_gekuerzt]


def _stufe_teil(p, welche: str):
    """Baut eine Seite des Doppelbruchs — je nach Stufe anders aufgebaut.

    Genau hier sitzt die Levelachse. Rückgabe: (Wert, Anzeigetext, Teile).
    """
    stufe = p["stufe"]
    if welche == "oben":
        z, n, z2, n2 = p["z1"], p["n1"], p["z3"], p["n3"]
    else:
        z, n, z2, n2 = p["z2"], p["n2"], p["z3"], p["n3"]

    if stufe == "einfach":
        return Rational(z, n), br(z, n), [(z, n)]
    if stufe == "zusammengesetzt":
        if welche == "oben":
            wert = Rational(z, n) * Rational(z2, n2)
            return wert, f"({br(z, n)} · {br(z2, n2)})", [(z, n), (z2, n2)]
        return Rational(z, n), br(z, n), [(z, n)]
    # summe
    if welche == "oben":
        wert = Rational(z, n) + Rational(z2, n2)
        return wert, f"({br(z, n)} + {br(z2, n2)})", [(z, n), (z2, n2)]
    return Rational(z, n), br(z, n), [(z, n)]


def _aufbauen(wert, text, teile, p):
    """Hebt den ZÄHLER auf die Aufbaustufe des Levels.

    Ohne das sähen A, B und C bei den meisten Bauformen gleich aus — nur
    mit anderen Zahlen. Der Testlauf beanstandet das zu Recht: ein Level,
    das man der Aufgabe nicht ansieht, ist für den Schüler kein Level.

        einfach          der Zähler bleibt, wie er ist
        zusammengesetzt  ein Faktor kommt dazu       (a/b · c/d)
        summe            ein Summand kommt dazu      (a/b + c/d)
    """
    stufe = p["stufe"]
    if stufe == "einfach":
        return wert, text, teile
    z, n = p["z3"], p["n3"] + 1
    #: Die Klammern NICHT wegnehmen, wenn im Text ein Plus oder Minus steht.
    #: «(2/7 + 1/8)» wurde sonst zu «(2/7 + 1/8 · 1/8)», und das liest der
    #: Parser als 2/7 + (1/8 · 1/8) — Punkt vor Strich. Die angezeigte Frage
    #: wäre eine andere als die gerechnete. Genau dieser Fehlertyp hatte
    #: früher einmal eine ganze Bauform unbrauchbar gemacht.
    hat_strich = "+" in text or "−" in text
    innen = text if (hat_strich or not text.startswith("(")) else text[1:-1]
    if hat_strich and not text.startswith("("):
        innen = f"({text})"
    if stufe == "zusammengesetzt":
        return (wert * Rational(z, n), f"({innen} · {br(z, n)})",
                teile + [(z, n)])
    return (wert + Rational(z, n), f"({innen} + {br(z, n)})",
            teile + [(z, n)])


def _doppelbruch(p, unten_ganz=False, unten_stamm=False):
    o_wert, o_text, o_teile = _stufe_teil(p, "oben")
    if unten_ganz:
        u_wert, u_text, u_teile = Rational(p["k"]), str(p["k"]), [(p["k"], 1)]
    elif unten_stamm:
        u_wert = Rational(1, p["n2"])
        u_text, u_teile = br(1, p["n2"]), [(1, p["n2"])]
    else:
        u_wert, u_text, u_teile = _stufe_teil(p, "unten")
    # Beide Seiten IMMER klammern. Der frühere Versuch, überflüssige
    # Klammern zu sparen, erzeugte «(5/8 · 4/5)/5/4» — und das liest der
    # Parser als 5/8 · 4/5 : 5 : 4, also etwas ganz anderes.
    def _klammer(txt):
        return txt if txt.startswith("(") else f"({txt})"

    frage = f"{_klammer(o_text)}/{_klammer(u_text)}"
    return bau(o_wert, u_wert, frage, o_teile, u_teile)


# ── BF1 bis BF3 · die Grundformen ────────────────────────────────────────
BF1 = Bauform("BF1", "Doppelbruch aus zwei Brüchen",
    bereiche=BEREICHE, bauen=lambda p: _doppelbruch(p), filter=STANDARD)

BF2 = Bauform("BF2", "Der Nenner ist eine ganze Zahl",
    bereiche=BEREICHE, bauen=lambda p: _doppelbruch(p, unten_ganz=True),
    filter=STANDARD)

BF3 = Bauform("BF3", "Der Nenner ist ein Stammbruch — das Ergebnis wächst",
    bereiche=BEREICHE, bauen=lambda p: _doppelbruch(p, unten_stamm=True),
    filter=STANDARD)


# ── BF4 · Gleiche Nenner oben und unten ──────────────────────────────────
def bf4(p):
    """(5/8)/(3/8) — Aufgabe 63 a im Lehrmittel. Die Nenner heben sich weg."""
    n = p["n1"]
    o_wert, o_text, o_teile = _aufbauen(
        Rational(p["z1"], n), br(p["z1"], n), [(p["z1"], n)], p)
    u_wert, u_text, u_teile = Rational(p["z2"], n), br(p["z2"], n), [(p["z2"], n)]
    if not o_text.startswith("("):
        o_text = f"({o_text})"
    return bau(o_wert, u_wert, f"{o_text}/({u_text})", o_teile, u_teile,
               extra=[
        F("nenner_behalten", Rational(p["z1"], p["z2"] * n) if p["z2"] else None,
          "Die gleichen Nenner heben sich weg. Es bleibt Zähler durch "
          "Zähler."),
    ])


BF4 = Bauform("BF4", "Gleiche Nenner oben und unten",
    bereiche=BEREICHE, bauen=bf4, filter=STANDARD)


# ── BF5 · Ganze Zahl über einem Bruch ────────────────────────────────────
def bf5(p):
    """6/(1/7) — Aufgabe 66 b. Teilen durch einen Stammbruch vervielfacht."""
    k, n = p["k"], p["n2"]
    o_wert, o_text, o_teile = _aufbauen(Rational(k), str(k), [(k, 1)], p)
    if not o_text.startswith("("):
        o_text = f"({o_text})"
    return bau(o_wert, Rational(1, n), f"{o_text}/({br(1, n)})",
               o_teile, [(1, n)], extra=[
        F("mal_statt_geteilt_stamm", o_wert * Rational(1, n),
          f"Durch 1/{n} teilen heisst mit {n} malnehmen — das Ergebnis wird "
          f"grösser, nicht kleiner."),
    ])


BF5 = Bauform("BF5", "Ganze Zahl über einem Stammbruch",
    bereiche=BEREICHE, bauen=bf5, filter=STANDARD)


# ── BF6 · Summe im Zähler ────────────────────────────────────────────────
def bf6(p):
    """(1/2 + 1/3)/(1/6) — Aufgabe 65 a. Erst oben zusammenfassen."""
    o, o_text, o_teile = _aufbauen(
        Rational(p["z1"], p["n1"]) + Rational(p["z3"], p["n3"]),
        f"({br(p['z1'], p['n1'])} + {br(p['z3'], p['n3'])})",
        [(p["z1"], p["n1"]), (p["z3"], p["n3"])], p)
    u = Rational(1, p["n2"])
    frage = f"{o_text}/({br(1, p['n2'])})"
    return bau(o, u, frage, o_teile, [(1, p["n2"])], extra=[
        F("nur_ein_summand",
          Rational(p["z1"], p["n1"]) / u,
          "Der zweite Summand im Zähler fehlt."),
    ])


BF6 = Bauform("BF6", "Summe im Zähler",
    bereiche=BEREICHE, bauen=bf6, filter=STANDARD)


# ── BF7 · Summe im Nenner ────────────────────────────────────────────────
def bf7(p):
    """(2/3)/(3/4 + 5/6) — Aufgabe 65 b. Erst unten zusammenfassen."""
    o, o_text, o_teile = _aufbauen(
        Rational(p["z1"], p["n1"]), br(p["z1"], p["n1"]),
        [(p["z1"], p["n1"])], p)
    if not o_text.startswith("("):
        o_text = f"({o_text})"
    u = Rational(p["z2"], p["n2"]) + Rational(p["z3"], p["n3"])
    frage = (f"{o_text}"
             f"/({br(p['z2'], p['n2'])} + {br(p['z3'], p['n3'])})")
    return bau(o, u, frage, o_teile,
               [(p["z2"], p["n2"]), (p["z3"], p["n3"])], extra=[
        F("nenner_nicht_zusammengefasst",
          o / Rational(p["z2"], p["n2"]),
          "Im Nenner steht eine Summe — die muss zuerst zusammengefasst "
          "werden."),
    ])


BF7 = Bauform("BF7", "Summe im Nenner",
    bereiche=BEREICHE, bauen=bf7, filter=STANDARD)


# ── BF8 · Differenz im Zähler ────────────────────────────────────────────
def bf8(p):
    """(1/4 − 1/5)/(1/20) — Aufgabe 65 d."""
    o, o_text, o_teile = _aufbauen(
        Rational(p["z1"], p["n1"]) - Rational(p["z3"], p["n3"]),
        f"({br(p['z1'], p['n1'])} − {br(p['z3'], p['n3'])})",
        [(p["z1"], p["n1"])], p)
    u = Rational(1, p["n2"])
    frage = f"{o_text}/({br(1, p['n2'])})"
    return bau(o, u, frage, o_teile, [(1, p["n2"])], extra=[
        F("plus_statt_minus",
          (o + 2 * Rational(p["z3"], p["n3"])) / u,
          "Im Zähler steht ein Minus."),
    ])


BF8 = Bauform("BF8", "Differenz im Zähler",
    bereiche=BEREICHE, bauen=bf8, filter=STANDARD)


# ── BF9 · Produkt im Zähler ──────────────────────────────────────────────
def bf9(p):
    """((8/5)·(51/8))/(5/2) — Aufgabe 63 e. Erst oben malnehmen."""
    o, o_text, o_teile = _aufbauen(
        Rational(p["z1"], p["n1"]) * Rational(p["z3"], p["n3"]),
        f"({br(p['z1'], p['n1'])} · {br(p['z3'], p['n3'])})",
        [(p["z1"], p["n1"])], p)
    u = Rational(p["z2"], p["n2"])
    frage = f"{o_text}/({br(p['z2'], p['n2'])})"
    return bau(o, u, frage, o_teile, [(p["z2"], p["n2"])])


BF9 = Bauform("BF9", "Produkt im Zähler",
    bereiche=BEREICHE, bauen=bf9, filter=STANDARD)


# ── BF10 · Gemischte Rechenarten in einer Zeile (Lektion 2.13) ───────────
def bf10(p):
    """1/6 + 11/15 : 6 — Aufgabe 74 e. Punkt vor Strich, ohne Doppelbruch.

    Das ist die Mischform aus Lektion 2.13: Addition und Division in einer
    Aufgabe. Der Fehler, den sie abfragt, ist nicht neu — es ist Punkt vor
    Strich, und wer von links nach rechts rechnet, bekommt etwas anderes.
    """
    a = Rational(p["z1"], p["n1"])
    b = Rational(p["z2"], p["n2"])
    k = p["k"]
    loesung = a + b / k
    frage = f"{br(p['z1'], p['n1'])} + {br(p['z2'], p['n2'])} : {k}"
    #: Die Zahl der Glieder wächst mit dem Level — das ist hier die einzige
    #: Achse, die man der Aufgabe ansieht.
    if p["stufe"] != "einfach":
        c = Rational(p["z3"], p["n3"])
        loesung = loesung + c
        frage += f" + {br(p['z3'], p['n3'])}"
    if p["stufe"] == "summe":
        loesung = loesung - Rational(1, p["n3"])
        frage += f" − {br(1, p['n3'])}"
    return bau(loesung, Rational(1), frage,
               [(loesung.p, loesung.q)], [(1, 1)], extra=[
        F("von_links", (a + b) / k,
          "Punkt vor Strich: erst die Division, dann die Addition."),
        F("mal_statt_geteilt", a + b * k,
          "Hier steht ein Doppelpunkt, kein Malpunkt."),
        F("nur_erster_summand", a, "Der zweite Teil fehlt."),
        F("ganze_zahl_ignoriert", a + b,
          f"Durch {k} teilen wurde vergessen."),
    ])


BF10 = Bauform("BF10", "Gemischt: Punkt vor Strich in einer Zeile",
    bereiche=BEREICHE, bauen=bf10, filter=STANDARD)


# ── BF11 · Sonderfall: das Ergebnis ist eins ─────────────────────────────
def bf11(p):
    """(3/5)/(3/5) = 1 — oben und unten dasselbe."""
    z, n = p["z1"], p["n1"]
    if z == n:
        z, n = 2, 3
    w = Rational(z, n)
    #: Damit A, B und C verschieden aussehen, wächst BEIDE Seiten mit —
    #: sonst stünde dreimal dieselbe Form da.
    z2, n2 = p["z3"], p["n3"]
    if p["stufe"] == "einfach":
        seite, w = br(z, n), Rational(z, n)
    elif p["stufe"] == "zusammengesetzt":
        seite = f"{br(z, n)} · {br(z2, n2)}"
        w = Rational(z, n) * Rational(z2, n2)
    else:
        seite = f"{br(z, n)} + {br(z2, n2)}"
        w = Rational(z, n) + Rational(z2, n2)
    return bau(w, w, f"({seite})/({seite})", [(z, n)], [(z, n)],
               extra=[
        F("quadriert", w * w,
          "Oben und unten steht dasselbe — das ergibt eins."),
        F("null", Integer(0), "Gleich durch gleich ist eins, nicht null."),
        F("zwei", Integer(2), "Nachrechnen: es bleibt genau eins."),
        F("nenner_als_antwort", Integer(n),
          "Das ist der Nenner, nicht das Ergebnis."),
        F("zaehler_als_antwort", Integer(z),
          "Das ist der Zähler, nicht das Ergebnis."),
        F("nur_eine_seite", w, "Oben und unten steht dasselbe — das kürzt "
          "sich zu eins."),
        F("minus_eins", Integer(-1), "Gleich durch gleich ist eins."),
        F("summe", w + w, "Der Bruchstrich bedeutet teilen, nicht addieren."),
    ])


def _ergibt_eins(p, g) -> bool:
    return g["loesung_text"] == "1"


BF11 = Bauform("BF11", "Sonderfall: oben und unten dasselbe",
    bereiche=BEREICHE, bauen=bf11,
    filter=[fehler_eindeutig, _ergibt_eins, _frage_gekuerzt])


# ── BF12 · Sonderfall: der Zähler ist null ───────────────────────────────
def bf12(p):
    """(0)/(3/5) = 0. Null geteilt durch etwas bleibt null.

    Die Umkehrung — ein Nenner null — kommt bewusst nicht vor: sie ist nicht
    definiert, und eine Aufgabe ohne Lösung gehört nicht in eine Übung, in
    der jede Eingabe eine Rückmeldung bekommen soll.
    """
    z, n = p["z2"], p["n2"]
    u = Rational(z, n)
    z2, n2 = p["z3"], p["n3"]
    if p["stufe"] == "einfach":
        unten_text = br(z, n)
    elif p["stufe"] == "zusammengesetzt":
        unten_text = f"{br(z, n)} · {br(z2, n2)}"
        u = u * Rational(z2, n2)
    else:
        unten_text = f"{br(z, n)} + {br(z2, n2)}"
        u = u + Rational(z2, n2)
    return bau(Rational(0), u, f"(0)/({unten_text})", [(0, 1)], [(z, n)],
               extra=[
        F("null_ignoriert", u, "Null geteilt durch irgendetwas bleibt null."),
        F("kehrwert", Rational(n, z) if z else None,
          "Der Zähler ist null — dann ist alles null."),
        F("eins", Integer(1), "Null durch etwas ist null, nicht eins."),
        F("minus_eins", Integer(-1), "Null bleibt null."),
        F("zwei", Integer(2), "Nachrechnen: null bleibt null."),
        F("nenner_abgeschrieben", u, "Das ist der Nenner. Oben steht null."),
        F("drei", Integer(3), "Null geteilt durch etwas bleibt null."),
    ])


def _ergibt_null(p, g) -> bool:
    return g["loesung_text"] == "0"


BF12 = Bauform("BF12", "Sonderfall: der Zähler ist null",
    bereiche=BEREICHE, bauen=bf12,
    filter=[fehler_eindeutig, _ergibt_null, _frage_gekuerzt])


S58 = Schablone(
    nr="S58", titel="Doppelbrüche und Gemischtes",
    lektionen="2.12 – 2.13", erhebung="",
    anleitung=ANLEITUNG,
    levelachse="Aufbau von Zähler und Nenner",
    bauformen=[BF1, BF2, BF3, BF4, BF5, BF6,
               BF7, BF8, BF9, BF10, BF11, BF12],
    kernidee=("Ein Doppelbruch ist nichts Neues: der grosse Bruchstrich ist "
              "ein Doppelpunkt. (a/b)/(c/d) heisst a/b : c/d."),
)
