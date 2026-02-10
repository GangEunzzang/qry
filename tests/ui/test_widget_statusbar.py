"""Tests for StatusBar widget."""

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.ui.widgets.widget_statusbar import StatusBar


def _get_content(bar: StatusBar) -> str:
    """Get the text content of a StatusBar."""
    return str(bar._Static__content)


class TestStatusBarConnection:
    def test_initial_state_no_connection(self):
        bar = StatusBar()
        bar._update_display()
        content = _get_content(bar)
        assert "No connection" in content

    def test_set_connection_name(self):
        bar = StatusBar()
        bar.set_connection("my-db")
        content = _get_content(bar)
        assert "my-db" in content

    def test_clear_connection(self):
        bar = StatusBar()
        bar.set_connection("my-db")
        bar.clear_connection()
        content = _get_content(bar)
        assert "No connection" in content

    def test_set_connection_info_postgres(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="prod",
            db_type=DatabaseType.POSTGRES,
            host="db.example.com",
            port=5432,
            database="myapp",
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert "\U0001f418" in content
        assert "db.example.com:5432/myapp" in content

    def test_set_connection_info_mysql(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="staging",
            db_type=DatabaseType.MYSQL,
            host="mysql.local",
            port=3306,
            database="shop",
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert "\U0001f42c" in content
        assert "mysql.local:3306/shop" in content

    def test_set_connection_info_sqlite(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="local",
            db_type=DatabaseType.SQLITE,
            path="/data/test.db",
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert "\U0001f4e6" in content
        assert "/data/test.db" in content

    def test_set_connection_info_sqlite_memory(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="mem",
            db_type=DatabaseType.SQLITE,
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert ":memory:" in content

    def test_set_connection_info_no_port(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.POSTGRES,
            host="localhost",
            database="testdb",
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert "localhost/testdb" in content

    def test_set_connection_info_overrides_name(self):
        bar = StatusBar()
        bar.set_connection("old-name")
        config = ConnectionConfig(
            name="new-name",
            db_type=DatabaseType.SQLITE,
            path="/data.db",
        )
        bar.set_connection_info(config)
        content = _get_content(bar)
        assert "/data.db" in content

    def test_clear_connection_resets_info(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="prod",
            db_type=DatabaseType.POSTGRES,
            host="db.example.com",
            port=5432,
            database="myapp",
        )
        bar.set_connection_info(config)
        bar.clear_connection()
        content = _get_content(bar)
        assert "No connection" in content
        assert "db.example.com" not in content


class TestStatusBarQueryResult:
    def test_set_query_result(self):
        bar = StatusBar()
        bar.set_connection("test")
        bar.set_query_result(42, 12.3)
        content = _get_content(bar)
        assert "42 rows" in content
        assert "12.3ms" in content

    def test_set_query_result_zero_rows(self):
        bar = StatusBar()
        bar.set_connection("test")
        bar.set_query_result(0, 0.5)
        content = _get_content(bar)
        assert "0 rows" in content
        assert "0.5ms" in content

    def test_no_query_result_initially(self):
        bar = StatusBar()
        bar.set_connection("test")
        bar._update_display()
        content = _get_content(bar)
        assert "rows" not in content

    def test_clear_connection_clears_query_result(self):
        bar = StatusBar()
        bar.set_connection("test")
        bar.set_query_result(10, 5.0)
        bar.clear_connection()
        content = _get_content(bar)
        assert "rows" not in content

    def test_query_result_formatting(self):
        bar = StatusBar()
        bar.set_connection("test")
        bar.set_query_result(1000, 123.456)
        content = _get_content(bar)
        assert "1000 rows" in content
        assert "123.5ms" in content


class TestStatusBarMessage:
    def test_set_message(self):
        bar = StatusBar()
        bar.set_message("Exported to file.csv")
        content = _get_content(bar)
        assert "Exported to file.csv" in content

    def test_clear_message(self):
        bar = StatusBar()
        bar.set_message("some message")
        bar.clear_message()
        content = _get_content(bar)
        assert "some message" not in content


class TestStatusBarDisplay:
    def test_always_shows_run_hint(self):
        bar = StatusBar()
        bar._update_display()
        content = _get_content(bar)
        assert "Ctrl+Enter: Run" in content

    def test_full_display_format(self):
        bar = StatusBar()
        config = ConnectionConfig(
            name="prod",
            db_type=DatabaseType.POSTGRES,
            host="db.host",
            port=5432,
            database="mydb",
        )
        bar.set_connection_info(config)
        bar.set_query_result(50, 8.2)
        content = _get_content(bar)
        assert " | " in content
        assert "50 rows" in content
        assert "8.2ms" in content
        assert "db.host:5432/mydb" in content
        assert "Ctrl+Enter: Run" in content
