#!/usr/bin/env python3
"""
Summarize lines of code by file extension for tracked files.

This script walks the Git index to count lines for each tracked file. It is
meant to provide a quick overview of what kinds of files are present in the
checkout without relying on external dependencies.
"""

import argparse
import collections
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize lines of code for files tracked by Git, grouped by "
            "extension."
        )
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help=(
            "Limit output to the N largest extensions by line count. "
            "Use 0 to show all entries."
        ),
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        help=(
            "Filter results to the provided file extensions (with or without "
            "a leading dot)."
        ),
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="NAME",
        help="Exclude any path containing this directory name (may be repeated).",
    )
    parser.add_argument(
        "--show-empty",
        action="store_true",
        help="Include extensions that resolve to zero counted files.",
    )
    return parser.parse_args()


def normalize_extensions(extensions: Sequence[str] | None) -> Set[str]:
    if not extensions:
        return set()
    normalized = set()
    for ext in extensions:
        ext = ext.strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = "." + ext
        normalized.add(ext)
    return normalized


def tracked_files() -> List[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True
    )
    raw_paths = result.stdout.decode("utf-8", errors="ignore").split("\0")
    return [Path(p) for p in raw_paths if p]


def should_skip(path: Path, exclude_dirs: Iterable[str], extensions: Set[str]) -> bool:
    if any(part in exclude_dirs for part in path.parts):
        return True
    if extensions and path.suffix not in extensions:
        return True
    return False


def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def gather_statistics(files: Iterable[Path], exclude_dirs: List[str], extensions: Set[str]) -> Dict[str, tuple[int, int]]:
    stats: Dict[str, tuple[int, int]] = collections.defaultdict(lambda: (0, 0))
    for path in files:
        if should_skip(path, exclude_dirs, extensions):
            continue
        extension = path.suffix or "<no extension>"
        line_count = count_lines(path)
        files_seen, lines_seen = stats[extension]
        stats[extension] = (files_seen + 1, lines_seen + line_count)
    return stats


def render_table(stats: Dict[str, tuple[int, int]], top: int, show_empty: bool) -> str:
    ordered = sorted(stats.items(), key=lambda item: item[1][1], reverse=True)
    if top > 0:
        ordered = ordered[:top]

    if not ordered and not show_empty:
        return "No matching files found."

    extension_width = max((len(ext) for ext, _ in ordered), default=len("Extension"))
    files_width = max((len(str(counts[0])) for _, counts in ordered), default=len("Files"))
    lines_width = max((len(str(counts[1])) for _, counts in ordered), default=len("Lines"))

    header = f"{'Extension':<{extension_width}}  {'Files':>{files_width}}  {'Lines':>{lines_width}}"
    separator = f"{'-' * extension_width}  {'-' * files_width}  {'-' * lines_width}"

    rows = [header, separator]
    for extension, (files_seen, lines_seen) in ordered:
        if not show_empty and files_seen == 0:
            continue
        rows.append(
            f"{extension:<{extension_width}}  {files_seen:>{files_width}}  {lines_seen:>{lines_width}}"
        )

    return "\n".join(rows)


def main() -> None:
    args = parse_args()
    extensions = normalize_extensions(args.extensions)
    files = tracked_files()
    stats = gather_statistics(files, args.exclude_dir, extensions)
    print(render_table(stats, args.top, args.show_empty))


if __name__ == "__main__":
    main()
