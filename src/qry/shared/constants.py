"""Application constants."""

# --- App Metadata ---
APP_NAME = "qry"
VERSION = "0.1.0"

# --- Default Settings ---
DEFAULT_THEME = "dark"
DEFAULT_EDITOR_THEME = "dracula"
DEFAULT_TAB_SIZE = 2
DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_COLUMN_WIDTH = 50
DEFAULT_HISTORY_SIZE = 1000
DEFAULT_TIMEOUT_MS = 30000

# --- Display ---
NULL_DISPLAY = "NULL"

# --- UI Messages ---
MSG_NO_CONNECTION = "No database connection"
MSG_HELP_MAIN = "Press Ctrl+Enter to run query, Ctrl+B for sidebar"
MSG_HELP_SHORTCUTS = "Ctrl+Enter: Run query | Ctrl+B: Toggle sidebar | Ctrl+Q: Quit"

# --- SQL Keywords (for completion) ---
SQL_KEYWORDS = frozenset(
    [
        "SELECT",
        "FROM",
        "WHERE",
        "AND",
        "OR",
        "NOT",
        "IN",
        "LIKE",
        "ORDER",
        "BY",
        "ASC",
        "DESC",
        "LIMIT",
        "OFFSET",
        "INSERT",
        "INTO",
        "VALUES",
        "UPDATE",
        "SET",
        "DELETE",
        "CREATE",
        "TABLE",
        "DROP",
        "ALTER",
        "INDEX",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "ON",
        "GROUP",
        "HAVING",
        "DISTINCT",
        "AS",
        "NULL",
        "IS",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
    ]
)

SQL_TABLE_CONTEXT_KEYWORDS = ("FROM ", "JOIN ")

# --- Config Section Names ---
CONFIG_SECTION_GENERAL = "general"
CONFIG_SECTION_EDITOR = "editor"
CONFIG_SECTION_RESULTS = "results"
CONFIG_SECTION_HISTORY = "history"
