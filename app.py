from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# ── Konfiguration ──────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-bitte-aendern")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///local.db"          # lokal: SQLite | Produktion: PostgreSQL-URL von Supabase
).replace("postgres://", "postgresql://")          # Render.com-Fix
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Bitte zuerst einloggen."

# ── Modelle ────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    # Eigene Felder hier ergänzen ↓
    notes         = db.relationship("Note", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    """Beispiel-Modell – kann durch eigene Tabelle ersetzt werden."""
    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Routen ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"].strip()
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Benutzername bereits vergeben.", "error")
        elif User.query.filter_by(email=email).first():
            flash("E-Mail bereits registriert.", "error")
        elif len(password) < 6:
            flash("Passwort muss mindestens 6 Zeichen lang sein.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Konto erstellt – willkommen!", "success")
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"].strip().lower()).first()
        if user and user.check_password(request.form["password"]):
            login_user(user, remember=request.form.get("remember") == "on")
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("E-Mail oder Passwort falsch.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Erfolgreich ausgeloggt.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        content = request.form["content"].strip()
        if content:
            note = Note(content=content, author=current_user)
            db.session.add(note)
            db.session.commit()
            flash("Notiz gespeichert.", "success")
    notes = Note.query.filter_by(user_id=current_user.id)\
                      .order_by(Note.created_at.desc()).all()
    return render_template("dashboard.html", notes=notes)


@app.route("/note/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Kein Zugriff.", "error")
        return redirect(url_for("dashboard"))
    db.session.delete(note)
    db.session.commit()
    flash("Notiz gelöscht.", "success")
    return redirect(url_for("dashboard"))


# ── Start ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
