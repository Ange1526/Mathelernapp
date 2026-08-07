from flask import (Flask, render_template, redirect, url_for, flash,
                   request, session, g)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, date
import json
import os
import random
import secrets

from korrektur import auswerten, aufgabe_aus_generator, Status
from generator.anbindung import (KAPITEL, KAPITEL_NAMEN, MISCHEN,
                                 aufgabe_aus_session, kernidee,
                                 mischen_moeglich, neue_aufgabe)
from generator import theorie as theorie_modul
from generator.lernstand import (LEVELS, MASTERY, Ziehung, bewerten,
                                 fortschritt, naechstes_level, vorheriges_level)
from generator.netz import (ALLE, KLARTEXT, SCHABLONE_FUER, ZIEL,
                            erhebung_abgedeckt, naechste_lektion, restaufwand,
                            rueckwaerts_gutschreiben, rueckwaerts_zu,
                            voraussetzungen, zielmenge)
from generator.netz import fortschritt as netz_fortschritt
from generator.einstufung import Einstufung
from generator.vertiefung import (LEVEL_C, MISCHAUFGABEN, MODI, PROBE_ERHEBUNG,
                                  SCHWACHSTELLEN, BESCHREIBUNG, Probelauf,
                                  TITEL as VTITEL, naechster_modus,
                                  schwachstellen)

app = Flask(__name__)

# ── Konfiguration ──────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-matura-2024")

# Abgestorbene Datenbankverbindungen erkennen, bevor sie benutzt werden.
# Gratis-Datenbanken trennen Verbindungen nach kurzer Ruhe; die App merkt es
# sonst erst mitten in einer Abfrage und stirbt mit «SSL error: decryption
# failed or bad record mac». `pool_pre_ping` schickt vorher ein winziges
# Signal und baut bei Bedarf still eine neue Verbindung auf — das kostet
# weniger als eine Millisekunde und erspart genau diesen Absturz.
# Nach einem `commit()` wirft SQLAlchemy standardmaessig ALLE geladenen
# Objekte weg — beim naechsten Zugriff wird jedes einzeln neu geholt.
# Gemessen an einer abgeschickten Antwort: 35 Datenbankabfragen, davon
# ACHT allein fuer den angemeldeten Benutzer, weil zwischendurch mehrmals
# gespeichert wird.
#
# Lokal faellt das nicht auf (SQLite liegt auf derselben Platte). Auf einem
# Server mit einer Datenbank in einem anderen Rechenzentrum kostet jede
# Abfrage dreissig bis hundert Millisekunden — dann sind es zwei Sekunden
# pro Klick, und genau darueber haben die Testpersonen sich beschwert.
#
# `expire_on_commit=False` laesst die Objekte nach dem Speichern gueltig.
# Der Preis: liest jemand ANDERES gleichzeitig denselben Datensatz und
# aendert ihn, sieht man den alten Stand bis zum Ende der Anfrage. Bei
# einer Lern-App, in der jeder nur seine eigenen Daten anfasst, ist das
# folgenlos.
#: Wird unten beim Anlegen der Erweiterung uebergeben.
SITZUNG = {"expire_on_commit": False}

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,        # Verbindungen vor dem Ablauf selbst erneuern
}

database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, session_options=SITZUNG)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ── Konstanten ─────────────────────────────────────────────────────────────────
MIN_QUESTIONS   = 10    # Mindestanzahl Aufgaben vor Levelwechsel
RATE_UP         = 0.80  # >= 80% korrekt → Aufstieg
RATE_DOWN       = 0.60  # <  60% korrekt → Abstieg
CONSECUTIVE_ERR = 2     # Fehler in Folge → Theorie-Hinweis
MAX_TRIES       = 3     # Versuche an derselben Aufgabe, danach Lösung zeigen
RESET_MINUTES   = 60    # Gültigkeit des Passwort-Links in Minuten

# Kapitelnamen (fuer die Uebersicht der markierten Aufgaben)
CHAPTER_NAMES = {
    "1.3": "Addition",
    "1.4": "Subtraktion",
    "1.5": "Addition gemischt",
    "1.6": "Addition negativ",
    "1.7": "Subtraktion negativ",
}
CHAPTER_NAMES.update(KAPITEL_NAMEN)

# Obertitel der 16 Kapitel — steht ueber den Lektionskarten im Dashboard.
KAPITEL_TITEL = {
    "1":  "Zahlen und Vorzeichen",
    "2":  "Brüche",
    "3":  "Variablen und Terme",
    "4":  "Gleichartige Terme",
    "5":  "Multiplikation von Termen",
    "6":  "Gemischte Operationen",
    "7":  "Potenzen",
    "8":  "Wurzeln",
    "9":  "Division von Termen",
    "10": "Klammern",
    "11": "Distributivgesetz",
    "12": "Faktorisieren",
    "13": "Gleichungen",
    "14": "Bruchterme",
    "15": "Bruchgleichungen",
    "16": "Vermischtes",
}

# Hinweistext pro Kapitel, erscheint nach einer falschen Antwort
HINTS = {
    "1.3": ("Schau dir die Vorzeichen genau an.<br>"
            "Beispiel: <strong>3 + (−5)</strong> bedeutet, du gehst von 3 um 5 "
            "nach links → Ergebnis: <strong>−2</strong><br>"
            "<em>Merksatz: Plus und Minus ergibt Minus.</em>"),
    "1.4": ("Minus vor der Klammer dreht das Vorzeichen um.<br>"
            "Beispiel: <strong>4 − (−6)</strong> wird zu <strong>4 + 6 = 10</strong><br>"
            "<em>Merksatz: Minus und Minus ergibt Plus.</em>"),
    "1.5": ("Rechne Schritt für Schritt von links nach rechts.<br>"
            "Beispiel: <strong>2 + (−7) + 3</strong> → zuerst 2 + (−7) = −5, "
            "dann −5 + 3 = <strong>−2</strong>"),
    "1.6": ("Zwei negative Zahlen addieren heisst: beide gehen nach links.<br>"
            "Beispiel: <strong>−4 + (−3)</strong> = <strong>−7</strong><br>"
            "<em>Die Beträge werden addiert, das Vorzeichen bleibt negativ.</em>"),
    "1.7": ("Wandle die Subtraktion zuerst in eine Addition um.<br>"
            "Beispiel: <strong>−5 − (−8)</strong> wird zu <strong>−5 + 8 = 3</strong>"),
}


def get_hint(chapter):
    """Bei Generatorkapiteln kommt der Tipp aus der Schablone — er passt damit
    zur konkreten Bauform, nicht nur zum Kapitel."""
    if chapter in KAPITEL:
        tipps = (aufgabe_laden() or {}).get("tipps") or []
        if len(tipps) >= 2:
            return tipps[1]
    return HINTS.get(chapter, HINTS["1.3"])

