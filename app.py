from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

app = Flask(__name__)

# ── SVE-Konfiguration (Render & Lokal kompatibel) ──────────────────────────────
# Holt den Secret Key von Render, nutzt lokal den Fallback
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-matura-2024")

# Verarbeitet die Datenbank-URL (behebt das "postgres://" vs "postgresql://" Problem bei SQLAlchemy)
database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ── Modelle ────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    xp = db.Column(db.Integer, default=0)
    current_level = db.Column(db.String(1), default="B")  
    current_chapter = db.Column(db.String(10), default="1.3")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    chapter = db.Column(db.String(10)) 
    level = db.Column(db.String(1))  
    correct_cnt = db.Column(db.Integer, default=0) 
    total_cnt = db.Column(db.Integer, default=0) 

@login_manager.user_loader
def load_user(user_id):
    # Verwendung von session.get() statt query.get(), da query.get() veraltet ist
    return db.session.get(User, int(user_id))

def generate_math_task(chapter, level):
    span = 10 if level == "A" else 50 if level == "B" else 100
    a, b = random.randint(-span, span), random.randint(-span, span)
    if chapter == "1.3":
        if level == "C":
            c = random.randint(1, 20)
            return f"{a} + ({b}) + ({c})", float(a + b + c)
        return f"{a} + ({b})", float(a + b)
    return f"{a} - ({b})", float(a - b)

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
    prog = Progress.query.filter_by(user_id=current_user.id, chapter=chapter, level=current_user.current_level).first()
    quote = 0
    geloest = 0
    if prog:
        c_cnt = prog.correct_cnt or 0
        t_cnt = prog.total_cnt or 0
        geloest = t_cnt
        if t_cnt > 0:
            quote = int((c_cnt / t_cnt) * 100)
    
    frage, loesung = generate_math_task(chapter, current_user.current_level)
    session['current_solution'] = loesung
    return render_template("lektion.html", frage=frage, chapter=chapter, quote=quote, geloest=geloest)

@app.route("/check", methods=["POST"])
@login_required
def check():
    user_input = request.form.get("antwort", "").strip().replace(',', '.')
    korrekte_loesung = session.get('current_solution')
    chapter = request.form.get("chapter", "1.3")
    
    try:
        user_val = float(user_input)
        prog = Progress.query.filter_by(user_id=current_user.id, chapter=chapter, level=current_user.current_level).first()
        
        if not prog:
            prog = Progress(user_id=current_user.id, chapter=chapter, level=current_user.current_level, correct_cnt=0, total_cnt=0)
            db.session.add(prog)

        if prog.correct_cnt is None: prog.correct_cnt = 0
        if prog.total_cnt is None: prog.total_cnt = 0

        if abs(user_val - float(korrekte_loesung)) < 0.0001:
            prog.correct_cnt += 1
            current_user.xp = (current_user.xp or 0) + 10
            flash("Richtig!", "success")
        else:
            flash(f"Falsch! Lösung: {korrekte_loesung}", "error")

        prog.total_cnt += 1
        db.session.commit()

        # Wechsel erst ab 20 Aufgaben
        if prog.total_cnt >= 20:
            rate = prog.correct_cnt / prog.total_cnt
            if rate >= 0.8:
                old_lvl = current_user.current_level
                prog.correct_cnt = 0
                prog.total_cnt = 0
                
                if old_lvl == "A":
                    current_user.current_level = "B"
                    db.session.commit()
                    return redirect(url_for('levelup_a_b'))
                elif old_lvl == "B":
                    current_user.current_level = "C"
                    db.session.commit()
                    return redirect(url_for('levelup_b_c'))
                elif old_lvl == "C":
                    current_user.current_level = "B"
                    try:
                        p1, p2 = chapter.split('.')
                        chapter = f"{p1}.{int(p2)+1}"
                    except: chapter = "1.4"
                    db.session.commit()
                    return redirect(url_for('lektion', chapter=chapter))

    except:
        flash("Ungültige Eingabe", "error")
    
    db.session.commit()
    return redirect(url_for("lektion", chapter=chapter))

@app.route("/levelup_a_b")
@login_required
def levelup_a_b(): return render_template("levelup_a_b.html")

@app.route("/levelup_b_c")
@login_required
def levelup_b_c(): return render_template("levelup_b_c.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = User.query.filter_by(email=request.form.get("email")).first()
        if u and u.check_password(request.form.get("password")):
            login_user(u); return redirect(url_for("dashboard"))
        flash("Fehler beim Login", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = User(username=request.form.get("username"), email=request.form.get("email"))
        u.set_password(request.form.get("password"))
        db.session.add(u)
        db.session.commit()
        login_user(u); return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context(): 
        db.create_all()
    app.run(debug=True)