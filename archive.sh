#!/bin/bash
# Based on https://www.rootusers.com/gzip-vs-bzip2-vs-xz-performance-comparison/
# Using all threads and with most efficient compression level for being the quickest.
# Hex blob dump for safeguarding import.

mysqldump --hex-blob rbt incoming | xz -1 -T0 > incoming.sql.xz
