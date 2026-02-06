"""SQL query splitter - splits multiple statements by semicolons."""


class QuerySplitter:
    """Splits SQL text into individual statements.

    Handles:
    - Semicolon-separated statements
    - Single-quoted strings ('...')
    - Double-quoted identifiers ("...")
    - Line comments (--)
    - Block comments (/* ... */)
    """

    @staticmethod
    def split(sql: str) -> list[str]:
        """Split SQL text into individual statements."""
        statements: list[str] = []
        current: list[str] = []
        i = 0
        length = len(sql)

        while i < length:
            ch = sql[i]

            # Single-quoted string
            if ch == "'":
                current.append(ch)
                i += 1
                while i < length:
                    if sql[i] == "'" and i + 1 < length and sql[i + 1] == "'":
                        current.append("''")
                        i += 2
                    elif sql[i] == "'":
                        current.append("'")
                        i += 1
                        break
                    else:
                        current.append(sql[i])
                        i += 1
                continue

            # Double-quoted identifier
            if ch == '"':
                current.append(ch)
                i += 1
                while i < length and sql[i] != '"':
                    current.append(sql[i])
                    i += 1
                if i < length:
                    current.append('"')
                    i += 1
                continue

            # Line comment
            if ch == "-" and i + 1 < length and sql[i + 1] == "-":
                while i < length and sql[i] != "\n":
                    current.append(sql[i])
                    i += 1
                continue

            # Block comment
            if ch == "/" and i + 1 < length and sql[i + 1] == "*":
                current.append("/")
                current.append("*")
                i += 2
                while i < length:
                    if sql[i] == "*" and i + 1 < length and sql[i + 1] == "/":
                        current.append("*")
                        current.append("/")
                        i += 2
                        break
                    else:
                        current.append(sql[i])
                        i += 1
                continue

            # Semicolon - statement separator
            if ch == ";":
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue

            current.append(ch)
            i += 1

        # Last statement (no trailing semicolon)
        stmt = "".join(current).strip()
        if stmt:
            statements.append(stmt)

        return statements
