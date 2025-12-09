===================
Git LOC summary tool
===================

The ``scripts/git-loc-summary.py`` helper prints a brief summary of tracked
files grouped by extension. It offers a quick way to see where code lives
without requiring external dependencies or a full checkout scan.

Basic usage
===========

To inspect every tracked file and list the total lines by extension::

   $ scripts/git-loc-summary.py

Limiting output
---------------

Use ``--top`` to constrain output to the largest extensions by line count::

   $ scripts/git-loc-summary.py --top 5

Filtering paths
---------------

The ``--extensions`` option restricts the report to a specific set of file
extensions. The leading dot may be omitted::

   $ scripts/git-loc-summary.py --extensions c h

Use ``--exclude-dir`` to omit directories by name. The option can be repeated
when multiple directories should be skipped::

   $ scripts/git-loc-summary.py --exclude-dir tools --exclude-dir samples

Showing empty entries
---------------------

By default, extensions that would report zero files are suppressed. Use
``--show-empty`` to include them, which can be helpful when used alongside
``--extensions``.
