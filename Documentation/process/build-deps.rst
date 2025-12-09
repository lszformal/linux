.. SPDX-License-Identifier: GPL-2.0

===============================
Kernel build dependency checker
===============================

The ``scripts/check-build-deps.sh`` helper provides a quick way to verify
that common build dependencies are available in the current environment
before starting a kernel build. The script checks for a set of default
build utilities, reports where each tool is found on ``$PATH``, and exits
with a non-zero status if any are missing.

Usage
-----

The script can be run directly from the repository root::

    scripts/check-build-deps.sh

By default it checks the presence of ``make``, ``gcc``, ``ld``, ``bc``,
``flex``, ``bison``, ``perl``, ``pahole``, ``python3``, ``rsync`` and
``openssl``.

Extra tools can be added with ``--tool`` and defaults can be skipped with
``--skip``::

    scripts/check-build-deps.sh --tool clang --skip openssl

The command exits with status 0 when all requested tools are available
and 1 when any are missing. Use ``--help`` to show a brief summary of the
available options.
