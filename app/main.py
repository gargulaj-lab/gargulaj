import os
from pathlib import Path
import sqlite3
import json

from fastapi import FastAPI, Form, Request, Query
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from starlette.middleware.sessions import SessionMiddleware
from app.railway import (
    find_route,
    find_route_via,
    stations,
    edge_length,
    edge_coordinates,
)
from app.database import get_connection, init_database


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(os.environ.get("RAIL_STATIC_DIR", str(BASE_DIR / "static")))

app = FastAPI(title="Moje železnice")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

password_hash = PasswordHash.recommended()

init_database()


# Pro lokální vývoj.
# Před nasazením aplikace na internet použijeme
# náhodný tajný klíč uložený mimo zdrojový kód.
SESSION_SECRET = os.environ.get(
    "SESSION_SECRET",
    "local-development-only-change-before-deployment"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False
)


@app.get("/")
def home(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    registered = (
        request.query_params.get("registered") == "1"
    )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "registered": registered
        }
    )


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    email = email.strip().lower()

    with get_connection() as connection:

        user = connection.execute(
            """
            SELECT
                id,
                email,
                password_hash
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error":
                    "Nesprávný e-mail nebo heslo."
            },
            status_code=400
        )

    if not password_hash.verify(
        password,
        user["password_hash"]
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error":
                    "Nesprávný e-mail nebo heslo."
            },
            status_code=400
        )

    request.session.clear()
    request.session["user_id"] = user["id"]

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.get("/register")
def register_page(request: Request):

    if request.session.get("user_id"):
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
):

    email = email.strip().lower()

    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error":
                    "Zadaná hesla se neshodují."
            },
            status_code=400
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error":
                    "Heslo musí mít alespoň 8 znaků."
            },
            status_code=400
        )

    hashed_password = password_hash.hash(password)

    try:

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO users (
                    email,
                    password_hash
                )
                VALUES (?, ?)
                """,
                (
                    email,
                    hashed_password
                )
            )

            connection.commit()

    except sqlite3.IntegrityError:

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error":
                    "Účet s tímto e-mailem už existuje."
            },
            status_code=400
        )

    return RedirectResponse(
        url="/?registered=1",
        status_code=303
    )


