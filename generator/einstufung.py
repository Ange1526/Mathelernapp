# -*- coding: utf-8 -*-
"""
Einstufungstest — wo steigt dieser Schüler ein, und wo genau fehlt ihm etwas?

Der Test muss ZWEI sehr verschiedene Leute bedienen:

  Der Anfänger      kann wenig und soll den ganzen Weg der Reihe nach gehen.
                    Für ihn darf der Test NICHT immer schwerer werden — er
                    würde nur immer wieder scheitern, und am Schluss wüsste
                    die App bloss «kann nichts». Für ihn wird der Test
                    SPEZIFISCHER: gleiche Stufe, aber gezielt eine Ebene
                    tiefer, bis klar ist, wo die Kette reisst.

  Der Gymnasiast    kann fast alles und hat drei, vier Lücken. Für ihn muss
                    der Test SCHNELL schwerer werden, sonst löst er zwanzig
                    leichte Aufgaben und die App weiss immer noch nicht, wo
                    die Lücken sind. Genau diese Lücken sind aber das, was
                    die Studie messen soll.

Deshalb drei Phasen:

  1  ANKER          Binäre Suche über die Themenstränge. Vier Aufgaben, und
                    die grobe Höhe steht. Danach ist klar, ob wir es mit
                    einem Anfänger oder einem Fortgeschrittenen zu tun haben.

  2  STRANGDURCHGANG Jeder Themenstrang, der noch nicht entschieden ist,
                    bekommt eine Sonde. Die STUFE dieser Sonde richtet sich
                    nach dem laufenden Niveau: wer stark ist, wird sofort auf
                    Level C gefragt; wer schwach ist, bekommt die Grundform
                    auf Level A. Ein Fehlschlag schiebt den Strang ein, der
                    die Voraussetzungen liefert — nicht schwerer, sondern
                    tiefer.

  3  FEINSCHLIFF    Nur für die Starken. Alles, was bisher nur ÜBER DIE
                    VORSTUFENREGEL gutgeschrieben wurde und nie selbst
                    geprüft war, wird jetzt auf Level C nachgeprüft — genau
                    an den Stellen, die die Erhebung abfragt. Wer hier
                    scheitert, verliert die Gutschrift wieder. Das ist die
                    Lückensuche für Leute, die sonst mit 100 Prozent aus dem
                    Test kämen.

Am Schluss steht nicht nur eine Startlektion, sondern ein PLAN: welche
Lektionen, in welcher Reihenfolge, auf welchem Level.

Die Stränge werden NICHT von Hand gepflegt. Sie entstehen aus
`SCHABLONE_FUER` — kommt ein Generator dazu, prüft der Test ihn automatisch
mit. Was keinen Generator hat, kommt gar nicht erst vor.
"""
from __future__ import annotations

from .netz import (KLARTEXT, SCHABLONE_FUER, ZIEL, alle_vorstufen,
                   naechste_lektion, rueckwaerts_gutschreiben, voraussetzungen,
                   zielmenge)

# ───────────────────────────────────────────────────────────── Stellschrauben

#: Höchstzahl Aufgaben — zwei Grenzen, und das ist Absicht.
#:
#: Für den Starken IST der Test die Lückensuche. Er beantwortet eine Sonde in
#: zwanzig Sekunden; dreissig Sonden sind zehn Minuten, und dafür bekommt er
#: jede seiner Lücken benannt statt eines nutzlosen «du kannst 95 Prozent».
#: Für den Schwachen wäre dieselbe Zahl eine Viertelstunde Misserfolg, die am
#: Plan nichts mehr ändert — er kommt über den Frühabbruch früher heraus.
MAX_AUFGABEN = 30

#: Niveau -> Obergrenze. Wer unten steht, wird nicht mit Aufgaben zugedeckt,
#: die er ohnehin nicht löst.
GRENZE = {0: 16, 1: 22, 2: 30, 3: 30}

#: So viele Aufgaben werden mindestens gestellt, auch wenn rechnerisch schon
#: alles gutgeschrieben wäre. Sonst kommt ein starker Schüler nach vier
#: richtigen Antworten heraus, ohne dass eine Lücke gesucht wurde.
MIN_AUFGABEN = 10

#: So viele Sonden hat die Ankerphase.
ANKER_SONDEN = 3

#: So viele Fehlschläge in Folge auf der untersten Stufe, dann steht fest:
#: dieser Schüler beginnt vorne. Weitere Sonden wären nur weitere
#: Misserfolge und ändern am Plan nichts mehr.
ABBRUCH_FEHLER = 3

#: Vor dem Frühabbruch werden noch so viele weit auseinanderliegende Stellen
#: auf Level A geprüft. Sonst übersieht der Test die Inselbegabung — jemanden,
#: der beim Rechnen schwach ist, Potenzen aber sicher kann — und er weiss
#: nicht, wo dieser Schüler wirklich anfängt.
STREU_SONDEN = 5
STREU_STELLEN = (0.0, 0.15, 0.35, 0.6, 0.85)

