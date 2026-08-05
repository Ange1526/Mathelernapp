"""
Prüfung einer Schülerantwort gegen Musterlösung, Zielform und Fehlerkatalog.

Zwei getrennte Fragen, wie im Projektplan:
    1. Stimmt es?   -> Äquivalenz (gestuft, siehe _ist_null)
    2. Ist es fertig? -> Zielform (Kürzen / Faktorisieren / Ausmultiplizieren)

Ergebnis ist dreiwertig: RICHTIG / UNFERTIG / FALSCH.
Dazu kommt EINGABEFEHLER — das ist kein Rechenfehler und sollte in der
Statistik getrennt gezählt werden, sonst verfälscht ein Tippfehler die
Fehlerquote.
"""

from __future__ import annotations

import signal
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum

from sympy import (Expr, Mul, Rational as R, S, cancel, ceiling, expand,
                   factor, factorint, floor, fraction, gcd, simplify,
                   sympify, together)

from sympy import Symbol

from .eingabe_parser import ParsedAnswer, ParseError, parse_answer, symbole  # noqa: F401


#: Hartes Zeitlimit pro Antwort. Die Eingabegrenzen im Parser fangen die
#: bekannten Blockaden ab; das hier ist das Netz darunter.
ZEITLIMIT_S = 2.0


@contextmanager
def _zeitlimit(sekunden: float):
    """SIGALRM-basiert. Greift nur im Hauptthread eines POSIX-Prozesses.

    Unter dem threaded Flask-Dev-Server passiert also nichts — dort muss der
    Schutz vom Server kommen (gunicorn --timeout) oder die Pruefung in einen
    eigenen Prozess. Deshalb ist das hier die zweite Verteidigungslinie und
    nicht die erste.
    """
    aktiv = (hasattr(signal, "SIGALRM")
             and threading.current_thread() is threading.main_thread())
    if not aktiv:
        yield
        return

    def ausloesen(signum, frame):
        raise TimeoutError

    alt = signal.signal(signal.SIGALRM, ausloesen)
    signal.setitimer(signal.ITIMER_REAL, sekunden)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, alt)


class Status(str, Enum):
    RICHTIG = "richtig"
    UNFERTIG = "unfertig"          # äquivalent, aber Zielform nicht erreicht
    FALSCH = "falsch"
    EINGABEFEHLER = "eingabefehler"
    ZEITLIMIT = "zeitlimit"        # nicht Schuld der Schuelerin -> getrennt zaehlen


class Zielform(str, Enum):
    BELIEBIG = "beliebig"          # keine Formprüfung
    GEKUERZT = "gekuerzt"
    ZUSAMMENGEFASST = "zusammengefasst"   # "vereinfache so weit wie moeglich"
    FAKTORISIERT = "faktorisiert"
    AUSMULTIPLIZIERT = "ausmultipliziert"


class Art(str, Enum):
    EXPR = "expr"
    KEINE_LOESUNG = "keine_loesung"
    ALLE_ZAHLEN = "alle_zahlen"


@dataclass(frozen=True)
class Loesung:
    art: Art
    expr: Expr | None = None

    @staticmethod
    def zahl(e) -> "Loesung":
        # sympify, damit auch ein blankes int/Fraction funktioniert
        return Loesung(Art.EXPR, sympify(e))

    @staticmethod
    def keine() -> "Loesung":
        return Loesung(Art.KEINE_LOESUNG)

    @staticmethod
    def alle() -> "Loesung":
        return Loesung(Art.ALLE_ZAHLEN)


@dataclass(frozen=True)
class Fehler:
    """Ein Eintrag im Fehlerkatalog: falsches Ergebnis + Erklärung."""
    schluessel: str
    ergebnis: Loesung
    text: str


@dataclass
class Aufgabe:
    loesung: Loesung
    variablen: set[str] = field(default_factory=lambda: {"x"})
    zielform: Zielform = Zielform.BELIEBIG
    fehlerkatalog: list[Fehler] = field(default_factory=list)
    #: True: (2x-4)(x+2) gilt als noch nicht fertig, weil der gemeinsame
    #: Faktor 2 nicht ausgeklammert ist. False: wird akzeptiert.
    content_streng: bool = True
    #: True: Variablen gelten als positiv, damit sqrt(25a^2) = 5a wird
    #: (Schulkonvention). Achtung: mit positive=True liefert solve() fuer
    #: negative Loesungen []. Beim BERECHNEN der Musterloesung darum
    #: gewoehnliche Symbole verwenden, erst danach angleichen.
    positiv: bool = True
    #: Wenn die exakte Loesung KEINE endliche Dezimaldarstellung hat (-2/7,
    #: 32/3), zaehlt eine korrekt gerundete Dezimalzahl mit mindestens so
    #: vielen Nachkommastellen als richtig. Auf None setzen, um exakte
    #: Brueche zu erzwingen.
    dezimal_stellen: int | None = 2


