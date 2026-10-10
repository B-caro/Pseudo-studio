import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.projects.store import ProjectConflict, ProjectNotFound, ProjectStore


class ProjectStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.store = ProjectStore(Path(self.directory.name) / "data.sqlite3")

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_create_update_duplicate_delete_and_version_conflict(self) -> None:
        project = self.store.create_project("Suma", "Inicio\nFin\n")
        self.assertEqual(project["version"], 1)
        updated = self.store.update_project(project["id"], 1, name="Suma 2", source="Inicio\nEscribir 2\nFin\n")
        self.assertEqual((updated["name"], updated["version"]), ("Suma 2", 2))
        self.assertNotEqual(project["source_hash"], updated["source_hash"])
        with self.assertRaises(ProjectConflict):
            self.store.update_project(project["id"], 1, name="stale", source="")
        duplicate = self.store.duplicate_project(project["id"])
        self.assertEqual(duplicate["source"], updated["source"])
        self.store.delete_project(project["id"])
        with self.assertRaises(ProjectNotFound):
            self.store.get_project(project["id"])

    def test_backup_restores_projects_and_run_history_excludes_input_values(self) -> None:
        project = self.store.create_project("Privado", "Inicio\nFin\n")
        self.store.record_run(
            {
                "run_id": "r1",
                "source_hash": "s" * 64,
                "artifact_hash": "a" * 64,
                "target": "python",
                "runtime_version": "3.12.14",
                "status": "completed",
                "exit_code": 0,
                "duration_ms": 2.5,
            },
            project["id"],
        )
        backup = self.store.backup(Path(self.directory.name) / "backup.sqlite3")
        with sqlite3.connect(backup) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(runs)")}
            self.assertNotIn("inputs", columns)
            self.assertEqual(connection.execute("SELECT count(*) FROM projects").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_health_check_runs_against_sqlite(self) -> None:
        self.assertTrue(self.store.health())


if __name__ == "__main__":
    unittest.main()
