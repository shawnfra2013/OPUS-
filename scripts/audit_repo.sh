#!/bin/bash

# Collect metadata
echo "Collecting repo metadata..."
find . -type f -exec ls -lh {} \; > repo_metadata.txt

# Run lint, type-check, and tests
npm run format
npm run lint
npm run type-check
npm test

# Produce audit report
echo "Generating AUDIT_REPORT.md..."
echo "# Audit Report" > AUDIT_REPORT.md
echo "## Metadata" >> AUDIT_REPORT.md
cat repo_metadata.txt >> AUDIT_REPORT.md

echo "## Lint Results" >> AUDIT_REPORT.md
npm run lint >> AUDIT_REPORT.md

echo "## Type-Check Results" >> AUDIT_REPORT.md
npm run type-check >> AUDIT_REPORT.md

echo "## Test Results" >> AUDIT_REPORT.md
npm test >> AUDIT_REPORT.md

rm repo_metadata.txt