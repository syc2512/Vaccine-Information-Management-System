import os
import tempfile
import unittest
from pathlib import Path

from services.vaccine_service import VaccineService
from utils.data_repository import SQLiteRepository
from utils.security import is_password_hash


def build_service(base_dir):
    repository = SQLiteRepository(base_dir=base_dir, import_legacy=False)
    return VaccineService(repository=repository)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_admin_and_authentication(self):
        service = build_service(self.base_dir)

        result = service.authenticate("admin", os.environ["VACCINE_ADMIN_PASSWORD"])

        self.assertTrue(result["success"])
        self.assertEqual(result["user"]["role"], "超级管理员")
        self.assertTrue(is_password_hash(service.users[0]["password"]))

    def test_user_changes_and_logs_survive_restart(self):
        service = build_service(self.base_dir)
        service.authenticate("admin", os.environ["VACCINE_ADMIN_PASSWORD"])
        service.create_user("operator", "operator-password", "普通操作员")
        service.update_user(service.users[-1]["id"], "operator2", "普通操作员", "new-password")

        restarted = VaccineService(
            repository=SQLiteRepository(base_dir=self.base_dir, import_legacy=False)
        )

        self.assertTrue(any(user["username"] == "operator2" for user in restarted.users))
        self.assertTrue(
            any(log["action"] == "修改用户：operator2" for log in restarted.operation_logs)
        )
        self.assertFalse(
            any("new-password" in str(log) for log in restarted.operation_logs)
        )


if __name__ == "__main__":
    unittest.main()
