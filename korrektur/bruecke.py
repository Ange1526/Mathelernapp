"""Brücke zwischen der bestehenden Lernapp und der SymPy-Korrektur.

Die App erzeugt Aufgaben mit `generate_math_task()` und bekommt dort einen
Float als Lösung zurück. Diese Datei macht daraus ein `Aufgabe`-Objekt und
übersetzt das dreiwertige Prüfergebnis in die Zähler, die die Adaptivität
schon verwendet.
"""

from __future__ import annotations

from dataclasses import dataclass

from sympy import nsimplify

from .pruefung import Aufgabe, Loesung, Status, Zielform, pruefe


def aufgabe_aus_generator(loesung, variablen=None, zielform=Zielform.BELIEBIG,
                          fehlerkatalog=None, dezimal_stellen=2) -> Aufgabe:
    """Float oder int aus dem Generator -> Aufgabe für die Korrektur.

    nsimplify statt Rational(float): 0.1 als Float ist nicht exakt 1/10, und
    genau daran scheitert sonst der Vergleich.
    """
    return Aufgabe(
        loesung=Loesung.zahl(nsimplify(loesung, rational=True)),
        variablen=set(variablen or set()),
        zielform=zielform,
        fehlerkatalog=list(fehlerkatalog or []),
        dezimal_stellen=dezimal_stellen,
    )


@dataclass
class Auswertung:
    """Was die Route wissen muss, ohne selbst Status auseinandernehmen zu müssen."""
    status: Status
    text: str
    fehlerschluessel: str | None

    #: Als gelöste Aufgabe zählen (total_cnt hoch, neue Aufgabe)?
    zaehlt_als_geloest: bool
    #: Als richtig zählen (correct_cnt, XP)?
    zaehlt_als_richtig: bool
    #: Fehler in Folge hochzählen (löst den Theorie-Hinweis aus)?
    zaehlt_als_fehler: bool
    #: Für den Flash-Kanal: "success" | "error" | "warning"
    kanal: str


def auswerten(eingabe: str, aufgabe: Aufgabe) -> Auswertung:
    """pruefe() plus die Entscheidung, was der Status für die Zähler bedeutet.

    Die Zuordnung ist die eigentliche Aussage:

    RICHTIG        zählt voll.
    UNFERTIG       ist kein Wissensfehler — die Rechnung stimmt, nur die Form
                   ist noch nicht fertig. Weder als gelöst noch als Fehler
                   zählen, Aufgabe bleibt offen, Hinweistext anzeigen.
    FALSCH         zählt als gelöste Aufgabe und als Fehler, wie bisher.
    EINGABEFEHLER  Tippfehler, kein Rechenfehler. Gar nicht zählen, sonst
                   verfälscht er die Quote und löst Abstiege aus.
    ZEITLIMIT      technisches Problem, ebenfalls nicht zählen.
    """
    e = pruefe(eingabe, aufgabe)

    if e.status is Status.RICHTIG:
        geloest, richtig, fehler, kanal = True, True, False, "success"
    elif e.status is Status.FALSCH:
        geloest, richtig, fehler, kanal = True, False, True, "error"
    elif e.status is Status.UNFERTIG:
        geloest, richtig, fehler, kanal = False, False, False, "warning"
    else:                                   # EINGABEFEHLER, ZEITLIMIT
        geloest, richtig, fehler, kanal = False, False, False, "error"

    return Auswertung(status=e.status, text=e.text,
                      fehlerschluessel=e.fehlerschluessel,
                      zaehlt_als_geloest=geloest, zaehlt_als_richtig=richtig,
                      zaehlt_als_fehler=fehler, kanal=kanal)
