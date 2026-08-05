"""
Parser für Schülereingaben -> SymPy-Ausdruck.

Sicherheitsprinzip: kein eval(), und parse_expr() wird NIE direkt auf den
Rohstring losgelassen. Vorher laufen drei Filter:
  1. Normalisierung  (Unicode, Komma, ^, ², :, ·)
  2. Zeichen-Whitelist
  3. Token-Whitelist (Namen und Operatoren)
Erst danach parse_expr mit eingeschränktem global_dict.

Warum Filter 3 nötig ist: parse_expr allein ist KEINE Sandbox.
    parse_expr("(1).__class__.__mro__[1].__subclasses__()")
läuft durch und gibt eine Klassenliste zurück. Der Punkt-Operator und
Namen mit Unterstrich müssen darum vorher hart abgelehnt werden.
"""

from __future__ import annotations

import io
import re
import tokenize
from dataclasses import dataclass, field

import sympy
from sympy import Expr, Symbol
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication,
    parse_expr,
    rationalize,
    split_symbols_custom,
    standard_transformations,
)

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------

#: Harte Grenzen gegen Blockade des Servers. "9^9^9" beschaeftigt SymPy
#: sonst minutenlang und legt den Worker fuer die ganze Klasse lahm.
MAX_LAENGE = 200          # Zeichen
MAX_EXPONENT = 10         # Grad 10 reicht fuer Algebra 1 dreifach
MAX_ZAHL_STELLEN = 15     # laengere Literale kommen im Test nicht vor

#: Funktionen, die eine Schülerin schreiben darf. Bewusst klein halten.
ERLAUBTE_FUNKTIONEN: dict[str, object] = {
    "sqrt": sympy.sqrt,
    "abs": sympy.Abs,
}

#: Operator-Token, die durchgelassen werden. Alles andere fliegt raus:
#: '.', ',', '[', ']', ':', '=', ';', '%', '//', '&', '|', '~', '@' ...
ERLAUBTE_OPERATOREN = {"+", "-", "*", "/", "**", "^", "(", ")"}

#: Antworten, die kein Ausdruck sind (Sonderfall 3 und 4).
KEINE_LOESUNG_WOERTER = {
    "keinelösung", "keinelosung", "keine", "leeremenge", "l={}", "{}",
    "unlösbar", "unlosbar", "nichtlösbar", "nichtlosbar",
}
ALLE_ZAHLEN_WOERTER = {
    "allezahlen", "jedezahl", "allgemeingültig", "allgemeingultig",
    "unendlichviele", "immerwahr", "immerwahr!", "r", "ℝ",
}


#: Nur diese Namen stehen dem erzeugten Code zur Verfügung. Die
#: Transformationen von SymPy bauen daraus Integer(2), Symbol('x') usw.
#: Der eigentliche Schutz ist Filter 3 — hier ist bloss nichts Überflüssiges.
GLOBAL_DICT: dict[str, object] = {
    "Integer": sympy.Integer,
    "Float": sympy.Float,
    "Rational": sympy.Rational,
    "Symbol": sympy.Symbol,
    "Mul": sympy.Mul,          # nur für evaluate=False nötig
    "Add": sympy.Add,
    "Pow": sympy.Pow,
}


def symbole(namen: str, positiv: bool = True) -> tuple:
    """Symbole MIT denselben Annahmen erzeugen, die der Parser verwendet.

    Wichtig: Symbol('a') und Symbol('a', positive=True) sind fuer SymPy zwei
    verschiedene Symbole. Musterloesungen muessen darum ueber diese Funktion
    gebaut werden, sonst hebt sich antwort - loesung nie auf.
    """
    return tuple(Symbol(n, positive=positiv) for n in namen.split())


class ParseError(ValueError):
    """Ungültige Eingabe. `.message` ist für die Schülerin gedacht."""

    def __init__(self, message: str, roh: str = ""):
        super().__init__(message)
        self.message = message
        self.roh = roh


@dataclass(frozen=True)
class ParsedAnswer:
    """Ergebnis des Parsens.

    kind == "expr"          -> expr ist ein SymPy-Ausdruck
    kind == "keine_loesung" -> Gleichung ist unlösbar / L = {}
    kind == "alle_zahlen"   -> Gleichung ist allgemeingültig
    """

    kind: str
    expr: Expr | None = None        # ausgewertet  -> Äquivalenzprüfung
    form: Expr | None = None        # unausgewertet -> Formprüfung
    normalisiert: str = ""
    roh: str = ""


# --------------------------------------------------------------------------
# 1. Normalisierung
# --------------------------------------------------------------------------

_HOCHZAHLEN = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

