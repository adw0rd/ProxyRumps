#!/usr/bin/env python3
"""Menu bar app to toggle SOCKS proxy on macOS."""

import json
import subprocess
import threading
import rumps

NETWORK_SERVICE = "Wi-Fi"
SOCKS_HOST = "localhost"
SOCKS_PORT = "8888"
IP_CHECK_URL = "https://ipinfo.io/json"


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
        self._toggle_item = rumps.MenuItem("...", callback=self._on_toggle)
        icon = "🟢" if is_socks_enabled() else "🔴"
        super().__init__(f"{icon} ...", quit_button="Reload")
        self.menu = [self._toggle_item, None]
        self._data = {}
        self._update_toggle_label()
        self._fetch_ip()

    def _update_toggle_label(self):
        if is_socks_enabled():
            self._toggle_item.title = "Disable Proxy"
        else:
            self._toggle_item.title = "Enable Proxy"

    def _status_icon(self):
        return "🟢" if is_socks_enabled() else "🔴"

    def _update_title(self):
        country = self._data.get("country", "")
        code = country.upper() if country else "..."
        self.title = f"{self._status_icon()} {code}"
        self._update_toggle_label()

    def _fetch_ip(self):
        def _do():
            self._data = fetch_ip_data()
            self._update_title()
        threading.Thread(target=_do, daemon=True).start()

    def _on_toggle(self, _):
        currently_on = is_socks_enabled()
        set_socks(not currently_on)
        state_label = "ON" if not currently_on else "OFF"
        self.title = f"{self._status_icon()} ..."
        self._update_toggle_label()
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
