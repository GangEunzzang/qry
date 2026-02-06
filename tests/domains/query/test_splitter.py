"""Tests for QuerySplitter."""

from qry.domains.query.splitter import QuerySplitter


class TestQuerySplitter:
    def test_single_statement(self):
        assert QuerySplitter.split("SELECT 1") == ["SELECT 1"]

    def test_single_with_semicolon(self):
        assert QuerySplitter.split("SELECT 1;") == ["SELECT 1"]

    def test_two_statements(self):
        result = QuerySplitter.split("SELECT 1; SELECT 2")
        assert result == ["SELECT 1", "SELECT 2"]

    def test_multiple_statements(self):
        sql = "SELECT 1; SELECT 2; SELECT 3;"
        result = QuerySplitter.split(sql)
        assert result == ["SELECT 1", "SELECT 2", "SELECT 3"]

    def test_empty_string(self):
        assert QuerySplitter.split("") == []

    def test_whitespace_only(self):
        assert QuerySplitter.split("   ") == []

    def test_empty_statements_filtered(self):
        assert QuerySplitter.split(";;; SELECT 1 ;;;") == ["SELECT 1"]

    def test_single_quoted_string_with_semicolon(self):
        sql = "SELECT 'hello;world'"
        assert QuerySplitter.split(sql) == ["SELECT 'hello;world'"]

    def test_double_quoted_identifier_with_semicolon(self):
        sql = 'SELECT "col;name" FROM t'
        assert QuerySplitter.split(sql) == ['SELECT "col;name" FROM t']

    def test_escaped_single_quote(self):
        sql = "SELECT 'it''s'; SELECT 1"
        result = QuerySplitter.split(sql)
        assert result == ["SELECT 'it''s'", "SELECT 1"]

    def test_line_comment(self):
        sql = "SELECT 1; -- this is a comment\nSELECT 2"
        result = QuerySplitter.split(sql)
        assert result == ["SELECT 1", "-- this is a comment\nSELECT 2"]

    def test_line_comment_with_semicolon(self):
        sql = "-- comment; not a separator\nSELECT 1"
        result = QuerySplitter.split(sql)
        assert result == ["-- comment; not a separator\nSELECT 1"]

    def test_block_comment(self):
        sql = "SELECT /* comment */ 1; SELECT 2"
        result = QuerySplitter.split(sql)
        assert result == ["SELECT /* comment */ 1", "SELECT 2"]

    def test_block_comment_with_semicolon(self):
        sql = "SELECT /* ; */ 1"
        assert QuerySplitter.split(sql) == ["SELECT /* ; */ 1"]

    def test_multiline_statement(self):
        sql = "SELECT\n  *\nFROM\n  users;\nSELECT 1"
        result = QuerySplitter.split(sql)
        assert len(result) == 2
        assert "users" in result[0]

    def test_preserves_whitespace_within(self):
        sql = "SELECT  1  +  2"
        assert QuerySplitter.split(sql) == ["SELECT  1  +  2"]

    def test_complex_mixed(self):
        sql = """
        INSERT INTO t VALUES ('a;b', "c;d");
        /* multi
           line; comment */
        SELECT * FROM t; -- end
        """
        result = QuerySplitter.split(sql)
        assert len(result) == 3
