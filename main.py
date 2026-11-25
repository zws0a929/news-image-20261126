#!/usr/bin/env python3
"""Entry program for the make.fun bounty ``news-image-20261126``.

Competition: "Sum up 26 November's world news in one image"
(https://make.fun/bounty/news-image-20261126, $100 prize pool).

What this program does
----------------------
It takes the front-page image ``entry.png`` that sits next to this file
and copies it, byte for byte, to ``/output/entry.png``.  The copy is
verified with SHA-256 so the file the judges see is exactly the file
that was built here.  Nothing is fetched from the network and no
third-party packages are used: Python 3.13 standard library only.

Stories on the front page (Thursday, November 26, 2026)
--------------------------------------------------------
1. Pakistan's first astronaut -- Muhammad Zeeshan Ali flies aboard
   China's Shenzhou-24 and becomes the first foreign astronaut to
   board the Tiangong space station.
2. North Korea expels Switzerland's envoy -- Pyongyang orders Sylvain
   Astier, head of the Swiss diplomatic office, out within 48 hours
   and closes the office over Swiss sanctions.
3. Hodeida hit, Houthis vow revenge -- the Saudi-led coalition strikes
   Yemen's port city of Hodeida; the Houthis threaten Jeddah and other
   Red Sea ports.
4. All 20 hostages freed in Cartagena -- Colombian police and troops
   storm an Exito supermarket after a 17-hour siege; one captor killed.
5. Pacific pact -- Australia and Solomon Islands sign a landmark
   treaty: Canberra becomes the primary security partner, pledging
   A$740 million over a decade, and no foreign military bases.
6. Russian war dead near 500,000 -- leaked Rosstat figures analysed by
   the BBC show at least 490,334 Russian soldiers killed in Ukraine.
7. Shanghai party chief under investigation -- Politburo member Chen
   Jining is probed for graft, the fourth top leader to fall since 2025.
8. Also: the United States proposes new tariffs on 14 trading
   partners, with China facing the highest rate.

Usage
-----
    python3 main.py               # copy entry.png to /output/entry.png
    python3 main.py --verify-only # only check entry.png, do not copy
    python3 main.py --output DIR  # copy into a different directory

Exit codes: 0 on success, 1 on any failure (missing file, bad PNG,
oversize file, hash mismatch, ...).  Failures are loud: the program
prints an error to stderr and stops instead of writing a bad copy.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
import tempfile
import zlib

# The front-page image must be a 1024 x 1024 PNG and no larger than
# 1 MiB.  These limits come from the competition rules.
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_SIZE_BYTES = 1 * 1024 * 1024  # 1 MiB

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
OUTPUT_FILENAME = "entry.png"


def fail(message: str) -> "SystemExit":
    """Print an error to stderr and return a failing exit."""
    print(f"error: {message}", file=sys.stderr)
    return SystemExit(1)


def source_path() -> str:
    """Absolute path of the entry.png next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, OUTPUT_FILENAME)