#: Ab diesem Anteil sicherer Lektionen gilt jemand als fortgeschritten und
#: bekommt die Feinschliffphase.
FEIN_AB_PROZENT = 70

#: Höchstzahl Sonden im Feinschliff.
FEIN_SONDEN = 8

#: Niveau 0 bis 3 — die laufende Schätzung. Startet in der Mitte.
NIVEAU_START = 2

#: Niveau  ->  (welche Sprosse der Leiter, welches Level)
#: Das ist die Umsetzung der Kernregel: nach oben wird es SCHWERER,
#: nach unten wird es SPEZIFISCHER — das Level bleibt bei A, die Sprosse sinkt.
STUFE = {
    3: ("hoch", "C"),
    2: ("mitte", "B"),
    1: ("mitte", "A"),
    0: ("tief", "A"),
}

LEVELS = ("A", "B", "C")


def _num(lektion: str) -> tuple[int, int]:
    k, n = lektion.split(".")
    return int(k), int(n)


# ───────────────────────────────────────────────────────────────── Stränge

class Strang:
    """Ein Themenstrang: alles, was EINE Schablone übt.

    Die Leiter hat drei Sprossen. Bei einer Schablone mit nur einer Lektion
    fallen sie zusammen — dann trägt allein das Level den Unterschied.
    """

    def __init__(self, nr: str, lektionen: list[str]):
        self.nr = nr
        self.lektionen = sorted(lektionen, key=_num)
        self.tief = self.lektionen[0]
        self.mitte = self.lektionen[len(self.lektionen) // 2]
        self.hoch = self.lektionen[-1]

    def sprosse(self, name: str) -> str:
        return {"tief": self.tief, "mitte": self.mitte, "hoch": self.hoch}[name]

    def bis(self, lektion: str) -> list[str]:
        """Alle Lektionen des Strangs bis einschliesslich dieser."""
        return [l for l in self.lektionen if _num(l) <= _num(lektion)]

    def ab(self, lektion: str) -> list[str]:
        return [l for l in self.lektionen if _num(l) > _num(lektion)]

    def __repr__(self):
        return f"<Strang {self.nr}: {self.tief}…{self.hoch}>"


def straenge() -> list[Strang]:
    """Alle Stränge, nach Netztiefe geordnet — leicht zuerst.

    Grundlage ist `SCHABLONE_FUER`. Eine Lektion ohne Generator kann nicht
    geprüft werden und taucht darum auch nicht auf.
    """
    gruppen: dict[str, list[str]] = {}
    for lektion, kap in SCHABLONE_FUER.items():
        gruppen.setdefault(kap, []).append(lektion)
    return [Strang(k, v) for k, v in sorted(gruppen.items(), key=lambda p: _num(p[0]))]


def strang_von(lektion: str, liste: list[Strang]) -> Strang | None:
    kap = SCHABLONE_FUER.get(lektion)
    for s in liste:
        if s.nr == kap:
            return s
    return None


def vorstrang(s: Strang, liste: list[Strang]) -> str | None:
    """Der Strang, der die Voraussetzungen der untersten Sprosse liefert.

    Dorthin geht die Sonde, wenn jemand an diesem Strang scheitert. Das ist
    der Unterschied zwischen «nochmals dasselbe, nur leichter» und «eine
    Ebene tiefer nachschauen».
    """
    for v in voraussetzungen(s.tief):
        kap = SCHABLONE_FUER.get(v)
        if kap and kap != s.nr:
            return kap
    # Keine direkte Voraussetzung mit Generator: dann der Strang davor.
    nummern = [x.nr for x in liste]
    if s.nr in nummern:
        i = nummern.index(s.nr)
        if i > 0:
            return nummern[i - 1]
    return None


# ───────────────────────────────────────────────────────────────── Der Test

class Einstufung:
    """Der Zustand während des Tests. Wird in der Session gehalten.

    Alle Felder sind einfache Typen, damit `als_dict()` in die Flask-Session
    passt.
    """

    def __init__(self, sicher=None, gescheitert=None, gestellt: int = 0,
                 einstiegslevel=None, niveau: int = NIVEAU_START,
                 phase: str = "anker", lo: int = 0, hi: int = -1,
                 anker: int = 0, warteschlange=None, erledigt=None,
                 aktuell=None, protokoll=None, geprueft=None,
                 rueckwaerts=None, fein=None, abstieg=None,
                 folgefehler: int = 0, streu=None, kontrolle=None):
        self._cache = straenge()
        self.sicher = set(sicher or ())
        self.gescheitert = set(gescheitert or ())
        self.gestellt = gestellt
        #: Lektion -> Level, auf dem der Schüler einsteigt.
        self.einstiegslevel = dict(einstiegslevel or {})
        self.niveau = niveau
        self.phase = phase
        self.lo = lo
        self.hi = hi if hi >= 0 else max(len(self._cache) - 1, 0)
        self.anker = anker
        #: Stränge, die noch eine Sonde brauchen (Kapitelschlüssel).
        self.warteschlange = list(warteschlange) if warteschlange is not None \
            else [s.nr for s in self._cache]
        #: Strang -> Ergebnis ("C", "B", "A", "luecke", "uebersprungen")
        self.erledigt = dict(erledigt or {})
        #: Die Sonde, die gerade offen ist: [strang, lektion, level]
        self.aktuell = list(aktuell) if aktuell else None
        #: [(lektion, level, richtig), ...] — für den Bericht
        self.protokoll = [list(x) for x in (protokoll or [])]
        #: Lektionen, die der Schüler SELBST gelöst hat (nicht gutgeschrieben)
        self.geprueft = set(geprueft or ())
        #: Stränge, für die schon einmal rückwärts gesucht wurde
        self.rueckwaerts = set(rueckwaerts or ())
        #: Warteschlange der Feinschliffphase
        self.fein = list(fein or [])
        #: Strang -> Level, auf dem die NÄCHSTE Sonde dieses Strangs steht.
        #: Trägt den Abstieg C -> B -> A innerhalb eines Strangs.
        self.abstieg = dict(abstieg or {})
        #: Fehlschläge in Folge — Grundlage des Frühabbruchs.
        self.folgefehler = folgefehler
        #: Streuprobe vor dem Frühabbruch. None = noch nicht zusammengestellt.
        self.streu = list(streu) if streu is not None else None
        #: Lektionen, die gutgeschrieben sind, aber nur MITTELBAR: über die
        #: Vorstufenregel oder über eine Antwort auf einer leichteren Stufe.
        #: Sie fallen nicht aus dem Weg — sie kommen als Kontrollrunde
        #: wieder, auf dem Level, das noch nicht bewiesen ist. Ohne das
        #: entsteht genau der Deckeneffekt, den die Studie fürchtet:
        #: «alles sicher», weil nie jemand nachgefragt hat.
        self.kontrolle = dict(kontrolle or {})

    # ------------------------------------------------------------ Hilfen

    @property
    def _straenge(self) -> list[Strang]:
        return self._cache

    def _strang(self, nr: str) -> Strang | None:
        for s in self._cache:
            if s.nr == nr:
                return s
        return None

    def _prozent(self) -> int:
        """Anteil sicherer Lektionen an ALLEN 170 — für die Anzeige."""
        ziel = zielmenge()
        return int(len(ziel & self.sicher) / len(ziel) * 100) if ziel else 0

    def _prozent_uebbar(self) -> int:
        """Anteil an dem, was überhaupt geübt werden kann.

        Der Unterschied ist gross und wichtig: von 170 Lektionen haben erst
        rund 80 einen Generator. Wer alles kann, was die App prüfen kann,
        steht bei 100 Prozent hier — und bei 47 Prozent auf der anderen Zahl.
        Für Entscheidungen im Test zählt DIESE Zahl, sonst greift keine
        Regel, die an einer Schwelle hängt.
        """
        uebbar = set(SCHABLONE_FUER)
        if not uebbar:
            return 0
        return int(len(uebbar & self.sicher) / len(uebbar) * 100)

    def _budget(self) -> int:
        """Wie viele Aufgaben noch? Der Starke bekommt mehr.

        Nicht aus Strenge, sondern weil bei ihm jede weitere Sonde eine
        mögliche Lücke aufdeckt, während sie beim Schwachen nur bestätigt,
        was nach drei Fehlschlägen schon feststeht.
        """
        return GRENZE.get(max(0, min(3, self.niveau)), MAX_AUFGABEN) - self.gestellt

    # ------------------------------------------------------------ Ablauf

    def naechste(self) -> str | None:
        """Welche Lektion wird als Nächstes gefragt? None heisst: fertig.

        Die Funktion darf mehrfach aufgerufen werden — solange keine Antwort
        kam, kommt dieselbe Aufgabe zurück.
        """
        if self.aktuell:
            return self.aktuell[1]
        if self._budget() <= 0:
            return None
        gewaehlt = self._waehlen()
        if gewaehlt is None:
            return None
        self.aktuell = list(gewaehlt)
        return self.aktuell[1]

    def naechstes_level(self) -> str:
        """Auf welchem Level wird die aktuelle Sonde gestellt?

        Das ist der Kern der Adaptivität. Früher stand hier fest «B».
        """
        if not self.aktuell:
            self.naechste()
        return self.aktuell[2] if self.aktuell else "B"

    def _waehlen(self):
        """Die nächste Sonde bestimmen: (strang, lektion, level)."""
        alle = self._straenge
        if not alle:
            return None

        # ── Phase 1 · Anker ──────────────────────────────────────────────
        if self.phase == "anker":
            if self.anker < ANKER_SONDEN and self.lo <= self.hi:
                i = max(0, min(len(alle) - 1, (self.lo + self.hi) // 2))
                s = alle[i]
                if s.mitte not in self.geprueft:
                    return (s.nr, s.mitte, "B")
            self.phase = "straenge"
            self.warteschlange = self._reihenfolge()

        # ── Phase 2 · Strangdurchgang ────────────────────────────────────
        if self.phase == "straenge":
            # Frühabbruch. Wer dreimal in Folge auf der untersten Stufe
            # scheitert, beginnt vorne — jede weitere Sonde wäre ein
            # weiterer Misserfolg und würde am Plan nichts mehr ändern.
            # Vorher aber die Streuprobe: sonst übersieht der Test die
            # Inselbegabung.
            if self.folgefehler >= ABBRUCH_FEHLER and self.niveau == 0:
                if self.streu is None:
                    self.streu = self._streuprobe()
                while self.streu:
                    lektion = self.streu.pop(0)
                    if lektion in self.geprueft:
                        continue
                    s = strang_von(lektion, alle)
                    return (s.nr if s else "-", lektion, "A")
                self.phase = "fein"
                self.fein = []
                return None

            while self.warteschlange:
                nr = self.warteschlange[0]
                s = self._strang(nr)
                if s is None or nr in self.erledigt:
                    self.warteschlange.pop(0)
                    continue
                # Ein Strang, der über die Vorstufenregel komplett
                # gutgeschrieben wurde, bekommt beim Starken trotzdem eine
                # KONTROLLSONDE auf der obersten Sprosse und der schwersten
                # Stufe. Genau hier steckt der Deckeneffekt: ohne diese Sonde
                # führt eine einzige richtige Antwort in Kapitel 12 dazu, dass
                # dreissig Lektionen als sicher gelten, die nie jemand
                # angeschaut hat. Beim Schwachen wäre dieselbe Sonde nur
                # verlorene Zeit — deshalb hängt sie am Niveau.
                offen = [l for l in s.lektionen if l not in self.sicher]
                if not offen:
                    if self.niveau >= 2 and s.hoch not in self.geprueft:
                        return (s.nr, s.hoch, "C")
                    self.erledigt[nr] = "uebersprungen"
                    self.warteschlange.pop(0)
                    continue

                # Welches Level? Entweder der laufende Abstieg dieses Strangs
                # (nach einem Fehlschlag) oder das Niveau des Schülers.
                if nr in self.abstieg:
                    level = self.abstieg[nr]
                    sprosse = {"C": "hoch", "B": "mitte", "A": "tief"}[level]
                else:
                    sprosse, level = STUFE[max(0, min(3, self.niveau))]
                lektion = s.sprosse(sprosse)

                # Eine Sprosse, die schon sicher oder schon geprüft ist,
                # bringt nichts — dann die erste offene, ungeprüfte nehmen.
                if lektion in self.sicher or lektion in self.geprueft:
                    frisch = [l for l in offen if l not in self.geprueft]
                    if not frisch:
                        self.erledigt[nr] = "uebersprungen"
                        self.warteschlange.pop(0)
                        continue
                    lektion = frisch[0]
                return (s.nr, lektion, level)

            self.phase = "fein"
            self.fein = self._feinschliff_liste()

        # ── Phase 3 · Feinschliff ────────────────────────────────────────
        if self.phase == "fein":
            while self.fein:
                lektion = self.fein.pop(0)
                if lektion in self.geprueft:
                    continue
                s = strang_von(lektion, alle)
                return (s.nr if s else "-", lektion, "C")

        # ── Nachschlag ───────────────────────────────────────────────────
        # Unter MIN_AUFGABEN hört der Test nicht auf. Wer nach acht Aufgaben
        # fertig wäre, bekommt die schwersten Stellen, die er noch nie selbst
        # gelöst hat — beim Starken sind das genau seine blinden Flecken.
        if self.gestellt < MIN_AUFGABEN:
            stark = self.niveau >= 2
            rest = [l for l in sorted(set(SCHABLONE_FUER), key=_num,
                                      reverse=stark)
                    if l not in self.geprueft]
            if rest:
                # Beim Starken die schwersten Stellen, die er nie selbst
                # gelöst hat — dort liegen seine blinden Flecken. Beim
                # Schwachen die leichtesten, die noch offen sind — dort
                # entscheidet sich, wo er wirklich anfängt.
                lektion = rest[0]
                s = strang_von(lektion, alle)
                return (s.nr if s else "-", lektion, "C" if stark else "A")
        return None

    def _reihenfolge(self) -> list[str]:
        """Welcher Strang zuerst?

        Stränge, in denen eine Teilaufgabe der Erhebung hängt, kommen zuerst.
        Reicht das Budget nicht für alle, fällt hinten das weg, was am
        wenigsten zählt — und nicht zufällig das, was die Prüfung abfragt.
        """
        ziel_lektionen = set(ZIEL.values())
        offen = [x for x in self._straenge if x.nr not in self.erledigt]
        return [x.nr for x in sorted(
            offen, key=lambda x: (0 if set(x.lektionen) & ziel_lektionen else 1,
                                  _num(x.nr)))]

    def _streuprobe(self) -> list[str]:
        """Weit auseinanderliegende Stellen, auf der leichtesten Stufe.

        Sie kostet drei Aufgaben und verhindert den teuersten Irrtum des
        Tests: jemanden, der beim Kopfrechnen scheitert, aber Potenzen
        sicher kann, ganz nach vorne zu setzen.
        """
        alle = self._straenge
        if not alle:
            return []
        n = len(alle)
        stellen = {int(n * anteil) for anteil in STREU_STELLEN}
        raus = []
        for i in sorted(stellen):
            s = alle[min(i, n - 1)]
            if s.tief not in self.geprueft and s.nr not in self.erledigt:
                raus.append(s.tief)
        return raus[:STREU_SONDEN]

    def _feinschliff_liste(self) -> list[str]:
        """Der Rest des Budgets, gezielt eingesetzt.

        Wer bis hierher kommt, hat alle Stränge durch und noch Aufgaben übrig.
        Diese gehen an die Stellen, die INNERHALB eines gutgeschriebenen
        Strangs liegen und nie selbst geprüft wurden — zuerst dorthin, wo die
        Erhebung eine Teilaufgabe hat, dann in die grossen Stränge, wo eine
        einzelne Sonde am wenigsten aussagt.

        Das ist die zweite Verteidigungslinie gegen den Deckeneffekt. Die
        dritte ist die Probe-Erhebung nach dem Test: eine Lücke, die HIER
        durchrutscht, fällt dort auf und wird zurückgenommen.
        """
        if self._prozent_uebbar() < FEIN_AB_PROZENT:
            return []
        ziel = set(ZIEL.values())
        kandidaten = []
        for s in self._straenge:
            for l in s.lektionen:
                if l in self.geprueft or l not in self.sicher:
                    continue
                kandidaten.append((0 if l in ziel else 1, -len(s.lektionen),
                                   _num(l), l))
        kandidaten.sort()
        return [k[-1] for k in kandidaten][:FEIN_SONDEN]

    # ------------------------------------------------------------ Antwort

    def antwort(self, lektion: str, richtig: bool) -> None:
        """Eine Antwort verbuchen und den Zustand fortschreiben."""
        if self.aktuell and self.aktuell[1] == lektion:
            strang_nr, _, level = self.aktuell
        else:
            # Aufruf von aussen (z.B. Lektion ohne Generator überspringen).
            s = strang_von(lektion, self._straenge)
            strang_nr, level = (s.nr if s else "-"), "B"
        self.aktuell = None
        self.gestellt += 1
        self.protokoll.append([lektion, level, bool(richtig)])
        self.geprueft.add(lektion)
        if richtig and level == "C":
            self.kontrolle.pop(lektion, None)

        s = self._strang(strang_nr)
        phase_war = self.phase

        if richtig:
            self.niveau = min(3, self.niveau + 1)
            self._gutschreiben(lektion, level, s)
        else:
            self.niveau = max(0, self.niveau - 1)
            self.gescheitert.add(lektion)
            self._luecke(lektion, level, s, phase_war)

        self._phase_fortschreiben(strang_nr, richtig, level)

    def _gutschreiben(self, lektion: str, level: str, s: Strang | None) -> None:
        """Was zählt eine richtige Antwort?

        Auf B und C: die Lektion und ALLE ihre Vorstufen im ganzen Netz —
        wer 12.8 auf C löst, kann das Ausklammern darunter auch.

        Auf A nur die Lektion selbst und ihre Vorstufen INNERHALB des Strangs.
        Die Grundform zu können heisst nicht, dass die schwierigen Fälle
        sitzen. Ohne diese Unterscheidung schrieb ein einziger Treffer auf der
        leichtesten Stufe bis zu 34 Lektionen gut.
        """
        if level in ("B", "C"):
            vorher = set(self.sicher)
            self.sicher = rueckwaerts_gutschreiben(lektion, self.sicher)
            # Alles, was NUR über die Vorstufenregel dazukam, ist nicht
            # bewiesen — es kommt als Kontrolle wieder.
            for l in (self.sicher - vorher):
                if l != lektion and l in SCHABLONE_FUER and l not in self.geprueft:
                    self.kontrolle.setdefault(l, level)
        else:
            self.sicher.add(lektion)
            if s:
                vorher = alle_vorstufen(lektion)
                self.sicher |= {l for l in s.bis(lektion) if l in vorher}
            # Auf Level A gelöst heisst: die Grundform sitzt. Ob die
            # schwierigen Fälle sitzen, ist damit NICHT gezeigt.
            self.kontrolle[lektion] = "B"
        if s is None:
            return
        if level == "C":
            self.sicher |= set(s.bis(lektion))
            if lektion == s.hoch:
                # Oberste Sprosse auf der schwersten Stufe: der Strang sitzt.
                # Die Lektionen darunter wurden aber nie einzeln gefragt —
                # sie kommen als kurze Kontrollrunde auf Level C wieder.
                self.sicher |= set(s.lektionen)
                for l in s.lektionen:
                    if l != lektion and l not in self.geprueft:
                        self.kontrolle.setdefault(l, "C")
                self.erledigt[s.nr] = "C"
                return
            self.erledigt.setdefault(s.nr, "C")
            for l in s.ab(lektion):
                self.einstiegslevel[l] = "C"
        elif level == "B":
            self.sicher |= set(s.bis(lektion))
            for l in s.ab(lektion):
                self.einstiegslevel[l] = "B"
            self.erledigt.setdefault(s.nr, "B")
        else:
            for l in s.ab(lektion):
                self.einstiegslevel.setdefault(l, "A")
            self.erledigt.setdefault(s.nr, "A")

    def _luecke(self, lektion: str, level: str, s: Strang | None,
                phase: str) -> None:
        """Ein Fehlschlag: die Gutschrift wird zurückgenommen.

        Die falsch gelöste Lektion und alles, was im selben Strang darauf
        aufbaut, verliert eine allfällige Gutschrift wieder — sonst behauptet
        die App Lückenfreiheit, wo eine Lücke ist. Genau dieser Fall führt
        bei starken Schülern zum Deckeneffekt: sie bekommen über die
        Vorstufenregel alles gutgeschrieben und üben vier Wochen nichts.

        Das Einstiegslevel wird NICHT sofort auf A gesetzt. Wer an Level C
        scheitert, ist nicht auf Level A zurückgeworfen — das wäre die
        Unterforderung, die wir gerade vermeiden wollen. Den Ausschlag gibt
        die nächste Sonde desselben Strangs, eine Stufe tiefer.
        """
        self.sicher.discard(lektion)
        if s is None:
            self.einstiegslevel[lektion] = "A"
            return
        for l in s.ab(lektion):
            self.sicher.discard(l)
        tiefer = {"C": "B", "B": "A", "A": "A"}[level]
        for l in s.lektionen:
            if l not in self.sicher:
                self.einstiegslevel[l] = tiefer

    def _phase_fortschreiben(self, strang_nr, richtig, level) -> None:
        self.folgefehler = 0 if richtig else self.folgefehler + 1

        if self.phase == "anker":
            self.anker += 1
            i = self._index(strang_nr)
            if i is not None:
                if richtig:
                    self.lo = i + 1
                else:
                    self.hi = i - 1
            if self.anker >= ANKER_SONDEN or self.lo > self.hi:
                self.phase = "straenge"
                self.warteschlange = self._reihenfolge()
            return

        if self.phase == "straenge":
            s = self._strang(strang_nr)
            if richtig:
                self.abstieg.pop(strang_nr, None)
                self.erledigt.setdefault(strang_nr, level)
                if strang_nr in self.warteschlange:
                    self.warteschlange.remove(strang_nr)
                return

            # Fehlschlag: erst eine Stufe tiefer im SELBEN Strang. Das ist
            # der Unterschied zwischen «kann das Thema nicht» und «kann die
            # schwerste Form davon noch nicht».
            tiefer = {"C": "B", "B": "A"}.get(level)
            if tiefer and s is not None:
                offen = [l for l in s.lektionen if l not in self.geprueft]
                if offen:
                    self.abstieg[strang_nr] = tiefer
                    return

            # Auch die Grundform sitzt nicht: Strang steht fest, und die
            # Sonde geht eine EBENE tiefer — in den Strang, der die
            # Voraussetzungen liefert.
            self.abstieg.pop(strang_nr, None)
            self.erledigt.setdefault(strang_nr, "luecke")
            if strang_nr in self.warteschlange:
                self.warteschlange.remove(strang_nr)
            if s is not None and s.nr not in self.rueckwaerts:
                self.rueckwaerts.add(s.nr)
                vor = vorstrang(s, self._straenge)
                if vor and vor not in self.erledigt:
                    if vor in self.warteschlange:
                        self.warteschlange.remove(vor)
                    self.warteschlange.insert(0, vor)
            return

    def _index(self, strang_nr: str) -> int | None:
        for i, s in enumerate(self._straenge):
            if s.nr == strang_nr:
                return i
        return None

    # ------------------------------------------------------------ Ergebnis

    def fertig(self) -> bool:
        return self.naechste() is None

    def geschaetzt_gesamt(self) -> int:
        """Wie viele Aufgaben es insgesamt etwa werden — für den Balken.

        Eine Schätzung, keine feste Zahl: der Test entscheidet unterwegs, wie
        weit er geht. Der Balken darf darum nie rückwärts laufen, deshalb das
        Maximum aus «schon gestellt + 1» und der Schätzung.
        """
        rest = len([n for n in self.warteschlange if n not in self.erledigt])
        if self.phase == "anker":
            rest += max(0, ANKER_SONDEN - self.anker)
        rest += len(self.fein)
        grenze = GRENZE.get(max(0, min(3, self.niveau)), MAX_AUFGABEN)
        return max(self.gestellt + 1, min(grenze, self.gestellt + rest))

    def startpunkt(self) -> str | None:
        """Die erste Lektion, die dieser Schüler wirklich zu sehen bekommt.

        NICHT die kleinste offene Nummer im Netz: davon haben rund neunzig
        noch keinen Generator, und die App überspringt sie beim Üben ohnehin.
        Stünde diese Nummer auf der Ergebnisseite, läse ein Gymnasiast dort
        «du beginnst bei: Zahlen auf der Zahlengeraden» — und würde der
        Einstufung zu Recht misstrauen.
        """
        plan = self.plan()
        if plan:
            return plan[0]["lektion"]
        return naechste_lektion(self.sicher)

    def plan(self) -> list[dict]:
        """Der persönliche Plan: welche Lektion auf welchem Level.

        Nur Lektionen mit Generator — was nicht geübt werden kann, gehört
        nicht in einen Plan. Reihenfolge ist die Netzreihenfolge.
        """
        # Stränge, für die das Budget nicht mehr reichte, bekommen KEINE
        # Gutschrift — aber auch nicht stur Level A. Wer sich im Test als
        # stark gezeigt hat, steigt dort auf B ein. Sonst übt ein
        # Gymnasiast vier Wochen lang Aufgaben, die er im Schlaf löst, und
        # die Studie misst nichts.
        ungeprueft = {l for s in self._straenge if s.nr not in self.erledigt
                      for l in s.lektionen}
        vorgabe = "B" if self.niveau >= 2 else "A"
        raus = []
        for lektion in sorted(set(SCHABLONE_FUER), key=_num):
            if lektion in self.sicher:
                continue
            level = self.einstiegslevel.get(
                lektion, vorgabe if lektion in ungeprueft else "A")
            if lektion in self.gescheitert:
                grund = "im Test nicht gelöst"
            elif lektion in ungeprueft:
                grund = "im Test nicht geprüft"
            elif level == "A":
                grund = "noch nicht gezeigt"
            else:
                grund = f"Grundform sitzt — Einstieg auf {level}"
            raus.append({"lektion": lektion,
                         "name": KLARTEXT.get(lektion, lektion),
                         "level": level, "grund": grund, "art": "pflicht"})
        return raus

    def plan_kontrolle(self) -> list[dict]:
        """Die Kontrollrunde: sitzt, aber nicht auf der Stufe, die zählt.

        Für den Gymnasiasten ist DAS der eigentliche Vierwochenplan. Er hat
        keine zwanzig offenen Lektionen — er hat fünfzig, die er im Test nur
        mittelbar gutgeschrieben bekam. Die Kontrollrunde auf Level C geht
        schnell, wo es sitzt, und bleibt genau an der Bauform stehen, wo
        nicht. Das ist die Lückensuche, die ein Test mit dreissig Aufgaben
        nicht leisten kann: sie braucht mehr Aufgaben, aber sie kostet keine
        eigene Zeit, weil sie das Üben selbst ist.
        """
        return [{"lektion": l, "name": KLARTEXT.get(l, l), "level": lv,
                 "grund": "gutgeschrieben, aber nie selbst gelöst",
                 "art": "kontrolle"}
                for l, lv in sorted(self.kontrolle.items(), key=lambda p: _num(p[0]))
                if l in self.sicher and l in SCHABLONE_FUER]

    def plan_kapitel(self) -> list[dict]:
        """Derselbe Plan, aber je Schablone zusammengefasst.

        Dreissig Zeilen liest niemand. Acht schon.
        """
        gruppen: dict[str, dict] = {}
        for eintrag in self.plan():
            kap = SCHABLONE_FUER.get(eintrag["lektion"])
            if kap is None:
                continue
            g = gruppen.setdefault(kap, {"kapitel": kap, "lektionen": [],
                                         "level": eintrag["level"],
                                         "name": KLARTEXT.get(kap, kap)})
            g["lektionen"].append(eintrag["lektion"])
            # Das niedrigste Level im Kapitel gibt den Einstieg vor.
            if LEVELS.index(eintrag["level"]) < LEVELS.index(g["level"]):
                g["level"] = eintrag["level"]
        for g in gruppen.values():
            g["anzahl"] = len(g["lektionen"])
            g["von_bis"] = (f"{g['lektionen'][0]} – {g['lektionen'][-1]}"
                            if len(g["lektionen"]) > 1 else g["lektionen"][0])
        return sorted(gruppen.values(), key=lambda g: _num(g["kapitel"]))

    def luecken(self) -> list[dict]:
        """Die Stellen, an denen der Test wirklich etwas gefunden hat.

        Für den Fortgeschrittenen ist das die eigentliche Ausbeute des Tests:
        nicht «du bist bei 92 Prozent», sondern «diese vier Sachen fehlen».
        """
        return [{"lektion": l, "name": KLARTEXT.get(l, l),
                 "level": self.einstiegslevel.get(l, "A")}
                for l in sorted(self.gescheitert, key=_num)]

    def profil(self) -> str:
        """Ein Wort für die Rückmeldung — und für die Auswertung der Studie."""
        p = self._prozent_uebbar()
        if p >= 85:
            return "fortgeschritten"
        if p >= 55:
            return "solide"
        if p >= 25:
            return "im Aufbau"
        return "am Anfang"

    def bericht(self) -> dict:
        ziel = zielmenge()
        g = len(ziel & self.sicher)
        plan = self.plan()
        start = self.startpunkt()
        return {
            "gestellt": self.gestellt,
            "sicher": sorted(self.sicher, key=_num),
            "sicher_anzahl": g,
            "ziel_anzahl": len(ziel),
            "prozent": int(g / len(ziel) * 100) if ziel else 0,
            "prozent_uebbar": self._prozent_uebbar(),
            "uebbar_anzahl": len(set(SCHABLONE_FUER)),
            "uebbar_sicher": len(set(SCHABLONE_FUER) & self.sicher),
            "start": start,
            "start_name": KLARTEXT.get(start, start or "—"),
            "noch_offen": len(ziel) - g,
            "einstiegslevel": self.einstiegslevel,
            "start_level": (plan[0]["level"] if plan
                            else self.einstiegslevel.get(start, "A")),
            "niveau": self.niveau,
            "profil": self.profil(),
            "plan": plan,
            "kontrolle": self.plan_kontrolle(),
            "kontrolle_laenge": len(self.plan_kontrolle()),
            "plan_kapitel": self.plan_kapitel(),
            "plan_laenge": len(plan),
            "luecken": self.luecken(),
            "richtig": sum(1 for _, _, r in self.protokoll if r),
            "protokoll": [{"lektion": l, "name": KLARTEXT.get(l, l),
                           "level": lv, "richtig": r}
                          for l, lv, r in self.protokoll],
        }

    # ------------------------------------------------------------ Session

    def als_dict(self) -> dict:
        return {"sicher": sorted(self.sicher), "gescheitert": sorted(self.gescheitert),
                "gestellt": self.gestellt, "einstiegslevel": self.einstiegslevel,
                "niveau": self.niveau, "phase": self.phase, "lo": self.lo,
                "hi": self.hi, "anker": self.anker,
                "warteschlange": self.warteschlange, "erledigt": self.erledigt,
                "aktuell": self.aktuell, "protokoll": self.protokoll,
                "geprueft": sorted(self.geprueft),
                "rueckwaerts": sorted(self.rueckwaerts), "fein": self.fein,
                "abstieg": self.abstieg, "folgefehler": self.folgefehler,
                "streu": self.streu, "kontrolle": self.kontrolle}

    @classmethod
    def aus_dict(cls, d: dict) -> "Einstufung":
        if not d:
            return cls()
        return cls(sicher=set(d.get("sicher", ())),
                   gescheitert=set(d.get("gescheitert", ())),
                   gestellt=d.get("gestellt", 0),
                   einstiegslevel=d.get("einstiegslevel"),
                   niveau=d.get("niveau", NIVEAU_START),
                   phase=d.get("phase", "anker"),
                   lo=d.get("lo", 0), hi=d.get("hi", -1),
                   anker=d.get("anker", 0),
                   warteschlange=d.get("warteschlange"),
                   erledigt=d.get("erledigt"),
                   aktuell=d.get("aktuell"),
                   protokoll=d.get("protokoll"),
                   geprueft=d.get("geprueft"),
                   rueckwaerts=d.get("rueckwaerts"),
                   fein=d.get("fein"),
                   abstieg=d.get("abstieg"),
                   folgefehler=d.get("folgefehler", 0),
                   streu=d.get("streu"),
                   kontrolle=d.get("kontrolle"))


#: Bleibt erhalten, damit älterer Code, der die Liste importiert, weiterläuft.
LEITAUFGABEN = [s.mitte for s in straenge()]
LEIT_LEVEL = "B"