_ERSETZUNGEN = [
    ("\u00a0", " "), ("\u2009", " "), ("\u202f", " "),   # schmale Leerzeichen
    ("\u2212", "-"), ("\u2013", "-"), ("\u2014", "-"),   # Minus, Gedankenstrich
    ("\u00b7", "*"), ("\u22c5", "*"), ("\u2219", "*"),   # ·  ⋅  ∙
    ("\u00d7", "*"), ("\u2217", "*"),                     # ×  ∗
    ("\u00f7", "/"), ("\u2215", "/"), ("\u2044", "/"),   # ÷  ∕  ⁄
    (":", "/"),                                            # Divisionsdoppelpunkt
    ("[", "("), ("]", ")"), ("{", "("), ("}", ")"),
]


def normalisieren(text: str) -> str:
    """Schülernotation -> Python-nahe Notation. Rein textuell, kein Parsen."""
    s = text.strip()

    # Hochgestellte Ziffern: x² -> x^2, aber x²y -> x^2*y (implizites Mal
    # erledigt der Parser).
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", lambda m: "^" + m.group(0).translate(_HOCHZAHLEN), s)

    for alt, neu in _ERSETZUNGEN:
        s = s.replace(alt, neu)

    # √16 -> sqrt(16), √x -> sqrt(x), √(a+b) -> sqrt(a+b).
    # Ohne Klammer reicht das Wurzelzeichen nur ueber EIN Zeichen; steht dort
    # mehr, ist die Eingabe mehrdeutig (√25a² kann 5a oder 5a² heissen) und
    # wird abgelehnt statt stillschweigend falsch gelesen.
    if re.search(r"√\s*(?:\d+(?:[.,]\d+)?(?![\d.,])|[A-Za-z])\s*[A-Za-z0-9^]", s):
        raise ParseError(
            "Setz nach dem Wurzelzeichen eine Klammer, z.B. √(25a²).", s)
    s = re.sub(r"√\s*(\d+(?:[.,]\d+)?|[A-Za-z])", r"sqrt(\1)", s)
    s = s.replace("√", "sqrt")

    # Dezimalkomma nur zwischen Ziffern: 1,5 -> 1.5
    s = re.sub(r"(?<=\d),(?=\d)", ".", s)

    return s


# --------------------------------------------------------------------------
# 2. Zeichen-Whitelist
# --------------------------------------------------------------------------


