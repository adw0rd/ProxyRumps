# ProxyRumps

macOS menu bar app to toggle system SOCKS proxy on/off with one click.

Shows your current IP address and country flag right in the menu bar.

## Features

- Toggle SOCKS proxy (`localhost:8888`) from the menu bar
- Displays country flag and current IP in the menu bar
- Detailed status popup: IP, country, city, ISP, timezone
- Auto-refreshes IP info every 30 seconds
- macOS native notifications on proxy state change

## Requirements

- macOS
- Python 3.9+
- [uv](https://docs.astral.sh/uv/)
- SOCKS proxy running on `localhost:8888` (e.g. SSH tunnel, Shadowsocks, etc.)

## Installation

```bash
git clone git@github.com:adw0rd/ProxyRumps.git
cd ProxyRumps
./install.sh
```

This will:
- Create a virtual environment and install dependencies
- Add `ProxyRumps.app` to `~/Applications/` (launchable from Spotlight)
- Install a LaunchAgent to auto-start on login

## Usage

Launch **ProxyRumps** from Spotlight, or run manually:

```bash
cd ProxyRumps
uv run app.py
```

The app will appear in your menu bar with a flag and IP address.

- Click the icon to open the menu
- **Enable/Disable Proxy** — toggle SOCKS proxy on or off
- **Status** — show detailed IP information
- **Reload** — restart the app

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist
rm ~/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist
rm -rf ~/Applications/ProxyRumps.app
```

## Configuration

Edit the constants at the top of `app.py`:

| Variable | Default | Description |
|---|---|---|
| `NETWORK_SERVICE` | `Wi-Fi` | macOS network service name |
| `SOCKS_HOST` | `localhost` | SOCKS proxy host |
| `SOCKS_PORT` | `8888` | SOCKS proxy port |

## License

MIT
