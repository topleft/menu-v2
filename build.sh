#!/bin/bash

mkdir -p python/lib/python3.12/site-packages

# Export and install dependencies for Lambda layer
poetry export -f requirements.txt --without-hashes --output requirements.txt
pip install -r requirements.txt -t python/lib/python3.12/site-packages/

# Create ZIP file for the layer
zip -r python.zip python/

# Clean up
rm -rf python/
rm requirements.txt

echo "Python dependencies packaged successfully!" 