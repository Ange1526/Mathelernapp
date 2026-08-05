# -*- coding: utf-8 -*-
"""Drei neue Spalten in der Tabelle `user` anlegen: streak, bester_streak,
last_active.

Notwendig, weil `db.create_all()` nur FEHLENDE TABELLEN anlegt. Eine
bestehende Tabelle wird nicht um neue Spalten erweitert — ohne dieses Skript
laeuft die App mit einer alten Datenbank in einen Fehler.

Aufruf unter Windows:

    python migration_streak.py

Das Skript ist gefahrlos mehrfach ausfuehrbar: was schon da ist, wird
uebersprungen. Bestehende Daten werden nicht angeruehrt.
"""
from sqlalchemy import inspect, text

from app import app, db

NEUE_SPALTEN = {
    "streak": "INTEGER DEFAULT 0",
    "bester_streak": "INTEGER DEFAULT 0",
    "last_active": "DATE",
}


def main():
    with app.app_context():
        # Fehlende Tabellen zuerst — BauformStand, KapitelStand, Lernweg
        # entstehen so beim ersten Lauf mit.
        db.create_all()

        vorhanden = {s["name"] for s in inspect(db.engine).get_columns("user")}

        for name, typ in NEUE_SPALTEN.items():
            if name in vorhanden:
                print(f"  schon da:   user.{name}")
                continue
            db.session.execute(text(f'ALTER TABLE "user" ADD COLUMN {name} {typ}'))
            print(f"  angelegt:   user.{name}")

        db.session.commit()

        # Bestehende Konten auf 0 setzen statt auf NULL — sonst zeigt die
        # Flamme im Header nichts an, bis zum ersten Mal geuebt wird.
        db.session.execute(text(
            'UPDATE "user" SET streak = 0 WHERE streak IS NULL'))
        db.session.execute(text(
            'UPDATE "user" SET bester_streak = 0 WHERE bester_streak IS NULL'))
        db.session.commit()

        print("\nFertig.")


if __name__ == "__main__":
    main()