#: Buchstaben sind hier absichtlich pauschal erlaubt — welche Namen
#: tatsächlich zulässig sind, entscheidet Filter 3 mit einer verständlichen
#: Meldung ("'sin' kenne ich nicht") statt "Zeichen 'i' nicht erlaubt".
#: '_' bleibt verboten: es kommt in keiner Schülerantwort vor, aber in jedem
#: Dunder-Angriff.
_ZEICHEN_BASIS = set("abcdefghijklmnopqrstuvwxyz"
                     "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                     "0123456789+-*/^(). ")


def _zeichen_pruefen(s: str, variablen: set[str]) -> None:
    schlecht = sorted({c for c in s if c not in _ZEICHEN_BASIS})
    if schlecht:
        gezeigt = " ".join(repr(c) for c in schlecht[:5])
        raise ParseError(f"Diese Zeichen sind nicht erlaubt: {gezeigt}", s)


# --------------------------------------------------------------------------
# 3. Token-Whitelist
# --------------------------------------------------------------------------


def _token_pruefen(s: str, variablen: set[str]) -> None:
    erlaubte_namen = set(variablen) | set(ERLAUBTE_FUNKTIONEN)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(s).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        raise ParseError("Der Term ist unvollständig — fehlt eine Klammer?", s)

    tiefe = 0
    for tok in tokens:
        if tok.type in (tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL,
                        tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT):
            continue
        if tok.type == tokenize.NAME:
            if tok.string not in erlaubte_namen:
                # split_symbols zerlegt 'xy' später in x*y; darum hier prüfen,
                # ob wenigstens alle Einzelbuchstaben bekannte Variablen sind.
                if not (tok.string and all(c in variablen for c in tok.string)):
                    raise ParseError(
                        f"'{tok.string}' kenne ich nicht. "
                        f"Erlaubt sind: {', '.join(sorted(erlaubte_namen))}.", s)
        elif tok.type == tokenize.NUMBER:
            if not re.fullmatch(r"\d+(\.\d*)?|\.\d+", tok.string):
                raise ParseError(f"Ungültige Zahl: '{tok.string}'", s)
            if len(tok.string.replace(".", "")) > MAX_ZAHL_STELLEN:
                raise ParseError("Diese Zahl ist unrealistisch gross.", s)
        elif tok.type == tokenize.OP:
            if tok.string not in ERLAUBTE_OPERATOREN:
                raise ParseError(f"Das Zeichen '{tok.string}' ist hier nicht erlaubt.", s)
            if tok.string == "(":
                tiefe += 1
            elif tok.string == ")":
                tiefe -= 1
                if tiefe < 0:
                    raise ParseError("Eine Klammer wird geschlossen, die nie aufging.", s)
        else:
            raise ParseError("Diese Eingabe verstehe ich nicht.", s)

    if tiefe != 0:
        raise ParseError("Es fehlt eine schliessende Klammer.", s)


# --------------------------------------------------------------------------
# 4. Parsen
# --------------------------------------------------------------------------


def _transformationen(variablen: set[str]):
    def teilbar(symbol: str) -> bool:
        # 'xy' -> x*y nur, wenn jeder Buchstabe eine erklärte Variable ist.
        return bool(symbol) and all(c in variablen for c in symbol)

    return standard_transformations + (
        split_symbols_custom(teilbar),
        implicit_multiplication,   # 2a -> 2*a, 3(x+1) -> 3*(x+1)
        convert_xor,               # x^2 -> x**2
        rationalize,               # 1.75 -> 7/4  (siehe Kommentar unten)
    )


def _roh_parse(s: str, lokal: dict, variablen: set[str], evaluate: bool) -> Expr:
    try:
        return parse_expr(s, local_dict=lokal, global_dict=dict(GLOBAL_DICT),
                          transformations=_transformationen(variablen),
                          evaluate=evaluate)
    except Exception as exc:
        raise ParseError("Der Term ist nicht korrekt geschrieben.", s) from exc


def _exponenten_pruefen(roh: Expr, s: str) -> None:
    for potenz in roh.atoms(sympy.Pow):
        exp = potenz.exp
        # Rational zulassen, weil sqrt(x) intern x**(1/2) ist.
        if not exp.is_Rational:
            raise ParseError("Im Exponenten ist nur eine Zahl erlaubt.", s)
        if abs(exp.p) > MAX_EXPONENT or exp.q > MAX_EXPONENT:
            raise ParseError(f"Exponenten über {MAX_EXPONENT} sind nicht erlaubt.", s)


def parse_term(text: str, variablen: set[str] | None = None,
               evaluate: bool = True, positiv: bool = True) -> Expr:
    """Rohtext -> SymPy-Ausdruck. Wirft ParseError statt abzustürzen.

    evaluate=True  : normalisiert; 3(x+1) wird zu 3*x + 3.  Für "Stimmt es?"
    evaluate=False : Oberflaeche bleibt erhalten; 3(x+1) bleibt 3*(x+1).
                     Nur so ist "Ist es fertig?" ueberhaupt entscheidbar.
    """
    # None = "nicht gesagt" -> x annehmen. Eine LEERE Menge heisst dagegen
    # ausdruecklich "keine Variablen erlaubt" (reine Zahlenaufgaben).
    variablen = {"x"} if variablen is None else set(variablen)
    if not text or not text.strip():
        raise ParseError("Die Eingabe ist leer.", text)
    if len(text) > MAX_LAENGE:
        raise ParseError(f"Die Eingabe ist zu lang (max. {MAX_LAENGE} Zeichen).", text)

    s = normalisieren(text)
    _zeichen_pruefen(s, variablen)
    _token_pruefen(s, variablen)

    lokal = {name: Symbol(name, positive=positiv) for name in variablen}
    lokal.update(ERLAUBTE_FUNKTIONEN)

    # Schutzschritt: Der unausgewertete Parse ist auch bei "9^9^9" in ~1 ms
    # fertig, weil nichts gerechnet wird. Erst danach darf ausgewertet werden.
    if evaluate:
        _exponenten_pruefen(_roh_parse(s, lokal, variablen, evaluate=False), s)

    try:
        expr = parse_expr(
            s,
            local_dict=lokal,
            global_dict=dict(GLOBAL_DICT),        # kein voller SymPy-Namensraum
            transformations=_transformationen(variablen),
            evaluate=evaluate,
        )
    except ParseError:
        raise
    except Exception as exc:                      # SyntaxError, TypeError, ...
        raise ParseError("Der Term ist nicht korrekt geschrieben.", s) from exc

    if not isinstance(expr, Expr):
        raise ParseError("Das ist kein Rechenausdruck.", s)

    fremd = {sym for sym in expr.free_symbols if str(sym) not in variablen}
    if fremd:
        namen = ", ".join(sorted(str(f) for f in fremd))
        raise ParseError(f"Unbekannte Variable: {namen}", s)

    return expr


def parse_answer(text: str, variablen: set[str] | None = None,
                 positiv: bool = True) -> ParsedAnswer:
    """Wie parse_term, erkennt zusätzlich 'keine Lösung' / 'alle Zahlen'."""
    roh = text or ""
    schluessel = re.sub(r"[\s.!]", "", roh.strip().lower())

    if schluessel in KEINE_LOESUNG_WOERTER:
        return ParsedAnswer(kind="keine_loesung", roh=roh)
    if schluessel in ALLE_ZAHLEN_WOERTER:
        return ParsedAnswer(kind="alle_zahlen", roh=roh)

    expr = parse_term(roh, variablen, evaluate=True, positiv=positiv)
    form = parse_term(roh, variablen, evaluate=False, positiv=positiv)
    return ParsedAnswer(kind="expr", expr=expr, form=form,
                        normalisiert=normalisieren(roh), roh=roh)
