"""SQLite-based persistence for the desktop application.

The original project stored every entity in a separate JSON file. This
repository keeps the same public method names to avoid a risky UI rewrite,
but writes all records through SQLite transactions. Each entity record is
stored as JSON payload so the schema can be evolved incrementally.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import threading
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from config.settings import DEFAULT_SETTINGS


STORE_FILES = {
    "vaccines": "vaccines.json",
    "manufacturers": "manufacturers.json",
    "categories": "categories.json",
    "cold_storage": "cold_storage.json",
    "orders": "orders.json",
    "outbound_records": "outbound_records.json",
    "inventory_records": "inventory_records.json",
    "users": "users.json",
    "roles": "roles.json",
    "suppliers": "suppliers.json",
    "purchase_requests": "purchase_requests.json",
    "temp_humidity_records": "temp_humidity_records.json",
    "recipient_units": "recipient_units.json",
    "operation_logs": "operation_logs.json",
}

FILE_STORES = {filename: store for store, filename in STORE_FILES.items()}


class SQLiteRepository:
    """Small repository with atomic snapshot writes and legacy JSON import."""

    def __init__(
        self,
        base_dir: str | Path | None = None,
        db_filename: str = "vaccine_system.db",
        import_legacy: bool = True,
        db_path: str | Path | None = None,
    ) -> None:
        if getattr(sys, "frozen", False):
            project_root = Path(sys.executable).resolve().parent
        else:
            project_root = Path(__file__).resolve().parent.parent
        self.base_dir = Path(base_dir or project_root / "data")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        configured_path = os.getenv("VACCINE_DB_PATH") if base_dir is None else None
        self.db_path = (
            Path(db_path)
            if db_path
            else Path(configured_path)
            if configured_path
            else self.base_dir / db_filename
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        self._initialize_schema()
        if import_legacy and os.getenv("VACCINE_IMPORT_JSON", "1") != "0":
            self._import_legacy_json()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_schema(self) -> None:
        with self._lock, self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = NORMAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS store_records (
                    store_name TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (store_name, seq)
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def _store_has_records(self, store_name: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM store_records WHERE store_name = ? LIMIT 1",
                (store_name,),
            ).fetchone()
            return row is not None

    def _settings_have_records(self) -> bool:
        with self._connection() as connection:
            row = connection.execute("SELECT 1 FROM settings LIMIT 1").fetchone()
            return row is not None

    def _legacy_imported(self, filename: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT value FROM metadata WHERE key = ?",
                (f"legacy_imported:{filename}",),
            ).fetchone()
            return row is not None

    def _mark_legacy_imported(self, filename: str) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO metadata(key, value) VALUES (?, ?)",
                (f"legacy_imported:{filename}", datetime.now().isoformat()),
            )

    def _import_legacy_json(self) -> None:
        for store_name, filename in STORE_FILES.items():
            source = self.base_dir / filename
            if not source.exists() or self._legacy_imported(filename):
                continue
            if store_name != "operation_logs" and self._store_has_records(store_name):
                self._mark_legacy_imported(filename)
                continue

            try:
                with source.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, list):
                    self._replace_store(store_name, data)
                self._mark_legacy_imported(filename)
            except (OSError, json.JSONDecodeError) as error:
                print(f"迁移旧数据 {filename} 失败: {error}")

        settings_source = self.base_dir / "settings.json"
        if settings_source.exists() and not self._legacy_imported("settings.json"):
            try:
                if not self._settings_have_records():
                    with settings_source.open("r", encoding="utf-8") as file:
                        data = json.load(file)
                    if isinstance(data, dict):
                        self.save_settings(data)
                self._mark_legacy_imported("settings.json")
            except (OSError, json.JSONDecodeError) as error:
                print(f"迁移设置数据失败: {error}")

    def _replace_store(self, store_name: str, records: list[Any]) -> bool:
        rows = [
            (store_name, index, json.dumps(record, ensure_ascii=False))
            for index, record in enumerate(records)
        ]
        with self._lock, self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "DELETE FROM store_records WHERE store_name = ?",
                (store_name,),
            )
            connection.executemany(
                "INSERT INTO store_records(store_name, seq, payload) VALUES (?, ?, ?)",
                rows,
            )
        return True

    def _load_store(self, store_name: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT payload FROM store_records WHERE store_name = ? ORDER BY seq",
                (store_name,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def load_json(self, filename: str, default: Any = None) -> Any:
        if filename == "settings.json":
            return self.load_settings()
        store_name = FILE_STORES.get(filename, Path(filename).stem)
        return self._load_store(store_name)

    def save_json(self, filename: str, data: Any) -> bool:
        if filename == "settings.json":
            return self.save_settings(data)
        store_name = FILE_STORES.get(filename, Path(filename).stem)
        if not isinstance(data, list):
            raise ValueError(f"{filename} 必须保存为列表")
        return self._replace_store(store_name, data)

    def save_snapshot(self, stores: dict[str, list[Any]], settings: dict[str, Any] | None = None) -> bool:
        """Persist all entity lists and settings in one SQLite transaction."""
        with self._lock, self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for store_name, records in stores.items():
                connection.execute(
                    "DELETE FROM store_records WHERE store_name = ?",
                    (store_name,),
                )
                rows = [
                    (store_name, index, json.dumps(record, ensure_ascii=False))
                    for index, record in enumerate(records)
                ]
                connection.executemany(
                    "INSERT INTO store_records(store_name, seq, payload) VALUES (?, ?, ?)",
                    rows,
                )
            if settings is not None:
                for key, value in settings.items():
                    connection.execute(
                        "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
                        (key, json.dumps(value, ensure_ascii=False)),
                    )
        return True

    def load_settings(self) -> dict[str, Any]:
        values = DEFAULT_SETTINGS.copy()
        with self._connection() as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        for row in rows:
            values[row["key"]] = json.loads(row["value"])
        return values

    def save_settings(self, settings: dict[str, Any]) -> bool:
        with self._lock, self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for key, value in settings.items():
                connection.execute(
                    "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)",
                    (key, json.dumps(value, ensure_ascii=False)),
                )
        return True

    def create_backup(self, filename: str | None = None) -> str | None:
        """Create a consistent SQLite backup without copying an active WAL file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = self.backup_dir / f"vaccine_system_{timestamp}.db"
        try:
            with self._connection() as source:
                with closing(sqlite3.connect(backup_path)) as destination:
                    source.backup(destination)
                    destination.commit()
            return str(backup_path)
        except sqlite3.Error as error:
            print(f"创建数据库备份失败: {error}")
            return None

    def create_all_backups(self) -> dict[str, str | None]:
        return {"database": self.create_backup()}

    def list_backups(self, filename: str | None = None) -> list[dict[str, Any]]:
        backups = []
        for path in self.backup_dir.glob("*.db"):
            try:
                stat = path.stat()
                backups.append(
                    {
                        "filename": path.name,
                        "path": str(path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )
            except OSError:
                continue
        backups.sort(key=lambda item: item["modified"], reverse=True)
        return backups

    def restore_from_backup(
        self,
        backup_filename: str,
        target_filename: str | None = None,
    ) -> bool:
        backup_path = self.backup_dir / Path(backup_filename).name
        if not backup_path.is_file():
            return False

        try:
            with closing(sqlite3.connect(backup_path)) as source:
                integrity = source.execute("PRAGMA integrity_check").fetchone()
                if not integrity or integrity[0] != "ok":
                    return False
                with self._connection() as destination:
                    source.backup(destination)
                    destination.commit()
            return True
        except sqlite3.Error as error:
            print(f"恢复数据库备份失败: {error}")
            return False

    def delete_backup(self, backup_filename: str) -> bool:
        backup_path = self.backup_dir / Path(backup_filename).name
        try:
            if not backup_path.is_file():
                return False
            backup_path.unlink()
            return True
        except OSError as error:
            print(f"删除数据库备份失败: {error}")
            return False

    def load_vaccines(self):
        return self._load_store("vaccines")

    def save_vaccines(self, vaccines):
        return self._replace_store("vaccines", vaccines)

    def load_manufacturers(self):
        return self._load_store("manufacturers")

    def save_manufacturers(self, manufacturers):
        return self._replace_store("manufacturers", manufacturers)

    def load_categories(self):
        return self._load_store("categories")

    def save_categories(self, categories):
        return self._replace_store("categories", categories)

    def load_cold_storage(self):
        return self._load_store("cold_storage")

    def save_cold_storage(self, cold_storages):
        return self._replace_store("cold_storage", cold_storages)

    def load_orders(self):
        return self._load_store("orders")

    def save_orders(self, orders):
        return self._replace_store("orders", orders)

    def load_outbound_records(self):
        return self._load_store("outbound_records")

    def save_outbound_records(self, records):
        return self._replace_store("outbound_records", records)

    def load_inventory_records(self):
        return self._load_store("inventory_records")

    def save_inventory_records(self, records):
        return self._replace_store("inventory_records", records)

    def load_users(self):
        return self._load_store("users")

    def save_users(self, users):
        return self._replace_store("users", users)

    def load_roles(self):
        return self._load_store("roles")

    def save_roles(self, roles):
        return self._replace_store("roles", roles)

    def load_suppliers(self):
        return self._load_store("suppliers")

    def save_suppliers(self, suppliers):
        return self._replace_store("suppliers", suppliers)

    def load_purchase_requests(self):
        return self._load_store("purchase_requests")

    def save_purchase_requests(self, requests):
        return self._replace_store("purchase_requests", requests)

    def load_temp_humidity_records(self):
        return self._load_store("temp_humidity_records")

    def save_temp_humidity_records(self, records):
        return self._replace_store("temp_humidity_records", records)

    def load_recipient_units(self):
        return self._load_store("recipient_units")

    def save_recipient_units(self, units):
        return self._replace_store("recipient_units", units)

    def load_operation_logs(self):
        return self._load_store("operation_logs")

    def save_operation_logs(self, logs):
        return self._replace_store("operation_logs", logs)


repository = SQLiteRepository()
