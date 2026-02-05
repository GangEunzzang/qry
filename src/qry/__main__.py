"""CLI entry point for qry."""

import argparse
import sys

from qry.app import run
from qry.connection.config import ConnectionConfig, DatabaseType
from qry.connection.manager import ConnectionManager
from qry.core.constants import VERSION


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="qry",
        description="A fast and beautiful SQL TUI client",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"qry {VERSION}",
    )
    parser.add_argument(
        "-c", "--connection",
        help="Connection name to use",
        metavar="NAME",
    )
    parser.add_argument(
        "database",
        nargs="?",
        help="SQLite database file path",
    )

    args = parser.parse_args()

    connection: ConnectionConfig | None = None

    if args.connection:
        manager = ConnectionManager()
        connection = manager.get(args.connection)
        if not connection:
            print(f"Error: Connection '{args.connection}' not found", file=sys.stderr)
            return 1
    elif args.database:
        connection = ConnectionConfig(
            name="cli",
            db_type=DatabaseType.SQLITE,
            path=args.database,
        )

    run(connection=connection)
    return 0


if __name__ == "__main__":
    sys.exit(main())
