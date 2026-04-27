from __future__ import annotations

from pathlib import Path

from dashboard.pipeline import DB_PATH, run_pipeline


def build_database() -> Path:
    run_pipeline()
    return DB_PATH


def build_database_if_missing() -> Path:
    if not DB_PATH.exists():
        return build_database()
    return DB_PATH


if __name__ == "__main__":
    print(f"Built database at {build_database()}")
