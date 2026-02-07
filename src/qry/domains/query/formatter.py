"""SQL formatter - auto-formats SQL queries."""

import re

from qry.shared.constants import SQL_KEYWORDS

# Clauses that should start on a new line (at top level)
_NEWLINE_CLAUSES = (
    "FROM",
    "WHERE",
    "JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "INNER JOIN",
    "OUTER JOIN",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "CROSS JOIN",
    "ORDER BY",
    "GROUP BY",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "ON",
    "AND",
    "OR",
    "SET",
    "VALUES",
    "INTO",
    "UNION",
    "UNION ALL",
    "EXCEPT",
    "INTERSECT",
)

# Build regex for multi-word keywords (ORDER BY, GROUP BY, etc.)
_MULTI_WORD_KEYWORDS = [
    "ORDER BY",
    "GROUP BY",
    "LEFT JOIN",
    "RIGHT JOIN",
    "INNER JOIN",
    "OUTER JOIN",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "CROSS JOIN",
    "UNION ALL",
    "INSERT INTO",
    "NOT IN",
    "NOT LIKE",
    "NOT NULL",
    "IS NOT",
    "IS NULL",
]

_MULTI_WORD_KEYWORDS_SET = frozenset(_MULTI_WORD_KEYWORDS)


def _tokenize(sql: str) -> list[tuple[str, str]]:
    """Split SQL into tokens preserving strings, comments, and parentheses.

    Returns list of (token_type, value) tuples.
    Token types: 'word', 'string', 'comment', 'paren_open', 'paren_close',
                 'comma', 'semicolon', 'operator', 'whitespace', 'other'.
    """
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(sql)

    while i < n:
        ch = sql[i]

        # Whitespace
        if ch in " \t\r\n":
            start = i
            while i < n and sql[i] in " \t\r\n":
                i += 1
            tokens.append(("whitespace", sql[start:i]))
            continue

        # Single-line comment
        if ch == "-" and i + 1 < n and sql[i + 1] == "-":
            start = i
            while i < n and sql[i] != "\n":
                i += 1
            tokens.append(("comment", sql[start:i]))
            continue

        # Block comment
        if ch == "/" and i + 1 < n and sql[i + 1] == "*":
            start = i
            i += 2
            while i + 1 < n and not (sql[i] == "*" and sql[i + 1] == "/"):
                i += 1
            i += 2  # skip */
            tokens.append(("comment", sql[start:i]))
            continue

        # Single-quoted string
        if ch == "'":
            start = i
            i += 1
            while i < n:
                if sql[i] == "'" and i + 1 < n and sql[i + 1] == "'":
                    i += 2  # escaped quote
                elif sql[i] == "'":
                    i += 1
                    break
                else:
                    i += 1
            tokens.append(("string", sql[start:i]))
            continue

        # Double-quoted identifier
        if ch == '"':
            start = i
            i += 1
            while i < n and sql[i] != '"':
                i += 1
            if i < n:
                i += 1
            tokens.append(("string", sql[start:i]))
            continue

        # Parentheses
        if ch == "(":
            tokens.append(("paren_open", "("))
            i += 1
            continue
        if ch == ")":
            tokens.append(("paren_close", ")"))
            i += 1
            continue

        # Comma
        if ch == ",":
            tokens.append(("comma", ","))
            i += 1
            continue

        # Semicolon
        if ch == ";":
            tokens.append(("semicolon", ";"))
            i += 1
            continue

        # Word (identifier or keyword)
        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (sql[i].isalnum() or sql[i] in "_.$"):
                i += 1
            tokens.append(("word", sql[start:i]))
            continue

        # Number
        if ch.isdigit() or (ch == "." and i + 1 < n and sql[i + 1].isdigit()):
            start = i
            while i < n and (sql[i].isdigit() or sql[i] == "."):
                i += 1
            tokens.append(("other", sql[start:i]))
            continue

        # Operators and other characters
        tokens.append(("other", ch))
        i += 1

    return tokens


