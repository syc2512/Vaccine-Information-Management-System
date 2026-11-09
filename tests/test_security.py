import unittest

from utils.security import hash_password, is_password_hash, validate_new_password, verify_password


class SecurityTests(unittest.TestCase):
    def test_password_hash_round_trip(self):
        encoded = hash_password("correct-horse")

        self.assertNotEqual(encoded, "correct-horse")
        self.assertTrue(is_password_hash(encoded))
        self.assertTrue(verify_password("correct-horse", encoded))
        self.assertFalse(verify_password("wrong-password", encoded))

    def test_password_hash_uses_unique_salt(self):
        first = hash_password("same-password")
        second = hash_password("same-password")

        self.assertNotEqual(first, second)
        self.assertTrue(verify_password("same-password", first))
        self.assertTrue(verify_password("same-password", second))

    def test_invalid_new_password_is_rejected(self):
        for password in ["", "short", "x" * 129]:
            with self.subTest(password=password):
                with self.assertRaises(ValueError):
                    validate_new_password(password)


if __name__ == "__main__":
    unittest.main()
