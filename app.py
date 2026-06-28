from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

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


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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


# ── Routen ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


@app.route("/lektion/<chapter>")
@login_required
def lektion(chapter):
    prog    = get_or_create_progress(current_user.id, chapter, current_user.current_level)
    db.session.commit()

    total   = prog.total_cnt   or 0
    correct = prog.correct_cnt or 0
    quote   = int((correct / total) * 100) if total > 0 else 0

    # Aufgabe generieren & Lösung in Session speichern
    frage, loesung = generate_math_task(chapter, current_user.current_level)
    session["current_solution"] = loesung

    # Theorie-Hinweis anzeigen wenn 2 Fehler in Folge
    show_hint = prog.consecutive_err >= CONSECUTIVE_ERR

    return render_template(
        "lektion.html",
        frage=frage,
        chapter=chapter,
        quote=quote,
        geloest=total,
        level=current_user.current_level,
        show_hint=show_hint,
        min_questions=MIN_QUESTIONS,
    )


@app.route("/check", methods=["POST"])
@login_required
def check():
    user_input        = request.form.get("antwort", "").strip().replace(",", ".")
    korrekte_loesung  = session.get("current_solution")
    chapter           = request.form.get("chapter", "1.3")

    try:
        user_val = float(user_input)
    except ValueError:
        flash("Ungültige Eingabe – bitte eine Zahl eingeben.", "error")
        return redirect(url_for("lektion", chapter=chapter))

    prog = get_or_create_progress(current_user.id, chapter, current_user.current_level)

    # ── Antwort auswerten ──────────────────────────────────────────────────────
    if abs(user_val - float(korrekte_loesung)) < 0.0001:
        prog.correct_cnt     += 1
        prog.consecutive_err  = 0
        current_user.xp       = (current_user.xp or 0) + 10
        flash("✅ Richtig!", "success")
    else:
        prog.consecutive_err += 1
        flash(f"❌ Falsch! Richtige Lösung: {int(korrekte_loesung) if korrekte_loesung == int(korrekte_loesung) else korrekte_loesung}", "error")

    prog.total_cnt += 1
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
        existing = User.query.filter_by(email=request.form.get("email")).first()
        if existing:
            flash("Diese E-Mail ist bereits registriert.", "error")
            return render_template("register.html")

        u = User(
            username=request.form.get("username"),
            email=request.form.get("email"),
        )
        u.set_password(request.form.get("password"))
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


# ── Start ──────────────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
