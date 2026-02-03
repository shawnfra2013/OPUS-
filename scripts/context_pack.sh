#!/bin/bash

# Gather high-signal files
echo "Packing context bundle..."
mkdir -p context_bundle
cp README.md package.json tsconfig.json .eslintrc* context_bundle/
cp -r src context_bundle/

# Output deterministic context bundle
tar -czf context_bundle.tar.gz context_bundle
rm -rf context_bundle