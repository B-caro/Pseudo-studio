"""SQLite persistence with version-checked project updates and privacy-safe run records."""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class ProjectNotFound(LookupError):
    pass


class ProjectConflict(RuntimeError):
    pass


class ProjectStore:
    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    def migrate(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
                )
                applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
                if 1 not in applied:
                    connection.execute(
                        """CREATE TABLE projects (
                            id TEXT PRIMARY KEY,
                            name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 120),
                            source TEXT NOT NULL,
                            source_hash TEXT NOT NULL,
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL,
                            version INTEGER NOT NULL CHECK(version >= 1)
                        )"""
                    )
                    connection.execute(
                        """CREATE TABLE runs (
                            id TEXT PRIMARY KEY,
                            project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
                            source_hash TEXT NOT NULL,
                            artifact_hash TEXT NOT NULL,
                            target TEXT NOT NULL CHECK(target IN ('python','javascript')),
                            runtime_version TEXT NOT NULL,
                            status TEXT NOT NULL,
                            exit_code INTEGER,
                            duration_ms REAL NOT NULL,
                            created_at TEXT NOT NULL
                        )"""
                    )
                    connection.execute("CREATE INDEX runs_created_at_idx ON runs(created_at DESC)")
                    connection.execute(
                        "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                        (1, self._now()),
                    )
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _digest(source: str) -> str:
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    @staticmethod
    def _project(row: sqlite3.Row) -> dict[str, Any]:
        return {key: row[key] for key in ("id", "name", "source", "source_hash", "created_at", "updated_at", "version")}

    def health(self) -> bool:
        with self._connection() as connection:
            version = connection.execute(
                "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
            ).fetchone()
            integrity = connection.execute("PRAGMA quick_check").fetchone()
        return bool(version and version[0] == self.SCHEMA_VERSION and integrity and integrity[0] == "ok")

    def list_projects(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM projects ORDER BY updated_at DESC, name COLLATE NOCASE").fetchall()
        return [self._project(row) for row in rows]

    def get_project(self, project_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise ProjectNotFound(project_id)
        return self._project(row)

    def create_project(self, name: str, source: str) -> dict[str, Any]:
        project_id = uuid.uuid4().hex
        now = self._now()
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO projects(id,name,source,source_hash,created_at,updated_at,version) VALUES(?,?,?,?,?,?,1)",
                (project_id, name.strip(), source, self._digest(source), now, now),
            )
        return self.get_project(project_id)

    def update_project(self, project_id: str, expected_version: int, *, name: str, source: str) -> dict[str, Any]:
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT version FROM projects WHERE id = ?", (project_id,)).fetchone()
            if row is None:
                connection.execute("ROLLBACK")
                raise ProjectNotFound(project_id)
            if row["version"] != expected_version:
                connection.execute("ROLLBACK")
                raise ProjectConflict(f"Expected version {expected_version}; current version is {row['version']}.")
            cursor = connection.execute(
                """UPDATE projects SET name = ?, source = ?, source_hash = ?, updated_at = ?, version = version + 1
                   WHERE id = ? AND version = ?""",
                (name.strip(), source, self._digest(source), self._now(), project_id, expected_version),
            )
            if cursor.rowcount != 1:
                connection.execute("ROLLBACK")
                raise ProjectConflict("El proyecto cambió mientras se guardaba.")
            connection.execute("COMMIT")
        return self.get_project(project_id)

    def duplicate_project(self, project_id: str, name: str | None = None) -> dict[str, Any]:
        original = self.get_project(project_id)
        return self.create_project(name or f"{original['name']} (copia)", original["source"])

    def delete_project(self, project_id: str) -> None:
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        if cursor.rowcount == 0:
            raise ProjectNotFound(project_id)

    def record_run(self, result: dict[str, Any], project_id: str | None = None) -> None:
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO runs(id,project_id,source_hash,artifact_hash,target,runtime_version,status,exit_code,duration_ms,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (
                    result["run_id"],
                    project_id,
                    result["source_hash"],
                    result["artifact_hash"],
                    result["target"],
                    result["runtime_version"],
                    result["status"],
                    result["exit_code"],
                    result["duration_ms"],
                    self._now(),
                ),
            )

    def list_runs(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id,project_id,source_hash,artifact_hash,target,runtime_version,status,exit_code,duration_ms,created_at FROM runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def backup(self, destination: str | Path) -> Path:
        destination = Path(destination).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as source:
            target = sqlite3.connect(destination)
            try:
                source.backup(target)
            finally:
                target.close()
        return destination
