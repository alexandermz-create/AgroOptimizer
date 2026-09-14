from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "agrooptimizer.db"

DEFAULT_CROPS = [
    ("Maíz", "Grano", 4500.0, 5.5, 3000.0, 20.0, 8.0, 4200.0, 1200.0, 22000.0, 180.0, 1),
    ("Frijol", "Grano", 7000.0, 1.8, 2500.0, 18.0, 5.0, 3200.0, 900.0, 12600.0, 140.0, 1),
    ("Tomate", "Hortaliza", 18000.0, 7.0, 8000.0, 35.0, 12.0, 5000.0, 2500.0, 35000.0, 250.0, 1),
    ("Chile", "Hortaliza", 15000.0, 4.5, 6000.0, 30.0, 10.0, 4500.0, 1800.0, 25000.0, 220.0, 1),
    ("Pepino", "Hortaliza", 12500.0, 5.0, 5500.0, 28.0, 9.0, 4000.0, 1600.0, 20000.0, 210.0, 1),
    ("Alfalfa", "Forraje", 9000.0, 8.0, 3500.0, 22.0, 7.0, 6500.0, 1000.0, 18000.0, 190.0, 1),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    yield_per_ha REAL NOT NULL CHECK(yield_per_ha >= 0),
    cost REAL NOT NULL CHECK(cost >= 0),
    labor REAL NOT NULL CHECK(labor >= 0),
    water REAL NOT NULL CHECK(water >= 0),
    light REAL NOT NULL CHECK(light >= 0),
    min_temp REAL NOT NULL,
    max_temp REAL NOT NULL,
    max_ha REAL NOT NULL CHECK(max_ha >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM crops").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO crops
                (name, category, price, yield_per_ha, cost, labor, water, light,
                 min_temp, max_temp, max_ha, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                DEFAULT_CROPS,
            )


def _validate(name: str, price: float, yield_per_ha: float, cost: float,
              labor: float, water: float, light: float, min_temp: float,
              max_temp: float, max_ha: float) -> None:
    if not name.strip():
        raise ValueError("El nombre del cultivo es obligatorio.")
    values = [price, yield_per_ha, cost, labor, water, light, max_ha]
    if any(float(v) < 0 for v in values):
        raise ValueError("Los valores numéricos no pueden ser negativos.")
    if min_temp > max_temp:
        raise ValueError("La temperatura mínima no puede ser mayor que la máxima.")


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def get_crops(active_only: bool = True) -> list[dict[str, Any]]:
    query = "SELECT * FROM crops"
    if active_only:
        query += " WHERE active = 1"
    query += " ORDER BY name"
    with get_connection() as conn:
        return [_row_to_dict(r) for r in conn.execute(query).fetchall()]


def add_crop(name: str, category: str, price: float, yield_per_ha: float,
             cost: float, labor: float, water: float, light: float,
             min_temp: float, max_temp: float, max_ha: float, active: bool = True) -> None:
    _validate(name, price, yield_per_ha, cost, labor, water, light, min_temp, max_temp, max_ha)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO crops
            (name, category, price, yield_per_ha, cost, labor, water, light,
             min_temp, max_temp, max_ha, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), category, price, yield_per_ha, cost, labor, water,
             light, min_temp, max_temp, max_ha, int(active)),
        )


def update_crop(crop_id: int, name: str, category: str, price: float, yield_per_ha: float,
                cost: float, labor: float, water: float, light: float,
                min_temp: float, max_temp: float, max_ha: float, active: bool) -> None:
    _validate(name, price, yield_per_ha, cost, labor, water, light, min_temp, max_temp, max_ha)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE crops SET name=?, category=?, price=?, yield_per_ha=?, cost=?,
            labor=?, water=?, light=?, min_temp=?, max_temp=?, max_ha=?, active=?
            WHERE id=?
            """,
            (name.strip(), category, price, yield_per_ha, cost, labor, water,
             light, min_temp, max_temp, max_ha, int(active), crop_id),
        )


def delete_crop(crop_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM crops WHERE id=?", (crop_id,))


def get_dashboard_stats() -> dict[str, float | int]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS crop_count,
                   SUM(active) AS active_count,
                   COALESCE(AVG(price * yield_per_ha - cost), 0) AS avg_profit,
                   COALESCE(AVG(water), 0) AS avg_water
            FROM crops
            """
        ).fetchone()
    return {
        "crop_count": int(row["crop_count"] or 0),
        "active_count": int(row["active_count"] or 0),
        "avg_profit": float(row["avg_profit"] or 0),
        "avg_water": float(row["avg_water"] or 0),
    }
