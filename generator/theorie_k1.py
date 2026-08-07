# -*- coding: utf-8 -*-
"""
Theorie für Kapitel 1 — mit einer Zahlengeraden zum Mitgehen.

WARUM DIESE DATEI
-----------------
Die Theorie zu Kapitel 1 war ein Textblock. Für einen Erstklässler, der aus
der Primarschule kommt und nicht versteht, warum minus mal minus plus
ergibt, ist ein Textblock die schlechteste aller Erklärungen: er setzt
genau das voraus, was fehlt.

Alles hier ist auf EIN Bild gebaut — die Zahlengerade. Sie wird aus den
vorhandenen Textstücken zusammengesetzt, jedes mit eigenem Schlüssel; die
Animation lässt dann eine Markierung darüber wandern. Es braucht keine
neue Technik, nur eine andere Verwendung der alten.

    −5  −4  −3  −2  −1   0   1   2   3   4   5
                     ▲

Der Lift, den sich Donatella gewünscht hat, ist dasselbe Bild um neunzig
Grad gedreht: oben plus, unten minus, die Null ist das Erdgeschoss. Wo die
Zahlengerade besser passt, steht sie; beim Vorzeichen der Multiplikation
ist es das Umdrehen der Fahrtrichtung.

SPRACHE: kurze Hauptsätze, kein Fachwort ohne Erklärung. Wer das hier
liest, hat den Stoff noch nicht.
"""
from __future__ import annotations

from .theorie import S, Animation


def _gerade(mitte: int = 0, von: int = -5, bis: int = 5,
            marke: int | None = None, zweite: int | None = None):
    """Baut die Zahlengerade als Liste von Textstücken.

    Jede Zahl bekommt ihren eigenen Schlüssel («p3» für +3, «m3» für −3).
    Dadurch bleibt sie über die Schritte hinweg stehen, und nur die
    Markierung wandert — genau das macht daraus eine Animation statt einer
    Folge von Bildern.
    """
    teile = []
    for n in range(von, bis + 1):
        schluessel = f"p{n}" if n >= 0 else f"m{abs(n)}"
        if n == marke:
            stil = "mark"
        elif n == zweite:
            stil = "neu"
        else:
            stil = ""
        text = f"{n}" if n >= 0 else f"−{abs(n)}"
        teile.append((f" {text} ", stil, schluessel))
    return teile


