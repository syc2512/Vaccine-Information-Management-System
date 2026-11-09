import unittest

from services.validators import validate_date_format, validate_vaccine_data


def valid_vaccine():
    return {
        "name": "示例流感疫苗",
        "category": "灭活疫苗",
        "manufacturer": "示例生物科技",
        "batch_number": "DEMO-2026-001",
        "production_date": "2026-01-01",
        "expiry_date": "2099-12-31",
        "quantity": "100",
    }


class ValidatorTests(unittest.TestCase):
    def test_vaccine_validation_accepts_complete_record(self):
        valid, message = validate_vaccine_data(valid_vaccine())

        self.assertTrue(valid)
        self.assertEqual(message, "校验通过")

    def test_vaccine_validation_reports_missing_fields(self):
        data = valid_vaccine()
        data["name"] = ""
        data["quantity"] = 0

        valid, message = validate_vaccine_data(data)

        self.assertFalse(valid)
        self.assertIn("疫苗名称不能为空", message)
        self.assertIn("数量必须大于0", message)

    def test_date_format_normalizes_slashes(self):
        valid, normalized = validate_date_format("2026/11/06")

        self.assertTrue(valid)
        self.assertEqual(normalized, "2026-11-06")


if __name__ == "__main__":
    unittest.main()
