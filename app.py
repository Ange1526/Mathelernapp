from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
import random
import secrets

app = Flask(__name__)

# ── Konfiguration ──────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-matura-2024")

database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
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
    correct_solution = db.Column(db.Float, nullable=False)
    user_answer = db.Column(db.Float, nullable=False)

    correct = db.Column(db.Boolean, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    chapters = ["1.3", "1.4", "1.5", "1.6", "1.7"]
    progress_map = {}

    for ch in chapters:
        progs = Progress.query.filter_by(
            user_id=current_user.id,
            chapter=ch
        ).all()

        if progs:
            total_correct = sum(p.correct_cnt or 0 for p in progs)
            total_done = sum(p.total_cnt or 0 for p in progs)

            done = any(
                p.level == "C" and (p.correct_cnt or 0) >= 8
                for p in progs
            )

            progress_map[ch] = {
                "done": done,
                "progress_pct": min(
                    int((total_correct / total_done) * 100),
                    100
                ) if total_done > 0 else 0
            }

    return render_template(
        "dashboard.html",
        user=current_user,
        progress_map=progress_map
    )


@app.route("/lektion/<chapter>")
@login_required
def lektion(chapter):
    prog    = get_or_create_progress(current_user.id, chapter, current_user.current_level)
    db.session.commit()

    total   = prog.total_cnt   or 0
    correct = prog.correct_cnt or 0
    quote   = int((correct / total) * 100) if total > 0 else 0

    # Die laufende Aufgabe bleibt in der Session stehen, solange sie offen ist.
    # Nur so bleibt bei einer falschen Antwort dieselbe Rechnung sichtbar.
    passend = (
        session.get("task_open")
        and session.get("task_chapter") == chapter
        and session.get("task_level") == current_user.current_level
    )

    if passend:
        frage   = session["current_question"]
        loesung = session["current_solution"]
    else:
        frage, loesung = generate_math_task(chapter, current_user.current_level)
        session["current_question"] = frage
        session["current_solution"] = loesung
        session["task_chapter"]     = chapter
        session["task_level"]       = current_user.current_level
        session["task_open"]        = True
        session["task_tries"]       = 0
        session["last_wrong"]       = False

    # Hinweis nach einer falschen Antwort oder nach 2 Fehlern in Folge
    show_hint = session.get("last_wrong", False) or prog.consecutive_err >= CONSECUTIVE_ERR

    # Nach mehreren Versuchen die Lösung verraten, damit niemand feststeckt
    versuche = session.get("task_tries", 0)
    zeige_loesung = versuche >= MAX_TRIES

    return render_template(
        "lektion.html",
        frage=frage,
        chapter=chapter,
        quote=quote,
        geloest=total,
        level=current_user.current_level,
        show_hint=show_hint,
        min_questions=MIN_QUESTIONS,
        hint_text=get_hint(chapter),
        zeige_loesung=zeige_loesung,
        loesung=fmt_zahl(loesung) if zeige_loesung else None,
        versuche=versuche,
        chapter_name=CHAPTER_NAMES.get(chapter, ""),
        # base.html verbraucht die Flash-Meldungen, darum eigener Status
        antwort_status=session.pop("antwort_status", None),
    )


def fmt_zahl(wert):
    """8.0 -> '8', 2.5 -> '2.5'"""
    try:
        f = float(wert)
    except (TypeError, ValueError):
        return str(wert)
    return str(int(f)) if f == int(f) else str(f)


def close_task():
    """Aktuelle Aufgabe abschliessen, beim naechsten Laden kommt eine neue."""
    session["task_open"]  = False
    session["last_wrong"] = False
    session["task_tries"] = 0


@app.route("/check", methods=["POST"])
@login_required
def check():
    user_input        = request.form.get("antwort", "").strip().replace(",", ".")
    korrekte_loesung  = session.get("current_solution")
    frage              = session.get("current_question")
    chapter            = request.form.get("chapter", "1.3")

    try:
        user_val = float(user_input)
    except ValueError:
        flash("Ungültige Eingabe – bitte eine Zahl eingeben.", "error")
        return redirect(url_for("lektion", chapter=chapter))

    prog = get_or_create_progress(current_user.id, chapter, current_user.current_level)

    # ── Antwort auswerten ──────────────────────────────────────────────────────
    richtig = abs(user_val - float(korrekte_loesung)) < 0.0001

    if richtig:
        prog.correct_cnt     += 1
        prog.consecutive_err  = 0
        current_user.xp       = (current_user.xp or 0) + 10
        close_task()                     # erst jetzt kommt eine neue Aufgabe
        session["antwort_status"] = "success"
        flash("✅ Richtig!", "success")
    else:
        prog.consecutive_err += 1
        session["last_wrong"] = True     # loest die Hinweis-Box aus
        session["task_tries"] = session.get("task_tries", 0) + 1
        # Aufgabe bleibt offen -> dieselbe Rechnung wird nochmals angezeigt
        session["antwort_status"] = "error"
        flash("❌ Falsch – schau dir den Tipp an und versuch es nochmal.", "error")

    prog.total_cnt += 1
    attempt = TaskAttempt(
        user_id=current_user.id,
        chapter=chapter,
        level=current_user.current_level,
        question=frage,
        correct_solution=float(korrekte_loesung),
        user_answer=user_val,
        correct=richtig
    )

    db.session.add(attempt)
    db.session.commit()

    # ── Levelwechsel erst nach MIN_QUESTIONS Aufgaben ─────────────────────────
    if prog.total_cnt >= MIN_QUESTIONS:
        rate      = prog.correct_cnt / prog.total_cnt
        old_level = current_user.current_level

        # ── AUFSTIEG ──────────────────────────────────────────────────────────
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
                # Kapitel abgeschlossen → nächstes Kapitel, zurück auf A
                current_user.current_level = "A"
                try:
                    p1, p2 = chapter.split(".")
                    next_chapter = f"{p1}.{int(p2) + 1}"
                except Exception:
                    next_chapter = "1.4"
                current_user.current_chapter = next_chapter
                db.session.commit()
                return redirect(url_for("kapitel_abgeschlossen", chapter=chapter, next_chapter=next_chapter))

        # ── ABSTIEG ───────────────────────────────────────────────────────────
        elif rate < RATE_DOWN:
            reset_progress(prog)

            if old_level == "C":
                current_user.current_level = "B"
                db.session.commit()
                flash("⬇️ Abstieg zu Level B – weiter üben!", "warning")

            elif old_level == "B":
                current_user.current_level = "A"
                db.session.commit()
                flash("⬇️ Abstieg zu Level A – Grundlagen wiederholen!", "warning")

            # Bei Level A bleibt man, Theorie-Hinweis wird in lektion() angezeigt
            db.session.commit()

        # ── STABIL (60–79 %) → weiter üben ───────────────────────────────────
        else:
            # Kein Levelwechsel, aber Zähler zurücksetzen damit es nicht ewig weiterläuft
            reset_progress(prog)
            db.session.commit()
            flash("➡️ Weiter so – noch mehr üben für den Aufstieg!", "info")

    return redirect(url_for("lektion", chapter=chapter))


# ── Markierte Aufgaben ─────────────────────────────────────────────────────────

@app.route("/markieren", methods=["POST"])
@login_required
def markieren():
    """Stern beim Ueben: Aufgabe fuer die Lehrperson merken und ueberspringen."""
    chapter = request.form.get("chapter", "1.3")
    frage   = session.get("current_question")
    loesung = session.get("current_solution")

    if not frage:
        return redirect(url_for("lektion", chapter=chapter))

    schon_da = MarkedTask.query.filter_by(
        user_id=current_user.id, question=frage, resolved=False
    ).first()

    if not schon_da:
        db.session.add(MarkedTask(
            user_id=current_user.id,
            chapter=chapter,
            level=current_user.current_level,
            question=frage,
            solution=float(loesung) if loesung is not None else None,
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
        # Prüfen ob E-Mail bereits existiert
        existing =