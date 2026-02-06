# qry

A fast and beautiful SQL TUI client for developers.

## Features

- Multi-database support: SQLite (PostgreSQL, MySQL planned)
- SQL syntax highlighting
- Query autocompletion
- Query history with search
- Saved connections with secure password storage
- Export results to CSV/JSON

## Installation

```bash
pip install qry
```

### Database Drivers

```bash
# PostgreSQL support (planned)
pip install 'qry[postgres]'

# MySQL support (planned)
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

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+Enter | Execute query |
| Ctrl+B | Toggle sidebar |
| Ctrl+Q | Quit |
| F1 | Help |

## Development

```bash
git clone https://github.com/GangEunzzang/qry.git
cd qry
pip install -e '.[dev]'
```

## License

MIT
