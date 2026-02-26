#!/usr/bin/env python3
"""Menu bar app to toggle SOCKS proxy on macOS."""

import json
import os
import subprocess
import threading
import rumps
from AppKit import NSImage, NSColor, NSBezierPath, NSSize

NETWORK_SERVICE = "Wi-Fi"
SOCKS_HOST = "localhost"
SOCKS_PORT = "8888"
IP_CHECK_URL = "https://ipinfo.io/json"


ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")


def _generate_icon(color, path, size=20):
    """Generate a colored circle PNG icon for the menu bar."""
    image = NSImage.alloc().initWithSize_(NSSize(size, size))
    image.lockFocus()
    color.setFill()
    padding = 4
    NSBezierPath.bezierPathWithOvalInRect_(
        ((padding, padding), (size - 2 * padding, size - 2 * padding))
    ).fill()
    image.unlockFocus()
    image.setTemplate_(False)
    tiff = image.TIFFRepresentation()
    from AppKit import NSBitmapImageRep, NSPNGFileType
    rep = NSBitmapImageRep.imageRepWithData_(tiff)
    png = rep.representationUsingType_properties_(NSPNGFileType, {})
    png.writeToFile_atomically_(path, True)


def ensure_icons():
    """Generate green/red status icons if they don't exist."""
    os.makedirs(ICON_DIR, exist_ok=True)
    green = os.path.join(ICON_DIR, "green.png")
    red = os.path.join(ICON_DIR, "red.png")
    if not os.path.exists(green):
        _generate_icon(NSColor.systemGreenColor(), green)
    if not os.path.exists(red):
        _generate_icon(NSColor.systemRedColor(), red)
    return green, red


def country_to_flag(code):
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


def is_socks_enabled():
    result = subprocess.run(
        ["networksetup", "-getsocksfirewallproxy", NETWORK_SERVICE],
        capture_output=True, text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Enabled:"):
            return "Yes" in line
    return False


def set_socks(enabled: bool):
    state = "on" if enabled else "off"
    subprocess.run(
        ["networksetup", "-setsocksfirewallproxystate", NETWORK_SERVICE, state],
    )
    if enabled:
        subprocess.run(
            ["networksetup", "-setsocksfirewallproxy", NETWORK_SERVICE, SOCKS_HOST, SOCKS_PORT],
        )


def fetch_ip_data():
    try:
        cmd = ["curl", "-s", "--max-time", "5"]
        if is_socks_enabled():
            cmd += ["--socks5", f"{SOCKS_HOST}:{SOCKS_PORT}"]
        else:
            cmd += ["--noproxy", "*"]
        cmd.append(IP_CHECK_URL)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return json.loads(result.stdout)
    except Exception:
        return {}


class SocksProxyApp(rumps.App):
    def __init__(self):
        self._green_icon, self._red_icon = ensure_icons()
        self._toggle_item = rumps.MenuItem("...", callback=self._on_toggle)
        super().__init__("...", quit_button="Reload")
        self.menu = [self._toggle_item, None]
        self._data = {}
        self._update_status()
        self._fetch_ip()

    def _update_toggle_label(self):
        if is_socks_enabled():
            self._toggle_item.title = "Disable Proxy"
        else:
            self._toggle_item.title = "Enable Proxy"

    def _set_status_icon(self):
        self.icon = self._green_icon if is_socks_enabled() else self._red_icon

    def _update_status(self):
        self._set_status_icon()
        self._update_toggle_label()

    def _update_title(self):
        country = self._data.get("country", "")
        self.title = country.upper() if country else "..."
        self._update_status()

    def _fetch_ip(self):
        def _do():
            self._data = fetch_ip_data()
            self._update_title()
        threading.Thread(target=_do, daemon=True).start()

    def _on_toggle(self, _):
        currently_on = is_socks_enabled()
        set_socks(not currently_on)
        state_label = "ON" if not currently_on else "OFF"
        self.title = "..."
        self._update_status()
        rumps.notification("SOCKS Proxy", "", f"Proxy {state_label}")
        self._fetch_ip()

    @rumps.clicked("Status")
    def status(self, _):
        d = self._data
        if not d:
            rumps.alert("SOCKS Proxy Status", "No data available")
            return
        country = d.get("country", "")
        flag = country_to_flag(country) if country else ""
        proxy_state = "ON" if is_socks_enabled() else "OFF"
        lines = [
            f"Proxy: {proxy_state}",
            f"IP: {d.get('ip', '?')}",
            f"Country: {flag} {d.get('country', '?')}",
            f"City: {d.get('city', '?')}, {d.get('region', '?')}",
            f"Org: {d.get('org', '?')}",
            f"Timezone: {d.get('timezone', '?')}",
            f"Location: {d.get('loc', '?')}",
        ]
        hostname = d.get("hostname")
        if hostname:
            lines.insert(2, f"Hostname: {hostname}")
        rumps.alert("SOCKS Proxy Status", "\n".join(lines))

    @rumps.timer(30)
    def refresh(self, _):
        self._fetch_ip()


if __name__ == "__main__":
    SocksProxyApp().run()
