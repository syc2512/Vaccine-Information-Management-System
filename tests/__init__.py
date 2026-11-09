import os
import tempfile


TEST_DATA_DIR = tempfile.mkdtemp(prefix="vaccine-desktop-tests-")
os.environ["VACCINE_DB_PATH"] = os.path.join(TEST_DATA_DIR, "test-global.db")
os.environ["VACCINE_IMPORT_JSON"] = "0"
os.environ["VACCINE_ADMIN_PASSWORD"] = "test-admin-password"
os.environ["VACCINE_PASSWORD_ITERATIONS"] = "1000"
