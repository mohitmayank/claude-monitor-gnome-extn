# Claude Token Monitor

A GNOME Shell 48 extension that monitors [Claude Code](https://docs.anthropic.com/en/docs/claude-code) token usage, cost, and burn rate in real time from your taskbar.

It reads the JSONL data files (`~/.claude/projects/**/*.jsonl`) that Claude Code writes locally, parses token usage across all entry types, calculates cost and burn rate per model, and displays it as a panel indicator with a click-to-expand dropdown for details. No accounts, API keys, or browser cookies required — everything comes from data already on disk.

![GNOME Shell 48](https://img.shields.io/badge/GNOME_Shell-48-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

![Claude Token Monitor dropdown showing token breakdown, cost, burn rate, and plan usage](screenshots/dropdown.png)

## Features

- **Progress bar** showing cost or token usage against plan limits (Pro, Max 5x, Max 20x)
- **Individual toggles** — show/hide icon, bar, percentage, time, and status dot independently
- **Time remaining** estimate until your plan limit resets, with a clock-time countdown (e.g. "2h 44m reset (13:00)")
- **11 bar styles** — Unicode (blocks, dots, squares, thin, smooth), Cairo-rendered (pill, thick-rounded, segmented, glow-edge), and vertical (vbar, vbar-dual)
- **15 color schemes** — white, green-red, blue, purple, amber, rainbow, dracula, nord, catppuccin, neon, sunset, ocean, solarized, system accent, or a custom gradient
- **Pill backgrounds** — off, solid, subtle, border-only, status-aware (green/yellow/red), neon glow
- **3 dropdown styles** — classic (text rows), modern (progress bar + sparkline + colored dots), gauges (circular arc gauges)
- **Prefix options** — "Claude" text, Claude icon, or a theme-adaptive symbolic SVG icon
- **Animations** — smooth bar fill, pulse at high usage, icon spin on refresh, label fade on update
- **Typography** — 3 font sizes, glow/shadow text effects
- **Middle-click** to cycle bar styles instantly
- **Configurable** bar length, refresh interval, panel position, and metric (cost or tokens)
- **Estimation modes** — conservative, balanced, and generous scaling to approximate Anthropic's `/usage` numbers
- **Performance optimized** — mtime-based file filtering, per-file caching, string pre-filter

## Installation

1. Clone this repository:

   ```bash
   git clone git@github.com:mohitmayank/claude-monitor-gnome-extn.git
   cd claude-monitor-gnome-extn
   ```

2. Symlink it into the GNOME Shell extensions directory:

   ```bash
   ln -s "$(pwd)" ~/.local/share/gnome-shell/extensions/claude-monitor@mohitmayank
   ```

3. Compile the GSettings schema:

   ```bash
   glib-compile-schemas schemas/
   ```

4. Restart GNOME Shell so it picks up the new extension:
   - **Wayland**: Log out and log back in.
   - **X11**: Press `Alt+F2`, type `r`, and press Enter.

5. Enable the extension:

   ```bash
   gnome-extensions enable claude-monitor@mohitmayank
   ```

## Configuration

![Settings window with plan, style, and general options](screenshots/settings.png)

Open the preferences window from the dropdown menu ("Settings") or via:

```bash
gnome-extensions prefs claude-monitor@mohitmayank
```

Preferences are split across three pages: **General**, **Appearance**, and **Advanced**.

### General

| Setting | Options | Description |
|---------|---------|-------------|
| Plan Type | Pro, Max 5x, Max 20x | Sets token and cost limits for the usage bar |
| Estimation Mode | Conservative, Balanced, Generous | How aggressively to scale estimates vs `/usage` |
| Bar Metric | Cost, Tokens | What the progress bar represents |
| Refresh Interval | 5–120 seconds | How often to re-read data files |
| Panel Position | Left, Right | Which side of the top bar |

### Appearance

| Setting | Options | Description |
|---------|---------|-------------|
| Show Icon / Bar / Percentage / Time / Status Dot | On/Off each | Independently toggle each panel element |
| Element Order | Drag to reorder | Left-to-right arrangement of icon, label, bar, dot |
| Prefix Style | Text, Icon, Symbolic Icon | "Claude" label, PNG icon, or theme-adaptive SVG |
| Bar Style | 11 styles | Unicode, Cairo-rendered, or vertical bars |
| Bar Length | 5–30 | Number of segments in the progress bar |
| Bar Color | 15 schemes | Includes Dracula, Nord, Catppuccin, system accent, and a custom color-picker gradient |
| Pill Background | Off, Solid, Subtle, Border Only, Status, Glow | Background treatment behind the indicator |
| Dropdown Style | Classic, Modern, Gauges | Layout of the click-to-expand menu |
| Time Display | None, Remaining, Reset | What the time field shows |

### Advanced

| Setting | Options | Description |
|---------|---------|-------------|
| Font Size | Small, Medium, Large | Panel indicator text size |
| Text Effect | None, Glow, Shadow | Visual effect on panel text |
| Pulse Animation | On/Off + threshold (50–100%) | Pulses the indicator above a usage threshold |

Middle-click the indicator at any time to cycle through bar styles.

## How It Works

The extension reads Claude Code's JSONL conversation logs on a timer and:

1. **Finds recent files** — scans `~/.claude/projects/` for `.jsonl` files modified within a 10-hour lookback window, using mtime filtering to stay fast.
2. **Deduplicates entries** — keeps the first JSONL entry per `message_id:request_id` and skips subsequent streaming duplicates; entries missing either ID are always kept.
3. **Detects the session window** — walks entry timestamps to find 5-hour usage windows data-driven from Anthropic's actual reset behavior, rather than assuming fixed UTC blocks.
4. **Calculates per-model costs** — each entry is priced by its own model tier (Opus, Sonnet, Haiku) using all four token types (input, output, cache creation, cache read).
5. **Applies estimation scaling** — a small configurable multiplier (0.8x–1.2x) approximates Anthropic's server-side `/usage` numbers, which may include overhead not recorded in JSONL files.
6. **Renders the panel indicator** — a progress bar with the chosen style, color scheme, and optional time-remaining estimate, with a detailed dropdown on click.

## File Structure

```
├── extension.js      # Main indicator logic, data parsing, cost calculation, Cairo rendering, animations
├── prefs.js           # GTK4/Adw preferences window (General, Appearance, Advanced)
├── stylesheet.css     # Panel styling
├── metadata.json      # GNOME Shell extension metadata
├── schemas/           # GSettings schema for user preferences
│   └── org.gnome.shell.extensions.claude-monitor.gschema.xml
└── icons/              # Claude logo PNGs (16/32/48px) + symbolic SVG
```

## Development

- On Wayland, `disable`/`enable` via D-Bus reloads settings but **not** JS code changes — a full session restart (log out/in) is required to pick up `extension.js` changes.
- After modifying the GSettings schema, recompile:

  ```bash
  glib-compile-schemas schemas/
  ```

- View extension logs:

  ```bash
  journalctl -f -o cat /usr/bin/gnome-shell
  ```

## Acknowledgements

Inspired by [Claude Code Usage Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor).

## License

MIT
