# -*- coding: utf-8 -*-
"""
Theorie als Schritt-für-Schritt-Animation statt als Textblock.

Bisher stand am Anfang jeder Lektion Teil 6 der Schablone als Satz:

    «Ein Minus vor der Klammer kehrt jedes Vorzeichen darin um.»

Das liest niemand. Neu wird dieselbe Idee VORGEFÜHRT: eine Beispielaufgabe,
die sich in drei bis fünf Schritten selbst umformt, mit einem kurzen Satz je
Schritt. Bei «Minus vor der Klammer» heisst das:

    Schritt 1   −(4 + 3)        das Minus wird markiert
    Schritt 2   −4 − 3          jedes Vorzeichen darin ist gedreht
    Schritt 3   −7              die Klammer ist weg, fertig

DAS DATENMODELL IST BEWUSST ARM. Eine Animation ist eine Liste von
Schritten, ein Schritt ist eine Zeile aus Textstuecken mit einem Stil. Mehr
braucht es nicht — und weil es so wenig ist, laesst sich eine Animation in
zehn Zeilen schreiben. Bei 43 Schablonen ist das der Unterschied zwischen
machbar und nicht machbar.

Vier Stile:

    ""       gewoehnlich
    "mark"   hervorgehoben — das, worum es in diesem Schritt geht
    "neu"    hat sich gegenueber dem Schritt davor geaendert
    "weg"    verschwindet in diesem Schritt (blass, durchgestrichen)

Die Sprache der Erklaerungen ist fuer alle gedacht: kurze Hauptsaetze, kein
Fachwort ohne Erklaerung, keine Anrede, die nur zu Kindern passt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .anzeige import MINUS


@dataclass
class Schritt:
    """Eine Zeile der Animation plus der Satz dazu."""
    #: Textstuecke als (Text, Stil) oder (Text, Stil, Schluessel).
    #:
    #: DER SCHLUESSEL IST DAS HERZ DER ANIMATION. Stuecke mit demselben
    #: Schluessel sind ueber die Schritte hinweg DASSELBE Element: es bleibt
    #: stehen, rutscht an seinen neuen Platz und dreht sich um, wenn sich
    #: sein Text aendert. Nur was keinen Partner hat, wird ein- oder
    #: ausgeblendet.
    #:
    #: Ohne Schluessel wird der Text selbst genommen. Dann bleibt stehen,
    #: was gleich heisst — das genuegt fuer einfache Faelle.
    teile: list[tuple]
    #: Ein kurzer Satz. Hoechstens rund zwoelf Woerter — er wird gelesen,
    #: waehrend die Zeile schon dasteht.
    text: str


@dataclass
class Animation:
    """Die Theorie einer Schablone, vorgefuehrt statt beschrieben."""
    titel: str
    schritte: list[Schritt] = field(default_factory=list)
    #: Der Merksatz, der am Ende stehen bleibt. Das ist Teil 6 der Schablone.
    merksatz: str = ""

    def als_dict(self) -> dict:
        """Fuer die Vorlage — dort wird daraus JSON."""
        return {
            "titel": self.titel,
            "merksatz": self.merksatz,
            "schritte": [{"teile": _teile(sch.teile), "text": sch.text}
                         for sch in self.schritte],
        }


def _teile(rohe) -> list[dict]:
    """Teile normalisieren und jedem einen eindeutigen Schluessel geben."""
    raus, gesehen = [], {}
    for stueck in rohe:
        text, stil = stueck[0], stueck[1]
        schluessel = stueck[2] if len(stueck) > 2 else text.strip() or "leer"
        gesehen[schluessel] = gesehen.get(schluessel, 0) + 1
        if gesehen[schluessel] > 1:
            schluessel = f"{schluessel}#{gesehen[schluessel]}"
        raus.append({"t": text, "s": stil, "k": schluessel})
    return raus


def S(text_, *teile) -> Schritt:
    """Kurzschreibweise.

        S("Das Minus gilt für alles",
          ("−", "mark", "op"), (" (4 + 3)", ""))

    Das dritte Feld ist der Schluessel — hier «op». Taucht «op» im naechsten
    Schritt wieder auf, wandert dasselbe Element dorthin, statt neu gezeichnet
    zu werden.
    """
    return Schritt(teile=list(teile), text=text_)


# ══════════════════════════════════════════════════════════════════════════
# Die Animationen
# ══════════════════════════════════════════════════════════════════════════

#: S10 · Minus vor der Klammer — das haeufigste Ruecksprungziel im ganzen Netz.
#: Genau der Ablauf, den du beschrieben hast: markieren, drehen, Klammer weg.
MINUS_KLAMMER = Animation(
    titel="Minus vor der Klammer",
    schritte=[
        S("Vor der Klammer steht ein Minus. Merk dir das.",
          ("20", "", "a"), ("−", "mark", "op"), ("(", "", "kl1"),
          ("7", "", "z1"), ("+", "", "op1"), ("5", "", "z2"), (")", "", "kl2")),
        S("Es gilt für alles in der Klammer — für die 7 und für die 5.",
          ("20", "", "a"), ("−", "mark", "op"), ("(", "", "kl1"),
          ("7", "mark", "z1"), ("+", "", "op1"), ("5", "mark", "z2"),
          (")", "", "kl2")),
        S("Jedes Zeichen darin dreht sich um: aus plus wird minus.",
          ("20", "", "a"), ("−", "", "op"), ("(", "weg", "kl1"),
          ("7", "", "z1"), ("−", "neu", "op1"), ("5", "", "z2"),
          (")", "weg", "kl2")),
        S("Die Klammer wird nicht mehr gebraucht.",
          ("20", "", "a"), ("−", "", "op"), ("7", "", "z1"),
          ("−", "", "op1"), ("5", "", "z2")),
        S("Jetzt von links nach rechts rechnen: 20 − 7 = 13.",
          ("13", "neu", "a"), ("−", "", "op1"), ("5", "", "z2")),
        S("Fertig.", ("8", "neu", "a")),
    ],
    merksatz="Ein Minus vor der Klammer dreht jedes Vorzeichen darin um — "
             "auch das zweite und dritte.",
)

#: S16 · Gleichartige Terme
GLEICHARTIGE = Animation(
    titel="Gleichartige Terme zusammenfassen",
    schritte=[
        S("Schau dir an, welche Teile genau gleich aussehen.",
          ("4a²", "", "q1"), ("−", "", "m1"), ("2a", "", "e1"),
          ("+", "", "p1"), ("3a²", "", "q2")),
        S("4a² und 3a² sind gleichartig: gleiche Variable, gleiche Hochzahl.",
          ("4a²", "mark", "q1"), ("−", "", "m1"), ("2a", "", "e1"),
          ("+", "", "p1"), ("3a²", "mark", "q2")),
        S("Sie rücken zusammen — nur ihre Zahlen werden verrechnet.",
          ("4a²", "mark", "q1"), ("+", "", "p1"), ("3a²", "mark", "q2"),
          ("−", "", "m1"), ("2a", "", "e1")),
        S("4 + 3 = 7. Aus zwei Gliedern wird eines.",
          ("7a²", "neu", "q1"), ("−", "", "m1"), ("2a", "", "e1")),
        S("2a hat keine Hochzahl und bleibt allein stehen.",
          ("7a²", "", "q1"), ("−", "", "m1"), ("2a", "mark", "e1")),
        S("Fertig. Zwei verschiedene Sorten bleiben nebeneinander.",
          ("7a²", "neu", "q1"), ("−", "", "m1"), ("2a", "neu", "e1")),
    ],
    merksatz="Gleichartig sind nur Terme mit genau denselben Variablen und "
             "denselben Hochzahlen. Beim Zusammenfassen werden ihre Zahlen "
             "addiert.",
)

#: S20 · Punkt vor Strich mit Variablen — Lektionen 6.1 bis 6.4.
#: Hier wird nur ausgerechnet. Was danach mit den Gliedern passiert, ist
#: Lektion 6.5 und hat mit PUNKT_VOR_STRICH eine eigene Animation.
PUNKT_ZUERST = Animation(
    titel="Punkt vor Strich mit Variablen",
    schritte=[
        S("Geh den Term durch und such das Malzeichen.",
          ("3x", "", "a"), ("+", "", "op"), ("2 · 4x", "mark", "p")),
        S("Punkt vor Strich: das Mal wird zuerst gerechnet, auch mit Buchstaben.",
          ("3x", "", "a"), ("+", "", "op"), ("2 · 4x", "mark", "p")),
        S("Die Zahlen werden malgenommen: 2 · 4 = 8. Das x bleibt.",
          ("3x", "", "a"), ("+", "", "op"), ("8x", "neu", "p")),
        S("Jetzt steht nur noch ein Plus da.",
          ("3x", "mark", "a"), ("+", "mark", "op"), ("8x", "mark", "p")),
        S("3x und 8x sind gleichartig — beide haben genau ein x.",
          ("3x", "mark", "a"), ("+", "", "op"), ("8x", "mark", "p")),
        S("Zusammenzählen: 3 + 8 = 11. Fertig.",
          ("11x", "neu", "a")),
    ],
    merksatz="Punkt vor Strich gilt auch mit Variablen: erst multiplizieren, "
             "dann addieren oder subtrahieren.",
)

#: S21 · Ausrechnen und danach zusammenfassen — Lektionen 6.5 bis 6.7.
#: Der Term ist Erhebungsaufgabe 2a.
PUNKT_VOR_STRICH = Animation(
    titel="Ausrechnen und dann zusammenfassen",
    schritte=[
        S("Suche zuerst das Mal- oder Geteiltzeichen.",
          ("5b ", ""), ("− 5b · 2c", "mark"), (" + 3bc", "")),
        S("Das Mal wird zuerst gerechnet, auch wenn es in der Mitte steht.",
          ("5b − ", ""), ("10bc", "neu"), (" + 3bc", "")),
        S("Jetzt bleiben nur noch Plus und Minus übrig.",
          ("5b ", ""), ("− 10bc + 3bc", "mark")),
        S("bc-Glieder zusammenfassen: −10 + 3 = −7.",
          ("5b ", ""), ("− 7bc", "neu")),
        S("Fertig. b und bc sind verschiedene Sorten.",
          ("5b − 7bc", "neu")),
    ],
    merksatz="Klammer vor Punkt vor Strich. Erst das Mal ausrechnen, dann "
             "gleichartige Glieder zusammenfassen.",
)

#: S30 · Terme dividieren — Lektionen 9.1 bis 9.3.
DIVIDIEREN = Animation(
    titel="Terme dividieren",
    schritte=[
        S("Oben steht 12ab, unten 4a. Schau beides getrennt an.",
          ("12ab", "mark", "o"), (" : ", "", "op"), ("(4a)", "mark", "u")),
        S("Zuerst die Zahlen: 12 : 4 ergibt 3.",
          ("3", "neu", "o"), (" · ", "", "op"), ("ab : a", "", "u")),
        S("Jetzt jede Variable: steht sie oben UND unten?",
          ("3", "", "o"), ("a", "mark", "u"), ("b", "", "b")),
        S("Das a steht oben und unten — es fällt weg.",
          ("3", "", "o"), ("a", "weg", "u"), ("b", "", "b")),
        S("Das b steht nur oben und bleibt stehen. Fertig: 3b.",
          ("3b", "neu", "o")),
    ],
    merksatz="Beim Dividieren werden die Zahlen geteilt, und jede Variable, "
             "die oben und unten steht, fällt weg.",
)

#: S31 · Summe durch Monom — Lektionen 9.4 und 9.5.
#: Das aufgehende Glied ist der gefaehrliche Punkt: dort bleibt eine 1.
SUMME_TEILEN = Animation(
    titel="Eine Summe dividieren",
    schritte=[
        S("Oben steht eine Summe aus drei Gliedern.",
          ("(18u⁴ − 12u³ + 2u²)", "mark", "o"), (" : (2u²)", "", "u")),
        S("Jedes Glied wird EINZELN geteilt, nicht die Summe als Ganzes.",
          ("18u⁴ : 2u²", "neu", "g1"), ("−", "", "m"),
          ("12u³ : 2u²", "neu", "g2"), ("+", "", "p"),
          ("2u² : 2u²", "neu", "g3")),
        S("Zahlen teilen, Hochzahlen subtrahieren: 4 − 2 = 2.",
          ("9u²", "neu", "g1"), ("−", "", "m"), ("6u", "neu", "g2"),
          ("+", "", "p"), ("2u² : 2u²", "", "g3")),
        S("Das letzte Glied geht ganz auf — dort bleibt eine 1 stehen.",
          ("9u²", "", "g1"), ("−", "", "m"), ("6u", "", "g2"),
          ("+", "", "p"), ("1", "mark", "g3")),
        S("Wer die 1 weglässt, verliert ein ganzes Glied.",
          ("9u² − 6u", "weg", "falsch")),
        S("Fertig: 9u² − 6u + 1.",
          ("9u² − 6u + 1", "neu", "g1")),
    ],
    merksatz="Beim Dividieren werden die Zahlen geteilt und die Hochzahlen "
             "subtrahiert. Steht im Zähler eine Summe, wird jedes Glied "
             "einzeln geteilt — auch das, welches ganz aufgeht.",
)

#: S32 · Division in einem laengeren Term — Lektion 9.6, Erhebung 2c.
DIVISION_IM_TERM = Animation(
    titel="Wie weit die Division gilt",
    schritte=[
        S("Zwei Glieder sehen gleich aus — aber dazwischen steht ein Plus.",
          ("12ab", "", "a"), (" + ", "mark", "op"), ("21ab : (7a)", "", "b")),
        S("Die Division ist eine Punktrechnung und bindet stärker.",
          ("12ab", "", "a"), (" + ", "", "op"),
          ("21ab : (7a)", "mark", "b")),
        S("Geteilt wird nur 21ab, nicht 12ab + 21ab.",
          ("12ab", "weg", "a"), (" + ", "", "op"),
          ("21ab : (7a)", "mark", "b")),
        S("21ab : (7a) ergibt 3b. Das a fällt weg.",
          ("12ab", "", "a"), (" + ", "", "op"), ("3b", "neu", "b")),
        S("12ab hat ein a, 3b nicht — sie gehören nicht zusammen.",
          ("12ab", "mark", "a"), (" + ", "", "op"), ("3b", "mark", "b")),
        S("Fertig. 12ab + 3b ist die Antwort.",
          ("12ab + 3b", "neu", "a")),
    ],
    merksatz="Eine Division ist eine Punktoperation und bindet stärker als "
             "Plus und Minus. Ohne Klammer wird nur das Glied direkt davor "
             "geteilt.",
)

#: S22 · Was eine Potenz ist — Lektionen 7.1 und 7.2.
WAS_IST_POTENZ = Animation(
    titel="Was eine Potenz ist",
    schritte=[
        S("Eine Potenz ist eine Abkürzung.",
          ("2", "mark", "b"), ("³", "mark", "e")),
        S("Die kleine Zahl sagt, wie oft die grosse dasteht — hier dreimal.",
          ("2", "", "b"), ("³", "mark", "e")),
        S("Ausgeschrieben heisst das 2 · 2 · 2.",
          ("2 · 2 · 2", "neu", "b")),
        S("Jetzt einfach ausrechnen: 2 · 2 = 4, mal 2 = 8.",
          ("8", "neu", "b")),
        S("6 wäre falsch — das käme vom Malnehmen der beiden Zahlen.",
          ("2 · 3 = 6", "weg", "falsch")),
    ],
    merksatz="Eine Potenz ist eine Abkürzung für ein Produkt gleicher "
             "Faktoren. Der Exponent sagt, wie oft die Basis vorkommt — er "
             "wird nicht mit ihr multipliziert.",
)

#: S23 · Klammer vor Potenz vor Punkt vor Strich — Lektionen 7.3 und 7.4.
#: Der Unterschied zwischen −7² und (−7)² ist der Kern von 7.4.
POTENZ_VORZEICHEN = Animation(
    titel="Minus vor der Potenz",
    schritte=[
        S("Hier steht ein Minus vor einer Potenz.",
          (MINUS, "mark", "op"), ("7", "", "b"), ("²", "", "e")),
        S("Ohne Klammer gehört das Minus NICHT zur Basis.",
          (MINUS, "mark", "op"), ("7", "mark", "b"), ("²", "", "e")),
        S("Zuerst die Potenz: 7² ist 49.",
          (MINUS, "", "op"), ("49", "neu", "b")),
        S("Erst dann kommt das Minus dazu.",
          (MINUS + "49", "neu", "op")),
        S("Mit Klammer wäre es anders: dort gehört das Minus zur Basis.",
          ("(" + MINUS + "7)² = +49", "weg", "falsch")),
    ],
    merksatz="Klammer vor Potenz vor Punkt vor Strich. Ein Minus ohne "
             "Klammer gehört nicht zur Basis: −7² ist −49, aber (−7)² "
             "ist +49.",
)

#: S25 · Potenz eines Produkts — Lektionen 7.9 und 7.10, Vorstufe zu 3e.
PRODUKT_POTENZ = Animation(
    titel="Potenz eines Produkts",
    schritte=[
        S("In der Klammer stehen zwei Faktoren: die 5 und das a.",
          ("(", "", "k1"), ("5", "mark", "z"), ("a", "mark", "v"),
          (")", "", "k2"), ("²", "", "e")),
        S("Die Hochzahl gilt für BEIDE — für die Zahl und für den Buchstaben.",
          ("5² · a²", "neu", "z")),
        S("5² ist 25, a² bleibt a².",
          ("25a²", "neu", "z")),
        S("Rückwärts geht es genauso: aus 25a² wird wieder (5a)².",
          ("25a² = (5a)²", "mark", "z")),
        S("Das braucht man beim Wurzelziehen: √(25a²) ist 5a.",
          ("√(25a²) = 5a", "neu", "z")),
    ],
    merksatz="Eine Potenz eines Produkts gilt für jeden Faktor darin: (2ab)² "
             "ist 4a²b². Rückwärts heisst das: bei der Zahl die Wurzel "
             "ziehen, bei jeder Variablen die Hochzahl halbieren.",
)

#: S24 · Potenzgesetze — Lektionen 7.5 bis 7.8.
POTENZEN = Animation(
    titel="Potenzen multiplizieren",
    schritte=[
        S("Beide Potenzen haben dieselbe Basis: x.",
          ("x²", "mark"), (" · ", ""), ("x³", "mark")),
        S("Ausgeschrieben heisst das: zwei x und drei x.",
          ("x · x", "neu"), (" · ", ""), ("x · x · x", "neu")),
        S("Zusammen sind das fünf x nebeneinander.",
          ("x · x · x · x · x", "mark")),
        S("Fünf gleiche Faktoren schreibt man als Hochzahl 5.",
          ("x⁵", "neu")),
        S("Kurz gesagt: die Hochzahlen werden addiert. 2 + 3 = 5.",
          ("x² · x³ = x⁵", "neu")),
    ],
    merksatz="Beim Multiplizieren werden die Hochzahlen addiert, beim "
             "Dividieren subtrahiert. Beim Addieren bleibt die Hochzahl gleich.",
)

#: S4 · Faktorisieren
FAKTORISIEREN = Animation(
    titel="Ausklammern",
    schritte=[
        S("Schau, was in beiden Gliedern steckt.",
          ("12a² ", ""), ("+ ", ""), ("8a", "")),
        S("In 12 und 8 steckt die 4. In a² und a steckt das a.",
          ("12a²", "mark"), (" + ", ""), ("8a", "mark")),
        S("Der gemeinsame Faktor ist also 4a. Er kommt vor die Klammer.",
          ("4a", "neu"), (" · (", ""), ("… + …", ""), (")", "")),
        S("In der Klammer steht, was übrig bleibt: 12a² : 4a = 3a.",
          ("4a(", ""), ("3a", "neu"), (" + …)", "")),
        S("Und 8a : 4a = 2. Fertig.",
          ("4a(3a + 2)", "neu")),
    ],
    merksatz="Ausklammern ist das Umgekehrte des Ausmultiplizierens: der "
             "grösste Faktor, der in JEDEM Glied steckt, kommt vor die Klammer.",
)

#: S26 · Wurzeln verstehen
WURZEL = Animation(
    titel="Was eine Wurzel ist",
    schritte=[
        S("Die Wurzel stellt eine Frage.",
          ("√49", "mark")),
        S("Sie fragt: welche Zahl ergibt mal sich selbst 49?",
          ("? · ? = 49", "neu")),
        S("6 · 6 ist 36 — zu klein.",
          ("6 · 6 = 36", "weg")),
        S("7 · 7 ist 49 — das passt.",
          ("7 · 7 = 49", "neu")),
        S("Also ist √49 gleich 7.",
          ("√49 = 7", "neu")),
    ],
    merksatz="Die Quadratwurzel aus a ist die nicht negative Zahl, die mit "
             "sich selbst multipliziert a ergibt.",
)

#: S27 · Wurzel aus einer Summe — der Wurzelstrich als Klammer
WURZEL_SUMME = Animation(
    titel="Wurzel aus einer Summe",
    schritte=[
        S("Unter dem Wurzelstrich steht eine Summe.",
          ("√(", ""), ("4 + 4 + 1", "mark"), (")", "")),
        S("Der Wurzelstrich wirkt wie eine Klammer: alles darunter gehört zusammen.",
          ("√(4 + 4 + 1)", "mark")),
        S("Also zuerst zusammenzählen: 4 + 4 + 1 = 9.",
          ("√", ""), ("9", "neu")),
        S("Erst jetzt die Wurzel ziehen.",
          ("3", "neu")),
        S("Der falsche Weg wäre √4 + √4 + √1 = 5. Das ist etwas anderes.",
          ("√4 + √4 + √1 = 5", "weg")),
    ],
    merksatz="Der Wurzelstrich wirkt wie eine Klammer. √(a + b) ist nicht "
             "√a + √b — erst den Radikanden ausrechnen, dann die Wurzel ziehen.",
)

#: S28 · Wurzelgesetze
WURZELGESETZE = Animation(
    titel="Wurzeln zusammenfassen",
    schritte=[
        S("Zwei Wurzeln, verbunden mit geteilt.",
          ("√700", "mark"), (" : ", ""), ("√7", "mark")),
        S("Bei mal und geteilt darfst du beide unter einen Strich schreiben.",
          ("√(700 : 7)", "neu")),
        S("Jetzt den Radikanden ausrechnen: 700 : 7 = 100.",
          ("√", ""), ("100", "neu")),
        S("Und die Wurzel ziehen.",
          ("10", "neu")),
        S("Bei plus und minus geht das nicht: √2 + √2 bleibt 2√2.",
          ("√2 + √2 = 2√2", "weg")),
    ],
    merksatz="√a · √b = √(a · b) und √a : √b = √(a : b). Für Summen und "
             "Differenzen gibt es kein entsprechendes Gesetz.",
)

#: S29 · Wurzel mit Variable
WURZEL_VARIABLE = Animation(
    titel="Wurzel aus Zahl mal Variable",
    schritte=[
        S("Unter der Wurzel steht ein Produkt.",
          ("√(", "", "w"), ("25", "mark", "z"), ("a²", "mark", "v"),
          (")", "", "w2")),
        S("Ein Produkt darfst du in einzelne Wurzeln zerlegen.",
          ("√25", "neu", "z"), ("·", "", "mal"), ("√(a²)", "neu", "v")),
        S("Bei der Zahl wird radiziert: √25 = 5.",
          ("5", "neu", "z"), ("·", "", "mal"), ("√(a²)", "", "v")),
        S("Bei der Variablen wird die Hochzahl halbiert: aus ² wird ¹.",
          ("5", "", "z"), ("·", "", "mal"), ("a", "neu", "v")),
        S("Fertig. Probe: (5a)² ist wieder 25a².",
          ("5", "", "z"), ("a", "", "v")),
    ],
    merksatz="√(a · b) = √a · √b. Deshalb wird bei √(25a²) die Zahl radiziert "
             "und die Hochzahl der Variablen halbiert.",
)


#: S15 · Sorten erkennen
SORTEN = Animation(
    titel="Verschiedene Sorten erkennen",
    schritte=[
        S("Schau zuerst, welche Buchstaben vorkommen.",
          ("5a + 3b + 2a", "")),
        S("Es gibt zwei Sorten: a und b. Sie werden getrennt behandelt.",
          ("5a", "mark"), (" + 3b + ", ""), ("2a", "mark")),
        S("Die a-Glieder zusammenzählen: 5 + 2 = 7.",
          ("7a", "neu"), (" + 3b", "")),
        S("Das b-Glied steht allein und bleibt, wie es ist.",
          ("7a + ", ""), ("3b", "mark")),
        S("Fertig. 7a + 3b ist kürzer — aber nicht ein einziges Glied.",
          ("7a + 3b", "neu")),
    ],
    merksatz="Zwei Glieder sind nur dann gleichartig, wenn sie genau "
             "dieselbe Variable haben. Verschiedene Sorten bleiben "
             "nebeneinander stehen.",
)

#: S17 · Produkte als Sorten
PRODUKTE = Animation(
    titel="Produkte vergleichen",
    schritte=[
        S("Hier stehen Produkte statt einzelner Buchstaben.",
          ("2ab + 3ba", "")),
        S("ab und ba sehen verschieden aus — sind aber dasselbe.",
          ("2", ""), ("ab", "mark"), (" + 3", ""), ("ba", "mark")),
        S("Bei mal spielt die Reihenfolge keine Rolle. Also beide als ab schreiben.",
          ("2ab + 3", ""), ("ab", "neu")),
        S("Jetzt zusammenzählen: 2 + 3 = 5.",
          ("5ab", "neu")),
        S("Aufgepasst: a²b und ab² sind NICHT dasselbe — dort zählen die Hochzahlen.",
          ("a²b ≠ ab²", "weg")),
    ],
    merksatz="Zwei Produkte sind gleichartig, wenn sie dieselben Variablen "
             "mit denselben Hochzahlen haben. Die Reihenfolge der Faktoren "
             "spielt keine Rolle.",
)


#: S12 · Zahlen einsetzen
EINSETZEN = Animation(
    titel="Zahlen in Terme einsetzen",
    schritte=[
        S("Die Buchstaben sind Platzhalter. Der Wert steht daneben.",
          ("a", "mark", "a"), ("−", "", "op"), ("b", "mark", "b")),
        S("Setze jeden Wert in einer eigenen Klammer ein.",
          ("(−26)", "neu", "a"), ("−", "", "op"), ("(−15)", "neu", "b")),
        S("Die Klammern sind wichtig: minus minus ergibt plus.",
          ("−26", "", "a"), ("+", "neu", "op"), ("15", "neu", "b")),
        S("Jetzt ausrechnen.", ("−11", "neu", "a")),
        S("Ohne Klammern hätte man −26 − −15 geschrieben und sich vertan.",
          ("−26 − −15", "weg", "warn")),
    ],
    merksatz="Eine Variable ist ein Platzhalter für eine Zahl. Setze den Wert "
             "immer in einer Klammer ein, dann bleiben die Vorzeichen erhalten.",
)

#: S13 · Variablen verknuepfen — plus zaehlt, mal potenziert
VARIABLEN = Animation(
    titel="Plus zählt, mal potenziert",
    schritte=[
        S("Zwei gleiche Variablen, verbunden mit plus.",
          ("a", "", "v1"), ("+", "mark", "op"), ("a", "", "v2")),
        S("Beim Addieren wird gezählt: zwei Stück a.",
          ("2a", "neu", "v1")),
        S("Jetzt dieselben zwei, aber verbunden mit mal.",
          ("a", "", "v1"), ("·", "mark", "op"), ("a", "", "v2")),
        S("Beim Multiplizieren entsteht eine Potenz.",
          ("a²", "neu", "v1")),
        S("2a und a² sind verschieden — das Rechenzeichen entscheidet.",
          ("2a", "", "v1"), ("≠", "mark", "op"), ("a²", "", "v2")),
    ],
    merksatz="Beim Addieren wird gezählt: a + a sind zwei Stück a, also 2a. "
             "Beim Multiplizieren entsteht eine Potenz: a · a ist a².",
)

#: S14 · Zahl und Variable sind zwei Sorten
ZAHL_UND_VARIABLE = Animation(
    titel="Zahl und Variable getrennt halten",
    schritte=[
        S("Hier stehen zwei verschiedene Dinge nebeneinander.",
          ("3a", "mark", "v"), ("+", "", "op"), ("4", "mark", "z")),
        S("3a ist eine Variable mit Zahl davor. Die 4 ist eine reine Zahl.",
          ("3a", "", "v"), ("+", "", "op"), ("4", "", "z")),
        S("Das sind zwei Sorten. Sie lassen sich nicht zusammenzählen.",
          ("3a", "mark", "v"), ("+", "", "op"), ("4", "", "z")),
        S("7a wäre falsch — die 4 hat kein a.",
          ("7a", "weg", "falsch")),
        S("3a + 4 ist bereits die Antwort. Kürzer geht es nicht.",
          ("3a", "neu", "v"), ("+", "", "op"), ("4", "neu", "z")),
    ],
    merksatz="Eine Variable und eine reine Zahl sind verschiedene Sorten. "
             "3a + 4 lässt sich nicht zusammenfassen — das ist bereits die "
             "Antwort.",
)


#: S18 · Variablen multiplizieren
MULTIPLIZIEREN = Animation(
    titel="Variablen multiplizieren",
    schritte=[
        S("Drei Faktoren, alle mit derselben Variablen.",
          ("2a", "", "f1"), ("·", "", "m1"), ("2a", "", "f2"),
          ("·", "", "m2"), ("2a", "", "f3")),
        S("Zuerst die Zahlen: 2 · 2 · 2 = 8. Multiplizieren, nicht addieren.",
          ("8", "neu", "f1"), ("·", "weg", "m1"), ("a · a · a", "", "f2")),
        S("Dann die Variable: sie kommt dreimal vor.",
          ("8", "", "f1"), ("a · a · a", "mark", "f2")),
        S("Dreimal derselbe Faktor heisst Hochzahl 3.",
          ("8", "", "f1"), ("a³", "neu", "f2")),
        S("6a³ wäre falsch — das käme vom Addieren der Zahlen.",
          ("6a³", "weg", "falsch")),
    ],
    merksatz="Beim Multiplizieren werden die Zahlen malgenommen und für jede "
             "Variable gezählt, wie oft sie vorkommt.",
)

#: S19 · Vorzeichen zaehlen
VORZEICHEN = Animation(
    titel="Minuszeichen zählen",
    schritte=[
        S("Vier Faktoren. Zähl zuerst die Minuszeichen.",
          ("(−2a)", "mark", "f1"), ("(−3b)", "mark", "f2"),
          ("(−4c)", "mark", "f3"), ("(−5d)", "mark", "f4")),
        S("Das sind vier Stück — eine gerade Anzahl.",
          ("4 Minuszeichen", "neu", "zaehl")),
        S("Gerade heisst: das Ergebnis wird positiv.",
          ("Ergebnis positiv", "neu", "zaehl")),
        S("Jetzt die Zahlen: 2 · 3 · 4 · 5 = 120.",
          ("120", "neu", "zahl"), ("abcd", "", "vars")),
        S("Bei drei Minuszeichen wäre dasselbe Ergebnis negativ.",
          ("120abcd", "neu", "zahl")),
    ],
    merksatz="Eine gerade Anzahl Minuszeichen ergibt plus, eine ungerade "
             "minus. Zählen, nicht raten.",
)


#: Kapitelnummer in der App  ->  Animation.
#: Was hier fehlt, faellt still auf den alten Textkasten zurueck — die
#: Lektion laeuft also auch ohne Animation.
FUER_KAPITEL: dict[str, Animation] = {
    "3.1": EINSETZEN,
    "3.4": VARIABLEN,
    "3.10": ZAHL_UND_VARIABLE,
    "5.1": MULTIPLIZIEREN,
    "5.5": VORZEICHEN,
    "4.1": SORTEN,
    "4.2": GLEICHARTIGE,
    "4.9": PRODUKTE,
    "6.1": PUNKT_ZUERST,
    "6.5": PUNKT_VOR_STRICH,
    "7.1": WAS_IST_POTENZ,
    "7.3": POTENZ_VORZEICHEN,
    "7.5": POTENZEN,
    "7.9": PRODUKT_POTENZ,
    "9.1": DIVIDIEREN,
    "9.4": SUMME_TEILEN,
    "9.6": DIVISION_IM_TERM,
    "8.1": WURZEL,
    "8.3": WURZEL_SUMME,
    "8.4": WURZELGESETZE,
    "8.9": WURZEL_VARIABLE,
    "10.1": MINUS_KLAMMER,
    "12.1": FAKTORISIEREN,
}


def fuer(kapitel: str) -> dict | None:
    a = FUER_KAPITEL.get(kapitel)
    return a.als_dict() if a else None