@dataclass
class Ergebnis:
    status: Status
    text: str = ""
    fehlerschluessel: str | None = None    # None | Katalogschlüssel | "unbekannt"
    antwort: ParsedAnswer | None = None


# --------------------------------------------------------------------------
# Äquivalenz
# --------------------------------------------------------------------------

def _ist_null(d: Expr) -> bool:
    """Gestuft von billig nach teuer. simplify erst als letzte Instanz."""
    if d == 0:                     # strukturell, praktisch gratis
        return True
    e = expand(d)
    if e == 0:
        return True
    c = cancel(together(e))        # deckt Brüche und gemeinsame Nenner ab
    if c == 0:
        return True
    return simplify(c) == 0


def _angleichen(e: Expr, positiv: bool) -> Expr:
    """Symbolannahmen der Musterloesung an die des Parsers angleichen.

    Sicherheitsnetz, falls die Aufgabe mit symbols('x') statt symbole('x')
    gebaut wurde — sonst waere antwort - loesung nie null.
    """
    ersatz = {s: Symbol(s.name, positive=positiv) for s in e.free_symbols
              if s.is_positive is not positiv}
    return e.xreplace(ersatz) if ersatz else e


def _endliche_dezimalzahl(r: Expr) -> bool:
    """Laesst sich r ohne Rest als Dezimalzahl schreiben? (Nenner nur 2 und 5)"""
    return bool(r.is_Rational) and set(factorint(r.q)) <= {2, 5}


def _nachkommastellen(r: Expr) -> int:
    """Wie viele Stellen braucht die Dezimaldarstellung von r?"""
    f = factorint(r.q)
    return max(f.get(2, 0), f.get(5, 0))


def _kaufmaennisch(wert: Expr, stellen: int) -> Expr:
    """Runden mit 5 aufwaerts, wie in der Schule — nicht Pythons round()."""
    verschoben = wert * 10**stellen
    ganz = (floor(verschoben + R(1, 2)) if wert >= 0
            else ceiling(verschoben - R(1, 2)))
    return R(ganz, 10**stellen)


def _ist_korrekt_gerundet(antwort: Expr, loesung: Expr,
                          stellen: int | None) -> bool:
    """Beide Seiten auf `stellen` runden und vergleichen.

    Entscheidend: verglichen wird IMMER auf derselben Stelle, egal wie viele
    Nachkommastellen die Schuelerin schreibt. Sonst bestraft die Regel
    Genauigkeit — 10,66666 waere "falsch", weil an der fuenften Stelle
    abgeschnitten statt gerundet wurde, obwohl 10,67 durchgeht.

    Nur dort, wo es gar keine exakte Dezimalzahl gibt. Bei Loesung 43 greift
    die Regel nicht, und 43,001 bleibt falsch.
    """
    if stellen is None:
        return False
    if not (antwort.is_Rational and loesung.is_Rational):
        return False
    if _endliche_dezimalzahl(loesung) or not _endliche_dezimalzahl(antwort):
        return False
    if _nachkommastellen(antwort) < stellen:
        return False                      # "-0,3" ist zu grob
    return _kaufmaennisch(antwort, stellen) == _kaufmaennisch(loesung, stellen)


def _gleich(a: ParsedAnswer, l: Loesung, positiv: bool = True,
            dezimal_stellen: int | None = None) -> bool:
    if l.art is Art.EXPR:
        if a.kind != "expr":
            return False
        ziel = _angleichen(l.expr, positiv)
        if _ist_null(a.expr - ziel):
            return True
        return _ist_korrekt_gerundet(a.expr, ziel, dezimal_stellen)
    return a.kind == l.art.value


# --------------------------------------------------------------------------
# Zielform  — arbeitet auf .form (unausgewertet), sonst ist die
# Information beim Prüfen schon weg.
# --------------------------------------------------------------------------

def _ist_gekuerzt(form: Expr) -> bool:
    # ACHTUNG: kein together() davor — together((2x+6)/2) liefert x+3 und
    # kuerzt damit genau das weg, was geprueft werden soll.
    p, q = fraction(form)
    if q == 1:
        return True
    return gcd(p, q) == 1


