"""Integration test fixtures — require Docker containers."""

import pytest


def _check_postgres() -> bool:
    try:
        import psycopg
        conn = psycopg.connect(
            host="localhost", port=15432,
            user="qry_test", password="qry_test", dbname="qry_test",
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        return False


def _check_mysql() -> bool:
    try:
        import pymysql
        conn = pymysql.connect(
            host="localhost", port=13306,
            user="root", password="qry_test", database="qry_test",
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture
def postgres_adapter():
    """Provide a connected PostgresAdapter. Skip if Docker not running."""
    if not _check_postgres():
        pytest.skip("PostgreSQL not available (run: docker compose -f docker-compose.test.yml up -d)")

    from qry.domains.database.postgres import PostgresAdapter
    from qry.domains.connection.models import ConnectionConfig, DatabaseType

    config = ConnectionConfig(
        name="test-pg",
        db_type=DatabaseType.POSTGRES,
        host="localhost",
        port=15432,
        user="qry_test",
        password="qry_test",
        database="qry_test",
    )
    adapter = PostgresAdapter(config)
    adapter.connect()

    # Setup test table
    adapter.execute("DROP TABLE IF EXISTS test_orders")
    adapter.execute("DROP TABLE IF EXISTS test_users")
    adapter.execute(
        "CREATE TABLE IF NOT EXISTS test_users ("
        "id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(200))"
    )
    adapter.execute(
        "CREATE TABLE IF NOT EXISTS test_orders ("
        "id SERIAL PRIMARY KEY, user_id INT REFERENCES test_users(id), amount NUMERIC)"
    )
    adapter.execute("INSERT INTO test_users (name, email) VALUES ('Alice', 'alice@test.com') ON CONFLICT DO NOTHING")

    yield adapter

    adapter.execute("DROP TABLE IF EXISTS test_orders")
    adapter.execute("DROP TABLE IF EXISTS test_users")
    adapter.disconnect()


@pytest.fixture
def mysql_adapter():
    """Provide a connected MySQLAdapter. Skip if Docker not running."""
    if not _check_mysql():
        pytest.skip("MySQL not available (run: docker compose -f docker-compose.test.yml up -d)")

    from qry.domains.database.mysql import MySQLAdapter
    from qry.domains.connection.models import ConnectionConfig, DatabaseType

    config = ConnectionConfig(
        name="test-my",
        db_type=DatabaseType.MYSQL,
        host="localhost",
        port=13306,
        user="root",
        password="qry_test",
        database="qry_test",
    )
    adapter = MySQLAdapter(config)
    adapter.connect()

    adapter.execute("DROP TABLE IF EXISTS test_orders")
    adapter.execute("DROP TABLE IF EXISTS test_users")
    adapter.execute(
        "CREATE TABLE IF NOT EXISTS test_users ("
        "id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(200))"
    )
    adapter.execute("INSERT INTO test_users (name, email) VALUES ('Alice', 'alice@test.com')")

    yield adapter

    adapter.execute("DROP TABLE IF EXISTS test_orders")
    adapter.execute("DROP TABLE IF EXISTS test_users")
    adapter.disconnect()
