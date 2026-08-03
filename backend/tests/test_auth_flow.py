import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import auth


class AuthFlowTests(unittest.TestCase):
    def test_password_validation_accepts_strong_password(self):
        self.assertTrue(auth.is_strong_password("Prajna@123"))

    def test_password_validation_rejects_weak_password(self):
        self.assertFalse(auth.is_strong_password("password"))

    def test_otp_hash_and_verification(self):
        code = "483921"
        hashed = auth.hash_otp(code)
        self.assertTrue(auth.verify_otp_code(code, hashed))
        self.assertFalse(auth.verify_otp_code("000000", hashed))


if __name__ == "__main__":
    unittest.main()
