#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Applications/ProxyRumps.app"

echo "Setting up venv..."
uv venv "$PROJECT_DIR/.venv"
uv pip install -q -p "$PROJECT_DIR/.venv" -r "$PROJECT_DIR/pyproject.toml"

echo "Creating ProxyRumps.app..."
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"

cat > "$APP_DIR/Contents/MacOS/ProxyRumps" <<LAUNCHER
#!/bin/bash
cd "$PROJECT_DIR"
exec "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/app.py"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/ProxyRumps"

cat > "$APP_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>ProxyRumps</string>
    <key>CFBundleIdentifier</key>
    <string>dev.adw0rd.proxyrumps</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>ProxyRumps</string>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
PLIST

PLIST_PATH="$HOME/Library/LaunchAgents/dev.adw0rd.proxyrumps.plist"
echo "Installing LaunchAgent..."
cat > "$PLIST_PATH" <<AGENT
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>dev.adw0rd.proxyrumps</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python</string>
        <string>$PROJECT_DIR/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/proxyrumps.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/proxyrumps.err</string>
</dict>
</plist>
AGENT

echo "Installed:"
echo "  App:         $APP_DIR"
echo "  LaunchAgent: $PLIST_PATH"
echo ""
echo "Launch from Spotlight or log out/in to auto-start."
