#!/usr/bin/env python3
"""Patch DSH Desktop v2.0.17 for experimental macOS 12 builds."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
app = root / "dsh-plugin-desktop"
package_file = app / "package.json"
package = json.loads(package_file.read_text(encoding="utf-8"))
assert package["version"] == "2.0.17", "Expected DSH Desktop 2.0.17"
assert package["devDependencies"]["electron"] == "44.0.0", "Unexpected upstream Electron version"
assert package["peerDependencies"]["electron"] == "44.0.0", "Unexpected Electron peer version"
# Pin the exact supported Electron 43.0.0 runtime fingerprint.\n# node-addon-require-builtin 0.1.6 rejects later Electron 43 patch versions.\npackage["devDependencies"]["electron"] = "43.0.0"
package["peerDependencies"]["electron"] = "43.0.0"
package["build"]["mac"]["minimumSystemVersion"] = "12.0.0"
# Old build images have Xcode 16; .icon needs Xcode 26 actool.
# Upstream already provides a prebuilt .icns for legacy macOS.
assert (app / "build" / "app-icon.icns").is_file(), "Missing macOS legacy icon"
package["build"]["mac"]["icon"] = "build/app-icon.icns"
package_file.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Upstream expects Electron 44's precompiled fs-ext ABI 149. Electron 43 is ABI 148.
# Its packaging step rebuilds fs-ext for the installed Electron runtime.
for path in app.rglob("*"):
    if path.is_file() and path.suffix in (".ts", ".js", ".mjs"):
        text = path.read_text(encoding="utf-8")
        if "electron.abi149.node" in text:
            path.write_text(text.replace("electron.abi149.node", "electron.abi148.node"), encoding="utf-8")
            print("Patched ABI check:", path.relative_to(root))
print("Prepared experimental DSH v2.0.17 / Electron 43.0.0 / macOS >=12 build")
