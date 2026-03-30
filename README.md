# MeineApp – Flask Starter

Maturaarbeit Starter-Code mit Login, PostgreSQL und Deployment auf Render.com.

## Lokale Entwicklung

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. App starten (SQLite wird automatisch erstellt)
python app.py

# → App läuft auf http://localhost:5000
```

## Deployment auf Render.com

1. Code auf GitLab / GitHub pushen
2. Auf render.com → "New Web Service" → Repo verbinden
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Umgebungsvariablen setzen:
   - `SECRET_KEY` → langer, zufälliger String (z.B. mit Python: `import secrets; secrets.token_hex(32)`)
   - `DATABASE_URL` → PostgreSQL-URL von Supabase

## Supabase (Datenbank)

1. Kostenloses Konto auf supabase.com erstellen
2. Neues Projekt anlegen
3. Settings → Database → Connection String kopieren
4. Als `DATABASE_URL` bei Render.com eintragen

## Projektstruktur

```
webapp/
├── app.py              ← Flask App, Routen, Datenbankmodelle
├── requirements.txt    ← Python-Pakete
├── Procfile            ← Start-Befehl für Render.com
├── templates/
│   ├── base.html       ← Grundgerüst (Navbar, Footer)
│   ├── index.html      ← Startseite
│   ├── login.html      ← Login-Formular
│   ├── register.html   ← Registrierungs-Formular
│   └── dashboard.html  ← Geschützter Bereich
└── static/
    └── css/
        └── style.css   ← Alle Styles
```

## Eigene Tabellen hinzufügen

In `app.py` ein neues Modell definieren:

```python
class MeinModell(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    titel      = db.Column(db.String(200), nullable=False)
    inhalt     = db.Column(db.Text)
    erstellt   = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
```

Dann `db.create_all()` beim Start ausführen – fertig.
