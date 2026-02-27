#!/bin/bash
# qmd reindex — keeps the memory index fresh
# Run via cron every 4 hours
qmd update 2>/dev/null
qmd embed 2>/dev/null
