# -*- coding: utf-8 -*-
"""
Theorie für Kapitel 2 — mit einem Balken zum Anschauen.

WARUM DIESE DATEI
-----------------
Kapitel 2 hatte gar keine Theorie: `theorie.fuer("2.1")` gab None zurück,
und auf der Lektionsseite stand nur die Kernidee als Satz. Für Brüche ist
das die schlechteste Lösung — ein Bruch IST ein Bild, und wer ihn nicht
sieht, lernt Regeln auswendig, die er nicht prüfen kann.

Alles hier baut auf einem Balken auf, der in Teile zerlegt ist:

    ███░░░░░       3/8      drei von acht Teilen sind gefüllt

Gefüllte Kästchen sind der Zähler, alle Kästchen zusammen der Nenner. Am
selben Bild lässt sich zeigen, warum Kürzen den Wert nicht ändert (die
gefüllte Fläche bleibt gleich, nur die Einteilung wird gröber) und warum
man beim Addieren erst gleichnamig machen muss (zwei verschiedene
Einteilungen lassen sich nicht zusammenzählen).

TECHNIK: Der Balken ist EIN mehrzeiliger Text, so wie der Lift in Kapitel
1. Keine Flexbox, keine Höhenrechnerei — der Browser setzt die Umbrüche
selbst um. Dieselbe Lehre wie dort: was einfach gebaut ist, erscheint auch.

SPRACHE: kurze Sätze, kein Fachwort ohne Erklärung.
"""
from __future__ import annotations

from .theorie import S, Animation


def balken(zaehler: int, nenner: int, beschriftung: str = "") -> str:
    """Ein Bruch als Balken: gefüllte und leere Kästchen.

    ███░░░░░  entspricht 3/8. Die Kästchen sind Blockzeichen, keine Grafik —
    damit funktioniert es überall gleich, auch ohne Bilddateien.
    """
    voll = "█" * max(0, min(zaehler, nenner))
    leer = "░" * max(0, nenner - zaehler)
    text = f"{voll}{leer}"
    return f"{text}   {beschriftung}" if beschriftung else text


def zwei(oben: str, unten: str) -> str:
    """Zwei Balken untereinander — zum Vergleichen."""
    return f"{oben}\n{unten}"


