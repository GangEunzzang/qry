"""Tests for SQL formatter."""

from qry.domains.query.formatter import format_sql


class TestFormatSql:
    def test_empty_string(self):
        assert format_sql("") == ""

    def test_whitespace_only(self):
        assert format_sql("   ") == ""

    def test_uppercase_keywords(self):
        result = format_sql("select * from users")
        assert "SELECT" in result
        assert "FROM" in result

    def test_simple_select(self):
        result = format_sql("select * from users")
        assert result == "SELECT *\nFROM users"

    def test_select_with_where(self):
        result = format_sql("select id, name from users where id = 1")
        assert result == "SELECT id, name\nFROM users\nWHERE id = 1"

    def test_select_with_order_by(self):
        result = format_sql("select * from users order by name asc")
        assert result == "SELECT *\nFROM users\nORDER BY name ASC"

    def test_select_with_group_by_having(self):
        result = format_sql(
            "select dept, count(*) from emp group by dept having count(*) > 5"
        )
        assert "GROUP BY" in result
        assert "HAVING" in result
        lines = result.split("\n")
        # GROUP BY and HAVING should be on separate lines
        group_line = [line for line in lines if "GROUP BY" in line]
        having_line = [line for line in lines if "HAVING" in line]
        assert len(group_line) == 1
        assert len(having_line) == 1

    def test_join(self):
        result = format_sql(
            "select * from users join orders on users.id = orders.user_id"
        )
        assert "JOIN" in result
        assert "\nJOIN" in result
        assert "\nON" in result

    def test_left_join(self):
        result = format_sql(
            "select * from users left join orders on users.id = orders.user_id"
        )
        assert "LEFT JOIN" in result

    def test_multiple_conditions_with_and_or(self):
        result = format_sql("select * from users where age > 18 and active = 1 or role = 'admin'")
        assert "\nAND" in result
        assert "\nOR" in result

    def test_normalize_whitespace(self):
        result = format_sql("select  *   from    users")
        # No double spaces in the result
        assert "  " not in result.replace("\n  ", "\nXX")  # allow indentation

    def test_preserves_string_literals(self):
        result = format_sql("select * from users where name = 'John Doe'")
        assert "'John Doe'" in result

    def test_preserves_double_quoted_identifiers(self):
        result = format_sql('select "column name" from "table name"')
        assert '"column name"' in result
        assert '"table name"' in result

    def test_preserves_comments_inline(self):
        result = format_sql("select * -- get all\nfrom users")
        assert "-- get all" in result

    def test_preserves_block_comments(self):
        result = format_sql("select /* all columns */ * from users")
        assert "/* all columns */" in result

    def test_aggregate_functions(self):
        result = format_sql("select count(*), sum(amount), avg(price) from orders")
        assert "COUNT(*)" in result
        assert "SUM(amount)" in result
        assert "AVG(price)" in result

    def test_limit_offset(self):
        result = format_sql("select * from users limit 10 offset 20")
        assert "\nLIMIT" in result
        assert "\nOFFSET" in result

    def test_insert_statement(self):
        result = format_sql("insert into users (name, age) values ('Alice', 30)")
        assert "INSERT" in result
        assert "INTO" in result
        assert "VALUES" in result

    def test_update_statement(self):
        result = format_sql("update users set name = 'Bob' where id = 1")
        assert "UPDATE" in result
        assert "\nSET" in result
        assert "\nWHERE" in result

    def test_delete_statement(self):
        result = format_sql("delete from users where id = 1")
        assert "DELETE" in result
        assert "\nFROM" in result
        assert "\nWHERE" in result

    def test_subquery_parentheses(self):
        result = format_sql(
            "select * from users where id in (select user_id from orders)"
        )
        assert "IN" in result
        assert "(" in result
        assert ")" in result

    def test_string_with_semicolons(self):
        result = format_sql("select * from t where name = 'a;b;c'")
        assert "'a;b;c'" in result

    def test_escaped_single_quotes(self):
        result = format_sql("select * from t where name = 'it''s'")
        assert "'it''s'" in result

    def test_complex_query(self):
        sql = (
            "select u.id, u.name, count(o.id) as order_count "
            "from users u "
            "left join orders o on u.id = o.user_id "
            "where u.active = 1 and u.created_at > '2024-01-01' "
            "group by u.id, u.name "
            "having count(o.id) > 0 "
            "order by order_count desc "
            "limit 10"
        )
        result = format_sql(sql)
        lines = result.split("\n")
        assert len(lines) >= 7  # At least one line per major clause
        assert lines[0].startswith("SELECT")

    def test_distinct(self):
        result = format_sql("select distinct name from users")
        assert "SELECT DISTINCT" in result

    def test_create_table(self):
        result = format_sql("create table users (id integer, name text)")
        assert "CREATE TABLE" in result

    def test_already_formatted(self):
        """Formatting an already formatted query should not break it."""
        sql = "SELECT *\nFROM users\nWHERE id = 1"
        result = format_sql(sql)
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result

    def test_idempotent(self):
        """Formatting twice should give the same result."""
        sql = "select * from users where id = 1 order by name"
        first = format_sql(sql)
        second = format_sql(first)
        assert first == second
