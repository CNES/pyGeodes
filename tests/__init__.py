from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
TEST_ENV_DIR = TESTS_DIR.joinpath("test_env")
TEST_ENV_DOWNLOAD_DIR = TEST_ENV_DIR.joinpath("download_dir")
TEST_ENV_S3_DOWNLOAD_DIR = TEST_ENV_DIR.joinpath("s3_download_dir")
VALID_API_KEY_PATH = TESTS_DIR.joinpath("valid-api-key.json")
TEST_ENV_SERIALIZED_DIR = TEST_ENV_DIR.joinpath("serialized")
