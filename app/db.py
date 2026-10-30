"""Persistence layer: SQLite connection + a generic Repository."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL, age INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS doctors(
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, specialty TEXT NOT NULL, fee REAL NOT NULL);
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL, doctor_id INTEGER NOT NULL,
    slot TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'BOOKED');
CREATE TABLE IF NOT EXISTS invoices(
    id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL, amount REAL NOT NULL,
    paid INTEGER NOT NULL DEFAULT 0, txn_id TEXT);
"""


def connect(path: str = "medislot.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


class Repository:
    """One class serves every table, so a new module needs no new SQL code."""

    def __init__(self, conn: sqlite3.Connection, table: str):
        self.conn, self.table = conn, table

    def add(self, **data) -> dict:
        cols = ", ".join(data)
        marks = ", ".join("?" * len(data))
        cur = self.conn.execute(
            f"INSERT INTO {self.table} ({cols}) VALUES ({marks})", tuple(data.values()))
        self.conn.commit()
        return self.get(cur.lastrowid)

    def get(self, id: int) -> dict | None:
        row = self.conn.execute(f"SELECT * FROM {self.table} WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def find(self, **where) -> list[dict]:
        sql = f"SELECT * FROM {self.table}"
        if where:
            sql += " WHERE " + " AND ".join(f"{k} = ?" for k in where)
        return [dict(r) for r in self.conn.execute(sql, tuple(where.values()))]

    def update(self, id: int, **data) -> dict:
        sets = ", ".join(f"{k} = ?" for k in data)
        self.conn.execute(f"UPDATE {self.table} SET {sets} WHERE id = ?", (*data.values(), id))
        self.conn.commit()
        return self.get(id)
