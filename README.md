# qry

A fast and beautiful SQL TUI client for developers.

## Features

- Multi-database support: SQLite, PostgreSQL, MySQL
- SQL syntax highlighting
- Query autocompletion
- Query history with search
- Saved connections with secure password storage
- Export results to CSV/JSON/Markdown
- Result search and column sorting
- SQL snippets with Ctrl+P picker
- SQL auto-formatter
- 12+ color themes

## Installation

```bash
pip install qry
```

### Database Drivers

```bash
# PostgreSQL support
pip install 'qry[postgres]'

# MySQL support
pip install 'qry[mysql]'

# All databases
pip install 'qry[all]'
```

## Usage

```bash
# Open SQLite database
qry database.db

# Use saved connection
qry -c mydb
```

## Comparison

| Feature | qry | Harlequin | lazysql | sqlit |
|---------|-----|-----------|---------|-------|
| Focus | Fast & light | Full IDE | lazygit-style | All DBs |
| Language | Python | Python | Go | Python |
| SQLite | Yes | Yes | Yes | Yes |
| PostgreSQL | Yes | Yes | Yes | Yes |
| MySQL | Yes | Yes | Yes | Yes |
| DuckDB | Planned | Yes | No | Yes |
| Startup | <1s | ~2s | <1s | ~1s |
| Syntax highlight | Yes | Yes | No | Yes |
| Autocomplete | Yes | Yes | No | No |
| Query history | Yes (with search) | Yes | No | No |
| Themes | 12+ | 10+ | 1 | 1 |
| Export | CSV/JSON/MD | CSV/JSON | No | No |
| Snippets | Yes | No | No | No |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+Enter | Execute query |
| Ctrl+B | Toggle sidebar |
| Ctrl+E | Export results |
| Ctrl+C | Copy row as JSON |
| Enter | Copy cell value |
| Ctrl+H | Query history |
| Ctrl+P | Snippet picker |
| Ctrl+R | Reverse history search |
| Ctrl+Shift+F | Format SQL |
| Ctrl+Space | Autocomplete |
| s | Sort column |
| / | Search results |
| F1 | Help |
| F2 | Change theme |
| Ctrl+Q | Quit |

## Development

```bash
git clone https://github.com/GangEunzzang/qry.git
cd qry
pip install -e '.[dev]'
```

## License

MIT