@app.get("/dashboard")
def dashboard(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    with get_connection() as connection:

        user = connection.execute(
            """
            SELECT
                id,
                email
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

    if user is None:
        request.session.clear()

        return RedirectResponse(
            url="/",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "email": user["email"],
            "demo_mode": "RAIL_GRAPH_FILE" not in os.environ
        }
    )


@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303
    )

class JourneyCreate(BaseModel):
    journey_date: str
    start: str
    end: str
    via: list[str] = []

@app.get("/api/route")
def api_route(
    request: Request,
    start: str,
    end: str,
    via: list[str] = Query(default=[])
):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    station_names = [start]

    station_names.extend(via)

    station_names.append(end)

    return find_route_via(
        station_names
    )

@app.post("/api/journeys")
def create_journey(
    request: Request,
    journey: JourneyCreate
):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    station_names = [journey.start]
    station_names.extend(journey.via)
    station_names.append(journey.end)

    # Trasu znovu spočítá server.
    route = find_route_via(station_names)

    if "error" in route:
        return {
            "error": route["error"]
        }

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO journeys (
                user_id,
                journey_date,
                start_station,
                end_station,
                via_stations,
                distance_km,
                coordinates,
                edge_ids
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                journey.journey_date,
                route["start"],
                route["end"],
                json.dumps(
                    route["via"],
                    ensure_ascii=False
                ),
                route["distance_km"],
                json.dumps(
                    route["coordinates"]
                ),
                json.dumps(
                    route["edge_ids"]
                )
            )
        )

        connection.commit()

        journey_id = cursor.lastrowid

    return {
        "success": True,
        "journey_id": journey_id,
        "distance_km": route["distance_km"],
        "edge_count": len(route["edge_ids"]),
        "message": "Jízda byla uložena."
    }

@app.get("/api/journeys")
def get_journeys(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                journey_date,
                start_station,
                end_station,
                via_stations,
                distance_km,
                coordinates,
                edge_ids,
                created_at
            FROM journeys
            WHERE user_id = ?
            ORDER BY journey_date, id
            """,
            (user_id,)
        ).fetchall()

    journeys = []

    for row in rows:
        journeys.append(
            {
                "id": row["id"],
                "journey_date": row["journey_date"],
                "start": row["start_station"],
                "end": row["end_station"],
                "via": json.loads(
                    row["via_stations"]
                ),
                "distance_km": row["distance_km"],
                "coordinates": json.loads(
                    row["coordinates"]
                ),
                "edge_ids": json.loads(
                    row["edge_ids"]
                ),
                "created_at": row["created_at"]
            }
        )

    return {
        "journeys": journeys,
        "count": len(journeys)
    }

@app.get("/api/stats")
def api_stats(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT

                COALESCE(
                    SUM(
                        CASE
                            WHEN strftime(
                                '%Y-%m',
                                journey_date
                            ) = strftime(
                                '%Y-%m',
                                'now',
                                'localtime'
                            )
                            THEN distance_km
                            ELSE 0
                        END
                    ),
                    0
                ) AS month_km,

                COALESCE(
                    SUM(
                        CASE
                            WHEN strftime(
                                '%Y',
                                journey_date
                            ) = strftime(
                                '%Y',
                                'now',
                                'localtime'
                            )
                            THEN distance_km
                            ELSE 0
                        END
                    ),
                    0
                ) AS year_km,

                COALESCE(
                    SUM(distance_km),
                    0
                ) AS total_km

            FROM journeys

            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()


        edge_rows = connection.execute(
            """
            SELECT edge_ids
            FROM journeys
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchall()

    unique_edges = set()

    for edge_row in edge_rows:
        try:
            edge_ids = json.loads(edge_row["edge_ids"] or "[]")
        except (json.JSONDecodeError, TypeError):
            edge_ids = []

        unique_edges.update(edge_ids)

    unique_km = sum(
        edge_length(edge_id)
        for edge_id in unique_edges
    )

    return {
        "month_km": round(float(row["month_km"]), 3),
        "year_km": round(float(row["year_km"]), 3),
        "total_km": round(float(row["total_km"]), 3),
        "unique_km": round(float(unique_km), 3),
        "unique_edges": len(unique_edges)
    }

@app.get("/api/network/travelled")
def api_travelled_network(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT journey_date, edge_ids
            FROM journeys
            WHERE user_id = ?
            ORDER BY journey_date, id
            """,
            (user_id,)
        ).fetchall()

    edge_stats = {}

    for row in rows:
        try:
            journey_edges = json.loads(row["edge_ids"] or "[]")
        except (json.JSONDecodeError, TypeError):
            journey_edges = []

        # Jedna jízda započítá konkrétní hranu maximálně jednou.
        # Tím se případná smyčka v jedné uložené trase nepočítá dvakrát.
        for edge_id in set(int(value) for value in journey_edges):
            stats = edge_stats.setdefault(
                edge_id,
                {
                    "count": 0,
                    "first_date": row["journey_date"],
                    "last_date": row["journey_date"]
                }
            )

            stats["count"] += 1

            if row["journey_date"] < stats["first_date"]:
                stats["first_date"] = row["journey_date"]

            if row["journey_date"] > stats["last_date"]:
                stats["last_date"] = row["journey_date"]

    result_edges = []
    total_km = 0.0

    for edge_id in sorted(edge_stats):
        length_km = edge_length(edge_id)
        total_km += length_km
        stats = edge_stats[edge_id]

        result_edges.append({
            "edge_id": edge_id,
            "length_km": round(float(length_km), 6),
            "coordinates": edge_coordinates(edge_id),
            "journey_count": stats["count"],
            "first_date": stats["first_date"],
            "last_date": stats["last_date"]
        })

    return {
        "edges": result_edges,
        "unique_edges": len(result_edges),
        "unique_km": round(total_km, 3)
    }


@app.get("/api/stations")
def api_stations(
    request: Request,
    q: str = ""
):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    query = q.strip().casefold()

    if len(query) < 2:
        return {
            "stations": []
        }

    results = []

    for station in stations:

        name = station.get("name")

        if not name:
            continue

        if query in name.casefold():
            results.append(name)

    # odstranění duplicit
    results = list(dict.fromkeys(results))

    # názvy začínající hledaným textem dáme nahoru
    results.sort(
        key=lambda name: (
            not name.casefold().startswith(query),
            name.casefold()
        )
    )

    return {
        "stations": results[:10]
    }

@app.delete("/api/journeys/{journey_id}")
def delete_journey(
    journey_id: int,
    request: Request
):
    user_id = request.session.get("user_id")

    if not user_id:
        return {
            "error": "Uživatel není přihlášen."
        }

    with get_connection() as connection:

        journey = connection.execute(
            """
            SELECT id
            FROM journeys
            WHERE id = ?
              AND user_id = ?
            """,
            (
                journey_id,
                user_id
            )
        ).fetchone()

        if not journey:
            return {
                "error": "Jízda nebyla nalezena."
            }

        connection.execute(
            """
            DELETE FROM journeys
            WHERE id = ?
              AND user_id = ?
            """,
            (
                journey_id,
                user_id
            )
        )

        connection.commit()

    return {
        "success": True,
        "deleted_id": journey_id
    }

