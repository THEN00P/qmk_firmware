#!/usr/bin/env python3
"""Generate release notes for a build-far release.

Per-board firmware versions come from `qmk info`, so the notes state the real
version of each binary instead of a placeholder.
"""

import argparse
import json
import os
import subprocess
import sys

UPSTREAM = "https://github.com/Keychron/qmk_firmware"

LAYOUTS = {
    "ansi": "ANSI (1-row enter)",
    "iso": "ISO (2-row enter)",
    "jis": "JIS (2-row enter)",
}


def layout_of(target):
    """ansi_encoder -> ANSI, iso -> ISO, ..."""
    leaf = target.rsplit("/", 1)[-1]
    base = leaf.replace("_encoder", "")
    return LAYOUTS.get(base, leaf)


def info(target):
    out = subprocess.run(
        ["qmk", "info", "-kb", target, "-f", "json"],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out)
    return data["keyboard_name"], data["usb"]["device_version"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--build-sha", required=True)
    args = ap.parse_args()

    targets = [t.strip() for t in open(args.targets) if t.strip()]
    bins = os.listdir(args.artifacts)

    rows = []
    for target in targets:
        name, version = info(target)
        km = target.split("/")[0]
        stem = target.replace("/", "_") + "_" + km
        match = next((b for b in bins if b == stem + ".bin"), None)
        if match is None:
            print(f"no binary for {target} (expected {stem}.bin)", file=sys.stderr)
            sys.exit(1)
        rows.append((name, layout_of(target), version, match))

    rows.sort()

    print("Full analog report firmware. Board versions carry a `+far` suffix "
          "so they are distinguishable from stock.\n")
    print("| Keyboard | Layout | Version | File |")
    print("|---|---|---|---|")
    for name, layout, version, fname in rows:
        print(f"| {name} | {layout} | `v{version}+far` | `{fname}` |")

    print(f"""
Built from Keychron [`{args.upstream_sha}`]({UPSTREAM}/commit/{args.upstream_sha}) \
(`2025q3`), source at [`{args.build_sha[:10]}`](../../tree/{args.build_sha}).

### Flashing
1. Install [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases).
2. Open the `.bin` for your keyboard and layout.
3. Tick **Auto-Flash**.
4. Unplug the keyboard.
5. Hold **Esc** while plugging it back in. It flashes in a few seconds.

Check the version in VIA afterwards: it should end in `+far`.""")


if __name__ == "__main__":
    main()
