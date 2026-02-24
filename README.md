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
- SOCKS proxy running on `localhost:8888` (e.g. SSH tunnel, Shadowsocks, etc.)

## Installation

```bash
# Clone the repo
git clone git@github.com:adw0rd/ProxyRumps.git
cd ProxyRumps

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
source venv/bin/activate
python socks_toggle.py
```

The app will appear in your menu bar with a flag and IP address.

- Click the icon to open the menu
- **Enable/Disable Proxy** — toggle SOCKS proxy on or off
- **Status** — show detailed IP information
- **Reload** — restart the app

## Run at Login

To start ProxyRumps automatically when you log in, install the LaunchAgent:

```bash
cp dev.adw0rd.proxyrumps.plist ~/Library/LaunchAgents/
```

Then either log out and back in, or load it manually:

```bash
launchctl load ~/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist
```

To stop and remove:

```bash
launchctl unload ~/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist
rm ~/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist
```

## Configuration

Edit the constants at the top of `socks_toggle.py`:

| Variable | Default | Description |
|---|---|---|
| `NETWORK_SERVICE` | `Wi-Fi` | macOS network service name |
| `SOCKS_HOST` | `localhost` | SOCKS proxy host |
| `SOCKS_PORT` | `8888` | SOCKS proxy port |

## License

MIT