# ══════════════════════════════════════════════════════════════════════════
#  2.1 · Was ein Bruch ist
# ══════════════════════════════════════════════════════════════════════════
BRUCH_VERSTEHEN = Animation(
    titel="Was ein Bruch bedeutet",
    schritte=[
        S("Ein Balken wird in gleich grosse Teile zerlegt. Hier in acht.",
          (balken(0, 8, "acht Teile"), "bild", "b")),
        S("Die untere Zahl — der Nenner — sagt, in wie viele Teile.",
          (balken(0, 8, "Nenner: 8"), "bild", "b")),
        S("Die obere Zahl — der Zähler — sagt, wie viele davon gemeint sind.",
          (balken(3, 8, "Zähler: 3"), "bild", "b")),
        S("Drei von acht Teilen: das ist 3/8.",
          (balken(3, 8, "3/8"), "bild", "b")),
        S("Sind alle Teile gemeint, ist der Bruch eine ganze Zahl: "
          "8/8 = 1.",
          (balken(8, 8, "8/8 = 1"), "bild", "b")),
    ],
    merksatz=("Der Nenner sagt, in wie viele Teile geteilt wurde. Der "
              "Zähler sagt, wie viele davon gemeint sind."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.2 · Kürzen und Erweitern
# ══════════════════════════════════════════════════════════════════════════
KUERZEN = Animation(
    titel="Kürzen ändert den Wert nicht",
    schritte=[
        S("Hier sind 6 von 8 Teilen gefüllt: 6/8.",
          (balken(6, 8, "6/8"), "bild", "b")),
        S("Jetzt fassen wir immer zwei Teile zu einem zusammen.",
          (zwei(balken(6, 8, "6/8"), balken(3, 4, "3/4")), "bild", "b")),
        S("Die gefüllte Fläche bleibt genau gleich gross — nur die "
          "Einteilung ist gröber.",
          (zwei(balken(6, 8, "6/8"), balken(3, 4, "gleich viel!")),
           "bild", "b")),
        S("Aus 6/8 wird 3/4. Zähler und Nenner wurden beide durch 2 geteilt.",
          (balken(3, 4, "3/4"), "bild", "b")),
        S("Umgekehrt geht es auch: mal 2 auf beiden Seiten, dann sind es "
          "wieder 6/8. Das heisst erweitern.",
          (zwei(balken(3, 4, "3/4"), balken(6, 8, "6/8")), "bild", "b")),
    ],
    merksatz=("Kürzen heisst: Zähler UND Nenner durch dieselbe Zahl teilen. "
              "Die Fläche bleibt gleich, der Wert also auch."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.3 – 2.4 · Gleicher Nenner
# ══════════════════════════════════════════════════════════════════════════
GLEICHER_NENNER = Animation(
    titel="Gleicher Nenner: nur die Zähler zählen",
    schritte=[
        S("Zwei Brüche mit derselben Einteilung: 2/7 und 3/7.",
          (zwei(balken(2, 7, "2/7"), balken(3, 7, "3/7")), "bild", "b")),
        S("Die Teile sind gleich gross. Also lassen sie sich einfach "
          "zusammenschieben.",
          (zwei(balken(2, 7, "2/7"), balken(3, 7, "+ 3/7")), "bild", "b")),
        S("Zwei Teile und drei Teile sind fünf Teile.",
          (balken(5, 7, "5/7"), "bild", "b")),
        S("Der Nenner bleibt stehen — die Teile sind ja nicht kleiner "
          "geworden.",
          (balken(5, 7, "Nenner bleibt 7"), "bild", "b")),
        S("Beim Abziehen genauso: 5/7 − 3/7 sind zwei Teile weniger.",
          (balken(2, 7, "2/7"), "bild", "b")),
    ],
    merksatz=("Bei gleichem Nenner werden nur die Zähler verrechnet. Der "
              "Nenner bleibt stehen."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.5 – 2.6 · Hauptnenner
# ══════════════════════════════════════════════════════════════════════════
HAUPTNENNER = Animation(
    titel="Verschiedene Nenner gleichnamig machen",
    schritte=[
        S("1/2 und 1/3 — die Teile sind verschieden gross.",
          (zwei(balken(1, 2, "1/2"), balken(1, 3, "1/3")), "bild", "b")),
        S("So lassen sie sich nicht zusammenzählen. Es fehlt eine "
          "gemeinsame Einteilung.",
          (zwei(balken(1, 2, "1/2"), balken(1, 3, "passt nicht")),
           "bild", "b")),
        S("Beide Balken lassen sich in Sechstel zerlegen: 6 ist der "
          "Hauptnenner.",
          (zwei(balken(3, 6, "1/2 = 3/6"), balken(2, 6, "1/3 = 2/6")),
           "bild", "b")),
        S("Jetzt sind die Teile gleich gross — und man kann rechnen.",
          (zwei(balken(3, 6, "3/6"), balken(2, 6, "+ 2/6")), "bild", "b")),
        S("Drei Teile und zwei Teile sind fünf: 5/6.",
          (balken(5, 6, "5/6"), "bild", "b")),
    ],
    merksatz=("Verschiedene Nenner müssen erst gleichnamig werden. Der "
              "Hauptnenner ist die kleinste Zahl, in die beide Einteilungen "
              "passen."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.7 – 2.8 · Ganze Zahlen
# ══════════════════════════════════════════════════════════════════════════
GANZE_ZAHL = Animation(
    titel="Eine ganze Zahl ist auch ein Bruch",
    schritte=[
        S("Ein voller Balken ist eins. In Vierteln: 4/4.",
          (balken(4, 4, "1 = 4/4"), "bild", "b")),
        S("Zwei volle Balken sind zwei — also 8/4.",
          (zwei(balken(4, 4, "4/4"), balken(4, 4, "4/4 → 8/4")), "bild", "b")),
        S("Um 1 + 3/4 zu rechnen, schreiben wir die Eins als 4/4.",
          (zwei(balken(4, 4, "1 = 4/4"), balken(3, 4, "+ 3/4")), "bild", "b")),
        S("Jetzt haben beide denselben Nenner: 4/4 + 3/4 = 7/4.",
          (balken(4, 4, "7/4 — mehr als ein Balken"), "bild", "b")),
        S("Merke: eine ganze Zahl bekommt den Nenner des anderen Bruchs.",
          (balken(4, 4, "n = n·Nenner / Nenner"), "bild", "b")),
    ],
    merksatz=("Eine ganze Zahl ist ein Bruch mit dem Nenner eins: 2 = 2/1. "
              "Zum Rechnen schreibt man sie mit dem Nenner des anderen "
              "Bruchs."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.9 · 2.11 · Multiplikation
# ══════════════════════════════════════════════════════════════════════════
MAL = Animation(
    titel="Malnehmen heisst «davon»",
    schritte=[
        S("1/2 · 3/4 heisst: die Hälfte VON drei Vierteln.",
          (balken(3, 4, "3/4"), "bild", "b")),
        S("Wir halbieren jedes Viertel — aus vier Teilen werden acht.",
          (zwei(balken(3, 4, "3/4"), balken(6, 8, "= 6/8")), "bild", "b")),
        S("Von diesen sechs Achteln nehmen wir die Hälfte: drei.",
          (balken(3, 8, "3/8"), "bild", "b")),
        S("Gerechnet: Zähler mal Zähler, Nenner mal Nenner. "
          "1·3 = 3 und 2·4 = 8.",
          (balken(3, 8, "3/8"), "bild", "b")),
        S("Anders als beim Addieren bleibt der Nenner NICHT stehen.",
          (balken(3, 8, "der Nenner ändert sich"), "bild", "b")),
    ],
    merksatz=("Zähler mal Zähler, Nenner mal Nenner. Malnehmen mit einem "
              "Bruch macht kleiner, nicht grösser."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.10 · Division
# ══════════════════════════════════════════════════════════════════════════
GETEILT = Animation(
    titel="Teilen heisst «wie oft passt es hinein»",
    schritte=[
        S("3/4 : 1/8 fragt: wie oft passt ein Achtel in drei Viertel?",
          (zwei(balken(6, 8, "3/4 = 6/8"), balken(1, 8, "1/8")),
           "bild", "b")),
        S("Drei Viertel sind sechs Achtel. Ein Achtel passt also sechsmal "
          "hinein.",
          (balken(6, 8, "sechsmal"), "bild", "b")),
        S("Das Ergebnis ist 6 — grösser als der Anfang!",
          (balken(6, 8, "3/4 : 1/8 = 6"), "bild", "b")),
        S("Gerechnet wird das mit dem Kehrwert: 3/4 · 8/1.",
          (balken(6, 8, "3/4 · 8/1"), "bild", "b")),
        S("Gestürzt wird der ZWEITE Bruch — der hinter dem Doppelpunkt.",
          (balken(6, 8, "nur der zweite"), "bild", "b")),
    ],
    merksatz=("Durch einen Bruch teilen heisst: mit seinem Kehrwert "
              "malnehmen. Gestürzt wird der zweite Bruch."),
)


# ══════════════════════════════════════════════════════════════════════════
#  2.12 – 2.13 · Doppelbrüche
# ══════════════════════════════════════════════════════════════════════════
DOPPELBRUCH = Animation(
    titel="Der grosse Bruchstrich ist ein Doppelpunkt",
    schritte=[
        S("Ein Doppelbruch sieht neu aus: oben ein Bruch, unten ein Bruch.",
          ("(3/4)", "", "o"), (" / ", "mark", "strich"), ("(1/2)", "", "u")),
        S("Der grosse Strich in der Mitte bedeutet nichts anderes als "
          "«geteilt durch».",
          ("3/4", "", "o"), (" : ", "neu", "strich"), ("1/2", "", "u")),
        S("Und Teilen kennen wir: mit dem Kehrwert malnehmen.",
          ("3/4", "", "o"), (" · ", "neu", "strich"), ("2/1", "neu", "u")),
        S("Also 3·2 = 6 oben und 4·1 = 4 unten: 6/4.",
          (balken(6, 8, "6/4"), "bild", "b")),
        S("Und zuletzt kürzen: 6/4 = 3/2.",
          (balken(3, 4, "3/2"), "bild", "b")),
    ],
    merksatz=("Ein Doppelbruch ist nichts Neues: (a/b)/(c/d) heisst "
              "a/b : c/d."),
)


#: Kapitelschluessel -> Animation. Die Schluessel sind die aus
#: `anbindung.KAPITEL` — bei Kapitel 2 ist das die Lektionsnummer selbst.
FUER_KAPITEL_K2 = {
    "2.1": BRUCH_VERSTEHEN,
    "2.2": KUERZEN,
    "2.3": GLEICHER_NENNER,
    "2.4": GLEICHER_NENNER,
    "2.5": HAUPTNENNER,
    "2.6": HAUPTNENNER,
    "2.7": GANZE_ZAHL,
    "2.8": GANZE_ZAHL,
    "2.9": MAL,
    "2.10": GETEILT,
    "2.11": MAL,
    "2.12": DOPPELBRUCH,
    "2.13": DOPPELBRUCH,
}
