#!/bin/bash
mkdocs build --clean 2>&1 | tee build_log.txt
echo "Checking for errors..."
grep -E "(ERROR|WARNING)" build_log.txt | head -30