def read_entry(path: str) -> bytes:
    """Read entry.png, failing loudly if it is missing or unreadable."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"entry image not found: {path}")
    with open(path, "rb") as handle:
        return handle.read()


def check_size(data: bytes, path: str) -> None:
    """Enforce the 1 MiB size cap on the entry image."""
    size = len(data)
    if size > MAX_SIZE_BYTES:
        raise ValueError(
            f"{path} is {size} bytes, over the "
            f"{MAX_SIZE_BYTES} byte limit"
        )


def parse_png_header(data: bytes) -> tuple[int, int]:
    """Parse the PNG signature and IHDR chunk; return (width, height).

    Raises ValueError if the file is not a PNG or its header is
    truncated.  The IHDR chunk is the first chunk in every PNG:
    4 bytes length, 4 bytes type ("IHDR"), then 13 bytes of data
    starting with width and height as big-endian 32-bit integers.
    """
    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file: bad signature")
    if len(data) < 8 + 8 + 13:
        raise ValueError("truncated PNG: IHDR chunk missing")
    chunk_length = struct.unpack(">I", data[8:12])[0]
    chunk_type = data[12:16]
    if chunk_type != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    if chunk_length != 13:
        raise ValueError(f"IHDR length is {chunk_length}, expected 13")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def check_ihdr_crc(data: bytes) -> None:
    """Verify the CRC-32 stored after the IHDR chunk's data.

    A PNG chunk's CRC covers its 4-byte type plus its data.  The IHDR
    chunk starts at offset 8 (length) / 12 (type) / 16 (data, 13 bytes),
    so its CRC lives at bytes 29..33.  A mismatch means the header was
    corrupted in transit and the dimensions above cannot be trusted.
    """
    if len(data) < 33:
        raise ValueError("truncated PNG: IHDR CRC missing")
    chunk_type = data[12:16]
    chunk_data = data[16:29]
    stored_crc = struct.unpack(">I", data[29:33])[0]
    computed_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
    if stored_crc != computed_crc:
        raise ValueError(
            f"IHDR CRC mismatch: stored {stored_crc:#010x}, "
            f"computed {computed_crc:#010x}"
        )


def check_dimensions(width: int, height: int) -> None:
    """The entry must be exactly 1024 x 1024 pixels."""
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"image is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )


def sha256_hex(data: bytes) -> str:
    """SHA-256 hex digest of a byte string."""
    return hashlib.sha256(data).hexdigest()


def verify_entry(data: bytes, path: str) -> tuple[int, int, str]:
    """Run every check on the entry bytes; return (w, h, sha256)."""
    check_size(data, path)
    width, height = parse_png_header(data)
    check_ihdr_crc(data)
    check_dimensions(width, height)
    return width, height, sha256_hex(data)


def write_copy(data: bytes, output_dir: str) -> str:
    """Write the entry bytes to <output_dir>/entry.png and return its path."""
    os.makedirs(output_dir, exist_ok=True)
    dest = os.path.join(output_dir, OUTPUT_FILENAME)
    with open(dest, "wb") as handle:
        handle.write(data)
    return dest


def determinism_self_check(data: bytes, expected_hash: str) -> None:
    """Prove the copy step is deterministic.

    Writes the entry bytes twice to two fresh temporary files and
    confirms both copies hash identically to the source.  If the two
    copies ever differed, the copy path itself would be unreliable and
    the program must refuse to produce an output.
    """
    hashes = []
    with tempfile.TemporaryDirectory(prefix="news-image-check-") as tmpdir:
        for index in (1, 2):
            trial = os.path.join(tmpdir, f"trial-{index}.png")
            with open(trial, "wb") as handle:
                handle.write(data)
            with open(trial, "rb") as handle:
                hashes.append(sha256_hex(handle.read()))
    if hashes[0] != expected_hash or hashes[1] != expected_hash:
        raise ValueError(
            "determinism self-check failed: repeated copies differ "
            f"({hashes[0][:12]} vs {hashes[1][:12]} vs {expected_hash[:12]})"
        )


def copy_and_verify(data: bytes, output_dir: str, expected_hash: str) -> str:
    """Copy entry.png and prove the copy matches the source byte for byte."""
    dest = write_copy(data, output_dir)
    with open(dest, "rb") as handle:
        copied = handle.read()
    if sha256_hex(copied) != expected_hash:
        raise ValueError(
            f"copy mismatch: {dest} does not match the source bytes"
        )
    return dest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Command-line options for the entry program."""
    parser = argparse.ArgumentParser(
        description=(
            "Copy the news-image-20261126 front page (entry.png) "
            "to /output/entry.png, verifying it byte for byte."
        )
    )
    parser.add_argument(
        "--output",
        default="/output",
        help="directory to write entry.png into (default: /output)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help=(
            "only run the checks on entry.png (size, PNG header, "
            "IHDR CRC, dimensions, SHA-256) and do not write a copy"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the entry program; return the process exit code."""
    args = parse_args(argv)
    path = source_path()
    try:
        data = read_entry(path)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    try:
        width, height, digest = verify_entry(data, path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"entry: {path}")
    print(f"size: {len(data)} bytes")
    print(f"dimensions: {width}x{height}")
    print(f"sha256: {digest}")
    if args.verify_only:
        print("verify-only: all checks passed, nothing written")
        return 0
    try:
        determinism_self_check(data, digest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("determinism: two trial copies hash identically")
    try:
        dest = copy_and_verify(data, args.output, digest)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote: {dest} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