def _merge_multi_word_keywords(
    tokens: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Merge multi-word SQL keywords into single tokens."""
    result: list[tuple[str, str]] = []
    i = 0

    while i < len(tokens):
        # Try matching multi-word keywords (up to 3 words)
        merged = False
        for length in (3, 2):
            words: list[str] = []
            positions: list[int] = []
            j = i
            while j < len(tokens) and len(words) < length:
                if tokens[j][0] == "whitespace":
                    j += 1
                    continue
                if tokens[j][0] == "word":
                    words.append(tokens[j][1].upper())
                    positions.append(j)
                    j += 1
                else:
                    break

            if len(words) == length:
                candidate = " ".join(words)
                if candidate in _MULTI_WORD_KEYWORDS:
                    result.append(("word", candidate))
                    i = j
                    merged = True
                    break

        if not merged:
            result.append(tokens[i])
            i += 1

    return result


def format_sql(sql: str) -> str:
    """Format a SQL query string.

    - Uppercases SQL keywords
    - Adds newlines before major clauses
    - Normalizes whitespace
    - Handles nested parentheses with indentation
    """
    sql = sql.strip()
    if not sql:
        return sql

    tokens = _tokenize(sql)
    tokens = [t for t in tokens if t[0] != "whitespace"]
    tokens = _merge_multi_word_keywords(tokens)

    parts: list[str] = []
    indent_level = 0
    indent_str = "  "
    prev_type = ""
    prev_value = ""

    def _add_newline_indent(level: int) -> None:
        parts.append("\n" + indent_str * level)

    for ttype, value in tokens:
        upper_value = value.upper() if ttype == "word" else value

        # Uppercase keywords
        if ttype == "word" and (
            upper_value in SQL_KEYWORDS
            or upper_value in _MULTI_WORD_KEYWORDS_SET
        ):
            value = upper_value

        if ttype == "comment":
            if parts:
                parts.append(" ")
            parts.append(value)
            prev_type = ttype
            prev_value = value
            continue

        if ttype == "string":
            if parts and prev_type not in ("paren_open", "comma"):
                parts.append(" ")
            parts.append(value)
            prev_type = ttype
            prev_value = value
            continue

        if ttype == "paren_open":
            if parts and prev_type == "word":
                # No space before ( if previous is a function name
                prev_upper = prev_value.upper()
                if prev_upper in (
                    "COUNT",
                    "SUM",
                    "AVG",
                    "MIN",
                    "MAX",
                    "COALESCE",
                    "NULLIF",
                    "CAST",
                    "UPPER",
                    "LOWER",
                    "TRIM",
                    "SUBSTRING",
                    "ROUND",
                    "ABS",
                    "LENGTH",
                    "IFNULL",
                    "IIF",
                    "IN",
                    "NOT IN",
                ):
                    pass
                else:
                    parts.append(" ")
            elif parts and prev_type not in ("paren_open",):
                parts.append(" ")
            parts.append("(")
            indent_level += 1
            prev_type = ttype
            prev_value = value
            continue

        if ttype == "paren_close":
            indent_level = max(0, indent_level - 1)
            parts.append(")")
            prev_type = ttype
            prev_value = value
            continue

        if ttype == "comma":
            parts.append(",")
            prev_type = ttype
            prev_value = value
            continue

        if ttype == "semicolon":
            parts.append(";")
            prev_type = ttype
            prev_value = value
            continue

        # Check if this token starts a new clause
        if ttype == "word" and upper_value in _NEWLINE_CLAUSES:
            if parts:  # Don't add newline at start
                _add_newline_indent(indent_level)
            parts.append(value)
            prev_type = ttype
            prev_value = value
            continue

        # Default: add space before token
        if parts and prev_type not in ("paren_open",):
            parts.append(" ")
        parts.append(value)
        prev_type = ttype
        prev_value = value

    result = "".join(parts)
    # Clean up any trailing whitespace on lines
    result = re.sub(r"[ \t]+\n", "\n", result)
    return result.strip()
