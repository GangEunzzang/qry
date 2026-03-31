# qry Design System

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#0D1117` | App background |
| Surface | `#161B22` | Panel/widget backgrounds |
| Accent | `#10B981` | Active states, highlights, buttons |
| Error | `#EF4444` | Error states, error text |
| Text Primary | `#E6EDF3` | Main text |
| Text Secondary | `#8B949E` | Dimmed/muted text |
| Border | `#30363D` | Default borders |
| Border Active | `#10B981` | Focused borders |

## Typography

- Monospace throughout (terminal aesthetic)
- Section titles: `//` comment-style prefix (e.g., `// query history`)
- Status elements: `$` prompt-style prefix (e.g., `$ export`)
- Tags: `[bracket]` style (e.g., `[sqlite]`, `[pg]`, `[!]`)

## Components

### Header
`> qry // sql tui client` with key hints on the right (`F1 info  F2 theme  ^q quit`)

### Status Bar
`[sqlite] /path/to/db  42 rows  0.3ms  Ctrl+Enter: Run`

### DB Type Icons
- PostgreSQL: `[pg]`
- MySQL: `[my]`
- SQLite: `[sqlite]`

### Error Bar
`[!] error message` with error-colored background

### Modals
- Title: `// section name` in comment style
- Action buttons: `$ action` (e.g., `$ export`)
- Border: thick accent color

## Interaction States

| State | Treatment |
|-------|-----------|
| Empty | Large `> _` cursor + connection instructions |
| Loading | Status bar shows `running...` + elapsed time |
| Error | Inline `[!]` bar + results area error display |
| Success | Result table with row count and timing |

## Data Display

- Zebra striping on alternating rows (not implemented yet, deferred to CSS theme)
- NULL values displayed as `NULL`
- Sort indicators: `name ▲` (ascending), `name ▼` (descending)
