#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def parse_database_url(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise ValueError("DATABASE_URL must use mysql or mysql+pymysql")
    if not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("DATABASE_URL must include host and database name")
    return {
        "host": parsed.hostname,
        "port": str(parsed.port or 3306),
        "user": parsed.username or "root",
        "password": parsed.password or "",
        "database": parsed.path.strip("/"),
    }


def run_dump(config: dict[str, str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "mysqldump",
        f"--host={config['host']}",
        f"--port={config['port']}",
        f"--user={config['user']}",
        "--single-transaction",
        "--routines",
        "--triggers",
        config["database"],
    ]
    environment = os.environ.copy()
    if config["password"]:
        environment["MYSQL_PWD"] = config["password"]
    with output.open("wb") as destination:
        subprocess.run(command, check=True, stdout=destination, env=environment)
    print(output)


def run_restore(config: dict[str, str], dump_file: Path) -> None:
    if not dump_file.is_file():
        raise FileNotFoundError(dump_file)
    command = [
        "mysql",
        f"--host={config['host']}",
        f"--port={config['port']}",
        f"--user={config['user']}",
        config["database"],
    ]
    environment = os.environ.copy()
    if config["password"]:
        environment["MYSQL_PWD"] = config["password"]
    with dump_file.open("rb") as source:
        subprocess.run(command, check=True, stdin=source, env=environment)
    print(f"Restored {dump_file}")


def main() -> int:
    parser = argparse.ArgumentParser(description="ManutenCar MySQL backup and restore")
    parser.add_argument("action", choices=["backup", "restore"])
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is required", file=sys.stderr)
        return 2
    try:
        config = parse_database_url(database_url)
        if args.action == "backup":
            output = args.file or Path("backups") / f"manutencar-{datetime.now():%Y%m%d-%H%M%S}.sql"
            run_dump(config, output)
        else:
            if not args.file:
                print("--file is required for restore", file=sys.stderr)
                return 2
            run_restore(config, args.file)
        return 0
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