# ══════════════════════════════════════════════════════════════════════════
#  1.1 – 1.2 · Die Zahlengerade und die Gegenzahl
# ══════════════════════════════════════════════════════════════════════════
ZAHLENGERADE = Animation(
    titel="Die Zahlengerade",
    schritte=[
        S("Alle Zahlen liegen auf einer Linie. In der Mitte steht die Null.",
          *_gerade(marke=0)),
        S("Rechts von der Null stehen die positiven Zahlen. Sie werden grösser.",
          *_gerade(marke=3)),
        S("Links von der Null stehen die negativen Zahlen. Sie werden kleiner.",
          *_gerade(marke=-3)),
        S("−3 und 3 sind gleich weit von der Null entfernt. Sie sind "
          "Gegenzahlen.",
          *_gerade(marke=-3, zweite=3)),
        S("Die Gegenzahl findest du, indem du auf die andere Seite der Null "
          "spiegelst.",
          *_gerade(marke=3, zweite=-3)),
    ],
    merksatz=("Rechts liegt das Grössere, links das Kleinere. Die Gegenzahl "
              "liegt gleich weit von der Null entfernt — auf der anderen "
              "Seite."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.3 · Vorzeichen und Operationszeichen
# ══════════════════════════════════════════════════════════════════════════
VORZEICHEN = Animation(
    titel="Vorzeichen und Rechenzeichen",
    schritte=[
        S("Ein Minus kann zweierlei bedeuten. Hier sind beide.",
          ("7", "", "a"), (" − ", "mark", "op"), ("(", "", "k1"),
          ("−", "mark", "vz"), ("4", "", "b"), (")", "", "k2")),
        S("Das erste Minus sagt, WAS gerechnet wird: abziehen.",
          ("7", "", "a"), (" − ", "mark", "op"), ("(", "", "k1"),
          ("−", "", "vz"), ("4", "", "b"), (")", "", "k2")),
        S("Das zweite gehört zur Zahl. Es sagt, WO sie liegt: links von "
          "der Null.",
          ("7", "", "a"), (" − ", "", "op"), ("(", "", "k1"),
          ("−", "mark", "vz"), ("4", "mark", "b"), (")", "", "k2")),
        S("Vier Schritte nach links abziehen heisst: vier Schritte nach "
          "rechts gehen.",
          *_gerade(von=0, bis=12, marke=7)),
        S("Also 7 + 4 = 11.",
          *_gerade(von=0, bis=12, marke=11, zweite=7)),
    ],
    merksatz=("Das Zeichen vor der Klammer sagt, was gerechnet wird. Das "
              "Zeichen an der Zahl sagt, auf welcher Seite der Null sie "
              "liegt. Zwei Minus heben sich auf."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.5 – 1.9 · Addieren und Subtrahieren als Gehen
# ══════════════════════════════════════════════════════════════════════════
GEHEN = Animation(
    titel="Plus und Minus sind Schritte",
    schritte=[
        S("Wir starten bei −3.",
          *_gerade(marke=-3)),
        S("Plus heisst: nach rechts gehen. Plus 5 sind fünf Schritte.",
          *_gerade(marke=-3, zweite=2)),
        S("Wir kommen bei 2 heraus. Also −3 + 5 = 2.",
          *_gerade(marke=2)),
        S("Minus heisst: nach links gehen. Von 2 aus minus 6.",
          *_gerade(marke=2, zweite=-4)),
        S("Wir landen bei −4. Über die Null hinweg zählt sie mit.",
          *_gerade(marke=-4)),
    ],
    merksatz=("Plus geht nach rechts, minus nach links. Die Null ist keine "
              "Wand — man geht über sie hinweg."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.10 – 1.12 · Warum minus mal minus plus ergibt
# ══════════════════════════════════════════════════════════════════════════
MAL_VORZEICHEN = Animation(
    titel="Minus mal Minus",
    schritte=[
        S("3 · 2 heisst: zweimal drei Schritte nach rechts.",
          *_gerade(von=0, bis=8, marke=6)),
        S("(−3) · 2 heisst: zweimal drei Schritte nach LINKS.",
          *_gerade(von=-8, bis=0, marke=-6)),
        S("Ein Minus beim ersten Faktor dreht die Richtung um.",
          ("(−3)", "mark", "a"), (" · ", "", "op"), ("2", "", "b"),
          (" = ", "", "gl"), ("−6", "neu", "e")),
        S("Ein Minus beim zweiten Faktor dreht sie nochmals um.",
          ("(−3)", "", "a"), (" · ", "", "op"), ("(−2)", "mark", "b"),
          (" = ", "", "gl"), ("6", "neu", "e")),
        S("Zweimal umdrehen heisst: wieder nach rechts. Darum plus.",
          *_gerade(von=0, bis=8, marke=6)),
    ],
    merksatz=("Jedes Minus dreht die Richtung um. Ein Minus ergibt Minus, "
              "zwei Minus heben sich auf und ergeben Plus."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.13 – 1.15 · Teilen ist Umkehren
# ══════════════════════════════════════════════════════════════════════════
TEILEN = Animation(
    titel="Teilen ist die Umkehrung",
    schritte=[
        S("Wir wissen: 6 · 7 = 42.",
          ("6", "", "a"), (" · ", "", "op"), ("7", "", "b"),
          (" = ", "", "gl"), ("42", "", "e")),
        S("Dann muss auch gelten: 42 : 7 = 6.",
          ("42", "mark", "e"), (" : ", "neu", "op"), ("7", "", "b"),
          (" = ", "", "gl"), ("6", "mark", "a")),
        S("Frag dich beim Teilen also: mal was ergibt die erste Zahl?",
          ("42", "", "e"), (" : ", "", "op"), ("7", "mark", "b"),
          (" = ", "", "gl"), ("?", "mark", "a")),
        S("Beim Vorzeichen gilt dieselbe Regel wie beim Malnehmen.",
          ("(−42)", "mark", "e"), (" : ", "", "op"), ("7", "", "b"),
          (" = ", "", "gl"), ("−6", "neu", "a")),
        S("Zwei Minus heben sich auch hier auf.",
          ("(−42)", "", "e"), (" : ", "", "op"), ("(−7)", "mark", "b"),
          (" = ", "", "gl"), ("6", "neu", "a")),
    ],
    merksatz=("Teilen ist Malnehmen rückwärts. Die Vorzeichenregel ist "
              "dieselbe: gleich ergibt Plus, verschieden ergibt Minus."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.16 – 1.19 · Punkt vor Strich
# ══════════════════════════════════════════════════════════════════════════
REIHENFOLGE = Animation(
    titel="Punkt vor Strich",
    schritte=[
        S("Hier stehen zwei Rechenarten in einer Zeile.",
          ("3", "", "a"), (" + ", "mark", "op1"), ("4", "", "b"),
          (" · ", "mark", "op2"), ("5", "", "c")),
        S("Von links nach rechts wäre falsch: 3 + 4 sind 7, mal 5 sind 35.",
          ("7", "weg", "a"), (" · ", "", "op2"), ("5", "", "c"),
          (" = ", "", "gl"), ("35", "weg", "f")),
        S("Der Malpunkt bindet stärker. Er kommt zuerst — egal wo er steht.",
          ("3", "", "a"), (" + ", "", "op1"), ("4", "mark", "b"),
          (" · ", "mark", "op2"), ("5", "mark", "c")),
        S("Also erst 4 · 5 = 20.",
          ("3", "", "a"), (" + ", "", "op1"), ("20", "neu", "b")),
        S("Und dann 3 + 20 = 23.",
          ("23", "neu", "a")),
    ],
    merksatz=("Punkt vor Strich: Mal und Geteilt zuerst, egal wo sie "
              "stehen. Stehen nur gleichrangige Zeichen da, wird von links "
              "nach rechts gerechnet."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.8 · Zwei negative Zahlen addieren  —  der Lift
# ══════════════════════════════════════════════════════════════════════════
# Hier passt der Lift besser als die Zahlengerade: zwei Minuszahlen zu
# addieren heisst zweimal hintereinander nach UNTEN fahren, und «unten»
# versteht jeder sofort. Auf der waagrechten Geraden muss man sich erst
# merken, dass links das Kleinere ist.
def _lift(marke: int) -> str:
    """Der Lift als EIN mehrzeiliger Text.

    Die erste Fassung baute ihn aus einzelnen Textstücken mit Umbrüchen
    dazwischen. Im HTML stand alles korrekt, zu sehen war trotzdem nichts:
    die Bühne stapelt ihre Schritte absolut übereinander, und absolut
    positionierte Inhalte lassen ihren Rahmen nicht mitwachsen. Der Lift
    ragte unsichtbar oben heraus.

    Jetzt ist er ein einziger Text mit Zeilenumbrüchen. Der Browser setzt
    ihn mit `white-space: pre-line` selbst um — ohne Flexbox, ohne
    Höhenrechnerei, ohne etwas, das schiefgehen kann.
    """
    zeilen = []
    for etage in range(2, -6, -1):
        beschriftung = f"{etage}" if etage >= 0 else f"−{abs(etage)}"
        pfeil = "▶ " if etage == marke else "   "
        raum = "  Erdgeschoss" if etage == 0 else ""
        zeilen.append(f"{pfeil}{beschriftung:>3}{raum}")
    return "\n".join(zeilen)


LIFT = Animation(
    titel="Der Lift: was negative Zahlen sind",
    schritte=[
        S("Stell dir einen Lift vor. Die Null ist das Erdgeschoss.",
          (_lift(0), "lift", "l")),
        S("Über der Null liegen die Stockwerke: 1, 2, 3 …",
          (_lift(2), "lift", "l")),
        S("Unter der Null liegt der Keller. Das sind die negativen Zahlen.",
          (_lift(-2), "lift", "l")),
        S("Je weiter unten, desto kleiner die Zahl. −5 ist kleiner als −2.",
          (_lift(-5), "lift", "l")),
        S("Und «plus» heisst nach oben fahren, «minus» nach unten.",
          (_lift(-1), "lift", "l")),
    ],
    merksatz=("Negative Zahlen liegen unter der Null — wie die Stockwerke "
              "im Keller. Je weiter unten, desto kleiner die Zahl."),
)


# ══════════════════════════════════════════════════════════════════════════
#  1.9 · Minus vor einer Minuszahl
# ══════════════════════════════════════════════════════════════════════════
# Der schwerste Schritt in Kapitel 1. Darum ein eigenes Bild: das Minus vor
# der Klammer DREHT die Fahrtrichtung um.
MINUS_MINUS = Animation(
    titel="Minus vor einer Minuszahl",
    schritte=[
        S("Wir starten bei 5 und ziehen 3 ab. Das geht nach links.",
          *_gerade(marke=5)),
        S("5 − 3 = 2. Minus heisst: nach links gehen.",
          *_gerade(marke=2, zweite=5)),
        S("Jetzt steht da: 5 − (−3). Das Minus vor der Klammer dreht die "
          "Richtung um.",
          ("5", "", "a"), (" − ", "mark", "op"), ("(−3)", "mark", "b")),
        S("Zweimal umgedreht ist geradeaus: aus − (−3) wird + 3.",
          ("5", "", "a"), (" + ", "neu", "op"), ("3", "neu", "b")),
        S("Also 5 − (−3) = 8. Wir gehen nach RECHTS, nicht nach links.",
          *_gerade(von=-2, bis=9, marke=8, zweite=5)),
    ],
    merksatz=("Ein Minus vor einer Klammer dreht das Vorzeichen darin um. "
              "5 − (−3) heisst 5 + 3."),
)


#: Lektion -> Animation. Der Schlüssel ist der KAPITEL-Schlüssel aus
#: `anbindung.KAPITEL`, nicht die Lektionsnummer.
FUER_KAPITEL_K1 = {
    # Der Lift steht am ANFANG: dort wird erklaert, WAS negative Zahlen
    # sind. Die Zahlengerade folgt in 1.2, wo es um ihre Lage geht, und
    # das Rechnen mit ihnen bekommt in 1.7 sein eigenes Bild.
    "1.1": LIFT,
    "1.2": ZAHLENGERADE,
    "1.3": VORZEICHEN,
    "1.4": REIHENFOLGE,
    "1.5": GEHEN,
    "1.6": GEHEN,
    # 1.7 bis 1.9 liegen im selben Kapitel «1.7» — ein Schluessel, eine
    # Animation. Genommen wird die zum schwersten Schritt: das Minus vor
    # der Klammer.
    "1.7": MINUS_MINUS,
    "1.10": MAL_VORZEICHEN,
    "1.11": MAL_VORZEICHEN,
    "1.12": MAL_VORZEICHEN,
    "1.13": TEILEN,
    "1.14": TEILEN,
    "1.15": TEILEN,
    "1.16": REIHENFOLGE,
    "1.17": REIHENFOLGE,
    "1.18": REIHENFOLGE,
    "1.19": REIHENFOLGE,
    "1.20": ZAHLENGERADE,
}
