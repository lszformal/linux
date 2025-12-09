#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0
#
# Simple build dependency checker for Linux kernel development.
# The script reports whether common toolchain components are available and
# exits with a non-zero status if any are missing.

set -euo pipefail

DEFAULT_TOOLS=(
    "make"
    "gcc"
    "ld"
    "bc"
    "flex"
    "bison"
    "perl"
    "pahole"
    "python3"
    "rsync"
    "openssl"
)

usage() {
    cat <<USAGE
Usage: ${0##*/} [options]

Options:
  --tool <name>    Check an additional tool (can be supplied multiple times).
  --skip <name>    Skip checking a tool from the default list.
  -h, --help       Display this help and exit.

The script verifies that common kernel build tools are available on the
system PATH. It exits with status 0 when all requested tools are present
and 1 otherwise.
USAGE
}

extra_tools=()
skipped_tools=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tool)
            [[ $# -lt 2 ]] && { echo "Missing argument for --tool" >&2; exit 2; }
            extra_tools+=("$2")
            shift 2
            ;;
        --skip)
            [[ $# -lt 2 ]] && { echo "Missing argument for --skip" >&2; exit 2; }
            skipped_tools+=("$2")
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 2
            ;;
    esac
done

contains() {
    local needle=$1
    shift
    for candidate in "$@"; do
        [[ $candidate == "$needle" ]] && return 0
    done
    return 1
}

build_tool_list=()
for tool in "${DEFAULT_TOOLS[@]}"; do
    if ! contains "$tool" "${skipped_tools[@]:-}"; then
        build_tool_list+=("$tool")
    fi
done
build_tool_list+=("${extra_tools[@]}")

missing=()
for tool in "${build_tool_list[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf "[ ok ] %-8s -> %s\n" "$tool" "$(command -v "$tool")"
    else
        printf "[missing] %s\n" "$tool"
        missing+=("$tool")
    fi
done

if [[ ${#missing[@]} -eq 0 ]]; then
    echo "All requested build tools are available."
else
    echo "Missing tools: ${missing[*]}" >&2
    exit 1
fi
