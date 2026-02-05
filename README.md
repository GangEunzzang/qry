# qry

A fast and beautiful SQL TUI client for developers.

## Features

- **Multi-database support**: SQLite, PostgreSQL, MySQL
- **Vim-style keybindings**: Modal editing for terminal purists
- **SQL autocomplete**: Context-aware completion for tables and columns
- **Query history**: Searchable, per-connection history
- **Modern TUI**: Built with Textual, featuring themes and responsive layouts

## Installation

```bash
# With uv (recommended)
uv tool install qry

# With pipx
pipx install qry

# With pip
pip install qry
```

### Database drivers

Install optional database drivers as needed:

```bash
# PostgreSQL
uv tool install 'qry[postgres]'

# MySQL
uv tool install 'qry[mysql]'

# All databases
uv tool install 'qry[all]'
```

## Usage

```bash
# Start qry
qry

# Connect to a specific database
qry --connection my-postgres-db
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/qry.git
cd qry

# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run the app
uv run qry
```

## License

MIT
