#!/bin/bash

# Create all required directories
mkdir -p /app/data/uploads \
         /app/data/processed \
         /app/data/pipeline_output

# Set permissions (readable/writable by all users in container)
chmod -R 777 /app/data

# Create empty .parquet files if they don't exist
touch /app/data/processed/.keep
touch /app/data/pipeline_output/.keep

# Output directory structure for debugging
echo "Directory structure:"
ls -la /app/data/