def _irreduzibel(b: Expr, content_streng: bool) -> bool:
    """Laesst sich b noch weiter zerlegen?

    NICHT ueber `factor(b) == b` pruefen: b stammt aus dem unausgewerteten
    Parse, dort ist die Argumentreihenfolge nicht kanonisch (Add(x, 1) statt
    Add(1, x)), und == vergleicht strukturell. Stattdessen die Gestalt von
    factor(b) anschauen.
    """
    zerlegt = factor(expand(b))
    args = Mul.make_args(zerlegt)
    zahlen = [a for a in args if not a.free_symbols]
    symbolisch = [a for a in args if a.free_symbols]

    if len(symbolisch) > 1:
        return False
    for a in symbolisch:
        if a.is_Pow and a.exp.is_Integer and a.exp > 1:
            return False
    if content_streng:
        prod = Mul(*zahlen) if zahlen else S.One
        if prod not in (S.One, S.NegativeOne):
            return False                    # gemeinsamer Zahlenfaktor fehlt
    return True


def _ist_faktorisiert(form: Expr, ziel: Expr, content_streng: bool = True) -> bool:
    # Wenn die Loesung gar nicht zerlegbar ist, kann man nichts verlangen.
    zerlegt = factor(expand(ziel))
    if not (zerlegt.is_Mul or zerlegt.is_Pow):
        return True

    faktoren = Mul.make_args(form)
    if len(faktoren) < 2 and not form.is_Pow:
        return False
    for f in faktoren:
        basis = f.base if f.is_Pow else f
        if not basis.free_symbols:
            continue                        # reiner Zahlenfaktor ist ok
        if not _irreduzibel(basis, content_streng):
            return False
    return True


def _anzahl_summanden(e: Expr) -> int:
    return len(e.args) if e.is_Add else 1


def _ist_zusammengefasst(form: Expr) -> bool:
    """Stehen noch gleichartige Glieder nebeneinander?

    5b - 10bc + 3bc hat drei Summanden, ausmultipliziert bleiben zwei.
    Auf .expr ist das nicht sichtbar: SymPy fasst beim Auswerten selbst
    zusammen.
    """
    return _anzahl_summanden(form) == _anzahl_summanden(expand(form))


def _ist_ausmultipliziert(expr: Expr) -> bool:
    return expand(expr) == expr


def _form_erreicht(a: ParsedAnswer, aufgabe: Aufgabe) -> bool:
    z = aufgabe.zielform
    if z is Zielform.BELIEBIG or a.kind != "expr":
        return True
    if z is Zielform.GEKUERZT:
        return _ist_gekuerzt(a.form)
    if z is Zielform.FAKTORISIERT:
        return _ist_faktorisiert(a.form,
                                 _angleichen(aufgabe.loesung.expr, aufgabe.positiv),
                                 aufgabe.content_streng)
    if z is Zielform.ZUSAMMENGEFASST:
        return _ist_zusammengefasst(a.form)
    if z is Zielform.AUSMULTIPLIZIERT:
        return _ist_ausmultipliziert(a.expr)
    return True


# --------------------------------------------------------------------------
# Hauptfunktion
# --------------------------------------------------------------------------

def _fehlende_klammer(a: ParsedAnswer, aufgabe: Aufgabe, l: Expr):
    """Waere die Antwort mit einer Klammer um Zaehler oder Nenner richtig?

    "6a+1/5" heisst nach Punktrechnung 6a + 0,2, gemeint ist (6a+1)/5.
    "(2-3z)/3z" heisst ((2-3z)/3)·z, gemeint ist (2-3z)/(3z).
    Beides kam im Testlauf vor.
    """
    text = a.normalisiert
    if "/" not in text:
        return None
    kopf, _, rest = text.partition("/")
    if not kopf.strip() or not rest.strip():
        return None
    for versuch, wo in ((f"({kopf})/{rest}", "Zähler"),
                        (f"{kopf}/({rest})", "Nenner"),
                        (f"({kopf})/({rest})", "Zähler und Nenner")):
        try:
            neu = parse_answer(versuch, aufgabe.variablen, positiv=aufgabe.positiv)
        except ParseError:
            continue
        if neu.kind == "expr" and _ist_null(neu.expr - l):
            return wo
    return None


