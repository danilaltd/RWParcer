import os
from pathlib import Path

import aiosql
import pytest

# Укажите путь к вашей папке с SQL файлами (например, app/infrastructure/db/sql)
SQL_DIR = Path(__file__).parent.parent.parent / "app" / "infrastructure" / "db" / "queries"


def test_all_aiosql_files_are_valid() -> None:
    sql_files = [f for f in os.listdir(SQL_DIR) if f.endswith(".sql")]

    assert sql_files, f"SQL файлы не найдены в директории {SQL_DIR}"

    for file_name in sql_files:
        file_path = SQL_DIR / file_name
        try:
            aiosql.from_path(file_path, driver_adapter="asyncpg")
        except Exception as e:
            pytest.fail(f"Ошибка валидации в файле {file_name}: {e}")
