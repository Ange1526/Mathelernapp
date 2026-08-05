"""Korrektur mit SymPy — Parser, Prüffunktion, Aufgabenkatalog.

Alles, was die Flask-App braucht:

    from korrektur import pruefe, Status, AUFGABEN

    ergebnis = pruefe("-2/7", AUFGABEN["1a"])
    ergebnis.status              # Status.RICHTIG
    ergebnis.text                # Text für die Schülerin
    ergebnis.fehlerschluessel    # None | Katalogschlüssel | "unbekannt"
"""

from .bruecke import Auswertung, aufgabe_aus_generator, auswerten
from .eingabe_parser import ParseError, parse_answer, parse_term, symbole
from .katalog_erhebung import AUFGABEN, TEXTE
from .pruefung import (Aufgabe, Ergebnis, Fehler, Loesung, Status, Zielform,
                       pruefe)

__all__ = [
    "pruefe", "Status", "Zielform", "Aufgabe", "Fehler", "Loesung", "Ergebnis",
    "AUFGABEN", "TEXTE",
    "auswerten", "aufgabe_aus_generator", "Auswertung",
    "parse_answer", "parse_term", "symbole", "ParseError",
]
