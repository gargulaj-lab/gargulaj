import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = Path(os.environ.get("DATABASE_FILE", str(BASE_DIR / "data/moje_zeleznice.db")))


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with get_connection() as connection:

        # ==============================================
        # UŽIVATELÉ
        # ==============================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


        # ==============================================
        # JÍZDY
        # ==============================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS journeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                journey_date TEXT NOT NULL,

                start_station TEXT NOT NULL,
                end_station TEXT NOT NULL,

                via_stations TEXT NOT NULL DEFAULT '[]',

                distance_km REAL NOT NULL,

                coordinates TEXT NOT NULL,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )


        # ==============================================
        # MIGRACE: HRANY PROJETÉ TRASY
        # ==============================================
        # Starší databáze už tabulku journeys mají.
        # CREATE TABLE IF NOT EXISTS proto existující tabulku
        # nezmění, takže nový sloupec přidáme bezpečně přes
        # ALTER TABLE pouze tehdy, když ještě neexistuje.

        journey_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(journeys)"
            ).fetchall()
        }

        if "edge_ids" not in journey_columns:
            connection.execute(
                """
                ALTER TABLE journeys
                ADD COLUMN edge_ids TEXT NOT NULL DEFAULT '[]'
                """
            )


        # Index nám později pomůže při načítání
        # jízd konkrétního uživatele.

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_journeys_user_id
            ON journeys(user_id)
            """
        )


        # Index pro statistiky podle data.

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_journeys_user_date
            ON journeys(user_id, journey_date)
            """
        )


        connection.commit()


if __name__ == "__main__":
    init_database()

    print(
        f"Databáze připravena: "
        f"{DATABASE_FILE.resolve()}"
    )