#!/usr/bin/env python3
"""Entry point for the news-image-20261118 make.fun entry.

Delivers the committed entry.png to the grader's output directory.
The image itself is drawn by build_image.py (deterministic Pillow
drawing); this program only has to move it, byte for byte, to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png), after
checking it against the competition's image gate:

  * whole PNG (signature and IEND chunk present)
  * at most 1 MiB (1,048,576 bytes)
  * at most 1024 x 1024 pixels

If entry.png is missing beside this file it is regenerated first by
running build_image.py, which reproduces the identical bytes.
Standard library only; no network.
"""

import os
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def regenerate():
    """Rebuild entry.png from build_image.py (same bytes every run)."""
    subprocess.run([sys.executable, str(HERE / "build_image.py")],
                   check=True, cwd=str(HERE))


def check_gate(data):
    """Raise ValueError unless data is a whole PNG inside the gate."""
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the 1 MiB gate")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("entry.png does not start with the PNG signature")
    if b"IEND" not in data[-32:]:
        raise ValueError("entry.png is truncated: no IEND chunk at the end")
    # IHDR is the first chunk: width and height are big-endian uint32
    # at byte offsets 16 and 20.
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"entry.png is {width}x{height}, over the 1024x1024 gate")
    return width, height


def main():
    if not SOURCE.exists():
        regenerate()
    data = SOURCE.read_bytes()
    width, height = check_gate(data)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)
    print(f"entry.png: {len(data)} bytes, {width}x{height} -> {target}")


if __name__ == "__main__":
    main()
