import json
import os
import tempfile
import unittest
from pathlib import Path

from utils.data_repository import SQLiteRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_snapshot_round_trip(self):
        repository = SQLiteRepository(base_dir=self.base_dir, import_legacy=False)
        users = [{"id": 1, "username": "tester", "role": "普通操作员"}]
        vaccines = [{"id": "V-001", "name": "示例疫苗", "quantity": 20}]

        self.assertTrue(repository.save_snapshot({"users": users, "vaccines": vaccines}))

        self.assertEqual(repository.load_users(), users)
        self.assertEqual(repository.load_vaccines(), vaccines)

    def test_settings_round_trip(self):
        repository = SQLiteRepository(base_dir=self.base_dir, import_legacy=False)

        repository.save_settings({"system_name": "测试系统", "min_stock": 5})
        settings = repository.load_settings()

        self.assertEqual(settings["system_name"], "测试系统")
        self.assertEqual(settings["min_stock"], 5)
        self.assertIn("expiry_warning_days", settings)

    def test_legacy_json_is_imported_once(self):
        previous = os.environ.get("VACCINE_IMPORT_JSON")
        os.environ["VACCINE_IMPORT_JSON"] = "1"
        try:
            source = self.base_dir / "vaccines.json"
            source.write_text(
                json.dumps([{"id": 1, "name": "旧数据疫苗"}], ensure_ascii=False),
                encoding="utf-8",
            )

            repository = SQLiteRepository(base_dir=self.base_dir, import_legacy=True)
            self.assertEqual(repository.load_vaccines()[0]["name"], "旧数据疫苗")

            repository.save_vaccines([{"id": 2, "name": "新数据"}])
            reloaded = SQLiteRepository(base_dir=self.base_dir, import_legacy=True)
            self.assertEqual(reloaded.load_vaccines(), [{"id": 2, "name": "新数据"}])
        finally:
            if previous is None:
                os.environ.pop("VACCINE_IMPORT_JSON", None)
            else:
                os.environ["VACCINE_IMPORT_JSON"] = previous

    def test_backup_and_restore(self):
        repository = SQLiteRepository(base_dir=self.base_dir, import_legacy=False)
        repository.save_users([{"id": 1, "username": "before"}])

        backup_path = repository.create_backup()
        self.assertIsNotNone(backup_path)

        repository.save_users([{"id": 1, "username": "after"}])
        self.assertEqual(repository.load_users()[0]["username"], "after")

        backup_name = repository.list_backups()[0]["filename"]
        self.assertTrue(repository.restore_from_backup(backup_name))
        self.assertEqual(repository.load_users()[0]["username"], "before")
        self.assertTrue(repository.delete_backup(backup_name))


if __name__ == "__main__":
    unittest.main()