# ── Modelle ────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(80),  unique=True, nullable=False)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    password_hash   = db.Column(db.String(256), nullable=False)
    xp              = db.Column(db.Integer, default=0)
    current_level   = db.Column(db.String(1),  default="A")   # Start immer auf A
    current_chapter = db.Column(db.String(10), default="1.3")

    # ── Taegliche Serie (die Flamme im Header) ────────────────────────────────
    # streak      = Anzahl Tage hintereinander, an denen geuebt wurde
    # last_active = der letzte Tag, an dem eine Antwort abgeschickt wurde
    # bester_streak bleibt stehen, auch wenn die Serie reisst — sonst waere ein
    # einziger verpasster Tag ein Totalverlust, und das entmutigt.
    streak          = db.Column(db.Integer, default=0)
    bester_streak   = db.Column(db.Integer, default=0)
    last_active     = db.Column(db.Date)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Progress(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    chapter         = db.Column(db.String(10))
    level           = db.Column(db.String(1))
    correct_cnt     = db.Column(db.Integer, default=0)
    total_cnt       = db.Column(db.Integer, default=0)
    consecutive_err = db.Column(db.Integer, default=0)  # Fehler in Folge

class TaskAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    chapter = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(1), nullable=False)

    question = db.Column(db.String(255), nullable=False)

    # Text statt Float: Loesungen sind neu auch Brueche und Terme
    correct_solution = db.Column(db.String(255), nullable=False)

    # Rohtext der Schuelerin, unveraendert. Das ist das Studienmaterial --
    # daraus werden spaeter die Fehlerkataloge nachgeschaerft.
    user_answer = db.Column(db.String(255), nullable=False)

    correct = db.Column(db.Boolean, nullable=False)

    # richtig | unfertig | falsch | eingabefehler | zeitlimit
    status = db.Column(db.String(20))

    # None | Katalogschluessel | "unbekannt"
    # Nur "unbekannt" geht spaeter an den KI-Fallback.
    fehlerschluessel = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BauformStand(db.Model):
    """FEHLER 1 · Mastery pro Bauform statt Quote über die Lektion.

    Bisher entschied «10 Aufgaben, 80 % richtig» über den Aufstieg. Damit
    konnte jemand aufsteigen, der ausgerechnet eine Aufgabenart nie beherrscht
    hat — die Lücke blieb bis zur Prüfung bestehen.

    Neu hat jede Bauform ihr eigenes Häkchen. Das Level gilt erst als fertig,
    wenn alle Bauformen sitzen. Wer eine nicht kann, bekommt genau die wieder —
    nicht irgendeine.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    chapter = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(1), nullable=False)
    bauform = db.Column(db.String(10), nullable=False)

    treffer = db.Column(db.Integer, default=0)      # richtige Antworten in Folge
    fehler = db.Column(db.Integer, default=0)       # Fehlversuche insgesamt
    gemeistert = db.Column(db.Boolean, default=False)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class KapitelStand(db.Model):
    """FEHLER 2 · Ein Level pro Kapitel statt eines pro Schüler.

    `User.current_level` galt für alles. Wer bei Brüchen schwach und beim
    Faktorisieren stark ist, bekam für beides dasselbe Niveau — einmal
    Überforderung, einmal Langeweile.

    `User.current_level` bleibt bestehen (die alten Kapitel benutzen es
    weiter), wird für Generatorkapitel aber nicht mehr gelesen.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    chapter = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(1), default="A")
    abgeschlossen = db.Column(db.Boolean, default=False)

    #: Reihenfolge der noch nicht gezogenen Bauformen dieser Runde, als Text.
    #: Muss gespeichert werden, sonst stimmt die Reihum-Ziehung nach einer
    #: Unterbrechung nicht mehr.
    offen = db.Column(db.String(255), default="")

    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class EinstufungsStand(db.Model):
    """Der Zwischenstand des Einstufungstests — in der DATENBANK, nicht im Cookie.

    WARUM: Flask legt die ganze Session in ein signiertes Cookie, und Browser
    werfen Cookies ueber rund 4096 Zeichen weg. Der Einstufungsstand waechst
    mit jeder Aufgabe; gemessen: 867 Zeichen zu Beginn, 4296 nach dreissig
    Aufgaben. Beim Ueberlaufen verschwindet die GANZE Session — der Schueler
    ist ausgeloggt, der Test weg, die Ergebnisseite nie gesehen. Genau das
    haben die Testpersonen gemeldet: «stuerzt nach dem Starttest ab, danach
    muss man sich neu anmelden, und den Plan sieht man nie».

    Mit 48 statt 30 Aufgaben trifft es fast jeden. Im Cookie steht jetzt nur
    noch ein Verweis; die Daten liegen hier und koennen beliebig wachsen.
    """
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    daten   = db.Column(db.Text, default="")
    #: Die aktuell gestellte Aufgabe. Sie steckte ebenfalls im Cookie und
    #: macht allein rund 2000 Zeichen aus — zusammen mit dem Einstufungsstand
    #: reichte das zum Ueberlauf. Hier ist Platz.
    aufgabe = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Lernweg(db.Model):
    """Der persoenliche Weg EINES Schuelers durch das Netz.

    Der Schueler waehlt kein Kapitel mehr. Nach dem Einstufungstest sagt die
    App bei jedem Oeffnen, was jetzt dran ist — vorwaerts, wenn eine Lektion
    sitzt, rueckwaerts zu genau der Voraussetzung, auf die ein Fehler deutet.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)

    #: Lektionen, die als sicher gelten — kommagetrennt, z.B. "1.9,1.19,3.11"
    sicher = db.Column(db.Text, default="")

    #: Woran er gerade arbeitet
    aktuelle_lektion = db.Column(db.String(10))

    #: Wohin er zurueckkehrt, wenn die Luecke geschlossen ist
    zurueck_zu = db.Column(db.String(10))

    #: Lektionen, die uebersprungen wurden, WEIL es noch keinen Generator gibt.
    #: Sie gelten NICHT als sicher — sonst waere die Lueckenfreiheit eine Luege.
    #: Sobald der Generator da ist, fallen sie in den Weg zurueck.
    uebersprungen = db.Column(db.Text, default="")

    eingestuft = db.Column(db.Boolean, default=False)

    #: Ist der Weg durch? Dann laeuft die Vertiefung.
    durchgelaufen = db.Column(db.Boolean, default=False)
    probe_gemacht = db.Column(db.Boolean, default=False)
    probe_quote = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def sichere_menge(self):
        return {l for l in (self.sicher or "").split(",") if l}

    def setze_sicher(self, menge):
        self.sicher = ",".join(sorted(menge))

    def uebersprungene_menge(self):
        return {l for l in (self.uebersprungen or "").split(",") if l}

    def merke_uebersprungen(self, lektion):
        m = self.uebersprungene_menge()
        m.add(lektion)
        self.uebersprungen = ",".join(sorted(m))

    def uebersprungene_aufraeumen(self) -> set:
        """Lektionen aus der Uebersprungen-Liste holen, die es jetzt gibt.

        WARUM DAS NOETIG IST: «uebersprungen» merkt sich, wo die App keine
        Aufgaben hatte. Sobald ein Generator dazukommt, ist der Eintrag
        falsch — die Lektion bliebe fuer immer grau.

        WARUM DAS NICHT REICHT: Wer die Lektion damals uebersprungen hat,
        ist inzwischen weitergekommen. Nimmt man sie einfach aus der Liste,
        gilt sie weder als sicher noch als uebersprungen — und die App
        schickt einen Schueler, der schon bei Kapitel 5 stand, zurueck auf
        Lektion 1.1. Genau das ist passiert, als Kapitel 1 und 2 fertig
        wurden.

        Darum: was VOR der aktuellen Stelle liegt, wird gutgeschrieben. Der
        Schueler hat es nicht uebersprungen, die App hatte damals nichts
        anzubieten. Was DAHINTER liegt, wird zu einer normalen offenen
        Lektion und kommt der Reihe nach dran.
        """
        alt = self.uebersprungene_menge()
        befreit = {l for l in alt if kapitel_fuer_lektion(l)}
        if not befreit:
            return set()

        self.uebersprungen = ",".join(sorted(alt - befreit))

        # Alles vor der aktuellen Stelle gutschreiben.
        def nummer(lektion):
            teile = lektion.split(".")
            return (int(teile[0]), int(teile[1]) if len(teile) > 1 else 0)

        stand = self.aktuelle_lektion
        if stand:
            grenze = nummer(stand)
            davor = {l for l in befreit if nummer(l) < grenze}
            if davor:
                self.setze_sicher(self.sichere_menge() | davor)

        return befreit


class MarkedTask(db.Model):
    """Aufgabe, die der Lernende spaeter mit der Lehrperson anschauen will."""
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    chapter = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(1))

    question = db.Column(db.String(255), nullable=False)
    solution = db.Column(db.Float)
    note = db.Column(db.String(500))

    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordReset(db.Model):
    """Einmal-Token zum Zuruecksetzen des Passworts."""
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    @property
    def is_valid(self):
        return (not self.used) and datetime.utcnow() < self.expires_at


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_generator_kapitel():
    """Damit das Template weiss, ob der Balken Aufgaben oder Aufgabenarten zaehlt."""
    return {"generator_kapitel": set(KAPITEL)}


def streak_aktualisieren():
    """Die Flamme im Header: Tage hintereinander, an denen geuebt wurde.

    Wird bei jeder abgeschickten Antwort gerufen. Massgebend ist der Tag,
    nicht die Aufgabenzahl — eine einzige Aufgabe haelt die Serie am Leben.
    Das ist Absicht: die Huerde soll klein sein.

    - gleicher Tag        -> nichts aendert sich
    - gestern zuletzt     -> Serie waechst um eins
    - laenger her (oder nie) -> Serie beginnt neu bei eins
    """
    heute = date.today()
    letzter = current_user.last_active

    if letzter == heute:
        return

    if letzter == heute - timedelta(days=1):
        current_user.streak = (current_user.streak or 0) + 1
    else:
        current_user.streak = 1

    current_user.last_active = heute
    if (current_user.streak or 0) > (current_user.bester_streak or 0):
        current_user.bester_streak = current_user.streak


@app.context_processor
def inject_streak():
    """Die Flamme zeigt 0, sobald ein Tag ausgelassen wurde.

    Ohne das wuerde die alte Zahl stehen bleiben, bis wieder geuebt wird —
    die Serie waere dann laenger, als sie ist.
    """
    if not current_user.is_authenticated:
        return {"streak_aktuell": 0}

    heute = date.today()
    letzter = current_user.last_active
    if letzter in (heute, heute - timedelta(days=1)):
        aktuell = current_user.streak or 0
    else:
        aktuell = 0
    return {"streak_aktuell": aktuell,
            "streak_heute": letzter == heute,
            "streak_bester": current_user.bester_streak or 0}


@app.context_processor
def inject_marked_count():
    """Anzahl offener Fragen, damit sie im Header/Dashboard angezeigt werden kann."""
    if current_user.is_authenticated:
        anzahl = MarkedTask.query.filter_by(
            user_id=current_user.id, resolved=False
        ).count()
    else:
        anzahl = 0
    return {"offene_fragen": anzahl}


# ── Aufgabengenerierung ────────────────────────────────────────────────────────
def generate_math_task(chapter, level):
    """
    Gibt (frage_string, loesung_float) zurück.
    Level A: kleine Zahlen (±10)
    Level B: mittlere Zahlen (±50)
    Level C: grössere Zahlen (±100) / mehr Operanden
    """
    if level == "A":
        span = 10
    elif level == "B":
        span = 50
    else:
        span = 100

    a = random.randint(-span, span)
    b = random.randint(-span, span)

    if chapter == "1.3":
        # Addition
        if level == "C":
            c = random.randint(1, 20)
            return f"{a} + ({b}) + ({c})", float(a + b + c)
        return f"{a} + ({b})", float(a + b)

    # Standardfall: Subtraktion (z.B. Kapitel 1.4)
    return f"{a} - ({b})", float(a - b)


def neue_aufgabe_fuer(chapter, level, bauform=None):
    """Aufgabe als Session-Dictionary — mitsamt Zielform und Fehlerkatalog.

    Ohne die beiden koennte check() eine Faktorisieraufgabe nicht auf ihre
    Form pruefen und wuerde 2az + 3a durchwinken, wo a(2z + 3) verlangt ist.
    """
    if chapter in KAPITEL:
        return neue_aufgabe(chapter, level, bauform)
    frage, loesung = generate_math_task(chapter, level)
    return {"schablone": chapter, "bauform": "-", "level": level,
            "anleitung": "Loese die Aufgabe", "frage": frage,
            "loesung": str(loesung), "loesung_text": fmt_zahl(loesung),
            "zielform": "beliebig", "fehler": [], "tipps": [], "schritte": []}


# ── Der persoenliche Weg ──────────────────────────────────────────────────────

def _stand_datensatz():
    """Der Datensatz des Benutzers — einmal je Anfrage geholt, dann gemerkt.

    Zwischenstand und aktuelle Aufgabe liegen im selben Datensatz. Er wurde
    pro Anfrage bis zu fuenfmal frisch geholt, weil jede Hilfsfunktion ihre
    eigene Abfrage machte. Auf einer entfernten Datenbank sind das fuenf
    Rundreisen statt einer.

    `g` ist Flasks Ablage fuer die Dauer EINER Anfrage — danach ist sie
    wieder leer, es kann also nichts zwischen Benutzern verwechselt werden.
    """
    if not hasattr(g, "_stand"):
        g._stand = EinstufungsStand.query.filter_by(
            user_id=current_user.id).first()
    return g._stand


def einstufung_laden():
    """Zwischenstand aus der Datenbank holen — leeres Dict, wenn keiner da."""
    st = _stand_datensatz()
    if not st or not st.daten:
        return {}
    try:
        return json.loads(st.daten)
    except Exception:                                  # noqa: BLE001
        return {}


def einstufung_speichern(daten):
    st = _stand_datensatz()
    if not st:
        st = EinstufungsStand(user_id=current_user.id)
        db.session.add(st)
        g._stand = st
    st.daten = json.dumps(daten)
    st.updated_at = datetime.utcnow()
    db.session.commit()


def aufgabe_laden():
    """Die gestellte Aufgabe aus der Datenbank."""
    st = _stand_datensatz()
    if not st or not st.aufgabe:
        return None
    try:
        return json.loads(st.aufgabe)
    except Exception:                                  # noqa: BLE001
        return None


def aufgabe_speichern(daten):
    st = _stand_datensatz()
    if not st:
        st = EinstufungsStand(user_id=current_user.id)
        db.session.add(st)
        g._stand = st
    st.aufgabe = json.dumps(daten) if daten else ""
    st.updated_at = datetime.utcnow()
    db.session.commit()


def einstufung_loeschen():
    EinstufungsStand.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    if hasattr(g, "_stand"):
        del g._stand


def lernweg():
    lw = Lernweg.query.filter_by(user_id=current_user.id).first()
    if not lw:
        lw = Lernweg(user_id=current_user.id, sicher="", eingestuft=False)
        db.session.add(lw)
        db.session.commit()
    return lw


def lektion_fertig_melden(lw, lektion):
    """Lektion sitzt: gutschreiben und schauen, was als Naechstes kommt."""
    menge = lw.sichere_menge()
    menge.add(lektion)
    lw.setze_sicher(menge)
    # Wenn er wegen einer Luecke hier war, geht es zurueck zur urspruenglichen
    # Lektion — nicht irgendwohin.
    if lw.zurueck_zu:
        ziel, lw.zurueck_zu = lw.zurueck_zu, None
        lw.aktuelle_lektion = ziel
    else:
        lw.aktuelle_lektion = naechste_lektion(
            lw.sichere_menge() | lw.uebersprungene_menge())
    lw.updated_at = datetime.utcnow()
    db.session.commit()


def zurueckspringen(lw, ziel_lektion):
    """Ein Fehler zeigt, dass etwas darunter fehlt. Genau dorthin."""
    if lw.zurueck_zu is None:
        lw.zurueck_zu = lw.aktuelle_lektion
    lw.aktuelle_lektion = ziel_lektion
    lw.updated_at = datetime.utcnow()
    db.session.commit()


def kapitel_fuer_lektion(lektion):
    """Welche Schablone uebt diese Lektion? None = noch kein Generator da."""
    return SCHABLONE_FUER.get(lektion)


# ── Lernstand: Level pro Kapitel, Mastery pro Bauform ─────────────────────────

def kapitel_stand(chapter):
    """Der Stand DIESES Schülers in DIESEM Kapitel."""
    ks = KapitelStand.query.filter_by(user_id=current_user.id, chapter=chapter).first()
    if not ks:
        ks = KapitelStand(user_id=current_user.id, chapter=chapter, level="A", offen="")
        db.session.add(ks)
        db.session.commit()
    return ks


def aktuelles_level(chapter):
    """FEHLER 2 · Generatorkapitel haben ihr eigenes Level."""
    if chapter in KAPITEL:
        return kapitel_stand(chapter).level
    return current_user.current_level


def _bauform_staende(chapter, level):
    """Alle Bauformstaende eines Kapitels und Levels — EINE Abfrage.

    `bauform_stand()` holte jeden Stand einzeln. Beim Pruefen einer Antwort
    wurde die Tabelle darum fuenfmal befragt, obwohl eine Abfrage alles
    liefert. Auf einer entfernten Datenbank sind das vier Rundreisen zu viel.
    """
    if not hasattr(g, "_bfs"):
        g._bfs = {}
    schluessel = (chapter, level)
    if schluessel not in g._bfs:
        g._bfs[schluessel] = {
            b.bauform: b for b in BauformStand.query
            .filter_by(user_id=current_user.id, chapter=chapter, level=level)
            .order_by(BauformStand.id)}
    return g._bfs[schluessel]


def bauform_stand(chapter, level, bauform):
    """Der Zaehlerstand einer Bauform — genau EIN Datensatz je Kombination.

    WARUM DAS `flush()` NOETIG IST: `db.session.add()` schreibt noch nichts in
    die Datenbank. Die naechste `query.filter_by(...)` sucht dort, findet
    nichts, und legt einen ZWEITEN Datensatz an. So entstanden Paare wie
    (BF10, treffer 1) und (BF10, treffer 2) nebeneinander — und im schlimmsten
    Fall zaehlt keiner je bis zwei, weil jede richtige Antwort eine neue Zeile
    mit treffer 1 anlegt. Fuer den Schueler sieht das aus, als bewege sich der
    Fortschritt nicht, egal wie viel er loest.

    `flush()` schiebt den neuen Datensatz in die laufende Transaktion, ohne
    sie abzuschliessen. Die naechste Abfrage findet ihn dann.
    """
    bs = _bauform_staende(chapter, level).get(bauform)
    if not bs:
        bs = BauformStand(user_id=current_user.id, chapter=chapter, level=level,
                          bauform=bauform, treffer=0, fehler=0, gemeistert=False)
        db.session.add(bs)
        db.session.flush()
        _bauform_staende(chapter, level)[bauform] = bs
    return bs


def bereit_zum_ueben(lektion, sicher, lw) -> bool:
    """Darf diese Lektion jetzt geuebt werden?

    Nur wenn sie einen Generator hat und ihre Voraussetzungen sitzen —
    sonst schickt die App den Schueler auf eine Seite, die er nicht loesen
    kann, und das ist schlimmer als ein Umweg ueber die Grundlagen.
    """
    if not kapitel_fuer_lektion(lektion):
        return False
    bekannt = set(sicher) | lw.uebersprungene_menge()
    return all(v in bekannt for v in voraussetzungen(lektion))


def doppelte_bauformen_zusammenlegen():
    """Raeumt die Doppeleintraege auf, die vor dem flush()-Fix entstanden sind.

    Wer die App vorher benutzt hat, hat pro Bauform mehrere Datensaetze in der
    Datenbank. Der Fortschritt bleibt dann stehen, obwohl richtig geloest
    wird. Beim Oeffnen der Lernreise werden sie einmalig zusammengelegt: der
    hoechste Trefferstand gewinnt, gemeistert bleibt gemeistert.
    """
    alle = BauformStand.query.filter_by(user_id=current_user.id).all()
    nach_schluessel = {}
    for bs in alle:
        schluessel = (bs.chapter, bs.level, bs.bauform)
        nach_schluessel.setdefault(schluessel, []).append(bs)

    geaendert = False
    for eintraege in nach_schluessel.values():
        if len(eintraege) < 2:
            continue
        eintraege.sort(key=lambda b: b.id)
        behalten = eintraege[0]
        behalten.treffer = max(e.treffer or 0 for e in eintraege)
        behalten.fehler = max(e.fehler or 0 for e in eintraege)
        behalten.gemeistert = any(e.gemeistert for e in eintraege)
        for weg in eintraege[1:]:
            db.session.delete(weg)
        geaendert = True

    if geaendert:
        db.session.commit()


def gemeisterte(chapter, level):
    return {nr for nr, b in _bauform_staende(chapter, level).items()
            if b.gemeistert}


def alle_bauformen(chapter, level):
    schablone = KAPITEL[chapter]
    return [b.nr for b in schablone.bauformen_fuer(level)]


def naechste_bauform(chapter, level):
    """FEHLER 1 · Reihum ziehen, gemeisterte überspringen."""
    ks = kapitel_stand(chapter)
    alle = alle_bauformen(chapter, level)
    offen = [b for b in (ks.offen or "").split(",") if b]
    z = Ziehung(alle, gemeisterte(chapter, level), offen)
    nr = z.naechste()
    ks.offen = ",".join(z.offen)
    db.session.commit()
    return nr


# ── Hilfsfunktion: Progress laden oder erstellen ───────────────────────────────
def get_or_create_progress(user_id, chapter, level):
    prog = Progress.query.filter_by(
        user_id=user_id, chapter=chapter, level=level
    ).first()
    if not prog:
        prog = Progress(
            user_id=user_id,
            chapter=chapter,
            level=level,
            correct_cnt=0,
            total_cnt=0,
            consecutive_err=0,
        )
        db.session.add(prog)
    # Sicherheitsnetz: None-Werte korrigieren
    if prog.correct_cnt     is None: prog.correct_cnt     = 0
    if prog.total_cnt       is None: prog.total_cnt       = 0
    if prog.consecutive_err is None: prog.consecutive_err = 0
    return prog


def reset_progress(prog):
    prog.correct_cnt     = 0
    prog.total_cnt       = 0
    prog.consecutive_err = 0
    # Bei Levelwechsel passt die alte Aufgabe nicht mehr zur Schwierigkeit
    session["task_open"]  = False
    session["last_wrong"] = False
    session["task_tries"] = 0


# ── Routen ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    lw = lernweg()

    # Wer noch nie eingestuft wurde, gehoert zuerst in den Einstufungstest.
    # Ohne diese Zeile landet ein frisch angemeldeter Schueler direkt auf der
    # Lernreise: der Test wird nie angeboten, der Lernweg bleibt leer, und
    # Kacheln wie «Gemischte Aufgaben» tauchen gar nicht erst auf, weil noch
    # keine Lektion als sicher gilt. /start leitet von hier korrekt weiter.
    if not lw.eingestuft:
        return redirect(url_for("start"))

    doppelte_bauformen_zusammenlegen()

    # Neue Generatoren freischalten, bevor die Kacheln gebaut werden.
    # BEWUSST OHNE MELDUNG: fuer den Lernenden ist es keine Nachricht, dass
    # eine Lektion jetzt Aufgaben hat — sie ist einfach da. Eine Liste von
    # Nummern oben auf der Lernreise ist Entwicklerinformation und stoert.
    if lw.uebersprungene_aufraeumen():
        db.session.commit()

    prog_rows = Progress.query.filter_by(user_id=current_user.id).all()
    progress_map = {p.chapter: p for p in prog_rows}
    sicher = lw.sichere_menge()
    uebersprungen = lw.uebersprungene_menge()
    bekannt = sicher | uebersprungen

    # ── Alle Lektionen, nach Kapiteln gruppiert ─────────────────────────────
    # Sichtbar ist alles. Anklickbar nur, was freigeschaltet ist: eine Lektion
    # ist frei, wenn alle ihre Voraussetzungen sitzen. Der Rest bleibt
    # ausgegraut mit Schloss — sichtbar, damit der Weg als Ganzes erkennbar
    # bleibt, aber nicht anklickbar, damit niemand Lueckenspringt.
    kapitel_liste = []
    for knr in sorted({l.split(".")[0] for l in ALLE}, key=int):
        lektionen = [l for l in ALLE if l.split(".")[0] == knr]
        eintraege = []
        for l in lektionen:
            uebbar = kapitel_fuer_lektion(l)

            # Kapitel 16 sind keine Lektionen auf dem Weg, sondern die Stufe
            # darueber: Mischaufgaben und die Probe-Erhebung. Sie stehen
            # bewusst NICHT in SCHABLONE_FUER, damit sie nicht in den
            # Einstufungstest und nicht in den Fortschritt einfliessen.
            # Ohne den folgenden Zweig las man dort «noch keine Aufgaben» —
            # was nach Panne aussieht, obwohl beides laengst laeuft, nur
            # eben ueber einen eigenen Knopf.
            if l.startswith("16."):
                eintraege.append({
                    "nr": l,
                    "titel": KLARTEXT.get(l, l),
                    "zustand": "vertiefung",
                    "kapitel": uebbar,
                    # 16.1 geht ueber /gemischt, weil dort erst geprueft
                    # wird, ob genug Grundlagen sitzen. 16.2 fuehrt direkt
                    # zur Schablone — ueber /gemischt landete man sonst
                    # IMMER bei 16.1, und unter der Ueberschrift «Gemischte
                    # Gleichungen» stand dann eine Termvereinfachung.
                    "ziel": (url_for("probe") if l == "16.3"
                             else url_for("lektion", chapter="16.2")
                             if l == "16.2"
                             else url_for("gemischt")),
                })
                continue

            if l in sicher:
                zustand = "fertig"
            elif l == lw.aktuelle_lektion:
                zustand = "aktuell"
            elif l in uebersprungen:
                zustand = "keine_aufgaben"
            elif all(v in bekannt for v in voraussetzungen(l)):
                zustand = "frei" if uebbar else "keine_aufgaben"
            else:
                zustand = "gesperrt"
            eintraege.append({
                "nr": l,
                "titel": KLARTEXT.get(l, l),
                "zustand": zustand,
                "kapitel": uebbar,          # Kapitelnummer der Schablone oder None
            })
        kapitel_liste.append({
            "nummer": knr,
            "titel": KAPITEL_TITEL.get(knr, ""),
            "lektionen": eintraege,
            "fertig": sum(1 for e in eintraege if e["zustand"] == "fertig"),
            "gesamt": len(eintraege),
        })

    g, ges, pct = netz_fortschritt(sicher)
    rest = restaufwand(sicher)

    # ── Medaillen ────────────────────────────────────────────────────────
    # Eine je vollstaendig abgeschlossenem Kapitel. Bewusst klein gehalten:
    # eine Zahl in einem Kreis, mehr nicht. Grosse Belohnungssysteme haetten
    # bei einer Studie ueber Adaptivitaet einen Haken — man wuesste hinterher
    # nicht, ob die Anpassung gewirkt hat oder die Urkunde.
    #
    # Kapitel 16 zaehlt nicht mit: das sind die Mischaufgaben, die man nie
    # «fertig» hat.
    medaillen = [k for k in kapitel_liste
                 if k["gesamt"] > 0 and k["fertig"] == k["gesamt"]
                 and str(k["nummer"]) != "16"]

    return render_template(
        "dashboard.html",
        medaillen=medaillen,
        medaillen_gesamt=len([k for k in kapitel_liste
                              if str(k["nummer"]) != "16"]),
        progress_map=progress_map,
        kapitel_liste=kapitel_liste,
        lernweg_stand=lw,
        aktuelle_lektion=lw.aktuelle_lektion,
        aktuelle_lektion_name=KLARTEXT.get(lw.aktuelle_lektion, ""),
        sicher_anzahl=g, ziel_anzahl=ges, prozent=pct,
        rest=rest,
        gemischt_moeglich=bool(gemischte_kapitel(lw)),
    )


def gemischte_kapitel(lw):
    """Kapitel, die der Schueler schon hatte — Grundlage fuer gemischte Aufgaben.

    Nur Themen, die er bereits durchlaufen hat. Sonst waere es kein
    Wiederholen, sondern ein Vorgriff.
    """
    raus = []
    for lektion in lw.sichere_menge():
        kap = kapitel_fuer_lektion(lektion)
        if kap and kap not in raus:
            raus.append(kap)
    return raus


@app.route("/gemischt")
@login_required
def gemischt():
    """Gemischte Aufgaben ueber alles, was bisher dran war.

    Zieht reihum ueber die Kapitel, nicht zufaellig — sonst kaeme dasselbe
    Thema mehrfach hintereinander.
    """
    lw = lernweg()
    kapitel = gemischte_kapitel(lw)
    if not kapitel:
        flash("Fuer gemischte Aufgaben musst du zuerst eine Lektion abschliessen.",
              "info")
        return redirect(url_for("dashboard"))

    # ECHTE Mischaufgaben, sobald genug Grundlagen sitzen: eine Aufgabe, in
    # der zwei bis drei Kapitel gleichzeitig vorkommen. Vorher war
    # «gemischt» nur ein Reihumgehen durch die bekannten Kapitel — die
    # Aufgaben blieben Einzelteile, und genau daran scheitert man in der
    # Erhebung, die kombiniert.
    if mischen_moeglich(kapitel):
        session["gemischt_modus"] = True
        close_task()
        return redirect(url_for("lektion", chapter=MISCHEN))

    # Reihum durch die bekannten Kapitel
    zuletzt = session.get("gemischt_zuletzt")
    if zuletzt in kapitel and len(kapitel) > 1:
        i = (kapitel.index(zuletzt) + 1) % len(kapitel)
    else:
        i = 0
    kap = kapitel[i]
    session["gemischt_zuletzt"] = kap
    session["gemischt_modus"] = True
    close_task()
    return redirect(url_for("lektion", chapter=kap))


@app.route("/lektion/<chapter>")
@login_required
def lektion(chapter):
    level = aktuelles_level(chapter)
    prog  = get_or_create_progress(current_user.id, chapter, level)
    db.session.commit()

    passend = (
        session.get("task_open")
        and session.get("task_chapter") == chapter
        and session.get("task_level") == level
        and aufgabe_laden()
    )

    if passend:
        daten = aufgabe_laden()
    else:
        bauform = naechste_bauform(chapter, level) if chapter in KAPITEL else None
        if chapter in KAPITEL and bauform is None:
            # Alle Bauformen dieses Levels sitzen -> Level fertig
            return redirect(url_for("level_fertig", chapter=chapter))
        if session.get("kernidee_kapitel") != chapter:
            session["kernidee_zeigen"] = True
            session["kernidee_kapitel"] = chapter
        daten = neue_aufgabe_fuer(chapter, level, bauform)
        aufgabe_speichern(daten)
        session["current_question"] = daten["frage"]
        session["current_solution"] = daten["loesung"]
        session["task_chapter"]     = chapter
        session["task_level"]       = level
        session["task_open"]        = True
        session["task_tries"]       = 0
        session["last_wrong"]       = False

    # ── Fortschritt: bei Generatorkapiteln zaehlen die Bauformen, nicht die
    #    Aufgaben. «7 von 12 Aufgabenarten sitzen» sagt mehr als «8 von 10
    #    Aufgaben geloest», weil es die Luecken sichtbar macht.
    if chapter in KAPITEL:
        alle = alle_bauformen(chapter, level)
        g, ges, pct = fortschritt(alle, gemeisterte(chapter, level))
        geloest, min_questions, quote = g, ges, pct

        # ── Der Balken zaehlt auch HALBE Schritte ────────────────────────
        # Eine Bauform gilt erst nach zwei richtigen Antworten als sicher.
        # Bei zwoelf Bauformen und Reihum-Ziehung heisst das: die ersten
        # ZWOELF richtigen Antworten bewegen den Zaehler um null. Wer so
        # lange nichts sieht, haelt die App fuer kaputt — zu Recht, denn
        # eine Rueckmeldung, die zwoelf Aufgaben lang schweigt, ist keine.
        # Der Balken zeigt darum den halben Schritt schon an, die Zahl
        # daneben bleibt bei den wirklich sicheren Bauformen.
        staende = {b.bauform: (b.treffer or 0) for b in BauformStand.query
                   .filter_by(user_id=current_user.id, chapter=chapter,
                              level=level)}
        punkte = sum(min(staende.get(b, 0), MASTERY) for b in alle)
        balken = int(punkte / (len(alle) * MASTERY) * 100) if alle else 0
        angefangen = sum(1 for b in alle if 0 < staende.get(b, 0) < MASTERY)
    else:
        total   = prog.total_cnt   or 0
        correct = prog.correct_cnt or 0
        geloest, min_questions = total, MIN_QUESTIONS
        quote = int((correct / total) * 100) if total > 0 else 0
        balken = quote
        angefangen = 0

    show_hint     = prog.consecutive_err >= CONSECUTIVE_ERR
    versuche      = session.get("task_tries", 0)
    zeige_loesung = versuche >= MAX_TRIES

    return render_template(
        "lektion.html",
        frage=daten["frage"],
        chapter=chapter,
        quote=quote,
        balken=balken,
        angefangen=angefangen,
        geloest=geloest,
        level=level,
        show_hint=show_hint,
        min_questions=min_questions,
        hint_text=get_hint(chapter),
        zeige_loesung=zeige_loesung,
        loesung=daten["loesung_text"] if zeige_loesung else None,
        versuche=versuche,
        chapter_name=CHAPTER_NAMES.get(chapter, ""),
        anleitung=daten.get("anleitung", "Loese die Aufgabe"),
        antwort_status=session.pop("antwort_status", None),
        antwort_text=session.pop("antwort_text", None),
        luecke=session.pop("luecke", None),
        # Teil 6 der Schablone, einmal beim Einstieg. Auch wer das Level
        # ueberspringt, soll die Regel gelesen haben.
        # Die Theorie wird VORGEFUEHRT, nicht beschrieben: eine
        # Beispielaufgabe formt sich in drei bis fuenf Schritten selbst um.
        # Wo noch keine Animation existiert, erscheint wie bisher der
        # Textkasten mit Teil 6 der Schablone.
        # Die Theorie erscheint bei JEDEM Aufruf der Lektionsseite.
        #
        # Vorher hing sie an `kernidee_zeigen`, das nur beim allerersten
        # Betreten eines Kapitels gesetzt wurde. Wer die Lektion schon einmal
        # offen hatte, bekam sie nie wieder zu sehen — auch nicht nach dem
        # Einbau einer neuen Fassung. Genau daran ist das Ausprobieren
        # gescheitert.
        #
        # Sie steht oben, laeuft von selbst und laesst sich mit einem Klick
        # ausblenden. Das ist zumutbar; unsichtbare Theorie ist es nicht.
        theorie=theorie_modul.fuer(chapter),
        kernidee=(kernidee(chapter)
                  if session.pop("kernidee_zeigen", False) else None),
    )


@app.route("/level-fertig/<chapter>")
@login_required
def level_fertig(chapter):
    """FEHLER 1 · Aufstieg erst, wenn JEDE Bauform sitzt — nicht bei 80 %."""
    ks    = kapitel_stand(chapter)
    alt   = ks.level
    neu   = naechstes_level(alt)
    ks.offen = ""
    close_task()

    if neu:
        ks.level = neu
        db.session.commit()
        flash(f"Alle Aufgabenarten von Level {alt} sitzen. Weiter mit Level {neu}.",
              "success")
    else:
        ks.abgeschlossen = True
        db.session.commit()
        # Alle Lektionen, die diese Schablone uebt, gelten jetzt als sicher.
        lw = lernweg()
        for lek, kap in SCHABLONE_FUER.items():
            if kap == chapter:
                lektion_fertig_melden(lw, lek)
        flash("Geschafft — jede Aufgabenart sitzt auf allen drei Levels.", "success")
        return redirect(url_for("start"))
    return redirect(url_for("lektion", chapter=chapter))


@app.route("/level-ueberspringen/<chapter>", methods=["POST"])
@login_required
def level_ueberspringen(chapter):
    """«Das ist mir zu einfach» — eine Stufe weiter, ohne alles zu lösen.

    WARUM ES DAS GEBEN MUSS: Eine Aufgabenart gilt erst nach zwei richtigen
    Antworten als sicher; bei zwölf Bauformen sind das vierundzwanzig
    Aufgaben je Level. Wer den Stoff längst kann, sitzt damit über eine
    Stunde an Dingen, die er im Schlaf beherrscht — und hört auf. Für eine
    Plattform, die freiwillig zu Hause benutzt wird, ist das der sicherste
    Weg, niemanden zu erreichen.

    WAS DABEI NICHT PASSIERT: Das übersprungene Level wird NICHT als
    gemeistert verbucht. Die Bauformen bleiben offen, und im Lernstand ist
    nachher sichtbar, dass hier übersprungen wurde. Wer sich überschätzt,
    fällt in der Probe-Erhebung darauf zurück — dort kommen falsch gelöste
    Lektionen wieder in den Weg. Das ist die ehrlichere Lösung, als den
    Sprung zu verbieten.
    """
    if chapter not in KAPITEL:
        return redirect(url_for("lektion", chapter=chapter))

    ks = kapitel_stand(chapter)
    alt = ks.level
    neu = naechstes_level(alt)
    ks.offen = ""
    close_task()

    #: Wer überspringt, hat die LEKTION abgehakt, nicht bloss eine Stufe.
    #: Vorher zählte nur der Sprung über Level C — man musste dreimal
    #: klicken, und bis dahin blieb alles gesperrt, was diese Lektion
    #: voraussetzt. Das ist genau das Gegenteil dessen, wofür der Knopf da
    #: ist: er soll den Weg frei machen, nicht dreimal nachfragen.
    lw = lernweg()
    for lek, kap in SCHABLONE_FUER.items():
        if kap == chapter:
            lektion_fertig_melden(lw, lek)

    if neu:
        #: Das Level wandert trotzdem mit. Wer später zurückkommt, landet
        #: dort, wo es interessant wird, und nicht wieder bei A.
        ks.level = neu
        ks.abgeschlossen = True
        db.session.commit()
        flash(f"Übersprungen. Die Lektion ist abgehakt und alles, was sie "
              f"voraussetzt, ist offen — du kannst sie jederzeit auf Level "
              f"{neu} nachholen.", "info")
        return redirect(url_for("start"))

    ks.abgeschlossen = True
    db.session.commit()
    flash("Lektion übersprungen. Sie bleibt im Dashboard, falls du sie "
          "später doch üben willst.", "info")
    return redirect(url_for("start"))


@app.route("/luecke-schliessen", methods=["POST"])
@login_required
def luecke_schliessen():
    """FEHLER 3 · Zum Kapitel wechseln, das die Luecke enthaelt."""
    ziel = request.form.get("ziel")
    close_task()
    if not ziel:
        return redirect(url_for("start"))
    lw = lernweg()
    zurueckspringen(lw, ziel)
    flash(f"Wir schauen zuerst «{KLARTEXT.get(ziel, ziel)}» an. "
          f"Danach geht es hier weiter.", "info")
    return redirect(url_for("lernen"))


def fmt_zahl(wert):
    """8.0 -> '8', 2.5 -> '2.5'"""
    try:
        f = float(wert)
    except (TypeError, ValueError):
        return str(wert)
    return str(int(f)) if f == int(f) else str(f)


def _als_float(wert):
    try:
        return float(wert)
    except (TypeError, ValueError):
        return None


def close_task():
    """Aktuelle Aufgabe abschliessen, beim naechsten Laden kommt eine neue."""
    session["task_open"]  = False
    session["last_wrong"] = False
    session["task_tries"] = 0
    aufgabe_speichern(None)
    aufgabe_speichern(None)


@app.route("/check", methods=["POST"])
@login_required
def check():
    user_input = request.form.get("antwort", "")
    daten      = aufgabe_laden()
    chapter    = request.form.get("chapter", "1.3")

    if not daten:
        return redirect(url_for("lektion", chapter=chapter))

    frage   = daten["frage"]
    level   = daten.get("level") or aktuelles_level(chapter)
    bauform = daten.get("bauform", "-")
    prog    = get_or_create_progress(current_user.id, chapter, level)

    # ── Antwort auswerten ────────────────────────────────────────────────────
    # Die ganze Aufgabe kommt aus der Session, mitsamt Zielform und
    # Fehlerkatalog. Aus dem blossen Loesungswert liesse sich beides nicht
    # rekonstruieren.
    aufgabe = aufgabe_aus_session(daten)
    a = auswerten(user_input, aufgabe)

    # Die Flamme zaehlt Tage, nicht Treffer — auch eine falsche Antwort ist
    # geuebt. Sonst wuerde ausgerechnet an schweren Tagen die Serie reissen.
    streak_aktualisieren()

    # Tippfehler zaehlen nicht als Versuch.
    if a.status in (Status.EINGABEFEHLER, Status.ZEITLIMIT):
        session["antwort_status"] = "error"
        session["antwort_text"]   = a.text
        return redirect(url_for("lektion", chapter=chapter))

    if a.zaehlt_als_richtig:
        prog.correct_cnt    += 1
        prog.consecutive_err = 0
        current_user.xp      = (current_user.xp or 0) + 10
        close_task()
        session["antwort_status"] = "success"
        session["antwort_text"]   = a.text

    elif a.status is Status.UNFERTIG:
        # Rechnung stimmt, nur die Form ist noch nicht fertig.
        # Kein Wissensfehler: Aufgabe bleibt offen, nichts wird gezaehlt.
        session["last_wrong"] = True
        session["task_tries"] = session.get("task_tries", 0) + 1
        session["antwort_status"] = "warning"
        session["antwort_text"]   = a.text

    else:
        prog.consecutive_err += 1
        session["last_wrong"] = True
        session["task_tries"] = session.get("task_tries", 0) + 1
        session["antwort_status"] = "error"
        session["antwort_text"]   = a.text

    db.session.add(TaskAttempt(
        user_id=current_user.id, chapter=chapter, level=level,
        question=frage, correct_solution=str(daten["loesung"]),
        user_answer=user_input, correct=a.zaehlt_als_richtig,
        status=a.status.value, fehlerschluessel=a.fehlerschluessel,
    ))

    if not a.zaehlt_als_geloest:
        # UNFERTIG: die Rechnung stimmt, nur die Form fehlt noch. Die Aufgabe
        # bleibt offen, damit der Schueler sie fertigschreiben kann.
        db.session.commit()
        return redirect(url_for("lektion", chapter=chapter))

    prog.total_cnt += 1

    # ── FEHLER 1 · Mastery pro Bauform statt Quote ───────────────────────────
    if chapter in KAPITEL:
        bs = bauform_stand(chapter, level, bauform)
        bs.treffer, bs.fehler, bs.gemeistert = bewerten(
            bs.treffer or 0, bs.fehler or 0, a.zaehlt_als_richtig)
        bs.updated_at = datetime.utcnow()

        # ── Luecke suchen: WOHIN genau? ──────────────────────────────────────
        # Nicht «irgendeine Voraussetzung», sondern die, auf die DIESER Fehler
        # deutet. Bei einer Bruchgleichung kann derselbe falsche Wert von der
        # Minusklammer, vom Hauptnenner oder von der Gleichungsumformung
        # kommen — der Fehlerschluessel sagt, welche es war.
        if not a.zaehlt_als_richtig:
            ziel = rueckwaerts_zu(daten.get("schablone", ""), bauform,
                                  a.fehlerschluessel)
            if ziel and (bs.fehler or 0) >= 2:
                lw = lernweg()
                if ziel not in lw.sichere_menge():
                    session["luecke"] = {
                        "kapitel": ziel,
                        "name": KLARTEXT.get(ziel, ziel),
                        "text": (f"Der Fehler deutet auf «{KLARTEXT.get(ziel, ziel)}» "
                                 f"hin. Das ist die Voraussetzung fuer diese "
                                 f"Aufgabenart. Zuerst dort nochmals ueben?"),
                    }

        db.session.commit()

        # Nur wenn die Antwort richtig war, ist die Aufgabe erledigt. Bei
        # einem Fehler bleibt sie offen — der Schueler bekommt die Hinweisbox
        # und darf es nochmals versuchen, genau wie in den alten Kapiteln.
        if a.zaehlt_als_richtig:
            alle = alle_bauformen(chapter, level)
            if set(alle) <= gemeisterte(chapter, level):
                return redirect(url_for("level_fertig", chapter=chapter))

        return redirect(url_for("lektion", chapter=chapter))

    # ── Alte Zahlenkapitel: Quotenlogik wie bisher ──────────────────────────
    db.session.commit()

    if prog.total_cnt >= MIN_QUESTIONS:
        rate      = prog.correct_cnt / prog.total_cnt
        old_level = current_user.current_level

        if rate >= RATE_UP:
            reset_progress(prog)
            if old_level == "A":
                current_user.current_level = "B"
                db.session.commit()
                return redirect(url_for("levelup_a_b", chapter=chapter))
            elif old_level == "B":
                current_user.current_level = "C"
                db.session.commit()
                return redirect(url_for("levelup_b_c", chapter=chapter))
            elif old_level == "C":
                current_user.current_level = "A"
                try:
                    p1, p2 = chapter.split(".")
                    next_chapter = f"{p1}.{int(p2) + 1}"
                except Exception:
                    next_chapter = "1.4"
                current_user.current_chapter = next_chapter
                db.session.commit()
                return redirect(url_for("kapitel_abgeschlossen",
                                        chapter=chapter, next_chapter=next_chapter))

        elif rate < RATE_DOWN:
            reset_progress(prog)
            if old_level == "C":
                current_user.current_level = "B"
                flash("Abstieg zu Level B - weiter ueben!", "warning")
            elif old_level == "B":
                current_user.current_level = "A"
                flash("Abstieg zu Level A - Grundlagen wiederholen!", "warning")
            db.session.commit()

        else:
            reset_progress(prog)
            db.session.commit()
            flash("Weiter so - noch mehr ueben fuer den Aufstieg!", "info")

    return redirect(url_for("lektion", chapter=chapter))



# ── Einstufungstest und personalisierter Weg ─────────────────────────────────

@app.route("/start")
@login_required
def start():
    """Die einzige Tuer. Von hier wird der Schueler weitergeleitet —
    zum Einstufungstest, wenn er noch nicht eingestuft ist, sonst zu der
    Lektion, die jetzt dran ist."""
    lw = lernweg()
    if not lw.eingestuft:
        return redirect(url_for("einstufung"))
    if not lw.aktuelle_lektion:
        lw.aktuelle_lektion = naechste_lektion(lw.sichere_menge())
        db.session.commit()
    if lw.aktuelle_lektion is None:
        return redirect(url_for("vertiefung"))
    return redirect(url_for("lernen"))


def einstiegslevel_anwenden(niveaus, sicher=None):
    """Das Ergebnis des Einstufungstests in die Kapitelstände schreiben.

    `einstufung.py` rechnet aus, wer wo auf Level B einsteigen darf: wer eine
    Leitaufgabe auf B loest, kann die folgenden Lektionen nicht auf Level A
    ueben muessen — das waere Unterforderung und kostet in einer vierwoechigen
    Studie rund zwei Drittel der Zeit.

    Bisher wurde dieser Wert berechnet und dann weggeworfen. Jedes Kapitel
    startete bei A, fuer alle. Hier landet er endlich im `KapitelStand`.

    ZWEI REGELN führen zu Level B:

    1  Nachfolgerregel (aus `einstufung.py`): wer die Leitaufgabe geloest hat,
       steigt in den FOLGENDEN Lektionen bei B ein.

    2  Kapitelregel: gilt auch nur EINE Lektion eines Kapitels bereits als
       sicher, dann beherrscht der Schueler die Grundform dieses Kapitels.
       Level A ist die Einstiegsstufe fuer jemanden, der das Kapitel noch
       nie gesehen hat — fuer ihn ist sie Unterforderung.

       Ohne diese zweite Regel griff der Levelsprung fast nie: die Kapitel,
       in denen noch Arbeit ansteht, sind meist gar keine Nachfolger der
       geloesten Leitaufgabe.

    Angehoben wird nur, wo noch NICHTS geuebt wurde. Wer in einem Kapitel
    schon Haekchen gesammelt hat, behaelt seinen Stand — sonst wuerde ein
    spaeterer Aufruf die Arbeit von gestern verwerfen.
    """
    ziel_level = {}

    for lektion, level in (niveaus or {}).items():
        if level in LEVELS and level != "A":
            kap = kapitel_fuer_lektion(lektion)
            if kap:
                ziel_level[kap] = level

    for lektion in (sicher or ()):
        kap = kapitel_fuer_lektion(lektion)
        if kap:
            ziel_level.setdefault(kap, "B")

    for kap, level in ziel_level.items():
        if kap not in KAPITEL:
            continue

        ks = kapitel_stand(kap)
        if ks.abgeschlossen or ks.level != "A":
            continue

        schon_geuebt = BauformStand.query.filter_by(
            user_id=current_user.id, chapter=kap).first()
        if schon_geuebt:
            continue

        ks.level = level
        ks.offen = ""                 # Ziehungsreihenfolge gilt je Level
        ks.updated_at = datetime.utcnow()

    db.session.commit()


def _ratbar(daten):
    """Kann man diese Aufgabe ohne Rechnen treffen?

    Zwei Faelle, beide legitime Aufgabenarten im Ueben, aber untauglich als
    LEITAUFGABE — im Einstufungstest schreibt eine einzige richtige Antwort
    bis zu 34 Lektionen gut:

    - Loesung ist 0 (Bauform «das Ergebnis ist null»). Wer blind 0 tippt,
      wird zu hoch eingestuft und ueberspringt Stoff, den er nicht kann.
    - Loesung ist die Frage selbst (Bauform «nichts laesst sich
      zusammenfassen»). Wer die Aufgabe abschreibt, kommt durch.
    """
    loesung = (daten.get("loesung_text") or "").replace(" ", "")
    frage = (daten.get("frage") or "").replace(" ", "")
    return loesung in ("0", "-0", "−0") or (loesung and loesung == frage)


def hat_level(kapitel, level):
    """Gibt es diese Stufe in dieser Schablone ueberhaupt?

    Nicht jede Bauform kann jedes Level. Ohne diese Pruefung bricht der
    Einstufungstest mit einem ValueError ab, sobald er eine Sonde auf C
    stellen will und die Schablone dort keine Bauform hat.
    """
    if kapitel not in KAPITEL:
        return True
    return bool(KAPITEL[kapitel].bauformen_fuer(level))


def bestes_level(kapitel, wunsch):
    """Das gewuenschte Level, sonst das naechstniedrigere, das es gibt."""
    for lv in (wunsch, "B", "A", "C"):
        if hat_level(kapitel, lv):
            return lv
    return "A"


def leitaufgabe(kapitel, level, versuche=30):
    """Eine Aufgabe fuer den Einstufungstest, ohne ratbare Sonderfaelle."""
    daten = neue_aufgabe_fuer(kapitel, level)
    for _ in range(versuche):
        if not _ratbar(daten):
            return daten
        daten = neue_aufgabe_fuer(kapitel, level)
    # Alle Bauformen dieses Kapitels sind Sonderfaelle — dann lieber eine
    # ratbare Aufgabe als gar keine Einstufung.
    return daten


@app.route("/einstufung")
@login_required
def einstufung():
    """Der Einstufungstest. Zwoelf Leitaufgaben, binaere Suche durchs Netz.

    Wer eine loest, bekommt alle Vorstufen gutgeschrieben — sonst braeuchte
    der Test 41 Aufgaben statt zwoelf.
    """
    lw = lernweg()

    # Wer schon eingestuft ist und keinen laufenden Test hat, gehoert nicht
    # hierher. Ohne diese Zeile startet ein Klick auf den Link einen zweiten
    # Test und wirft den Plan weg, den der erste gerade erstellt hat.
    if lw.eingestuft and not einstufung_laden():
        return redirect(url_for("start"))

    e = Einstufung.aus_dict(einstufung_laden())

    # Lektionen ohne Generator ueberspringen — in einer Schleife, nicht ueber
    # Redirects. Sonst laeuft der Browser bei zehn fehlenden Generatoren in
    # eine Weiterleitungsschleife.
    lektion = e.naechste()
    while lektion is not None and kapitel_fuer_lektion(lektion) is None:
        e.antwort(lektion, False)
        lektion = e.naechste()
    einstufung_speichern(e.als_dict())

    if lektion is None:
        # ZUERST den Bericht bauen, DANN speichern.
        #
        # `bericht()` schreibt bei einem starken Ergebnis die Grundlagen
        # gut — alles unter Lektion 5.1. Wurde vorher gespeichert, landete
        # dieser Nachtrag nirgends, und der Schüler bekam als nächste
        # Lektion 1.20 oder 2.8: eine Grundlage, die er längst kann, während
        # Kapitel 15 bei ihm offen war. Genau das haben die Testpersonen
        # gemeldet.
        bericht = e.bericht()

        lw.setze_sicher(e.sicher)
        lw.eingestuft = True

        # ── DORT ANFANGEN, WO ES GEHAKT HAT ──────────────────────────────
        # `naechste_lektion` liefert die kleinste offene Nummer. Bei einem
        # starken Schüler ist das eine Lektion, die er nur deshalb nicht
        # bewiesen hat, weil sie nie gefragt wurde — während seine echte
        # Lücke in Kapitel 12 liegt. Der Test hat sie gefunden, und dann
        # schickt ihn die App woandershin.
        #
        # Darum: gibt es Lektionen, an denen er im Test tatsächlich
        # gescheitert ist, beginnt er bei der ersten davon. Nur wenn er
        # nirgends gescheitert ist, entscheidet die Reihenfolge.
        # DIE REIHENFOLGE FOLGT DEM NETZ, NICHT DER FUNDSTELLE.
        #
        # Zwischenzeitlich begann der Schüler bei seiner ersten Lücke. Das
        # klang richtig, ergab aber einen Sprung: erst Lektion 14.2, dann
        # zurück auf 5.9, dann wieder aufwärts. Für den Lernenden sieht das
        # nach Zufall aus, und es ist auch fachlich schlechter — was in 5.9
        # fehlt, trägt bis 14.2 hinauf.
        #
        # Jetzt gilt wieder die Reihenfolge des Netzes: die kleinste offene
        # Lektion. Bei einem starken Schüler sind Kapitel 1 bis 4
        # gutgeschrieben, also beginnt er trotzdem weit oben — und seine
        # Lücken liegen ohnehin im offenen Teil und kommen der Reihe nach.
        lw.aktuelle_lektion = naechste_lektion(e.sicher)
        db.session.commit()
        # Der Levelsprung: wer die Leitaufgabe auf B geloest hat, faengt in
        # den folgenden Kapiteln bei B an statt bei A.
        einstiegslevel_anwenden(e.einstiegslevel, e.sicher)
        einstufung_loeschen()
        session["einstufung_bericht"] = bericht
        return redirect(url_for("einstufung_fertig"))

    kapitel = kapitel_fuer_lektion(lektion)
    # DAS ist die Adaptivitaet: der Test entscheidet selbst, wie schwer die
    # naechste Sonde ist. Wer eben richtig geantwortet hat, bekommt die
    # naechste eine Stufe hoeher; wer gescheitert ist, bekommt nicht
    # dasselbe nochmals, sondern dieselbe Stufe an einer tieferen Stelle.
    # Vorher stand hier fest «B» — fuer den Anfaenger zu schwer, fuer den
    # Gymnasiasten zu leicht, und beide waren nach zwoelf Aufgaben gleich
    # schlecht eingeschaetzt.
    level = bestes_level(kapitel, e.naechstes_level())
    daten = leitaufgabe(kapitel, level)
    daten["einstufung_lektion"] = lektion
    aufgabe_speichern(daten)
    session["task_open"] = True
    session["task_chapter"] = kapitel
    session["task_level"] = level
    session["task_tries"] = 0

    return render_template(
        "einstufung.html",
        frage=daten["frage"],
        anleitung=daten.get("anleitung", "Loese die Aufgabe"),
        lektion=lektion,
        lektion_name=KLARTEXT.get(lektion, lektion),
        nummer=e.gestellt + 1,
        gesamt=e.geschaetzt_gesamt(),
        level=level,
        antwort_text=session.pop("antwort_text", None),
        antwort_status=session.pop("antwort_status", None),
    )


@app.route("/einstufung/pruefen", methods=["POST"])
@login_required
def einstufung_pruefen():
    daten = aufgabe_laden() or {}
    lektion = daten.get("einstufung_lektion")
    if not lektion:
        return redirect(url_for("einstufung"))

    # «Kann ich nicht» — zaehlt als nicht geloest und bringt den Test weiter.
    #
    # Vorher gab es diesen Knopf nicht, und der Hinweis lautete «lass das Feld
    # leer und klick auf Weiter». Das funktionierte nicht: eine leere Eingabe
    # kommt als EINGABEFEHLER zurueck, wird bewusst NICHT gezaehlt (damit ein
    # Vertipper niemanden zu tief einstuft) — und dieselbe Aufgabe erschien
    # wieder. Wer eine Aufgabe nicht konnte, kam nicht mehr weiter.
    if request.form.get("kannnicht"):
        e = Einstufung.aus_dict(einstufung_laden())
        e.antwort(lektion, False)
        einstufung_speichern(e.als_dict())
        aufgabe_speichern(None)
        return redirect(url_for("einstufung"))

    a = auswerten(request.form.get("antwort", ""), aufgabe_aus_session(daten))

    # Tippfehler zaehlen nicht — sonst stuft ein Vertipper den Schueler
    # zu tief ein und er muss vier Wochen Bekanntes wiederholen.
    if a.status in (Status.EINGABEFEHLER, Status.ZEITLIMIT):
        session["antwort_status"] = "error"
        session["antwort_text"] = a.text
        return redirect(url_for("einstufung"))

    db.session.add(TaskAttempt(
        user_id=current_user.id, chapter="einstufung",
        level=daten.get("level", "B"), question=daten["frage"],
        correct_solution=str(daten["loesung"]),
        user_answer=request.form.get("antwort", ""),
        correct=a.zaehlt_als_richtig, status=a.status.value,
        fehlerschluessel=a.fehlerschluessel))
    db.session.commit()

    e = Einstufung.aus_dict(einstufung_laden())
    e.antwort(lektion, a.zaehlt_als_richtig)
    einstufung_speichern(e.als_dict())
    aufgabe_speichern(None)
    return redirect(url_for("einstufung"))


@app.route("/einstufung/fertig")
@login_required
def einstufung_fertig():
    return render_template("einstufung_fertig.html",
                           bericht=session.pop("einstufung_bericht", None))


@app.route("/lernen")
@login_required
def lernen():
    """Die Lektion, die JETZT dran ist. Ohne Kapitelauswahl."""
    lw = lernweg()
    if not lw.eingestuft:
        return redirect(url_for("einstufung"))
    if lw.aktuelle_lektion is None:
        return redirect(url_for("vertiefung"))

    # Lektionen ohne Generator ueberspringen — in einer Schleife, nicht ueber
    # Redirects, sonst laeuft der Browser in eine Weiterleitungsschleife.
    # Sobald ein Generator dazukommt, faellt die Lektion von selbst wieder
    # in den Weg zurueck.
    # Ohne Generator kann die Lektion nicht geuebt werden. Sie wird
    # uebersprungen, aber NICHT als sicher verbucht — sonst behauptet die App
    # Lueckenfreiheit, wo keine ist. Sie steht in einer eigenen Liste und
    # faellt in den Weg zurueck, sobald der Generator existiert.
    sprung = []
    while lw.aktuelle_lektion and kapitel_fuer_lektion(lw.aktuelle_lektion) is None:
        lw.merke_uebersprungen(lw.aktuelle_lektion)
        sprung.append(lw.aktuelle_lektion)
        lw.aktuelle_lektion = naechste_lektion(
            lw.sichere_menge() | lw.uebersprungene_menge())
        db.session.commit()
        if len(sprung) > 400:          # Notbremse gegen Endlosschleifen
            break

    if sprung:
        app.logger.info("Ohne Generator uebersprungen: %s", ", ".join(sprung))

    kapitel = kapitel_fuer_lektion(lw.aktuelle_lektion) if lw.aktuelle_lektion else None
    if kapitel is None:
        # Nichts mehr uebbar — entweder ist der Weg durch, oder es fehlen
        # schlicht die Generatoren. Beides fuehrt in die Vertiefung, die den
        # Unterschied benennt.
        return redirect(url_for("vertiefung"))

    return redirect(url_for("lektion", chapter=kapitel))


@app.route("/vertiefung")
@login_required
def vertiefung():
    """Wer vor Ablauf der vier Wochen durch ist, hoert nicht auf.

    Ohne Anschluss wuerde er die restliche Studienzeit nichts tun — und das
    verzerrt den Vergleich mit der Kontrollgruppe, die weiterarbeitet.
    """
    lw = lernweg()
    lw.durchgelaufen = True
    db.session.commit()

    schwach = schwachstellen(BauformStand.query.filter_by(user_id=current_user.id).all())
    modus = naechster_modus(lw.probe_gemacht, bool(schwach),
                            mischen_moeglich(gemischte_kapitel(lw)))

    return render_template(
        "vertiefung.html",
        modus=modus, titel=VTITEL, beschreibung=BESCHREIBUNG,
        schwach=[(k, l, b, f, KLARTEXT.get(k, k)) for k, l, b, f in schwach],
        probe_gemacht=lw.probe_gemacht, probe_quote=lw.probe_quote,
        mischen=mischen_moeglich(gemischte_kapitel(lw)),
    )


@app.route("/probe")
@login_required
def probe():
    """Probe-Erhebung: 19 Aufgaben, eine pro Teilaufgabe, in Pruefungsform."""
    p = Probelauf.aus_dict(session.get("probe") or {}) if session.get("probe") \
        else Probelauf.neu()

    # Teilaufgaben ohne Generator ueberspringen — ehrlicher, als sie als
    # bestanden zu zaehlen. Sie erscheinen im Bericht als "nicht geprueft".
    while not p.fertig() and not Probelauf.ist_mischaufgabe(p.aktuelle()) \
            and kapitel_fuer_lektion(p.lektion()) is None:
        p.uebersprungen()
    session["probe"] = p.als_dict()

    if p.fertig():
        lw = lernweg()
        b = p.bericht()
        lw.probe_gemacht = True
        lw.probe_quote = b["quote"]
        # WAS IN DER PROBE SCHIEFGING, GILT NICHT MEHR ALS SICHER.
        #
        # Ohne diesen Rueckweg war die Probe-Erhebung eine Anzeige ohne
        # Folgen: sie meldete «14 von 19», und danach uebte die App
        # weiter, als waere alles in Ordnung. Genau hier faellt die Luecke
        # eines starken Schuelers auf — der Einstufungstest mit dreissig
        # Aufgaben kann sie nicht in achtzig Lektionen orten, die Probe mit
        # neunzehn Pruefungsaufgaben schon.
        # ── Nach vorne gutschreiben ──────────────────────────────────────
        # Wer eine Erhebungsaufgabe richtig loest, kann diese Lektion — und
        # mit ihr die Vorstufen. Ohne diesen Schritt bleibt ein Schueler,
        # der die Probe fehlerfrei besteht, genau dort stehen, wo er vorher
        # war, und die Probe fuehlt sich an wie eine Pruefung ohne Wirkung.
        gewonnen = [l for l in p.richtige_lektionen()
                    if l not in lw.sichere_menge()]
        if gewonnen:
            menge = lw.sichere_menge()
            for lektion in gewonnen:
                menge = rueckwaerts_gutschreiben(lektion, menge)
            lw.setze_sicher(menge)

        verloren = [l for l in p.falsche_lektionen() if l in lw.sichere_menge()]
        if verloren:
            menge = lw.sichere_menge() - set(verloren)
            lw.setze_sicher(menge)

            # DIREKT ZU DEM, WAS SCHIEFGING — nicht zur kleinsten offenen
            # Nummer. `naechste_lektion` nimmt sonst die niedrigste offene
            # Lektion im ganzen Netz, und das ist nach einer Probe fast
            # immer 1.1: der Schueler landet bei den Grundlagen auf Level A,
            # obwohl die Probe genau gezeigt hat, wo es klemmt. Von den
            # zurueckgeholten Lektionen wird die mit der kleinsten Nummer
            # genommen, damit die Reihenfolge nachvollziehbar bleibt.
            ziel = min(verloren, key=lambda l: [int(x) for x in l.split(".")])
            lw.aktuelle_lektion = ziel if bereit_zum_ueben(ziel, menge, lw) \
                else naechste_lektion(menge | lw.uebersprungene_menge())
            lw.durchgelaufen = False
            for lektion in verloren:
                kap = kapitel_fuer_lektion(lektion)
                if not kap:
                    continue
                ks = kapitel_stand(kap)
                ks.abgeschlossen = False
                ks.level = "C"          # er kann das Thema, nur nicht ganz
                ks.offen = ""
            flash(f"{len(verloren)} Lektionen kommen zurueck in deinen Weg — "
                  f"dort ging in der Probe etwas schief.", "info")
        elif gewonnen:
            flash(f"{len(gewonnen)} Aufgabenarten sitzen — sie sind aus "
                  f"deinem Weg verschwunden.", "success")

        # ── Wohin nach der Probe? ────────────────────────────────────────
        # NICHT zur kleinsten offenen Nummer. Das waere fast immer Kapitel 1,
        # und ein Schueler, der die Probe fast fehlerfrei loest, landete
        # ausgerechnet bei «Zahlen auf der Zahlengeraden». Die Probe ist eine
        # Lueckensuche — also gehoert er zu der Luecke, die sie gefunden hat.
        bekannt = lw.sichere_menge() | lw.uebersprungene_menge()

        # ALLE falsch geloesten Teilaufgaben zaehlen, nicht nur die, die
        # vorher schon als sicher galten. Sonst passiert Folgendes: wer die
        # Probe mit 81 % besteht, aber vier Themen verfehlt, hatte diese
        # vier nie gutgeschrieben — `verloren` bleibt leer, und die App
        # schickt ihn zur kleinsten offenen Nummer, also nach 1.1. Er hat
        # gerade neunzehn Pruefungsaufgaben geloest und landet bei «Zahlen
        # auf der Zahlengeraden». Das ist die Rueckmeldung, die niemand
        # versteht — und sie ist auch sachlich falsch: die Probe hat ihm
        # genau gesagt, wo es hakt.
        # EIN FEHLER SCHLAEGT EINE GUTSCHRIFT.
        #
        # Der Haken war subtil: wer 6a richtig loest, bekommt ueber
        # `rueckwaerts_gutschreiben` auch alle Vorstufen von 15.5 gutgeschrieben
        # — und darunter kann ausgerechnet die Lektion sein, deren eigene
        # Teilaufgabe er falsch hatte. Sie stand danach als «sicher» da, die
        # Liste der Luecken war leer, und die App schickte ihn zur kleinsten
        # offenen Nummer: 1.1. Er hat gerade neunzehn Pruefungsaufgaben
        # geloest und landet bei «Zahlen auf der Zahlengeraden».
        #
        # Darum werden die falsch geloesten Lektionen ZULETZT wieder
        # gestrichen — nach dem Gutschreiben, nicht davor. Was er in der
        # Pruefung nicht konnte, kann keine Nebenrechnung gutmachen.
        alle_falschen = p.falsche_lektionen()
        if alle_falschen:
            menge = lw.sichere_menge() - set(alle_falschen)
            lw.setze_sicher(menge)
            lw.durchgelaufen = False
            for lektion in alle_falschen:
                kap = kapitel_fuer_lektion(lektion)
                if not kap:
                    continue
                ks = kapitel_stand(kap)
                ks.abgeschlossen = False
                ks.level = "C"
                ks.offen = ""
            lw.aktuelle_lektion = sorted(
                alle_falschen,
                key=lambda l: [int(x) for x in l.split(".")])[0]
        else:
            # ── Fehlerfrei ───────────────────────────────────────────────
            # Hier NICHT zur naechsten offenen Lektion schicken. Die Probe
            # deckt neunzehn von hundertsiebenundsechzig Lektionen ab; was
            # danach offen bleibt, ist grossteils Kapitel 1 — nicht weil er
            # es nicht kann, sondern weil es nie geprueft wurde. Ihn
            # ausgerechnet dorthin zu schicken, nachdem er neunzehn
            # Pruefungsaufgaben fehlerfrei geloest hat, liest sich wie eine
            # Strafe.
            #
            # Stattdessen bekommt er gesagt, dass er das Ziel erreicht hat,
            # und die Wahl: Mischaufgaben, oder die restlichen Lektionen
            # freiwillig. Das Feld `durchgelaufen` merkt sich das, damit die
            # Abschlussseite nicht bei jedem Aufruf neu erscheint.
            lw.durchgelaufen = True
            if lw.aktuelle_lektion in lw.sichere_menge() or not lw.aktuelle_lektion:
                lw.aktuelle_lektion = naechste_lektion(
                    lw.sichere_menge() | lw.uebersprungene_menge())
        db.session.commit()
        session.pop("probe", None)
        b["erhebung_geschafft"] = not p.falsche_lektionen()
        b["offen_danach"] = len([l for l in SCHABLONE_FUER
                                 if l not in lw.sichere_menge()
                                 and l not in lw.uebersprungene_menge()])
        return render_template("probe_fertig.html", bericht=b)

    # Die drei Mischaufgaben am Schluss haben keine eigene Lektion: sie
    # stehen eine Stufe ueber allen Kapiteln.
    if Probelauf.ist_mischaufgabe(p.aktuelle()):
        kapitel = MISCHEN
    else:
        kapitel = kapitel_fuer_lektion(p.lektion())
    daten = neue_aufgabe_fuer(kapitel, "C")
    daten["probe_teilaufgabe"] = p.aktuelle()
    aufgabe_speichern(daten)

    return render_template(
        "probe.html", frage=daten["frage"],
        anleitung=daten.get("anleitung", "Loese die Aufgabe"),
        teilaufgabe=p.aktuelle(), nummer=p.position + 1,
        gesamt=len(p.reihenfolge),
        antwort_text=session.pop("antwort_text", None),
        antwort_status=session.pop("antwort_status", None),
    )


@app.route("/probe/pruefen", methods=["POST"])
@login_required
def probe_pruefen():
    daten = aufgabe_laden() or {}
    if "probe_teilaufgabe" not in daten:
        return redirect(url_for("probe"))
    a = auswerten(request.form.get("antwort", ""), aufgabe_aus_session(daten))

    # In der Pruefung zaehlt auch der Tippfehler nicht als Rechenfehler.
    if a.status in (Status.EINGABEFEHLER, Status.ZEITLIMIT):
        session["antwort_status"] = "error"
        session["antwort_text"] = a.text
        return redirect(url_for("probe"))

    db.session.add(TaskAttempt(
        user_id=current_user.id, chapter="probe", level="C",
        question=daten["frage"], correct_solution=str(daten["loesung"]),
        user_answer=request.form.get("antwort", ""),
        correct=a.zaehlt_als_richtig, status=a.status.value,
        fehlerschluessel=a.fehlerschluessel))
    db.session.commit()

    p = Probelauf.aus_dict(session.get("probe") or {})
    p.antwort(a.zaehlt_als_richtig)
    session["probe"] = p.als_dict()
    aufgabe_speichern(None)
    return redirect(url_for("probe"))


@app.route("/wiederholen/<modus>")
@login_required
def wiederholen(modus):
    """Schwachstellen oder Level C — beides fuehrt in die normale Lektion,
    nur mit anderer Auswahl."""
    if modus == SCHWACHSTELLEN:
        schwach = schwachstellen(
            BauformStand.query.filter_by(user_id=current_user.id).all(), 1)
        if not schwach:
            return redirect(url_for("vertiefung"))
        kapitel, level, bauform, _ = schwach[0]
        # Haekchen entfernen, damit die Bauform wieder gezogen wird
        bs = bauform_stand(kapitel, level, bauform)
        bs.gemeistert = False
        bs.treffer = 0
        db.session.commit()
        close_task()
        return redirect(url_for("lektion", chapter=kapitel))

    if modus == MISCHAUFGABEN:
        close_task()
        return redirect(url_for("lektion", chapter=MISCHEN))

    if modus == LEVEL_C:
        # Alle Kapitel mit Generator auf C stellen. Auch die, bei denen der
        # Schueler ueber den Levelsprung eingestiegen ist und C nie sah.
        for kapitel in KAPITEL:
            ks = kapitel_stand(kapitel)
            ks.level = "C"
            ks.abgeschlossen = False
            ks.offen = ""
        db.session.commit()
        close_task()
        return redirect(url_for("lektion", chapter=list(KAPITEL)[0]))

    return redirect(url_for("vertiefung"))


@app.route("/ziel-erreicht")
@login_required
def ziel_erreicht():
    lw = lernweg()
    g, ges, pct = netz_fortschritt(lw.sichere_menge())
    fehlend = sorted(lw.uebersprungene_menge())
    return render_template("ziel_erreicht.html", sicher=g, gesamt=ges, prozent=pct,
                           erhebung=erhebung_abgedeckt(lw.sichere_menge()),
                           uebersprungen=[(l, KLARTEXT.get(l, l)) for l in fehlend])


# ── Markierte Aufgaben ─────────────────────────────────────────────────────────

@app.route("/markieren", methods=["POST"])
@login_required
def markieren():
    """Stern beim Ueben: Aufgabe fuer die Lehrperson merken und ueberspringen."""
    chapter = request.form.get("chapter", "1.3")
    daten   = aufgabe_laden() or {}
    frage   = daten.get("frage") or session.get("current_question")
    loesung = daten.get("loesung")

    if not frage:
        return redirect(url_for("lektion", chapter=chapter))

    schon_da = MarkedTask.query.filter_by(
        user_id=current_user.id, question=frage, resolved=False
    ).first()

    if not schon_da:
        db.session.add(MarkedTask(
            user_id=current_user.id,
            chapter=chapter,
            level=aktuelles_level(chapter),
            question=frage,
            # Float-Spalte: Terme wie "a*(2*z + 3)" passen nicht hinein.
            # Die Frage im Wortlaut steht ohnehin daneben.
            solution=_als_float(loesung),
            note=(request.form.get("notiz") or "").strip() or None,
        ))
        db.session.commit()
        flash("⭐ Aufgabe gemerkt – du findest sie im Dashboard.", "success")
    else:
        flash("Diese Aufgabe ist schon gemerkt.", "success")

    close_task()
    return redirect(url_for("lektion", chapter=chapter))


@app.route("/naechste", methods=["POST"])
@login_required
def naechste():
    """Weiter zur naechsten Aufgabe, nachdem die Loesung gezeigt wurde."""
    chapter = request.form.get("chapter", "1.3")
    close_task()
    return redirect(url_for("lektion", chapter=chapter))


@app.route("/markierte")
@login_required
def markierte():
    offen = (MarkedTask.query
             .filter_by(user_id=current_user.id, resolved=False)
             .order_by(MarkedTask.created_at.desc()).all())
    # Verstandene bleiben sichtbar (durchgestrichen), damit man spaeter
    # noch nachvollziehen kann, wo es Muehe gab.
    verstanden = (MarkedTask.query
                  .filter_by(user_id=current_user.id, resolved=True)
                  .order_by(MarkedTask.created_at.desc()).all())
    return render_template("markierte.html", offen=offen, verstanden=verstanden,
                           chapter_names=CHAPTER_NAMES)


@app.route("/markierte/<int:mid>/erledigt", methods=["POST"])
@login_required
def markierung_erledigt(mid):
    m = MarkedTask.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    m.resolved = not m.resolved
    db.session.commit()
    return redirect(url_for("markierte"))


@app.route("/markierte/<int:mid>/loeschen", methods=["POST"])
@login_required
def markierung_loeschen(mid):
    m = MarkedTask.query.filter_by(id=mid, user_id=current_user.id).first_or_404()
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for("markierte"))


# ── Level-Up Seiten ────────────────────────────────────────────────────────────

@app.route("/levelup_a_b")
@login_required
def levelup_a_b():
    chapter = request.args.get("chapter", "1.3")
    return render_template("levelup_a_b.html", chapter=chapter)


@app.route("/levelup_b_c")
@login_required
def levelup_b_c():
    chapter = request.args.get("chapter", "1.3")
    return render_template("levelup_b_c.html", chapter=chapter)


@app.route("/kapitel_abgeschlossen")
@login_required
def kapitel_abgeschlossen():
    chapter      = request.args.get("chapter", "1.3")
    next_chapter = request.args.get("next_chapter", "1.4")
    return render_template("kapitel_abgeschlossen.html", chapter=chapter, next_chapter=next_chapter)


# ── Auth ───────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(email=request.form.get("email")).first()
        if u and u.check_password(request.form.get("password")):
            login_user(u)
            return redirect(url_for("dashboard"))
        flash("E-Mail oder Passwort falsch.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        benutzername = (request.form.get("username") or "").strip()
        mail = (request.form.get("email") or "").strip()
        passwort = request.form.get("password") or ""

        # Prüfen ob E-Mail bereits existiert
        existing = User.query.filter_by(email=mail).first()
        if existing:
            flash("Diese E-Mail ist bereits registriert.", "error")
            return render_template("register.html")

        # Der Benutzername ist in der Datenbank eindeutig. Ohne diese Pruefung
        # bricht das Speichern mit einem Datenbankfehler ab, und die Schuelerin
        # sieht eine weisse Fehlerseite statt eines Hinweises.
        if User.query.filter_by(username=benutzername).first():
            flash("Dieser Benutzername ist schon vergeben.", "error")
            return render_template("register.html")

        if len(passwort) < 6:
            flash("Das Passwort braucht mindestens 6 Zeichen.", "error")
            return render_template("register.html")

        u = User(
            username=benutzername,
            email=mail,
        )
        u.set_password(passwort)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ── Passwort ───────────────────────────────────────────────────────────────────

@app.route("/passwort-vergessen", methods=["GET", "POST"])
def passwort_vergessen():
    reset_link = None

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        u = User.query.filter(db.func.lower(User.email) == email).first()

        if u:
            eintrag = PasswordReset(
                user_id=u.id,
                token=secrets.token_urlsafe(32),
                expires_at=datetime.utcnow() + timedelta(minutes=RESET_MINUTES),
            )
            db.session.add(eintrag)
            db.session.commit()

            reset_link = url_for("passwort_neu", token=eintrag.token, _external=True)
            # Ohne Mailserver wird der Link im Terminal ausgegeben.
            print(f"\n[Passwort-Link fuer {u.email}] {reset_link}\n")

        # Gleiche Meldung fuer alle: sonst koennte man Konten erraten.
        flash("Falls die E-Mail bei uns registriert ist, wurde ein Link erstellt.", "success")

    return render_template("passwort_vergessen.html",
                           reset_link=reset_link,
                           debug=app.debug)


@app.route("/passwort-neu/<token>", methods=["GET", "POST"])
def passwort_neu(token):
    eintrag = PasswordReset.query.filter_by(token=token).first()

    if not eintrag or not eintrag.is_valid:
        flash("Dieser Link ist abgelaufen oder wurde schon benutzt.", "error")
        return redirect(url_for("passwort_vergessen"))

    if request.method == "POST":
        pw1 = request.form.get("password", "")
        pw2 = request.form.get("password2", "")

        if len(pw1) < 6:
            flash("Das Passwort braucht mindestens 6 Zeichen.", "error")
        elif pw1 != pw2:
            flash("Die beiden Passwörter stimmen nicht überein.", "error")
        else:
            u = db.session.get(User, eintrag.user_id)
            u.set_password(pw1)
            eintrag.used = True
            db.session.commit()
            flash("Passwort geändert – du kannst dich jetzt anmelden.", "success")
            return redirect(url_for("login"))

    return render_template("passwort_neu.html", token=token)


@app.route("/passwort-aendern", methods=["GET", "POST"])
@login_required
def passwort_aendern():
    if request.method == "POST":
        alt = request.form.get("old_password", "")
        pw1 = request.form.get("password", "")
        pw2 = request.form.get("password2", "")

        if not current_user.check_password(alt):
            flash("Das bisherige Passwort stimmt nicht.", "error")
        elif len(pw1) < 6:
            flash("Das neue Passwort braucht mindestens 6 Zeichen.", "error")
        elif pw1 != pw2:
            flash("Die beiden Passwörter stimmen nicht überein.", "error")
        else:
            current_user.set_password(pw1)
            db.session.commit()
            flash("Passwort geändert.", "success")
            return redirect(url_for("dashboard"))

    return render_template("passwort_aendern.html")


@app.route("/neu-starten", methods=["GET", "POST"])
@login_required
def neu_starten():
    """Den eigenen Lernstand loeschen und wieder beim Starttest beginnen.

    WARUM ALS FUNKTION UND NICHT PER DATENBANKBEFEHL: Wer den Test nochmals
    machen will, muesste sonst in der Datenbank herumloeschen — mit dem
    Risiko, ein vergessenes WHERE zu tippen und alle Konten zu treffen. Hier
    kann nur das eigene Konto zurueckgesetzt werden, weil `current_user.id`
    fest verdrahtet ist. Es gibt keinen Weg, damit fremde Daten anzufassen.

    Das KONTO bleibt bestehen — Anmeldedaten und Serie aendern sich nicht.
    Weg ist der Lernweg: Einstufung, Fortschritt, Kapitelstaende, Versuche.
    """
    if request.method == "POST":
        uid = current_user.id
        for tabelle in (TaskAttempt, BauformStand, KapitelStand,
                        EinstufungsStand, Progress, MarkedTask, Lernweg):
            tabelle.query.filter_by(user_id=uid).delete()
        current_user.xp = 0
        current_user.current_level = "A"
        # NICHT auf None setzen: das Dashboard baut daraus eine Adresse und
        # bricht sonst mit BuildError ab. Leerer Text ist genauso «nichts»,
        # aber die Vorlage kann ihn abfragen.
        current_user.current_chapter = ""
        db.session.commit()
        session.clear()
        login_user(User.query.get(uid))
        flash("Dein Lernstand wurde zurückgesetzt. Der Starttest beginnt "
              "von vorne.", "success")
        return redirect(url_for("start"))

    return render_template("neu_starten.html")


# ── Start ──────────────────────────────────────────────────────────────────────
def spalten_nachziehen():
    """Fehlende Spalten in bestehenden Tabellen anlegen.

    WARUM ES DAS BRAUCHT: `db.create_all()` legt fehlende TABELLEN an, aber
    es fasst bestehende nie an. Kommt eine Spalte dazu — etwa `streak` bei
    `user` —, bleibt die Datenbank auf dem alten Stand, und die erste
    Abfrage stirbt mit «column user.streak does not exist». Lokal faellt das
    nicht auf, weil man die Datei einfach loescht; auf dem Server mit echten
    Daten ist Loeschen keine Option.

    Diese Funktion vergleicht die Modelle mit dem, was wirklich in der
    Datenbank steht, und ergaenzt nur, was fehlt. Sie loescht nichts und
    aendert nichts Bestehendes — der schlimmste Fall ist, dass sie nichts
    tut.

    Sie laeuft bei jedem Start. Das kostet Sekundenbruchteile und erspart
    beim naechsten Schemawechsel dasselbe Theater.
    """
    from sqlalchemy import inspect as _inspect, text as _text

    pruefer = _inspect(db.engine)
    vorhanden_tabellen = set(pruefer.get_table_names())

    for tabelle in db.metadata.sorted_tables:
        if tabelle.name not in vorhanden_tabellen:
            continue                       # legt create_all() selbst an
        da = {s["name"] for s in pruefer.get_columns(tabelle.name)}

        for spalte in tabelle.columns:
            if spalte.name in da:
                continue
            typ = spalte.type.compile(dialect=db.engine.dialect)
            standard = ""
            if spalte.default is not None and spalte.default.is_scalar:
                wert = spalte.default.arg
                standard = (f" DEFAULT {wert}" if isinstance(wert, (int, float))
                            else f" DEFAULT '{wert}'")
            befehl = (f'ALTER TABLE "{tabelle.name}" '
                      f'ADD COLUMN "{spalte.name}" {typ}{standard}')
            try:
                with db.engine.begin() as verbindung:
                    verbindung.execute(_text(befehl))
                app.logger.info("Spalte ergaenzt: %s.%s",
                                tabelle.name, spalte.name)
            except Exception as fehler:               # noqa: BLE001
                # Nicht abbrechen: eine Spalte, die sich nicht anlegen
                # laesst, soll nicht den ganzen Start verhindern. Der
                # Eintrag im Log sagt, wo nachzuschauen ist.
                app.logger.warning("Spalte %s.%s nicht angelegt: %s",
                                   tabelle.name, spalte.name, fehler)

        # ── Falscher Spaltentyp ──────────────────────────────────────────
        # Zweiter Fall, der bei einer gewachsenen Datenbank auftritt: die
        # Spalte IST da, hat aber noch den alten Typ. `correct_solution`
        # war frueher eine Zahl, weil die Loesungen Zahlen waren. Seit es
        # Terme gibt, steht dort «4*a**2 - 4*a» — und Postgres weist das
        # zurueck: «invalid input syntax for type double precision».
        # SQLite faellt das nie auf, weil es Typen nicht erzwingt.
        #
        # Umgewandelt wird NUR von Zahl nach Text, und das ist verlustfrei:
        # jede Zahl laesst sich als Text schreiben. Der umgekehrte Weg
        # waere gefaehrlich und wird darum gar nicht erst versucht.
        bestand = {s["name"]: s for s in pruefer.get_columns(tabelle.name)}
        for spalte in tabelle.columns:
            alt = bestand.get(spalte.name)
            if alt is None:
                continue
            ist_text_gewuenscht = spalte.type.__class__.__name__ in (
                "String", "Text", "Unicode", "UnicodeText", "VARCHAR")
            ist_zahl_in_db = alt["type"].__class__.__name__ in (
                "FLOAT", "DOUBLE_PRECISION", "REAL", "NUMERIC", "INTEGER",
                "BIGINT", "SMALLINT", "Float", "Numeric", "Integer")
            if not (ist_text_gewuenscht and ist_zahl_in_db):
                continue
            typ = spalte.type.compile(dialect=db.engine.dialect)
            befehl = (f'ALTER TABLE "{tabelle.name}" '
                      f'ALTER COLUMN "{spalte.name}" TYPE {typ} '
                      f'USING "{spalte.name}"::text')
            try:
                with db.engine.begin() as verbindung:
                    verbindung.execute(_text(befehl))
                app.logger.info("Spaltentyp korrigiert: %s.%s -> %s",
                                tabelle.name, spalte.name, typ)
            except Exception as fehler:           # noqa: BLE001
                app.logger.warning("Spaltentyp %s.%s nicht geaendert: %s",
                                   tabelle.name, spalte.name, fehler)


with app.app_context():
    db.create_all()
    spalten_nachziehen()

if __name__ == "__main__":
    # ── Start ────────────────────────────────────────────────────────────
    # `app.run(debug=True)` horcht nur auf 127.0.0.1 — also NUR auf dem
    # Rechner, auf dem es laeuft. Fuer den eigenen Test ist das richtig,
    # fuer zehn Mitschueler nicht: sie kommen nicht heran.
    #
    # HOST=0.0.0.0 oeffnet die App fuers lokale Netz (gleiches WLAN).
    # Fuer die Studie ueber das Internet braucht es einen Hoster; dann
    # setzt dieser PORT und SECRET_KEY selbst.
    #
    # debug=True zeigt bei einem Fehler den Quelltext IM BROWSER und
    # erlaubt das Ausfuehren von Code. Auf dem eigenen Rechner egal,
    # sobald andere zugreifen ein Sicherheitsloch. Darum standardmaessig
    # aus, sobald HOST gesetzt ist.
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1" if host == "127.0.0.1" else "0")
    app.run(host=host, port=port, debug=(debug == "1"))
