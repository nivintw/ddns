from pathlib import Path

import pytest


@pytest.fixture()
def temp_database_path(tmp_path: Path) -> Path:
    db_root = tmp_path
    return db_root / "ddns.db"