def _allgemeiner_fehler(a: ParsedAnswer, aufgabe: Aufgabe):
    """Zwei Fehlerklassen, die in JEDER Aufgabe auftreten.

    Sie gehoeren nicht in den Katalog jeder einzelnen Aufgabe, sondern hierher
    — sonst muesste man sie 17-mal von Hand eintragen und faengt sie trotzdem
    nur teilweise.
    """
    if a.kind != "expr" or aufgabe.loesung.art is not Art.EXPR:
        return None
    l = _angleichen(aufgabe.loesung.expr, aufgabe.positiv)

    # 1. Vorzeichenfehler: die Antwort ist das Negative der Loesung.
    if _ist_null(a.expr + l):
        return ("vorzeichen_allgemein", "Fast — schau nochmals das Vorzeichen an.")

    # 2. Nennerklammer vergessen: "2b^2/3a^2" heisst nach Punktrechnung
    #    (2b²/3)·a², gemeint ist fast immer 2b²/(3a²).
    wo = _fehlende_klammer(a, aufgabe, l)
    if wo:
        beispiel = {"Zähler": "(6a+1)/5 statt 6a+1/5",
                    "Nenner": "2b/(3a) statt 2b/3a",
                    "Zähler und Nenner": "(6a+1)/(3a) statt 6a+1/3a"}[wo]
        return ("fehlende_klammer",
                f"Da fehlt eine Klammer um den {wo} — z.B. {beispiel}.")

    # 3. Kommastelle verrutscht: "-29" statt "-0,29".
    if a.expr.is_Rational and l.is_Number and l != 0:
        for k in (1, 2, 3, -1, -2, -3):
            verschoben = a.expr / 10**k
            if (_ist_null(verschoben - l)
                    or _ist_korrekt_gerundet(verschoben, l, aufgabe.dezimal_stellen)):
                return ("komma_verrutscht",
                        "Der Wert stimmt, aber die Kommastelle nicht.")

    # 4. Gerundet statt exakt: nur bei Dezimaleingaben (Nenner ist Zehnerpotenz)
    #    und nur, wenn der Wert nahe genug an der Loesung liegt.
    if a.expr.is_Rational and l.is_Number and l != 0:
        n = a.expr.q
        ist_dezimal = n > 1 and set(factorint(n)) <= {2, 5}
        if ist_dezimal and abs((a.expr - l) / l) <= R(1, 10):
            # Nur wo es gar keine exakte Dezimalform gibt, ist Runden erlaubt
            # und die Rueckmeldung soll aufs Runden zeigen.
            if aufgabe.dezimal_stellen is None or _endliche_dezimalzahl(l):
                return ("gerundet",
                        "Der Wert stimmt ungefähr — gefragt ist aber der exakte Bruch.")
            return ("falsch_gerundet",
                    f"Fast — schau nochmals das Runden an "
                    f"(mindestens {aufgabe.dezimal_stellen} Nachkommastellen).")
    return None


UNFERTIG_TEXT = {
    Zielform.GEKUERZT: "Stimmt — aber das lässt sich noch kürzen.",
    Zielform.ZUSAMMENGEFASST: "Stimmt — aber du kannst noch gleichartige Glieder zusammenfassen.",
    Zielform.FAKTORISIERT: "Stimmt — aber das ist noch kein fertiges Produkt.",
    Zielform.AUSMULTIPLIZIERT: "Stimmt — aber die Klammern sind noch nicht ausmultipliziert.",
}


def pruefe(eingabe: str, aufgabe: Aufgabe) -> Ergebnis:
    try:
        with _zeitlimit(ZEITLIMIT_S):
            return _pruefe(eingabe, aufgabe)
    except TimeoutError:
        return Ergebnis(Status.ZEITLIMIT,
                        text="Das dauert zu lange — bitte kürzer schreiben.")


def _pruefe(eingabe: str, aufgabe: Aufgabe) -> Ergebnis:
    try:
        antwort = parse_answer(eingabe, aufgabe.variablen, positiv=aufgabe.positiv)
    except ParseError as e:
        return Ergebnis(Status.EINGABEFEHLER, text=e.message)

    if _gleich(antwort, aufgabe.loesung, aufgabe.positiv,
               aufgabe.dezimal_stellen):
        if _form_erreicht(antwort, aufgabe):
            return Ergebnis(Status.RICHTIG, text="Richtig.", antwort=antwort)
        return Ergebnis(Status.UNFERTIG,
                        text=UNFERTIG_TEXT.get(aufgabe.zielform, "Stimmt, aber noch nicht fertig."),
                        antwort=antwort)

    for f in aufgabe.fehlerkatalog:
        if _gleich(antwort, f.ergebnis, aufgabe.positiv):
            return Ergebnis(Status.FALSCH, text=f.text,
                            fehlerschluessel=f.schluessel, antwort=antwort)

    allgemein = _allgemeiner_fehler(antwort, aufgabe)
    if allgemein:
        return Ergebnis(Status.FALSCH, text=allgemein[1],
                        fehlerschluessel=allgemein[0], antwort=antwort)

    return Ergebnis(Status.FALSCH, text="Das stimmt leider nicht.",
                    fehlerschluessel="unbekannt", antwort=antwort)
